"""
Tools Package

This package contains all FunctionTools and tool utilities used by the Research Agent.

Tools:
- hitl_handler: Human-in-the-Loop confirmation for gap research
- init_handler: Unified agent factory (creates ALL agents)
"""

from .hitl_handler import conduct_adaptive_gap_search
from .init_handler import (
    setup_retry_config,
    setup_generation_config,
    create_all_agents,
)

__all__ = [
    # HITL
    'conduct_adaptive_gap_search',
    # Init/Factory
    'setup_retry_config',
    'setup_generation_config',
    'create_all_agents',
]