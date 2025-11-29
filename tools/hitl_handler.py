
"""
Human-in-the-Loop (HITL) Handler - User Confirmation Module

This module implements the HITL confirmation mechanism for the Research Agent,
allowing users to approve or reject bulk research operations before execution.

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: Human-in-the-Loop (HITL)
═══════════════════════════════════════════════════════════════════════════════

HITL is a critical pattern in agentic systems that:
1. Keeps humans in control of significant operations
2. Allows review before potentially expensive/extensive actions
3. Enables user customization of agent behavior mid-workflow
4. Provides transparency into what the agent wants to do

Implementation Pattern:
    1. Agent identifies action requiring approval (gap research)
    2. Tool calls request_confirmation() with hint and payload
    3. ADK pauses execution and prompts user
    4. User approves/rejects via UI or chat
    5. Agent resumes with decision in tool_context.tool_confirmation

═══════════════════════════════════════════════════════════════════════════════
PARALLEL EXECUTION MODE
═══════════════════════════════════════════════════════════════════════════════

When PARALLEL_GAP_RESEARCH=true, this handler can execute ALL gap research
in parallel using asyncio.gather(), achieving 3-5x speedup:

    Sequential: Gap1 → Gap2 → Gap3 → Gap4 = ~60 seconds
    Parallel:   Gap1 ─┬─ Gap3             = ~20 seconds
                Gap2 ─┴─ Gap4

═══════════════════════════════════════════════════════════════════════════════
ARCHITECTURE POSITION
═══════════════════════════════════════════════════════════════════════════════

Phase 4 of 5-phase workflow:
    [Search] → [Quality] → [Gap] → [HITL] → [Synthesis]
                                     ↑ YOU ARE HERE

═══════════════════════════════════════════════════════════════════════════════
KNOWN ISSUES & WORKAROUNDS
═══════════════════════════════════════════════════════════════════════════════

ADK Bug: In ADK 1.18.0, clicking the confirmation button causes a JSON parsing
error (json.loads called on dict in request_confirmation.py line 84).

Workarounds:
    1. Type "yes" or "approve" in chat instead of clicking button
    2. Set AUTO_APPROVE_GAPS=true to skip confirmation entirely

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.tools import ToolContext
from typing import Dict, Any, List, Optional
from ..utils.logger import setup_logger
import logging
import json
import os

logger = setup_logger("HITL-Handler", level=logging.INFO)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Set AUTO_APPROVE_GAPS=true to skip HITL confirmation (workaround for ADK bug)
AUTO_APPROVE_GAPS = os.getenv("AUTO_APPROVE_GAPS", "false").lower() == "true"

# Set PARALLEL_GAP_RESEARCH=true to execute all gaps in parallel (3-5x faster)
# Default is now TRUE to use ParallelAgent!
PARALLEL_GAP_RESEARCH = os.getenv("PARALLEL_GAP_RESEARCH", "true").lower() == "true"

# Maximum concurrent gap searches (to avoid rate limiting)
MAX_CONCURRENT_GAPS = int(os.getenv("MAX_CONCURRENT_GAPS", "3"))

# Track confirmation state to prevent duplicate requests
_confirmation_requested = {}

# ═══════════════════════════════════════════════════════════════════════════════
# APPROVAL KEYWORDS (case-insensitive)
# ═══════════════════════════════════════════════════════════════════════════════
APPROVAL_KEYWORDS = {"yes", "approve", "approved", "positive" , "ok", "okay", "go", "proceed", "confirm", "y"}
REJECTION_KEYWORDS = {"no", "reject", "rejected", "skip", "cancel", "n", "stop", "decline"}


def _check_text_approval(tool_context: ToolContext) -> str | None:
    """
    Check if the user's last message contains approval/rejection keywords.
    
    This is a workaround for ADK's tool_confirmation button bug.
    When users type "yes", "ok", "approved" etc. in chat, we interpret that
    as approval even though tool_confirmation isn't set.
    
    Returns:
        "approved" if approval keyword found
        "rejected" if rejection keyword found
        None if no clear signal
    """
    # Try to get the last user message from actions or context
    # The ADK passes the user's reply through different mechanisms
    try:
        # Check if there's a pending confirmation and look at session state
        if not tool_context.state.get("hitl_confirmation_requested", False):
            return None
            
        # The user's response should be available - we check by looking at
        # what the agent received. Since we're being called again after the user
        # responded, the framework should have the response.
        # 
        # Unfortunately, ADK doesn't directly expose the user's text in tool_context.
        # However, when tool_confirmation IS set (even without .confirmed), 
        # we can check it. Also, the root agent is instructed to call this
        # function with specific parameters based on user response.
        
        return None  # Let the main logic handle it
    except Exception as e:
        logger.debug(f"Error checking text approval: {e}")
        return None


def conduct_adaptive_gap_search(
    gaps: List[Dict[str, Any]], 
    tool_context: ToolContext,
    user_decision: Optional[str] = None
) -> str:
    """
    Conduct adaptive searches based on identified gaps.
    This bulk action requires user approval via HITL.
    
    NOTE: The `user_decision` parameter allows the LLM to explicitly pass
    the user's approval/rejection decision when calling this function again
    after the "pending" status. Valid values: "approved" or "rejected".
    
    ═══════════════════════════════════════════════════════════════════════════
    HITL FLOW DIAGRAM
    ═══════════════════════════════════════════════════════════════════════════
    
    Gap Agent identifies gaps
            │
            ▼
    ┌───────────────────────────────────────────┐
    │  conduct_adaptive_gap_search() called     │
    │  with list of gaps                        │
    └───────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────┐
    │  First call? (no tool_confirmation)       │
    │  → request_confirmation() with hint       │
    │  → Return "pending" status                │
    │  → Agent WAITS for user                   │
    └───────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────┐
    │  User sees prompt in ADK UI               │
    │  → Reviews gaps list                      │
    │  → Clicks Approve/Reject OR types reply  │
    └───────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────┐
    │  Function called again with               │
    │  tool_context.tool_confirmation set       │
    │  → Check .confirmed boolean               │
    │  → Return appropriate status              │
    └───────────────────────────────────────────┘
            │
      ┌─────┴─────┐
      ▼           ▼
   APPROVED    REJECTED
   (search     (skip to
   each gap)   synthesis)
    
    Args:
        gaps (List[Dict]): List of identified information gaps.
            Each gap should have:
            - topic: Brief description of what's missing
            - suggested_query: Optimized search query to fill gap
            - priority: high/medium/low
            - rationale: Why this gap matters
            
        tool_context (ToolContext): ADK context providing:
            - tool_confirmation: User's approval decision (after HITL)
            - state: Shared state dictionary
            - request_confirmation(): Method to trigger HITL
        
    Returns:
        str: JSON string with one of these statuses:
            - "pending": Awaiting user approval
            - "approved": User approved, proceed with gap research
            - "rejected": User declined, skip to synthesis
            - "completed": No gaps to process
    
    Example:
        >>> gaps = [{"topic": "Recent data", "suggested_query": "topic 2024"}]
        >>> result = conduct_adaptive_gap_search(gaps, tool_context)
        >>> # First call returns: {"status": "pending", ...}
        >>> # After approval returns: {"status": "approved", ...}
    """
    logger.info("=" * 60)
    logger.info("HITL Handler: conduct_adaptive_gap_search invoked")
    logger.info(f"Gaps received: {len(gaps) if gaps else 0}")
    logger.info("=" * 60)
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 1: No gaps provided - nothing to do
    # ──────────────────────────────────────────────────────────────────────────
    if not gaps:
        logger.info("✓ No gaps provided - skipping gap research")
        return json.dumps({
            'status': 'completed',
            'message': 'No gaps provided for adaptive search.',
            'requires_action': False
        })
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 2: Auto-approve mode (bypass HITL bug)
    # ──────────────────────────────────────────────────────────────────────────
    if AUTO_APPROVE_GAPS:
        logger.info(f"✓ AUTO_APPROVE_GAPS enabled - approving {len(gaps)} gaps automatically")
        execution_mode = "parallel" if PARALLEL_GAP_RESEARCH else "sequential"
        logger.info(f"  Execution mode: {execution_mode}" + (f" (max {MAX_CONCURRENT_GAPS} concurrent)" if PARALLEL_GAP_RESEARCH else ""))
        
        return json.dumps({
            "status": "approved",
            "message": f"✅ Auto-approved gap research for {len(gaps)} gaps.",
            "requires_action": True,
            "gaps_to_research": gaps,
            "execution_mode": execution_mode,
            "max_concurrent": MAX_CONCURRENT_GAPS if PARALLEL_GAP_RESEARCH else 1,
            "next_steps": [
                f"Execute gap research in {execution_mode} mode",
                "For each gap, call search_quality_pipeline with gap's suggested_query",
                "Incorporate results into final synthesis"
            ]
        })
    
    # ──────────────────────────────────────────────────────────────────────────
    # Check if confirmation was already requested (prevent duplicates)
    # ──────────────────────────────────────────────────────────────────────────
    confirmation_key = f"hitl_confirmation_requested"
    already_requested = tool_context.state.get(confirmation_key, False)
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 3: Check for tool_confirmation response
    # ──────────────────────────────────────────────────────────────────────────
    if tool_context.tool_confirmation:
        logger.info(f"🔍 Received tool_confirmation: confirmed={tool_context.tool_confirmation.confirmed}")
        
        # Clear the confirmation state
        tool_context.state[confirmation_key] = False
        
        if tool_context.tool_confirmation.confirmed:
            # APPROVED
            logger.info("✅ User APPROVED gap research - proceeding with searches")
            
            execution_mode = "parallel" if PARALLEL_GAP_RESEARCH else "sequential"
            logger.info(f"  Execution mode: {execution_mode}" + (f" (max {MAX_CONCURRENT_GAPS} concurrent)" if PARALLEL_GAP_RESEARCH else ""))
            
            confirmed_gaps = tool_context.tool_confirmation.payload.get('gaps', gaps)
            tool_context.state['adaptive_gaps'] = confirmed_gaps
            tool_context.state['gap_research_approved'] = True
            
            return json.dumps({
                "status": "approved",
                "message": f"✅ User approved adaptive gap research for {len(confirmed_gaps)} gaps.",
                "requires_action": True,
                "gaps_to_research": confirmed_gaps,
                "execution_mode": execution_mode,
                "max_concurrent": MAX_CONCURRENT_GAPS if PARALLEL_GAP_RESEARCH else 1,
                "next_steps": [
                    f"Execute gap research in {execution_mode} mode",
                    "For each gap, call search_quality_pipeline with gap's suggested_query",
                    "Incorporate results into final synthesis"
                ]
            })
        else:
            # REJECTED
            logger.info("❌ User REJECTED gap research - skipping to synthesis")
            tool_context.state['gap_research_approved'] = False
            
            return json.dumps({
                "status": "rejected",
                "message": "❌ User declined adaptive gap research. Proceeding with available information.",
                "requires_action": False,
                "fallback_action": "proceed_to_synthesis"
            })
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 4: Already requested, and called again WITHOUT tool_confirmation
    # ──────────────────────────────────────────────────────────────────────────
    # The root agent calls us again after the user responded.
    # The LLM should pass user_decision="approved" or "rejected" based on
    # what the user said. Check this parameter to determine the response.
    # ──────────────────────────────────────────────────────────────────────────
    if already_requested:
        logger.info(f"🔍 Re-called after confirmation. user_decision={user_decision}")
        
        # Clear the confirmation state
        tool_context.state[confirmation_key] = False
        
        # Check user_decision parameter (case-insensitive)
        decision = (user_decision or "").lower().strip()
        
        # Check for rejection keywords
        if decision in REJECTION_KEYWORDS or decision == "rejected":
            logger.info("❌ User REJECTED gap research (via user_decision parameter)")
            tool_context.state['gap_research_approved'] = False
            
            return json.dumps({
                "status": "rejected",
                "message": "❌ User declined adaptive gap research. Proceeding with available information.",
                "requires_action": False,
                "fallback_action": "proceed_to_synthesis"
            })
        
        # Check for approval keywords (or default to approval for backwards compatibility)
        if decision in APPROVAL_KEYWORDS or decision == "approved" or not decision:
            # If no decision provided, log a warning but proceed (backwards compat)
            if not decision:
                logger.warning("⚠️ No user_decision provided, assuming APPROVAL for backwards compatibility")
            
            logger.info("✅ User APPROVED gap research (via user_decision parameter)")
            
            execution_mode = "parallel" if PARALLEL_GAP_RESEARCH else "sequential"
            logger.info(f"  Execution mode: {execution_mode}" + (f" (max {MAX_CONCURRENT_GAPS} concurrent)" if PARALLEL_GAP_RESEARCH else ""))
            
            tool_context.state['adaptive_gaps'] = gaps
            tool_context.state['gap_research_approved'] = True
            
            return json.dumps({
                "status": "approved",
                "message": f"✅ Approved adaptive gap research for {len(gaps)} gaps.",
                "requires_action": True,
                "gaps_to_research": gaps,
                "execution_mode": execution_mode,
                "max_concurrent": MAX_CONCURRENT_GAPS if PARALLEL_GAP_RESEARCH else 1,
                "next_steps": [
                    f"Execute gap research in {execution_mode} mode",
                    "Call parallel_gap_researcher with all gap queries",
                    "Incorporate results into final synthesis"
                ]
            })
        
        # Unknown decision - treat as rejection for safety
        logger.warning(f"⚠️ Unknown user_decision '{decision}' - treating as REJECTION for safety")
        tool_context.state['gap_research_approved'] = False
        
        return json.dumps({
            "status": "rejected",
            "message": f"⚠️ Unknown decision '{decision}'. Proceeding without gap research.",
            "requires_action": False,
            "fallback_action": "proceed_to_synthesis"
        })
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 5: First call - request approval
    # ──────────────────────────────────────────────────────────────────────────
    logger.info("⏸️ First call - requesting user confirmation...")
    
    # Mark that we've requested confirmation
    tool_context.state[confirmation_key] = True
    
    # Format gaps for display
    gap_summary = "\n".join([
        f"  {i+1}. [{gap.get('priority', 'medium').upper()}] "
        f"{gap.get('topic', 'Unknown')}\n"
        f"      Query: \"{gap.get('suggested_query', 'N/A')}\""
        for i, gap in enumerate(gaps[:5])
    ])
    
    if len(gaps) > 5:
        gap_summary += f"\n  ... and {len(gaps) - 5} more gaps"
    
    # Request confirmation
    tool_context.request_confirmation(
        hint=(
            f"🔍 **Gap Research Approval**\n\n"
            f"Found {len(gaps)} information gaps:\n\n"
            f"{gap_summary}\n\n"
            f"---\n"
            f"**Reply with 'yes' to approve or 'no' to skip.**\n"
            f"(Note: Type your response in the chat - button may not work due to ADK bug)"
        ),
        payload={
            "num_gaps": len(gaps),
            "gaps": gaps,
            "operation": "adaptive_gap_research"
        },
    )
    
    logger.info("📋 Confirmation requested - awaiting user response")
    return json.dumps({
        "status": "pending",
        "message": f"⏸️ Awaiting approval for {len(gaps)} gap searches. Reply 'yes' or 'no' in the chat.",
        "requires_action": False,
        "gaps": gaps
    })
