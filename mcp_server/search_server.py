"""
Custom MCP Server for Web Search
Uses DuckDuckGo via ddgs package (no API key needed)
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import logging
import sys

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

# Initialize FastMCP server
mcp = FastMCP("Research Search Server")

@mcp.tool()
def duckduckgo_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10)
        
    Returns:
        List of search results with title, url, and snippet
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


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio")