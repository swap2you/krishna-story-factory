"""Guard: ordinary unit tests must not depend on local-only runtime paths."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

# Path-like literals that indicate a hermeticity violation.
# Match filesystem path usage, not prose that happens to contain the word.
_FORBIDDEN = re.compile(
    r"""(?x)
    (?:^|[\s\"'`=(])output/[A-Za-z0-9_.-]   # developer package tree path
    |(?:^|[\s\"'`=(])work/(?:stories|tmp|runs)/  # local worktree path
    |MyPilotDropbox
    |(?:[\"'])C:\\\\Development
    |(?:[\"'])C:/Development
    |(?:[\"'])/Users/[A-Za-z]
    """,
)

# Files allowed to mention output/ when they are explicitly local/archive gated
# or document absence of packages (still hermetic).
_ALLOWLIST_FILES = {
    "test_hermetic_tests_no_local_paths.py",  # this file
    "test_ci_tier_contract.py",
    "test_launch_story_hash_guard.py",
    "test_pilot_release_hash_evidence.py",
    "test_release_artifacts_001_006.py",
    "test_unicode_printable_copyright.py",
    "test_sample_first_pipeline.py",  # skips when package absent
}

_LOCAL_MARKERS = {"local_archive", "local_runtime", "slow", "content_release"}


def _is_ordinary_test_module(path: Path) -> bool:
    if path.name in _ALLOWLIST_FILES:
        return False
    if "portal" in path.parts and path.name.startswith("test_"):
        # Portal tests often use tmp_path fixtures; still scan but allow
        # output/ mentions only inside comments is handled by AST string scan.
        pass
    text = path.read_text(encoding="utf-8")
    # Skip modules that are exclusively local-marked at module level.
    if re.search(r"pytestmark\s*=\s*pytest\.mark\.(local_archive|local_runtime)", text):
        return False
    return path.name.startswith("test_") and path.suffix == ".py"


def _string_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append(node.value)
        elif isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    out.append(v.value)
    return out


def test_ordinary_tests_do_not_reference_local_runtime_paths() -> None:
    violations: list[str] = []
    for path in sorted(TESTS.rglob("test_*.py")):
        if not _is_ordinary_test_module(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for literal in _string_literals(path):
            if _FORBIDDEN.search(literal):
                # Allow fixture-relative paths under tests/fixtures/
                if "tests/fixtures/" in literal.replace("\\", "/"):
                    continue
                if literal.replace("\\", "/").startswith("fixtures/"):
                    continue
                violations.append(f"{rel}: {literal!r}")
    assert not violations, "Non-hermetic local path references:\n" + "\n".join(violations)
