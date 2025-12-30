"""Test server functionality."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from parallel_llm_mcp.server import ParallelLLMServer


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    return "test-api-key"


@pytest.fixture
def server(mock_api_key):
    """Create a test server instance."""
    with patch.dict('os.environ', {'OPENROUTER_API_KEY': mock_api_key}):
        return ParallelLLMServer()


def test_server_initialization_no_api_key():
    """Test server initialization fails without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable"):
            ParallelLLMServer()


def test_server_initialization_with_api_key(mock_api_key):
    """Test server initialization succeeds with API key."""
    with patch.dict('os.environ', {'OPENROUTER_API_KEY': mock_api_key}):
        server = ParallelLLMServer()
        assert server.client.api_key == mock_api_key
        assert len(server.parallel_models) == 5
        assert server.synthesizer_model == "google/gemini-2.5-pro"


def test_build_synthesis_prompt(server):
    """Test synthesis prompt building."""
    original_prompt = "What is 2+2?"
    models = ["model1", "model2"]
    responses = ["It's 4", "Four"]

    prompt = server._build_synthesis_prompt(original_prompt, models, responses)

    assert "What is 2+2?" in prompt
    assert "model1" in prompt
    assert "model2" in prompt
    assert "It's 4" in prompt
    assert "Four" in prompt
    assert "expert synthesiser" in prompt


@pytest.mark.asyncio
async def test_list_models_tool(server):
    """Test the list_models MCP tool."""
    result = await server.mcp.tools["list_models"]()
    expected_models = [
        "openai/gpt-5-codex",
        "x-ai/grok-4-fast",
        "mistralai/codestral-2508",
        "google/gemini-2.5-pro",
        "z-ai/glm-4.6",
    ]
    assert result == expected_models


@pytest.mark.asyncio
async def test_get_config_tool(server):
    """Test the get_config MCP tool."""
    result = await server.mcp.tools["get_config"]()

    assert "parallel_models" in result
    assert "synthesizer_model" in result
    assert "num_parallel_models" in result
    assert result["num_parallel_models"] == 5
    assert result["synthesizer_model"] == "google/gemini-2.5-pro"


@pytest.mark.asyncio
async def test_process_prompt_tool(server):
    """Test the process_prompt MCP tool with mocked API calls."""
    mock_responses = [
        "Response 1: The answer is 42",
        "Response 2: Forty-two",
        "Response 3: 42",
        "Response 4: The answer is forty-two",
        "Response 5: It's 42",
    ]

    final_synthesis = "The best answer is 42, which is the answer to life, the universe, and everything."

    # Mock the parallel execution
    with patch.object(server, '_call_models_parallel', new_callable=AsyncMock) as mock_parallel:
        mock_parallel.return_value = mock_responses

        # Mock the synthesizer call
        with patch.object(server.client, 'call_model_async', new_callable=AsyncMock) as mock_synthesizer:
            mock_synthesizer.return_value = final_synthesis

            # Test the process
            result = await server.mcp.tools["process_prompt"]("What is the answer to life?")

            # Verify results
            assert result == final_synthesis

            # Check that parallel was called correctly
            mock_parallel.assert_called_once_with("What is the answer to life?")

            # Check that synthesizer was called with proper prompt
            mock_synthesizer.assert_called_once()
            synthesis_prompt = mock_synthesizer.call_args[0][0]
            assert "What is the answer to life?" in synthesis_prompt
            assert "Response 1" in synthesis_prompt


@pytest.mark.asyncio
async def test_process_prompt_error_handling(server):
    """Test error handling in process_prompt tool."""
    # Mock parallel call to raise an exception
    with patch.object(server, '_call_models_parallel', new_callable=AsyncMock) as mock_parallel:
        mock_parallel.side_effect = Exception("API Error")

        result = await server.mcp.tools["process_prompt"]("Test prompt")

        assert "Error processing prompt" in result


@pytest.mark.asyncio
async def test_run_server_stdio(server):
    """Test running the server with stdio transport."""
    with patch.object(server.mcp, 'run', new_callable=AsyncMock) as mock_run:
        await server.run("stdio")
        mock_run.assert_called_once_with(transport="stdio")


@pytest.mark.asyncio
async def test_run_server_unsupported_transport(server):
    """Test that unsupported transport raises error."""
    with pytest.raises(ValueError, match="Only 'stdio' transport is supported"):
        await server.run("http")