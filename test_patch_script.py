import re

with open("G:/aicodeprep-2026/aicodeprep-gui/aicodeprep_gui/pro/flow/nodes/llm_nodes.py", "r", encoding="utf-8") as f:
    text = f.read()

get_prov_code = '''
    def get_resolved_provider(self) -> str:
        try:
            from NodeGraphQt import BaseNode as NGBaseNode
            val = (NGBaseNode.get_property(self, "provider") or self.default_provider()).strip().lower()
            if val.startswith("compatible"):
                return "compatible"
            return val
        except Exception:
            return self.default_provider()

    def default_provider(self) -> str:
'''

text = re.sub(
    r'\s+def default_provider\(self\) -> str:',
    get_prov_code,
    text,
    count=1
)

text = re.sub(
    r'provider = \(self\.get_property\("provider"\)\s*or self\.default_provider\(\)\)\.strip\(\)\.lower\(\)',
    'provider = self.get_resolved_provider()',
    text
)
with open("G:/aicodeprep-2026/aicodeprep-gui/aicodeprep_gui/pro/flow/nodes/llm_nodes.py", "w", encoding="utf-8") as f:
    f.write(text)

print("done patching resolved provider")
