"""Entry point for python -m parallel_llm_mcp.server"""

from .server import main_sync


if __name__ == "__main__":
    main_sync()