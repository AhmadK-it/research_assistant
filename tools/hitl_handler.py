
"""
TODO 1: intergrate
        async def _phase_4_hitl(self, gaps):
        ""HITL checkpoint with real user input for terminal mode""
        logger.info("=" * 60)
        logger.info("HITL CHECKPOINT - Pausing for user input")
        logger.info("=" * 60)

        approval = self.hitl.request_search_approval(gaps)

        self.research_state['user_interactions'].append({
            'type': 'search_approval',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': approval['message']
        })

        logger.info("\n" + approval['message'])

        if os.getenv('HITL_MODE') == 'terminal' and sys.stdin.isatty():
            print("\n" + "=" * 60)
            print("⏸️  HUMAN INPUT REQUIRED")
            print("=" * 60)
            print(approval['message'])
            print("\nOptions:")
            for idx, opt in enumerate(approval['options'], 1):
                print(f"  {idx}. {opt}")

            while True:
                choice = input("\n👉 Enter your choice (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    break
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

            if choice == '1':
                decision = {
                    'continue_search': True,
                    'modified_queries': [gap['suggested_query'] for gap in gaps.get('critical_gaps', [])],
                    'user_feedback': 'User chose: Continue with suggested searches'
                }
            elif choice == '2':
                print("\n📝 Enter your modified search strategy:")
                custom_query = input("Search query: ").strip()
                decision = {
                    'continue_search': True,
                    'modified_queries': [custom_query],
                    'user_feedback': f'User provided custom query: {custom_query}'
                }
            elif choice == '3':
                decision = {
                    'continue_search': False,
                    'user_feedback': 'User chose: Stop and synthesize'
                }
            else:
                print("\n📝 Enter custom search query:")
                custom_query = input("Query: ").strip()
                decision = {
                    'continue_search': True,
                    'modified_queries': [custom_query] + [gap['suggested_query'] for gap in gaps.get('critical_gaps', [])],
                    'user_feedback': f'User added custom query: {custom_query}'
                }

            print(f"\n✅ {decision['user_feedback']}")
            print("=" * 60)
        else:
            logger.warning("HITL_MODE not terminal or stdin not TTY - using simulated response")
            decision = {
                'continue_search': True,
                'modified_queries': [gap['suggested_query'] for gap in gaps.get('critical_gaps', [])],
                'user_feedback': 'Simulated: Continue (set HITL_MODE=terminal for real input)'
            }

        logger.info(f"USER DECISION: {decision['user_feedback']}")
        logger.info("=" * 60)

        return decision
    
"""
"""
TODO 2: update instruction to include HITL steps and user notification requirements
"""
from google.adk.tools import ToolContext
from typing import Dict, Any, List
from ..utils.logger import setup_logger
import logging

logger = setup_logger("HITL-Handler", level=logging.INFO)


def conduct_adaptive_gap_search(
    gaps: List[Dict[str, Any]], 
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Conduct adaptive searches based on identified gaps.
    This bulk action requires approval.

    Args:
        gaps (list): List of identified information gaps with suggested queries.
        tool_context (ToolContext): Contextual information for the tool execution.
        
    Returns:
        dict: Search results or status message with execution instructions.
    """
    logger.info("Conducting adaptive gap search...")
    # ----------------------------------------------------------------------
    # SCENARIO 1: No gaps provided - nothing to do
    # ----------------------------------------------------------------------
    if not gaps:
        logger.info("No gaps provided for adaptive search.")
        return {
            'status': 'completed',
            'message': 'No gaps provided for adaptive search.',
            'requires_action': False
        }
    
    # ----------------------------------------------------------------------
    # SCENARIO 2: First call - request approval for bulk operation
    # ----------------------------------------------------------------------
    if not tool_context.tool_confirmation:
        # Format gaps for user display
        logger.info("Requesting user approval for adaptive gap search...")
        gap_summary = "\n".join([
            f"  {i+1}. {gap.get('topic', 'Unknown')}: {gap.get('suggested_query', 'N/A')}"
            for i, gap in enumerate(gaps[:5])  # Show first 5
        ])
        
        if len(gaps) > 5:
            gap_summary += f"\n  ... and {len(gaps) - 5} more gaps"
        
        tool_context.request_confirmation(
            hint=(
                f"⚠️ Bulk Research Operation Detected\n\n"
                f"Found {len(gaps)} information gaps that require additional research:\n\n"
                f"{gap_summary}\n\n"
                f"This will trigger Phase 1-2 (Search + Quality Assessment) for each gap.\n"
                f"Approve to proceed?"
            ),
            payload={
                "num_gaps": len(gaps),
                "gaps": gaps,  # Store gaps in payload for resumption
                "operation": "adaptive_gap_research"
            },
        )
        
        # Return pending status - agent will wait for user response
        return {
            "status": "pending",
            "message": f"Awaiting approval for {len(gaps)} adaptive gap searches.",
            "requires_action": False,  # Agent should NOT proceed yet
            "gaps": gaps  # Keep gaps available for agent context
        }
    
    # ----------------------------------------------------------------------
    # SCENARIO 3A: User APPROVED - proceed with gap research
    # ----------------------------------------------------------------------
    if tool_context.tool_confirmation.confirmed:
        logger.info("User approved adaptive gap search. Proceeding...")
        # Retrieve gaps from confirmation payload (more reliable)
        confirmed_gaps = tool_context.tool_confirmation.payload.get('gaps', gaps)
        
        # Store in tool context state for agent access
        tool_context.state['adaptive_gaps'] = confirmed_gaps
        tool_context.state['gap_research_approved'] = True
        tool_context.state['gap_research_phase'] = 'executing'
        
        return {
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
        }
    
    # ----------------------------------------------------------------------
    # SCENARIO 3B: User REJECTED - skip gap research
    # ----------------------------------------------------------------------
    else:
        logger.info("User rejected adaptive gap search. Skipping...")
        tool_context.state['gap_research_approved'] = False
        tool_context.state['gap_research_phase'] = 'rejected'
        
        return {
            "status": "rejected",
            "message": "❌ User declined adaptive gap research. Proceeding with available information.",
            "requires_action": False,  # Agent should skip gap research
            "fallback_action": "proceed_to_synthesis"
        }
