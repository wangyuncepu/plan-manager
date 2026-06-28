#!/usr/bin/env python3
"""List ready plan-manager tasks in execution order."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import parse_list, read_field


PRIORITY = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def plan_approved(task_dir: Path) -> bool:
    plan = task_dir / "plan.md"
    if not plan.exists():
        return False
    text = plan.read_text(encoding="utf-8", errors="replace")
    return "Plan Status: approved" in text or "Status: approved" in text


def collect_statuses(root: Path):
    statuses = {}
    for task_file in root.glob("project/*/tasks/*/.task"):
        task_id = read_field(task_file, "id")
        status = read_field(task_file, "status")
        if task_id:
            statuses[task_id] = status
    return statuses


def project_has_active(project_dir: Path) -> bool:
    for task_file in project_dir.glob("tasks/*/.task"):
        if read_field(task_file, "status") == "in_progress":
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="List ready tasks in execution order")
    ap.add_argument("--root", required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    root = Path(args.root)
    statuses = collect_statuses(root)
    ready = []

    for task_file in root.glob("project/*/tasks/*/.task"):
        task_dir = task_file.parent
        project_dir = task_dir.parent.parent
        if read_field(task_file, "status") != "ready":
            continue
        if project_has_active(project_dir):
            continue
        if not plan_approved(task_dir):
            continue
        deps = parse_list(read_field(task_file, "depends_on")) + parse_list(read_field(task_file, "depends_on_cross"))
        if any(statuses.get(dep) != "completed" for dep in deps):
            continue
        priority = read_field(task_file, "priority") or "P1"
        order = read_field(task_file, "order") or "999999"
        created = read_field(task_file, "created") or "9999-99-99"
        task_id = read_field(task_file, "id")
        title = read_field(task_file, "title")
        ready.append((PRIORITY.get(priority, 9), int(order) if order.isdigit() else 999999, created, project_dir.name, task_id, title, priority))

    ready.sort()
    if args.limit > 0:
        ready = ready[: args.limit]

    print("| # | Project | Task | Priority | Title |")
    print("|---|---------|------|:--------:|-------|")
    for idx, item in enumerate(ready, 1):
        _, _, _, project, task_id, title, priority = item
        print(f"| {idx} | {project} | {task_id} | {priority} | {title} |")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
