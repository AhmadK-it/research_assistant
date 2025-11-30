# Research Agent - Capstone Project Presentation

## Problem Statement

Traditional research is time-consuming: manual web searches, subjective quality assessment, missing information gaps, and tedious synthesis of findings. High-quality research is fundamental to decision-making, yet most people lack the time or expertise to do it thoroughly.

---

## Why Agents?

Research is a multi-step, decision-driven workflow requiring:

- **Specialization** - Different tasks need different expertise (search, quality, gap analysis, synthesis)
- **Orchestration** - Conditional logic between phases with decision-making
- **Tool Use** - External web search via MCP
- **Human Collaboration** - HITL keeps users in control
- **Parallelism** - Fill multiple gaps simultaneously

A single LLM call can't do this—a coordinated team of agents can.

---

## What I Created

Multi-agent research orchestrator with 5-phase workflow:

![Agent Architecture](Multi-agent%20Sys.png)

| Pattern | Usage |
|---------|-------|
| **SequentialAgent** | Chains Search → Quality |
| **ParallelAgent** | 3 slots for simultaneous gap research |
| **AgentTool** | Wraps agents as callable tools |
| **BuiltInCodeExecutor** | Code-based report formatting |
| **MCP Integration** | DuckDuckGo search |
| **HITL** | User approval before gap research |

---

## Demo

1. User submits research query
2. **Phase 1+2**: Search + Quality assessment (SequentialAgent)
3. **Phase 3**: Gap analysis + Initial report
4. **Phase 4**: HITL approval → ParallelAgent fills 3 gaps
5. **Phase 5**: Final comprehensive report

---

## The Build

| Component | Technology |
|-----------|------------|
| Framework | Google ADK 1.x |
| LLM | Gemini 2.5 Flash |
| Search | FastMCP + DuckDuckGo |
| Language | Python 3.10+ |

---

## If I Had More Time

- Long-term memory for past research sessions
- More search sources (arXiv, Google Scholar)
- Export to PDF/Google Docs
- Evaluation framework for research quality
