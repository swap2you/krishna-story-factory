"""Lossless narration chunking for OpenAI TTS input limits."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for reconstruction equality checks."""
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


@dataclass(frozen=True, slots=True)
class NarrationChunk:
    sequence: int
    text: str
    char_count: int
    word_count: int
    text_sha256: str
    boundary: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class ChunkPlan:
    original_normalized: str
    original_sha256: str
    reconstructed: str
    reconstructed_sha256: str
    reconstruction_equal: bool
    chunks: tuple[NarrationChunk, ...]
    max_input_chars: int


def chunk_narration(text: str, *, max_input_chars: int = 3600) -> ChunkPlan:
    """Split narration losslessly: paragraph → sentence → clause → hard split.

    Chunks are contiguous, non-overlapping slices of the normalized source.
    Joining chunk texts reconstructs the exact normalized source.
    """
    if max_input_chars < 64:
        raise ValueError("max_input_chars must be at least 64")
    normalized = normalize_whitespace(text)
    if not normalized:
        raise ValueError("Narration text is empty after normalization.")
    original_sha = sha256_text(normalized)

    cut_points, cut_kinds = _preferred_cut_points(normalized)
    ranges = _pack_units(normalized, cut_points, cut_kinds, max_input_chars)

    chunks: list[NarrationChunk] = []
    for idx, (start, end, boundary) in enumerate(ranges, start=1):
        piece = normalized[start:end]
        if not piece:
            raise ValueError(f"Empty chunk at sequence {idx}")
        if not piece.strip():
            raise ValueError(f"Whitespace-only chunk at sequence {idx}")
        if len(piece) > max_input_chars:
            raise ValueError(f"Chunk {idx} length {len(piece)} exceeds max_input_chars={max_input_chars}")
        chunks.append(
            NarrationChunk(
                sequence=idx,
                text=piece,
                char_count=len(piece),
                word_count=len(re.findall(r"\S+", piece)),
                text_sha256=sha256_text(piece),
                boundary=boundary,
                start=start,
                end=end,
            )
        )

    if not chunks or chunks[0].start != 0 or chunks[-1].end != len(normalized):
        raise ValueError("Chunk ranges do not cover the full narration.")
    for i in range(1, len(chunks)):
        if chunks[i].start != chunks[i - 1].end:
            raise ValueError("Chunk ranges are not contiguous.")

    reconstructed = "".join(c.text for c in chunks)
    reconstructed_norm = normalize_whitespace(reconstructed)
    if reconstructed != normalized or reconstructed_norm != normalized:
        raise ValueError("Chunk reconstruction differs from normalized source.")
    reconstructed_sha = sha256_text(reconstructed)
    if reconstructed_sha != original_sha:
        raise ValueError("Chunk reconstruction SHA mismatch.")

    return ChunkPlan(
        original_normalized=normalized,
        original_sha256=original_sha,
        reconstructed=reconstructed,
        reconstructed_sha256=reconstructed_sha,
        reconstruction_equal=True,
        chunks=tuple(chunks),
        max_input_chars=max_input_chars,
    )


def _preferred_cut_points(text: str) -> tuple[list[int], dict[int, str]]:
    """Return candidate cut indices (end of a unit) with preferred boundary kind."""
    cuts: dict[int, str] = {len(text): "full"}
    for match in re.finditer(r"\n\n", text):
        cuts[match.end()] = "paragraph"
    for match in re.finditer(r"[.!?][\"')\]]*(?:\s+|$)", text):
        cuts.setdefault(match.end(), "sentence")
    for match in re.finditer(r"[,:;][\"')\]]*(?:\s+|$)", text):
        cuts.setdefault(match.end(), "clause")
    for match in re.finditer(r"\s+", text):
        cuts.setdefault(match.end(), "hard")
    ordered = sorted(c for c in cuts if 0 < c <= len(text))
    if not ordered or ordered[-1] != len(text):
        ordered.append(len(text))
        cuts[len(text)] = "full"
    return ordered, cuts


def _pack_units(
    text: str,
    cut_points: list[int],
    cut_kinds: dict[int, str],
    max_input_chars: int,
) -> list[tuple[int, int, str]]:
    if len(text) <= max_input_chars:
        return [(0, len(text), "full")]

    ranges: list[tuple[int, int, str]] = []
    start = 0
    while start < len(text):
        limit = start + max_input_chars
        if limit >= len(text):
            ranges.append((start, len(text), cut_kinds.get(len(text), "full")))
            break

        candidates = [c for c in cut_points if start < c <= limit]
        if not candidates:
            end = limit
            ranges.append((start, end, "hard"))
            start = end
            continue

        def rank_of(cut: int) -> int:
            kind = cut_kinds.get(cut, "hard")
            return {"paragraph": 0, "sentence": 1, "clause": 2, "hard": 3, "full": 0}.get(kind, 4)

        best_rank = min(rank_of(c) for c in candidates)
        end = max(c for c in candidates if rank_of(c) == best_rank)
        kind = cut_kinds.get(end, "hard")
        ranges.append((start, end, kind))
        start = end

    return ranges
