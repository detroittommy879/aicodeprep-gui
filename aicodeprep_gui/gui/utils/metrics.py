import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from PySide6 import QtNetwork, QtCore

from aicodeprep_gui import __version__
from aicodeprep_gui.config import get_config_dir
from aicodeprep_gui.user_settings import get_section, get_setting


class MetricsManager(QtCore.QObject):
    BATCH_ENDPOINT_URL = "https://wuu73.org/idea/aicp-metrics/batch"
    SINGLE_EVENT_ENDPOINT_URL = "https://wuu73.org/idea/aicp-metrics/event"
    BATCH_SIZE = 25
    MAX_QUEUE_SIZE = 1000
    FLUSH_DELAY_MS = 12000
    SINGLE_EVENT_DELAY_MS = 3000   # min ms between events in single-event fallback
    PERIODIC_FLUSH_MS = 45000
    RETRY_BASE_MS = 10000
    RETRY_MAX_MS = 300000
    MAX_EVENT_AGE_HOURS = 48       # purge persisted events older than this on load

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self._queue_path = Path(get_config_dir()) / "metrics-queue.json"
        self._queue: list[dict[str, Any]] = []
        self._request_in_flight = False
        self._retry_delay_ms = self.RETRY_BASE_MS
        self._supports_batch_endpoint = True
        self._seen_once_keys: set[str] = set()

        self._flush_timer = QtCore.QTimer(self)
        self._flush_timer.setSingleShot(True)
        self._flush_timer.timeout.connect(self.flush_queue)

        self._periodic_timer = QtCore.QTimer(self)
        self._periodic_timer.setInterval(self.PERIODIC_FLUSH_MS)
        self._periodic_timer.timeout.connect(self.flush_queue)
        self._periodic_timer.start()

        self._load_queue()
        if self._queue:
            self._schedule_flush(self.SINGLE_EVENT_DELAY_MS)

    def _metrics_disabled(self) -> bool:
        return (
            os.environ.get("AICODEPREP_TEST_MODE") == "1"
            or os.environ.get("AICODEPREP_NO_METRICS") == "1"
        )

    def _parse_event_time(self, event: dict) -> datetime:
        try:
            return datetime.fromisoformat(event.get("local_time", ""))
        except Exception:
            return datetime.min

    def _load_queue(self) -> None:
        if not self._queue_path.exists():
            return

        try:
            with open(self._queue_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)

            if isinstance(data, dict):
                events = data.get("events", [])
            else:
                events = data

            if isinstance(events, list):
                self._queue = [
                    event for event in events if isinstance(event, dict)]
        except Exception as exc:
            logging.warning(f"Metrics: failed to load queue file: {exc}")
            self._queue = []

        # Purge events that are too old to be useful — they will never be
        # accepted by the server and would otherwise re-blast on every launch.
        if self._queue:
            cutoff = datetime.now() - timedelta(hours=self.MAX_EVENT_AGE_HOURS)
            before = len(self._queue)
            self._queue = [
                e for e in self._queue
                if self._parse_event_time(e) >= cutoff
            ]
            purged = before - len(self._queue)
            if purged:
                logging.info(
                    "Metrics: purged %d stale event(s) older than %dh from persisted queue.",
                    purged, self.MAX_EVENT_AGE_HOURS,
                )

    def _save_queue(self) -> None:
        payload = {
            "version": 1,
            "events": self._queue,
        }
        tmp_path = self._queue_path.with_suffix(".tmp")

        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=True,
                          separators=(",", ":"))
            tmp_path.replace(self._queue_path)
        except Exception as exc:
            logging.error(f"Metrics: failed to save queue file: {exc}")
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass

    def _schedule_flush(self, delay_ms: int | None = None) -> None:
        if self._metrics_disabled() or self._request_in_flight or not self._queue:
            return

        delay_ms = self.FLUSH_DELAY_MS if delay_ms is None else max(
            0, int(delay_ms))

        if delay_ms == 0:
            QtCore.QTimer.singleShot(0, self.flush_queue)
            return

        if not self._flush_timer.isActive() or delay_ms < self._flush_timer.remainingTime():
            self._flush_timer.start(delay_ms)

    def _enqueue_payload(self, payload: dict[str, Any]) -> None:
        self._queue.append(payload)
        if len(self._queue) > self.MAX_QUEUE_SIZE:
            drop_count = len(self._queue) - self.MAX_QUEUE_SIZE
            del self._queue[:drop_count]
            logging.warning(
                f"Metrics: queue exceeded {self.MAX_QUEUE_SIZE}, dropped {drop_count} oldest events"
            )
        self._save_queue()

    def _coerce_jsonable(self, value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return {str(key): self._coerce_jsonable(val) for key, val in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._coerce_jsonable(item) for item in value]
        return str(value)

    def _current_plan_status(self) -> str:
        try:
            paid_license = get_section("pro_license")
            license_key = str(paid_license.get(
                "license_key", "") or "").strip()
            has_paid_license = bool(
                paid_license.get("pro_enabled", False)
                and paid_license.get("license_verified", False)
                and license_key
            )
            if has_paid_license:
                return "paid"

            free_access_cache = get_section("pro_free_access")
            if bool(free_access_cache.get("free_for_all", False)):
                return "free_remote_access"
        except Exception as exc:
            logging.debug(f"Metrics: failed to determine plan status: {exc}")

        return "free"

    def _current_language(self) -> str:
        try:
            language = get_setting("language", "current_language", "en")
            return str(language or "en").strip() or "en"
        except Exception:
            return "en"

    def _build_payload(self, event_type: str, token_count=None, details=None) -> dict[str, Any] | None:
        if not hasattr(self.main_window, "user_uuid") or not self.main_window.user_uuid:
            logging.warning("Metrics: user_uuid not found, skipping event.")
            return None

        normalized_event_type = str(event_type or "").strip().lower()
        if not normalized_event_type:
            return None

        payload: dict[str, Any] = {
            "event_id": str(uuid.uuid4()),
            "user_id": self.main_window.user_uuid,
            "event_type": normalized_event_type,
            "local_time": datetime.now().isoformat(),
            "plan_status": self._current_plan_status(),
            "ui_language": self._current_language(),
            "app_version": __version__,
        }

        if token_count is not None:
            try:
                payload["token_count"] = int(token_count)
            except Exception:
                logging.debug(
                    f"Metrics: invalid token_count for {normalized_event_type}: {token_count}")

        safe_details = self._coerce_jsonable(details or {})
        if isinstance(safe_details, dict) and safe_details:
            payload["details"] = safe_details

        return payload

    def _send_metric_event(self, event_type, token_count=None, details=None, once_key=None):
        if self._metrics_disabled():
            logging.debug(f"Test mode: skipping metric event: {event_type}")
            return

        try:
            dedupe_key = str(once_key).strip() if once_key else None
            if dedupe_key and dedupe_key in self._seen_once_keys:
                return

            payload = self._build_payload(
                event_type, token_count=token_count, details=details)
            if payload is None:
                return

            self._enqueue_payload(payload)
            if dedupe_key:
                self._seen_once_keys.add(dedupe_key)

            if len(self._queue) >= self.BATCH_SIZE:
                self._schedule_flush(self.SINGLE_EVENT_DELAY_MS)
            else:
                self._schedule_flush()
        except Exception as exc:
            logging.error(f"Error queueing metric event '{event_type}': {exc}")

    def _build_request(self, url: str) -> QtNetwork.QNetworkRequest:
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        request.setHeader(
            QtNetwork.QNetworkRequest.ContentTypeHeader,
            "application/json",
        )
        return request

    def flush_queue(self) -> None:
        if self._metrics_disabled() or self._request_in_flight or not self._queue:
            return

        try:
            if self._supports_batch_endpoint:
                batch = self._queue[:self.BATCH_SIZE]
                endpoint_url = self.BATCH_ENDPOINT_URL
                request_body = {"events": batch}
            else:
                batch = self._queue[:1]
                endpoint_url = self.SINGLE_EVENT_ENDPOINT_URL
                request_body = batch[0]

            request = self._build_request(endpoint_url)
            json_data = QtCore.QByteArray(
                json.dumps(request_body, ensure_ascii=True,
                           separators=(",", ":")).encode("utf-8")
            )

            batch_ids = [event.get("event_id")
                         for event in batch if event.get("event_id")]
            self._request_in_flight = True
            reply = self.main_window.network_manager.post(request, json_data)
            reply.finished.connect(
                lambda reply=reply, batch_ids=batch_ids, used_batch=self._supports_batch_endpoint: self._handle_flush_reply(
                    reply,
                    batch_ids,
                    used_batch,
                )
            )
        except Exception as exc:
            self._request_in_flight = False
            logging.error(f"Metrics: failed to flush queue: {exc}")
            self._schedule_flush(self._retry_delay_ms)
            self._retry_delay_ms = min(
                self._retry_delay_ms * 2, self.RETRY_MAX_MS)

    def _handle_flush_reply(self, reply, batch_ids, used_batch: bool) -> None:
        self._request_in_flight = False
        status_code = reply.attribute(
            QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)

        try:
            error = reply.error()
            body = bytes(reply.readAll()).decode("utf-8", errors="replace")
        except Exception:
            error = QtNetwork.QNetworkReply.NetworkError.UnknownNetworkError
            body = ""

        success = (
            error == QtNetwork.QNetworkReply.NetworkError.NoError
            and isinstance(status_code, int)
            and 200 <= status_code < 300
        )

        if success:
            batch_id_set = set(batch_ids)
            self._queue = [
                event for event in self._queue
                if event.get("event_id") not in batch_id_set
            ]
            self._save_queue()
            self._retry_delay_ms = self.RETRY_BASE_MS
            if self._queue:
                # Use a delay even for batch mode to avoid blasting the server
                # at full speed when the queue is large.
                self._schedule_flush(self.SINGLE_EVENT_DELAY_MS)
        else:
            logging.warning(
                f"Metrics flush failed (status={status_code}, error={error}): {body[:400]}"
            )

            if status_code == 422:
                # Server permanently rejected these events due to schema
                # validation (e.g. unknown event_type on an older deployment).
                # Retrying will never help — drop them and move on.
                batch_id_set = set(batch_ids)
                dropped_count = sum(
                    1 for e in self._queue
                    if e.get("event_id") in batch_id_set
                )
                self._queue = [
                    event for event in self._queue
                    if event.get("event_id") not in batch_id_set
                ]
                self._save_queue()
                self._retry_delay_ms = self.RETRY_BASE_MS
                logging.warning(
                    "Metrics: dropped %d event(s) permanently rejected by server "
                    "(422 schema mismatch — server may not support newer event types yet).",
                    dropped_count,
                )
                if self._queue:
                    # Use the single-event delay even here so a backlog of
                    # rejected events doesn't blast the server at full speed.
                    self._schedule_flush(self.SINGLE_EVENT_DELAY_MS)
            elif used_batch and status_code in {404, 405}:
                logging.info(
                    "Metrics: batch endpoint unavailable, falling back to single-event delivery")
                self._supports_batch_endpoint = False
                self._schedule_flush(self.SINGLE_EVENT_DELAY_MS)
            else:
                self._schedule_flush(self._retry_delay_ms)
                self._retry_delay_ms = min(
                    self._retry_delay_ms * 2, self.RETRY_MAX_MS)

        reply.deleteLater()
