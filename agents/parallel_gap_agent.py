"""
Parallel Gap Agent - ADK ParallelAgent for Concurrent Gap Research

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: ParallelAgent Pattern (Static Configuration)
═══════════════════════════════════════════════════════════════════════════════

This module demonstrates the ParallelAgent pattern from Google ADK with a
FIXED number of parallel pipelines (3 gaps maximum).

By fixing the pipeline count, we can:
1. Create ParallelAgent at MODULE LOAD TIME (not runtime)
2. Wire it as a regular AgentTool (like other agents)
3. Avoid asyncio complexity - ADK handles parallelism internally

    ┌────────────────────────────────────────────────────────────────────────┐
    │                     ParallelAgent (Fixed 3 Slots)                      │
    │                                                                        │
    │   Slot 1 ──▶ [search_quality_pipeline] ──┐                            │
    │   Slot 2 ──▶ [search_quality_pipeline] ──┼──▶ Combined Results        │
    │   Slot 3 ──▶ [search_quality_pipeline] ──┘         │                  │
    │                                                    ▼                   │
    │                                              Root Agent                │
    │                                                   │                    │
    │                                                   ▼                    │
    │                                           synthesis_agent              │
    └────────────────────────────────────────────────────────────────────────┘

Why Fixed Count?
- ParallelAgent needs sub_agents at creation time
- By fixing to 3, we create at module load (compile time)
- Can be wired as AgentTool just like search_quality_pipeline
- Root agent provides all 3 gap queries in one prompt

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.agents import ParallelAgent
from .search_quality_pipeline import create_search_quality_pipeline
import logging

logger = logging.getLogger("ResearchAssistant.ParallelGapAgent")

# Fixed number of parallel gap research slots
MAX_PARALLEL_GAPS = 3


def create_parallel_gap_agent(
    model: str,
    retry_config,
    search_toolset,
    generation_config
) -> ParallelAgent:
    """
    Create a ParallelAgent with FIXED 3 slots for gap research.
    
    ═══════════════════════════════════════════════════════════════════════════
    COURSE CONCEPT: Static ParallelAgent Configuration
    ═══════════════════════════════════════════════════════════════════════════
    
    Unlike dynamic creation, this approach:
    - Creates ParallelAgent at module load time
    - Uses a fixed number of sub-agents (3 pipelines)
    - Can be wired as AgentTool to root agent
    - ADK handles parallel execution internally
    
    The root agent will call this with a prompt containing up to 3 gap queries.
    Each pipeline handles one gap, and results are combined automatically.
    
    Args:
        model: LLM model to use
        retry_config: HTTP retry configuration
        search_toolset: MCP search tool
        generation_config: Generation parameters
        
    Returns:
        ParallelAgent with 3 search_quality_pipeline sub-agents
    """
    
    logger.info(f"🔧 Creating ParallelAgent with {MAX_PARALLEL_GAPS} fixed slots...")
    
    # Create fixed number of pipeline instances
    pipelines = []
    for i in range(MAX_PARALLEL_GAPS):
        pipeline = create_search_quality_pipeline(
            model=model,
            retry_config=retry_config,
            search_toolset=search_toolset,
            generation_config=generation_config
        )
        pipeline.name = f'gap_researcher_{i+1}'
        pipeline.description = f'Parallel gap researcher slot {i+1} - researches and assesses one gap topic'
        pipelines.append(pipeline)
        logger.info(f"  ✓ Created pipeline slot {i+1}")
    
    # Create ParallelAgent with all pipelines
    parallel_agent = ParallelAgent(
        name='parallel_gap_researcher',
        description=f'''Researches EXACTLY {MAX_PARALLEL_GAPS} knowledge gaps simultaneously.
        
This agent has {MAX_PARALLEL_GAPS} parallel research slots. Each slot is a search_quality_pipeline.

IMPORTANT: Always provide exactly {MAX_PARALLEL_GAPS} gap queries, one per line:
- Slot 1 researches the first gap
- Slot 2 researches the second gap  
- Slot 3 researches the third gap

All {MAX_PARALLEL_GAPS} slots run in parallel for faster results.

Example prompt format:
"Research these 3 gaps:
1. [First gap query]
2. [Second gap query]
3. [Third gap query]"
''',
        sub_agents=pipelines
    )
    
    logger.info(f"✅ ParallelAgent created with {MAX_PARALLEL_GAPS} sub-agents (static)")
    
    return parallel_agent


# ═══════════════════════════════════════════════════════════════════════════════
# EDUCATIONAL NOTES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Static vs Dynamic ParallelAgent
# ────────────────────────────────
# 
# STATIC (this approach):
#   ✓ Created at module load time
#   ✓ Wired as AgentTool (like other agents)
#   ✓ No asyncio needed - ADK handles parallelism
#   ✓ Simple integration with root agent
#   ✗ Fixed capacity (3 gaps max)
#   ✗ Extra slots unused if fewer gaps
#
# DYNAMIC (alternative in parallel_gap_tool.py):
#   ✓ Exact number of agents per gap count
#   ✓ More flexible capacity
#   ✗ Requires FunctionTool wrapper
#   ✗ Needs asyncio for execution
#   ✗ More complex integration
#
# For this course demonstration, STATIC is preferred because:
# 1. Shows pure ADK ParallelAgent pattern (no asyncio boilerplate)
# 2. Consistent with how other agents are wired (AgentTool)
# 3. Simpler to understand and maintain
# 4. 3 gaps is a reasonable limit for most research queries
#
# ═══════════════════════════════════════════════════════════════════════════════