from aicodeprep_gui.gui.settings.preferences import _read_prefs_file, _write_prefs_file


def test_project_preferences_round_trip_dock_state(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    dock_widgets_state = {
        "flow_studio": {"main_splitter_state": "abcd"},
        "ai_chat": {"side_by_side": True, "tile_mode": "3col"},
    }

    _write_prefs_file(
        ["src/app.py"],
        window_size=(1200, 800),
        splitter_state=b"splitter-bytes",
        output_format="markdown",
        pro_features={
            "preview_window_enabled": True,
            "flow_studio_enabled": True,
            "ai_chat_enabled": False,
        },
        dock_state=b"dock-bytes",
        dock_widgets_state=dock_widgets_state,
    )

    checked, window_size, splitter_state, output_format, pro_features, _prefs_path, _is_legacy, dock_state, parsed_dock_widgets_state = _read_prefs_file()

    assert checked == {"src/app.py"}
    assert window_size == (1200, 800)
    assert splitter_state == b"splitter-bytes"
    assert output_format == "markdown"
    assert pro_features["preview_window_enabled"] is True
    assert pro_features["flow_studio_enabled"] is True
    assert pro_features["ai_chat_enabled"] is False
    assert dock_state == b"dock-bytes"
    assert parsed_dock_widgets_state == dock_widgets_state
