import json
import logging
from datetime import datetime
from PySide6 import QtNetwork, QtCore

class MetricsManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _send_metric_event(self, event_type, token_count=None):
        try:
            if not hasattr(self.main_window, 'user_uuid') or not self.main_window.user_uuid:
                logging.warning("Metrics: user_uuid not found, skipping event.")
                return

            endpoint_url = "https://wuu73.org/idea/aicp-metrics/event"
            request = QtNetwork.QNetworkRequest(QtCore.QUrl(endpoint_url))
            request.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json")

            payload = {
                "user_id": self.main_window.user_uuid,
                "event_type": event_type,
                "local_time": datetime.now().isoformat()
            }
            if token_count is not None:
                payload["token_count"] = token_count

            json_data = QtCore.QByteArray(json.dumps(payload).encode('utf-8'))
            self.main_window.network_manager.post(request, json_data)
            logging.info(f"Sent metric event: {event_type}")

        except Exception as e:
            logging.error(f"Error creating metric request for event '{event_type}': {e}")
