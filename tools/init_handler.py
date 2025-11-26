

from google.genai import types
from ..agents.search_agent import create_search_agent
from ..agents.quality_agent import create_quality_agent
from ..agents.gap_agent import create_gap_agent
from ..agents.synthesis_agent import create_synthesis_agent
import logging
from ..utils.logger import setup_logger

logger = setup_logger("InitHandler", level=logging.INFO)

def setup_retry_config(attempts: int = 5, exp_base: int = 7, initial_delay: int = 1) -> types.HttpRetryOptions:
    """Sets up HTTP retry configuration for LLM calls."""
    logger.info("Setting up retry configuration...")
    
    return types.HttpRetryOptions(
    attempts=attempts,  # Maximum retry attempts
    exp_base=exp_base,  # Delay multiplier
    initial_delay=initial_delay,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

def create_specialist_agents(retry_config: types.HttpRetryOptions, search_toolset) -> dict:
    
        """Create all specialist agents"""
        
        logger.info("Creating Search Agent...")
        search_agent = create_search_agent(
            model='gemini-2.5-flash-lite', 
            tools=[search_toolset],
            retry_config=retry_config
        )

        logger.info("Creating Quality Agent...")
        quality_agent = create_quality_agent(model='gemini-2.5-flash-lite', retry_config=retry_config)

        logger.info("Creating Gap Agent...")
        gap_agent = create_gap_agent(retry_config=retry_config, search_toolset=search_toolset)
        
        logger.info("Creating Synthesis Agent...")
        synthesis_agent = create_synthesis_agent(model='gemini-2.5-flash-lite', retry_config=retry_config)
        
        return search_agent, quality_agent, gap_agent, synthesis_agent
    
"""TODO: integrate
async def _phase_5_adaptive(self, decision):
        ""Refine search based on gaps and user feedback""
        logger.info("Adaptive Loop → Refining based on gaps")
        
        queries = decision.get('modified_queries', [])
        
        for query in queries:
            if self.research_state['iteration_count'] >= self.research_state['max_iterations']:
                logger.warning("Max iterations reached")
                break
            
            self.research_state['iteration_count'] += 1
            
            logger.info(f"\n--- Iteration {self.research_state['iteration_count']} ---")
            logger.info(f"Refined Query: {query}")
            
            prompt = f""Execute search for: {query}

            Use duckduckgo_search tool to find sources.
            Focus on filling the identified gap.
            ""
            
            response = await self._invoke_agent(self.search_agent, prompt)
            
            self.research_state['search_history'].append({
                'iteration': self.research_state['iteration_count'],
                'query': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            logger.info(f"✓ Iteration {self.research_state['iteration_count']} complete")
"""

"""TODO: integrate
    def _format_sources(self, sources: list) -> str:
        ""Format sources for synthesis agent""
        if not sources:
            return "No sources available"
        
        formatted = ""
        for idx, source in enumerate(sources, 1):
            if isinstance(source, dict):
                title = source.get('title', 'Unknown Title')
                url = source.get('url', 'Unknown URL')
                snippet = source.get('snippet', '')[:200]
                formatted += f"{idx}. {title}\n   URL: {url}\n   {snippet}\n\n"
            else:
                formatted += f"{idx}. {str(source)}\n\n"
        
        return formatted
"""