from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SERIES_PATH = PROJECT_ROOT / "input" / "series_plan.csv"
LOG_PATH = PROJECT_ROOT / "tracking" / "story_log.csv"
OUTPUT_ROOT = PROJECT_ROOT / "output"

st.set_page_config(page_title="Krishna Story Factory", layout="wide")
st.title("Krishna Story Factory")
st.caption("Local dashboard for queue, generation, quality status, and delivery mode.")


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
        timeout=600,
    )
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()

series_df = read_csv(SERIES_PATH)
log_df = read_csv(LOG_PATH)

col1, col2, col3 = st.columns(3)
with col1:
    pending_count = int((series_df.get("status", pd.Series(dtype=str)).astype(str).str.lower() == "pending").sum()) if not series_df.empty else 0
    st.metric("Pending stories", pending_count)
with col2:
    generated_count = len(log_df) if not log_df.empty else 0
    st.metric("Run log rows", generated_count)
with col3:
    latest_status = log_df.iloc[-1]["status"] if not log_df.empty and "status" in log_df.columns else "N/A"
    st.metric("Latest run", latest_status)

st.header("Next pending story")
if series_df.empty:
    st.warning("No series_plan.csv found or file is empty.")
else:
    pending = series_df[series_df["status"].astype(str).str.lower() == "pending"] if "status" in series_df.columns else pd.DataFrame()
    if pending.empty:
        st.info("No pending stories.")
    else:
        st.dataframe(pending.head(1), use_container_width=True)

st.header("Run controls")
run_col1, run_col2, run_col3 = st.columns(3)
with run_col1:
    if st.button("Run test package"):
        code, output = run_cli(["--mode", "test", "--force"])
        st.code(output)
        st.success("Test run completed." if code == 0 else "Test run failed.")
with run_col2:
    confirm_prod = st.checkbox("I understand prod can call paid APIs and sender APIs")
    if st.button("Run prod package", disabled=not confirm_prod):
        code, output = run_cli(["--mode", "prod"])
        st.code(output)
        st.success("Prod run completed." if code == 0 else "Prod run failed.")
with run_col3:
    confirm_force = st.checkbox("Allow --force override")
    if st.button("Run prod with force", disabled=not (confirm_prod and confirm_force)):
        code, output = run_cli(["--mode", "prod", "--force"])
        st.code(output)
        st.success("Forced prod run completed." if code == 0 else "Forced prod run failed.")

st.header("Story queue editor")
if not series_df.empty:
    edited = st.data_editor(series_df, use_container_width=True, num_rows="dynamic")
    if st.button("Save series_plan.csv"):
        save_csv(SERIES_PATH, edited)
        st.success("Saved input/series_plan.csv")
else:
    st.info("Create input/series_plan.csv first by running the CLI once.")

st.header("Story log")
if log_df.empty:
    st.info("No story log yet.")
else:
    st.dataframe(log_df.tail(50), use_container_width=True)

st.header("Generated output folders")
if OUTPUT_ROOT.exists():
    folders = sorted([p for p in OUTPUT_ROOT.iterdir() if p.is_dir()], reverse=True)
    for folder in folders[:20]:
        st.write(str(folder.relative_to(PROJECT_ROOT)))
else:
    st.info("No output folder yet.")
