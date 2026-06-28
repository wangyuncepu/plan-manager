#!/usr/bin/env python3
"""Shared helpers for plan-manager scripts.

Import via:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _common import die, slugify, read_data, atomic_write, ...
"""

import shutil
from datetime import datetime
from pathlib import Path


def die(message: str) -> None:
    raise SystemExit(f"Error: {message}")


def slugify(value: str) -> str:
    chars = []
    last_dash = False
    for ch in value.lower():
        if ch.isalnum():
            chars.append(ch)
            last_dash = False
        elif not last_dash:
            chars.append("-")
            last_dash = True
    return "".join(chars).strip("-")


def validate_name(name: str, label: str = "name") -> None:
    if not name or "/" in name or ".." in name or any(ord(ch) < 32 for ch in name):
        die(f"invalid {label}")
    if not slugify(name):
        die(f"{label} produces empty slug")


def read_data(path: Path) -> dict:
    """Parse a YAML-like `.project`/`.task` file, preserving `field: |` block scalars."""
    data = {}
    if not path.exists():
        return data
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line or line.startswith(" ") or ":" not in line:
            i += 1
            continue
        key, raw = line.split(":", 1)
        value = raw.strip()
        if value == "|":
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i] == ""):
                block.append(lines[i][2:] if lines[i].startswith("  ") else lines[i].lstrip())
                i += 1
            data[key] = "\n".join(block).rstrip()
            continue
        data[key] = value
        i += 1
    return data


def read_field(path: Path, field: str) -> str:
    """Read a single field (block-scalar aware) from a YAML-like file."""
    return read_data(path).get(field, "")


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dst = path.with_name(f"{path.name}.bak.{stamp}")
    shutil.copy2(path, dst)
    return dst


def maybe_apply(apply: bool, description: str, fn) -> None:
    if not apply:
        print(f"DRY-RUN: {description}")
        print("         pass --apply to execute")
        return
    fn()
    print(f"APPLIED: {description}")


def parse_list(value: str) -> list[str]:
    """Parse a `[a, b, c]` style list field into a list of strings."""
    value = (value or "").strip()
    if value in {"", "[]"}:
        return []
    if value.startswith("[") and value.endswith("]"):
        return [part.strip().strip('"\'') for part in value[1:-1].split(",") if part.strip()]
    return [value]


def list_string(values: list[str]) -> str:
    return "[" + ", ".join(values) + "]" if values else "[]"
