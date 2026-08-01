from krishna_story_factory.content.story_tts_equivalence import (
    compare_canonical_to_tts,
    extract_canonical_narrative,
    normalize_semantic,
)


def test_extract_drops_educational_sections():
    md = "# Title\n\nBody line.\n\n## Lessons\n- one\n\n## Questions\nQ?\n"
    body = extract_canonical_narrative(md)
    assert "Body line." in body
    assert "Lessons" not in body
    assert "Questions" not in body


def test_non_semantic_pause_difference():
    story = "# S\n\nKrishna smiled.\n"
    tts = "Krishna smiled. [pause]"
    result = compare_canonical_to_tts(story_md=story, tts_source=tts)
    assert result.status in {"MATCH", "NON-SEMANTIC DIFFERENCE"}
    assert normalize_semantic(extract_canonical_narrative(story)) == normalize_semantic(tts)


def test_material_difference():
    story = "# S\n\nKrishna smiled.\n"
    tts = "Balarama laughed."
    result = compare_canonical_to_tts(story_md=story, tts_source=tts)
    assert result.status == "MATERIAL DIFFERENCE"
