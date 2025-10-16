import asyncio
import logging
import os
import tempfile
from typing import Dict
from pathlib import Path

# Important: These are local package imports
from ..flow.engine import execute_graph
from ..flow.serializer import load_session
from ..flow.nodes.io_nodes import ContextOutputNode, OutputDisplayNode, FileWriteNode

logger = logging.getLogger(__name__)


class FlowMCPServer:
    def __init__(self):
        try:
            from fastmcp import FastMCP
            from NodeGraphQt import NodeGraph
            self.mcp = FastMCP("aicodeprep-flow-server")
            self.NodeGraph = NodeGraph
        except ImportError as e:
            raise ImportError(f"Missing dependency for MCP Server: {e}")

        self._register_nodes_globally()
        self._register_mcp_tools()

    def _register_nodes_globally(self):
        # We need to register nodes with the NodeGraphQt framework itself
        # so they can be deserialized correctly.
        from ..flow.nodes.io_nodes import ContextOutputNode, ClipboardNode, FileWriteNode, OutputDisplayNode
        from ..flow.nodes.llm_nodes import OpenRouterNode, OpenAINode, GeminiNode, OpenAICompatibleNode
        from ..flow.nodes.aggregate_nodes import BestOfNNode
        from NodeGraphQt import setup_context_menu

        nodes_to_register = [
            ContextOutputNode, ClipboardNode, FileWriteNode, OutputDisplayNode,
            OpenRouterNode, OpenAINode, GeminiNode, OpenAICompatibleNode, BestOfNNode,
        ]

        menu_items = {'graph': {}, 'nodes': {}}
        for node_cls in nodes_to_register:
            category = "I/O"
            if "LLM" in node_cls.__name__:
                category = "LLM"
            if "BestOfN" in node_cls.__name__:
                category = "Aggregate"

            if category not in menu_items['nodes']:
                menu_items['nodes'][category] = {}

            menu_items['nodes'][category][
                node_cls.NODE_NAME] = f"{node_cls.__identifier__}.{node_cls.__name__}"

        setup_context_menu(node_menu=menu_items)
        logger.info("Globally registered all flow nodes.")

    def _register_mcp_tools(self):
        @self.mcp.tool()
        async def execute_flow(graph_path: str, context_text: str) -> str:
            """Executes a flow graph with the provided text and returns the result."""
            if not Path(graph_path).is_file():
                return f"Error: Graph file not found at '{graph_path}'"

            # Create a temporary file for the context input
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt", encoding='utf-8') as tmp:
                tmp.write(context_text)
                context_file_path = tmp.name

            logger.info(
                f"Wrote context to temporary file: {context_file_path}")

            try:
                # Run the graph execution in a separate thread to avoid blocking asyncio loop
                result = await asyncio.to_thread(
                    self._run_graph_sync, graph_path, context_file_path
                )
                return result
            except Exception as e:
                logger.error(
                    f"Error during graph execution: {e}", exc_info=True)
                return f"Error: {e}"
            finally:
                os.unlink(context_file_path)

    def _run_graph_sync(self, graph_path: str, context_file_path: str) -> str:
        """Synchronous wrapper for executing the graph."""
        graph = self.NodeGraph()

        if not load_session(graph, graph_path):
            raise RuntimeError(f"Failed to load graph session: {graph_path}")

        # Modify the ContextOutputNode to point to our temporary input file
        for node in graph.all_nodes():
            if isinstance(node, ContextOutputNode):
                node.set_property('path', context_file_path)
                logger.info(
                    f"Patched ContextOutputNode to use '{context_file_path}'")

        # Execute the graph
        execute_graph(graph, parent_widget=None, show_progress=False)

        # Extract the result
        # Strategy: Find OutputDisplayNode and get its 'last_result' property.
        for node in graph.all_nodes():
            if isinstance(node, OutputDisplayNode):
                result_text = node.get_property('last_result')
                if result_text:
                    logger.info("Extracted result from OutputDisplayNode.")
                    return result_text

        # Fallback Strategy: Find the last FileWriteNode and read its output
        for node in graph.all_nodes():
            if isinstance(node, FileWriteNode):
                output_path = node.get_property('path')
                if output_path and Path(output_path).exists():
                    logger.info(
                        f"Extracted result from FileWriteNode file: {output_path}")
                    return Path(output_path).read_text(encoding='utf-8')

        return "Flow executed, but no result could be extracted from OutputDisplayNode or FileWriteNode."


def main_sync():
    """Entry point for running the MCP server."""
    try:
        server = FlowMCPServer()
        server.mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
