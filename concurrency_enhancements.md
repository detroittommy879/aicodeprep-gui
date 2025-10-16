# Concurrency Enhancements for aicodeprep-flow MCP Server

## Current State Analysis

The `best_of_all2.txt` plan is **partially concurrent-ready** but needs enhancements for true multi-user server scenarios.

### ✅ What's Already Good:

1. Uses `asyncio.to_thread()` for non-blocking execution
2. Creates separate `NodeGraph()` instances per request
3. Uses temporary files for context input

### ⚠️ What Needs Enhancement:

## 1. Executor Pool for Controlled Concurrency

**Problem:** Unlimited concurrent executions could overwhelm the server.

**Solution:** Add a ThreadPoolExecutor with a configurable limit.

```python
# In src/aicodeprep_flow/mcp/server.py

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

class FlowMCPServer:
    def __init__(self, max_workers: int = 5):
        from fastmcp import FastMCP
        from NodeGraphQt import NodeGraph
        self.mcp = FastMCP("aicodeprep-flow-server")
        self.NodeGraph = NodeGraph

        # NEW: Add executor pool
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self._register_nodes_globally()
        self._register_mcp_tools()

    def _register_mcp_tools(self):
        @self.mcp.tool()
        async def execute_flow(graph_path: str, context_text: str) -> str:
            """Executes a flow graph with the provided text and returns the result."""
            if not Path(graph_path).is_file():
                return f"Error: Graph file not found at '{graph_path}'"

            # Create a unique temporary file for this execution
            import uuid
            execution_id = uuid.uuid4().hex

            with tempfile.NamedTemporaryFile(
                mode='w+',
                delete=False,
                suffix=f"_{execution_id}.txt",  # UNIQUE per request
                encoding='utf-8'
            ) as tmp:
                tmp.write(context_text)
                context_file_path = tmp.name

            logger.info(f"[{execution_id}] Wrote context to: {context_file_path}")

            try:
                # NEW: Submit to executor pool instead of direct asyncio.to_thread
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._run_graph_sync,
                    graph_path,
                    context_file_path,
                    execution_id  # Pass ID for logging
                )
                return result
            except Exception as e:
                logger.error(f"[{execution_id}] Error: {e}", exc_info=True)
                return f"Error: {e}"
            finally:
                os.unlink(context_file_path)

    def _run_graph_sync(self, graph_path: str, context_file_path: str, execution_id: str) -> str:
        """Synchronous wrapper for executing the graph - now with execution ID."""
        logger.info(f"[{execution_id}] Starting execution of {graph_path}")

        # Create isolated graph instance (already good!)
        graph = self.NodeGraph()

        if not load_session(graph, graph_path):
            raise RuntimeError(f"Failed to load graph session: {graph_path}")

        # ... rest of execution ...

        logger.info(f"[{execution_id}] Execution complete")
        return result_text
```

## 2. Thread-Safe Configuration Access

**Problem:** Multiple threads reading API keys could cause race conditions.

**Solution:** Add locking to config.py or use thread-local storage.

```python
# In src/aicodeprep_flow/config.py

import threading
from functools import lru_cache

# Thread-safe API key cache
_api_key_lock = threading.Lock()
_api_key_cache = {}

def get_api_key(provider: str) -> str:
    """Thread-safe API key retrieval."""
    global _api_key_cache

    # Check cache first (read-only, safe)
    if provider in _api_key_cache:
        return _api_key_cache[provider]

    # Acquire lock for file read
    with _api_key_lock:
        # Double-check after acquiring lock
        if provider in _api_key_cache:
            return _api_key_cache[provider]

        # Load from file
        api_keys = load_api_config()
        key = api_keys.get(provider, {}).get('api_key', '')

        # Update cache
        _api_key_cache[provider] = key
        return key

def invalidate_api_key_cache():
    """Call this when API keys are updated."""
    with _api_key_lock:
        _api_key_cache.clear()
```

## 3. Isolated Working Directories

**Problem:** Multiple executions using the same working directory could conflict.

**Solution:** Create temporary working directories per execution.

```python
def _run_graph_sync(self, graph_path: str, context_file_path: str, execution_id: str) -> str:
    """Synchronous wrapper with isolated working directory."""

    # Create isolated working directory
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory(prefix=f"flow_{execution_id}_") as work_dir:
        work_dir_path = Path(work_dir)
        logger.info(f"[{execution_id}] Working dir: {work_dir_path}")

        # Copy graph file to working directory
        local_graph_path = work_dir_path / "flow.json"
        shutil.copy(graph_path, local_graph_path)

        # Copy context file to working directory
        local_context_path = work_dir_path / "fullcode.txt"
        shutil.copy(context_file_path, local_context_path)

        # Load graph
        graph = self.NodeGraph()
        if not load_session(graph, str(local_graph_path)):
            raise RuntimeError(f"Failed to load graph session")

        # Update ContextOutputNode to use local path
        for node in graph.all_nodes():
            if isinstance(node, ContextOutputNode):
                node.set_property('path', str(local_context_path))
                logger.info(f"[{execution_id}] Updated context path")

        # Change to working directory for execution
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(work_dir_path)
            execute_graph(graph, parent_widget=None, show_progress=False)

            # Extract result (FileWriteNode will write to this dir)
            result = self._extract_result(graph, work_dir_path)
            return result
        finally:
            os.chdir(original_cwd)

        # Temp dir automatically cleaned up after 'with' block
```

## 4. Rate Limiting and Queue Management

**Problem:** Without limits, a flood of requests could crash the server.

**Solution:** Add request queuing and rate limiting.

```python
from collections import deque
from datetime import datetime, timedelta

class FlowMCPServer:
    def __init__(self, max_workers: int = 5, max_queue_size: int = 20):
        # ... existing init ...

        # NEW: Request queue management
        self.request_queue = asyncio.Queue(maxsize=max_queue_size)
        self.active_executions = 0
        self.max_active = max_workers

        # Rate limiting (per-user tracking would go here)
        self.rate_limit_window = timedelta(minutes=1)
        self.max_requests_per_window = 10
        self.request_history = deque(maxlen=100)

    async def _check_rate_limit(self, user_id: str = "default") -> bool:
        """Check if user is within rate limits."""
        now = datetime.now()
        cutoff = now - self.rate_limit_window

        # Count recent requests from this user
        recent_requests = [
            ts for ts, uid in self.request_history
            if ts > cutoff and uid == user_id
        ]

        if len(recent_requests) >= self.max_requests_per_window:
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            return False

        self.request_history.append((now, user_id))
        return True

    def _register_mcp_tools(self):
        @self.mcp.tool()
        async def execute_flow(graph_path: str, context_text: str) -> str:
            """Executes a flow graph (with rate limiting)."""

            # Check rate limit
            if not await self._check_rate_limit():
                return "Error: Rate limit exceeded. Please try again later."

            # Check queue capacity
            if self.request_queue.qsize() >= self.request_queue.maxsize:
                return "Error: Server is at capacity. Please try again later."

            # ... rest of execution logic ...
```

## 5. Monitoring and Metrics

**Problem:** No visibility into server health and performance.

**Solution:** Add basic metrics collection.

```python
from dataclasses import dataclass, field
from typing import List
import time

@dataclass
class ExecutionMetrics:
    execution_id: str
    graph_path: str
    start_time: float
    end_time: float = 0
    success: bool = False
    error_message: str = ""

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time else 0

class FlowMCPServer:
    def __init__(self, ...):
        # ... existing init ...
        self.metrics: List[ExecutionMetrics] = []
        self.metrics_lock = threading.Lock()

    def _record_metric(self, metric: ExecutionMetrics):
        with self.metrics_lock:
            self.metrics.append(metric)
            # Keep only last 1000 metrics
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]

    def _register_mcp_tools(self):
        @self.mcp.tool()
        async def get_server_stats() -> dict:
            """Get server statistics."""
            with self.metrics_lock:
                total = len(self.metrics)
                successful = sum(1 for m in self.metrics if m.success)
                failed = total - successful

                if total > 0:
                    avg_duration = sum(m.duration for m in self.metrics) / total
                else:
                    avg_duration = 0

                return {
                    "total_executions": total,
                    "successful": successful,
                    "failed": failed,
                    "average_duration_seconds": round(avg_duration, 2),
                    "active_executions": self.active_executions,
                    "queue_size": self.request_queue.qsize()
                }
```

## 6. Updated Main Entry Point

**Problem:** Need to configure concurrency settings.

**Solution:** Add CLI arguments for server configuration.

```python
# In src/aicodeprep_flow/main.py

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(
        description="AICodePrep Flow: Visual Editor and MCP Server."
    )
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Run in headless MCP server mode (stdio)."
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum concurrent flow executions (default: 5)"
    )
    parser.add_argument(
        "--max-queue",
        type=int,
        default=20,
        help="Maximum queued requests (default: 20)"
    )
    args = parser.parse_args()

    if args.mcp:
        from .mcp.server import FlowMCPServer
        print(f"Starting MCP server (max workers: {args.max_workers})")
        server = FlowMCPServer(
            max_workers=args.max_workers,
            max_queue_size=args.max_queue
        )
        server.mcp.run(transport="stdio")
    else:
        # ... GUI mode ...
```

## Summary of Changes

### Immediate Additions (Phase 4.5 - After Phase 4 in original plan):

1. **Add Executor Pool** → Controlled concurrency
2. **Add Unique Execution IDs** → Better logging and tracking
3. **Add Thread-Safe Config** → Prevent race conditions
4. **Add Isolated Working Dirs** → Prevent file conflicts

### Future Enhancements (Production Deployment):

5. **Rate Limiting** → Prevent abuse
6. **Metrics Collection** → Monitor health
7. **User Authentication** → Secure access
8. **Persistent Queue** → Survive restarts

## Testing Concurrent Execution

```python
# test_concurrent_execution.py

import asyncio
import json
from aicodeprep_flow.mcp.server import FlowMCPServer

async def test_concurrent():
    server = FlowMCPServer(max_workers=3)

    # Simulate 10 concurrent requests
    tasks = []
    for i in range(10):
        task = asyncio.create_task(
            server.execute_flow(
                graph_path="/path/to/flow.json",
                context_text=f"Test input {i}"
            )
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    print(f"Completed {len(results)} executions")
    for i, result in enumerate(results):
        print(f"Result {i}: {result[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_concurrent())
```

## Configuration Example

```json
// server_config.json
{
  "max_workers": 8,
  "max_queue_size": 50,
  "rate_limit": {
    "window_minutes": 1,
    "max_requests": 10
  },
  "temp_dir": "/tmp/aicodeprep-flow",
  "log_level": "INFO"
}
```

This design ensures the server can handle multiple users executing different flows simultaneously without conflicts or resource exhaustion.
