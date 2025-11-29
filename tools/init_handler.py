"""
Agent Initialization Handler - Factory for All Agents

This module provides the single factory function to create and configure ALL
agents used in the Research Agent system.

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: Agent Factory Pattern
═══════════════════════════════════════════════════════════════════════════════

Centralizing agent creation provides:
1. Consistent configuration across all agents
2. Easy modification of shared settings (model, retry, generation config)
3. Clear dependency injection (search_toolset only where needed)
4. Simplified testing and mocking

═══════════════════════════════════════════════════════════════════════════════
AGENT ROSTER
═══════════════════════════════════════════════════════════════════════════════

LlmAgents:
1. Search Agent    - Web search via MCP DuckDuckGo
2. Quality Agent   - Source credibility assessment
3. Gap Agent       - Information completeness analysis
4. Synthesis Agent - Report generation with AgentTool(formatter)

Pipelines:
5. Search+Quality Pipeline - SequentialAgent (Search → Quality)
6. Parallel Gap Agent      - ParallelAgent (3 fixed slots)

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.genai import types
from ..agents.search_agent import create_search_agent
from ..agents.quality_agent import create_quality_agent
from ..agents.gap_agent import create_gap_agent
from ..agents.synthesis_agent import create_synthesis_agent
from ..agents.search_quality_pipeline import create_search_quality_pipeline
from ..agents.parallel_gap_agent import create_parallel_gap_agent
import logging
from ..utils.logger import setup_logger

logger = setup_logger("InitHandler", level=logging.INFO)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def setup_retry_config(
    attempts: int = 6, 
    exp_base: int = 3, 
    initial_delay: int = 1
) -> types.HttpRetryOptions:
    """
    Sets up HTTP retry configuration for LLM calls.
    
    Demonstrates: Resilient API calls with exponential backoff
    
    Args:
        attempts: Maximum number of retry attempts
        exp_base: Exponential backoff multiplier
        initial_delay: Initial delay in seconds
        
    Returns:
        Configured HttpRetryOptions
    """
    logger.info("Setting up retry configuration...")
    
    return types.HttpRetryOptions(
        attempts=attempts,
        exp_base=exp_base,
        initial_delay=initial_delay,
        http_status_codes=[429, 500, 503, 504],  # Retry on rate limit and server errors
    )


def setup_generation_config(
    max_output_tokens: int = 8192, 
    temperature: float = 0.7
) -> types.GenerateContentConfig:
    """
    Sets up generation configuration for LLM responses.
    
    Args:
        max_output_tokens: Maximum tokens in response
        temperature: Creativity level (0.0-1.0)
        
    Returns:
        Configured GenerateContentConfig
    """
    return types.GenerateContentConfig(
        max_output_tokens=max_output_tokens,
        temperature=temperature,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED AGENT FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def create_all_agents(
    model: str = 'gemini-2.5-flash', 
    retry_config: types.HttpRetryOptions = None, 
    search_toolset = None, 
    generation_config = None
):
    """
    Create ALL agents with consistent configuration.
    
    ═══════════════════════════════════════════════════════════════════════════
    COURSE CONCEPT: Unified Factory Pattern
    ═══════════════════════════════════════════════════════════════════════════
    
    This single factory creates:
    - 4 LlmAgents (search, quality, gap, synthesis)
    - 1 SequentialAgent (search_quality_pipeline)
    - 1 ParallelAgent (parallel_gap_agent with 3 slots)
    
    All agents share the same configuration for consistency.
    
    Args:
        model: The LLM model to use for all agents
        retry_config: HTTP retry configuration
        search_toolset: MCP search tool (only given to Search Agent)
        generation_config: Generation parameters
        
    Returns:
        Dict with all agents:
        {
            'search': LlmAgent,
            'quality': LlmAgent,
            'gap': LlmAgent,
            'synthesis': LlmAgent,
            'search_quality_pipeline': SequentialAgent,
            'parallel_gap_agent': ParallelAgent,
        }
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # LlmAgents (4 specialists)
    # ─────────────────────────────────────────────────────────────────────────
    
    logger.info("Creating Search Agent...")
    search_agent = create_search_agent(
        model=model, 
        tools=[search_toolset],
        retry_config=retry_config,
        generation_config=generation_config
    )

    logger.info("Creating Quality Agent...")
    quality_agent = create_quality_agent(
        model=model, 
        retry_config=retry_config, 
        generation_config=generation_config
    )
    
    logger.info("Creating Gap Agent...")
    gap_agent = create_gap_agent(
        model=model,
        retry_config=retry_config, 
        search_toolset=None,  # No search tool to avoid nested AgentTool
        generation_config=generation_config
    )
    
    logger.info("Creating Synthesis Agent...")
    synthesis_agent = create_synthesis_agent(
        model=model, 
        retry_config=retry_config, 
        generation_config=generation_config
    )
    
    # ─────────────────────────────────────────────────────────────────────────
    # SequentialAgent (Search → Quality pipeline)
    # ─────────────────────────────────────────────────────────────────────────
    
    logger.info("Creating Search+Quality Pipeline (SequentialAgent)...")
    search_quality_pipeline = create_search_quality_pipeline(
        model=model,
        retry_config=retry_config,
        search_toolset=search_toolset,
        generation_config=generation_config
    )
    
    # ─────────────────────────────────────────────────────────────────────────
    # ParallelAgent (3 fixed slots for gap research)
    # ─────────────────────────────────────────────────────────────────────────
    
    logger.info("Creating Parallel Gap Agent (ParallelAgent with 3 slots)...")
    parallel_gap_agent = create_parallel_gap_agent(
        model=model,
        retry_config=retry_config,
        search_toolset=search_toolset,
        generation_config=generation_config
    )
    
    logger.info("✅ All agents created successfully")
    
    return {
        'search': search_agent,
        'quality': quality_agent,
        'gap': gap_agent,
        'synthesis': synthesis_agent,
        'search_quality_pipeline': search_quality_pipeline,
        'parallel_gap_agent': parallel_gap_agent,
    }
