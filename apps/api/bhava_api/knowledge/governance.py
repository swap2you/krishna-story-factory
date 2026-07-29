"""Publication gates for Knowledge resources."""
from __future__ import annotations

from dataclasses import dataclass


CONFIDENTIAL_PATTERNS = (
    "gayatri mantra text",
    "initiation mantra",
    "nyasa sequence",
    "restricted arcana",
)


@dataclass
class GateResult:
    ok: bool
    reasons: list[str]


def evaluate_publication(resource: dict) -> GateResult:
    reasons: list[str] = []
    rights = (resource.get("rights") or {}).get("status")
    if rights not in {"cleared", "bbt_authorized", "public_domain", "steward_owned"}:
        reasons.append("unknown_or_missing_rights")
    if resource.get("contains_sacred_text") and not resource.get("scriptural_reviewer"):
        reasons.append("unreviewed_sacred_text")
    if resource.get("confidential") is True:
        reasons.append("confidential_content")
    body = f"{resource.get('title', '')}\n{resource.get('body', '')}".lower()
    if any(p in body for p in CONFIDENTIAL_PATTERNS):
        reasons.append("confidential_pattern_detected")
    if resource.get("fabricated_citation") is True:
        reasons.append("fabricated_citation")
    if not resource.get("required_reviewer_completed"):
        reasons.append("missing_required_reviewer")
    tier = resource.get("source_tier")
    if tier in {None, "", "D"} and resource.get("lifecycle") in {"approved", "published"}:
        reasons.append("discovery_only_source_cannot_publish")
    return GateResult(ok=not reasons, reasons=reasons)
