from aicodeprep_gui.gui.components.ad_widget import AdWidget


def test_ad_widget_stays_hidden_when_ads_disabled(qapp_session):
    widget = AdWidget()
    widget.set_ads_disabled(True)

    widget.set_ad(
        {
            "title": "Test ad",
            "content": "Should remain hidden",
            "link": None,
        }
    )

    assert widget.isHidden()
    assert not widget.repeat_timer.isActive()
