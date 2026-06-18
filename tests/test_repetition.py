from __future__ import annotations

from krishna_story_factory.quality.repetition import clean_repetition, detect_repetition


def test_repeated_story_closing_fails() -> None:
    text = (
        "The devotees remember this pastime with faith and love. "
        "The devotees remember this pastime with faith and love."
    )
    report = detect_repetition(text, content_type="story")
    assert report.errors


def test_repeated_audio_closing_fails() -> None:
    text = (
        "Tonight we heard the wedding story. "
        "Tonight we heard the wedding story again."
    )
    report = detect_repetition(text, content_type="audio")
    assert report.errors


def test_repeated_paragraph_fails() -> None:
    para = "Devaki and Vasudeva prayed with peaceful hearts in the prison cell tonight."
    text = f"{para}\n\n{para}"
    report = detect_repetition(text, content_type="story")
    assert report.errors


def test_repeated_eight_word_phrase_fails() -> None:
    phrase = "the demigods prayed with sincere hearts for protection tonight always"
    text = f"{phrase}. Another line. {phrase}. Again here. {phrase}."
    report = detect_repetition(text, content_type="story")
    assert report.errors


def test_repeated_names_do_not_false_fail() -> None:
    text = (
        "Krishna protects Devaki and Vasudeva with love. "
        "Devaki and Vasudeva trust Krishna in Mathura. "
        "Krishna hears the prayers of Devaki and Vasudeva."
    )
    report = detect_repetition(text, content_type="story")
    assert not report.errors


def test_post_processing_removes_duplicated_closing_blocks() -> None:
    text = (
        "Main story line one.\n\n"
        "The devotees remember this pastime with faith and love.\n\n"
        "The devotees remember this pastime with faith and love."
    )
    cleaned = clean_repetition(text, content_type="story")
    assert cleaned.lower().count("the devotees remember this pastime") == 1


def test_quality_fails_if_post_processing_cannot_clean_repetition() -> None:
    sentence = "Before sleep, think of one kind action you can do tomorrow with joy."
    text = " ".join([sentence] * 4)
    cleaned = clean_repetition(text, content_type="audio")
    report = detect_repetition(cleaned, content_type="audio")
    assert report.errors
