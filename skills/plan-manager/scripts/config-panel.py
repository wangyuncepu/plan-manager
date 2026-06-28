#!/usr/bin/env python3
"""Config panel for plan-manager."""

import argparse
import json
from pathlib import Path


CONFIG_PATH = Path.home() / ".claude" / "plan-manager" / "config.json"
PANELS_PATH = Path.home() / ".claude" / "plan-manager" / "panels.json"


CORE_MEANING_ZH = {
    "root": "管理根目录",
    "role": "当前角色",
    "language": "输出语言",
    "parallelism": "并发项目数",
    "autonomy": "自主程度",
    "max_iterations_per_task": "单任务迭代上限",
    "overnight": "过夜模式",
}

CORE_MEANING_EN = {
    "root": "managed root",
    "role": "current role",
    "language": "output language",
    "parallelism": "parallel projects",
    "autonomy": "autonomy level",
    "max_iterations_per_task": "max iterations per task",
    "overnight": "overnight mode",
}


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value) if str(value) else "—"


def print_core(config: dict, lang: str) -> None:
    meanings = CORE_MEANING_ZH if lang == "zh" else CORE_MEANING_EN
    print("## Core Config")
    print("| Key | Value | Meaning |")
    print("|-----|-------|---------|")
    for key in ["root", "role", "language", "parallelism", "autonomy", "max_iterations_per_task", "overnight"]:
        print(f"| {key} | {fmt(config.get(key))} | {meanings[key]} |")
    print()


def print_github(config: dict) -> None:
    github = config.get("github") if isinstance(config.get("github"), dict) else {}
    print("## GitHub Config")
    print("| Key | Value |")
    print("|-----|-------|")
    for key in ["enabled", "owner", "repo_match", "check_remote"]:
        print(f"| {key} | {fmt(github.get(key))} |")
    print()


def print_panel_registry() -> None:
    panels = read_json(PANELS_PATH)
    fixed = panels.get("fixed") if isinstance(panels.get("fixed"), dict) else {}
    saved = panels.get("saved") if isinstance(panels.get("saved"), dict) else {}
    # fixed panels may be implicit in panel-manage.py even when panels.json missing.
    print("## Panel Registry")
    print("| Type | Count |")
    print("|------|------:|")
    print(f"| fixed | {len(fixed)} |")
    print(f"| saved | {len(saved)} |")


def main() -> int:
    ap = argparse.ArgumentParser(description="Show plan-manager config panel")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    args = ap.parse_args()

    config = read_json(CONFIG_PATH)
    print("# Config Panel")
    print()
    print_core(config, args.lang)
    print_github(config)
    print_panel_registry()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
