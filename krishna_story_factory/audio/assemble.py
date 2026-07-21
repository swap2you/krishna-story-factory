"""Deterministic MP3 assembly for chunked OpenAI TTS output."""
from __future__ import annotations

import hashlib
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def resolve_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"FFmpeg is required to assemble chunked narration: {exc}") from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def assemble_mp3_chunks(
    chunk_paths: list[Path],
    output_path: Path,
    *,
    pause_ms: int = 280,
) -> dict:
    """Concatenate chunk MP3s with a short natural pause between chunks.

    Writes atomically: assemble to a temp file, validate, then replace output_path.
    """
    if not chunk_paths:
        raise ValueError("No chunk paths provided for assembly.")
    for path in chunk_paths:
        if not path.exists() or path.stat().st_size < 100:
            raise ValueError(f"Missing or tiny chunk audio: {path}")

    ffmpeg = resolve_ffmpeg()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ksf_tts_assemble_") as tmp:
        tmp_dir = Path(tmp)
        silence = tmp_dir / "pause.mp3"
        if len(chunk_paths) > 1 and pause_ms > 0:
            _make_silence_mp3(ffmpeg, silence, pause_ms=pause_ms)
        list_file = tmp_dir / "concat.txt"
        lines: list[str] = []
        for idx, chunk in enumerate(chunk_paths):
            lines.append(f"file '{_ffmpeg_path(chunk)}'")
            if idx < len(chunk_paths) - 1 and silence.exists():
                lines.append(f"file '{_ffmpeg_path(silence)}'")
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        staged = tmp_dir / "assembled.mp3"
        cmd = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(staged),
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if completed.returncode != 0 or not staged.exists() or staged.stat().st_size < 500:
            # Re-encode fallback when stream copy fails across chunk encodings.
            cmd_re = [
                ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "128k",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(staged),
            ]
            completed = subprocess.run(cmd_re, capture_output=True, text=True, check=False)
            if completed.returncode != 0 or not staged.exists() or staged.stat().st_size < 500:
                detail = (completed.stderr or completed.stdout or "")[-500:]
                raise RuntimeError(f"FFmpeg assembly failed: {detail}")

        audio_bytes = staged.read_bytes()
        tmp_out = output_path.with_suffix(output_path.suffix + ".partial")
        tmp_out.write_bytes(audio_bytes)
        tmp_out.replace(output_path)

    return {
        "path": str(output_path),
        "bytes": len(audio_bytes),
        "sha256": sha256_bytes(audio_bytes),
        "chunk_count": len(chunk_paths),
        "pause_ms": pause_ms if len(chunk_paths) > 1 else 0,
    }


def _make_silence_mp3(ffmpeg: str, path: Path, *, pause_ms: int) -> None:
    seconds = max(0.05, pause_ms / 1000.0)
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"anullsrc=r=44100:cl=mono",
        "-t",
        f"{seconds:.3f}",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "128k",
        str(path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or not path.exists():
        raise RuntimeError(f"Failed to synthesize inter-chunk silence: {(completed.stderr or '')[-300:]}")


def _ffmpeg_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", r"'\''")
