#!/usr/bin/env python3
"""Help panel for plan-manager: command index + role-aware guided flows."""

import argparse
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude" / "plan-manager" / "config.json"
SK = "${CLAUDE_SKILL_DIR}/scripts"


def read_config() -> dict:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


STRATEGIST_FLOW = {
    "zh": [
        "/plan-manager                 查看全局总览（panel: overview）",
        "/plan-manager <project>       打开项目面板",
        "analyze <project>             深入分析现状、缺口、方向",
        "create project <name>         新建项目（脚本 dry-run → --apply）",
        "add task to <project>         加任务",
        "make plan for <ID>            起草计划 → 你审批",
        "switch to executor            切到执行角色开始干活",
    ],
    "en": [
        "/plan-manager                 global overview (panel: overview)",
        "/plan-manager <project>       open a project panel",
        "analyze <project>             deep state/gap/direction analysis",
        "create project <name>         new project (dry-run → --apply)",
        "add task to <project>         add a task",
        "make plan for <ID>            draft a plan → you approve",
        "switch to executor            switch role to start working",
    ],
}

EXECUTOR_FLOW = {
    "zh": [
        "/plan-manager ready-queue     看就绪队列",
        "switch to executor            切到执行角色",
        "execute / execute N projects  执行就绪任务",
        "auto                          连续执行直到无就绪任务",
        "continue / resume             崩溃/中断后断点续跑",
        "complete <ID> / block <ID>    手动改任务状态（脚本）",
    ],
    "en": [
        "/plan-manager ready-queue     view ready queue",
        "switch to executor            switch to executor role",
        "execute / execute N projects  run ready tasks",
        "auto                          run until no ready tasks remain",
        "continue / resume             resume from checkpoint",
        "complete <ID> / block <ID>    manual task state change (script)",
    ],
}

PANELS = [
    ("config", "配置看板", "config panel"),
    ("overview", "全局项目总览", "global overview"),
    ("projects", "项目元数据列表", "project metadata list"),
    ("tasks", "全部任务", "all tasks"),
    ("ready-queue", "可执行任务队列", "ready task queue"),
    ("remote", "GitHub remote 验证", "GitHub remote verify"),
    ("github-status", "GitHub 管理状态", "GitHub manage status"),
    ("trash", "软删除项目/任务", "trashed projects/tasks"),
    ("panels", "看板管理看板", "panel manager"),
    ("help", "本帮助看板", "this help panel"),
]

SCENARIOS = {
    "zh": [
        ("看现状", "/plan-manager  或  panel-manage.py run overview"),
        ("建项目", "project-manage.py create --root <root> --name <name> [--apply]"),
        ("加任务", "task-manage.py create --root <root> --project <p> --title <t> [--apply]"),
        ("执行任务", "switch to executor → execute / auto"),
        ("断点续跑", "continue"),
        ("找回误删", "trash-manage.py list → restore <name> --apply"),
        ("永久清理", "trash-manage.py purge <name> --force --apply"),
        ("改配置", "configure-plan-manager.sh ...  或  --show 查看"),
        ("固化看板", "panel-manage.py add <name> --script ... --args ... --apply"),
    ],
    "en": [
        ("See state", "/plan-manager  or  panel-manage.py run overview"),
        ("New project", "project-manage.py create --root <root> --name <name> [--apply]"),
        ("New task", "task-manage.py create --root <root> --project <p> --title <t> [--apply]"),
        ("Run tasks", "switch to executor → execute / auto"),
        ("Resume", "continue"),
        ("Undo delete", "trash-manage.py list → restore <name> --apply"),
        ("Purge", "trash-manage.py purge <name> --force --apply"),
        ("Configure", "configure-plan-manager.sh ...  or  --show"),
        ("Save a panel", "panel-manage.py add <name> --script ... --args ... --apply"),
    ],
}


def main() -> int:
    ap = argparse.ArgumentParser(description="plan-manager help panel")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    args = ap.parse_args()
    lang = args.lang
    cfg = read_config()
    role = cfg.get("role", "strategist")

    zh = lang == "zh"
    print("# Plan Manager — Help")
    print()
    print((f"当前角色: **{role}**" if zh else f"Current role: **{role}**"))
    print()

    flows = [("strategist", STRATEGIST_FLOW), ("executor", EXECUTOR_FLOW)]
    flows.sort(key=lambda f: f[0] != role)  # active role first

    head = "快速流程" if zh else "Quick flow"
    for name, flow in flows:
        marker = " ← 当前" if (zh and name == role) else (" ← current" if name == role else "")
        print(f"## {head}: {name}{marker}")
        for i, line in enumerate(flow[lang], 1):
            print(f"{i}. `{line}`")
        print()

    print("## 看板 (panel-manage.py run <name>)" if zh else "## Panels (panel-manage.py run <name>)")
    print("| Name | " + ("用途" if zh else "Use") + " |")
    print("|------|------|")
    for key, zh_desc, en_desc in PANELS:
        print(f"| {key} | {zh_desc if zh else en_desc} |")
    print()

    print("## 按场景导航" if zh else "## Where do I start?")
    print("| " + ("场景" if zh else "Goal") + " | " + ("命令" if zh else "Command") + " |")
    print("|------|------|")
    for label, cmd in SCENARIOS[lang]:
        print(f"| {label} | `{cmd}` |")
    print()

    print("## 安全约定" if zh else "## Safety rules")
    if zh:
        print("- 写操作默认 dry-run；确认后加 `--apply`")
        print("- 删除 = 移入 trash（可 restore）；`purge` 需 `--force` 才永久删")
        print("- 项目/任务元数据只用脚本写，勿手改 `.project` / `.task`")
    else:
        print("- Writes are dry-run by default; add `--apply` to commit")
        print("- delete = move to trash (restorable); `purge` needs `--force`")
        print("- Project/task metadata via scripts only; don't hand-edit `.project`/`.task`")
    print()
    print((f"脚本目录: `{SK}`" if zh else f"Scripts dir: `{SK}`"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
