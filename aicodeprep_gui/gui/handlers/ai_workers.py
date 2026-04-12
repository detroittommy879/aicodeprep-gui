import os
import re
import logging
from datetime import datetime
from PySide6 import QtCore
from aicodeprep_gui.pro.ai_assist.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class PromptRewriteWorker(QtCore.QObject):
    """Worker that rewrites a user prompt via AI for better LLM responses."""
    finished = QtCore.Signal(str)   # rewritten prompt text
    error = QtCore.Signal(str)      # error message

    def __init__(self, original_prompt: str, model: str, base_url: str, api_key: str = ""):
        super().__init__()
        self.original_prompt = original_prompt
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

    def run(self):
        """Execute the rewrite request."""
        try:
            client = AIClient()
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a prompt engineering expert. Rewrite the following prompt to get "
                        "better, more detailed, and more useful responses from AI coding assistants. "
                        "Keep the original intent but make it clearer, more specific, and better structured. "
                        "Return ONLY the rewritten prompt, nothing else — no explanation, no preamble."
                    )
                },
                {
                    "role": "user",
                    "content": self.original_prompt
                }
            ]
            result = client.chat(self.model, messages,
                                 self.base_url, self.api_key)
            self.finished.emit(result.strip())
        except AIClientError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")


class SmartSelectWorker(QtCore.QObject):
    """Worker that uses AI to suggest which files should be selected based on the user's prompt."""
    finished = QtCore.Signal(list)   # list of file paths to check
    error = QtCore.Signal(str)       # error message

    def __init__(self, user_prompt: str, project_dir: str, model: str, base_url: str, api_key: str = ""):
        super().__init__()
        self.user_prompt = user_prompt
        self.project_dir = project_dir
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

    def run(self):
        """Execute the smart select request."""
        try:
            dir_listing = self._build_directory_listing()
            prompt = self._build_prompt(dir_listing)

            client = AIClient()
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a code project analyst. Given a user's task/prompt and a directory listing, "
                        "determine which files are most likely needed to accomplish the task. "
                        "Respond with ONLY a list of file paths — one per line, using the exact relative paths "
                        "from the directory listing. Wrap them in <selected_files> XML tags. Example:\n"
                        "<selected_files>\n"
                        "src/main.py\n"
                        "src/utils/helpers.py\n"
                        "tests/test_main.py\n"
                        "</selected_files>\n"
                        "Include ONLY files that are relevant. Do NOT include build artifacts, "
                        "node_modules, __pycache__, .git, or binary files unless specifically needed."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            result = client.chat(self.model, messages,
                                 self.base_url, self.api_key, timeout=90)
            file_list = self._parse_file_list(result)
            self.finished.emit(file_list)
        except AIClientError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")

    def _build_directory_listing(self) -> str:
        """Walk the project directory and build a listing with file sizes and dates."""
        lines = []
        try:
            for root, dirs, files in os.walk(self.project_dir):
                # Skip common excluded directories
                dirs[:] = [d for d in dirs if d not in {
                    '.git', '__pycache__', 'node_modules', '.tox', '.mypy_cache',
                    '.pytest_cache', 'dist', 'build', '.eggs', '*.egg-info',
                    '.aicp', '.venv', 'venv', 'env', '.env'
                }]

                rel_root = os.path.relpath(root, self.project_dir)
                if rel_root == '.':
                    rel_root = ''

                for d in sorted(dirs):
                    dir_path = os.path.join(rel_root, d) if rel_root else d
                    lines.append(f"{dir_path}/")

                for f in sorted(files):
                    file_path = os.path.join(rel_root, f) if rel_root else f
                    abs_path = os.path.join(root, f)
                    try:
                        stat = os.stat(abs_path)
                        size = stat.st_size
                        mtime = datetime.fromtimestamp(
                            stat.st_mtime).strftime('%Y-%m-%d')

                        # Human-readable size
                        if size < 1024:
                            size_str = f"{size}B"
                        elif size < 1024 * 1024:
                            size_str = f"{size / 1024:.1f}KB"
                        else:
                            size_str = f"{size / (1024 * 1024):.1f}MB"

                        lines.append(f"{file_path}  ({size_str}, {mtime})")
                    except OSError:
                        lines.append(file_path)
        except OSError as e:
            logger.error(f"Error building directory listing: {e}")

        return "\n".join(lines)

    def _build_prompt(self, dir_listing: str) -> str:
        """Build the XML-tagged prompt for the LLM."""
        return (
            f"<user_prompt>{self.user_prompt}</user_prompt>\n\n"
            f"<directory_listing>\n{dir_listing}\n</directory_listing>\n\n"
            f"<instructions>\n"
            f"Analyze the user's task/prompt above and look at the directory listing. "
            f"Determine which files are most likely needed to accomplish the task described in the user_prompt. "
            f"Consider file names, paths, and the nature of the task. "
            f"Return the selected file paths wrapped in <selected_files> tags, one path per line. "
            f"Use the exact relative paths as shown in the directory listing (without the size/date info). "
            f"Only include files, not directories.\n"
            f"</instructions>"
        )

    @staticmethod
    def _parse_file_list(response: str) -> list:
        """Parse the LLM response to extract file paths.

        Supports two formats:
        1. XML: <selected_files>path1\npath2\n...</selected_files>
        2. Fallback: line-by-line parsing for paths (lines containing / or . that look like file paths)
        """
        # Try XML parsing first
        xml_match = re.search(
            r'<selected_files>(.*?)</selected_files>', response, re.DOTALL)
        if xml_match:
            content = xml_match.group(1).strip()
            paths = []
            for line in content.split('\n'):
                line = line.strip()
                # Remove any markdown formatting like backticks, bullets, numbers
                line = re.sub(r'^[\s\-\*\d\.]+', '', line).strip()
                line = line.strip('`').strip()
                if line and not line.startswith('#') and not line.startswith('//'):
                    # Remove size/date info if present (e.g., "  (1.2KB, 2024-01-01)")
                    line = re.sub(
                        r'\s*\([\d\.]+[BKMG]+,\s*\d{4}-\d{2}-\d{2}\)\s*$', '', line)
                    if line:
                        paths.append(line)
            return paths

        # Fallback: line-by-line path detection
        paths = []
        for line in response.split('\n'):
            line = line.strip()
            line = re.sub(r'^[\s\-\*\d\.]+', '', line).strip()
            line = line.strip('`').strip()
            # Looks like a file path if it contains a dot extension or forward slash
            if line and ('/' in line or '\\' in line or re.search(r'\.\w+$', line)):
                if not line.startswith('#') and not line.startswith('//') and len(line) < 200:
                    line = re.sub(
                        r'\s*\([\d\.]+[BKMG]+,\s*\d{4}-\d{2}-\d{2}\)\s*$', '', line)
                    if line and not line.endswith('/'):
                        paths.append(line)
        return paths
