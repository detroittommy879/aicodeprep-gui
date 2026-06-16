import json

from aicodeprep_gui.pro.flow.flow_repair import FlowAutoRepairer, extract_flow_json_tag


def _valid_flow_payload():
    return {
        "graph": {},
        "nodes": {
            "context": {
                "type_": "aicp.flow.ContextOutputNode",
                "custom": {},
                "subgraph_session": {},
            },
            "clip": {
                "type_": "aicp.flow.ClipboardNode",
                "custom": {},
                "subgraph_session": {},
            },
        },
        "connections": [
            {"out": ["context", "text"], "in": ["clip", "text"]}
        ],
    }


def test_extract_flow_json_tag_supports_short_closing_tag():
    text = "prefix <flow.json>{\"graph\": {}, \"nodes\": {}, \"connections\": []}</> suffix"
    assert extract_flow_json_tag(
        text) == '{"graph": {}, "nodes": {}, "connections": []}'


def test_flow_auto_repair_falls_through_models(monkeypatch):
    class FakeClient:
        def __init__(self):
            self.calls = []

        def list_models(self, base_url, api_key="", timeout=10, retries=1):
            return [{"id": "model-a"}, {"id": "model-b"}]

        def chat(self, model, messages, base_url, api_key="", timeout=60):
            self.calls.append(model)
            if model == "selected-model":
                raise RuntimeError("selected model unavailable")
            if model == "model-a":
                broken = {
                    "graph": {},
                    "nodes": {
                        "only": {
                            "type_": "aicp.flow.ContextOutputNode",
                            "custom": {},
                            "subgraph_session": {},
                        }
                    },
                    "connections": [
                        {"out": ["only", "text"], "in": ["missing", "text"]}
                    ],
                }
                return f"<flow.json>{json.dumps(broken)}</flow.json>"
            return f"<flow.json>{json.dumps(_valid_flow_payload())}</flow.json>"

    monkeypatch.setattr(
        "aicodeprep_gui.pro.flow.flow_repair.get_active_endpoint",
        lambda: {
            "url": "https://extra.wuu73.org/aimodels/v1",
            "api_key": "",
            "selected_model": "selected-model",
        },
    )

    client = FakeClient()
    repairer = FlowAutoRepairer(client=client)
    result = repairer.repair_flow_json(
        "{}", error_message="load failed", rounds_per_model=1)

    assert result is not None
    assert result.model == "model-b"
    assert client.calls == ["selected-model", "model-a", "model-b"]
