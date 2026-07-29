"""Centralized publication identity, copyright notices, and work-manifest helpers."""

from .identity import PublicationIdentity, get_identity, load_identity
from .fonts import UnicodeFontError, resolve_unicode_fonts, validate_font_glyph_coverage
from .notices import (
    audio_notice_lines,
    compact_footer,
    draft_watermark,
    image_credit_line,
    rights_and_credits_markdown,
    standard_visual_notice,
    website_footer_lines,
)
from .work_manifest import (
    WORK_MANIFEST_SCHEMA_VERSION,
    build_story_rights_block,
    first_publication_year,
    validate_work_manifest,
)

__all__ = [
    "PublicationIdentity",
    "UnicodeFontError",
    "WORK_MANIFEST_SCHEMA_VERSION",
    "audio_notice_lines",
    "build_story_rights_block",
    "compact_footer",
    "draft_watermark",
    "first_publication_year",
    "get_identity",
    "image_credit_line",
    "load_identity",
    "resolve_unicode_fonts",
    "rights_and_credits_markdown",
    "standard_visual_notice",
    "validate_font_glyph_coverage",
    "validate_work_manifest",
    "website_footer_lines",
]
