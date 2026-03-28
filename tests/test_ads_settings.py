from aicodeprep_gui import user_settings


def test_ads_disabled_setting_persists_in_global_settings(tmp_path, monkeypatch):
    monkeypatch.setattr(user_settings, "get_config_dir", lambda: tmp_path)

    user_settings.set_ads_disabled_setting(True)

    assert user_settings.get_ads_disabled_setting() is True
    assert (tmp_path / "settings.toml").exists()
    assert user_settings.load_settings()["ads"]["disabled"] is True


def test_ads_disabled_setting_migrates_from_legacy_pro_options(tmp_path, monkeypatch):
    monkeypatch.setattr(user_settings, "get_config_dir", lambda: tmp_path)

    user_settings.set_setting("pro_options", "ads_disabled", True)

    assert user_settings.get_ads_disabled_setting(default=None) is True
    settings_data = user_settings.load_settings()
    assert settings_data["ads"]["disabled"] is True
    assert settings_data["pro_options"]["ads_disabled"] is True
