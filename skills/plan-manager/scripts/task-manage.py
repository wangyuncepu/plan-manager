#!/usr/bin/env python3
"""Task CRUD manager for plan-manager.

Writes are dry-run by default. Pass --apply to mutate files.
"""

import argparse
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    atomic_write,
    backup,
    die,
    list_string,
    maybe_apply,
    parse_list,
    read_data,
    slugify,
    validate_name,
)


VALID_STATUS = {"pending", "planned", "ready", "in_progress", "completed", "cancelled", "blocked"}
VALID_PRIORITY = {"P0", "P1", "P2", "P3"}
TASK_FIELDS = [
    "id",
    "title",
    "project",
    "status",
    "priority",
    "order",
    "created",
    "deadline",
    "completed",
    "depends_on",
    "depends_on_cross",
    "description",
    "notes",
    "plan_file",
    "max_iterations",
]


def validate_status(status: str) -> None:
    if status not in VALID_STATUS:
        die(f"invalid status: {status}")


def validate_priority(priority: str) -> None:
    if priority not in VALID_PRIORITY:
        die(f"invalid priority: {priority}")


def write_data(path: Path, data: dict) -> None:
    lines = []
    for field in TASK_FIELDS:
        value = data.get(field, "")
        if field in {"description", "notes"}:
            lines.append(f"{field}: |")
            if value:
                lines.extend(f"  {line}" for line in str(value).splitlines())
        else:
            lines.append(f"{field}: {value}")
    atomic_write(path, "\n".join(lines) + "\n")


def project_dir(root: Path, project: str) -> Path:
    validate_name(project, "project")
    path = root / "project" / project
    if not (path / ".project").exists():
        die(f"project not found: {project}")
    return path


def task_files(root: Path):
    return sorted((root / "project").glob("*/tasks/*/.task"))


def find_task(root: Path, query: str) -> Path:
    needle = query.lower()
    for path in task_files(root):
        data = read_data(path)
        if needle in {data.get("id", "").lower(), data.get("title", "").lower(), path.parent.name.lower()}:
            return path
    die(f"task not found: {query}")


def prefix(project: str) -> str:
    result = "".join(ch for ch in project.upper() if ch.isalnum())[:3]
    return result or "TSK"


def next_id(project_path: Path, project: str) -> tuple[str, int]:
    pref = prefix(project)
    nums = []
    for task in project_path.glob("tasks/*/.task"):
        task_id = read_data(task).get("id", "")
        if task_id.startswith(f"{pref}-"):
            tail = task_id.split("-", 1)[1]
            if tail.isdigit():
                nums.append(int(tail))
    num = max(nums, default=0) + 1
    return f"{pref}-{num:03d}", num


def plan_path(task_file: Path) -> Path:
    return task_file.parent / "plan.md"


def set_plan_status(path: Path, status: str) -> None:
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("Plan Status:"):
            rest = ""
            if "|" in line:
                rest = " |" + line.split("|", 1)[1]
            lines[idx] = f"Plan Status: {status}{rest}"
            atomic_write(path, "\n".join(lines) + "\n")
            return


def cmd_list(args) -> None:
    print("| ID | Project | Status | Priority | Title |")
    print("|----|---------|--------|:--------:|-------|")
    for path in task_files(Path(args.root)):
        data = read_data(path)
        if args.project and data.get("project") != args.project:
            continue
        if args.status and data.get("status") != args.status:
            continue
        print(f"| {data.get('id')} | {data.get('project')} | {data.get('status')} | {data.get('priority')} | {data.get('title')} |")


def cmd_read(args) -> None:
    path = find_task(Path(args.root), args.task)
    print(path.read_text(encoding="utf-8"), end="")


def cmd_create(args) -> None:
    validate_priority(args.priority)
    validate_name(args.title, "title")
    root = Path(args.root)
    proj = project_dir(root, args.project)
    slug = slugify(args.title)
    task_dir = proj / "tasks" / slug
    if task_dir.exists():
        die(f"task directory already exists: {task_dir}")
    task_id, order = next_id(proj, args.project)
    data = {
        "id": task_id,
        "title": args.title,
        "project": args.project,
        "status": "pending",
        "priority": args.priority,
        "order": str(order),
        "created": date.today().isoformat(),
        "deadline": "",
        "completed": "",
        "depends_on": "[]",
        "depends_on_cross": "[]",
        "description": args.description or "",
        "notes": "",
        "plan_file": "plan.md",
        "max_iterations": str(args.max_iterations),
    }

    def apply_create() -> None:
        (task_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
        write_data(task_dir / ".task", data)

    maybe_apply(args.apply, f"create task {task_id} in {task_dir}", apply_create)


def update_task_file(task_file: Path, fields: dict) -> None:
    data = read_data(task_file)
    data.update({k: v for k, v in fields.items() if v is not None})
    if data.get("status") == "completed" and not data.get("completed"):
        data["completed"] = date.today().isoformat()
    write_data(task_file, data)


def cmd_update(args) -> None:
    root = Path(args.root)
    task_file = find_task(root, args.task)
    if args.status:
        validate_status(args.status)
    if args.priority:
        validate_priority(args.priority)
    fields = {
        "status": args.status,
        "priority": args.priority,
        "description": args.description,
        "notes": args.notes,
        "max_iterations": str(args.max_iterations) if args.max_iterations is not None else None,
    }

    def apply_update() -> None:
        backup(task_file)
        update_task_file(task_file, fields)

    maybe_apply(args.apply, f"update task {args.task}", apply_update)


def cmd_start(args) -> None:
    root = Path(args.root)
    task_file = find_task(root, args.task)
    data = read_data(task_file)
    project = data.get("project")
    for other in task_files(root):
        other_data = read_data(other)
        if other != task_file and other_data.get("project") == project and other_data.get("status") == "in_progress":
            die(f"project already has in_progress task: {other_data.get('id')}")

    def apply_start() -> None:
        backup(task_file)
        update_task_file(task_file, {"status": "in_progress"})
        set_plan_status(plan_path(task_file), "executing")

    maybe_apply(args.apply, f"start task {data.get('id')}", apply_start)


def cmd_complete(args) -> None:
    task_file = find_task(Path(args.root), args.task)
    data = read_data(task_file)

    def apply_complete() -> None:
        backup(task_file)
        update_task_file(task_file, {"status": "completed", "completed": date.today().isoformat()})
        set_plan_status(plan_path(task_file), "done")

    maybe_apply(args.apply, f"complete task {data.get('id')}", apply_complete)


def cmd_block(args) -> None:
    task_file = find_task(Path(args.root), args.task)
    old = read_data(task_file)
    reason = args.reason or "blocked"
    notes = old.get("notes", "")
    notes = (notes + "\n" if notes else "") + f"Blocked: {reason}"

    def apply_block() -> None:
        backup(task_file)
        update_task_file(task_file, {"status": "blocked", "notes": notes})

    maybe_apply(args.apply, f"block task {old.get('id')}: {reason}", apply_block)


def cmd_cancel(args) -> None:
    args.status = "cancelled"
    args.priority = args.description = args.notes = None
    args.max_iterations = None
    cmd_update(args)


def cmd_deps(args) -> None:
    root = Path(args.root)
    task_file = find_task(root, args.task)
    data = read_data(task_file)
    deps = parse_list(data.get("depends_on", "[]"))
    if args.add:
        dep_file = find_task(root, args.add)
        dep_id = read_data(dep_file).get("id")
        if dep_id == data.get("id"):
            die("task cannot depend on itself")
        if dep_id not in deps:
            deps.append(dep_id)
    if args.remove:
        deps = [dep for dep in deps if dep != args.remove]
    if not args.add and not args.remove:
        print(list_string(deps))
        return

    def apply_deps() -> None:
        backup(task_file)
        update_task_file(task_file, {"depends_on": list_string(deps)})

    maybe_apply(args.apply, f"update deps for {data.get('id')} -> {list_string(deps)}", apply_deps)


def cmd_delete(args) -> None:
    root = Path(args.root)
    task_file = find_task(root, args.task)
    data = read_data(task_file)
    task_id = data.get("id")
    dependents = []
    for other in task_files(root):
        other_data = read_data(other)
        if task_id in parse_list(other_data.get("depends_on", "[]")):
            dependents.append(other_data.get("id"))
    if dependents and not args.force:
        die(f"dependent tasks exist: {', '.join(dependents)}; pass --force")
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    trash = task_file.parent.parent / ".trash" / f"{task_file.parent.name}-{stamp}"

    def apply_delete() -> None:
        trash.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(task_file.parent), str(trash))

    maybe_apply(args.apply, f"move task {task_id} to {trash}", apply_delete)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage plan-manager tasks")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.add_argument("--root", required=True)
    p.add_argument("--project")
    p.add_argument("--status")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("read")
    p.add_argument("--root", required=True)
    p.add_argument("task")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("create")
    p.add_argument("--root", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--priority", default="P1")
    p.add_argument("--description", default="")
    p.add_argument("--max-iterations", type=int, default=0)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("update")
    p.add_argument("--root", required=True)
    p.add_argument("task")
    p.add_argument("--status")
    p.add_argument("--priority")
    p.add_argument("--description")
    p.add_argument("--notes")
    p.add_argument("--max-iterations", type=int)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_update)

    for name, func in (("start", cmd_start), ("complete", cmd_complete), ("cancel", cmd_cancel)):
        p = sub.add_parser(name)
        p.add_argument("--root", required=True)
        p.add_argument("task")
        p.add_argument("--apply", action="store_true")
        p.set_defaults(func=func)

    p = sub.add_parser("block")
    p.add_argument("--root", required=True)
    p.add_argument("task")
    p.add_argument("--reason")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_block)

    p = sub.add_parser("deps")
    p.add_argument("--root", required=True)
    p.add_argument("task")
    p.add_argument("--add")
    p.add_argument("--remove")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_deps)

    p = sub.add_parser("delete")
    p.add_argument("--root", required=True)
    p.add_argument("task")
    p.add_argument("--force", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
