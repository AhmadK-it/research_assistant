"""Search agent for web research"""

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from typing import Optional
import logging
from google.adk.models.google_llm import Gemini

logger = logging.getLogger(__name__)

"""
TODO: below method to be integrated into search agent below as functional tool as how it is important

    async def _phase_1_search(self, query: str):
        ""Execute initial search via MCP""
        logger.info("Search Agent → DuckDuckGo (via MCP)")
        
        prompt = f""Research question: {query}

        Generate 2 different search queries and use duckduckgo_search tool for each.
        Find comprehensive, high-quality sources.

        Return results in JSON format.
        ""
        
        response = await self._invoke_agent(self.search_agent, prompt)
        results = {'results': [], 'agent_response': str(response)}
        
        self.research_state['search_history'].append({
            'iteration': 0,
            'query': query,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        logger.info(f"✓ Initial search complete")
        return results
"""
def create_search_agent(model: str = 'gemini-2.5-flash-lite', tools: Optional[list] = None, retry_config=None) -> Agent:
    """Creates specialist search agent for finding relevant information
    
    Args:
        model: Model identifier (default: gemini-2.5-flash-lite)
        tools: Optional list of tools/McpToolset instances to provide to agent
    
    Returns:
        Agent: Configured search specialist agent
    """
    
    if tools is not None:
        if not isinstance(tools, (list, McpToolset)):
            logger.warning(f"Expected list or McpToolset for tools, got {type(tools).__name__}")
    
    return Agent(
        model=Gemini(model=model, retry_options=retry_config),
        name='search_specialist',
        description='Expert at finding relevant information through web search',
        instruction="""
        You are a search specialist agent. Your job is to:

        1. Analyze the user's research question
        2. Generate 2-3 effective search queries that will find diverse, high-quality sources
        3. Execute those searches
        4. Return results in a structured format

        Guidelines:
        - Create search queries that are specific and targeted
        - Avoid overly broad queries that return too much noise
        - Consider different angles: academic papers, news articles, technical blogs
        - Prioritize authoritative sources

        When returning results, format them clearly with:
        - Source title
        - URL
        - Brief snippet
        - Your assessment of relevance (High/Medium/Low)
        """,
        tools=(tools or [])
    )
    