"""Lock the CI test-tier contract.

Tier markers exist so that tests needing unshippable data (large media, private
pre-copyright drafts, operator runtime state) run where that data exists instead
of failing everywhere. That mechanism is only trustworthy if it cannot grow
quietly, so the census below is exhaustive: adding a marker to a new test fails
this test until the tier is justified here.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Needs public Stories 001-020 bytes; provisioned in CI from the approved
# bhava-content-001-020-v1 GitHub Release.
BAND_CHAPTERS = ("001", "002", "003", "006", "007", "008", "009")
CORRECTED_CHAPTERS = ("007", "009")

EXPECTED_CONTENT_RELEASE = {
    "tests/portal/test_catalog_discover_stories.py::test_catalog_discovers_released_stories_including_008",
    "tests/portal/test_package_hash_guard.py::test_locked_story_packages_match_recorded_hashes",
    "tests/portal/test_package_to_tabs_contract.py::test_package_to_tabs_required_web_assets",
    "tests/portal/test_package_to_tabs_contract.py::test_package_to_tabs_reader_nonempty",
    "tests/portal/test_package_to_tabs_contract.py::test_package_to_tabs_source_links_reviewed",
    "tests/portal/test_package_to_tabs_contract.py::test_package_to_tabs_shlokas_not_fake_pending",
    "tests/portal/test_public_rights_contract.py::test_public_reader_rights_section_contract",
    "tests/portal/test_public_rights_contract.py::test_public_web_manifest_rights_contract",
    "tests/portal/test_v11_safety_baseline.py::test_stories_001_007_file_hashes_match_baseline",
    "tests/test_launch_story_hash_guard.py::test_story_beyond_public_ceiling_absent_from_output",
    "tests/test_poster_text_glyphs.py::test_already_credited_poster_is_not_accepted_as_a_master",
    "tests/test_poster_text_glyphs.py::test_band_and_corrected_chapters_are_discovered",
    "tests/test_poster_text_glyphs.py::test_story_007_poster_caption_keeps_its_diacritics",
    "tests/test_poster_text_glyphs.py::test_story_009_poster_shows_the_expected_devanagari_transliteration",
    "tests/test_poster_text_glyphs.py::test_text_less_posters_are_not_misdecomposed",
    "tests/test_publication_copyright.py::test_retrofitted_packages_have_rights_and_exact_eight",
    "tests/test_unicode_printable_copyright.py::test_public_packages_version_and_exact_eight",
    "tests/test_unicode_printable_copyright.py::test_public_pdf_has_footer_on_all_activity_pages",
    "tests/test_unicode_printable_copyright.py::test_story_beyond_public_ceiling_absent_from_public_content",
} | {
    f"tests/test_launch_story_hash_guard.py::test_launch_story_hashes_unchanged[{n:03d}]"
    for n in range(1, 10)
} | {
    f"tests/test_poster_text_glyphs.py::test_poster_text_bands_contain_no_missing_glyph_boxes[{chapter}]"
    for chapter in BAND_CHAPTERS
} | {
    f"tests/test_poster_text_glyphs.py::{name}[{chapter}]"
    for chapter in CORRECTED_CHAPTERS
    for name in (
        "test_correction_history_records_poster_fix",
        "test_manifest_records_poster_text_rebuild",
        "test_unicode_poster_caption_band_uses_a_real_typeface",
        "test_unicode_poster_text_glyphs_are_covered",
        "test_unicode_poster_text_has_no_replacement_or_box_characters",
        "test_unicode_poster_text_is_not_transliterated",
        "test_unicode_poster_title_band_uses_a_real_typeface",
    )
} | {
    f"tests/test_poster_text_glyphs.py::{name}[007]"
    for name in (
        "test_narration_and_narrative_survive_the_correction",
        "test_only_poster_story_and_manifest_changed",
    )
} | {
    f"tests/test_production_gates_026_035.py::test_026_035_production_publishable[{n:03d}]"
    for n in range(26, 36)
} | {
    f"tests/test_production_gates_026_035.py::test_026_035_story_md_has_no_staging_process_wording[{n:03d}]"
    for n in range(26, 36)
} | {
    "tests/test_production_gates_026_035.py::test_030_senior_review_not_falsely_complete",
    "tests/test_production_gates_026_035.py::test_030_poster_child_safety_attestation",
    "tests/test_production_gates_026_035.py::test_029_poster_hash_matches_disk",
    "tests/test_production_gates_026_035.py::test_staging_eligibility_still_works_for_private_staging_gate",
}

# Needs output/_archive/pre-copyright/**: superseded devotional drafts that were
# never published and must not be published, so they exist only on operator
# workstations and are deliberately absent from CI.
EXPECTED_LOCAL_ARCHIVE = {
    "tests/test_poster_text_glyphs.py::test_old_story_007_poster_caption_specifically_fails",
    "tests/test_poster_text_glyphs.py::test_old_story_009_poster_specifically_fails",
    "tests/test_poster_text_glyphs.py::test_swap_backup_records_its_true_version",
    "tests/test_publication_copyright.py::test_retrofit_preserved_superseded_archives",
    "tests/test_unicode_printable_copyright.py::test_image_credit_strip_unicode_and_no_duplicate",
    "tests/test_unicode_printable_copyright.py::test_narrative_unchanged_before_rights",
    "tests/test_unicode_printable_copyright.py::test_pdf_rights_page_preserves_bhava_and_footer_every_page",
} | {
    f"tests/test_launch_story_hash_guard.py::test_pre_copyright_archive_preserved[{n:03d}]"
    for n in range(1, 10)
} | {
    f"tests/test_launch_story_hash_guard.py::test_prior_2_1_0_archive_preserved[{n:03d}]"
    for n in range(1, 10)
} | {
    f"tests/test_poster_text_glyphs.py::{name}[{n:03d}]"
    for n in range(1, 10)
    for name in (
        "test_credit_strip_does_not_obstruct_sacred_artwork",
        "test_poster_has_exactly_one_credit_strip",
    )
} | {
    f"tests/test_poster_text_glyphs.py::test_superseded_archive_is_intact_and_correctly_labelled[{chapter}]"
    for chapter in CORRECTED_CHAPTERS
} | {
    f"tests/test_poster_text_glyphs.py::test_superseded_poster_with_box_glyphs_is_rejected[{chapter}]"
    for chapter in CORRECTED_CHAPTERS
}

# Needs tracking/queue_state.csv: mutable scheduler state owned by the operator
# workstation. Equivalent logic is covered deterministically by
# test_coverage_non_skipping.py::test_next_pending_is_cart_breaking.
# Also includes private 021/022 package lock drift checks against local output/.
EXPECTED_LOCAL_RUNTIME = {
    "tests/portal/test_queue_guard.py::test_queue_001_025_done_public_baseline_and_private_boundary",
    "tests/portal/test_v11_safety_baseline.py::test_queue_public_baseline_complete_next_pending_after_025",
    "tests/test_coverage_non_skipping.py::test_live_queue_next_pending_after_public_ceiling",
    "tests/test_private_story_lock_021_022.py::test_private_lock_ledger_matches_local_packages_when_present",
    "tests/test_accepted_story_lock_023_025.py::test_accepted_lock_ledger_matches_local_packages_when_present",
    "tests/test_unicode_printable_copyright.py::test_queue_public_ceiling_and_private_batch_boundary",
}

EXPECTED = {
    "content_release": EXPECTED_CONTENT_RELEASE,
    "local_archive": EXPECTED_LOCAL_ARCHIVE,
    "local_runtime": EXPECTED_LOCAL_RUNTIME,
}


def _collect(marker: str) -> set[str]:
    env = dict(os.environ)
    api = str(ROOT / "apps" / "api")
    existing = env.get("PYTHONPATH", "")
    if api not in existing.split(os.pathsep):
        env["PYTHONPATH"] = os.pathsep.join([api, existing]) if existing else api
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--collect-only", "-m", marker],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if result.returncode not in (0, 5):
        raise AssertionError(f"Collection for -m {marker} failed:\n{result.stdout}\n{result.stderr}")
    return {
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if "::" in line and line.strip().startswith("tests/")
    }


@pytest.mark.parametrize("marker", sorted(EXPECTED))
def test_tier_membership_is_declared(marker: str) -> None:
    collected = _collect(marker)
    expected = EXPECTED[marker]
    added = collected - expected
    removed = expected - collected
    assert not added, (
        f"Tests newly marked '{marker}' must be justified in test_ci_tier_contract.py "
        f"before they stop running in ordinary CI: {sorted(added)}"
    )
    assert not removed, (
        f"Tests no longer marked '{marker}' must be removed from the census: {sorted(removed)}"
    )


def test_tiers_do_not_overlap() -> None:
    for left in EXPECTED:
        for right in EXPECTED:
            if left < right:
                assert not EXPECTED[left] & EXPECTED[right], (
                    f"{left} and {right} claim the same tests"
                )
