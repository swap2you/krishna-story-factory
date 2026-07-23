#!/usr/bin/env python3
"""Cross-platform Bhāva multi-instance port allocator and runtime helpers."""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WEB_RANGE = range(3000, 3100)
API_RANGE = range(8000, 8100)

INSTANCE_PRESETS: dict[str, tuple[int, int]] = {
    "default": (3000, 8000),
    "cursor": (3000, 8000),
    "cowork": (3001, 8001),
    "codex": (3002, 8002),
    "claude": (3003, 8003),
}

SUPPORTED_INSTANCES = frozenset(INSTANCE_PRESETS)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def instances_root(root: Path | None = None) -> Path:
    return (root or repo_root()) / ".bhava" / "instances"


def instance_dir(name: str, root: Path | None = None) -> Path:
    return instances_root(root) / _safe_name(name)


def runtime_path(name: str, root: Path | None = None) -> Path:
    return instance_dir(name, root) / "runtime.json"


def _safe_name(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in name.strip().lower())
    if not cleaned:
        raise ValueError("Instance name is required")
    return cleaned


def port_free(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def allocate_port(preferred: int, port_range: range, host: str = "127.0.0.1") -> int:
    candidates = [preferred] + [p for p in port_range if p != preferred]
    for port in candidates:
        if port_free(port, host=host):
            return port
    raise RuntimeError(f"No free port available in {port_range.start}-{port_range.stop - 1}")


def load_runtime(name: str, root: Path | None = None) -> dict[str, Any] | None:
    path = runtime_path(name, root)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError):
        return False
    return True


def instance_running(name: str, root: Path | None = None) -> bool:
    data = load_runtime(name, root)
    if not data:
        return False
    return pid_alive(data.get("web_pid")) or pid_alive(data.get("api_pid"))


def write_runtime(data: dict[str, Any], root: Path | None = None) -> Path:
    name = _safe_name(str(data["instance_name"]))
    path = runtime_path(name, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def allocate(instance: str, preferred_web: int | None, preferred_api: int | None) -> dict[str, Any]:
    name = _safe_name(instance)
    if name in INSTANCE_PRESETS:
        preset_web, preset_api = INSTANCE_PRESETS[name]
    else:
        preset_web, preset_api = 3000, 8000
    web_pref = preferred_web if preferred_web is not None else preset_web
    api_pref = preferred_api if preferred_api is not None else preset_api
    if web_pref not in WEB_RANGE:
        raise ValueError(f"Preferred web port {web_pref} outside {WEB_RANGE.start}-{WEB_RANGE.stop - 1}")
    if api_pref not in API_RANGE:
        raise ValueError(f"Preferred API port {api_pref} outside {API_RANGE.start}-{API_RANGE.stop - 1}")
    web_port = allocate_port(web_pref, WEB_RANGE)
    api_port = allocate_port(api_pref, API_RANGE)
    return {
        "instance_name": name,
        "web_port": web_port,
        "api_port": api_port,
        "web_url": f"http://127.0.0.1:{web_port}",
        "api_url": f"http://127.0.0.1:{api_port}",
        "preferred_web_port": web_pref,
        "preferred_api_port": api_pref,
        "collision": web_port != web_pref or api_port != api_pref,
    }


def list_instances(root: Path | None = None) -> list[dict[str, Any]]:
    base = instances_root(root)
    if not base.exists():
        return []
    rows: list[dict[str, Any]] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        data = load_runtime(child.name, root) or {"instance_name": child.name}
        data = dict(data)
        data["running"] = instance_running(child.name, root)
        rows.append(data)
    return rows


def wait_http(url: str, timeout_sec: float = 180.0) -> bool:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= int(response.status) < 500:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(1.5)
    return False


def cmd_allocate(args: argparse.Namespace) -> int:
    if instance_running(args.instance):
        existing = load_runtime(args.instance) or {}
        print(json.dumps({"error": "already_running", "runtime": existing}, indent=2))
        return 2
    result = allocate(args.instance, args.preferred_web, args.preferred_api)
    print(json.dumps(result, indent=2))
    return 0


def cmd_write_runtime(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read())
    payload.setdefault("started_at", datetime.now(timezone.utc).isoformat())
    path = write_runtime(payload)
    print(str(path))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    rows = list_instances()
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("No Bhāva instances registered.")
        return 0
    for row in rows:
        status = "RUNNING" if row.get("running") else "stopped"
        print(
            f"{row.get('instance_name')}: {status}  "
            f"web={row.get('web_url', '-')}  api={row.get('api_url', '-')}"
        )
    return 0


def cmd_running(args: argparse.Namespace) -> int:
    print("1" if instance_running(args.instance) else "0")
    return 0


def cmd_wait(args: argparse.Namespace) -> int:
    ok = wait_http(args.url, timeout_sec=args.timeout)
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bhāva multi-instance runtime helper")
    sub = parser.add_subparsers(dest="command", required=True)

    allocate_p = sub.add_parser("allocate", help="Reserve free web/API ports")
    allocate_p.add_argument("--instance", required=True)
    allocate_p.add_argument("--preferred-web", type=int, default=None)
    allocate_p.add_argument("--preferred-api", type=int, default=None)
    allocate_p.set_defaults(func=cmd_allocate)

    write_p = sub.add_parser("write-runtime", help="Write runtime.json")
    write_p.add_argument("--file", default=None)
    write_p.set_defaults(func=cmd_write_runtime)

    list_p = sub.add_parser("list", help="List registered instances")
    list_p.add_argument("--json", action="store_true")
    list_p.set_defaults(func=cmd_list)

    running_p = sub.add_parser("running", help="Exit 0 and print 1/0 if instance running")
    running_p.add_argument("--instance", required=True)
    running_p.set_defaults(func=cmd_running)

    wait_p = sub.add_parser("wait", help="Wait until an HTTP endpoint responds")
    wait_p.add_argument("--url", required=True)
    wait_p.add_argument("--timeout", type=float, default=180.0)
    wait_p.set_defaults(func=cmd_wait)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
