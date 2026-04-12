import random

from aicodeprep_gui.pro.flow.model_picker import (
    _prefer_anonymous_compatible_models,
    choose_random_model_ids,
)


def test_choose_random_model_ids_repeats_when_needed():
    picks = choose_random_model_ids(
        ["model-a", "model-b"], 5, rng=random.Random(0))

    assert len(picks) == 5
    assert set(picks).issubset({"model-a", "model-b"})


def test_choose_random_model_ids_prefers_unique_when_possible():
    picks = choose_random_model_ids(
        ["model-a", "model-b", "model-c", "model-d"],
        3,
        rng=random.Random(1),
    )

    assert len(picks) == 3
    assert len(set(picks)) == 3


def test_prefer_anonymous_compatible_models_filters_to_free_and_auto_when_no_api_key():
    picks = _prefer_anonymous_compatible_models(
        [
            "qwen3-coder-plus",
            "minimax/minimax-m2.5:free",
            "kilo/auto",
            "glm-5",
            "kilo-auto/free",
        ],
        api_key="",
    )

    assert picks == [
        "minimax/minimax-m2.5:free",
        "kilo/auto",
        "kilo-auto/free",
    ]


def test_prefer_anonymous_compatible_models_keeps_all_with_api_key():
    model_ids = ["qwen3-coder-plus", "glm-5", "minimax/minimax-m2.5:free"]

    assert _prefer_anonymous_compatible_models(
        model_ids, api_key="secret") == model_ids


def test_prefer_anonymous_compatible_models_accepts_none_api_key():
    picks = _prefer_anonymous_compatible_models(
        [
            "qwen3-coder-plus",
            "minimax/minimax-m2.5:free",
            "kilo/auto",
        ],
        api_key=None,
    )

    assert picks == [
        "minimax/minimax-m2.5:free",
        "kilo/auto",
    ]
