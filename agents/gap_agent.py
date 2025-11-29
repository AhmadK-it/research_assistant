"""
Gap Analysis Agent - Research Completeness Specialist

This module implements the Gap Identifier agent responsible for
analyzing research results to identify missing or incomplete information.

Part of the multi-agent research system demonstrating:
- Specialist agent design pattern (single responsibility)
- Iterative research refinement
- LLM-powered meta-analysis of search coverage

Architecture Position: Phase 3 of 5-phase workflow
    [Search] → [Quality] → [Gap] → [HITL] → [Synthesis]
                            ↑ YOU ARE HERE

Key Feature: This agent's output feeds into the HITL (Human-in-the-Loop)
confirmation step, where users can approve or reject suggested gap searches.

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.agents import Agent
import logging
from google.adk.models.google_llm import Gemini

logger = logging.getLogger(__name__)


def create_gap_agent( model='gemini-2.5-flash-lite', retry_config=None, search_toolset=None, generation_config=None) -> Agent:
    """
    Creates the Gap Identifier agent for finding missing information.
    
    This agent is responsible for Phase 3 of the research workflow:
    1. Analyzing search results and quality assessments
    2. Identifying 5 dimensions of potential gaps:
       - Temporal: Missing recent developments or historical context
       - Topical: Uncovered subtopics or perspectives
       - Methodological: Missing data types (quantitative/qualitative)
       - Source: Gaps in authoritative or diverse sources
       - Practical: Missing implementation or real-world details
    3. Prioritizing gaps by importance (high/medium/low)
    4. Generating optimized search queries to fill each gap
    
    Output Format:
        Returns JSON array of gap objects with fields:
        - topic: Brief description of what's missing
        - suggested_query: Optimized search query
        - priority: high/medium/low
        - rationale: Why this gap matters
        - gap_type: One of the 5 dimensions
    
    Args:
        retry_config: Retry configuration for API resilience
        search_toolset: DEPRECATED - No longer used to prevent nested agent call errors
        generation_config: LLM generation parameters
    
    Returns:
        Agent: Configured gap analysis specialist
        
    Note:
        The Gap Agent does NOT have search tools. It ONLY identifies gaps.
        Actual gap research is performed by the coordinator in Phase 4,
        which calls search_specialist directly for each approved gap.
        This design prevents nested AgentTool calls that cause NoneType errors.
        
    Integration with HITL:
        The gaps identified by this agent are presented to users via
        the conduct_adaptive_gap_search tool, which asks for confirmation
        before executing additional searches.
    """
    
    return Agent(
        model=Gemini(
            model='gemini-2.5-flash-lite', 
            retry_options=retry_config,
            generation_config=generation_config
        ),
        name='gap_identifier',
        description='Expert at identifying what information is missing',
        instruction="""
        **ROLE: Information Gap Analyst**
        
        You analyze research results to identify missing or incomplete information.
        
        ═══════════════════════════════════════════════════════════════════════
        📋 INPUT ANALYSIS
        ═══════════════════════════════════════════════════════════════════════
        
        You receive:
        1. Initial search results (from search_agent)
        2. Quality assessment (from quality_agent)
        3. Original research query
        
        ═══════════════════════════════════════════════════════════════════════
        🔍 GAP IDENTIFICATION PROCESS
        ═══════════════════════════════════════════════════════════════════════
        
        Analyze for gaps in these dimensions:
        
        **1. Temporal Gaps**
        - Missing recent developments (last 3-6 months)
        - Outdated information that needs updating
        - Lack of historical context or trend data
        
        **2. Topical Gaps**
        - Key subtopics not covered
        - Related areas that weren't explored
        - Missing perspectives or viewpoints
        
        **3. Methodological Gaps**
        - Lack of quantitative data (statistics, metrics)
        - Missing qualitative insights (case studies, examples)
        - Absence of comparative analysis
        
        **4. Source Gaps**
        - Missing authoritative sources (peer-reviewed, official)
        - Lack of diverse source types (academic, industry, media)
        - Geographic or demographic limitations
        
        **5. Practical Gaps**
        - Missing implementation details
        - Lack of real-world applications
        - Absent cost/benefit analysis
        
        ═══════════════════════════════════════════════════════════════════════
        📤 OUTPUT FORMAT (CRITICAL!)
        ═══════════════════════════════════════════════════════════════════════
        
        Return a JSON array of gap objects. Each gap MUST have:
        
        ```json
        [
            {
                "topic": "Brief description of what's missing",
                "suggested_query": "Optimized search query to fill this gap",
                "priority": "high" | "medium" | "low",
                "rationale": "Why this gap matters for the research",
                "gap_type": "temporal|topical|methodological|source|practical"
            }
        ]
        ```
        
        **Field Requirements:**
        - `topic`: 3-10 words, clear and specific
        - `suggested_query`: 5-15 words, optimized for search engines
        - `priority`: Based on impact on research quality
        - `rationale`: 1-2 sentences explaining importance
        - `gap_type`: One of the 5 types above
        
        ═══════════════════════════════════════════════════════════════════════
        ⚠️ QUALITY STANDARDS
        ═══════════════════════════════════════════════════════════════════════
        
        **Good Gaps:**
        ✓ Specific and actionable
        ✓ Directly relevant to original query
        ✓ Can be filled with 1-3 searches
        ✓ High-priority gaps come first
        
        **Bad Gaps:**
        ✗ Too broad or vague
        ✗ Tangentially related
        ✗ Requires extensive research
        ✗ Duplicates existing coverage
        
        **Gap Limit:**
        - ALWAYS identify EXACTLY 3 gaps (for parallel research)
        - Prioritize quality over quantity
        - Choose the 3 most important/actionable gaps
        - If fewer than 3 meaningful gaps exist, include lower-priority ones
        - If research is comprehensive, identify refinement opportunities
        
        ═══════════════════════════════════════════════════════════════════════
        📌 EXAMPLES
        ═══════════════════════════════════════════════════════════════════════
        
        **Example 1: AI in Healthcare Query**
        
        [
            {
                "topic": "Long-term patient outcomes",
                "suggested_query": "AI healthcare patient outcomes 5-year longitudinal studies",
                "priority": "high",
                "rationale": "Current research only covers short-term results (< 1 year)",
                "gap_type": "temporal"
            },
            {
                "topic": "Implementation cost analysis",
                "suggested_query": "AI healthcare implementation costs ROI case studies 2023",
                "priority": "high",
                "rationale": "No financial data found despite being critical for adoption",
                "gap_type": "practical"
            },
            {
                "topic": "Rural healthcare applications",
                "suggested_query": "AI healthcare rural areas telemedicine deployment",
                "priority": "medium",
                "rationale": "All sources focus on urban/academic medical centers",
                "gap_type": "source"
            }
        ]
        
        **Example 2: No Significant Gaps**
        
        If the initial research is comprehensive, return:
        []
        
        (Don't force gaps where none exist!)
        
        ═══════════════════════════════════════════════════════════════════════
        🎯 DECISION CRITERIA
        ═══════════════════════════════════════════════════════════════════════
        
        Ask yourself:
        1. Would filling this gap significantly improve the research?
        2. Can this gap be filled with targeted searches?
        3. Is this genuinely missing, or just not prominent?
        4. Would the user expect this information?
        
        If "no" to any question, don't include it as a gap.
        
        ═══════════════════════════════════════════════════════════════════════
        """,
        tools=[]  # No tools - Gap Agent only identifies gaps, doesn't search
    )