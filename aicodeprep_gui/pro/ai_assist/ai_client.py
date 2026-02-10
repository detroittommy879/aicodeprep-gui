import requests
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Custom exception for AI client failures."""
    pass


class AIClient:
    """
    OpenAI-compatible HTTP client using requests.
    Supports chat completions and model listing with automatic retries.
    """

    def __init__(self):
        self.session = requests.Session()

    def _request_with_retry(
        self,
        method: str,
        url: str,
        retries: int = 3,
        backoff_base: float = 1.0,
        timeout: int = 60,
        **kwargs
    ) -> requests.Response:
        """
        Internal request wrapper with exponential backoff retry logic.
        """
        last_exception = None
        for attempt in range(retries):
            try:
                response = self.session.request(
                    method, url, timeout=timeout, **kwargs)

                # Retry on 5xx errors
                if 500 <= response.status_code < 600:
                    logger.warning(
                        f"Server error {response.status_code} on attempt {attempt + 1}. Retrying...")
                    response.raise_for_status()  # This will be caught to retry

                return response

            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                last_exception = e
                if attempt < retries - 1:
                    sleep_time = backoff_base * (2 ** attempt)
                    logger.info(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Final attempt failed: {e}")

        raise AIClientError(
            f"Request failed after {retries} attempts: {last_exception}")

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        base_url: str,
        api_key: str = "",
        timeout: int = 60
    ) -> str:
        """
        Sends a chat completion request.
        """
        url = f"{base_url.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        try:
            response = self._request_with_retry(
                "POST",
                url,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("message", {}).get("content", "")
            else:
                raise AIClientError(
                    "Invalid response format: 'choices' missing or empty")

        except requests.exceptions.JSONDecodeError:
            raise AIClientError("Failed to parse response as JSON")
        except Exception as e:
            if isinstance(e, AIClientError):
                raise
            raise AIClientError(f"Chat completion failed: {str(e)}")

    def list_models(
        self,
        base_url: str,
        api_key: str = "",
        timeout: int = 10,
        retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Lists available models from the endpoint.
        Returns the 'data' array from the response.
        Use retries=1 for interactive / dialog use to avoid long freezes.
        """
        url = f"{base_url.rstrip('/')}/models"

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = self._request_with_retry(
                "GET",
                url,
                headers=headers,
                timeout=timeout,
                retries=retries
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            # According to specs: Should NOT raise on failure, just log and return empty list
            logger.error(f"Failed to list models from {url}: {e}")
            return []
