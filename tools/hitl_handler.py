
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
ARCHITECTURE POSITION
═══════════════════════════════════════════════════════════════════════════════

Phase 4 of 5-phase workflow:
    [Search] → [Quality] → [Gap] → [HITL] → [Synthesis]
                                     ↑ YOU ARE HERE

This is the ONLY point where the user is asked for input during research.
All other phases run autonomously.

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
from typing import Dict, Any, List
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


def conduct_adaptive_gap_search(
    gaps: List[Dict[str, Any]], 
    tool_context: ToolContext
) -> str:
    """
    Conduct adaptive searches based on identified gaps.
    This bulk action requires user approval via HITL.
    
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
        return json.dumps({
            "status": "approved",
            "message": f"✅ Auto-approved gap research for {len(gaps)} gaps.",
            "requires_action": True,
            "gaps_to_research": gaps,
            "next_steps": [
                "For each gap, execute Phase 1 (Search Agent) with gap-specific queries",
                "Then execute Phase 2 (Quality Agent) to assess source quality",
                "Incorporate results into final synthesis"
            ]
        })
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 3: First call - request approval for bulk operation
    # ──────────────────────────────────────────────────────────────────────────
    if not tool_context.tool_confirmation:
        logger.info("⏸️ First call - requesting user confirmation...")
        
        # Format gaps for user-friendly display
        gap_summary = "\n".join([
            f"  {i+1}. [{gap.get('priority', 'medium').upper()}] "
            f"{gap.get('topic', 'Unknown')}\n"
            f"      Query: \"{gap.get('suggested_query', 'N/A')}\""
            for i, gap in enumerate(gaps[:5])  # Show first 5
        ])
        
        if len(gaps) > 5:
            gap_summary += f"\n  ... and {len(gaps) - 5} more gaps"
        
        # Request user confirmation - this pauses agent execution
        tool_context.request_confirmation(
            hint=(
                f"🔍 **Gap Research Approval**\n\n"
                f"Found {len(gaps)} information gaps:\n\n"
                f"{gap_summary}\n\n"
                f"---\n"
                f"**Reply with 'yes' to approve or 'no' to skip.**"
            ),
            payload={
                "num_gaps": len(gaps),
                "gaps": gaps,  # Store gaps in payload for resumption
                "operation": "adaptive_gap_research"
            },
        )
        
        # Return pending status - agent will wait for user response
        logger.info("📋 Confirmation requested - awaiting user response")
        return json.dumps({
            "status": "pending",
            "message": f"⏸️ Awaiting approval for {len(gaps)} gap searches. Check the chat for confirmation prompt.",
            "requires_action": False,  # Agent should NOT proceed yet
            "gaps": gaps  # Keep gaps available for agent context
        })
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 4: User APPROVED - proceed with gap research
    # ──────────────────────────────────────────────────────────────────────────
    if tool_context.tool_confirmation.confirmed:
        logger.info("✅ User APPROVED gap research - proceeding with searches")
        
        # Retrieve gaps from confirmation payload (more reliable than parameter)
        confirmed_gaps = tool_context.tool_confirmation.payload.get('gaps', gaps)
        
        # Store approval state for other components
        tool_context.state['adaptive_gaps'] = confirmed_gaps
        tool_context.state['gap_research_approved'] = True
        tool_context.state['gap_research_phase'] = 'executing'
        
        logger.info(f"📊 Processing {len(confirmed_gaps)} gaps")
        
        return json.dumps({
            "status": "approved",
            "message": f"✅ User approved adaptive gap research for {len(confirmed_gaps)} gaps.",
            "requires_action": True,  # Signal agent to proceed
            "gaps_to_research": confirmed_gaps,
            "next_steps": [
                "For each gap, execute Phase 1 (Search Agent) with gap-specific queries",
                "Then execute Phase 2 (Quality Agent) to assess source quality",
                "Skip Phase 3 (Gap Agent) - we don't need gaps for gaps",
                "Incorporate results into final synthesis"
            ]
        })
    
    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO 5: User REJECTED - skip gap research
    # ──────────────────────────────────────────────────────────────────────────
    else:
        logger.info("❌ User REJECTED gap research - skipping to synthesis")
        
        tool_context.state['gap_research_approved'] = False
        tool_context.state['gap_research_phase'] = 'rejected'
        
        return json.dumps({
            "status": "rejected",
            "message": "❌ User declined adaptive gap research. Proceeding with available information.",
            "requires_action": False,  # Agent should skip gap research
            "fallback_action": "proceed_to_synthesis"
        })
