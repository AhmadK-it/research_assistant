"""
Custom MCP Server for Web Search

This module implements a Model Context Protocol (MCP) server that provides
web search capabilities to ADK agents via the DuckDuckGo search engine.

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: Model Context Protocol (MCP)
═══════════════════════════════════════════════════════════════════════════════

MCP is a standardized protocol for connecting LLM agents to external tools
and data sources. Key benefits:

1. STANDARDIZATION - Common interface for tool integration across LLM systems
2. SEPARATION - Tools run in separate processes, improving reliability
3. DISCOVERABILITY - Agents can query available tools at runtime
4. SECURITY - Sandboxed execution prevents tools from affecting agent state

How it works in this project:
    ┌─────────────────┐       MCP Protocol       ┌─────────────────┐
    │   ADK Agent     │◄──────(stdio)──────────►│  MCP Server     │
    │ (search_agent)  │                          │ (this file)     │
    └─────────────────┘                          └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   DuckDuckGo    │
                                                 │   (ddgs pkg)    │
                                                 └─────────────────┘

═══════════════════════════════════════════════════════════════════════════════
TOOL REGISTRATION
═══════════════════════════════════════════════════════════════════════════════

FastMCP makes tool registration simple:

    @mcp.tool()
    def my_tool(param: str) -> List[Dict]:
        '''Docstring becomes tool description for agent'''
        return results

The decorated function becomes available to any ADK agent that connects
to this MCP server via McpToolset.

═══════════════════════════════════════════════════════════════════════════════
INTEGRATION WITH ADK
═══════════════════════════════════════════════════════════════════════════════

In agent.py, we connect to this server:

    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioServerParameters
    
    search_toolset = await McpToolset.from_server(
        connection_params=StdioServerParameters(
            command="python",
            args=["-m", "mcp_server.search_server"]
        )
    )
    
    search_agent = Agent(
        ...,
        tools=[search_toolset]  # Agent can now use duckduckgo_search
    )

═══════════════════════════════════════════════════════════════════════════════
WHY DUCKDUCKGO?
═══════════════════════════════════════════════════════════════════════════════

- NO API KEY REQUIRED - Reduces setup friction for demos
- FREE - No rate limits or costs for reasonable usage
- PRIVACY-FOCUSED - Aligns with responsible AI principles
- RELIABLE - Well-maintained ddgs package

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import logging
import sys

# ═══════════════════════════════════════════════════════════════════════════════
# PACKAGE COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

# CRITICAL: Force use of new ddgs package, not deprecated duckduckgo_search
# Remove old package from sys.modules if it was loaded
for mod_name in list(sys.modules.keys()):
    if 'duckduckgo_search' in mod_name:
        del sys.modules[mod_name]

# Now import the new package
try:
    from ddgs import DDGS
    logger = logging.getLogger(__name__)
    logger.info("✓ Using new ddgs package")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("✗ ddgs package not installed!")
    raise

logging.basicConfig(level=logging.INFO)

# ═══════════════════════════════════════════════════════════════════════════════
# MCP SERVER INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

# Initialize FastMCP server with a descriptive name
# This name appears in MCP tool discovery
mcp = FastMCP("Research Search Server")


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def duckduckgo_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo.
    
    This is the primary search tool used by the Search Agent in Phase 1
    of the research workflow. It returns structured results that can be
    evaluated by the Quality Agent in Phase 2.
    
    Args:
        query: Search query string. Best results come from specific,
               targeted queries (5-15 words). Avoid single-word queries.
        max_results: Maximum number of results to return (default: 10).
                     Higher values increase latency and token usage.
        
    Returns:
        List of search result dictionaries, each containing:
        - title: Page title
        - url: Full URL to the page
        - snippet: Text excerpt from the page
        - source: "DuckDuckGo" (for attribution)
        
    Example:
        >>> duckduckgo_search("AI healthcare outcomes 2024 studies", 5)
        [
            {
                "title": "AI in Healthcare: 2024 Outcomes Report",
                "url": "https://example.com/ai-healthcare-2024",
                "snippet": "A comprehensive study of AI implementation...",
                "source": "DuckDuckGo"
            },
            ...
        ]
    """
    logger.info(f"MCP Server: Searching for '{query}'")
    
    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "DuckDuckGo"
                })
            
            logger.info(f"MCP Server: Found {len(results)} results")
            return results
            
    except Exception as e:
        logger.error(f"MCP Server: Search failed - {e}")
        return [{"error": str(e)}]


# ═══════════════════════════════════════════════════════════════════════════════
# SERVER ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    # This allows ADK to communicate via stdin/stdout
    mcp.run(transport="stdio")