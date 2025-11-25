"""Synthesis agent for creating comprehensive research reports"""

from google.adk.agents import Agent
import logging
from google.adk.models.google_llm import Gemini
logger = logging.getLogger(__name__)


"""
TODO: below method to be integrated into search agent below as functional tool as how it is important

    async def _phase_6_synthesis(self):
        ""Generate final research report""
        logger.info("=" * 60)
        logger.info("Synthesis Agent → Creating comprehensive report")
        logger.info("=" * 60)
        
        high_quality = self.research_state.get('high_quality_results', [])
        medium_quality = self.research_state.get('medium_quality_results', [])
        
        prompt = f""Create comprehensive research report on: {self.research_state['query']}

        High quality sources ({len(high_quality)}):
        {self._format_sources(high_quality)}

        Medium quality sources ({len(medium_quality)}):
        {self._format_sources(medium_quality)}

        Generate a structured report with:
        - Executive Summary
        - Key Findings (organized by theme)
        - Source Citations
        - Confidence Levels for major claims
        - Identified Gaps or Uncertainties

        Format as professional markdown. Focus on clarity and accuracy.
        ""
        
        report = await self._invoke_agent(self.synthesis_agent, prompt)
        
        self.research_state['final_report'] = str(report)
        
        logger.info("✓ Report synthesis complete")
        logger.info("=" * 60)
        
        return {'report': str(report)}
"""


def create_synthesis_agent(model: str = 'gemini-2.5-flash-lite', retry_config=None):
    """Creates agent for synthesizing research findings into comprehensive reports
    
    Args:
        model: Model identifier (default: gemini-2.5-flash-lite)
    
    Returns:
        Agent: Configured synthesis specialist agent
    """
    
    return Agent(
        model=Gemini(model=model, retry_options=retry_config),
        name='research_synthesizer',
        description='Expert at creating comprehensive research reports from gathered sources',
        instruction="""
        You are a research synthesis specialist. Your job is to:

        1. **Analyze All Sources:**
        - Review all provided high and medium quality sources
        - Identify key themes, patterns, and insights
        - Note any contradictions or disagreements between sources
        - Assess the strength of evidence for major claims

        2. **Organize Information:**
        - Group related information by major themes/topics
        - Identify the most important findings
        - Highlight areas of consensus vs. disagreement
        - Flag any surprising or significant discoveries

        3. **Create Structured Report:**
        - Executive Summary (2-3 sentences capturing main findings)
        - Key Findings (organized by theme with supporting details)
        - Source Citations (clear attribution of claims)
        - Confidence Levels (indicate strength of evidence: High/Medium/Low)
        - Identified Gaps (what remains uncertain or unexplored)

        4. **Writing Guidelines:**
        - Use clear, accessible language (avoid jargon when possible)
        - Be objective and data-driven
        - Distinguish between facts and interpretations
        - Provide proper context for findings
        - Include specific examples from sources

        5. **Output Format:**
        Format your report as professional markdown with:
        - Clear headings for each section
        - Bullet points for key findings
        - Proper citations in format: [Source Title - Author/Organization]
        - Emphasis on evidence-based conclusions

        **Quality Standards:**
        - Accuracy: All claims must be traceable to sources
        - Clarity: Language should be accessible but precise
        - Completeness: Address the original research question thoroughly
        - Objectivity: Present findings without undue bias
        - Usefulness: Organize information to help reader understand the topic
        """
    )
