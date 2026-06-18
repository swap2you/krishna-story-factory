from __future__ import annotations

from krishna_story_factory.content.caption import format_whatsapp_caption


def test_drive_package_link_included_in_caption_when_configured() -> None:
    link = "https://drive.google.com/drive/folders/1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei?usp=sharing"
    caption = format_whatsapp_caption(story_title="The Wedding and the Heavenly Voice", package_link=link)
    assert link in caption
    assert "Today's Krishna Book bedtime story is ready" in caption
    assert "reply here" in caption.lower()
    assert "group" not in caption.lower()
