"""Parallel LLM MCP Server.

A minimal, working MCP server that calls multiple LLMs in parallel
and synthesizes their results.

Example:
    >>> from parallel_llm_mcp import ParallelLLMServer
    >>> server = ParallelLLMServer()
    >>> # Run with stdio transport
    >>> asyncio.run(server.run())
"""

from .client import OpenRouterClient
from .server import ParallelLLMServer
from .parallel import parallel_call

__version__ = "0.1.0"
__all__ = ["ParallelLLMServer", "OpenRouterClient", "parallel_call"]