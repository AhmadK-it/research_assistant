"""
Centralized Logging Configuration

This module provides structured logging for the Research Agent system,
enabling comprehensive observability and debugging capabilities.

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: Logging & Observability
═══════════════════════════════════════════════════════════════════════════════

Proper logging is essential for agentic systems because:

1. DEBUGGING - Agents make autonomous decisions that may fail silently.
   Logs help understand what decisions were made and why.

2. AUDITING - Research workflows involve multiple phases and tool calls.
   Logs provide a complete audit trail of all operations.

3. PERFORMANCE - Logs can track timing for each phase to identify
   bottlenecks in the research pipeline.

4. USER TRUST - When users can see what the agent is doing,
   they're more likely to trust its output.

═══════════════════════════════════════════════════════════════════════════════
LOGGING STRATEGY
═══════════════════════════════════════════════════════════════════════════════

This module implements dual-output logging:

    ┌─────────────────┐
    │  Logger Call    │
    │  logger.info()  │
    └────────┬────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
    ┌──────┐  ┌──────────────────────────────────────┐
    │STDOUT│  │ logs/research_agent_YYYYMMDD_HHMMSS │
    │INFO+ │  │ DEBUG+ (all messages)               │
    └──────┘  └──────────────────────────────────────┘

Benefits:
- Console shows user-relevant INFO+ messages
- File captures DEBUG+ for detailed troubleshooting
- Timestamp-based files prevent log collision

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════

    from utils.logger import setup_logger
    
    logger = setup_logger("MyComponent", level=logging.DEBUG)
    
    logger.debug("Detailed debugging info")
    logger.info("User-relevant status update")
    logger.warning("Something unexpected but handled")
    logger.error("Something failed")

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

import logging
import sys
import os
from datetime import datetime


def setup_logger(name: str = "ResearchAgent", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with console and file output.
    
    Creates a logger that outputs to both stdout and a timestamped log file.
    The file handler captures all messages (DEBUG+) while the console handler
    only shows messages at the specified level and above.
    
    Args:
        name: Logger name (appears in log messages). Use component names like
              "SearchAgent", "QualityAgent", "HITL-Handler" for clarity.
        level: Minimum logging level for console output.
               Default is INFO to avoid cluttering user output.
    
    Returns:
        logging.Logger: Configured logger instance.
    
    Example:
        >>> logger = setup_logger("SearchAgent")
        >>> logger.info("Starting search phase")
        2025-11-27 10:30:00 - SearchAgent - INFO - Starting search phase
        
    File Output:
        Logs are written to: logs/research_agent_YYYYMMDD_HHMMSS.log
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Console handler - shows INFO+ to user
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Ensure logs directory exists
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # File handler - captures DEBUG+ for detailed troubleshooting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(f"{logs_dir}/research_agent_{timestamp}.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Consistent format: timestamp - component - level - message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger