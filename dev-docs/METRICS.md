# Metrics Overview

This document describes how metrics currently work in `aicodeprep-gui`, where the code lives, what gets sent, and how the system behaves when the server or client changes.

## Goals

- Keep metrics lightweight and anonymous.
- Avoid blocking the UI on network delivery.
- Survive app restarts and temporary network failures.
- Stay compatible with older or partial server deployments.
- Stay fully disabled in automated tests.

## Main Implementation

The core implementation is in `aicodeprep_gui/gui/utils/metrics.py`.

`MetricsManager` is created once from `FileSelectionGUI` in `aicodeprep_gui/gui/main_window.py` and all normal metric events flow through `main_window._send_metric_event(...)`.

That gives the app a single place for:

- payload building
- queueing
- local persistence
- batching
- retry handling
- compatibility fallback from batch to single-event delivery

## Data Flow

The normal flow is:

1. UI code calls `self._send_metric_event(...)`.
2. `MetricsManager._build_payload(...)` creates a normalized JSON-safe payload.
3. The payload is appended to an in-memory queue.
4. The queue is written to `~/.aicodeprep-gui/metrics-queue.json`.
5. A delayed or immediate flush is scheduled.
6. The app tries to POST either a batch or a single event.
7. On success, delivered events are removed from the queue.
8. On failure, the queue stays on disk and is retried later.

This means metrics are best-effort and non-blocking. If the network is down or the endpoint is unavailable, events are not discarded immediately.

## Payload Shape

Each event is built with these common fields:

- `event_id`: random UUID for the event
- `user_id`: anonymous persisted app UUID
- `event_type`: normalized lower-case event name
- `local_time`: local ISO timestamp
- `plan_status`: `free`, `free_remote_access`, or `paid`
- `ui_language`: current UI language
- `app_version`: current app version

Optional fields:

- `token_count`: included when available and coercible to an integer
- `details`: extra event-specific metadata after JSON-safe coercion

The client does not send raw Python objects. Dicts, lists, tuples, sets, numbers, booleans, strings, and `None` are converted into JSON-safe values. Unknown objects are stringified.

## Queueing and Persistence

The queue file is stored at:

- `~/.aicodeprep-gui/metrics-queue.json`

Important constants from `MetricsManager`:

- `BATCH_SIZE = 25`
- `MAX_QUEUE_SIZE = 1000`
- `FLUSH_DELAY_MS = 12000`
- `PERIODIC_FLUSH_MS = 45000`
- `RETRY_BASE_MS = 10000`
- `RETRY_MAX_MS = 300000`

Behavior:

- New events are queued immediately.
- A normal flush is delayed by 12 seconds to avoid sending tiny requests constantly.
- A periodic flush runs every 45 seconds.
- If the queue reaches 25 events, the flush is scheduled immediately.
- If the queue grows past 1000 events, the oldest events are dropped and a warning is logged.
- Queue writes use a temporary file and replace step to reduce corruption risk.

## Delivery Endpoints

The metrics client currently knows about two endpoints:

- Batch: `https://wuu73.org/idea/aicp-metrics/batch`
- Single event: `https://wuu73.org/idea/aicp-metrics/event`

Normal behavior is to prefer the batch endpoint.

If the batch endpoint responds with `404` or `405`, the client assumes that deployment does not support batching yet and permanently falls back to single-event delivery for the rest of the session.

That fallback is the main backward-compatibility behavior in the current metrics system.

## Retry Behavior

On failed delivery:

- the queue remains on disk
- the client logs the failure
- retry delay grows exponentially from 10 seconds up to 5 minutes

On successful delivery:

- delivered events are removed from the queue
- retry delay is reset to the base value
- if more queued events remain, another flush is scheduled immediately

This makes the client resilient to temporary outages without freezing the GUI.

## Test and Local Disable Behavior

Metrics are disabled entirely when either of these environment variables is set to `1`:

- `AICODEPREP_TEST_MODE`
- `AICODEPREP_NO_METRICS`

This is checked in `MetricsManager._metrics_disabled()`.

The test suite sets both values in `tests/conftest.py`, so tests do not accidentally send live events and do not become flaky because of network calls.

## Event Sources

The main event sources currently include these areas.

### Main window

From `aicodeprep_gui/gui/main_window.py`:

- `open`
- `feature_toggle`
- `generate_start`
- `generate_success`
- `generate_canceled`
- `generate_to_ai_start`
- `generate_to_ai_success`
- `generate_to_ai_canceled`
- `generate_to_ai_failed`

These events include contextual details such as selected file count, destination, prompt usage, selected AI models, and token counts when available.

### AI Chat

From `aicodeprep_gui/pro/ai_chat/chat_tab.py`:

- `ai_chat_request_started`
- `ai_chat_request_completed`
- `ai_chat_request_failed`

These include fields such as endpoint id, model, message count, response length, and error text.

### Flow Studio

From `aicodeprep_gui/pro/flow/flow_dock.py`:

- `flow_run_started`
- `flow_run_completed`
- `flow_run_failed`

These include the configured models involved in the current flow execution.

### Preferences and dialogs

Other UI paths also emit metrics, for example:

- preference changes in `aicodeprep_gui/gui/settings/preferences.py`
- feature voting in `aicodeprep_gui/gui/components/dialogs.py`

## Special Case: Feature Vote Dialog

The feature vote dialog has a fallback path in `aicodeprep_gui/gui/components/dialogs.py`.

If it has access to a parent window with `_send_metric_event`, it uses the normal `MetricsManager` queue.

If it does not, it posts a single event directly to the single-event endpoint.

That means most metrics are queued and retried, but this one dialog still has a direct-send fallback path.

## Compatibility Notes

The current metrics implementation is intentionally tolerant of mixed server/client versions.

### Older server, newer client

If the client supports batching but the deployed server only supports single-event ingestion, the client falls back automatically after a `404` or `405` from the batch endpoint.

### Offline or failing server

Events stay in `metrics-queue.json` and are retried later with backoff.

### Test runs or scripted GUI automation

Metrics are disabled by environment variable so test runs do not generate live traffic.

### App upgrades

Queued events are plain JSON and carry an `app_version`, so future server-side analysis can distinguish old and new clients without breaking transport.

## Logging and Troubleshooting

Useful log messages already exist for:

- queue load failures
- queue save failures
- invalid token counts
- missing `user_uuid`
- flush failures
- batch endpoint fallback to single-event delivery
- queue overflow trimming

If metrics appear to be missing, check these first:

1. Is `AICODEPREP_TEST_MODE=1` or `AICODEPREP_NO_METRICS=1` set?
2. Does `~/.aicodeprep-gui/metrics-queue.json` exist and keep growing?
3. Are logs showing batch fallback or repeated retry warnings?
4. Does the running server support `/batch`, `/event`, or only one of them?

## Files to Inspect

- `aicodeprep_gui/gui/utils/metrics.py`
- `aicodeprep_gui/gui/main_window.py`
- `aicodeprep_gui/pro/ai_chat/chat_tab.py`
- `aicodeprep_gui/pro/flow/flow_dock.py`
- `aicodeprep_gui/gui/components/dialogs.py`
- `aicodeprep_gui/gui/settings/preferences.py`
- `tests/conftest.py`

## Practical Summary

The current metrics system is a queued Qt-network client with disk persistence, delayed flushes, exponential retry, and automatic fallback from batch delivery to single-event delivery. The important compatibility point is that a newer app can still work against an older metrics deployment without losing all events, and tests remain isolated because metrics are hard-disabled in test mode.
