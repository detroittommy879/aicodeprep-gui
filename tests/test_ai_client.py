import unittest
from unittest.mock import patch, MagicMock
import requests
from aicodeprep_gui.pro.ai_assist.ai_client import AIClient, AIClientError


class TestAIClient(unittest.TestCase):
    def setUp(self):
        self.client = AIClient()
        self.base_url = "http://api.example.com/v1"
        self.api_key = "test-key"
        self.model = "gpt-3.5-turbo"
        self.messages = [{"role": "user", "content": "Hello"}]

    @patch("requests.Session.request")
    def test_ai_client_chat_success(self, mock_request):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hi there!"}}]
        }
        mock_request.return_value = mock_response

        result = self.client.chat(
            self.model, self.messages, self.base_url, self.api_key)

        self.assertEqual(result, "Hi there!")
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["json"]["model"], self.model)
        self.assertEqual(kwargs["headers"]
                         ["Authorization"], f"Bearer {self.api_key}")

    @patch("requests.Session.request")
    @patch("time.sleep", return_value=None)  # Skip sleep in tests
    def test_ai_client_chat_retry_on_failure(self, mock_sleep, mock_request):
        # Mock two failures then success
        mock_failure = MagicMock()
        mock_failure.status_code = 500
        mock_failure.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Server Error")

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {
            "choices": [{"message": {"content": "Success after retries"}}]
        }

        # Side effect: failure, failure, success
        mock_request.side_effect = [requests.exceptions.ConnectionError(
        ), requests.exceptions.Timeout(), mock_success]

        result = self.client.chat(
            self.model, self.messages, self.base_url, self.api_key)

        self.assertEqual(result, "Success after retries")
        self.assertEqual(mock_request.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("requests.Session.request")
    def test_ai_client_list_models(self, mock_request):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"id": "model-1"}, {"id": "model-2"}]
        }
        mock_request.return_value = mock_response

        result = self.client.list_models(self.base_url, self.api_key)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "model-1")
        mock_request.assert_called_once()
        self.assertTrue(self.base_url in mock_request.call_args[0][1])

    @patch("requests.Session.request")
    @patch("time.sleep", return_value=None)
    def test_ai_client_timeout_handling(self, mock_sleep, mock_request):
        # Mock all attempts failing with timeout
        mock_request.side_effect = requests.exceptions.Timeout("Timeout")

        with self.assertRaises(AIClientError):
            self.client.chat(self.model, self.messages,
                             self.base_url, self.api_key)

        self.assertEqual(mock_request.call_count, 3)

    @patch("requests.Session.request")
    def test_ai_client_chat_sends_correct_headers(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]}
        mock_request.return_value = mock_response

        self.client.chat(self.model, self.messages,
                         self.base_url, api_key="secret-token")

        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]
                         ["Authorization"], "Bearer secret-token")

    @patch("requests.Session.request")
    def test_ai_client_chat_no_auth_header_when_no_key(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]}
        mock_request.return_value = mock_response

        self.client.chat(self.model, self.messages, self.base_url, api_key="")

        _, kwargs = mock_request.call_args
        self.assertNotIn("Authorization", kwargs["headers"])

    @patch("requests.Session.request")
    def test_ai_client_chat_stream_preserves_post_across_redirect(self, mock_request):
        redirect_response = MagicMock()
        redirect_response.status_code = 301
        redirect_response.headers = {
            "Location": "https://api.example.com/v1/chat/completions"}

        stream_response = MagicMock()
        stream_response.status_code = 200
        stream_response.headers = {}
        stream_response.iter_lines.return_value = iter([
            'data: {"choices":[{"delta":{"content":"Hi"}}]}',
            'data: [DONE]',
        ])
        stream_response.raise_for_status.return_value = None

        mock_request.side_effect = [redirect_response, stream_response]

        result = self.client.chat_stream(
            self.model, self.messages, self.base_url, self.api_key)

        self.assertEqual(result, "Hi")
        self.assertEqual(mock_request.call_args_list[0].args[:2], (
            "POST",
            "http://api.example.com/v1/chat/completions",
        ))
        self.assertEqual(mock_request.call_args_list[1].args[:2], (
            "POST",
            "https://api.example.com/v1/chat/completions",
        ))


if __name__ == "__main__":
    unittest.main()
