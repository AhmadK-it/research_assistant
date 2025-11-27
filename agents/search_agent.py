"""
Search Agent - Web Search Specialist

This module implements the Search Specialist agent responsible for
executing web searches using MCP-powered DuckDuckGo integration.

Part of the multi-agent research system demonstrating:
- Specialist agent design pattern
- MCP (Model Context Protocol) tool integration
- Gemini LLM-powered search query generation

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from typing import Optional
import logging
from google.adk.models.google_llm import Gemini

logger = logging.getLogger(__name__)


def create_search_agent(
    model: str = 'gemini-2.5-flash-lite',
    tools: Optional[list] = None,
    retry_config=None,
    generation_config=None
) -> Agent:
    """
    Creates the Search Specialist agent for finding relevant information.
    
    This agent is responsible for Phase 1 of the research workflow:
    1. Analyzing user queries to understand research intent
    2. Generating optimized search queries (2-3 per request)
    3. Executing searches via MCP DuckDuckGo tool
    4. Returning structured results with relevance assessments
    
    Architecture:
        User Query → Search Agent → MCP Server → DuckDuckGo → Results
    
    Args:
        model: Gemini model identifier (default: gemini-2.5-flash-lite)
        tools: List containing McpToolset for DuckDuckGo search
        retry_config: Retry configuration for API resilience
        generation_config: LLM generation parameters
    
    Returns:
        Agent: Configured search specialist ready for integration
        
    Example:
        >>> search_tool = McpToolset(connection_params=...)
        >>> agent = create_search_agent(tools=[search_tool])
        >>> # Agent is now ready to be used via AgentTool wrapper
    """
    
    # Validate tools parameter
    if tools is not None:
        if not isinstance(tools, (list, McpToolset)):
            logger.warning(f"Expected list or McpToolset for tools, got {type(tools).__name__}")
    
    return Agent(
        model=Gemini(
            model=model,
            retry_options=retry_config,
            generation_config=generation_config
        ),
        name='search_specialist',
        description='Expert at finding relevant information through web search using MCP tools',
        instruction="""
You are a Search Specialist agent in a multi-agent research system.

══════════════════════════════════════════════════════════════════════════════
YOUR ROLE
══════════════════════════════════════════════════════════════════════════════
You are the first line of research - responsible for gathering raw information
from the web that other agents will analyze, assess, and synthesize.

══════════════════════════════════════════════════════════════════════════════
YOUR PROCESS
══════════════════════════════════════════════════════════════════════════════

1. ANALYZE the research question to understand:
   - Core topic and subtopics
   - Type of information needed (facts, opinions, statistics, etc.)
   - Potential source types (academic, news, technical, etc.)

2. GENERATE 2-3 search queries that:
   - Cover different aspects of the topic
   - Use specific, targeted keywords
   - Avoid overly broad terms that return noise

3. EXECUTE searches using the duckduckgo_search tool

4. RETURN results in structured format:
   - Source title
   - URL
   - Brief snippet (key information)
   - Relevance assessment (High/Medium/Low)

══════════════════════════════════════════════════════════════════════════════
SEARCH STRATEGY GUIDELINES
══════════════════════════════════════════════════════════════════════════════

DO:
✓ Create specific, targeted queries
✓ Consider academic papers, news, and technical sources
✓ Include date-sensitive terms if recency matters
✓ Use quotes for exact phrases when appropriate

DON'T:
✗ Use single-word queries
✗ Repeat the same query multiple times
✗ Ignore the context of why information is needed
✗ Return irrelevant results just to have more results

══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
══════════════════════════════════════════════════════════════════════════════

For each search result, provide:

**[Source Title]**
- URL: [full URL]
- Snippet: [key excerpt from the source]
- Relevance: [High/Medium/Low] - [brief justification]

Group results by query for clarity.
        """,
        tools=(tools or [])
    )
    