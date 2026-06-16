from aicodeprep_gui.gui.settings.preferences import _read_prefs_file, _write_prefs_file
from aicodeprep_gui.gui.settings.preferences import PreferencesManager


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


def test_project_preferences_use_explicit_project_root(monkeypatch, tmp_path):
    project_root = tmp_path / "project"
    other_dir = tmp_path / "other"
    project_root.mkdir()
    other_dir.mkdir()

    monkeypatch.chdir(other_dir)

    _write_prefs_file(["src/app.py"], project_root=str(project_root))

    checked, window_size, splitter_state, output_format, pro_features, prefs_path, is_legacy, dock_state, dock_widgets_state = _read_prefs_file(
        project_root=str(project_root)
    )

    assert checked == {"src/app.py"}
    assert window_size is None
    assert splitter_state is None
    assert output_format == "xml"
    assert pro_features == {}
    assert prefs_path == str(project_root / ".aicp" / "preferences.ini")
    assert is_legacy is False
    assert dock_state is None
    assert dock_widgets_state == {}


def test_preferences_manager_loads_from_window_project_root(monkeypatch, tmp_path):
    project_root = tmp_path / "project"
    other_dir = tmp_path / "other"
    project_root.mkdir()
    other_dir.mkdir()

    monkeypatch.chdir(other_dir)
    _write_prefs_file(["src/main.py"], project_root=str(project_root))

    class DummyWindow:
        def __init__(self, project_root):
            self.project_root = str(project_root)

    manager = PreferencesManager(DummyWindow(project_root))
    manager.load_prefs_if_exists()

    assert manager.prefs_loaded is True
    assert manager.prefs_file_exists is True
    assert manager.checked_files_from_prefs == {"src/main.py"}
