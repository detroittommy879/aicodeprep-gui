"""HTTP-based client for multiple LLM providers used by Flow Studio."""

from __future__ import annotations

import json
import logging
import random
import time
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin

import requests


OPENAI_API_BASE = "https://api.openai.com/v1"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class LLMError(Exception):
    """Exception raised by LLM client operations."""


class ChatResponseIterator:
    """Iterator that yields chunks from a streaming LLM response."""

    def __init__(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        provider: Optional[str] = None,
    ):
        self.model = model
        self.messages = messages
        self.api_key = api_key
        self.base_url = base_url
        self.extra_headers = extra_headers or {}
        self.temperature = temperature
        self.top_p = top_p
        self.provider = provider
        self._iterator: Optional[Iterator[str]] = None
        self._complete_response = ""

    def _init_stream(self) -> Iterator[str]:
        return LLMClient._stream_response_chunks(
            model=self.model,
            messages=self.messages,
            api_key=self.api_key,
            base_url=self.base_url,
            extra_headers=self.extra_headers,
            temperature=self.temperature,
            top_p=self.top_p,
            provider=self.provider,
        )

    def __iter__(self):
        self._iterator = self._init_stream()
        self._complete_response = ""
        return self

    def __next__(self):
        if self._iterator is None:
            raise StopIteration

        try:
            content = next(self._iterator)
        except StopIteration:
            raise
        except Exception as exc:
            raise LLMError(f"Stream error: {exc}") from exc

        if content:
            self._complete_response += content
        return content

    def get_complete_response(self) -> str:
        return self._complete_response


class LLMClient:
    """Minimal HTTP wrapper for chat completions and model listing."""

    @staticmethod
    def _request_with_retry(
        method: str,
        url: str,
        *,
        retries: int = 3,
        backoff_base: float = 1.0,
        timeout: int = 120,
        **kwargs,
    ) -> requests.Response:
        last_exception: Optional[Exception] = None

        for attempt in range(retries):
            try:
                response = LLMClient._request_following_redirects(
                    method, url, timeout=timeout, **kwargs)
                if 500 <= response.status_code < 600:
                    response.raise_for_status()
                return response
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as exc:
                last_exception = exc
                if attempt >= retries - 1:
                    break
                sleep_time = backoff_base * (2 ** attempt)
                logging.info(
                    "Request failed on attempt %s/%s for %s %s: %s. Retrying in %.1fs.",
                    attempt + 1,
                    retries,
                    method,
                    url,
                    exc,
                    sleep_time,
                )
                time.sleep(sleep_time)

        raise LLMError(
            f"Request failed after {retries} attempts: {last_exception}")

    @staticmethod
    def _request_following_redirects(
        method: str,
        url: str,
        *,
        timeout: int,
        max_redirects: int = 5,
        **kwargs,
    ) -> requests.Response:
        request_method = method.upper()
        request_url = url
        request_kwargs = dict(kwargs)
        request_kwargs["allow_redirects"] = False

        for redirect_index in range(max_redirects + 1):
            response = requests.request(
                request_method,
                request_url,
                timeout=timeout,
                **request_kwargs,
            )

            location = response.headers.get("Location", "")
            if response.status_code not in {301, 302, 303, 307, 308} or not location:
                return response

            if redirect_index >= max_redirects:
                raise LLMError(f"Too many redirects while requesting {url}")

            next_url = urljoin(request_url, location)
            logging.info(
                "LLMClient redirect preserved method %s: %s -> %s (%s)",
                request_method,
                request_url,
                next_url,
                response.status_code,
            )

            if response.status_code == 303 and request_method not in {"GET", "HEAD"}:
                request_method = "GET"
                request_kwargs.pop("json", None)
                request_kwargs.pop("data", None)

            request_url = next_url

        return response

    @staticmethod
    def _build_openai_headers(
        api_key: Optional[str],
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    @staticmethod
    def _normalize_provider(provider: Optional[str], base_url: Optional[str]) -> str:
        normalized = (provider or "").strip().lower()
        if normalized in {"openai", "openrouter", "gemini", "compatible", "generic"}:
            return normalized

        lowered_base_url = (base_url or "").lower()
        if "openrouter.ai" in lowered_base_url:
            return "openrouter"
        if "generativelanguage.googleapis.com" in lowered_base_url:
            return "gemini"
        if lowered_base_url:
            return "compatible"
        return "openai"

    @staticmethod
    def _normalize_model(model: str, provider: str) -> str:
        cleaned = (model or "").strip()
        if provider == "openrouter" and cleaned.startswith("openrouter/"):
            return cleaned.split("/", 1)[1]
        if provider == "gemini":
            for prefix in ("gemini/", "google/"):
                if cleaned.startswith(prefix):
                    cleaned = cleaned.split("/", 1)[1]
            return cleaned
        return cleaned

    @staticmethod
    def _resolve_base_url(provider: str, base_url: Optional[str]) -> str:
        normalized_base_url = (base_url or "").strip()
        if normalized_base_url:
            return normalized_base_url
        if provider == "openai":
            return OPENAI_API_BASE
        if provider == "openrouter":
            return OPENROUTER_API_BASE
        if provider == "gemini":
            return GEMINI_API_BASE
        return normalized_base_url

    @staticmethod
    def _is_unsupported_param_error(error: Exception) -> bool:
        error_str = str(error).lower()
        has_param_name = "temperature" in error_str or "top_p" in error_str
        has_unsupported_hint = any(
            hint in error_str
            for hint in ("unsupported", "not support", "unknown field", "invalid argument")
        )
        return has_param_name and has_unsupported_hint

    @staticmethod
    def _coerce_content_to_text(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)
            return "\n".join(part for part in parts if part)
        return ""

    @staticmethod
    def _build_openai_payload(
        model: str,
        messages: List[Dict[str, Any]],
        temperature: Optional[float],
        top_p: Optional[float],
        stream: bool,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        return payload

    @staticmethod
    def _build_gemini_payload(
        messages: List[Dict[str, Any]],
        temperature: Optional[float],
        top_p: Optional[float],
    ) -> Dict[str, Any]:
        contents: List[Dict[str, Any]] = []
        system_instruction: Optional[Dict[str, Any]] = None

        for message in messages:
            role = (message.get("role") or "user").lower()
            text = LLMClient._coerce_content_to_text(message.get("content"))
            if not text:
                continue

            if role == "system":
                system_instruction = {"parts": [{"text": text}]}
                continue

            gemini_role = "model" if role == "assistant" else "user"
            contents.append({"role": gemini_role, "parts": [{"text": text}]})

        payload: Dict[str, Any] = {"contents": contents}
        generation_config: Dict[str, Any] = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if top_p is not None:
            generation_config["topP"] = top_p
        if generation_config:
            payload["generationConfig"] = generation_config
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        return payload

    @staticmethod
    def _extract_message_content(message: Any) -> str:
        if message is None:
            return ""

        if hasattr(message, "get"):
            content = message.get("content", "")
            if content:
                return LLMClient._coerce_content_to_text(content)

            reasoning = message.get(
                "reasoning") or message.get("reasoning_content")
            if isinstance(reasoning, str) and reasoning.strip():
                return reasoning

            reasoning_details = message.get("reasoning_details") or []
            if isinstance(reasoning_details, list):
                parts = []
                for item in reasoning_details:
                    if not isinstance(item, dict):
                        continue
                    text = item.get("text") or item.get(
                        "content") or item.get("reasoning")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
                if parts:
                    return "\n\n".join(parts)

        content = getattr(message, "content", "")
        if isinstance(content, str) and content:
            return content

        reasoning = getattr(message, "reasoning", "") or getattr(
            message, "reasoning_content", "")
        if isinstance(reasoning, str) and reasoning.strip():
            return reasoning

        reasoning_details = getattr(message, "reasoning_details", None) or []
        if isinstance(reasoning_details, list):
            parts = []
            for item in reasoning_details:
                if not isinstance(item, dict):
                    continue
                text = item.get("text") or item.get(
                    "content") or item.get("reasoning")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
            if parts:
                return "\n\n".join(parts)

        return ""

    @staticmethod
    def _extract_gemini_text(data: Dict[str, Any]) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            prompt_feedback = data.get("promptFeedback") or {}
            block_reason = prompt_feedback.get("blockReason")
            if block_reason:
                raise LLMError(f"Gemini blocked the response: {block_reason}")
            raise LLMError("Gemini response did not include candidates")

        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        text_parts: List[str] = []
        for part in parts:
            text = part.get("text")
            if isinstance(text, str) and text:
                text_parts.append(text)
        return "\n".join(text_parts).strip()

    @staticmethod
    def _chat_openai_family(
        *,
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str],
        base_url: Optional[str],
        extra_headers: Optional[Dict[str, str]],
        temperature: Optional[float],
        top_p: Optional[float],
        timeout: int,
    ) -> str:
        resolved_base_url = LLMClient._resolve_base_url(provider, base_url)
        if not resolved_base_url:
            raise LLMError(
                f"Chat error: provider '{provider}' requires a base_url")

        normalized_model = LLMClient._normalize_model(model, provider)
        payload = LLMClient._build_openai_payload(
            model=normalized_model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=False,
        )
        headers = LLMClient._build_openai_headers(api_key, extra_headers)
        url = f"{resolved_base_url.rstrip('/')}/chat/completions"

        response = LLMClient._request_with_retry(
            "POST",
            url,
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        try:
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise LLMError(
                f"Chat error: invalid JSON response: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            body = response.text.strip() if response.text else str(exc)
            raise LLMError(f"Chat error: {body}") from exc

        choices = data.get("choices") or []
        if not choices:
            raise LLMError("Chat error: response did not include choices")

        message = choices[0].get("message")
        content = LLMClient._extract_message_content(message)
        logging.info(
            "LLM call successful - provider: %s, response length: %s", provider, len(content))
        return content

    @staticmethod
    def _chat_gemini(
        *,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str],
        base_url: Optional[str],
        extra_headers: Optional[Dict[str, str]],
        temperature: Optional[float],
        top_p: Optional[float],
        timeout: int,
    ) -> str:
        if not api_key:
            raise LLMError("Chat error: Gemini requires an API key")

        resolved_base_url = LLMClient._resolve_base_url("gemini", base_url)
        normalized_model = LLMClient._normalize_model(model, "gemini")
        payload = LLMClient._build_gemini_payload(messages, temperature, top_p)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-goog-api-key": api_key,
        }
        if extra_headers:
            headers.update(extra_headers)

        url = f"{resolved_base_url.rstrip('/')}/models/{normalized_model}:generateContent"
        response = LLMClient._request_with_retry(
            "POST",
            url,
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        try:
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise LLMError(
                f"Gemini error: invalid JSON response: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            body = response.text.strip() if response.text else str(exc)
            raise LLMError(f"Gemini error: {body}") from exc

        content = LLMClient._extract_gemini_text(data)
        logging.info(
            "Gemini call successful - response length: %s", len(content))
        return content

    @staticmethod
    def _chat_openai_compatible(
        model: str,
        messages: List[Dict[str, Any]],
        base_url: str,
        api_key: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        timeout: int = 120,
    ) -> str:
        return LLMClient._chat_openai_family(
            provider="compatible",
            model=model,
            messages=messages,
            api_key=api_key,
            base_url=base_url,
            extra_headers=extra_headers,
            temperature=temperature,
            top_p=top_p,
            timeout=timeout,
        )

    @staticmethod
    def chat(
        model: str,
        user_content: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        system_content: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        provider: Optional[str] = None,
    ) -> str:
        try:
            headers = extra_headers.copy() if extra_headers else {}
            messages: List[Dict[str, Any]] = []
            if system_content:
                messages.append({"role": "system", "content": system_content})
            messages.append({"role": "user", "content": user_content})

            resolved_provider = LLMClient._normalize_provider(
                provider, base_url)

            def request_once(use_sampling: bool) -> str:
                request_temperature = temperature if use_sampling else None
                request_top_p = top_p if use_sampling else None

                if resolved_provider == "gemini":
                    return LLMClient._chat_gemini(
                        model=model,
                        messages=messages,
                        api_key=api_key,
                        base_url=base_url,
                        extra_headers=headers if headers else None,
                        temperature=request_temperature,
                        top_p=request_top_p,
                        timeout=120,
                    )

                return LLMClient._chat_openai_family(
                    provider=resolved_provider,
                    model=model,
                    messages=messages,
                    api_key=api_key,
                    base_url=base_url,
                    extra_headers=headers if headers else None,
                    temperature=request_temperature,
                    top_p=request_top_p,
                    timeout=120,
                )

            logging.info(
                "LLM call starting - provider: %s, model: %s, base_url: %s, has_api_key: %s",
                resolved_provider,
                model,
                base_url,
                bool(api_key),
            )
            logging.info(
                "LLM request details - messages: %s message(s), user_content_length: %s, extra_headers: %s",
                len(messages),
                len(user_content),
                list(headers.keys()) if headers else None,
            )

            if len(user_content) > 100000:
                logging.warning(
                    "Large input detected (%s chars). This may take a while or hit token limits.",
                    len(user_content),
                )

            try:
                return request_once(use_sampling=True)
            except Exception as exc:
                if (temperature is not None or top_p is not None) and LLMClient._is_unsupported_param_error(exc):
                    logging.warning(
                        "Model or endpoint rejected custom temperature/top_p, retrying with defaults: %s",
                        exc,
                    )
                    return request_once(use_sampling=False)
                raise
        except Exception as outer_exc:
            error_msg = f"Fatal LLM client error: {outer_exc}"
            logging.error(error_msg, exc_info=True)
            raise LLMError(error_msg) from outer_exc

    @staticmethod
    def _iter_openai_stream(response: requests.Response) -> Iterator[str]:
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue

            payload = line[5:].strip()
            if payload == "[DONE]":
                break

            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue

            choices = chunk.get("choices") or []
            if not choices:
                continue

            delta = choices[0].get("delta") or {}
            content = LLMClient._coerce_content_to_text(delta.get("content"))
            if content:
                yield content

    @staticmethod
    def _iter_gemini_stream(response: requests.Response) -> Iterator[str]:
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue

            payload = line[5:].strip()
            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue

            text = LLMClient._extract_gemini_text(chunk)
            if text:
                yield text

    @staticmethod
    def _stream_openai_family(
        *,
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str],
        base_url: Optional[str],
        extra_headers: Optional[Dict[str, str]],
        temperature: Optional[float],
        top_p: Optional[float],
        timeout: int,
    ) -> Iterator[str]:
        resolved_base_url = LLMClient._resolve_base_url(provider, base_url)
        if not resolved_base_url:
            raise LLMError(
                f"Chat error: provider '{provider}' requires a base_url")

        normalized_model = LLMClient._normalize_model(model, provider)
        payload = LLMClient._build_openai_payload(
            model=normalized_model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=True,
        )
        headers = LLMClient._build_openai_headers(api_key, extra_headers)
        url = f"{resolved_base_url.rstrip('/')}/chat/completions"
        response = LLMClient._request_with_retry(
            "POST",
            url,
            json=payload,
            headers=headers,
            timeout=timeout,
            stream=True,
        )
        response.raise_for_status()
        return LLMClient._iter_openai_stream(response)

    @staticmethod
    def _stream_gemini(
        *,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str],
        base_url: Optional[str],
        extra_headers: Optional[Dict[str, str]],
        temperature: Optional[float],
        top_p: Optional[float],
        timeout: int,
    ) -> Iterator[str]:
        if not api_key:
            raise LLMError("Chat error: Gemini requires an API key")

        resolved_base_url = LLMClient._resolve_base_url("gemini", base_url)
        normalized_model = LLMClient._normalize_model(model, "gemini")
        payload = LLMClient._build_gemini_payload(messages, temperature, top_p)
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "x-goog-api-key": api_key,
        }
        if extra_headers:
            headers.update(extra_headers)

        url = (
            f"{resolved_base_url.rstrip('/')}/models/"
            f"{normalized_model}:streamGenerateContent?alt=sse"
        )
        response = LLMClient._request_with_retry(
            "POST",
            url,
            json=payload,
            headers=headers,
            timeout=timeout,
            stream=True,
        )
        response.raise_for_status()
        return LLMClient._iter_gemini_stream(response)

    @staticmethod
    def _stream_response_chunks(
        *,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str],
        base_url: Optional[str],
        extra_headers: Optional[Dict[str, str]],
        temperature: Optional[float],
        top_p: Optional[float],
        provider: Optional[str],
    ) -> Iterator[str]:
        resolved_provider = LLMClient._normalize_provider(provider, base_url)
        if resolved_provider == "gemini":
            return LLMClient._stream_gemini(
                model=model,
                messages=messages,
                api_key=api_key,
                base_url=base_url,
                extra_headers=extra_headers,
                temperature=temperature,
                top_p=top_p,
                timeout=120,
            )
        return LLMClient._stream_openai_family(
            provider=resolved_provider,
            model=model,
            messages=messages,
            api_key=api_key,
            base_url=base_url,
            extra_headers=extra_headers,
            temperature=temperature,
            top_p=top_p,
            timeout=120,
        )

    @staticmethod
    def stream_chat(
        model: str,
        messages: List[Dict[str, str]],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        provider: Optional[str] = None,
    ) -> ChatResponseIterator:
        return ChatResponseIterator(
            model=model,
            messages=messages,
            api_key=api_key,
            base_url=base_url,
            extra_headers=extra_headers,
            temperature=temperature,
            top_p=top_p,
            provider=provider,
        )

    @staticmethod
    def list_models_openrouter(api_key: str) -> List[Dict[str, Any]]:
        url = f"{OPENROUTER_API_BASE}/models"
        try:
            logging.info("Fetching OpenRouter models from %s", url)
            response = LLMClient._request_with_retry(
                "GET",
                url,
                headers=LLMClient._build_openai_headers(api_key),
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            models = data.get("data", [])
            logging.info("Retrieved %s models from OpenRouter", len(models))
            return models
        except requests.exceptions.Timeout as exc:
            logging.error("OpenRouter model list fetch timed out: %s", exc)
            return []
        except requests.exceptions.RequestException as exc:
            logging.error(
                "OpenRouter model list fetch failed (network error): %s", exc)
            return []
        except Exception as exc:
            logging.error(
                "OpenRouter model list fetch failed (unexpected): %s", exc, exc_info=True)
            return []

    @staticmethod
    def list_models_openai(api_key: str) -> List[Dict[str, Any]]:
        url = f"{OPENAI_API_BASE}/models"
        try:
            response = LLMClient._request_with_retry(
                "GET",
                url,
                headers=LLMClient._build_openai_headers(api_key),
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as exc:
            logging.error("OpenAI model list fetch failed: %s", exc)
            return []

    @staticmethod
    def list_models_openai_compatible(base_url: str, api_key: str) -> List[Dict[str, Any]]:
        tried = []
        headers = LLMClient._build_openai_headers(api_key)
        for suffix in ("/v1/models", "/models"):
            url = base_url.rstrip("/") + suffix
            tried.append(url)
            try:
                response = LLMClient._request_with_retry(
                    "GET",
                    url,
                    headers=headers,
                    timeout=10,
                )
                if response.status_code == 404:
                    continue
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])
            except Exception:
                continue
        logging.error(
            "OpenAI-compatible models failed. Tried: %s", ", ".join(tried))
        return []

    @staticmethod
    def openrouter_pick_model(models: List[Dict[str, Any]], free_only: bool) -> Optional[str]:
        ids = []
        for model in models:
            model_id = model.get("id") or model.get("name")
            if not model_id:
                continue
            if free_only and not model_id.endswith(":free"):
                continue
            ids.append(model_id)
        if not ids:
            return None
        return random.choice(ids)
