"""
Quality Assessment Agent - Source Credibility Specialist

This module implements the Quality Assessor agent responsible for
evaluating search results for credibility, relevance, and reliability.

Part of the multi-agent research system demonstrating:
- Specialist agent design pattern (single responsibility)
- Quality filtering in research pipelines
- LLM-powered content evaluation

Architecture Position: Phase 2 of 5-phase workflow
    [Search] → [Quality] → [Gap] → [HITL] → [Synthesis]
                  ↑ YOU ARE HERE

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.agents import Agent
import logging
from google.adk.models.google_llm import Gemini

logger = logging.getLogger(__name__)


def create_quality_agent(model: str = 'gemini-2.5-flash-lite', retry_config=None, generation_config=None) -> Agent:
    """
    Creates the Quality Assessor agent for evaluating source credibility.
    
    This agent is responsible for Phase 2 of the research workflow:
    1. Receiving search results from Phase 1 (Search Agent)
    2. Evaluating each source on credibility, relevance, recency, and depth
    3. Scoring sources on a 1-10 scale across dimensions
    4. Flagging low-quality sources for removal
    5. Identifying top 3 highest-quality sources
    
    Scoring Criteria:
        - Credibility: Source reputation (peer-reviewed = 10, random blog = 1)
        - Relevance: How directly the source answers the research question
        - Recency: Currency of information (important for evolving topics)
        - Depth: Substantive analysis vs. superficial coverage
    
    Args:
        model: Gemini model identifier (default: gemini-2.5-flash-lite)
        retry_config: Retry configuration for API resilience
        generation_config: LLM generation parameters
    
    Returns:
        Agent: Configured quality assessment specialist
        
    Example:
        >>> agent = create_quality_agent()
        >>> # Agent evaluates sources and returns quality scores
    """
    
    return Agent(
        model=Gemini(model=model, retry_options=retry_config, generation_config=generation_config),
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
    