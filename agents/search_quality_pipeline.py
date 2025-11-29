"""
Search + Quality Pipeline (SequentialAgent)

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: SequentialAgent Pattern
═══════════════════════════════════════════════════════════════════════════════

This module demonstrates the SequentialAgent pattern from Google ADK, which
automatically chains multiple agents in a fixed order:

    ┌────────────────────────────────────────────────────────────────┐
    │                 SEARCH_QUALITY_PIPELINE                        │
    │                   (SequentialAgent)                            │
    │                                                                │
    │   ┌─────────────┐          ┌─────────────────┐                │
    │   │   Search    │ ───────▶ │    Quality      │                │
    │   │  Specialist │   auto   │   Assessor      │                │
    │   └─────────────┘          └─────────────────┘                │
    │        ▲                          │                            │
    │        │                          ▼                            │
    │    User Query              Assessed Results                    │
    └────────────────────────────────────────────────────────────────┘

Key Benefits:
- Guaranteed execution order
- Automatic output passing between stages
- Simplified orchestration (no manual sequencing)
- Atomic "unit of work" for phases 1+2

Usage:
    Instead of calling search_specialist then quality_assessor separately,
    the coordinator can call this pipeline ONCE to get searched AND assessed
    results in a single operation.

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.agents import SequentialAgent
from .search_agent import create_search_agent
from .quality_agent import create_quality_agent
import logging

# Get logger
logger = logging.getLogger("ResearchAssistant.Pipeline")


def create_search_quality_pipeline(
    model: str = 'gemini-2.5-flash',
    retry_config=None,
    search_toolset=None,
    generation_config=None
):
    """
    Create a SequentialAgent that chains Search → Quality Assessment.
    
    ═══════════════════════════════════════════════════════════════════════════
    COURSE CONCEPT: SequentialAgent
    ═══════════════════════════════════════════════════════════════════════════
    
    SequentialAgent automatically executes sub-agents in order:
    1. search_specialist receives the query and finds sources
    2. quality_assessor receives search output and evaluates credibility
    
    The SequentialAgent handles:
    - Passing output from search to quality
    - Maintaining conversation context
    - Aggregating final results
    
    Args:
        model: LLM model identifier
        retry_config: HTTP retry configuration
        search_toolset: MCP search tool for the search agent
        generation_config: Generation parameters
        
    Returns:
        SequentialAgent: A pipeline that runs Search → Quality automatically
    """
    
    logger.info("Creating Search+Quality SequentialAgent Pipeline...")
    
    # Create the individual agents
    search_agent = create_search_agent(
        model=model,
        tools=[search_toolset] if search_toolset else [],
        retry_config=retry_config,
        generation_config=generation_config
    )
    
    quality_agent = create_quality_agent(
        model=model,
        retry_config=retry_config,
        generation_config=generation_config
    )
    
    # Create the SequentialAgent pipeline
    # This chains: search_specialist → quality_assessor
    pipeline = SequentialAgent(
        name="search_quality_pipeline",
        description="""
        Combined Search + Quality Assessment Pipeline.
        
        This pipeline performs two operations in sequence:
        1. Web search using DuckDuckGo (via MCP)
        2. Quality assessment of found sources
        
        Returns: Searched and quality-assessed research results ready for analysis.
        """,
        sub_agents=[search_agent, quality_agent]
    )
    
    logger.info("✅ Search+Quality Pipeline created (SequentialAgent)")
    
    return pipeline


# ═══════════════════════════════════════════════════════════════════════════════
# EDUCATIONAL NOTE
# ═══════════════════════════════════════════════════════════════════════════════
#
# SequentialAgent vs Manual Orchestration:
#
# MANUAL (what the root agent does for Gap → Synthesis):
#   coordinator.call(search_specialist, query)
#   results = get_output()
#   coordinator.call(quality_assessor, results)
#   
# SEQUENTIAL (this pipeline):
#   coordinator.call(search_quality_pipeline, query)
#   # Automatically runs both and returns combined result
#
# When to use SequentialAgent:
# - Fixed, predictable order (always search THEN assess)
# - No conditional logic between stages
# - Want to treat multiple agents as a single "unit"
#
# When to use manual orchestration:
# - Conditional execution (skip quality if no results)
# - Need to inspect intermediate results
# - Complex decision logic between stages
#
# Our hybrid approach uses BOTH patterns:
# - SequentialAgent for Search+Quality (always together)
# - Manual orchestration for Gap+HITL+Synthesis (conditional)
# ═══════════════════════════════════════════════════════════════════════════════
