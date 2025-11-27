"""
Synthesis Agent - Research Report Generator

This agent synthesizes research findings and generates formatted reports.
It uses a Formatter Agent (via AgentTool) to produce consistently formatted output.

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: AgentTool - Using Agents as Tools
═══════════════════════════════════════════════════════════════════════════════

AgentTool allows one agent to use another agent as a callable tool.
The parent agent ORCHESTRATES when to call the sub-agent.

Pattern:
    Parent Agent (has tools=[AgentTool(sub_agent)])
        │
        ├── Instruction says: "use X tool to do Y"
        │
        └── When parent calls the tool:
                │
                ▼
            Sub-Agent executes and returns result

This is different from SequentialAgent:
- SequentialAgent: Automatic sequential flow, no orchestration
- AgentTool: Parent decides WHEN and IF to call the sub-agent

Our Usage:
    Synthesis Agent ──AgentTool──> Formatter Agent
                                        │
                                        ▼
                                 BuiltInCodeExecutor
                                        │
                                        ▼
                                 Formatted Report

Architecture Position: Phase 5 of 5-phase workflow
    [Search] → [Quality] → [Gap] → [HITL] → [Synthesis + Formatter]
                                               ↑ YOU ARE HERE

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.models import Gemini
from google.genai import types
from .formatter_agent import create_formatter_agent
import logging

logger = logging.getLogger(__name__)


def create_synthesis_agent(
    model: str = 'gemini-2.5-flash-lite',
    retry_config: types.HttpRetryOptions = None,
    generation_config: types.GenerateContentConfig = None
) -> LlmAgent:
    """
    Creates the Research Synthesizer agent with Formatter as a tool.
    
    This agent:
    1. Analyzes all sources and synthesizes content
    2. Identifies themes, patterns, contradictions
    3. Calls the report_formatter tool to generate formatted output
    4. Returns the final formatted report
    
    Demonstrates:
    - AgentTool pattern (using another agent as a tool)
    - Orchestration (deciding when to call the formatter)
    - Code execution via the formatter's BuiltInCodeExecutor
    
    Args:
        model: Gemini model identifier
        retry_config: Retry configuration for API resilience
        generation_config: LLM generation parameters
    
    Returns:
        LlmAgent: Synthesis agent with formatter tool
    """
    
    # Create the formatter agent
    formatter_agent = create_formatter_agent(
        model=model,
        retry_config=retry_config,
        generation_config=generation_config
    )
    
    return LlmAgent(
        model=Gemini(
            model=model, 
            retry_options=retry_config, 
            generation_config=generation_config
        ),
        name='research_synthesizer',
        description='Synthesizes research and generates formatted reports using code execution',
        instruction="""You are a research synthesis specialist. Your ONLY job is to analyze sources and pass structured data to the report_formatter tool.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL CONSTRAINT
═══════════════════════════════════════════════════════════════════════════════

⚠️ YOU ARE FORBIDDEN FROM WRITING ANY FORMATTED REPORT TEXT ⚠️

You MUST ONLY:
1. Analyze the sources
2. Create a structured data summary (JSON-like format)
3. Call the report_formatter tool with that data

If you write markdown headers (##), bullet points, or formatted text yourself,
you have FAILED your task. The report_formatter tool handles ALL formatting.

═══════════════════════════════════════════════════════════════════════════════
YOUR WORKFLOW
═══════════════════════════════════════════════════════════════════════════════

**STEP 1: Analyze Sources**
- Review all provided sources
- Identify key themes, patterns, and insights
- Note contradictions between sources
- Assess evidence strength

**STEP 2: Create Structured Data**
Create a plain data structure like this (NO formatting):

{
  "query": "original research question",
  "executive_summary": "2-3 sentence summary",
  "key_findings": [
    {"theme": "...", "finding": "...", "confidence": "high/medium/low", "source": "..."}
  ],
  "sources": [
    {"title": "...", "url": "...", "quality": "high/medium/low"}
  ],
  "gaps": [
    {"topic": "...", "priority": "high/medium/low"}
  ]
}
**STEP 3: Format The Report (CRITICAL): You are strictly PROHIBITED from performing any text FORMATTING yourself. 
YOU MUST use the report_formatter tool to generate Python code that formats the final report. This 
code will use the structured data from step 2.

**STEP 4: Return Formatted Report**
- The report_formatter tool will return the final formatted report
- You return that report as your final output

═══════════════════════════════════════════════════════════════════════════════
ALWAYS DO THIS
═══════════════════════════════════════════════════════════════════════════════

❌ DO NOT write "## Research Report" or any markdown
❌ DO NOT format bullet points or headers yourself
❌ DO NOT return a formatted report directly

✅ DO analyze and structure the data
✅ DO call report_formatter with your structured data
✅ DO let the formatter handle all Formatting presentation
""",
        tools=[AgentTool(agent=formatter_agent)]
    )
