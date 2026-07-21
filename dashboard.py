from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import read_next_pending

PROJECT_ROOT = Path(__file__).resolve().parent
SERIES_PATH = PROJECT_ROOT / "input" / "series_plan.csv"
STORY_LOG = PROJECT_ROOT / "tracking" / "story_log.csv"
SEND_LOG = PROJECT_ROOT / "tracking" / "send_log.csv"
STORAGE_LOG = PROJECT_ROOT / "tracking" / "storage_log.csv"
OUTPUT_ROOT = PROJECT_ROOT / "output"

settings = load_settings(PROJECT_ROOT)

st.set_page_config(page_title="Krishna Book Bedtime", layout="wide")
st.title("Krishna Story Factory")
st.subheader("Project: Krishna Book Bedtime")
st.caption("CLI is source of truth. Dashboard is optional.")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


def run_cli(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "run_daily_story.py", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=900,
    )
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def latest_output_dir() -> Path | None:
    if not OUTPUT_ROOT.exists():
        return None
    folders = sorted([p for p in OUTPUT_ROOT.iterdir() if p.is_dir()], reverse=True)
    return folders[0] if folders else None


def mp3_info(path: Path) -> dict[str, str]:
    if not path.exists():
        return {"size": "missing", "duration": "missing"}
    size = str(path.stat().st_size)
    try:
        from mutagen.mp3 import MP3

        duration = f"{float(MP3(path).info.length):.1f}s"
    except Exception:
        duration = "unknown"
    return {"size": size, "duration": duration}


series_df = read_csv(SERIES_PATH)
story_log_df = read_csv(STORY_LOG)
send_log_df = read_csv(SEND_LOG)
storage_log_df = read_csv(STORAGE_LOG)
pending_plan = read_next_pending(PROJECT_ROOT)
latest_dir = latest_output_dir()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Project", "krishna_book_bedtime")
with c2:
    pending = int((series_df.get("status", pd.Series(dtype=str)).astype(str).str.lower() == "pending").sum()) if not series_df.empty else 0
    st.metric("Pending", pending)
with c3:
    st.metric("WhatsApp template", settings.whatsapp_template_name)
with c4:
    st.metric("Drive upload", "enabled" if settings.google_drive_upload_enabled else "disabled")

st.header("Next pending story")
if pending_plan:
    st.json(
        {
            "chapter_no": pending_plan.chapter_no,
            "slug": pending_plan.slug,
            "title": pending_plan.title,
            "source_reference": pending_plan.source_reference,
        }
    )
else:
    st.info("No pending stories.")

st.header("Latest output")
if latest_dir:
    st.write(str(latest_dir.relative_to(PROJECT_ROOT)))
    manifest_path = latest_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        package = manifest.get("package", {})
        st.write(
            {
                "title": manifest.get("title"),
                "quality": manifest.get("quality", {}).get("status"),
                "package_link": package.get("package_link"),
                "drive_status": package.get("drive_status"),
                "whatsapp_template": manifest.get("whatsapp", {}).get("template_name"),
            }
        )
        activity = manifest.get("activity", {})
        parent_key = activity.get("parent_answer_key") or {}
        with st.expander("Parent Answer Key", expanded=False):
            if parent_key:
                st.json(parent_key)
                from krishna_story_factory.content.parent_answer_key import render_parent_answer_key_text

                key_text = render_parent_answer_key_text(parent_key, title=activity.get("title") or manifest.get("title") or "")
                st.code(key_text)
                st.download_button(
                    "Download Parent Key",
                    data=key_text,
                    file_name=f"parent_answer_key_{manifest.get('chapter_no', 'story')}.txt",
                    mime="text/plain",
                )
            else:
                st.info("No parent_answer_key in this manifest yet.")
    images = [p.name for p in latest_dir.glob("*.png")]
    st.write("Images:", images)
    audio = mp3_info(latest_dir / "narration.mp3")
    st.write("Audio:", audio)
else:
    st.info("No output folders yet.")

st.header("Model flags")
st.write(
    {
        "OPENAI_TEXT_ENABLED": settings.openai_text_enabled,
        "OPENAI_IMAGE_ENABLED": settings.openai_image_enabled,
        "ELEVENLABS_ENABLED": settings.elevenlabs_enabled,
        "WHATSAPP_SEND_ENABLED": settings.whatsapp_send_enabled,
        "GOOGLE_DRIVE_UPLOAD_ENABLED": settings.google_drive_upload_enabled,
    }
)

st.header("Run controls")
b1, b2 = st.columns(2)
with b1:
    if st.button("Run test package"):
        code, output = run_cli(["--mode", "test", "--force"])
        st.code(output)
        st.success("Done" if code == 0 else "Failed")
with b2:
    if st.checkbox("Confirm prod run") and st.button("Run prod with force"):
        code, output = run_cli(["--mode", "prod", "--force"])
        st.code(output)
        st.success("Done" if code == 0 else "Failed")

st.header("Story log")
st.dataframe(story_log_df.tail(20) if not story_log_df.empty else pd.DataFrame(), use_container_width=True)

st.header("Send log")
st.dataframe(send_log_df.tail(10) if not send_log_df.empty else pd.DataFrame(), use_container_width=True)

st.header("Storage log")
st.dataframe(storage_log_df.tail(10) if not storage_log_df.empty else pd.DataFrame(), use_container_width=True)

st.header("Queue")
if not series_df.empty:
    edited = st.data_editor(series_df, use_container_width=True, num_rows="dynamic")
    if st.button("Save series_plan.csv"):
        edited.to_csv(SERIES_PATH, index=False)
        st.success("Saved.")
