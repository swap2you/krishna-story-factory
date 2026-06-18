from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from krishna_story_factory.config import load_settings

PROJECT_ROOT = Path(__file__).resolve().parent
SERIES_PATH = PROJECT_ROOT / "input" / "series_plan.csv"
STORY_LOG = PROJECT_ROOT / "tracking" / "story_log.csv"
SEND_LOG = PROJECT_ROOT / "tracking" / "send_log.csv"
QUALITY_LOG = PROJECT_ROOT / "tracking" / "quality_log.csv"
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


def save_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_cli(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "run_daily_story.py", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=900,
    )
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


series_df = read_csv(SERIES_PATH)
story_log_df = read_csv(STORY_LOG)
send_log_df = read_csv(SEND_LOG)
quality_log_df = read_csv(QUALITY_LOG)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Library", "Krishna Book")
with c2:
    pending = int((series_df.get("status", pd.Series(dtype=str)).astype(str).str.lower() == "pending").sum()) if not series_df.empty else 0
    st.metric("Pending", pending)
with c3:
    st.metric("Runs logged", len(story_log_df))
with c4:
    st.metric("Sender", settings.whatsapp_sender_type)

st.header("Model flags")
st.write(
    {
        "OPENAI_TEXT_ENABLED": settings.openai_text_enabled,
        "OPENAI_IMAGE_ENABLED": settings.openai_image_enabled,
        "ELEVENLABS_ENABLED": settings.elevenlabs_enabled,
        "WHATSAPP_SEND_ENABLED": settings.whatsapp_send_enabled,
        "WHATSAPP_SENDER_TYPE": settings.whatsapp_sender_type,
    }
)

st.header("Next pending story")
if series_df.empty:
    st.warning("No series_plan.csv found.")
else:
    pending_rows = series_df[series_df["status"].astype(str).str.lower() == "pending"] if "status" in series_df.columns else pd.DataFrame()
    if pending_rows.empty:
        st.info("No pending stories.")
    else:
        st.dataframe(pending_rows.head(1), use_container_width=True)

st.header("Queue")
if not series_df.empty:
    edited = st.data_editor(series_df, use_container_width=True, num_rows="dynamic")
    if st.button("Save series_plan.csv"):
        save_csv(SERIES_PATH, edited)
        st.success("Saved.")

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
st.dataframe(story_log_df.tail(30) if not story_log_df.empty else pd.DataFrame(), use_container_width=True)

st.header("Send log")
st.dataframe(send_log_df.tail(30) if not send_log_df.empty else pd.DataFrame(), use_container_width=True)

st.header("Quality log")
st.dataframe(quality_log_df.tail(30) if not quality_log_df.empty else pd.DataFrame(), use_container_width=True)

st.header("Generated outputs")
if OUTPUT_ROOT.exists():
    for folder in sorted([p for p in OUTPUT_ROOT.iterdir() if p.is_dir()], reverse=True)[:20]:
        st.write(str(folder.relative_to(PROJECT_ROOT)))
