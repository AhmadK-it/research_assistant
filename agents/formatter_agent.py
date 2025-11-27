"""
Formatter Agent - Code-Based Report Formatting

This agent generates Python code to format research reports consistently.
It uses BuiltInCodeExecutor to execute the generated code.

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: BuiltInCodeExecutor
═══════════════════════════════════════════════════════════════════════════════

BuiltInCodeExecutor allows an LLM to:
1. Generate Python code as its response
2. Have that code automatically executed in a sandboxed environment
3. Return the execution output as the final result

This ensures CONSISTENT formatting - the LLM doesn't manually format text,
it writes code that produces the formatted output.

Pattern:
    LLM generates code → BuiltInCodeExecutor runs it → Output returned
    
Example:
    Input: "Format this data: name=John, age=30"
    LLM Output: print(f"Name: John\\nAge: 30")
    Execution Output: "Name: John\\nAge: 30"

Architecture Position: Sub-tool of Synthesis Agent
    [Synthesis Agent] ──AgentTool──> [Formatter Agent]
                                           │
                                           ▼
                                    BuiltInCodeExecutor

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.models import Gemini
from google.genai import types
import logging

logger = logging.getLogger(__name__)


def create_formatter_agent(
    model: str = 'gemini-2.5-flash',  # Use stronger model for code generation
    retry_config: types.HttpRetryOptions = None,
    generation_config: types.GenerateContentConfig = None
) -> LlmAgent:
    """
    Creates the Report Formatter agent that generates and executes Python code.
    
    This agent:
    - Receives structured content from Synthesis Agent
    - Generates Python code that formats and prints a markdown report
    - Uses BuiltInCodeExecutor to run the generated code
    - Returns the formatted output
    
    NOTE: This agent ALWAYS uses gemini-2.5-flash (not flash-lite) because
    code generation requires a more capable model to follow instructions.
    
    Args:
        model: Gemini model identifier (defaults to gemini-2.5-flash)
        retry_config: Retry configuration
        generation_config: LLM generation parameters
    
    Returns:
        LlmAgent: Code-generating formatter with BuiltInCodeExecutor
    """
    
    # Force stronger model for code generation - flash-lite doesn't follow instructions well
    formatter_model = 'gemini-2.5-flash'
    
    return LlmAgent(
        model=Gemini(
            model=formatter_model,
            retry_options=retry_config,
            generation_config=generation_config
        ),
        name='report_formatter',
        description='Generates Python code to format research reports into standardized markdown',
        instruction="""You are a CODE GENERATOR. You MUST respond with ONLY Python code.

YOUR TASK:
Take the research data and generate Python code that prints a formatted markdown report.

RULES:
1. Your ENTIRE response must be valid Python code
2. Use print() to output the formatted report
3. Use triple-quoted strings for the report content
4. NO explanations, NO text outside of code

EXAMPLE - Generate code like this:

```python
print('''
# Research Report: [Topic from input]

## Executive Summary
[Summary from input]

## Key Findings
- **Finding 1:** [Details]
- **Finding 2:** [Details]

## Sources
- Source 1
- Source 2

## Information Gaps
- Gap 1
- Gap 2
''')
```

Extract the actual content from the input data and put it in the print statement.
Your response should be ONLY the Python code block above (customized with real data).
""",
        code_executor=BuiltInCodeExecutor()
    )
