from __future__ import annotations

import random
from typing import Iterable, Optional

from aicodeprep_gui.pro.llm.llm_client import LLMClient


def _prefer_anonymous_compatible_models(model_ids: list[str], api_key: Optional[str] = "") -> list[str]:
    """Prefer models that are more likely to work without an API key."""
    unique = list(dict.fromkeys(model_ids))
    normalized_api_key = (api_key or "").strip()
    if normalized_api_key:
        return unique

    preferred = []
    for model_id in unique:
        lowered = model_id.lower()
        if ":free" in lowered or lowered.endswith("/free") or "auto" in lowered:
            preferred.append(model_id)

    return preferred or unique


def list_compatible_model_ids(base_url: str, api_key: Optional[str] = "") -> list[str]:
    """Return unique model ids from an OpenAI-compatible endpoint."""
    if not base_url:
        return []

    ids: list[str] = []
    seen: set[str] = set()
    for item in LLMClient.list_models_openai_compatible(base_url, api_key):
        model_id = (item.get("id") or item.get("name") or "").strip()
        if model_id and model_id not in seen:
            seen.add(model_id)
            ids.append(model_id)
    return _prefer_anonymous_compatible_models(ids, api_key)


def choose_random_model_ids(
    model_ids: Iterable[str],
    count: int,
    rng: random.Random | random.Random = random,
) -> list[str]:
    """Choose up to count model ids, repeating randomly only when needed."""
    normalized = [model_id.strip()
                  for model_id in model_ids if model_id and model_id.strip()]
    if count <= 0 or not normalized:
        return []

    unique = list(dict.fromkeys(normalized))
    if len(unique) >= count:
        return list(rng.sample(unique, count))

    picks = unique[:]
    while len(picks) < count:
        picks.append(rng.choice(unique))
    return picks
