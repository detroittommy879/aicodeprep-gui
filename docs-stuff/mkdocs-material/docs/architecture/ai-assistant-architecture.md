# AI Assistant Architecture Notes

This document describes how the current AI Help implementation works in
`w111erd`, what it stores, where requests flow, what safeguards exist today, and
what gaps still remain.

This is a description of the current implementation, not a final design.

## Current split: TypeScript vs Rust

The AI path is split on purpose.

### TypeScript / React side

Files:

- `src/components/AssistantOverlay.tsx`
- `src/components/DetachedAssistantWindow.tsx`
- `src/store/assistantStore.ts`
- `src/services/assistantService.ts`
- `src/ai/prompts/index.ts`
- `src/store/sessionStore.ts`
- `src/services/tauriService.ts`
- `src/services/windowBridge.ts`

Responsibilities:

- render the AI Help window UI
- store overlay UI state, bounds, messages, and settings state
- collect bounded terminal context from the active terminal session
- assemble prompt text/instructions
- validate provider settings before sending
- call the backend Tauri command
- sync the detached AI Help window with the active terminal via a small window bridge
- parse the reply into:
- explanation text
- up to three optional terminal actions
- status/error messaging
- dispatch explicit user-approved terminal input back into the active PTY

### Rust / Tauri side

Files:

- `src-tauri/src/main.rs`

Responsibilities:

- receive the AI completion request from the frontend
- perform the actual HTTP request using `reqwest`
- keep browser/CORS behavior out of the equation
- return the provider response back to the frontend
- participate in profile-based filesystem storage

So the current AI network request is done in Rust, while the prompt assembly and
UI/state handling are done in TypeScript.

## Where API keys are stored right now

Right now provider credentials are stored in the active profile config JSON.

They can now be edited from either:

- the quick controls inside the detached AI Help window
- the dedicated `AI Help` tab in the detached Settings window

That means:

- endpoint URL
- model ID
- provider kind
- API key

are persisted together with the rest of the app profile settings.

The config is stored under the app's profile data directory. In practice that is
the same profile-aware area already used for other persisted settings/themes.

Important caveat:

- the API key is not currently stored in the OS credential vault
- it is not currently encrypted at rest by the app
- it is simply part of the saved profile config document

That is acceptable for a first working pass, but it is not ideal long term.

## Current request flow

At a high level, the order is:

1. user opens the detached AI Help window
2. user enters a question
3. the assistant window syncs active-terminal state from the main window and uses that state for context
4. the assistant service builds the system/user prompts from
   `src/ai/prompts/index.ts`
5. TypeScript sends a Tauri invoke request to Rust
6. Rust makes an OpenAI-compatible HTTP request with `reqwest`
7. for chat replies, the backend now streams chunks back to the frontend over a
   Tauri event channel while the invoke is still in flight
8. the frontend keeps a live partial answer visible in the overlay
9. once the stream completes, the frontend parses the final response into text
   plus optional terminal actions
10. the overlay renders the final answer and action cards
11. if the reply contains terminal actions, the user can explicitly click a
    button to send a command, trigger a control action like `Ctrl+C`, or run a
    short ordered sequence of up to three executable steps

The important UX detail is that terminal actions are not silently executed. The
user must explicitly choose to send them.

There is also now a connection-test action in the UI that uses the same backend
request path, so you can confirm the configured endpoint, key, and model are
reaching a live provider.

There is also now a debug inspector mode in the overlay. When enabled, it shows:

- the exact system prompt and user prompt sent to the provider
- the terminal-context snapshot that was included
- the current UI chat history snapshot
- the raw streamed provider output before parsing

That is primarily there so prompt/context mistakes are visible instead of
guesswork.

AI Help now lives in its own native Tauri window. The main window stays
authoritative for active terminal selection and PTY-backed command dispatch,
while the assistant window keeps its own chat transcript and UI state.

## How terminal context is gathered

The current assistant can use recent terminal text from the active session.

Source:

- `src/store/sessionStore.ts`

Behavior:

- it pulls a bounded amount of recent terminal text
- the amount is limited by the configured character cap
- context inclusion can be disabled in settings

That keeps the prompt smaller and avoids sending an unlimited terminal backlog,
but it does **not** mean the text is automatically safe.

## Security and privacy concerns

The main current risk is straightforward:

- terminal output may contain secrets, tokens, hostnames, internal paths, or
  user data
- if context capture is enabled, some of that recent output may be sent to the
  configured AI provider

Current mitigations are basic:

- bounded context length
- explicit provider configuration
- no silent command execution
- prompts that try to stay diagnostic/helpful instead of aggressive

Current gaps:

- no automatic secret redaction
- no allow/block list for terminal patterns
- no "preview the exact context before send" step
- no per-provider data handling explanation in the UI yet
- no OS keychain storage for credentials yet

So today the user still needs to make an informed trust decision before enabling
terminal-context capture.

## Error handling and user transparency today

Current positive behaviors:

- missing configuration is validated before request
- frontend failures are surfaced instead of silently ignored
- backend/network errors are bubbled back to the UI
- streamed partial text is visible before the final parse step completes
- if structured command parsing fails, the frontend now tries to recover obvious
  command candidates from fenced or inline code in the reply text
- debug logging can now be written to a real log file when debug logging is
  enabled
- suggested commands require explicit user action before being sent

Current limitations:

- there is no retry policy yet
- there is no exponential backoff yet
- there is no circuit-breaker/rate-limit awareness yet
- there is no provider health indicator yet
- there is no request cancellation/restart policy beyond normal UI flow
- prior assistant chat turns are still not included in provider requests yet;
  the debug panel shows that gap explicitly

## Retries and backoff

Current state:

- no retry loop is implemented
- no exponential backoff is implemented

That means a transient 429/500/network failure will currently fail fast and
surface an error to the user.

This is honest behavior, but not yet polished behavior.

## Model selection and discovery

Current state:

- the user can type the model ID
- the UI now attempts a provider-backed `v1/models` fetch when endpoint and key
  are present
- successful model discovery is exposed as autocomplete suggestions in both the
  overlay and the full settings page

So the current UX is now discovery-first with a manual fallback.

That is enough to support OpenAI/OpenRouter/custom compatible endpoints, but it
assumes the user already knows the model identifier.

## Prompt system

Current prompt definitions live in:

- `src/ai/prompts/index.ts`

That is intentional so the prompt text is easy to locate and tune later.

The current prompts are designed to:

- keep answers practical
- prefer explanation plus suggested commands
- avoid silently running anything
- work with bounded recent-terminal context
- stream the human-readable answer first and put command metadata in a separate
  trailing section so the overlay can show progressive output without exposing
  raw structured payloads

## Storage locations related to AI/theme/debugging

Current profile-oriented storage areas are roughly:

- active profile config JSON: settings + assistant provider config
- profile themes folder: saved custom theme files
- debug log path: backend-managed log file when debug logging is enabled

This means the AI system is already using the same profile-aware storage model as
the rest of the app instead of creating a totally separate settings silo.

## What libraries or helper layers are worth considering later

No library is being chosen in this document. These are just sensible categories
to evaluate later.

### For retries / transport middleware

Rust options worth evaluating:

- `backoff`
- `tower`
- `reqwest-middleware`
- `tower-http`

These can help with:

- exponential backoff
- retry-on-transient-status rules
- timeout policy
- shared middleware for logging/metrics

### For secure secret handling

Rust/options worth evaluating:

- `keyring` for OS credential storage
- `secrecy`
- `zeroize`

These help with:

- moving API keys out of plain config files
- reducing accidental debug-log leakage
- clearer secret-handling boundaries in memory

### For tracing/logging

Worth evaluating:

- `tracing`
- `tracing-subscriber`

These would improve:

- request lifecycle visibility
- structured logs
- opt-in debug sessions when users report AI failures

### For content filtering / redaction

Worth evaluating:

- regex-based redaction pass for common secrets
- configurable redact/block lists
- a context preview screen before send

The biggest practical win may be a simple, transparent redaction layer before any
provider request leaves the machine.

## What should be improved next

From an architecture standpoint, the most useful next upgrades would be:

1. move API keys into OS keychain/keyring storage
2. add request retry with bounded exponential backoff
3. add optional model discovery for compatible providers
4. add context preview/redaction controls
5. add better provider status/error detail in the overlay

## Current truth in one paragraph

Today the AI system is a workable first pass: the frontend builds prompts and UI,
the Rust backend performs OpenAI-compatible requests, provider settings are
stored in the active profile config, terminal context is bounded but not
automatically sanitized, model entry is manual, retries/backoff are not yet
implemented, and the user must explicitly choose to send any suggested command to
the terminal.
