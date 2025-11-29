"""
Specialist Agents Package

This package contains all specialist agents used by the Research Agent system.

Agents:
- search_agent: Web search via MCP DuckDuckGo
- quality_agent: Source credibility assessment
- gap_agent: Information completeness analysis
- synthesis_agent: Report synthesis with AgentTool(formatter)
- formatter_agent: Code-based formatting with BuiltInCodeExecutor

Pipelines (SequentialAgent / ParallelAgent):
- search_quality_pipeline: Combined Search → Quality (SequentialAgent)
- parallel_gap_agent: Static ParallelAgent with 3 fixed slots
"""

from .search_agent import create_search_agent
from .quality_agent import create_quality_agent
from .gap_agent import create_gap_agent
from .synthesis_agent import create_synthesis_agent
from .formatter_agent import create_formatter_agent
from .search_quality_pipeline import create_search_quality_pipeline
from .parallel_gap_agent import create_parallel_gap_agent

__all__ = [
    # Individual agents
    'create_search_agent',
    'create_quality_agent', 
    'create_gap_agent',
    'create_synthesis_agent',
    'create_formatter_agent',
    # Pipeline agents
    'create_search_quality_pipeline',
    'create_parallel_gap_agent',
]
