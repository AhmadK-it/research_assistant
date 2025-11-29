"""
Parallel Gap Research Tool - asyncio-based Parallel Execution

═══════════════════════════════════════════════════════════════════════════════
COURSE CONCEPT: Parallel Execution with asyncio.gather()
═══════════════════════════════════════════════════════════════════════════════

This module provides a FunctionTool for parallel gap research using Python's
asyncio.gather() pattern. This is the TOOL wrapper, not the agent.

    ┌────────────────────────────────────────────────────────────────────────┐
    │                     PARALLEL GAP RESEARCH TOOL                         │
    │                                                                        │
    │   Gap 1 ──▶ [search_quality_pipeline] ──┐                             │
    │   Gap 2 ──▶ [search_quality_pipeline] ──┼──▶ Combined Results         │
    │   Gap 3 ──▶ [search_quality_pipeline] ──┤                             │
    │   Gap 4 ──▶ [search_quality_pipeline] ──┘                             │
    │                                                                        │
    │         Uses asyncio.gather() + Semaphore for rate limiting            │
    └────────────────────────────────────────────────────────────────────────┘

Why asyncio.gather() instead of ParallelAgent?
──────────────────────────────────────────────
1. We run the SAME pipeline multiple times (not different agents)
2. We need rate limiting via Semaphore
3. We want partial success (some gaps may fail, others succeed)
4. We have a DYNAMIC number of gaps (unknown at design time)

Performance:
────────────
    Sequential (6 gaps): ~60 seconds (10s each)
    Parallel (6 gaps, 3 concurrent): ~20 seconds (3x faster!)

Author: Research Agent Capstone Project
Course: Google AI Agents Intensive (Nov 2025)
"""

import asyncio
import time
from typing import List, Dict, Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import logging
import json

logger = logging.getLogger("ResearchAssistant.ParallelGapTool")


async def _research_single_gap(
    gap: Dict[str, Any],
    index: int,
    total: int,
    pipeline,
    session_service: InMemorySessionService,
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """
    Research a single gap with rate limiting via semaphore.
    
    This is an internal async function used by research_gaps_parallel.
    
    Args:
        gap: Gap dictionary with 'suggested_query' and 'topic'
        index: Index of this gap (for logging)
        total: Total number of gaps (for logging)
        pipeline: The search_quality_pipeline SequentialAgent
        session_service: Session service for creating sessions
        semaphore: Semaphore to limit concurrency
        
    Returns:
        Result dictionary with gap info and research results
    """
    async with semaphore:
        query = gap.get('suggested_query', gap.get('topic', 'unknown topic'))
        topic = gap.get('topic', 'unknown')[:40]
        
        logger.info(f"  🔍 [{index+1}/{total}] Researching: {topic}...")
        start = time.time()
        
        try:
            # Create a unique session for this gap
            session = session_service.create_session(
                app_name="parallel_gap_research",
                user_id=f"gap_{index}"
            )
            
            # Create runner for the pipeline
            runner = Runner(
                agent=pipeline,
                session_service=session_service,
            )
            
            # Execute the search+quality pipeline
            results = []
            async for event in runner.run_async(
                session_id=session.id,
                user_id=f"gap_{index}",
                new_message=query
            ):
                # Collect content from the event
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                results.append(part.text)
                    else:
                        results.append(str(event.content))
            
            elapsed = time.time() - start
            logger.info(f"  ✅ [{index+1}/{total}] Completed in {elapsed:.1f}s: {topic}")
            
            return {
                "gap": gap,
                "status": "success",
                "results": " ".join(results) if results else "No results found",
                "elapsed_seconds": round(elapsed, 1)
            }
            
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"  ❌ [{index+1}/{total}] Error after {elapsed:.1f}s: {str(e)[:80]}")
            return {
                "gap": gap,
                "status": "error",
                "error": str(e),
                "elapsed_seconds": round(elapsed, 1)
            }


async def research_gaps_parallel(
    gaps: List[Dict[str, Any]],
    search_quality_pipeline,
    session_service: InMemorySessionService,
    max_concurrent: int = 3
) -> Dict[str, Any]:
    """
    Execute gap research in parallel using asyncio.gather().
    
    This function demonstrates:
    1. Dynamic task creation based on gap list
    2. Semaphore-based concurrency control
    3. Concurrent agent execution with result aggregation
    4. Error handling for partial failures
    
    Args:
        gaps: List of gap dictionaries from gap_identifier
              Each gap should have 'suggested_query' and 'topic' fields
        search_quality_pipeline: The SequentialAgent pipeline
        session_service: Session service for creating sessions
        max_concurrent: Maximum concurrent searches (default: 3)
        
    Returns:
        Dictionary with status, timing, and all research results
        
    Example:
        >>> gaps = [{"topic": "AI", "suggested_query": "AI news"}]
        >>> result = await research_gaps_parallel(gaps, pipeline, session_svc)
        >>> print(result['successful_count'])  # Number of successful searches
    """
    if not gaps:
        return {
            "status": "completed",
            "message": "No gaps to research",
            "results": [],
            "total_time_seconds": 0
        }
    
    logger.info("=" * 60)
    logger.info(f"🚀 PARALLEL GAP RESEARCH (asyncio.gather)")
    logger.info(f"   Gaps: {len(gaps)}")
    logger.info(f"   Max Concurrent: {max_concurrent}")
    logger.info("=" * 60)
    
    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Create tasks for all gaps
    tasks = [
        _research_single_gap(
            gap=gap,
            index=i,
            total=len(gaps),
            pipeline=search_quality_pipeline,
            session_service=session_service,
            semaphore=semaphore
        )
        for i, gap in enumerate(gaps)
    ]
    
    # Execute all tasks concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    # Process results
    successful = []
    failed = []
    
    for r in results:
        if isinstance(r, Exception):
            failed.append({"status": "error", "error": str(r)})
        elif isinstance(r, dict):
            if r.get('status') == 'success':
                successful.append(r)
            else:
                failed.append(r)
        else:
            failed.append({"status": "error", "error": f"Unexpected result type: {type(r)}"})
    
    logger.info("=" * 60)
    logger.info(f"🏁 PARALLEL RESEARCH COMPLETE")
    logger.info(f"   Total Time: {total_time:.1f}s")
    logger.info(f"   Successful: {len(successful)}/{len(gaps)}")
    if failed:
        logger.info(f"   Failed: {len(failed)}/{len(gaps)}")
    logger.info("=" * 60)
    
    return {
        "status": "completed",
        "message": f"Parallel gap research completed: {len(successful)} successful, {len(failed)} failed",
        "total_time_seconds": round(total_time, 1),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "results": successful,
        "errors": failed if failed else None
    }


def create_parallel_gap_research_tool(search_quality_pipeline, session_service):
    """
    Create a FunctionTool wrapper for parallel gap research.
    
    This creates a sync function that can be used as a FunctionTool in ADK.
    The function internally runs the async parallel research.
    
    Args:
        search_quality_pipeline: The SequentialAgent pipeline for search+quality
        session_service: Session service for creating sessions
        
    Returns:
        Function that can be wrapped with FunctionTool
        
    Example:
        >>> tool_func = create_parallel_gap_research_tool(pipeline, session_svc)
        >>> tool = FunctionTool(func=tool_func)
        >>> # Now the root agent can use this tool!
    """
    
    def parallel_gap_research(gaps_json: str) -> str:
        """
        Execute parallel research for multiple gaps simultaneously.
        
        This is MUCH faster than sequential execution:
        - Sequential (6 gaps): ~60 seconds
        - Parallel (6 gaps): ~20 seconds
        
        Args:
            gaps_json: JSON string containing list of gap dictionaries.
                Each gap should have 'suggested_query' and 'topic' fields.
                
        Returns:
            JSON string with research results for all gaps.
        """
        # Parse gaps from JSON
        try:
            gaps = json.loads(gaps_json) if isinstance(gaps_json, str) else gaps_json
        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "error": f"Invalid JSON: {str(e)}"
            })
        
        # Run parallel research
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            research_gaps_parallel(
                gaps=gaps,
                search_quality_pipeline=search_quality_pipeline,
                session_service=session_service,
                max_concurrent=3
            )
        )
        
        return json.dumps(result, indent=2)
    
    return parallel_gap_research


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON: ParallelAgent (agent) vs asyncio.gather() (tool)
# ═══════════════════════════════════════════════════════════════════════════════
#
# ┌─────────────────────┬───────────────────────┬──────────────────────────────┐
# │ Feature             │ ParallelAgent         │ asyncio.gather()             │
# │                     │ (parallel_gap_agent)  │ (this file)                  │
# ├─────────────────────┼───────────────────────┼──────────────────────────────┤
# │ ADK Native          │ ✅ Yes                │ ❌ Python native             │
# │ Rate Limiting       │ ❌ No built-in        │ ✅ Semaphore control         │
# │ Dynamic Count       │ ⚠️ Create at runtime  │ ✅ Natural fit               │
# │ Error Handling      │ ⚠️ All-or-nothing     │ ✅ Partial success           │
# │ Same Agent, N times │ ⚠️ Need N copies      │ ✅ Reuse pipeline            │
# │ Different Agents    │ ✅ Perfect fit        │ ⚠️ Manual orchestration      │
# │ Progress Tracking   │ ❌ Limited            │ ✅ Full control              │
# │ File Location       │ agents/               │ tools/                       │
# └─────────────────────┴───────────────────────┴──────────────────────────────┘
#
# ═══════════════════════════════════════════════════════════════════════════════
