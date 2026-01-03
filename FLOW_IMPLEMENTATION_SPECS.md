# Flow Graph Feature Implementation Specifications

## Overview

This document outlines the implementation plan for enabling the flow graph feature in aicodeprep-gui. The goal is to transform the existing visual flow graph into an executable engine that can route context through multiple AI providers and synthesize "best-of-N" results.

## Current State Analysis

### What's Working
- Flow Studio UI with NodeGraphQt is functional
- Visual graph creation/manipulation works
- Basic I/O nodes (ContextOutput, Clipboard, FileWrite, OutputDisplay) exist

### What's Missing
- Execution engine to run the graphs
- LLM provider integration via LiteLLM
- "Best-of-N" synthesis functionality
- Multi-provider routing (OpenRouter, OpenAI, Gemini, etc.)
- Built-in templates for common workflows

## Implementation Strategy

### Phase 1: Core Runtime & LiteLLM Integration
1. **Add LiteLLM dependency** (`pyproject.toml`)
2. **Create unified LiteLLM client wrapper** (`pro/llm/litellm_client.py`)
3. **Implement LLM provider nodes** (`pro/flow/nodes/llm_nodes.py`)
4. **Create Best-of-N synthesis node** (`pro/flow/nodes/aggregate_nodes.py`)
5. **Make I/O nodes executable** (`pro/flow/nodes/io_nodes.py`)
6. **Build execution engine** (`pro/flow/engine.py`)
7. **Wire Run button and register nodes** (`pro/flow/flow_dock.py`)
8. **Add Flow menu items** (`gui/main_window.py`)

### Phase 2: Enhanced Features
- Token window validation
- Advanced error handling
- Provider settings dialog
- DSL/Text-based flow definition
- Model listing and caching
- Async execution for better performance

## Key Components to Implement

### 1. LiteLLM Client Wrapper (`pro/llm/litellm_client.py`)
- Centralized provider configuration
- Model listing for each provider
- Unified chat completion interface
- Random/free model selection for OpenRouter
- Error handling and user feedback

### 2. Provider Nodes (`pro/flow/nodes/llm_nodes.py`)
- Base LLM node with common functionality
- Specific nodes: OpenRouter, OpenAI, Gemini, OpenAI-Compatible
- API key resolution (node properties → QSettings fallback)
- Model selection with random/random_free modes
- Provider-specific headers and base URLs

### 3. Best-of-N Synthesis Node (`pro/flow/nodes/aggregate_nodes.py`)
- Accepts context + multiple candidate inputs
- Configurable synthesis prompt
- Uses specified provider for synthesis
- Outputs improved "best-of" result

### 4. Execution Engine (`pro/flow/engine.py`)
- Topological sorting of nodes
- Input gathering from connected ports
- Sequential execution with error handling
- Result propagation between nodes

### 5. Enhanced I/O Nodes (`pro/flow/nodes/io_nodes.py`)
- `ContextOutputNode`: Reads from fullcode.txt
- `ClipboardNode`: Copies text to clipboard
- `FileWriteNode`: Writes to configurable path
- `OutputDisplayNode`: Shows result in properties

## Built-in Template: Best-of-5 OpenRouter

The reference implementation will provide:
1. Context source (fullcode.txt)
2. 5 OpenRouter nodes (random_free models)
3. Best-of-N synthesizer (analyzes all outputs)
4. Dual output: Clipboard + best_of_n.txt file

### Graph Structure:
```
ContextOutput → [OpenRouter LLM] x5 → BestOfN → Clipboard
                                        └─→ FileWrite(best_of_n.txt)
```

### Synthesis Prompt:
```
You will receive:
- The original context (code and user prompt)
- N candidate answers from different models

Task:
1) Analyze strengths/weaknesses of each candidate
2) Synthesize a 'best of all' answer
3) Cite brief pros/cons observed
4) Ensure final answer is complete and practical
```

## Configuration & Settings

### API Key Storage
- Primary: Node properties (for workflow-specific keys)
- Fallback: QSettings under "aicodeprep-gui/APIKeys/{provider}/api_key"
- Cross-platform: Uses Qt's QSettings for Windows/Mac/Linux compatibility

### Supported Providers
- **OpenRouter**: Supports random/free model selection
- **OpenAI**: Official API endpoints
- **Gemini**: Google's Gemini models
- **OpenAI-Compatible**: Custom endpoints with base_url

## Error Handling Strategy

### User-Friendly Errors
- Missing API keys: Prompt user with specific provider name
- Network issues: Clear error messages with actionable steps
- Invalid models: Warn and suggest alternatives
- File I/O errors: Show path and permission issues

### Graceful Degradation
- Individual node failures don't crash entire flow
- Partial results still propagate where possible
- Clear logging for debugging

## Testing Checklist

### Phase 1 Validation
1. [ ] LiteLLM dependency installs correctly
2. [ ] Flow Studio loads with new nodes registered
3. [ ] Built-in template loads successfully
4. [ ] API key configuration works
5. [ ] Basic execution completes end-to-end
6. [ ] Clipboard and file outputs work
7. [ ] Error messages display appropriately

### Sample Test Scenario
1. Generate context (creates fullcode.txt)
2. Load "Best-of-5 OpenRouter" template
3. Configure OpenRouter API key
4. Run flow
5. Verify clipboard contains synthesized result
6. Verify best_of_n.txt file created
7. Check result quality across multiple models

## Future Enhancements

### Phase 2+
- Async/parallel execution
- Token window validation
- Provider settings dialog
- DSL for text-based flow definition
- Model metadata caching
- Advanced aggregation strategies
- Flow templates marketplace

## Rationale

This implementation prioritizes:
1. **Immediate functionality**: Get basic flows working quickly
2. **User experience**: Clear errors, intuitive configuration
3. **Extensibility**: Easy to add new providers and node types
4. **Robustness**: Graceful handling of edge cases
5. **Integration**: Works seamlessly with existing context generation

The phased approach allows testing core functionality before adding complexity, while the modular design enables incremental improvements.