# MCP Flow Server - Architecture & Implementation Plan

## Executive Summary

This document outlines the design and implementation plan for a **Model Context Protocol (MCP) server** that provides headless, programmatic access to the Flow Studio's multi-LLM workflow capabilities. This server enables AI agents (Claude Desktop, Cline, Aider, etc.) and CLI tools to leverage "best-of-N" consensus workflows without requiring a GUI.

### What is This?

An MCP server that allows AI coding assistants to:

1. **Send complex problems** to multiple LLMs simultaneously
2. **Aggregate and synthesize** responses into a superior "best-of-N" solution
3. **Define workflows** using simple text-based DSL (Domain Specific Language)
4. **Process large codebases** via context files (repomix, aicodeprep-gui output)

### Why Build This?

**Problem**: Single LLM solutions often miss edge cases, have blind spots, or make suboptimal choices. When facing complex problems (architecture decisions, refactoring, debugging race conditions), you want multiple perspectives.

**Solution**: An MCP server that orchestrates multi-LLM workflows:

- Claude Desktop encounters a hard bug → calls MCP server → server queries GPT-4, Claude, Gemini, Llama simultaneously → synthesizes best solution → returns to Claude
- Agentic tools can leverage collective intelligence without manual orchestration
- Reproducible workflows defined in simple text files

### Use Cases

1. **Complex Debugging**: "I have a race condition but can't find it" → 5 models analyze, one spots it
2. **Architecture Decisions**: "Should I use microservices or monolith?" → Multiple perspectives, synthesized recommendation
3. **Code Review**: Multiple models review PR → consolidated feedback with pros/cons
4. **Refactoring Strategies**: Different models propose approaches → best elements combined
5. **Security Audits**: Parallel analysis by specialized models → comprehensive findings

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (AI Agent)                     │
│                                                              │
│  Examples: Claude Desktop, Cline, Aider, Custom Scripts     │
└───────────────────────┬──────────────────────────────────────┘
                        │ MCP Protocol (JSON-RPC)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    MCP Flow Server                           │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Tools     │  │   Resources  │  │   Prompts    │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Flow Execution Engine                     │      │
│  │  - Parse flow definitions (DSL)                   │      │
│  │  - Parallel LLM orchestration                     │      │
│  │  - Result aggregation & synthesis                 │      │
│  └──────────────────────────────────────────────────┘      │
└───────────────────────┬──────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │OpenRouter│   │ OpenAI  │   │ Gemini  │
   │  (5 LLMs)│   │         │   │         │
   └─────────┘    └─────────┘    └─────────┘
```

---

## Core Components

### 1. MCP Server Implementation

**Technology Stack**:

- Python 3.11+ (matches existing codebase)
- `mcp` library (Anthropic's official MCP SDK)
- `litellm` (existing dependency, proven LLM abstraction)
- `asyncio` for parallel execution
- `pydantic` for validation

**Server Structure**:

```
aicodeprep_mcp_server/
├── __init__.py
├── server.py              # Main MCP server entry point
├── flow/
│   ├── __init__.py
│   ├── engine.py          # Headless flow execution (adapted from GUI)
│   ├── parser.py          # DSL → flow graph parser
│   ├── nodes.py           # Node implementations (LLM, aggregator, etc.)
│   └── executor.py        # Async parallel execution
├── dsl/
│   ├── __init__.py
│   ├── grammar.py         # Flow DSL grammar definition
│   └── examples/          # Example flow definitions
│       ├── best_of_5.flow
│       ├── debate.flow
│       └── review.flow
├── tools/
│   ├── __init__.py
│   ├── execute_flow.py    # MCP tool: execute a flow
│   ├── list_flows.py      # MCP tool: list available flows
│   └── validate_flow.py   # MCP tool: validate DSL syntax
├── resources/
│   ├── __init__.py
│   └── flow_definitions.py # MCP resource: flow templates
└── config/
    ├── __init__.py
    └── providers.py       # API key management
```

### 2. Flow Definition DSL (Domain Specific Language)

**Design Goals**:

- **Simple**: Easy for humans to write and understand
- **AI-Friendly**: LLMs can generate valid flows from natural language
- **Expressive**: Supports common patterns without complexity
- **Readable**: Self-documenting structure

**DSL Format** (YAML-inspired):

```yaml
# best_of_5.flow
name: "Best of 5 OpenRouter"
description: "Send context to 5 models, synthesize best answer"

nodes:
  - id: context_input
    type: input
    source: stdin # or file, or parameter

  - id: llm_1
    type: llm
    provider: openrouter
    model: random_free
    inputs:
      - context_input.text

  - id: llm_2
    type: llm
    provider: openrouter
    model: random_free
    inputs:
      - context_input.text

  - id: llm_3
    type: llm
    provider: openrouter
    model: random_free
    inputs:
      - context_input.text

  - id: llm_4
    type: llm
    provider: openrouter
    model: random_free
    inputs:
      - context_input.text

  - id: llm_5
    type: llm
    provider: openrouter
    model: random_free
    inputs:
      - context_input.text

  - id: synthesizer
    type: best_of_n
    provider: openrouter
    model: random_free
    prompt: |
      You are analyzing multiple AI responses to the same problem.

      Original Context:
      {context_input.text}

      Candidate Responses:
      1. {llm_1.response}
      2. {llm_2.response}
      3. {llm_3.response}
      4. {llm_4.response}
      5. {llm_5.response}

      Task: Analyze each response, identify strengths/weaknesses, 
      and synthesize the best possible solution combining insights from all.
    inputs:
      - context_input.text
      - llm_1.response
      - llm_2.response
      - llm_3.response
      - llm_4.response
      - llm_5.response

  - id: output
    type: output
    destination: stdout
    inputs:
      - synthesizer.result

execution:
  parallel: true # Execute independent nodes concurrently
  timeout: 300 # 5 minutes max
```

**Alternative: Compact DSL** (for simple flows):

```
# Compact syntax for common patterns
flow best_of_5:
  input -> [llm:openrouter:random_free x5] -> synthesize -> output
```

**Another Example - Debate Flow**:

```yaml
# debate.flow
name: "Adversarial Debate"
description: "Two models debate, third judges best argument"

nodes:
  - id: context_input
    type: input
    source: parameter

  - id: advocate
    type: llm
    provider: openai
    model: gpt-4
    system_prompt: "You are advocating FOR the proposed solution. Be persuasive."
    inputs: [context_input.text]

  - id: critic
    type: llm
    provider: anthropic
    model: claude-3-opus
    system_prompt: "You are critiquing the proposed solution. Find flaws."
    inputs: [context_input.text]

  - id: judge
    type: llm
    provider: openrouter
    model: google/gemini-pro
    prompt: |
      Advocate's Position:
      {advocate.response}

      Critic's Concerns:
      {critic.response}

      Provide a balanced judgment and recommendations.
    inputs:
      - context_input.text
      - advocate.response
      - critic.response

  - id: output
    type: output
    destination: stdout
    inputs: [judge.result]
```

### 3. MCP Tools (Server Capabilities)

#### Tool 1: `execute_flow`

**Purpose**: Execute a flow definition with provided context

**Input Schema**:

```json
{
  "flow_definition": "string (YAML/DSL or path to .flow file)",
  "context": "string (code/problem to analyze)",
  "parameters": {
    "timeout": 300,
    "stream_progress": true
  }
}
```

**Output**:

```json
{
  "result": "string (synthesized output)",
  "execution_time": 45.2,
  "nodes_executed": 7,
  "metadata": {
    "models_used": ["gpt-4", "claude-opus", "gemini-pro"],
    "token_usage": {
      "total": 15000,
      "by_model": {...}
    }
  }
}
```

#### Tool 2: `list_flows`

**Purpose**: List available flow templates

**Output**:

```json
{
  "flows": [
    {
      "name": "best_of_5",
      "description": "5 models, synthesize best",
      "path": "~/.aicodeprep/flows/best_of_5.flow"
    },
    {
      "name": "debate",
      "description": "Adversarial debate with judge",
      "path": "~/.aicodeprep/flows/debate.flow"
    }
  ]
}
```

#### Tool 3: `validate_flow`

**Purpose**: Check if flow DSL is valid before execution

**Input**: Flow definition (string)
**Output**: Validation errors or success

#### Tool 4: `generate_flow`

**Purpose**: AI-assisted flow generation from natural language

**Input**:

```json
{
  "description": "I want to send my code to 3 different models and pick the best refactoring suggestion"
}
```

**Output**:

```yaml
# Auto-generated flow based on description
name: "Code Refactoring Consensus"
nodes:
  - id: code_input
    type: input
  ...
```

### 4. MCP Resources

**Resource 1**: `flow://templates`

- Provides access to built-in flow templates
- Can be read/listed by MCP clients

**Resource 2**: `flow://results/{execution_id}`

- Access historical execution results
- Useful for comparing runs

### 5. MCP Prompts

**Prompt 1**: `analyze_with_consensus`

```
Use the flow server to analyze this problem with 5 different models and synthesize the best solution.

Context: {code}
Question: {question}

Flow: best_of_5
```

---

## Implementation Phases

### Phase 1: Core MCP Server (Week 1-2)

**Deliverables**:

1. Basic MCP server setup using `mcp` library
2. Simple flow parser (YAML-based)
3. Sequential execution (no parallelism yet)
4. `execute_flow` tool working with hardcoded "best_of_5" flow
5. Integration with existing `litellm_client.py`

**Files to Create**:

- `aicodeprep_mcp_server/server.py`
- `aicodeprep_mcp_server/flow/parser.py`
- `aicodeprep_mcp_server/flow/engine.py` (adapted from GUI engine)
- `aicodeprep_mcp_server/tools/execute_flow.py`

**Success Criteria**:

- Can call `execute_flow` from Claude Desktop
- Returns synthesized result from 5 OpenRouter models
- Basic error handling

### Phase 2: DSL & Parallel Execution (Week 3-4)

**Deliverables**:

1. Complete DSL parser with validation
2. Parallel node execution (asyncio + ThreadPoolExecutor)
3. Multiple flow templates (best_of_5, debate, review)
4. `list_flows` and `validate_flow` tools
5. Comprehensive error messages

**Files to Create**:

- `aicodeprep_mcp_server/dsl/grammar.py`
- `aicodeprep_mcp_server/dsl/examples/*.flow`
- `aicodeprep_mcp_server/flow/executor.py`

**Success Criteria**:

- 5 LLM nodes execute in parallel (~10 seconds vs 50)
- Can load custom flow files from disk
- Validation catches syntax errors before execution

### Phase 3: Advanced Features (Week 5-6)

**Deliverables**:

1. Streaming progress updates
2. `generate_flow` tool (AI-assisted flow creation)
3. Resource providers for templates
4. Caching layer for repeated queries
5. Token usage tracking & cost estimation

**Files to Create**:

- `aicodeprep_mcp_server/tools/generate_flow.py`
- `aicodeprep_mcp_server/resources/flow_definitions.py`
- `aicodeprep_mcp_server/cache/results.py`

**Success Criteria**:

- Can describe a workflow in plain English → generates valid DSL
- Streaming shows real-time progress in Claude Desktop
- Repeated queries use cached results (cost savings)

### Phase 4: Production Hardening (Week 7-8)

**Deliverables**:

1. Comprehensive test suite
2. Docker container for deployment
3. Documentation & examples
4. Rate limiting & quota management
5. Monitoring & logging

**Files to Create**:

- `tests/` directory with pytest tests
- `Dockerfile` and `docker-compose.yml`
- `docs/` with user guides and API reference
- `examples/` with integration examples

**Success Criteria**:

- 90%+ test coverage
- Can deploy via Docker with one command
- Production-ready error handling

---

## Technical Specifications

### Node Types

1. **Input Node**

   - Sources: `stdin`, `file`, `parameter`, `clipboard`
   - Validates input format

2. **LLM Node**

   - Providers: openrouter, openai, anthropic, google, custom
   - Model selection: specific, random, random_free
   - System prompts, temperature, max_tokens

3. **Aggregator Node** (Best-of-N)

   - Receives N inputs
   - Uses synthesis prompt template
   - Configurable voting/ranking strategies

4. **Transform Node**

   - Apply regex, format conversion, filtering
   - Example: Extract code blocks from responses

5. **Conditional Node**

   - Branch based on output characteristics
   - Example: If confidence < 0.8, query additional model

6. **Output Node**
   - Destinations: `stdout`, `file`, `clipboard`, `return`

### Execution Engine

**Key Features**:

- **Topological Sorting**: Dependency graph analysis (from GUI engine)
- **Parallel Execution**: asyncio for I/O-bound operations
- **Error Handling**: Graceful degradation (continue with partial results)
- **Timeouts**: Per-node and global timeouts
- **Cancellation**: Support for early termination

**Execution Algorithm**:

```python
async def execute_flow(flow_def, context):
    # 1. Parse DSL → internal graph
    graph = parse_flow(flow_def)

    # 2. Topological sort
    levels = topological_group(graph)

    # 3. Execute level by level
    results = {}
    for level in levels:
        # Gather inputs for each node in level
        node_inputs = prepare_inputs(level, results, context)

        # Execute nodes in parallel
        level_results = await asyncio.gather(*[
            execute_node(node, inputs)
            for node, inputs in node_inputs
        ])

        # Store results
        results.update(level_results)

    # 4. Return final output
    return extract_output(results, graph.output_node)
```

### LLM Integration

**Reuse Existing Code**:

- Leverage `aicodeprep_gui/pro/llm/litellm_client.py`
- Same provider configuration (api-keys.toml)
- Compatible with existing OpenRouter, OpenAI, Gemini setup

**Enhancements**:

- Async versions of all LLM calls
- Streaming support for real-time progress
- Retry logic with exponential backoff

### Configuration

**Config File** (`~/.aicodeprep/mcp-server.toml`):

```toml
[server]
host = "localhost"
port = 5173  # Or use stdio for Claude Desktop

[execution]
default_timeout = 300
max_parallel_nodes = 10
cache_results = true
cache_ttl = 3600  # 1 hour

[flows]
custom_flows_dir = "~/.aicodeprep/flows"
builtin_flows_dir = "/usr/local/share/aicodeprep/flows"

[limits]
max_tokens_per_request = 100000
max_execution_time = 600
rate_limit_requests_per_minute = 60

[logging]
level = "INFO"
file = "~/.aicodeprep/mcp-server.log"
```

### Security Considerations

1. **API Key Protection**:

   - Never log or expose API keys
   - Read from secure config files only
   - Support environment variables

2. **Input Validation**:

   - Validate all DSL inputs before execution
   - Sanitize context to prevent injection
   - Limit input size to prevent DOS

3. **Resource Limits**:

   - Cap parallel executions
   - Set memory limits
   - Implement request quotas

4. **Sandboxing**:
   - No arbitrary code execution
   - Whitelist of allowed node types
   - Validate file paths (no directory traversal)

---

## MCP Protocol Integration

### Server Declaration

```json
{
  "name": "aicodeprep-flow-server",
  "version": "1.0.0",
  "description": "Multi-LLM consensus workflow execution",
  "tools": [
    {
      "name": "execute_flow",
      "description": "Execute a flow with context and return synthesized result",
      "inputSchema": {...}
    },
    {
      "name": "list_flows",
      "description": "List available flow templates"
    },
    {
      "name": "validate_flow",
      "description": "Validate flow DSL syntax"
    },
    {
      "name": "generate_flow",
      "description": "Generate flow from natural language description"
    }
  ],
  "resources": [
    {
      "uri": "flow://templates",
      "name": "Flow Templates",
      "description": "Built-in flow definitions"
    }
  ]
}
```

### Claude Desktop Integration

**Config** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aicodeprep-flow": {
      "command": "python",
      "args": ["-m", "aicodeprep_mcp_server"],
      "env": {
        "AICODEPREP_CONFIG": "~/.aicodeprep/mcp-server.toml"
      }
    }
  }
}
```

**Usage in Claude Desktop**:

```
User: I have a complex race condition bug. Can you help?

Claude: Let me use the flow server to get multiple perspectives.

[Calls execute_flow with context from current files]

Claude: I consulted 5 different models. Here's the consensus...
```

---

## Example Workflows

### Example 1: Code Review

```yaml
# code_review.flow
name: "Multi-Model Code Review"
description: "3 models review code, 4th synthesizes feedback"

nodes:
  - id: code_input
    type: input
    source: parameter

  - id: security_reviewer
    type: llm
    provider: openai
    model: gpt-4
    system_prompt: "You are a security expert. Review for vulnerabilities."
    inputs: [code_input.text]

  - id: performance_reviewer
    type: llm
    provider: anthropic
    model: claude-3-opus
    system_prompt: "You are a performance expert. Find bottlenecks."
    inputs: [code_input.text]

  - id: maintainability_reviewer
    type: llm
    provider: google
    model: gemini-pro
    system_prompt: "You are a code quality expert. Review maintainability."
    inputs: [code_input.text]

  - id: synthesizer
    type: best_of_n
    provider: openrouter
    model: random_free
    prompt: |
      Code Review Synthesis

      Security Analysis:
      {security_reviewer.response}

      Performance Analysis:
      {performance_reviewer.response}

      Maintainability Analysis:
      {maintainability_reviewer.response}

      Provide a comprehensive code review consolidating all perspectives.
      Prioritize issues by severity and provide actionable recommendations.
    inputs:
      - code_input.text
      - security_reviewer.response
      - performance_reviewer.response
      - maintainability_reviewer.response

  - id: output
    type: output
    destination: stdout
    inputs: [synthesizer.result]

execution:
  parallel: true
  timeout: 180
```

### Example 2: Debugging Assistant

```yaml
# debug_helper.flow
name: "Multi-Model Debugging"
description: "Parallel debugging approaches, synthesize best solution"

nodes:
  - id: bug_context
    type: input
    source: parameter

  - id: debugger_1
    type: llm
    provider: openrouter
    model: anthropic/claude-3-sonnet
    system_prompt: "Debug systematically. Use print statements and logging."
    inputs: [bug_context.text]

  - id: debugger_2
    type: llm
    provider: openrouter
    model: openai/gpt-4
    system_prompt: "Debug using type checking and static analysis."
    inputs: [bug_context.text]

  - id: debugger_3
    type: llm
    provider: openrouter
    model: google/gemini-pro
    system_prompt: "Debug by analyzing data flow and state mutations."
    inputs: [bug_context.text]

  - id: debugger_4
    type: llm
    provider: openrouter
    model: meta-llama/llama-3-70b
    system_prompt: "Debug by looking for common anti-patterns."
    inputs: [bug_context.text]

  - id: solution_synthesizer
    type: best_of_n
    provider: openrouter
    model: anthropic/claude-3-opus
    prompt: |
      Multiple debugging approaches were attempted:

      Approach 1 (Logging):
      {debugger_1.response}

      Approach 2 (Type Analysis):
      {debugger_2.response}

      Approach 3 (Data Flow):
      {debugger_3.response}

      Approach 4 (Anti-patterns):
      {debugger_4.response}

      Synthesize the best debugging solution. Provide:
      1. Root cause analysis
      2. Step-by-step fix
      3. Prevention strategies
    inputs:
      - bug_context.text
      - debugger_1.response
      - debugger_2.response
      - debugger_3.response
      - debugger_4.response

  - id: output
    type: output
    destination: stdout
    inputs: [solution_synthesizer.result]

execution:
  parallel: true
  timeout: 300
```

---

## CLI Interface (Bonus)

While primarily an MCP server, provide a CLI for testing:

```bash
# Execute a flow
aicodeprep-flow run best_of_5.flow --context "$(cat problem.txt)"

# List flows
aicodeprep-flow list

# Validate flow
aicodeprep-flow validate my_custom.flow

# Generate flow from description
aicodeprep-flow generate "I want 3 models to debate architecture"

# Stream execution progress
aicodeprep-flow run debate.flow --stream --context "microservices vs monolith"
```

---

## Testing Strategy

### Unit Tests

- DSL parser with valid/invalid inputs
- Node execution (mocked LLM calls)
- Topological sorting edge cases
- Error handling scenarios

### Integration Tests

- End-to-end flow execution
- Real LLM API calls (with test quota)
- Multi-provider workflows
- Timeout and cancellation

### Performance Tests

- Parallel execution speedup (measure vs sequential)
- Large context handling (100K+ tokens)
- Memory usage under load

### MCP Protocol Tests

- Tool invocation from Claude Desktop
- Resource access
- Error response handling

---

## Documentation Plan

### User Documentation

1. **Quick Start Guide**

   - Installing the MCP server
   - Configuring Claude Desktop
   - First flow execution

2. **DSL Reference**

   - Complete syntax documentation
   - All node types with examples
   - Best practices

3. **Flow Templates**

   - Gallery of pre-built flows
   - Use case descriptions
   - Customization guide

4. **Integration Guides**
   - Claude Desktop
   - Cline
   - Aider
   - Custom scripts

### Developer Documentation

1. **Architecture Overview**

   - Component diagram
   - Data flow
   - Extension points

2. **API Reference**

   - MCP tools specification
   - Internal APIs
   - Node implementation guide

3. **Contributing Guide**
   - Development setup
   - Testing procedures
   - Pull request process

---

## Deployment Options

### Option 1: Local Installation (Recommended)

```bash
pip install aicodeprep-mcp-server
aicodeprep-mcp-server --config ~/.aicodeprep/mcp-server.toml
```

### Option 2: Docker Container

```bash
docker run -v ~/.aicodeprep:/config aicodeprep/mcp-server
```

### Option 3: System Service (Linux/Mac)

```bash
# systemd service file
sudo systemctl enable aicodeprep-mcp-server
sudo systemctl start aicodeprep-mcp-server
```

---

## Cost Estimation

### Development Effort

- **Phase 1**: ~40 hours (core server)
- **Phase 2**: ~40 hours (DSL + parallelism)
- **Phase 3**: ~30 hours (advanced features)
- **Phase 4**: ~30 hours (hardening)
- **Total**: ~140 hours (~4 weeks full-time)

### API Cost Savings

**Without Flow Server**:

- Developer manually queries 5 models sequentially
- Copy/paste overhead
- Inconsistent results
- Cost: Time + duplicate queries

**With Flow Server**:

- One command executes optimized workflow
- Parallel execution (5x faster)
- Cached results (cost savings)
- Consistent methodology
- Cost: Automated efficiency

**Example**:

- 100 hard problems/month
- 5 models per problem
- ~$0.10 per query
- Without: 500 queries = $50 + many hours
- With: 500 queries = $50, but 5x faster + consistent quality

**ROI**: Massive time savings + better quality decisions

---

## Future Enhancements

### Phase 5+ (Post-MVP)

1. **Visual Flow Designer** (Web UI)

   - Drag-and-drop flow creation
   - Real-time execution visualization
   - Shareable flow URLs

2. **Flow Marketplace**

   - Community-contributed flows
   - Ratings and reviews
   - One-click import

3. **Advanced Aggregation Strategies**

   - Voting mechanisms
   - Confidence scoring
   - Ensemble methods (ML-based synthesis)

4. **Specialized Nodes**

   - Code execution (sandbox)
   - Database queries
   - API calls
   - File I/O

5. **Multi-Stage Workflows**

   - Iterative refinement
   - Human-in-the-loop approval
   - Conditional branching

6. **Analytics Dashboard**
   - Token usage by flow
   - Cost tracking
   - Success rate metrics
   - Model performance comparison

---

## Success Metrics

### Technical Metrics

- [ ] Execution time: 5-10 seconds for 5-model consensus
- [ ] 95th percentile latency < 30 seconds
- [ ] 99% uptime
- [ ] < 1% error rate

### User Experience Metrics

- [ ] Claude Desktop integration works out-of-box
- [ ] < 5 minutes to first successful flow execution
- [ ] DSL is intuitive (user testing)
- [ ] Positive feedback from alpha users

### Business Metrics

- [ ] 100+ flows executed per day (across all users)
- [ ] 10+ custom flow contributions from community
- [ ] Positive cost/benefit ratio for users

---

## Conclusion

The MCP Flow Server transforms the GUI Flow Studio's capabilities into a programmable, agent-accessible service. By providing:

1. **Simple DSL** for workflow definition
2. **Parallel execution** for speed
3. **MCP integration** for AI agents
4. **Extensible architecture** for future growth

We enable AI coding assistants to leverage collective intelligence for complex problems, dramatically improving solution quality while reducing developer time investment.

**Next Steps**:

1. Validate architecture with stakeholders
2. Set up development environment
3. Begin Phase 1 implementation
4. Alpha testing with Claude Desktop users

---

## Appendix A: DSL Grammar Specification

```yaml
# Formal grammar (simplified BNF-style)

flow_definition:
  name: string
  description: string (optional)
  nodes: [node_definition+]
  execution: execution_config (optional)

node_definition:
  id: identifier
  type: node_type
  [type-specific fields]
  inputs: [node_reference+] (optional)

node_type:
  input | llm | best_of_n | transform | conditional | output

llm_node:
  provider: string
  model: string
  system_prompt: string (optional)
  temperature: float (optional)
  max_tokens: int (optional)

best_of_n_node:
  provider: string
  model: string
  prompt: string (template with placeholders)

execution_config:
  parallel: boolean (default: true)
  timeout: int (seconds)
  cache: boolean (default: false)

node_reference:
  <node_id>.<output_field>
```

---

## Appendix B: MCP Tool Schemas

### execute_flow Tool

```json
{
  "name": "execute_flow",
  "description": "Execute a multi-LLM consensus workflow",
  "inputSchema": {
    "type": "object",
    "properties": {
      "flow": {
        "type": "string",
        "description": "Flow name or inline YAML definition"
      },
      "context": {
        "type": "string",
        "description": "Problem context (code, question, etc.)"
      },
      "parameters": {
        "type": "object",
        "properties": {
          "timeout": { "type": "integer", "default": 300 },
          "stream": { "type": "boolean", "default": false },
          "cache": { "type": "boolean", "default": true }
        }
      }
    },
    "required": ["flow", "context"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "result": { "type": "string" },
      "metadata": {
        "type": "object",
        "properties": {
          "execution_time": { "type": "number" },
          "models_used": { "type": "array" },
          "token_usage": { "type": "object" }
        }
      }
    }
  }
}
```

---

_Document Version: 1.0_  
_Created: January 27, 2025_  
_Author: AI Assistant_  
_Status: Draft - Ready for Review_
