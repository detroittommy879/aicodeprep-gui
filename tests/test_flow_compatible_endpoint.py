from unittest.mock import patch

from aicodeprep_gui.pro.flow.nodes.aggregate_nodes import BestOfNNode
from aicodeprep_gui.pro.flow.nodes.llm_nodes import OpenAICompatibleNode


@patch("aicodeprep_gui.pro.flow.nodes.llm_nodes.LLMClient.chat")
@patch("aicodeprep_gui.pro.flow.nodes.llm_nodes.list_compatible_model_ids")
@patch("aicodeprep_gui.pro.flow.nodes.llm_nodes.get_active_endpoint")
def test_openai_compatible_node_runs_without_api_key(
    mock_get_active,
    mock_list_models,
    mock_chat,
):
    mock_get_active.return_value = {
        "url": "https://extra.wuu73.org/aimodels/v1",
        "api_key": "",
        "selected_model": "glm-5",
    }
    mock_list_models.return_value = ["glm-5"]
    mock_chat.return_value = "hello from compatible endpoint"

    node = OpenAICompatibleNode()
    result = node.run({"text": "hello"})

    assert result == {"text": "hello from compatible endpoint"}
    assert mock_chat.call_args.kwargs["model"] == "glm-5"
    assert mock_chat.call_args.kwargs["base_url"] == "https://extra.wuu73.org/aimodels/v1"
    assert mock_chat.call_args.kwargs["api_key"] == ""


@patch("aicodeprep_gui.pro.flow.nodes.aggregate_nodes.LLMClient.chat")
@patch("aicodeprep_gui.pro.flow.nodes.aggregate_nodes.list_compatible_model_ids")
@patch("aicodeprep_gui.pro.flow.nodes.aggregate_nodes.get_active_endpoint")
def test_best_of_n_compatible_runs_without_api_key(
    mock_get_active,
    mock_list_models,
    mock_chat,
):
    mock_get_active.return_value = {
        "url": "https://extra.wuu73.org/aimodels/v1",
        "api_key": "",
        "selected_model": "glm-5",
    }
    mock_list_models.return_value = ["glm-5"]
    mock_chat.return_value = "best answer"

    node = BestOfNNode()
    node.set_property("provider", "compatible")
    node.set_property("base_url", "")
    node.set_property("api_key", "")
    node.set_property("model_mode", "choose")
    node.set_property("model", "")

    result = node.run(
        {
            "context": "source context",
            "candidate1": "answer one",
            "candidate2": "answer two",
        }
    )

    assert result == {"text": "best answer"}
    assert mock_chat.call_args.kwargs["model"] == "glm-5"
    assert mock_chat.call_args.kwargs["base_url"] == "https://extra.wuu73.org/aimodels/v1"
    assert mock_chat.call_args.kwargs["api_key"] in ("", None)


def test_best_of_n_collects_sparse_candidates_without_stopping_at_first_gap():
    node = BestOfNNode()
    node.set_property("provider", "compatible")
    node.set_property("base_url", "https://extra.wuu73.org/aimodels/v1")
    node.set_property("api_key", "")
    node.set_property("model_mode", "choose")
    node.set_property("model", "glm-5")

    with patch("aicodeprep_gui.pro.flow.nodes.aggregate_nodes.LLMClient.chat", return_value="best answer") as mock_chat:
        result = node.run(
            {
                "context": "source context",
                "candidate2": "answer two",
                "candidate4": "answer four",
            }
        )

    assert result == {"text": "best answer"}
    prompt = mock_chat.call_args.kwargs["user_content"]
    assert "answer two" in prompt
    assert "answer four" in prompt


@patch("aicodeprep_gui.config.get_api_key", return_value=None)
@patch("aicodeprep_gui.pro.flow.nodes.aggregate_nodes.LLMClient.chat")
@patch("aicodeprep_gui.pro.flow.nodes.aggregate_nodes.list_compatible_model_ids")
@patch("aicodeprep_gui.pro.flow.nodes.aggregate_nodes.get_active_endpoint")
def test_best_of_n_compatible_random_tolerates_none_config_api_key(
    mock_get_active,
    mock_list_models,
    mock_chat,
    _mock_get_api_key,
):
    mock_get_active.return_value = {
        "url": "https://extra.wuu73.org/aimodels/v1",
        "api_key": "",
        "selected_model": "",
    }
    mock_list_models.return_value = ["minimax/minimax-m2.5:free"]
    mock_chat.return_value = "best answer"

    node = BestOfNNode()
    node.set_property("provider", "compatible")
    node.set_property("base_url", "")
    node.set_property("api_key", "")
    node.set_property("model_mode", "random")
    node.set_property("model", "")

    result = node.run(
        {
            "context": "source context",
            "candidate1": "answer one",
        }
    )

    assert result == {"text": "best answer"}
    assert mock_list_models.call_args.args == (
        "https://extra.wuu73.org/aimodels/v1",
        "",
    )
