from __future__ import annotations

from krishna_story_factory.content.caption import format_whatsapp_caption


def test_activity_send_mode_wording() -> None:
    cases = {
        "OPTIONAL": "Optional family activity: Prayer Wheel.",
        "WEEKEND_PROJECT": "Weekend project: Build a Chariot.",
        "COLORING_ONLY": "Today's optional activity is the coloring page.",
        "PARENT_GUIDED": "Parent-guided activity: Talk Together.",
    }
    for mode, expected in cases.items():
        caption = format_whatsapp_caption(
            story_title="Story", package_link="https://drive.example/story",
            activity_title={"OPTIONAL": "Prayer Wheel", "WEEKEND_PROJECT": "Build a Chariot", "PARENT_GUIDED": "Talk Together"}.get(mode, ""),
            recommended_send_mode=mode,
        )
        assert expected in caption


def test_drive_package_link_included_in_caption_when_configured() -> None:
    link = "https://drive.google.com/drive/folders/1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei?usp=sharing"
    caption = format_whatsapp_caption(story_title="The Wedding and the Heavenly Voice", package_link=link)
    assert link in caption
    assert "Today's Krishna Book bedtime story is ready" in caption
    assert "read or play" in caption.lower()
    assert "group" not in caption.lower()
