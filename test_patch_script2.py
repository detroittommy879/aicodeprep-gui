import re

with open("G:/aicodeprep-2026/aicodeprep-gui/aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py", "r", encoding="utf-8") as f:
    text = f.read()

import_patch = '''
from aicodeprep_gui.pro.flow.nodes.llm_nodes import _get_compat_provider_label, _cached_model_options
try:
    from NodeGraphQt.constants import NodePropWidgetEnum
except ImportError:
    class NodePropWidgetEnum:
        QLINE_EDIT = 3
        QCOMBO_BOX = 5
'''

text = re.sub(
    r'try:\s*from NodeGraphQt\.constants import NodePropWidgetEnum\nexcept ImportError:\s*class NodePropWidgetEnum:\s*QLINE_EDIT = 3\s*QCOMBO_BOX = 5',
    import_patch.strip(),
    text,
    count=1
)

text = re.sub(
    r'self\.create_property\("provider", "openrouter", widget_type=NodePropWidgetEnum\.QCOMBO_BOX\.value,\n\s*items=\["openrouter", "openai", "gemini", "compatible"\]\)',
    'self.create_property("provider", "openrouter", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value,\n                             items=["openrouter", "openai", "gemini", _get_compat_provider_label()])',
    text
)

text = re.sub(
    r'self\.create_property\(\n\s*"model", "", widget_type=NodePropWidgetEnum\.QLINE_EDIT\.value\)',
    'self.create_property(\n            "model", "", widget_type=NodePropWidgetEnum.QCOMBO_BOX.value, items=list(_cached_model_options))',
    text
)

prov_patch_2 = '''
        provider = (self.get_property("provider")
                    or "openrouter").strip().lower()
        if provider.startswith("compatible"):
            provider = "compatible"
'''

text = re.sub(
    r'provider = \(self\.get_property\("provider"\)\s*or "openrouter"\)\.strip\(\)\.lower\(\)',
    prov_patch_2.strip(),
    text
)

with open("G:/aicodeprep-2026/aicodeprep-gui/aicodeprep_gui/pro/flow/nodes/aggregate_nodes.py", "w", encoding="utf-8") as f:
    f.write(text)

print("done patching aggregate_nodes")
