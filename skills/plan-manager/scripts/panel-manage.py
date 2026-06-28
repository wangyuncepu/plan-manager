#!/usr/bin/env python3
"""Panel registry and runner for plan-manager.

Panels are script-backed dashboards. Fixed panels are built in; saved panels live in
~/.claude/plan-manager/panels.json. Mutating saved panels is dry-run by default;
pass --apply to write.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, maybe_apply


CONFIG_PATH = Path.home() / ".claude" / "plan-manager" / "config.json"
PANELS_PATH = Path.home() / ".claude" / "plan-manager" / "panels.json"
SCRIPT_DIR = Path(__file__).resolve().parent


DEFAULT_REGISTRY = {
    "version": "1.0.0",
    "fixed": {
        "config": {
            "title": "Config Panel",
            "script": "config-panel.py",
            "args": ["--lang", "$LANG"],
            "description": "plan-manager 配置看板",
        },
        "overview": {
            "title": "Project Overview",
            "script": "project-overview.py",
            "args": ["--root", "$ROOT", "--lang", "$LANG"],
            "description": "全局项目总览",
        },
        "projects": {
            "title": "Project CRUD List",
            "script": "project-manage.py",
            "args": ["list", "--root", "$ROOT"],
            "description": "项目 CRUD 列表（轻量，不含 session/remote/建议）",
        },
        "tasks": {
            "title": "Task List",
            "script": "task-manage.py",
            "args": ["list", "--root", "$ROOT"],
            "description": "全部任务列表",
        },
        "github-status": {
            "title": "GitHub Manage Status",
            "script": "github-manage.sh",
            "args": ["status", "--root", "$ROOT", "--owner", "$GITHUB_OWNER"],
            "description": "GitHub 管理入口的远程状态",
        },
        "ready-queue": {
            "title": "Ready Queue",
            "script": "ready-queue.py",
            "args": ["--root", "$ROOT"],
            "description": "可执行任务队列",
        },
        "remote": {
            "title": "GitHub Remote Panel",
            "script": "github-verify.py",
            "args": ["--root", "$ROOT", "--owner", "$GITHUB_OWNER", "--lang", "$LANG"],
            "description": "GitHub remote 状态",
        },
        "trash": {
            "title": "Trash Panel",
            "script": "trash-manage.py",
            "args": ["list", "--root", "$ROOT"],
            "description": "软删除项目/任务",
        },
        "panels": {
            "title": "Panel Manager",
            "script": "panel-manage.py",
            "args": ["list"],
            "description": "看板管理看板",
        },
    },
    "saved": {},
}


def read_json(path: Path, default: dict) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else default
    except (OSError, json.JSONDecodeError):
        return default


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def config() -> dict:
    return read_json(CONFIG_PATH, {})


def registry() -> dict:
    data = read_json(PANELS_PATH, DEFAULT_REGISTRY)
    fixed = DEFAULT_REGISTRY["fixed"] | data.get("fixed", {})
    saved = data.get("saved", {}) if isinstance(data.get("saved", {}), dict) else {}
    return {"version": data.get("version", "1.0.0"), "fixed": fixed, "saved": saved}


def save_registry(data: dict) -> None:
    fixed_saved_only = {"version": data.get("version", "1.0.0"), "fixed": DEFAULT_REGISTRY["fixed"], "saved": data.get("saved", {})}
    atomic_write(PANELS_PATH, fixed_saved_only)


def context() -> dict:
    cfg = config()
    github = cfg.get("github") if isinstance(cfg.get("github"), dict) else {}
    return {
        "$ROOT": cfg.get("root", ""),
        "$LANG": cfg.get("language", "zh"),
        "$GITHUB_OWNER": github.get("owner", ""),
    }


def expand_args(args: list[str]) -> list[str]:
    ctx = context()
    return [ctx.get(arg, arg) for arg in args]


def panel_lookup(name: str) -> tuple[str, dict]:
    data = registry()
    if name in data["fixed"]:
        return "fixed", data["fixed"][name]
    if name in data["saved"]:
        return "saved", data["saved"][name]
    die(f"panel not found: {name}")


def validate_panel(panel: dict) -> None:
    for key in ("title", "script", "args", "description"):
        if key not in panel:
            die(f"missing panel field: {key}")
    if not isinstance(panel["args"], list):
        die("panel args must be a JSON array")
    if "/" in panel["script"] or ".." in panel["script"]:
        die(f"panel script must be a bare filename in scripts/: {panel['script']}")
    script_path = (SCRIPT_DIR / panel["script"]).resolve()
    if script_path.parent != SCRIPT_DIR:
        die(f"panel script outside scripts dir: {panel['script']}")
    if not script_path.exists():
        die(f"panel script missing: {script_path}")


def cmd_list(_args) -> None:
    data = registry()
    print("# Panel Manager")
    print()
    print("| Type | Name | Title | Script | Description |")
    print("|------|------|-------|--------|-------------|")
    for kind in ("fixed", "saved"):
        for name, panel in sorted(data[kind].items()):
            print(f"| {kind} | {name} | {panel.get('title', '')} | {panel.get('script', '')} | {panel.get('description', '')} |")


def cmd_show(args) -> None:
    kind, panel = panel_lookup(args.name)
    print(json.dumps({"type": kind, args.name: panel}, ensure_ascii=False, indent=2))


def run_panel(panel: dict, extra_args: list[str]) -> int:
    validate_panel(panel)
    script_path = SCRIPT_DIR / panel["script"]
    cmd = [str(script_path)] + expand_args(panel["args"]) + extra_args
    proc = subprocess.run(cmd, text=True, check=False)
    return proc.returncode


def cmd_run(args) -> None:
    _, panel = panel_lookup(args.name)
    raise SystemExit(run_panel(panel, args.extra or []))


def parse_args_json(value: str) -> list[str]:
    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        die(f"invalid args JSON: {exc}")
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        die("--args must be a JSON array of strings")
    return data


def cmd_add(args) -> None:
    data = registry()
    if args.name in data["fixed"]:
        die("cannot override fixed panel")
    panel = {"title": args.title, "script": args.script, "args": parse_args_json(args.args), "description": args.description}
    validate_panel(panel)

    def apply_add() -> None:
        latest = registry()
        latest.setdefault("saved", {})[args.name] = panel
        save_registry(latest)

    maybe_apply(args.apply, f"save panel {args.name}", apply_add)


def cmd_remove(args) -> None:
    data = registry()
    if args.name not in data.get("saved", {}):
        die(f"saved panel not found: {args.name}")

    def apply_remove() -> None:
        latest = registry()
        latest.get("saved", {}).pop(args.name, None)
        save_registry(latest)

    maybe_apply(args.apply, f"remove saved panel {args.name}", apply_remove)


def cmd_generate(args) -> None:
    panel = {"title": "Temporary Panel", "script": args.script, "args": parse_args_json(args.args), "description": "temporary"}
    raise SystemExit(run_panel(panel, args.extra or []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage plan-manager panels")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show")
    p.add_argument("name")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("run")
    p.add_argument("name")
    p.add_argument("extra", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("add")
    p.add_argument("name")
    p.add_argument("--script", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--args", required=True)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("remove")
    p.add_argument("name")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("generate")
    p.add_argument("--script", required=True)
    p.add_argument("--args", required=True)
    p.add_argument("extra", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_generate)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
