from types import SimpleNamespace
from unittest.mock import patch

from aicodeprep_gui.pro.llm.llm_client import LLMClient


def test_extract_message_content_prefers_content():
    message = {"content": "final answer", "reasoning": "hidden chain"}

    assert LLMClient._extract_message_content(message) == "final answer"


def test_extract_message_content_falls_back_to_reasoning():
    message = {"content": None, "reasoning": "usable reasoning text"}

    assert LLMClient._extract_message_content(
        message) == "usable reasoning text"


def test_extract_message_content_supports_object_messages():
    message = SimpleNamespace(content=None, reasoning="object reasoning")

    assert LLMClient._extract_message_content(message) == "object reasoning"


@patch("aicodeprep_gui.pro.llm.llm_client.requests.request")
def test_chat_uses_direct_http_for_compatible_provider(mock_request):
    mock_response = mock_request.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "compatible answer",
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    result = LLMClient.chat(
        model="kilo/auto",
        user_content="hello",
        base_url="https://extra.wuu73.org/aimodels/v1",
        provider="compatible",
    )

    assert result == "compatible answer"
    assert mock_request.call_count == 1
    assert mock_request.call_args.args[:2] == (
        "POST",
        "https://extra.wuu73.org/aimodels/v1/chat/completions",
    )


@patch("aicodeprep_gui.pro.llm.llm_client.requests.request")
def test_chat_strips_openrouter_prefix_for_direct_api(mock_request):
    mock_response = mock_request.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "openrouter answer",
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    result = LLMClient.chat(
        model="openrouter/google/gemini-2.5-pro",
        user_content="hello",
        api_key="sk-or-test",
        base_url="https://openrouter.ai/api/v1",
        provider="openrouter",
    )

    assert result == "openrouter answer"
    payload = mock_request.call_args.kwargs["json"]
    assert payload["model"] == "google/gemini-2.5-pro"


@patch("aicodeprep_gui.pro.llm.llm_client.requests.request")
def test_chat_uses_gemini_generate_content(mock_request):
    mock_response = mock_request.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "gemini answer"},
                    ]
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    result = LLMClient.chat(
        model="gemini/gemini-2.5-pro",
        user_content="hello",
        system_content="be concise",
        api_key="gemini-test-key",
        provider="gemini",
    )

    assert result == "gemini answer"
    assert mock_request.call_args.args[:2] == (
        "POST",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent",
    )
    headers = mock_request.call_args.kwargs["headers"]
    payload = mock_request.call_args.kwargs["json"]
    assert headers["x-goog-api-key"] == "gemini-test-key"
    assert payload["systemInstruction"]["parts"][0]["text"] == "be concise"
    assert payload["contents"][0]["parts"][0]["text"] == "hello"


@patch("aicodeprep_gui.pro.llm.llm_client.requests.request")
def test_chat_compatible_provider_extracts_reasoning_when_content_is_null(mock_request):
    mock_response = mock_request.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": None,
                    "reasoning": "reasoning fallback",
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    result = LLMClient.chat(
        model="minimax/minimax-m2.5:free",
        user_content="hello",
        base_url="https://extra.wuu73.org/aimodels/v1",
        provider="compatible",
    )

    assert result == "reasoning fallback"


@patch("aicodeprep_gui.pro.llm.llm_client.requests.request")
def test_chat_compatible_provider_preserves_post_across_redirect(mock_request):
    redirect_response = mock_request.side_effect = None
    redirect_response = SimpleNamespace(
        status_code=301,
        headers={"Location": "https://api.example.com/v1/chat/completions"},
    )
    final_response = mock_request.return_value
    final_response.status_code = 200
    final_response.headers = {}
    final_response.json.return_value = {
        "choices": [{"message": {"content": "redirected ok"}}]
    }
    final_response.raise_for_status.return_value = None
    mock_request.side_effect = [redirect_response, final_response]

    result = LLMClient.chat(
        model="glm-5",
        user_content="hello",
        base_url="http://api.example.com/v1",
        provider="compatible",
    )

    assert result == "redirected ok"
    assert mock_request.call_args_list[0].args[:2] == (
        "POST",
        "http://api.example.com/v1/chat/completions",
    )
    assert mock_request.call_args_list[1].args[:2] == (
        "POST",
        "https://api.example.com/v1/chat/completions",
    )
