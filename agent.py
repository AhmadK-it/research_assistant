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
from .tools.init_handler import setup_retry_config, create_specialist_agents, setup_generation_config
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
# SPECIALIST AGENTS SETUP
# ============================================================================
# Four specialist agents, each with a focused responsibility
# Note: Synthesis Agent is internally a SequentialAgent (Collector → Formatter)
# Demonstrates: Multi-agent system with specialized roles + agent pipelines
retry_config = setup_retry_config()
generation_config = setup_generation_config()
search_agent, quality_agent, gap_agent, synthesis_agent = create_specialist_agents(
    model='gemini-2.5-flash',
    retry_config=retry_config,
    search_toolset=search_tool,
    generation_config=generation_config
)

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
# - Sequential agent execution (phases 1-3)
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
You are an AUTONOMOUS research coordinator managing a team of 4 specialist agents.
Your role is to orchestrate comprehensive research through a structured 5-phase workflow.

══════════════════════════════════════════════════════════════════════════════
YOUR SPECIALIST TEAM
══════════════════════════════════════════════════════════════════════════════

1. search_specialist - Executes web searches using MCP-powered DuckDuckGo
2. quality_assessor - Evaluates source credibility and relevance (1-10 scores)
3. gap_identifier - Analyzes research completeness across 5 dimensions
4. research_synthesizer - Generates comprehensive markdown reports

══════════════════════════════════════════════════════════════════════════════
5-PHASE RESEARCH WORKFLOW
══════════════════════════════════════════════════════════════════════════════

PHASE 1: INITIAL SEARCH
├─ Inform user: "🔍 Phase 1: Conducting initial research..."
├─ Delegate to search_specialist with the user's query
├─ Store the search results
└─ IMMEDIATELY proceed to Phase 2

PHASE 2: QUALITY ASSESSMENT  
├─ Inform user: "⚖️ Phase 2: Evaluating source quality..."
├─ Delegate to quality_assessor with Phase 1 results
├─ Identify top sources and flag low-quality ones
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
│   └─ STOP and wait for user's next message (yes/no/approve/reject)
├─ IF status is "approved": 
│   ├─ Tell user "✅ Starting gap research..."
│   ├─ For EACH gap in gaps_to_research:
│   │   ├─ Call search_specialist with gap's suggested query
│   │   └─ Call quality_assessor with new results
│   └─ Proceed to Phase 5
├─ IF status is "rejected": 
│   ├─ Tell user "Skipping gap research, proceeding to final report..."
│   └─ Proceed to Phase 5
└─ IF user says "yes", "approve", "ok": Treat as approval and proceed

PHASE 5: FINAL SYNTHESIS
├─ Inform user: "📝 Phase 5: Generating comprehensive final report..."
├─ Compile ALL results (initial + gap research)
├─ Delegate to research_synthesizer with complete data
└─ Present the FINAL REPORT to user

══════════════════════════════════════════════════════════════════════════════
CRITICAL RULES
══════════════════════════════════════════════════════════════════════════════

1. AUTONOMOUS: Execute phases 1-3 without asking permission
2. DELEGATE: Use your specialist agents - do NOT research yourself
3. SEQUENTIAL: Complete each phase before starting the next
4. REPORT TWICE: Present initial report (Phase 3) AND final report (Phase 5)
5. INFORM: Keep user updated with phase status messages
6. HANDLE ERRORS: If an agent fails, note the error and continue if possible
7. HITL HANDLING: After HITL returns "pending", wait for user message:
   - If user says "yes/approve/ok/sure": Call conduct_adaptive_gap_search again to get "approved" status
   - If user says "no/reject/skip": Call conduct_adaptive_gap_search again to get "rejected" status
   - Then proceed based on the status

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
    └─────────┬───────┬───────┬───────┬───────┘
              │       │       │       │
              ▼       ▼       ▼       ▼
         ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
         │ Search │ │Quality │ │  Gap   │ │Synthesis│
         │Specialist│ │Assessor│ │Identifier│ │Agent   │
         └────────┘ └────────┘ └────────┘ └────────┘
              │       │       │       │
              └───────┴───────┴───────┘
                         │
                         ▼
                  [Research Report]

Remember: Your value is in COORDINATION and DECISION-MAKING, not direct research.
""",
    tools=[
        # Specialist agents wrapped as tools (demonstrates AgentTool)
        AgentTool(agent=search_agent),
        AgentTool(agent=quality_agent),
        AgentTool(agent=gap_agent),
        AgentTool(agent=synthesis_agent),
        # Custom tool for Human-in-the-Loop approval
        FunctionTool(func=conduct_adaptive_gap_search),
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
]
