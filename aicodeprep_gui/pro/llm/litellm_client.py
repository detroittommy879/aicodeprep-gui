"""
Unified LiteLLM client wrapper for multiple LLM providers.
Supports OpenRouter, OpenAI, Gemini, and OpenAI-compatible endpoints.
"""

from __future__ import annotations
import os
import json
import random
import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    import litellm
except Exception as e:
    litellm = None
    _LITELLM_IMPORT_ERROR = e

import requests


class LLMError(Exception):
    """Exception raised by LLM client operations."""
    pass


class LLMClient:
    """
    Minimal wrapper on top of LiteLLM for simple chat completions and model listing.
    """

    @staticmethod
    def ensure_lib(parent=None):
        """Ensure LiteLLM is available, show error if not."""
        if litellm is None:
            logging.error(
                f"litellm is not installed. Please install it first.\n\n{_LITELLM_IMPORT_ERROR}"
            )
            raise LLMError("litellm not installed")

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
    ) -> str:
        """
        Perform a one-shot chat completion.
        """
        try:
            LLMClient.ensure_lib()

            headers = extra_headers.copy() if extra_headers else {}
            # LiteLLM uses `api_key` parameter; leave env fallback as-is
            kwargs = {}
            if api_key:
                kwargs["api_key"] = api_key
            if base_url:
                # Some providers (OpenRouter / generic OpenAI-compatible) need base_url
                kwargs["base_url"] = base_url

            messages = []
            if system_content:
                messages.append({"role": "system", "content": system_content})
            messages.append({"role": "user", "content": user_content})

            try:
                logging.info(
                    f"LiteLLM call starting - model: {model}, base_url: {base_url}, has_api_key: {bool(api_key)}")
                logging.info(
                    f"LiteLLM request details - messages: {len(messages)} message(s), "
                    f"user_content_length: {len(user_content)}, extra_headers: {list(headers.keys()) if headers else None}")

                # Warn about large inputs
                if len(user_content) > 100000:
                    logging.warning(
                        f"Large input detected ({len(user_content)} chars). This may take a while or hit token limits.")

                # Add timeout to prevent indefinite hangs
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = 120  # 2 minute timeout per request

                # Add temperature and top_p if provided
                if temperature is not None:
                    kwargs['temperature'] = temperature
                if top_p is not None:
                    kwargs['top_p'] = top_p

                resp = litellm.completion(
                    model=model,
                    messages=messages,
                    extra_headers=headers if headers else None,
                    **kwargs
                )
                # LiteLLM uses OpenAI response format
                content = resp.choices[0].message.get("content", "")
                logging.info(
                    f"LiteLLM call successful - response length: {len(content)}")
                return content
            except AttributeError as e:
                error_msg = f"Response format error: {e}. This may indicate an API compatibility issue."
                logging.error(error_msg, exc_info=True)
                raise LLMError(error_msg) from e
            except Exception as e:
                # Check if error is about unsupported temperature/top_p
                error_str = str(e).lower()
                if ('temperature' in error_str or 'top_p' in error_str) and ('unsupported' in error_str or 'not support' in error_str):
                    logging.warning(
                        f"Model doesn't support custom temperature/top_p, retrying with defaults: {e}")
                    # Retry without temperature and top_p
                    kwargs.pop('temperature', None)
                    kwargs.pop('top_p', None)
                    try:
                        resp = litellm.completion(
                            model=model,
                            messages=messages,
                            extra_headers=headers if headers else None,
                            **kwargs
                        )
                        content = resp.choices[0].message.get("content", "")
                        logging.info(
                            f"LiteLLM call successful (default temp) - response length: {len(content)}")
                        return content
                    except Exception as retry_e:
                        error_msg = f"Chat error (retry failed): {retry_e}"
                        logging.error(error_msg, exc_info=True)
                        raise LLMError(error_msg) from retry_e
                else:
                    error_msg = f"Chat error: {e}"
                    logging.error(error_msg, exc_info=True)
                    raise LLMError(error_msg) from e
        except Exception as outer_e:
            # Catch absolutely everything
            error_msg = f"Fatal LLM client error: {outer_e}"
            logging.error(error_msg, exc_info=True)
            raise LLMError(error_msg) from outer_e

    # ---- Model listing helpers ----

    @staticmethod
    def list_models_openrouter(api_key: str) -> List[Dict[str, Any]]:
        """
        List models via OpenRouter API: GET https://openrouter.ai/api/v1/models
        """
        url = "https://openrouter.ai/api/v1/models"
        try:
            logging.info(f"Fetching OpenRouter models from {url}")
            r = requests.get(
                url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            data = r.json()
            models = data.get("data", [])
            logging.info(f"Retrieved {len(models)} models from OpenRouter")
            return models
        except requests.exceptions.Timeout as e:
            logging.error(f"OpenRouter model list fetch timed out: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logging.error(
                f"OpenRouter model list fetch failed (network error): {e}")
            return []
        except Exception as e:
            logging.error(
                f"OpenRouter model list fetch failed (unexpected): {e}", exc_info=True)
            return []

    @staticmethod
    def list_models_openai(api_key: str) -> List[Dict[str, Any]]:
        """List models via OpenAI API."""
        url = "https://api.openai.com/v1/models"
        try:
            r = requests.get(
                url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            data = r.json()
            # OpenAI style returns {"data":[{"id":...}, ...]}
            return data.get("data", [])
        except Exception as e:
            logging.error(f"OpenAI model list fetch failed: {e}")
            return []

    @staticmethod
    def list_models_openai_compatible(base_url: str, api_key: str) -> List[Dict[str, Any]]:
        """
        Generic OpenAI-compatible endpoints should have /v1/models or /models
        We'll try both.
        """
        tried = []
        for suffix in ("/v1/models", "/models"):
            url = base_url.rstrip("/") + suffix
            tried.append(url)
            try:
                r = requests.get(
                    url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                if r.status_code == 404:
                    continue
                r.raise_for_status()
                data = r.json()
                return data.get("data", [])
            except Exception:
                continue
        logging.error(
            f"OpenAI-compatible models failed. Tried: {', '.join(tried)}")
        return []

    @staticmethod
    def openrouter_pick_model(models: List[Dict[str, Any]], free_only: bool) -> Optional[str]:
        """
        Pick a random model id from OpenRouter's list (optionally only ':free' models).
        """
        ids = []
        for m in models:
            mid = m.get("id") or m.get("name")
            if not mid:
                continue
            if free_only and not mid.endswith(":free"):
                continue
            ids.append(mid)
        if not ids:
            return None
        return random.choice(ids)
