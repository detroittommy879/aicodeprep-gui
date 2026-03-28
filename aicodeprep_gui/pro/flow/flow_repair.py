from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import re
from typing import Any, Optional

from aicodeprep_gui.pro.ai_assist.ai_client import AIClient
from aicodeprep_gui.pro.ai_assist.endpoint_config import get_active_endpoint

from .serializer import _normalize_node_data, validate_flow_structure

logger = logging.getLogger(__name__)

FLOW_JSON_PATTERN = re.compile(
    r"<flow\.json>(.*?)</(?:flow\.json)?>|<flow\.json>(.*?)</>",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class FlowRepairResult:
    flow_json: str
    model: str
    attempts: int


def extract_flow_json_tag(text: str) -> Optional[str]:
    if not text:
        return None

    match = FLOW_JSON_PATTERN.search(text)
    if match:
        for group in match.groups():
            if group:
                return group.strip()

    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    return None


def _flow_repair_instructions() -> str:
    return (
        "You repair Flow Studio JSON session files for NodeGraphQt.\n"
        "Return ONLY a corrected JSON object wrapped in <flow.json>...</flow.json>.\n"
        "Rules:\n"
        "- Top level keys: graph, nodes, connections.\n"
        "- nodes must be an object keyed by node id strings.\n"
        "- Each node must include type_, custom, subgraph_session.\n"
        "- custom and subgraph_session must be JSON objects, never strings.\n"
        "- Every connection must be {\"out\": [node_id, port_name], \"in\": [node_id, port_name]}.\n"
        "- Connections must reference existing nodes.\n"
        "- Valid Flow Studio node types include: aicp.flow.ContextOutputNode, aicp.flow.OpenAICompatibleNode, aicp.flow.OpenRouterNode, aicp.flow.BestOfNNode, aicp.flow.ClipboardNode, aicp.flow.FileWriteNode, aicp.flow.OutputDisplayNode.\n"
        "- BestOfNNode uses input ports context and candidate1..candidate10 and output port text.\n"
        "- LLM nodes typically use input ports text/system and output port text.\n"
        "- Prefer endpoint-compatible graphs by using aicp.flow.OpenAICompatibleNode with provider=compatible when repairing built-in templates.\n"
        "- Do not include markdown fences or commentary outside the XML tag.\n"
    )


class FlowAutoRepairer:
    def __init__(self, client: Optional[AIClient] = None):
        self.client = client or AIClient()

    def _get_candidate_models(self) -> tuple[dict[str, Any], list[str]]:
        endpoint = get_active_endpoint() or {}
        base_url = (endpoint.get("url") or "").strip()
        api_key = (endpoint.get("api_key") or "").strip()
        selected_model = (endpoint.get("selected_model") or "").strip()

        models: list[str] = []
        if selected_model:
            models.append(selected_model)

        if base_url:
            for model in self.client.list_models(base_url, api_key=api_key, timeout=10, retries=1):
                model_id = (model.get("id") or model.get("name") or "").strip()
                if model_id and model_id not in models:
                    models.append(model_id)

        return endpoint, models

    def repair_flow_json(
        self,
        flow_text: str,
        error_message: str = "",
        max_models: int = 5,
        rounds_per_model: int = 2,
    ) -> Optional[FlowRepairResult]:
        endpoint, candidate_models = self._get_candidate_models()
        if not endpoint or not endpoint.get("url") or not candidate_models:
            logger.warning(
                "[Flow Repair] No active endpoint or models available for repair")
            return None

        system_prompt = _flow_repair_instructions()
        endpoint_url = (endpoint.get("url") or "").strip()
        user_prompt = (
            f"Active endpoint: {endpoint_url}\n"
            f"Current load error: {error_message or 'unknown load error'}\n\n"
            "Repair this Flow Studio session JSON so it can be loaded successfully.\n"
            "If the graph is a default/built-in flow, prefer a stable endpoint-compatible graph using the active endpoint.\n"
            "Original JSON:\n"
            f"{flow_text}\n"
        )

        attempts = 0
        for model in candidate_models[:max_models]:
            history = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            for round_index in range(rounds_per_model):
                attempts += 1
                try:
                    response = self.client.chat(
                        model=model,
                        messages=history,
                        base_url=endpoint_url,
                        api_key=(endpoint.get("api_key") or "").strip(),
                        timeout=90,
                    )
                except Exception as exc:
                    logger.warning(
                        "[Flow Repair] Model %s failed on request %s: %s",
                        model,
                        attempts,
                        exc,
                    )
                    break

                tagged_json = extract_flow_json_tag(response)
                if not tagged_json:
                    history.append({"role": "assistant", "content": response})
                    history.append(
                        {
                            "role": "user",
                            "content": "Your reply did not contain a <flow.json>...</flow.json> block. Reply again with only that tag and valid JSON.",
                        }
                    )
                    continue

                try:
                    data = json.loads(tagged_json)
                except json.JSONDecodeError as exc:
                    history.append({"role": "assistant", "content": response})
                    history.append(
                        {
                            "role": "user",
                            "content": f"The JSON inside <flow.json> was invalid: {exc}. Return corrected JSON only.",
                        }
                    )
                    continue

                normalized = _normalize_node_data(data)
                validation_errors = validate_flow_structure(normalized)
                if validation_errors:
                    history.append({"role": "assistant", "content": response})
                    history.append(
                        {
                            "role": "user",
                            "content": "The repaired JSON is still invalid:\n- " + "\n- ".join(validation_errors) + "\nReturn a corrected flow wrapped in <flow.json>.",
                        }
                    )
                    continue

                return FlowRepairResult(
                    flow_json=json.dumps(normalized, indent=2),
                    model=model,
                    attempts=attempts,
                )

        logger.warning(
            "[Flow Repair] Exhausted repair attempts without a valid flow")
        return None
