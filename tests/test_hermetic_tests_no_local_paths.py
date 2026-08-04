"""Guard: ordinary unit tests must not depend on local-only runtime paths."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

# Path-like literals that indicate a hermeticity violation.
# Applied to AST string *values* (no surrounding quotes) and raw source scans.
_FORBIDDEN_LITERAL = re.compile(
    r"""(?x)
    (?:^|[\s\"'`=(])output/[A-Za-z0-9_.-]
    |(?:^|[\s\"'`=(])work/(?:stories|tmp|runs)/
    |MyPilotDropbox
    |(?:^|[\s\"'`=(])C:\\Development
    |(?:^|[\s\"'`=(])C:/Development
    |(?:^|[\s\"'`=(])/Users/[A-Za-z]
    |(?:^|[\s\"'`=(])/home/[A-Za-z]
    """,
)

_ALLOWLIST_FILES = {
    "test_hermetic_tests_no_local_paths.py",
    "test_ci_tier_contract.py",
    "test_launch_story_hash_guard.py",
    "test_pilot_release_hash_evidence.py",
    "test_release_artifacts_001_006.py",
    "test_unicode_printable_copyright.py",
    "test_sample_first_pipeline.py",
    # Portal package probes that intentionally inspect local packages when present.
    "test_package_hash_guard.py",
    "test_package_to_tabs_contract.py",
    "test_v11_safety_baseline.py",
    # Private 021/022 lock drift probe (local_runtime) against operator packages.
    "test_private_story_lock_021_022.py",
}

_LOCAL_NAME_FRAGMENTS = {
    "output",
    "work",
    "MyPilotDropbox",
    "Dropbox",
}


def _is_ordinary_test_module(path: Path) -> bool:
    if path.name in _ALLOWLIST_FILES:
        return False
    text = path.read_text(encoding="utf-8")
    if re.search(r"pytestmark\s*=\s*pytest\.mark\.(local_archive|local_runtime)", text):
        return False
    return path.name.startswith("test_") and path.suffix == ".py"


def _const_str(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _name_id(node: ast.AST) -> str | None:
    return node.id if isinstance(node, ast.Name) else None


def _find_path_composition_violations(tree: ast.AST) -> list[str]:
    """Detect ROOT / 'output', Path('work') / 'stories', joinpath('output'), etc."""
    hits: list[str] = []
    rootish = {"ROOT", "PROJECT_ROOT", "REPO_ROOT", "repository_root"}

    def note(msg: str) -> None:
        hits.append(msg)

    for node in ast.walk(tree):
        # ROOT / "output"
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            right = _const_str(node.right)
            left_name = _name_id(node.left)
            if left_name in rootish and right in _LOCAL_NAME_FRAGMENTS:
                note(f"{left_name} / {right!r}")
            # Path("work") / "stories"
            if isinstance(node.left, ast.Call) and _name_id(node.left.func) == "Path":
                for arg in node.left.args:
                    val = _const_str(arg)
                    if val in {"work", "output"} or (val and "MyPilotDropbox" in val):
                        note(f"Path({val!r}) / ...")
            # (ROOT / "work") / "stories"
            if (
                right == "stories"
                and isinstance(node.left, ast.BinOp)
                and isinstance(node.left.op, ast.Div)
                and _const_str(node.left.right) == "work"
                and _name_id(node.left.left) in rootish
            ):
                note("ROOT / 'work' / 'stories'")

        # ROOT.joinpath("output")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "joinpath" and _name_id(node.func.value) in rootish:
                for arg in node.args:
                    val = _const_str(arg)
                    if val in _LOCAL_NAME_FRAGMENTS or (val and "MyPilotDropbox" in val):
                        note(f"ROOT.joinpath({val!r})")

        # Path("C:/Development/...") or Path("/Users/...")
        if isinstance(node, ast.Call) and _name_id(node.func) == "Path":
            for arg in node.args:
                val = _const_str(arg)
                if not val:
                    continue
                if val.startswith(("C:\\", "C:/", "/Users/", "/home/")) or "MyPilotDropbox" in val:
                    note(f"Path({val!r})")

    return hits


def _string_literals(tree: ast.AST) -> list[str]:
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
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for literal in _string_literals(tree):
            if _FORBIDDEN_LITERAL.search(literal):
                if "tests/fixtures/" in literal.replace("\\", "/"):
                    continue
                if literal.replace("\\", "/").startswith("fixtures/"):
                    continue
                violations.append(f"{rel}: literal {literal!r}")
        # Portal suite must stay fully hermetic — enforce AST compositions there.
        if "portal" in path.parts:
            for hit in _find_path_composition_violations(tree):
                violations.append(f"{rel}: {hit}")
    assert not violations, "Non-hermetic local path references:\n" + "\n".join(violations)


def test_ast_guard_detects_output_and_work_compositions() -> None:
    """Regression: compositions like ROOT / 'output' must be rejected by AST scan."""
    samples = {
        "ROOT / 'output'": "ROOT / \"output\"\n",
        "joinpath output": "ROOT.joinpath(\"output\")\n",
        "Path work stories": "Path(\"work\") / \"stories\"\n",
        "MyPilotDropbox": "ROOT / \"MyPilotDropbox\"\n",
    }
    for label, src in samples.items():
        tree = ast.parse(src)
        hits = _find_path_composition_violations(tree)
        assert hits, f"Expected AST violation for {label}, got none"


def test_forbidden_literal_matches_absolute_ast_values() -> None:
    """Absolute developer paths must match AST string values (no surrounding quotes)."""
    for value in (
        r"C:\Development\Workspace\example",
        "C:/Development/Workspace/example",
        "/Users/example/project",
        "/home/example/project",
        "MyPilotDropbox/bhava-production-ops",
    ):
        assert _FORBIDDEN_LITERAL.search(value), value
