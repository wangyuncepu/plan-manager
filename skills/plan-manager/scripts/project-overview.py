#!/usr/bin/env python3
"""Generate plan-manager project and task dashboards."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


CONFIG_PATH = Path.home() / ".claude" / "plan-manager" / "config.json"
CHECK_RE = re.compile(r"^\s*(?:(?:\d+\.)|-)\s*\[(?P<mark>[ xX])\]\s*(?P<text>.*)$")


def read_field(path: Path, field: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""

    prefix = f"{field}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = line.split(":", 1)[1].strip()
        if value != "|":
            return value
        block_lines = []
        for block_line in lines[index + 1 :]:
            if not block_line.startswith((" ", "\t")):
                break
            stripped = block_line.strip()
            if stripped:
                block_lines.append(stripped)
        return " ".join(block_lines)
    return ""


def read_config() -> dict:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def github_config(config: dict) -> dict:
    github = config.get("github")
    return github if isinstance(github, dict) else {"enabled": False}


def print_config_header(config: dict, root: Path, lang: str) -> None:
    title = "重要配置" if lang == "zh" else "Configuration"
    cfg_root = config.get("root") or str(root)
    role = config.get("role", "?")
    language = config.get("language", lang)
    parallelism = config.get("parallelism", "?")
    autonomy = config.get("autonomy", "?")
    max_iterations = config.get("max_iterations_per_task", "?")
    overnight = str(config.get("overnight", "?"))
    github = github_config(config)
    github_owner = github.get("owner") or "—"
    github_enabled = str(github.get("enabled", False))

    print(f"## {title}")
    print("| Root | Role | Language | Parallelism | Autonomy | Max Iterations | Overnight | GitHub |")
    print("|------|------|----------|:-----------:|----------|:--------------:|:---------:|--------|")
    print(
        f"| {cfg_root} | {role} | {language} | {parallelism} | {autonomy} | "
        f"{max_iterations} | {overnight} | {github_enabled}:{github_owner} |"
    )
    print()


def remote_data(root: Path, script_dir: Path, config: dict, lang: str) -> dict[str, dict]:
    github = github_config(config)
    if not github.get("enabled") or not github.get("owner"):
        return {}
    cmd = [
        str(script_dir / "github-verify.py"),
        "--root",
        str(root),
        "--owner",
        str(github.get("owner")),
        "--lang",
        lang,
        "--json",
    ]
    if not github.get("check_remote", True):
        cmd.append("--no-remote-check")
    try:
        out = subprocess.run(
            cmd,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=20,
        ).stdout
        items = json.loads(out) if out.strip() else []
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return {}
    return {item.get("project", ""): item for item in items if item.get("project")}


def remote_cell(remote: dict | None) -> str:
    if not remote:
        return "—"
    return remote.get("status") or "—"


def count_tasks(project_dir: Path) -> dict:
    counts = {"total": 0, "active": 0, "pending": 0, "planned": 0, "ready": 0, "blocked": 0, "completed": 0}
    for task_file in sorted(project_dir.glob("tasks/*/.task")):
        counts["total"] += 1
        status = read_field(task_file, "status") or "pending"
        if status in counts:
            counts[status] += 1
        if status == "in_progress":
            counts["active"] += 1
    return counts


def task_summary(counts: dict, lang: str) -> str:
    ready = counts.get("ready", 0)
    active = counts.get("active", 0)
    completed = counts.get("completed", 0)
    total = counts.get("total", 0)
    return f"{active}/{ready}/{completed}/{total}"


def session_cell(script_dir: Path, project: str, root: Path, lang: str) -> str:
    digest = script_dir / "session-digest.py"
    if not digest.exists():
        return "无会话" if lang == "zh" else "no session"
    try:
        out = subprocess.run(
            [str(digest), project, "--root", str(root), "--lang", lang, "--max-user-msgs", "1"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).stdout.splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return "?"
    if not out or out[0].strip() == "session: none":
        return "无会话" if lang == "zh" else "no session"
    rel = "?"
    count = "0"
    for line in out:
        if line.startswith("relative_time:"):
            rel = line.split(":", 1)[1].strip()
        elif line.startswith("user_msg_count:"):
            count = line.split(":", 1)[1].strip()
    suffix = "条" if lang == "zh" else " msgs"
    return f"{rel}, {count}{suffix}"


def plan_quality(project_dir: Path) -> str:
    plans = list(project_dir.glob("tasks/*/plan.md"))
    tasks = list(project_dir.glob("tasks/*/.task"))
    if not tasks:
        return "—"
    if len(plans) == len(tasks):
        return "✓"
    return f"{len(plans)}/{len(tasks)}"


def project_summary(project_dir: Path, script_dir: Path, root: Path, lang: str, remote: dict | None = None) -> dict:
    name = project_dir.name
    project_file = project_dir / ".project"
    if project_file.exists():
        status = read_field(project_file, "status") or "active"
        goal = read_field(project_file, "goal") or ("未设定" if lang == "zh" else "unset")
        suggest = "检查计划" if lang == "zh" else "review plans"
    else:
        status = "unregistered"
        goal = "未设定" if lang == "zh" else "unset"
        suggest = "注册项目" if lang == "zh" else "register project"
    counts = count_tasks(project_dir)
    return {
        "name": name,
        "status": status,
        "goal": goal,
        "plan_quality": plan_quality(project_dir),
        "tasks": task_summary(counts, lang),
        "session": session_cell(script_dir, name, root, lang),
        "remote": remote_cell(remote),
        "remote_data": remote or {},
        "suggest": suggest,
        "counts": counts,
    }


def print_project_overview(root: Path, script_dir: Path, lang: str, remotes: dict[str, dict], show_remote: bool = False) -> list[dict]:
    projects_dir = root / "project"
    summaries = []
    if projects_dir.is_dir():
        summaries = [
            project_summary(project_dir, script_dir, root, lang, remotes.get(project_dir.name))
            for project_dir in sorted(p for p in projects_dir.iterdir() if p.is_dir())
        ]

    print("## 项目分析" if lang == "zh" else "## Project Analysis")
    # Show the Remote Status column whenever GitHub is enabled, even if the API
    # call returned nothing (per-row cell falls back to github_unknown / —).
    has_remote = show_remote or bool(remotes)
    if lang == "zh":
        header = "| 项目 | 状态 |"
        sep = "|------|------|"
    else:
        header = "| Project | Status |"
        sep = "|---------|--------|"
    if has_remote:
        header += " Remote Status |"
        sep += "---------------|"
    header += " 目标 | 计划质量 | 任务(执行/准备/完成/总) | 最近会话 |" if lang == "zh" else " Goal | Plan | Tasks(active/ready/done/total) | Last Session |"
    if lang == "zh":
        sep += "------|:------:|------|---------|"
    else:
        sep += "------|:----:|-------|--------------|"
    header += " 建议 |" if lang == "zh" else " Suggest |"
    sep += "------|" if lang == "zh" else "---------|"
    print(header)
    print(sep)

    remote_unknown = show_remote and not remotes
    for summary in summaries:
        row = f"| {summary['name']} | {summary['status']} |"
        if has_remote:
            cell = "github_unknown" if remote_unknown else summary["remote"]
            row += f" {cell} |"
        row += (
            f" {summary['goal']} | {summary['plan_quality']} | "
            f"{summary['tasks']} | {summary['session']} | {summary['suggest']} |"
        )
        print(row)
    return summaries


def suggested_actions(summaries: list[dict], lang: str) -> list[str]:
    actions = []
    for summary in summaries:
        remote = summary.get("remote_data") or {}
        if remote.get("status") == "origin_mismatch":
            action = f"fix origin remote for {summary['name']} → 当前 origin 不匹配预期仓库" if lang == "zh" else f"fix origin remote for {summary['name']} → origin mismatch"
            actions.append(action)
        elif remote.get("status") == "repo_missing":
            action = f"create repo {remote.get('expected_repo')} → 预期仓库不存在或无权限" if lang == "zh" else f"create repo {remote.get('expected_repo')} → missing expected repo"
            actions.append(action)
        elif remote.get("status") == "missing_origin":
            action = f"add origin remote for {summary['name']} → 缺少 origin" if lang == "zh" else f"add origin remote for {summary['name']} → missing origin"
            actions.append(action)

    for summary in summaries:
        if summary["status"] == "unregistered" and summary["session"] not in {"无会话", "no session", "?"}:
            action = f"create project {summary['name']} → 基于已有会话注册项目" if lang == "zh" else f"create project {summary['name']} → register from existing session"
            actions.append(action)

    for summary in summaries:
        if summary["status"] != "unregistered" and summary["goal"] in {"", "未设定", "unset"}:
            action = f"discuss direction for {summary['name']} → 补齐项目目标" if lang == "zh" else f"discuss direction for {summary['name']} → fill missing goal"
            actions.append(action)

    for summary in summaries:
        if summary["status"] != "unregistered" and summary["plan_quality"] != "✓":
            action = f"review plans for {summary['name']} → 修复计划质量" if lang == "zh" else f"review plans for {summary['name']} → fix plan quality"
            actions.append(action)

    if not actions:
        actions.append("暂无建议：所有项目状态正常" if lang == "zh" else "No suggestions: all projects look healthy")
    return actions[:5]


def print_suggested_actions(summaries: list[dict], lang: str) -> None:
    print()
    print("## 建议行动" if lang == "zh" else "## Suggested Actions")
    for idx, action in enumerate(suggested_actions(summaries, lang), 1):
        print(f"{idx}. {action}")


def find_project(root: Path, query: str) -> Path | None:
    needle = query.strip().lower()
    projects_dir = root / "project"
    if not projects_dir.is_dir():
        return None
    for project_dir in sorted(p for p in projects_dir.iterdir() if p.is_dir()):
        project_file = project_dir / ".project"
        name = read_field(project_file, "name").lower() if project_file.exists() else ""
        title = read_field(project_file, "title").lower() if project_file.exists() else ""
        slug = read_field(project_file, "slug").lower() if project_file.exists() else ""
        candidates = {project_dir.name.lower(), name, title, slug}
        if needle in {candidate for candidate in candidates if candidate}:
            return project_dir
    return None


def task_rows(project_dir: Path) -> list[dict]:
    rows = []
    for task_file in sorted(project_dir.glob("tasks/*/.task")):
        task_dir = task_file.parent
        plan_path = task_dir / "plan.md"
        steps = checklist(section_lines(plan_path, "Steps"))
        done_steps = sum(1 for done, _ in steps if done)
        rows.append(
            {
                "id": read_field(task_file, "id"),
                "title": read_field(task_file, "title"),
                "status": read_field(task_file, "status"),
                "priority": read_field(task_file, "priority"),
                "plan_status": read_plan_status(plan_path),
                "progress": f"{done_steps}/{len(steps)}",
                "slug": task_dir.name,
            }
        )
    return rows


def print_remote_fields(remote: dict | None, show_remote: bool = False) -> None:
    if not remote:
        if show_remote:
            print("| Remote Status | github_unknown |")
            print("| Remote Message | GitHub check returned no data |")
        return
    print(f"| Expected Repo | {remote.get('expected_repo') or '—'} |")
    print(f"| Origin | {remote.get('origin') or '—'} |")
    print(f"| Remote Status | {remote.get('status') or '—'} |")
    print(f"| GitHub URL | {remote.get('github_url') or '—'} |")
    print(f"| Remote Message | {remote.get('message') or '—'} |")


def print_project_panel(root: Path, script_dir: Path, project_dir: Path, lang: str, remote: dict | None = None, show_remote: bool = False) -> None:
    summary = project_summary(project_dir, script_dir, root, lang, remote)
    project_file = project_dir / ".project"
    description = read_field(project_file, "description") if project_file.exists() else ""
    notes = read_field(project_file, "notes") if project_file.exists() else ""

    print("## 项目面板" if lang == "zh" else "## Project Panel")
    print("| 字段 | 值 |" if lang == "zh" else "| Field | Value |")
    print("|------|----|")
    for key, value in [
        ("Name", summary["name"]),
        ("Status", summary["status"]),
        ("Goal", summary["goal"]),
        ("Plan Quality", summary["plan_quality"]),
        ("Tasks(active/ready/done/total)", summary["tasks"]),
        ("Last Session", summary["session"]),
        ("Path", str(project_dir)),
    ]:
        print(f"| {key} | {value or '—'} |")
    print_remote_fields(remote, show_remote)

    if description:
        print()
        print("## Description")
        print(description)
    if notes:
        print()
        print("## Notes")
        print(notes)

    rows = task_rows(project_dir)
    print()
    print("## 任务" if lang == "zh" else "## Tasks")
    print("| ID | Status | Priority | Plan | Progress | Title |")
    print("|----|--------|:--------:|------|----------|-------|")
    for row in rows:
        print(f"| {row['id']} | {row['status']} | {row['priority']} | {row['plan_status']} | {row['progress']} | {row['title']} |")

    print()
    print("## 建议行动" if lang == "zh" else "## Suggested Actions")
    if remote and remote.get("status") == "origin_mismatch":
        print(f"1. fix origin remote for {summary['name']} → 当前 origin 不匹配预期仓库" if lang == "zh" else f"1. fix origin remote for {summary['name']} → origin mismatch")
    elif remote and remote.get("status") == "repo_missing":
        print(f"1. create repo {remote.get('expected_repo')} → 预期仓库不存在或无权限" if lang == "zh" else f"1. create repo {remote.get('expected_repo')} → missing expected repo")
    elif remote and remote.get("status") == "missing_origin":
        print(f"1. add origin remote for {summary['name']} → 缺少 origin" if lang == "zh" else f"1. add origin remote for {summary['name']} → missing origin")
    elif any(row["status"] == "ready" for row in rows):
        print(f"1. switch to executor → 执行 {summary['name']} ready task" if lang == "zh" else f"1. switch to executor → run ready tasks for {summary['name']}")
    elif any(row["status"] in {"pending", "planned", "blocked", "in_progress"} for row in rows):
        print(f"1. review plans for {summary['name']} → 检查未完成任务" if lang == "zh" else f"1. review plans for {summary['name']} → inspect unfinished tasks")
    elif rows:
        print(f"1. add task to {summary['name']} → 当前任务已全部完成，创建下一阶段任务" if lang == "zh" else f"1. add task to {summary['name']} → all tasks completed, create next-stage task")
    else:
        print(f"1. add task to {summary['name']} → 创建下一步任务" if lang == "zh" else f"1. add task to {summary['name']} → create next task")


def find_task(root: Path, query: str) -> Path | None:
    needle = query.strip().lower()
    for task_file in sorted(root.glob("project/*/tasks/*/.task")):
        task_id = read_field(task_file, "id").lower()
        title = read_field(task_file, "title").lower()
        slug = task_file.parent.name.lower()
        if needle in {task_id, title, slug}:
            return task_file
    return None


def read_plan_status(plan_path: Path) -> str:
    try:
        for line in plan_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("Plan Status:"):
                return line.split(":", 1)[1].split("|", 1)[0].strip()
            if line.startswith("Status:"):
                return line.split(":", 1)[1].strip()
    except OSError:
        return "missing"
    return "unknown"


def section_lines(plan_path: Path, heading: str) -> list[str]:
    try:
        lines = plan_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    result = []
    in_section = False
    target = f"## {heading}"
    for line in lines:
        if line.startswith("## "):
            if in_section:
                break
            in_section = line.strip().startswith(target)
            continue
        if in_section:
            result.append(line)
    return result


def first_paragraph(lines: list[str]) -> str:
    parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped and parts:
            break
        if stripped:
            parts.append(stripped)
    return " ".join(parts)


def checklist(lines: list[str]) -> list[tuple[bool, str]]:
    items = []
    for line in lines:
        match = CHECK_RE.match(line)
        if match:
            done = match.group("mark").lower() == "x"
            items.append((done, match.group("text").strip()))
    return items


def dependency_status(root: Path, deps: str, deps_cross: str = "") -> str:
    raw = f"{deps.strip('[]')},{deps_cross.strip('[]')}"
    dep_items = [item.strip().strip('"\'') for item in raw.split(",") if item.strip()]
    if not dep_items:
        return "—"
    statuses = []
    for dep in dep_items:
        task = find_task(root, dep)
        status = read_field(task, "status") if task else "missing"
        statuses.append(f"{dep} ({status})")
    return ", ".join(statuses)


def checkpoint_summary(task_dir: Path) -> list[str]:
    checkpoint_dir = task_dir / "checkpoints"
    snapshot = checkpoint_dir / "snapshot.md"
    iterations = checkpoint_dir / "iterations.log"
    issues = checkpoint_dir / "issues.md"
    iteration_count = 0
    if iterations.exists():
        iteration_count = len(iterations.read_text(encoding="utf-8", errors="replace").splitlines())
    return [
        f"- snapshot: {'exists' if snapshot.exists() else 'missing'}",
        f"- iterations.log: {iteration_count} lines",
        f"- issues.md: {'exists' if issues.exists() else 'missing'}",
    ]


def print_task_panel(root: Path, task_file: Path, lang: str) -> None:
    task_dir = task_file.parent
    plan_path = task_dir / "plan.md"
    task_id = read_field(task_file, "id")
    title = read_field(task_file, "title")
    project = read_field(task_file, "project")
    status = read_field(task_file, "status")
    priority = read_field(task_file, "priority")
    created = read_field(task_file, "created")
    completed = read_field(task_file, "completed") or "—"
    deps = dependency_status(
        root,
        read_field(task_file, "depends_on"),
        read_field(task_file, "depends_on_cross"),
    )
    plan_status = read_plan_status(plan_path)
    criteria = checklist(section_lines(plan_path, "Success Criteria")) or checklist(section_lines(plan_path, "Success Criteria (COMPLETION PROMISE)"))
    steps = checklist(section_lines(plan_path, "Steps"))
    done_steps = sum(1 for done, _ in steps if done)
    max_iterations = read_field(task_file, "max_iterations") or "default"

    print("## 任务面板" if lang == "zh" else "## Task Panel")
    print("| 字段 | 值 |" if lang == "zh" else "| Field | Value |")
    print("|------|----|")
    rows = [
        ("ID", task_id),
        ("Project", project),
        ("Title", title),
        ("Status", status),
        ("Priority", priority),
        ("Created", created),
        ("Completed", completed),
        ("Dependencies", deps),
        ("Plan Status", plan_status),
        ("Progress", f"{done_steps}/{len(steps)} steps"),
        ("Iterations", f"0/{max_iterations}"),
        ("Task Dir", str(task_dir)),
    ]
    for key, value in rows:
        print(f"| {key} | {value or '—'} |")

    goal = first_paragraph(section_lines(plan_path, "Goal"))
    if goal:
        print()
        print("## Plan Goal")
        print(goal)
    if criteria:
        print()
        print("## Success Criteria")
        for done, text in criteria:
            mark = "x" if done else " "
            print(f"- [{mark}] {text}")
    if steps:
        print()
        print("## Steps")
        for done, text in steps:
            mark = "x" if done else " "
            print(f"- [{mark}] {text}")

    print()
    print("## Checkpoints")
    for line in checkpoint_summary(task_dir):
        print(line)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate plan-manager project overview")
    ap.add_argument("--root", required=True)
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("query", nargs="?", help="Project name or task ID/title/slug")
    ap.add_argument("--task", help="Show a task panel by task ID, title, or task directory slug")
    args = ap.parse_args()

    root = Path(args.root)
    script_dir = Path(__file__).resolve().parent
    config = read_config()
    remotes = remote_data(root, script_dir, config, args.lang)
    gh = github_config(config)
    show_remote = bool(gh.get("enabled") and gh.get("owner"))

    query = args.task or args.query
    project_dir = find_project(root, query) if query else None
    title = "# Plan Manager — project" if project_dir else ("# Plan Manager — task" if query else "# Plan Manager — strategist")
    print(title)
    print()
    print_config_header(config, root, args.lang)

    if project_dir:
        print_project_panel(root, script_dir, project_dir, args.lang, remotes.get(project_dir.name), show_remote)
        return 0
    if query:
        task_file = find_task(root, query)
        if task_file is None:
            print(f"Project or task not found: {query}", file=sys.stderr)
            return 1
        print_task_panel(root, task_file, args.lang)
        return 0

    summaries = print_project_overview(root, script_dir, args.lang, remotes, show_remote)
    print_suggested_actions(summaries, args.lang)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
