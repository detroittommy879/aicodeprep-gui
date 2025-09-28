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
            from PySide6 import QtWidgets
            QtWidgets.QMessageBox.critical(
                parent,
                "LiteLLM missing",
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
    ) -> str:
        """
        Perform a one-shot chat completion.
        """
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
            resp = litellm.completion(
                model=model,
                messages=messages,
                extra_headers=headers if headers else None,
                **kwargs
            )
            # LiteLLM uses OpenAI response format
            return resp.choices[0].message.get("content", "")
        except Exception as e:
            raise LLMError(f"Chat error: {e}") from e

    # ---- Model listing helpers ----

    @staticmethod
    def list_models_openrouter(api_key: str) -> List[Dict[str, Any]]:
        """
        List models via OpenRouter API: GET https://openrouter.ai/api/v1/models
        """
        url = "https://openrouter.ai/api/v1/models"
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            data = r.json()
            return data.get("data", [])
        except Exception as e:
            logging.error(f"OpenRouter model list fetch failed: {e}")
            return []

    @staticmethod
    def list_models_openai(api_key: str) -> List[Dict[str, Any]]:
        """List models via OpenAI API."""
        url = "https://api.openai.com/v1/models"
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
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
                r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                if r.status_code == 404:
                    continue
                r.raise_for_status()
                data = r.json()
                return data.get("data", [])
            except Exception:
                continue
        logging.error(f"OpenAI-compatible models failed. Tried: {', '.join(tried)}")
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