# 🔬 Research Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ADK](https://img.shields.io/badge/Google-ADK-green.svg)](https://github.com/google/adk-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash_Lite-blue.svg)](https://deepmind.google/technologies/gemini/)

An **autonomous multi-agent research orchestrator** built with Google's Agent Development Kit (ADK). This system implements a sophisticated 5-phase research workflow with Human-in-the-Loop (HITL) capabilities for conducting comprehensive web research.

> **📚 Course Capstone Project**: This project was developed for the **Google AI Agents Intensive (Nov 2025)** as a demonstration of multi-agent architectures, MCP integration, and agentic design patterns.

---

## 🏆 Course Concepts Demonstrated

This project showcases **6+ key concepts** from the Google AI Agents Intensive:

| Concept | Implementation | File(s) |
|---------|---------------|---------|
| **Multi-Agent Systems** | 4 specialist agents + 1 coordinator using AgentTool pattern | `agent.py`, `agents/*.py` |
| **MCP (Model Context Protocol)** | DuckDuckGo search integration via FastMCP server | `mcp_server/search_server.py` |
| **Human-in-the-Loop (HITL)** | User approval for gap research via `request_confirmation` | `tools/hitl_handler.py` |
| **Session Management** | InMemorySessionService for conversation state | `agent.py` |
| **Logging & Observability** | Structured logging with file output | `utils/logger.py` |
| **Sequential Agents** | 5-phase workflow executed in order | `agent.py` instructions |
| **Resumability** | ResumabilityConfig for long-running operations | `agent.py` |
| **Gemini Models** | All agents use gemini-2.5-flash-lite | Throughout |

---

## 🎯 The Journey: Problem → Solution

### The Problem
Traditional research is time-consuming, involving:
- Manual web searches across multiple sources
- Subjective quality assessment of sources
- Missing important information gaps
- Tedious synthesis of findings

### The Solution: Multi-Agent Research Orchestration
This system breaks research into **specialized phases**, each handled by an expert agent:

```
User Question
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: SEARCH                                             │
│  Search Agent → MCP → DuckDuckGo → Raw Results              │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: QUALITY                                            │
│  Quality Agent → Evaluate credibility → Scored Sources      │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: GAP ANALYSIS                                       │
│  Gap Agent → Identify missing info → Gap List               │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: HITL CONFIRMATION                                  │
│  "Fill these gaps?" → [Yes] / [No] → User decides           │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: SYNTHESIS                                          │
│  Synthesis Agent → All sources → Professional Report        │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
  📄 Final Research Report
```

### Why This Architecture?
1. **Separation of Concerns**: Each agent does one thing well
2. **Quality Control**: Explicit filtering prevents garbage-in-garbage-out
3. **Human Oversight**: HITL ensures user stays in control of research depth
4. **Iterative Refinement**: Gap analysis enables comprehensive coverage
5. **Traceable Results**: Structured output with source citations

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Agent Workflow](#-agent-workflow)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

Research Agent is a sophisticated multi-agent system that automates the research process by breaking it down into specialized phases:

1. **Search** - Find relevant information across the web
2. **Quality Assessment** - Evaluate source credibility and relevance
3. **Gap Analysis** - Identify missing information
4. **Synthesis** - Generate comprehensive research reports
5. **Adaptive Gap Research (HITL)** - Fill identified gaps with user approval

The system leverages Google's Gemini LLM models and integrates with DuckDuckGo for web searches via the Model Context Protocol (MCP).

---

## ✨ Features

- 🤖 **Multi-Agent Architecture** - Specialized agents for each research phase
- 🔄 **Autonomous Execution** - Phases 1-3 run automatically without user intervention
- 👤 **Human-in-the-Loop (HITL)** - User approval for adaptive gap research
- 🔍 **MCP Integration** - DuckDuckGo search via FastMCP server
- 📊 **Quality Scoring** - Source credibility evaluation (1-10 scale)
- 📝 **Structured Reports** - Professional markdown output with citations
- 🔁 **Resumability** - Session persistence and workflow resumption
- 📋 **Comprehensive Logging** - File and console logging for debugging

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ROOT AGENT                                │
│              (Research Orchestrator - LlmAgent)                  │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Search   │  │ Quality  │  │   Gap    │  │  Synthesis   │    │
│  │ Agent    │  │ Agent    │  │  Agent   │  │   Agent      │    │
│  └────┬─────┘  └──────────┘  └──────────┘  └──────────────┘    │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              MCP Server (DuckDuckGo Search)              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   HITL Handler  │
                    │ (User Approval) │
                    └─────────────────┘
```

---

## 🛠 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Dependencies

```bash
pip install google-adk
pip install google-genai
pip install fastmcp
pip install ddgs
pip install mcp
```

### Clone & Setup

```bash
# Clone the repository
git clone <repository-url>
cd research_agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export GOOGLE_API_KEY="your-gemini-api-key"
```

---

## 🚀 Usage

### Basic Usage with ADK CLI

```bash
# Start the ADK web server
adk web

# Or run in terminal mode
adk run
```

The agent is exposed as a resumable `App` which enables proper HITL (Human-in-the-Loop) functionality.

### Programmatic Usage

```python
from research_agent.agent import root_agent, runner, session_service

# Create a session
session = session_service.create_session(
    app_name="research_agent",
    user_id="user_123"
)

# Run a research query
async for response in runner.run_async(
    session_id=session.id,
    user_id="user_123",
    new_message="Research the impact of quantum computing on cryptography"
):
    print(response)
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ Yes |
| `AUTO_APPROVE_GAPS` | Set to `true` to skip HITL confirmation | ❌ No |

---

## 📁 Project Structure

```
research_agent/
├── __init__.py              # Package initialization
├── agent.py                 # Root agent & application setup (main entry)
├── README.md                # This file
│
├── agents/                  # Specialist agents
│   ├── __init__.py
│   ├── search_agent.py      # Web search specialist (MCP integration)
│   ├── quality_agent.py     # Source credibility evaluator
│   ├── gap_agent.py         # Information gap identifier
│   └── synthesis_agent.py   # Report generator
│
├── tools/                   # Agent tools & handlers
│   ├── __init__.py
│   ├── init_handler.py      # Agent initialization utilities
│   └── hitl_handler.py      # Human-in-the-Loop confirmation handler
│
├── mcp_server/              # MCP search server
│   ├── __init__.py
│   └── search_server.py     # DuckDuckGo MCP server (FastMCP)
│
├── utils/                   # Utility modules
│   ├── __init__.py
│   └── logger.py            # Logging configuration
│
└── logs/                    # Log files directory
    ├── __init__.py
    └── chat-sessions/       # Saved conversation sessions
│
├── utils/                   # Utility modules
│   ├── __init__.py
│   └── logger.py            # Logging configuration
│
├── memory/                  # Memory management (planned)
│   └── __init__.py
│
└── logs/                    # Log files directory
    └── __init__.py
```

---

## 🔄 Agent Workflow

### Phase 1: Initial Search
```
User Query → Search Agent → DuckDuckGo (via MCP) → Search Results
```
The search agent generates 2-3 optimized queries and retrieves diverse sources.

### Phase 2: Quality Assessment
```
Search Results → Quality Agent → Credibility Scores → Filtered Sources
```
Each source is evaluated on:
- **Credibility** (1-10): Publisher reputation
- **Relevance** (1-10): Query alignment
- **Recency**: Publication date

### Phase 3A: Gap Identification
```
Filtered Sources → Gap Agent → Information Gaps
```
Identifies gaps across 5 dimensions:
- Temporal (missing recent data)
- Topical (uncovered subtopics)
- Methodological (missing data types)
- Source (limited source diversity)
- Practical (missing implementation details)

### Phase 3B: Initial Synthesis
```
All Results → Synthesis Agent → Draft Report
```

### Phase 4: Adaptive Gap Research (HITL)
```
Gaps → HITL Handler → User Approval → Gap Research
```
User can:
- ✅ **Approve** - Conduct additional research for identified gaps
- ❌ **Reject** - Proceed with available information

### Phase 5: Final Synthesis
```
All Results + Gap Research → Synthesis Agent → Final Report
```

---

## ⚙️ Configuration

### Retry Configuration

```python
from research_agent.tools.init_handler import setup_retry_config

retry_config = setup_retry_config(
    attempts=6,        # Max retry attempts
    exp_base=3,        # Exponential backoff base
    initial_delay=1    # Initial delay in seconds
)
```

### Generation Configuration

```python
from research_agent.tools.init_handler import setup_generation_config

gen_config = setup_generation_config(
    max_output_tokens=8192,  # Maximum response length
    temperature=0.7          # Creativity level (0-1)
)
```

### Model Selection

All agents use `gemini-2.5-flash-lite` by default. To change:

```python
search_agent = create_search_agent(
    model='gemini-2.0-flash',  # Alternative model
    tools=[search_toolset],
    retry_config=retry_config
)
```

---

## 📚 API Reference

### Agents

| Agent | Description | Tools |
|-------|-------------|-------|
| `root_agent` | Research orchestrator | All specialist agents |
| `search_specialist` | Web search execution | MCP DuckDuckGo |
| `quality_assessor` | Source evaluation | None |
| `gap_identifier` | Gap analysis | MCP DuckDuckGo |
| `research_synthesizer` | Report generation | None |

### Tools

| Tool | Description |
|------|-------------|
| `duckduckgo_search` | MCP tool for web searches |
| `conduct_adaptive_gap_search` | HITL approval for gap research |

### Key Functions

```python
# Initialize agents
from research_agent.tools.init_handler import (
    setup_retry_config,
    setup_generation_config,
    create_specialist_agents
)

# HITL handler
from research_agent.tools.hitl_handler import conduct_adaptive_gap_search

# Logger
from research_agent.utils.logger import setup_logger
```

---

## 🔧 Customization

### Adding New Search Tools

1. Create a new MCP tool in `mcp_server/`:
```python
@mcp.tool()
def custom_search(query: str) -> List[Dict]:
    # Implementation
    pass
```

2. Add to search agent tools in `agent.py`

### Custom Gap Types

Modify `agents/gap_agent.py` to add new gap dimensions:

```python
# Add to instruction string
**6. Custom Gaps**
- Your custom gap criteria
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
flake8 research_agent/
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Google ADK](https://github.com/google/adk-python) - Agent Development Kit
- [FastMCP](https://github.com/jlowin/fastmcp) - Model Context Protocol server
- [ddgs](https://github.com/deedy5/ddgs) - DuckDuckGo search library

---

## 📞 Support

For questions or issues:
- 📧 Open an issue on GitHub
- 💬 Check the [discussions](../../discussions) page

---

<p align="center">
  Built with ❤️ using Google ADK
</p>
