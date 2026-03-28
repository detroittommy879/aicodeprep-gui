from datetime import datetime, timezone

from aicodeprep_gui.pro import license_state


class _DummyResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


def test_parse_remote_free_flag_understands_true_and_false_values():
    assert license_state._parse_remote_free_flag('"free=1\n"') is True
    assert license_state._parse_remote_free_flag("free=0") is False


def test_parse_remote_notice_message_supports_message_and_newlines():
    assert (
        license_state._parse_remote_notice_message(
            'message="Free period ending soon\\nThanks for trying it"\n'
        )
        == "Free period ending soon\nThanks for trying it"
    )


def test_paid_license_short_circuits_remote_free_check(monkeypatch):
    stored = {
        "pro_license": {
            "pro_enabled": True,
            "license_key": "paid-key",
            "license_verified": True,
        }
    }

    monkeypatch.setattr(license_state, "get_section",
                        lambda name: stored.get(name, {}))

    def fail_remote_call(*args, **kwargs):
        raise AssertionError("remote free check should not run for paid users")

    monkeypatch.setattr(license_state.requests, "get", fail_remote_call)

    assert license_state.is_pro_enabled([]) is True
    assert stored["pro_license"]["license_key"] == "paid-key"


def test_remote_free_flag_enables_pro_and_updates_cache(monkeypatch):
    stored = {}

    monkeypatch.setattr(license_state, "get_section",
                        lambda name: stored.get(name, {}))
    monkeypatch.setattr(license_state, "set_section",
                        lambda name, values: stored.__setitem__(name, values))
    monkeypatch.setattr(
        license_state.requests,
        "get",
        lambda *args, **kwargs: _DummyResponse("free=1\n"),
    )

    now = datetime(2026, 3, 9, 12, 0, tzinfo=timezone.utc)
    assert license_state.is_free_access_enabled(now=now) is True
    assert stored[license_state.FREE_ACCESS_SECTION]["free_for_all"] is True


def test_remote_access_state_includes_message(monkeypatch):
    stored = {}

    monkeypatch.setattr(license_state, "get_section",
                        lambda name: stored.get(name, {}))
    monkeypatch.setattr(license_state, "set_section",
                        lambda name, values: stored.__setitem__(name, values))
    monkeypatch.setattr(
        license_state.requests,
        "get",
        lambda *args, **kwargs: _DummyResponse(
            "free=1\nmessage=Heads up soon\n"),
    )

    state = license_state.get_remote_access_state(
        now=datetime(2026, 3, 9, 12, 30, tzinfo=timezone.utc)
    )

    assert state["free_for_all"] is True
    assert state["announcement_message"] == "Heads up soon"


class _DummySignal:
    def __init__(self):
        self._callback = None

    def connect(self, callback):
        self._callback = callback


class _DummyReply:
    def __init__(self):
        self.finished = _DummySignal()

    def isRunning(self):
        return True


class _DummyNetworkManager:
    def __init__(self):
        self.last_data = None

    def post(self, request, data):
        self.last_data = bytes(data).decode("utf-8")
        return _DummyReply()


def test_activate_dialog_verify_request_does_not_increment_uses(qapp_session):
    from aicodeprep_gui.gui.components.dialogs import ActivateProDialog

    manager = _DummyNetworkManager()
    dialog = ActivateProDialog("product-123", manager)
    dialog.send_request("paid-key")
    dialog.reply_timeout_timer.stop()

    assert "increment_uses_count=false" in manager.last_data
    dialog.close()
