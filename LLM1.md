Yes — absolutely. You can design a tiny domain-specific language (DSL) that only describes the logical flow (nodes, node types, node properties, and connections) and omits all UI metadata (colors, coords, size, etc.). Below I give a compact DSL design, a small grammar, examples (including compact versions of the two flows you posted), and a short Python approach to convert the DSL into your existing JSON format.

Design goals
- Human-writable and readable (few characters per node)
- Minimal required info: node id/name, type, essential properties
- Simple explicit connections (source:port -> target:port)
- Reasonable defaults to avoid verbosity
- Extensible (add properties, templates, includes)

Compact DSL (proposal)
Syntax overview (line-based):
- Comments begin with #
- Define nodes: node <id> : <Type> [ key=value, key2="value with spaces", ... ]
- Short type aliases allowed (LLM -> aicp.flow.OpenRouterNode, etc.)
- Connections: connect <source_id>[:port] -> <target_id>[:port]
- Output shortcuts: to file/clipboard/display
- Blocks for flow metadata (optional)

Example grammar (informal)
- NODE: "node" ID ":" TYPE [ "[" PROP_LIST "]" ]
- PROP_LIST: PROP ("," PROP)*
- PROP: KEY "=" VALUE
- CONNECT: "connect" SRC [":" PORT] "->" DST [":" PORT]

Defaults
- Default port name: text
- Default node properties: minimal set (e.g., for LLM nodes: model, provider, output_file, temperature)
- IDs can be short names (no need for hex addresses); converter will create full internal IDs

Example DSL (Best-of-5 flow — compact)
# best_of_5.dsl
# Define the context source
node ctx : ContextOutput [ path=fullcode.txt, use_latest_generated=true ]

# LLMs
node LLM1 : OpenRouter [ model=openai/gpt-5-codex, output_file=LLM1.md, temperature=0.7 ]
node LLM2 : OpenRouter [ model=anthropic/claude-sonnet-4.5, output_file=LLM2.md, temperature=0.7 ]
node LLM3 : OpenRouter [ model=z-ai/glm-4.6, output_file=LLM3.md, temperature=0.7 ]
node LLM4 : OpenRouter [ model=qwen/qwen3-next-80b-a3b-thinking, output_file=LLM4.md, temperature=0.7 ]
node LLM5 : OpenRouter [ model=openai/o4-mini, output_file=LLM5.md, temperature=0.7 ]

# Synthesizer
node SYNTH : BestOfN [ model=google/gemini-2.5-pro, extra_prompt="You are an expert coder..." ]

# Outputs
node CLIP : Clipboard []
node FILE : FileWrite [ path=best_of_all1.txt ]
node DISP : OutputDisplay []

# Connections (default port is "text" unless specified)
connect ctx -> LLM1
connect ctx -> LLM2
connect ctx -> LLM3
connect ctx -> LLM4
connect ctx -> LLM5
connect ctx -> SYNTH:context

connect LLM1 -> SYNTH:candidate1
connect LLM2 -> SYNTH:candidate2
connect LLM3 -> SYNTH:candidate3
connect LLM4 -> SYNTH:candidate4
connect LLM5 -> SYNTH:candidate5

connect SYNTH -> CLIP
connect SYNTH -> FILE
connect SYNTH -> DISP

Same flow but Best-of-3 (compact)
# best_of_3.dsl
node ctx : ContextOutput [ path=fullcode.txt, use_latest_generated=true ]
node LLM1 : OpenRouter [ model=openai/gpt-5-codex, output_file=LLM1.md ]
node LLM2 : OpenRouter [ model=qwen/qwen3-next-80b-a3b-thinking, output_file=LLM2.md ]
node LLM3 : OpenRouter [ model=anthropic/claude-sonnet-4.5, output_file=LLM3.md ]
node SYNTH : BestOfN [ model=google/gemini-2.5-pro, extra_prompt="..." ]
node CLIP : Clipboard []
node FILE : FileWrite [ path=best_of_3.txt ]
node DISP : OutputDisplay []

connect ctx -> LLM1
connect ctx -> LLM2
connect ctx -> LLM3
connect ctx -> SYNTH:context

connect LLM1 -> SYNTH:candidate1
connect LLM2 -> SYNTH:candidate2
connect LLM3 -> SYNTH:candidate3

connect SYNTH -> CLIP
connect SYNTH -> FILE
connect SYNTH -> DISP

Mapping to your JSON format
- Node type mapping: map compact type names to full class names. e.g., ContextOutput -> aicp.flow.ContextOutputNode, OpenRouter -> aicp.flow.OpenRouterNode, BestOfN -> aicp.flow.BestOfNNode, FileWrite -> aicp.flow.FileWriteNode.
- Create unique internal IDs (e.g., 0x... strings) for each DSL node.
- Fill minimal UI fields with defaults (color, visible = true, etc.) or omit if your loader tolerates missing fields. Your posted JSON includes many UI keys; the converter can insert sane defaults.
- Build "connections" list with "out": [source_internal_id, port] and "in": [target_internal_id, port].

Minimal Python converter example
This is a compact, illustrative parser — for production use, you’d want a proper parser (pyparsing, lark, or a small hand-rolled parser with error messages).


Example (conceptual, not full production code):


import json
import re
from uuid import uuid4

TYPE_MAP = {
    "ContextOutput": "aicp.flow.ContextOutputNode",
    "OpenRouter": "aicp.flow.OpenRouterNode",
    "BestOfN": "aicp.flow.BestOfNNode",
    "Clipboard": "aicp.flow.ClipboardNode",
    "FileWrite": "aicp.flow.FileWriteNode",
    "OutputDisplay": "aicp.flow.OutputDisplayNode",
}

def make_id(name):
    return "n_" + name  # or hex: hex(id...) etc.

def parse_prop_list(s):
    # naive: split on commas, handle quotes
    kvs = {}
    for m in re.finditer(r'(\w+)\s*=\s*(?:"([^"]*)"|([^,\]]+))', s):
        k = m.group(1)
        v = m.group(2) if m.group(2) is not None else m.group(3)
        # try to coerce numbers/bool
        if v in ("true","false"): v = (v=="true")
        else:
            try: v = float(v) if "." in v else int(v)
            except: v = v.strip()
        kvs[k] = v
    return kvs

def compile_dsl(lines):
    nodes = {}
    connections = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"): continue
        if ln.startswith("node"):
            # node ID : Type [ props ]
            m = re.match(r'node\s+(\w+)\s*:\s*(\w+)\s*(?:\[(.*)\])?', ln)
            if not m: raise ValueError("Bad node line: " + ln)
            nid, typ, props = m.group(1), m.group(2), m.group(3)
            node_id = make_id(nid)
            node = {
                "type_": TYPE_MAP.get(typ, typ),
                "name": f"{typ}: {nid}",
                "custom": {"version":"1.0.0"}
            }
            if props:
                node["custom"].update(parse_prop_list(props))
            nodes[nid] = (node_id, node)
        elif ln.startswith("connect"):
            # connect A[:port] -> B[:port]
            m = re.match(r'connect\s+([^\s]+)\s*->\s*([^\s]+)', ln)
            if not m: raise ValueError("Bad connect line: " + ln)
            src, dst = m.group(1), m.group(2)
            def split_sp(s):
                if ":" in s:
                    a,p = s.split(":",1); return a,p
                else:
                    return s,"text"
            sa, sp = split_sp(src); da, dp = split_sp(dst)
            connections.append({"out": [ nodes[sa][0], sp], "in": [ nodes[da][0], dp]})
        else:
            raise ValueError("Unknown line: " + ln)
    # assemble final JSON-like dict
    nodes_out = { nid: node for nid,_node in [(k, v[1]) for k,v in nodes.items()] }  # adapt id keys if needed
    # In this example, we used short keys as names; you can instead use internal hex ids as keys.
    return {"graph": {}, "nodes": {v[0]: v[1] for v in nodes.values()}, "connections": connections}

# Usage:
dsl_text = open("best_of_5.dsl").read().splitlines()
flow = compile_dsl(dsl_text)
print(json.dumps(flow, indent=2))


Notes & extensions
- Use YAML/JSON if you prefer structured format, but the custom DSL is more concise and friendlier for quick edits.
- Add "templates" or "include" directive so you can keep common LLM properties in one place.
- Validation: check for missing node references, required properties per node type (e.g., FileWrite needs path).
- Support variable interpolation: e.g., ${OUTDIR}/best.txt
- Add meta directives (defaults for model provider, temperature, model_mode) so individual node lines can be shorter.
- If you want, support generating UI positions optionally for a "save-back" feature.

Advantages over raw JSON
- Humans can write and read flows quickly.
- Less noise — only what's semantically important.
- Easier version control diffs.
- Can add programmatic constructs like loops, conditional branches, macros.

If you’d like, I can:
- Produce a parser that maps the DSL to the exact JSON keys and default UI fields your app expects.
- Provide a slightly richer DSL variant (YAML-compatible) if you prefer more structure and comments with built-in tooling.
- Generate the two DSL files for your posted flows and show the exact JSON they produce.

Which would you prefer next — a full converter script that emits the exact structure your app uses, or a tiny library/API to load and validate DSL flows?