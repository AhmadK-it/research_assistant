"""Gap analysis agent for identifying research gaps"""

from google.adk.agents import Agent
import logging
from google.adk.models.google_llm import Gemini

logger = logging.getLogger(__name__)


"""
TODO: below method to be integrated into search agent below as functional tool as how it is important

        async def _phase_3_gaps(self):
        ""Analyze information gaps and completeness""
        logger.info("Gap Agent → Analyzing completeness")
        
        prompt = f""Research Question: {self.research_state['query']}

        Current findings summary:
        - High quality sources: {len(self.research_state['high_quality_results'])}
        - Search iterations: {self.research_state['iteration_count']}

        Analyze:
        1. Is this sufficient to answer the question comprehensively?
        2. What specific information is missing?
        3. What additional searches would help?

        Return in JSON format with critical_gaps and recommendation.
        ""
        
        response = await self._invoke_agent(self.gap_agent, prompt)
        
        gaps = {
            'assessment': 'Mostly Complete',
            'critical_gaps': [
                {
                    'gap': 'Need more recent sources from 2024',
                    'suggested_query': f"{self.research_state['query']} 2024 recent",
                    'importance': 'Current information is critical'
                }
            ],
            'recommendation': 'Suggest additional search for completeness',
            'agent_analysis': str(response)
        }
        
        self.research_state['gaps_identified'] = gaps
        logger.info(f"✓ Gap analysis: {gaps['assessment']}")
        return gaps

        
"""

def create_gap_agent(model: str = 'gemini-2.5-flash-lite', retry_config=None):
    """Creates agent for identifying missing information in research coverage"""
    
    return Agent(
        model=Gemini(model=model, retry_options=retry_config),
        name='gap_identifier',
        description='Expert at identifying what information is missing',
        instruction="""
        You are a research gap analyst. Your job is to:

        1. Review the research question and what's been found so far
        2. Identify what's MISSING to fully answer the question
        3. Categorize gaps:
        - Critical gaps (without this, we can't answer the question)
        - Important gaps (would significantly improve the answer)
        - Nice-to-have gaps (would add depth but not essential)

        4. For each gap, suggest:
        - Specific search queries to fill it
        - What type of source would be ideal (academic, news, technical, etc.)
        - Why this gap matters

        5. Output format:
        {
            "assessment": "Overall completeness (Complete/Mostly Complete/Incomplete)",
            "critical_gaps": [
            {
                "gap": "Description of what's missing",
                "suggested_query": "Specific search query to fill gap",
                "source_type": "Type of source needed",
                "importance": "Why this matters"
            }
            ],
            "important_gaps": [...],
            "recommendation": "Should we continue searching? Yes/No and why"
        }

        Be specific and actionable in your recommendations.
        """
    )
    