"""
Research Agent - Multi-Agent Research Assistant with ADK

This module implements a sophisticated multi-agent research system demonstrating:
- Multi-agent architecture (coordinator + 4 specialist agents)
- Sequential and parallel agent execution
- MCP tool integration (DuckDuckGo search)
- Long-running operations with resumability
- Session and state management
- Comprehensive logging and observability

Built for the Google AI Agents Intensive Course Capstone Project.
"""

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool
from mcp import StdioServerParameters
import os
import logging

from .utils.logger import setup_logger
from .tools.init_handler import (
    setup_retry_config, 
    setup_generation_config,
    create_all_agents
)
from .tools.hitl_handler import conduct_adaptive_gap_search

logger = setup_logger("ResearchAssistant", level=logging.INFO)

# ============================================================================
# MCP SEARCH TOOL SETUP
# ============================================================================
# Integration with DuckDuckGo search via Model Context Protocol (MCP)
# Demonstrates: MCP tool integration
MCP_SERVER_PATH = os.path.join(
    os.path.dirname(__file__),
    "mcp_server",
    "search_server.py"
)

search_tool = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[MCP_SERVER_PATH]
        ),
        timeout=60
    )
)

# ============================================================================
# ALL AGENTS SETUP (Unified Factory)
# ============================================================================
# Creates all agents with consistent configuration:
# - 4 LlmAgents (search, quality, gap, synthesis)
# - 1 SequentialAgent (search_quality_pipeline)
# - 1 ParallelAgent (parallel_gap_agent with 3 slots)
#
# Demonstrates: Factory pattern, SequentialAgent, ParallelAgent
retry_config = setup_retry_config()
generation_config = setup_generation_config()

agents = create_all_agents(
    model='gemini-2.5-flash',
    retry_config=retry_config,
    search_toolset=search_tool,
    generation_config=generation_config
)

# Unpack for easy access
search_agent = agents['search']
quality_agent = agents['quality']
gap_agent = agents['gap']
synthesis_agent = agents['synthesis']
search_quality_pipeline = agents['search_quality_pipeline']
parallel_gap_agent = agents['parallel_gap_agent']

# ============================================================================
# SESSION SERVICE
# ============================================================================
# Demonstrates: Session & state management with InMemorySessionService
session_service = InMemorySessionService()

# ============================================================================
# ROOT AGENT - MULTI-AGENT COORDINATOR
# ============================================================================
# The coordinator agent orchestrates the 4 specialist agents through
# a structured 5-phase research workflow.
#
# Demonstrates:
# - Multi-agent orchestration (LLM-powered decision making)
# - SequentialAgent pattern (search_quality_pipeline)
# - Agent tools (AgentTool wrapping specialist agents)
# - Custom tools (conduct_adaptive_gap_search for HITL)
# - Long-running operations (ResumabilityConfig)

_root_agent = LlmAgent(
    model=Gemini(
        model='gemini-2.5-flash', 
        retry_options=retry_config,
        generation_config=generation_config
    ),
    name='research_coordinator',
    description='Autonomous multi-agent research orchestrator with 5-phase workflow',
    instruction="""
You are an AUTONOMOUS research coordinator managing a team of specialist agents.
Your role is to orchestrate comprehensive research through a structured 5-phase workflow.

══════════════════════════════════════════════════════════════════════════════
YOUR SPECIALIST TEAM
══════════════════════════════════════════════════════════════════════════════

1. search_quality_pipeline - SequentialAgent that combines:
   ├─ Search (DuckDuckGo via MCP)
   └─ Quality Assessment (source credibility scoring)
   → Use for initial research and individual gap research

2. gap_identifier - Analyzes research completeness across 5 dimensions
3. research_synthesizer - Generates comprehensive markdown reports
4. parallel_gap_researcher - ParallelAgent with 3 fixed slots (3x faster!)
   → Use when execution_mode is "parallel"
   → Provide up to 3 gap queries in one prompt

══════════════════════════════════════════════════════════════════════════════
5-PHASE RESEARCH WORKFLOW
══════════════════════════════════════════════════════════════════════════════

PHASE 1+2: INITIAL SEARCH + QUALITY (Combined via SequentialAgent)
├─ Inform user: "🔍 Phase 1+2: Conducting research with quality assessment..."
├─ Delegate to search_quality_pipeline with the user's query
│   (This automatically runs Search → Quality in sequence!)
├─ Store the quality-assessed search results
└─ IMMEDIATELY proceed to Phase 3

PHASE 3: GAP ANALYSIS + INITIAL SYNTHESIS
├─ Inform user: "🔬 Phase 3: Analyzing gaps and generating initial report..."
├─ Delegate to gap_identifier to find information gaps
├─ Delegate to research_synthesizer to create initial report
├─ Present the INITIAL REPORT to user
└─ IMMEDIATELY proceed to Phase 4

PHASE 4: ADAPTIVE GAP RESEARCH (Human-in-the-Loop)
├─ Call conduct_adaptive_gap_search with identified gaps
├─ This tool requests user approval for bulk research
├─ IF status is "pending": 
│   ├─ Tell user "Awaiting your approval for gap research..."
│   └─ STOP and wait for user's next message
├─ IF status is "approved": 
│   ├─ Tell user "✅ Starting parallel gap research..."
│   ├─ Call parallel_gap_researcher with a combined prompt:
│   │   "Research these gaps:
│   │    1. [first gap query]
│   │    2. [second gap query]  
│   │    3. [third gap query]"
│   │   (ParallelAgent researches ALL 3 simultaneously!)
│   └─ Proceed to Phase 5 with all gap results
├─ IF status is "rejected": 
│   ├─ Tell user "Skipping gap research, proceeding to final report..."
│   └─ Proceed to Phase 5 without gap research

PHASE 5: FINAL SYNTHESIS
├─ Inform user: "📝 Phase 5: Generating comprehensive final report..."
├─ Compile ALL results (initial + gap research)
├─ Delegate to research_synthesizer with complete data
└─ Present the FINAL REPORT to user

══════════════════════════════════════════════════════════════════════════════
CRITICAL RULES
══════════════════════════════════════════════════════════════════════════════

1. INITIAL RESEARCH: Use search_quality_pipeline for the first search
2. GAP RESEARCH: Use parallel_gap_researcher for all 3 gaps at once (faster!)
3. AUTONOMOUS: Execute phases 1-3 without asking permission
4. DELEGATE: Use your specialist agents - do NOT research yourself
5. SEQUENTIAL: Complete each phase before starting the next
6. REPORT TWICE: Present initial report (Phase 3) AND final report (Phase 5)
7. INFORM: Keep user updated with phase status messages
8. HANDLE ERRORS: If an agent fails, note the error and continue if possible
9. HITL HANDLING - CRITICAL: After HITL returns "pending", the VERY NEXT user message is their decision:
   - ANY form of approval (yes/ok/sure/approved/go/proceed/do it/fine/yep/y): IMMEDIATELY call conduct_adaptive_gap_search with user_decision="approved"
   - ANY form of rejection (no/reject/skip/stop/cancel/don't/nope/negative/n): IMMEDIATELY call conduct_adaptive_gap_search with user_decision="rejected"
   - DO NOT ask for confirmation again - the user's first response IS their decision!
   - DO NOT say "awaiting approval" - act on what they said immediately!
   - Then proceed based on the returned status

══════════════════════════════════════════════════════════════════════════════
AGENT COLLABORATION PATTERN
══════════════════════════════════════════════════════════════════════════════

You orchestrate agents like a research team lead:

    [User Query]
         │
         ▼
    ┌─────────────────────────────────────────┐
    │         RESEARCH COORDINATOR (You)       │
    │   Orchestrates workflow & makes decisions │
    └─────────┬───────────┬───────────┬───────┘
              │           │           │
              ▼           ▼           ▼
    ┌───────────────┐ ┌────────┐ ┌────────────┐
    │Search+Quality │ │  Gap   │ │  Synthesis │
    │  Pipeline     │ │Identifier│ │   Agent   │
    │(SequentialAgent)│ └────────┘ └────────────┘
    │  ├─ Search    │       │           │
    │  └─ Quality   │       │           │
    └───────────────┘       │           │
              │             │           │
              └─────────────┴───────────┘
                         │
                         ▼
                  [Research Report]

Remember: Your value is in COORDINATION and DECISION-MAKING, not direct research.
""",
    tools=[
        # SequentialAgent pipeline for ALL research (initial + gap research)
        AgentTool(agent=search_quality_pipeline),
        # Gap analysis and synthesis agents
        AgentTool(agent=gap_agent),
        AgentTool(agent=synthesis_agent),
        # Custom tool for Human-in-the-Loop approval
        FunctionTool(func=conduct_adaptive_gap_search),
        # ParallelAgent for gap research (3 slots, 3x faster than sequential!)
        AgentTool(agent=parallel_gap_agent),
    ]
)

# ============================================================================
# ADK APP CONFIGURATION
# ============================================================================
# Wrap the agent in an App with ResumabilityConfig for long-running operations
# Demonstrates: Long-running operations with pause/resume capability

root_agent = App(
    name="research_agent",
    root_agent=_root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

# Alias for explicit usage
app = root_agent

# Pre-configured runner with session management
runner = Runner(
    app=root_agent,
    session_service=session_service,
)

# ============================================================================
# LOGGING & OBSERVABILITY
# ============================================================================
# Demonstrates: Observability through structured logging
logger.info("=" * 60)
logger.info("RESEARCH AGENT INITIALIZED")
logger.info("=" * 60)
logger.info(f"App Name: {root_agent.name}")
logger.info(f"Resumability: {root_agent.resumability_config.is_resumable}")
logger.info(f"Specialist Agents: search, quality, gap, synthesis")
logger.info(f"SequentialAgent: search_quality_pipeline")
logger.info(f"ParallelAgent: parallel_gap_agent (3 fixed slots)")
logger.info(f"MCP Tool: DuckDuckGo Search")
logger.info(f"Session Service: InMemorySessionService")
logger.info("=" * 60)

# ============================================================================
# ALTERNATIVE: Programmatic Workflow Access
# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    'root_agent',           # The App (for ADK CLI)
    'app',                  # Alias for root_agent
    '_root_agent',          # The underlying LlmAgent
    'runner',               # Pre-configured runner
    'session_service',      # Session service
    'search_agent',         # Specialist agents for direct access
    'quality_agent',
    'gap_agent', 
    'synthesis_agent',
    'search_quality_pipeline',  # SequentialAgent pipeline
    'parallel_gap_agent',       # ParallelAgent (3 fixed slots)
]
