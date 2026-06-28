#!/usr/bin/env python3
"""Project CRUD manager for plan-manager.

Writes are dry-run by default. Pass --apply to mutate files.
"""

import argparse
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import atomic_write, backup, die, maybe_apply, read_data, slugify, validate_name


VALID_STATUS = {"active", "idle", "completed", "archived"}
VALID_PRIORITY = {"P0", "P1", "P2", "P3"}
PROJECT_FIELDS = ["name", "slug", "status", "priority", "created", "goal", "description", "notes"]


def validate_status(status: str) -> None:
    if status not in VALID_STATUS:
        die(f"invalid status: {status}")


def validate_priority(priority: str) -> None:
    if priority not in VALID_PRIORITY:
        die(f"invalid priority: {priority}")


def write_data(path: Path, data: dict) -> None:
    lines = []
    for field in PROJECT_FIELDS:
        value = data.get(field, "")
        if field in {"goal", "description", "notes"}:
            lines.append(f"{field}: |")
            if value:
                lines.extend(f"  {line}" for line in str(value).splitlines())
        else:
            lines.append(f"{field}: {value}")
    atomic_write(path, "\n".join(lines) + "\n")


def project_dir(root: Path, name: str) -> Path:
    validate_name(name, "project name")
    return root / "project" / name


def cmd_list(args) -> None:
    base = Path(args.root) / "project"
    print("| Project | Status | Priority | Goal |")
    print("|---------|--------|:--------:|------|")
    if not base.is_dir():
        return
    for path in sorted(p for p in base.iterdir() if p.is_dir()):
        data = read_data(path / ".project")
        if args.status and data.get("status") != args.status:
            continue
        print(f"| {path.name} | {data.get('status', 'unregistered')} | {data.get('priority', '—')} | {data.get('goal', '') or '—'} |")


def cmd_read(args) -> None:
    path = project_dir(Path(args.root), args.project) / ".project"
    if not path.exists():
        die(f"project not found: {args.project}")
    print(path.read_text(encoding="utf-8"), end="")


def cmd_create(args) -> None:
    validate_priority(args.priority)
    root = Path(args.root)
    path = project_dir(root, args.name)
    if (path / ".project").exists():
        die(f"project already exists: {args.name}")
    data = {
        "name": args.name,
        "slug": slugify(args.name),
        "status": args.status,
        "priority": args.priority,
        "created": date.today().isoformat(),
        "goal": args.goal or "",
        "description": args.description or "",
        "notes": args.notes or "",
    }
    validate_status(data["status"])

    def apply_create() -> None:
        (path / "tasks").mkdir(parents=True, exist_ok=True)
        write_data(path / ".project", data)
        readme = path / "README.md"
        if not readme.exists():
            readme.write_text(f"# {args.name}\n", encoding="utf-8")

    maybe_apply(args.apply, f"create project {args.name} at {path}", apply_create)


def cmd_update(args) -> None:
    path = project_dir(Path(args.root), args.project)
    file_path = path / ".project"
    if not file_path.exists():
        die(f"project not found: {args.project}")
    data = read_data(file_path)
    if args.status:
        validate_status(args.status)
        data["status"] = args.status
    if args.priority:
        validate_priority(args.priority)
        data["priority"] = args.priority
    for field in ("goal", "description", "notes"):
        value = getattr(args, field)
        if value is not None:
            data[field] = value

    def apply_update() -> None:
        backup(file_path)
        write_data(file_path, data)

    maybe_apply(args.apply, f"update project {args.project}", apply_update)


def cmd_archive(args) -> None:
    args.status = "archived"
    args.priority = None
    args.goal = args.description = args.notes = None
    cmd_update(args)


def cmd_delete(args) -> None:
    root = Path(args.root)
    path = project_dir(root, args.project)
    if not path.exists():
        die(f"project not found: {args.project}")
    tasks = list(path.glob("tasks/*/.task"))
    active = [t for t in tasks if read_data(t).get("status") == "in_progress"]
    if active and not args.force:
        die("project has active tasks; pass --force to move to trash")
    if tasks and not args.force:
        die("project has tasks; pass --force to move to trash")
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    trash = root / ".plan-manager" / "trash" / "projects" / f"{args.project}-{stamp}"

    def apply_delete() -> None:
        trash.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(trash))

    maybe_apply(args.apply, f"move project {args.project} to {trash}", apply_delete)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage plan-manager projects")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.add_argument("--root", required=True)
    p.add_argument("--status")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("read")
    p.add_argument("--root", required=True)
    p.add_argument("project")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("create")
    p.add_argument("--root", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--goal", default="")
    p.add_argument("--description", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--priority", default="P1")
    p.add_argument("--status", default="active")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("update")
    p.add_argument("--root", required=True)
    p.add_argument("project")
    p.add_argument("--goal")
    p.add_argument("--description")
    p.add_argument("--notes")
    p.add_argument("--status")
    p.add_argument("--priority")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("archive")
    p.add_argument("--root", required=True)
    p.add_argument("project")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_archive)

    p = sub.add_parser("delete")
    p.add_argument("--root", required=True)
    p.add_argument("project")
    p.add_argument("--force", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
