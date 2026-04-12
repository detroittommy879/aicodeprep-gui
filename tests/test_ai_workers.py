import pytest
from unittest.mock import patch, MagicMock
from aicodeprep_gui.gui.handlers.ai_workers import PromptRewriteWorker, SmartSelectWorker
from aicodeprep_gui.pro.ai_assist.ai_client import AIClientError


def test_rewrite_worker_emits_finished():
    """Test PromptRewriteWorker emits finished signal with result."""
    original_prompt = "hello"
    rewritten_prompt = "Hello, world!"

    with patch("aicodeprep_gui.gui.handlers.ai_workers.AIClient.chat") as mock_chat:
        mock_chat.return_value = rewritten_prompt

        worker = PromptRewriteWorker(
            original_prompt, "model-x", "http://api.test", "key-123")

        results = []
        worker.finished.connect(lambda x: results.append(x))

        worker.run()

        assert len(results) == 1
        assert results[0] == rewritten_prompt
        mock_chat.assert_called_once()


def test_rewrite_worker_emits_error_on_failure():
    """Test PromptRewriteWorker emits error signal on failure."""
    with patch("aicodeprep_gui.gui.handlers.ai_workers.AIClient.chat") as mock_chat:
        mock_chat.side_effect = AIClientError("Connection failed")

        worker = PromptRewriteWorker("hello", "model-x", "http://api.test")

        errors = []
        worker.error.connect(lambda x: errors.append(x))

        worker.run()

        assert len(errors) == 1
        assert "Connection failed" in errors[0]


def test_smart_select_worker_parse_xml_response():
    """Test SmartSelectWorker._parse_file_list() with XML tags."""
    response = """
Here are the files you need:
<selected_files>
src/main.py
src/utils/helpers.py
tests/test_main.py
</selected_files>
    """
    paths = SmartSelectWorker._parse_file_list(response)
    assert paths == ["src/main.py",
                     "src/utils/helpers.py", "tests/test_main.py"]


def test_smart_select_worker_parse_markdown_response():
    """Test SmartSelectWorker._parse_file_list() with markdown list."""
    response = """
1. `src/main.py`
2. `src/utils/helpers.py`
* tests/test_main.py
    """
    paths = SmartSelectWorker._parse_file_list(response)
    assert paths == ["src/main.py",
                     "src/utils/helpers.py", "tests/test_main.py"]


def test_smart_select_worker_parse_with_size_info():
    """Test _parse_file_list() strips size and date info."""
    response = """
<selected_files>
src/main.py  (1.2KB, 2024-01-01)
src/utils/helpers.py  (450B, 2024-02-05)
</selected_files>
    """
    paths = SmartSelectWorker._parse_file_list(response)
    assert paths == ["src/main.py", "src/utils/helpers.py"]


def test_smart_select_build_prompt_includes_dir_listing():
    """Test _build_prompt() includes user prompt and directory listing."""
    worker = SmartSelectWorker(
        "Fix the login bug", "/dummy/path", "model-x", "http://api.test")

    with patch.object(SmartSelectWorker, "_build_directory_listing") as mock_listing:
        mock_listing.return_value = "file1.py\nfile2.py"

        prompt = worker._build_prompt("file1.py\nfile2.py")

        assert "<user_prompt>Fix the login bug</user_prompt>" in prompt
        assert "file1.py\nfile2.py" in prompt
        assert "<selected_files>" in prompt or "Analyze the user's task" in prompt
        assert "<directory_listing>" in prompt
