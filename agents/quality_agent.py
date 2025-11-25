"""Quality assessment agent for source credibility evaluation"""

from google.adk.agents import Agent
import logging
from google.adk.models.google_llm import Gemini

logger = logging.getLogger(__name__)


"""
TODO: below method to be integrated into search agent below as functional tool as how it is important

    async def _phase_2_quality(self, search_results):
        ""Evaluate sources for credibility and relevance""
        logger.info("Quality Agent → Evaluating sources")
        
        prompt = f""Research Question: {self.research_state['query']}

        Search Results:
        {search_results['agent_response']}

        Evaluate each source for:
        1. Credibility (1-10)
        2. Relevance (1-10)
        3. Recency (1-10)

        Calculate overall scores and categorize as high/medium/low quality.
        Return in JSON format.
        ""
        
        response = await self._invoke_agent(self.quality_agent, prompt)
        self.research_state['high_quality_results'] = ['Placeholder - will parse from response']
        
        logger.info(f"✓ Quality filtering complete")
        return {'evaluation': str(response)}
"""


def create_quality_agent(model: str = 'gemini-2.5-flash-lite', retry_config=None):
    """Creates agent for evaluating search result quality and credibility"""
    
    return Agent(
        model=Gemini(model=model, retry_options=retry_config),
        name='quality_assessor',
        description='Expert at evaluating source credibility and relevance',
        instruction="""
        You are a quality assessment specialist. Your job is to:

        1. Evaluate each search result for:
        - Source credibility (Is this from a reputable publisher?)
        - Relevance (Does this actually answer the research question?)
        - Recency (Is this information current?)
        - Depth (Is this superficial or substantive?)

        2. For each result, assign scores:
        - Credibility: 1-10 (10 = peer-reviewed journal, 1 = random blog)
        - Relevance: 1-10 (10 = directly answers question, 1 = tangentially related)
        - Overall: Average of credibility + relevance

        3. Flag results that score below 6/10 overall as "Low Quality - Consider Removing"

        4. Identify the TOP 3 highest-quality sources

        Guidelines:
        - Academic papers (.edu, peer-reviewed journals) = High credibility
        - Government sources (.gov) = High credibility
        - Established news organizations = Medium-High credibility
        - Personal blogs, forums = Low-Medium credibility (unless expert author)
        - Consider publication date (prefer recent for current topics)

        Return your assessment in a structured format.
        """
    )
    