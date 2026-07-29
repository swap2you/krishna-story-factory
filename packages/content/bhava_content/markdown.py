"""Strict allowlist sanitizer for HTML emitted by a Markdown renderer."""
from __future__ import annotations

import bleach

ALLOWED_TAGS = {
    "a", "blockquote", "br", "code", "em", "h1", "h2", "h3", "h4",
    "li", "ol", "p", "pre", "strong", "ul",
}
ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}
ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


def sanitize_markdown_html(html: str) -> str:
    """Remove executable markup while retaining simple rendered story content."""
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
