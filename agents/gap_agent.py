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

def create_gap_agent(retry_config=None, search_toolset=None) -> Agent:
    """Creates agent for identifying missing information in research coverage"""
    
    return Agent(
        model=Gemini(model='gemini-2.5-flash-lite', retry_options=retry_config),
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
        - Identify 3-8 gaps maximum
        - Prioritize quality over quantity
        - If fewer than 3 meaningful gaps exist, that's fine
        - If no significant gaps exist, return an empty array: []
        
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
        tools=[search_toolset] if search_toolset else []
    )
#         You are a research gap analyst. Your job is to:

#         1. Review the research question and what's been found so far
#         2. Identify what's MISSING to fully answer the question
#         3. Categorize gaps:
#         - Critical gaps (without this, we can't answer the question) - Priority: high
#         - Important gaps (would significantly improve the answer) - Priority: medium
#         - Nice-to-have gaps (would add depth but not essential) - Priority: low

#         4. For each gap, suggest:
#         - Specific search queries to fill it
#         - What type of source would be ideal (academic, news, technical, etc.)
#         - Why this gap matters

#         5. Output format:
#             [
#             {
#                 "topic": "Description of what's missing",
#                 "suggested_query": "Specific search query to fill gap",
#                 "source_type": "Type of source needed",
#                 "importance": "Why this matters",
#                 "priority": "high / medium / low"
#             }
#             ]

#         Be specific and actionable in your recommendations.

#         EXAMPLE_GAP_RESPONSE =
#         [
#             {
#                 "topic": "Long-term healthcare outcomes",
#                 "suggested_query": "AI healthcare outcomes longitudinal studies 2023-2024",
#                 "priority": "high",
#                 "rationale": "Initial research lacked outcome data beyond 6 months"
#             },
#             {
#                 "topic": "Cost-benefit analysis",
#                 "suggested_query": "AI healthcare implementation costs ROI analysis",
#                 "priority": "medium",
#                 "rationale": "No financial impact data found in initial sources"
#             }
#         ]
#         "",
#     )
    

# from google.adk.agents import Agent
# from google.adk.models.google_llm import Gemini


# def create_gap_agent(retry_config, search_toolset):
#     """
#     Create gap analysis agent with structured output format.
    
#     This ensures gaps are properly formatted for the HITL workflow.
#     """
    
#     gap_agent = Agent(
#         model=Gemini(model='gemini-2.5-flash-lite', retry_options=retry_config),
#         name='gap_agent',
#         description='Identifies information gaps and suggests targeted searches',
#         instruction="""
        