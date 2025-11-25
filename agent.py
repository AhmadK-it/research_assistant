
from google.adk.agents import Agent
from google.adk.tools import google_search, AgentTool, ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.models.google_llm import Gemini


from mcp import StdioServerParameters
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
import asyncio


from .agents.search_agent import create_search_agent
from .agents.quality_agent import create_quality_agent
from .agents.gap_agent import create_gap_agent
from .agents.synthesis_agent import create_synthesis_agent
from .utils.logger import setup_logger
from .tools.init_handler import setup_retry_config, create_specialist_agents

logger = setup_logger("ResearchAssistant initialization", level=logging.INFO)

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

retry_config = setup_retry_config()
search_agent, quality_agent, gap_agent, synthesis_agent = create_specialist_agents(
    retry_config=retry_config,
    search_toolset=search_tool
)


"""
TODO: update instruction to include HITL steps and user notification requirements

"""

root_agent = Agent(
    model=Gemini(model='gemini-2.5-flash-lite', retry_options=retry_config),
    name='root_agent',
    description='Research assistant with 4-phase workflow and HITL',
    instruction="""
    **CRITICAL: You are a research COORDINATOR, NOT a direct researcher.**

    You're prohibited from performing searches or generating content directly.
    Your job is to route the user's research query to the 4-phase Adaptive Research Orchestrator workflow.

    The orchestrator should do:
    1. Execute initial broad searches
    2. Assess quality of sources
    3. Identify information gaps
    4. Generate comprehensive final report
    5. Provide the report to the user


    You demonstrate true agentic behavior through:
    - Autonomous quality decisions
    - Gap identification
    - Adaptive search refinement

    **IMPORTANT RULES:**
    1. DO NOT attempt to answer research queries yourself. 
    2. AUTOMATICALLY keep the user informed by the things you're doing. DON'T wait for approval to conduct phases 1-3.
    3. Always inform them with your current job, not all the thinking stuff.
    4. Don't hand the user the ability to control the workflow or to interrupt it.
    5. ALWAYS use the following tools to delegate tasks to specialist agents:
    6. PROVIDE THE FINAL REPORT TO THE USER YOURSELF. ONCE THE SYNTHESIS AGENT HAS COMPLETED THE REPORT, DELIVER IT.
    """,
    tools=[
        AgentTool(agent=search_agent),
        AgentTool(agent=quality_agent),
        AgentTool(agent=gap_agent),
        AgentTool(agent=synthesis_agent)
        ]
)