This is an excellent, well-structured codebase that demonstrates a solid grasp of modern Python and `asyncio`. The separation of concerns is clear, and the logging is very helpful. The review below focuses on improving robustness, performance, and maintainability by addressing several critical bugs and areas for refinement.

### High-Level Summary of Key Issues

1.  **Critical Bug - Broken Tests & Mismatched Docs:** The test suite (`test_server.py`) and documentation (`README.md`, `__init__.py`) reference a `server.run()` method that does not exist. This is the most critical issue as it indicates the tests are failing and the documentation is incorrect.
2.  **Performance Bottleneck - HTTP Client Instantiation:** A new `httpx.AsyncClient` is created for every API call. This is highly inefficient as it prevents connection pooling, adding significant overhead to each request.
3.  **Reliability Risk - Unsafe File I/O:** Files are written using a lambda (`open(...).write(...)`) that does not guarantee files are closed, especially on error. Furthermore, using fixed filenames (`test_llm_1.txt`) creates a race condition if multiple prompts are processed concurrently.
4.  **Bad Practice - Global Logging Configuration:** Logging is configured at the module level in `server.py`, which is a side effect that can interfere with other parts of an application that might import this server.
5.  **Robustness Issue - Brittle Error Handling:** Converting exceptions to simple strings (`"Error: ..."`) in `parallel.py` is lossy. It discards the original exception type and stack trace, making debugging difficult and creating a risk of misinterpreting a valid model response that happens to start with "Error:".
6.  **Dependency Bloat:** The `pydantic` library is listed as a dependency in `pyproject.toml` but is not used anywhere in the code.

---

### Detailed Review and Actionable Suggestions

#### `src/parallel_llm_mcp/client.py`

**1. Performance: Reuse `httpx.AsyncClient` for Connection Pooling**

- **Problem:** Creating a new client per request is inefficient.
- **Solution:** Instantiate the `httpx.AsyncClient` once in the `__init__` method and reuse it for all calls. This enables connection pooling, significantly reducing latency.
- **Reasoning:** Reusing the client avoids the overhead of repeated TCP handshakes and TLS negotiations.

```python
# In src/parallel_llm_mcp/client.py

class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        # ... (keep existing init code) ...
        timeout = httpx.Timeout(240.0, connect=60.0)
        self._client = httpx.AsyncClient(headers=self.headers, timeout=timeout)

    async def close(self):
        """Closes the underlying httpx client. Should be called on application shutdown."""
        await self._client.aclose()

    async def call_model_async(self, ...) -> str:
        # ... (build data dictionary) ...

        # REMOVE: timeout = httpx.Timeout(240.0, connect=60.0)
        import time # Move this to the top of the file
        start_time = time.time()
        logger.info(f"🚀 Starting API call to {model}...")

        # REMOVE: async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await self._client.post(
                f"{self.base_url}/chat/completions",
                json=data
            )
            # ... (rest of the method) ...
```

_Note: Ensure `server.client.close()` is called when the server gracefully shuts down._

**2. Bug: Synchronous Wrapper (`call_model`) is Unsafe in Async Contexts**

- **Problem:** `call_model` uses `asyncio.run()`, which creates a new event loop. If this function is ever called from code that is already running in an event loop, it will raise a `RuntimeError`.
- **Solution:** Add a warning to the docstring to prevent misuse.
- **Reasoning:** This makes the library safer for others to use and clarifies its limitations.

```python
# In src/parallel_llm_mcp/client.py
def call_model(self, ...) -> str:
    """Call a single model synchronously.

    NOTE: This method starts a new asyncio event loop and will fail
    if called from within an already running async context.
    ...
    """
    return asyncio.run(...)
```

**3. Code Quality: Minor Improvements**

- Move `import time` to the top of the file to adhere to PEP 8.
- The error handling logic duplicates the `elapsed = ...` calculation. This can be cleaned up using a `try...finally` block if desired, though the current implementation is clear enough.

#### `src/parallel_llm_mcp/parallel.py`

**1. Bug: Fragile Async Function Detection**

- **Problem:** `asyncio.iscoroutinefunction(func)` can fail for decorated functions, partials, or mock objects (like `unittest.mock.AsyncMock`) used in tests.
- **Solution:** Instead of checking the function, call it and then check if the _result_ is awaitable.
- **Reasoning:** This is a more robust pattern that correctly handles a wider variety of asynchronous callables.

```python
# In src/parallel_llm_mcp/parallel.py
import inspect # Add this import

async def run_single(args):
    # This is more robust than checking the function itself
    result = func(*args)
    if inspect.isawaitable(result):
        return await result
    else:
        # Run sync function in thread pool
        return await asyncio.to_thread(func, *args)
```

**2. Robustness: Improve Error Handling**

- **Problem:** Converting exceptions to strings (`f"Error: {str(result)}"`) loses valuable context (exception type, stack trace) and is brittle, as a model could legitimately return text starting with "Error:".
- **Solution:** Keep `return_exceptions=True` in `asyncio.gather` but process the results in the _caller_ (`server.py`). Let this function return either the successful result or the actual `Exception` object.
- **Reasoning:** This allows the caller to handle different exception types specifically (e.g., `TimeoutError` vs. `HTTPStatusError`) and makes the system more robust.

#### `src/parallel_llm_mcp/server.py`

**1. Critical Bug: Missing `run()` method**

- **Problem:** The `ParallelLLMServer` class lacks the `run()` method that is called in the `__init__.py` example and tested in `test_server.py`. The server is instead started via the standalone `main_sync()` function.
- **Solution:** Either add the `run()` method to the class or, more simply, fix the tests and documentation to reflect the actual entry point (`main_sync`). For consistency, adding the method is cleaner.
- **Reasoning:** This aligns the code with its tests and documentation, fixing a critical inconsistency.

```python
# In src/parallel_llm_mcp/server.py, inside the ParallelLLMServer class
# This method is currently missing
def run(self, transport: str = "stdio"):
    """Synchronously run the MCP server."""
    if transport != "stdio":
        raise ValueError("Only 'stdio' transport is supported at this time.")
    logger.info(f"Server starting with {transport} transport...")
    self.mcp.run(transport=transport)

# And update main_sync to use it
def main_sync():
    try:
        server = ParallelLLMServer()
        server.run() # Use the new method
    # ...
```

**2. Bad Practice: Global Logging Configuration**

- **Problem:** Configuring the root logger at import time is a side effect that can break logging in larger applications.
- **Solution:** Move all logging configuration inside the `main_sync()` function or a dedicated `setup_logging()` function that is called explicitly.
- **Reasoning:** This makes the library portion of the code side-effect-free and ensures that logging is only configured when the application is run as the main entry point.

**3. Reliability: Fix Unsafe File I/O**

- **Problem:** The current file writing logic is unsafe. `open(...).write()` does not guarantee the file is closed, and the fixed filenames are a race condition.
- **Solution:** Use a `with open(...)` context manager inside a dedicated helper function to ensure files are closed. For filenames, incorporate a unique identifier per request (e.g., a timestamp or UUID).
- **Reasoning:** This prevents resource leaks and data corruption from concurrent requests.

```python
# In src/parallel_llm_mcp/server.py

# A safe, synchronous file-writing helper
def _write_file_sync(filename: str, content: str):
    """Safely writes content to a file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to write to {filename}: {e}")
        # Optionally re-raise or handle
        raise

# In the process_prompt tool...
# Generate a unique prefix for this request
import time
request_id = f"{int(time.time())}"

# ... later, when writing files ...
for i, response in enumerate(responses, 1):
    filename = f"{request_id}_response_{i}.txt"
    await asyncio.to_thread(
        _write_file_sync, filename, str(response)
    )
```

#### `pyproject.toml`, `README.md`, and Tests

- **`pyproject.toml`:**
  - **Action:** Remove the unused `pydantic` dependency from `[project.dependencies]`.
- **`README.md`:**
  - **Action:** Update the "Quick Start" and docstring examples to reflect the correct way to run the server (either via `main_sync` or the new `server.run()` method).
  - **Action:** The "Debug Mode" section mentions a `PARALLEL_LLM_LOG_LEVEL` environment variable that is never used in the code. Either implement logic to read this variable or remove this section from the README.
- **`tests/test_server.py`:**
  - **Action:** The tests `test_run_server_stdio` and `test_run_server_unsupported_transport` are broken because `server.run()` does not exist. They must be updated to test the new `run` method or removed.

---

### Security Concerns

The code is generally secure for its intended purpose.

- **API Key:** Handled correctly via environment variables. The logs do not appear to leak the key.
- **File I/O:** The use of fixed filenames in the current working directory could be a minor risk if run on a sensitive system. Using a dedicated, non-privileged output directory and validating paths would be an improvement.
- **Prompt Injection:** This is an inherent risk with all LLM applications. The server itself is not vulnerable to code injection from the prompt, as it treats the prompt as opaque data.

### Summary of Recommendations

1.  **High Priority (Fix Bugs & Tests):**

    - Add the missing `run()` method to `ParallelLLMServer` and update `main_sync` to use it.
    - Fix the tests in `test_server.py` to correctly test the server's entry point.
    - Update the `README.md` to reflect the correct usage.

2.  **High Priority (Performance & Reliability):**

    - Refactor `OpenRouterClient` to reuse a single `httpx.AsyncClient` instance.
    - Fix the unsafe file I/O by using a `with` statement and unique filenames per request.

3.  **Medium Priority (Robustness & Best Practices):**
    - Move logging configuration out of the global scope and into `main_sync`.
    - Refactor `parallel_call_async` to return actual exception objects instead of strings.
    - Improve the async function detection in `parallel.py` to use `inspect.isawaitable`.
    - Remove the unused `pydantic` dependency.
