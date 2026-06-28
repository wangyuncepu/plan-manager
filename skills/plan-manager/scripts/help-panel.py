#!/usr/bin/env python3
"""Help panel for plan-manager: conversational, role-aware guide.

User-facing: lists what to SAY to the assistant in plain language.
All scripts are run by the assistant internally — never shown as user commands.
"""

import argparse
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude" / "plan-manager" / "config.json"


def read_config() -> dict:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


# Each flow row: (what you say, what happens)
STRATEGIST_FLOW = {
    "zh": [
        ("看看现状 / 总览", "全局项目总览面板"),
        ("打开 <项目>", "该项目的详情面板"),
        ("分析 <项目>", "深入分析现状、缺口、方向"),
        ("新建项目 <名字>", "我帮你建项目并一起定目标"),
        ("给 <项目> 加个任务", "我建任务、问清细节"),
        ("给 <任务> 做计划", "我起草计划 → 你点头才执行"),
        ("切到执行模式", "进入干活角色"),
    ],
    "en": [
        ("show overview", "global project overview panel"),
        ("open <project>", "that project's detail panel"),
        ("analyze <project>", "deep state / gap / direction analysis"),
        ("create project <name>", "I create it and set the goal with you"),
        ("add a task to <project>", "I create the task, ask for details"),
        ("make a plan for <task>", "I draft a plan → you approve before run"),
        ("switch to executor", "enter the working role"),
    ],
}

EXECUTOR_FLOW = {
    "zh": [
        ("有哪些能执行的任务", "就绪队列"),
        ("切到执行模式", "进入干活角色"),
        ("开始执行 / 执行下一个", "跑就绪任务"),
        ("一直跑 / 自动", "连续执行直到没有就绪任务"),
        ("继续 / 接着上次", "断点续跑"),
        ("把 <任务> 标记完成 / 阻塞", "改任务状态"),
    ],
    "en": [
        ("what can I run", "ready queue"),
        ("switch to executor", "enter the working role"),
        ("start / run next", "run ready tasks"),
        ("keep going / auto", "run until no ready tasks remain"),
        ("continue", "resume from checkpoint"),
        ("mark <task> done / blocked", "change task state"),
    ],
}

# What you say -> what you get. No scripts shown.
SCENARIOS = {
    "zh": [
        ("看现状", "“总览” 或 “打开 <项目>”"),
        ("建项目", "“新建项目 <名字>”"),
        ("加任务", "“给 <项目> 加任务 <标题>”"),
        ("执行任务", "“切到执行模式” → “开始执行”"),
        ("断点续跑", "“继续”"),
        ("找回误删", "“回收站有什么” → “恢复 <名字>”"),
        ("永久清理", "“永久删除 <名字>”（我会再确认一次）"),
        ("改配置", "“改成英文 / 切角色 / 看配置”"),
        ("固化常用看板", "“把这个存成常用看板 <名字>”"),
    ],
    "en": [
        ("See state", "\"overview\" or \"open <project>\""),
        ("New project", "\"create project <name>\""),
        ("New task", "\"add task <title> to <project>\""),
        ("Run tasks", "\"switch to executor\" → \"start\""),
        ("Resume", "\"continue\""),
        ("Undo delete", "\"what's in trash\" → \"restore <name>\""),
        ("Purge", "\"permanently delete <name>\" (I reconfirm)"),
        ("Configure", "\"set language en / switch role / show config\""),
        ("Save a panel", "\"save this as a panel called <name>\""),
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
    if zh:
        print(f"当前角色: **{role}** ｜ 你只管用大白话跟我说想做什么,具体操作我来做。")
    else:
        print(f"Current role: **{role}** | Just tell me what you want in plain words — I handle the rest.")
    print()

    flows = [("strategist", STRATEGIST_FLOW), ("executor", EXECUTOR_FLOW)]
    flows.sort(key=lambda f: f[0] != role)  # active role first

    head = "你可以说" if zh else "You can say"
    col_say = "对我说" if zh else "Say"
    col_do = "我会做" if zh else "I do"
    for name, flow in flows:
        marker = " ← 当前" if (zh and name == role) else (" ← current" if name == role else "")
        print(f"## {head}（{name}{marker}）" if zh else f"## {head} ({name}{marker})")
        print(f"| {col_say} | {col_do} |")
        print("|------|------|")
        for say, do in flow[lang]:
            print(f"| {say} | {do} |")
        print()

    print("## 按场景" if zh else "## Where do I start?")
    print("| " + ("想做什么" if zh else "Goal") + " | " + (col_say) + " |")
    print("|------|------|")
    for label, say in SCENARIOS[lang]:
        print(f"| {label} | {say} |")
    print()

    print("## 怎么安全" if zh else "## Safety")
    if zh:
        print("- 改动前我先给你看效果,确认后才落盘。")
        print("- 删除只是移进回收站,可恢复;永久删除我会再问一次。")
        print("- 这些细节你不用管,直接说意图即可。")
    else:
        print("- I preview changes first; nothing is written until you confirm.")
        print("- Delete just moves to trash (restorable); purge asks again.")
        print("- You don't manage any of this — just state intent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
