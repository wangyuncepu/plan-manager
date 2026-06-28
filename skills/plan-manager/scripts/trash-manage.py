#!/usr/bin/env python3
"""Trash management for plan-manager.

Trash locations:
- Projects: <root>/.plan-manager/trash/projects/<name>-<timestamp>
- Tasks: <root>/project/<project>/tasks/.trash/<slug>-<timestamp>

Writes are dry-run by default. Pass --apply to restore/purge/empty.
Permanent deletion requires --force.
"""

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, maybe_apply


@dataclass(frozen=True)
class TrashItem:
    kind: str
    name: str
    timestamp: str
    path: Path
    restore_path: Path
    project: str = ""


def parse_trash_name(value: str) -> tuple[str, str]:
    name, sep, stamp = value.rpartition("-")
    if not sep or len(stamp) != 14 or not stamp.isdigit():
        die(f"invalid trash item name: {value}")
    return name, stamp


def format_timestamp(stamp: str) -> str:
    return f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]} {stamp[8:10]}:{stamp[10:12]}:{stamp[12:14]}"


def safe_child(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def project_trash_dir(root: Path) -> Path:
    return root / ".plan-manager" / "trash" / "projects"


def project_items(root: Path) -> list[TrashItem]:
    base = project_trash_dir(root)
    if not base.is_dir():
        return []
    items = []
    for path in sorted(p for p in base.iterdir() if p.is_dir()):
        name, stamp = parse_trash_name(path.name)
        items.append(TrashItem("project", name, stamp, path, root / "project" / name))
    return items


def task_items(root: Path) -> list[TrashItem]:
    base = root / "project"
    if not base.is_dir():
        return []
    items = []
    for project_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        trash = project_dir / "tasks" / ".trash"
        if not trash.is_dir():
            continue
        for path in sorted(p for p in trash.iterdir() if p.is_dir()):
            name, stamp = parse_trash_name(path.name)
            items.append(TrashItem("task", name, stamp, path, project_dir / "tasks" / name, project_dir.name))
    return items


def all_items(root: Path, item_type: str | None = None) -> list[TrashItem]:
    if item_type == "project":
        return project_items(root)
    if item_type == "task":
        return task_items(root)
    return project_items(root) + task_items(root)


def find_item(root: Path, query: str) -> TrashItem:
    matches = []
    for item in all_items(root):
        if query in {item.name, item.path.name, str(item.path)}:
            matches.append(item)
    if not matches:
        die(f"trash item not found: {query}")
    if len(matches) > 1:
        choices = ", ".join(item.path.name for item in matches)
        die(f"ambiguous trash item {query}: {choices}; use full trash directory name")
    return matches[0]


def cmd_list(args) -> None:
    items = all_items(Path(args.root), args.type)
    print("| Type | Name | Project | Deleted At | Path | Restore Target |")
    print("|------|------|---------|------------|------|----------------|")
    for item in items:
        print(
            f"| {item.kind} | {item.name} | {item.project or '—'} | "
            f"{format_timestamp(item.timestamp)} | {item.path} | {item.restore_path} |"
        )


def cmd_show(args) -> None:
    item = find_item(Path(args.root), args.item)
    print(f"Type: {item.kind}")
    print(f"Name: {item.name}")
    print(f"Project: {item.project or '—'}")
    print(f"Deleted At: {format_timestamp(item.timestamp)}")
    print(f"Path: {item.path}")
    print(f"Restore Target: {item.restore_path}")
    print("Contents:")
    for child in sorted(item.path.rglob("*"))[:80]:
        print(f"- {child.relative_to(item.path)}")


def cmd_restore(args) -> None:
    root = Path(args.root)
    item = find_item(root, args.item)
    if not safe_child(root, item.path):
        die("trash item path is outside root")
    if item.restore_path.exists():
        die(f"restore target already exists: {item.restore_path}")

    def apply_restore() -> None:
        item.restore_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(item.path), str(item.restore_path))

    maybe_apply(args.apply, f"restore {item.kind} {item.name} to {item.restore_path}", apply_restore)


def cmd_purge(args) -> None:
    root = Path(args.root)
    item = find_item(root, args.item)
    if not args.force:
        die("pass --force to permanently delete a trash item")
    if not safe_child(root, item.path):
        die("trash item path is outside root")

    def apply_purge() -> None:
        shutil.rmtree(item.path)

    maybe_apply(args.apply, f"permanently delete {item.kind} {item.name} from {item.path}", apply_purge)


def cmd_empty(args) -> None:
    root = Path(args.root)
    items = all_items(root, args.type)
    if not args.force:
        die("pass --force to empty trash")
    for item in items:
        if not safe_child(root, item.path):
            die(f"trash item path is outside root: {item.path}")

    def apply_empty() -> None:
        for item in items:
            shutil.rmtree(item.path)

    label = args.type or "all"
    maybe_apply(args.apply, f"permanently delete {len(items)} {label} trash item(s)", apply_empty)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage plan-manager trash")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.add_argument("--root", required=True)
    p.add_argument("--type", choices=["project", "task"])
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show")
    p.add_argument("--root", required=True)
    p.add_argument("item")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("restore")
    p.add_argument("--root", required=True)
    p.add_argument("item")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_restore)

    p = sub.add_parser("purge")
    p.add_argument("--root", required=True)
    p.add_argument("item")
    p.add_argument("--force", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_purge)

    p = sub.add_parser("empty")
    p.add_argument("--root", required=True)
    p.add_argument("--type", choices=["project", "task"])
    p.add_argument("--force", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_empty)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
