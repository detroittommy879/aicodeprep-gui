import json
from pathlib import Path

from aicodeprep_gui.pro.flow.serializer import _normalize_node_data, validate_flow_structure


def test_validate_flow_structure_accepts_bundled_templates():
    data_dir = Path(__file__).resolve().parents[1] / "aicodeprep_gui" / "data"

    for file_name in ("flow.json", "flow_best_of_3.json"):
        payload = json.loads(
            (data_dir / file_name).read_text(encoding="utf-8"))
        normalized = _normalize_node_data(payload)
        assert validate_flow_structure(normalized) == []


def test_normalize_node_data_trims_string_fields():
    payload = {
        "graph": {},
        "nodes": {
            "node-1": {
                "type_": "aicp.flow.OpenAICompatibleNode",
                "custom": {
                    "model": " some-model\n",
                    "provider": " compatible ",
                    "base_url": " https://example.test/v1 ",
                },
                "subgraph_session": "{}",
            }
        },
        "connections": [],
    }

    normalized = _normalize_node_data(payload)
    custom = normalized["nodes"]["node-1"]["custom"]

    assert custom["model"] == "some-model"
    assert custom["provider"] == "compatible"
    assert custom["base_url"] == "https://example.test/v1"
    assert normalized["nodes"]["node-1"]["subgraph_session"] == {}


def test_validate_flow_structure_reports_missing_connection_node():
    payload = {
        "graph": {},
        "nodes": {
            "node-1": {
                "type_": "aicp.flow.ContextOutputNode",
                "custom": {},
                "subgraph_session": {},
            }
        },
        "connections": [
            {"out": ["node-1", "text"], "in": ["missing", "text"]}
        ],
    }

    errors = validate_flow_structure(payload)
    assert any("missing node 'missing'" in error for error in errors)
