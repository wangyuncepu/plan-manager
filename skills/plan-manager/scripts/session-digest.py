#!/usr/bin/env python3
"""Extract a digest of the most recent Claude Code session for a project.

Usage:
    session-digest.py <project-name> [--max-user-msgs N] [--lang zh|en]
                      [--full-path] [--root <path>]

Output (stdout, markdown):
    session: <sessionId> | none
    last_active: <ISO timestamp>
    relative_time: <e.g. "2 days ago" or "2天前">
    user_msg_count: <int>
    corrupt_lines: <int>
    ## Recent Messages
    - [<ts>] <snippet>
    ...
    ## Last AI Response
    <text>

Exit 0 always (no session is not an error). Exit 1 only on arg errors.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SYSTEM_PREFIXES = (
    "<local-command-caveat>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<system-reminder>",
    "<environment_context>",
    "<command-message>",
    "<command-name>",
    "<command-args>",
    "<bash-input>",
    "<bash-stdout>",
    "<bash-stderr>",
    "<skill>",
    "<user_instructions>",
    "<permissions instructions>",
)
USER_SNIPPET_CHARS = 200
AI_SNIPPET_CHARS = 500
LARGE_FILE_MB = 10
TAIL_LINES_LIMIT = 5000


def default_root():
    """Resolve default plan-manager root from env, then config. No personal fallback."""
    env_root = os.environ.get("PLAN_MANAGER_ROOT")
    if env_root:
        return env_root

    config_path = Path.home() / ".claude" / "plan-manager" / "config.json"
    try:
        with config_path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
        root = cfg.get("root")
        if isinstance(root, str) and root.strip():
            return root
    except (OSError, json.JSONDecodeError):
        pass

    return ""


def session_dir(project_name: str, root: str) -> Path:
    """Compute cc session directory for a project under <root>/project/<name>."""
    home = Path.home()
    cwd = Path(root) / "project" / project_name
    encoded = str(cwd).replace("/", "-").lstrip("-")
    return home / ".claude" / "projects" / f"-{encoded}"


def pick_latest_jsonl(d: Path):
    if not d.is_dir():
        return None
    files = [p for p in d.iterdir() if p.is_file() and p.suffix == ".jsonl"]
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def relative_time(ts_iso: str, lang: str) -> str:
    try:
        ts = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
    except Exception:
        return "?"
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - ts
    secs = int(delta.total_seconds())
    if secs < 0:
        return "in future"
    if lang == "zh":
        if secs < 60: return f"{secs}秒前"
        if secs < 3600: return f"{secs//60}分钟前"
        if secs < 86400: return f"{secs//3600}小时前"
        if secs < 86400*30: return f"{secs//86400}天前"
        return f"{secs//(86400*30)}月前"
    if secs < 60: return f"{secs}s ago"
    if secs < 3600: return f"{secs//60}m ago"
    if secs < 86400: return f"{secs//3600}h ago"
    if secs < 86400*30: return f"{secs//86400}d ago"
    return f"{secs//(86400*30)}mo ago"


def is_real_user_text(content) -> bool:
    if not isinstance(content, str):
        return False
    s = content.lstrip()
    if not s:
        return False
    for p in SYSTEM_PREFIXES:
        if s.startswith(p):
            return False
    return True


def extract_assistant_text(content) -> str:
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            t = block.get("text", "")
            if t:
                parts.append(t)
    return "\n".join(parts).strip()


def tail_lines(path: Path, limit: int):
    """Read the last `limit` lines of a file efficiently."""
    with path.open("rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        block = 8192
        data = b""
        while size > 0 and data.count(b"\n") <= limit:
            read = min(block, size)
            size -= read
            f.seek(size)
            data = f.read(read) + data
        return data.decode("utf-8", errors="replace").splitlines()[-limit:]


def digest(jsonl: Path, max_user_msgs: int):
    user_msgs = []  # list of (ts, snippet)
    last_ai_text = ""
    corrupt = 0

    size_mb = jsonl.stat().st_size / (1024 * 1024)
    large = size_mb > LARGE_FILE_MB
    warning = ""
    if large:
        warning = f"warning: large file ({size_mb:.1f} MB), reading last {TAIL_LINES_LIMIT} lines only"
        lines = tail_lines(jsonl, TAIL_LINES_LIMIT)
    else:
        with jsonl.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            corrupt += 1
            continue
        t = d.get("type")
        msg = d.get("message", {})
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        ts = d.get("timestamp", "")
        if t == "user" and is_real_user_text(content):
            user_msgs.append((ts, content.strip()))
        elif t == "assistant":
            txt = extract_assistant_text(content)
            if txt:
                last_ai_text = txt

    return user_msgs, last_ai_text, corrupt, warning


def main():
    ap = argparse.ArgumentParser(description="Extract cc session digest for a project")
    ap.add_argument("project")
    ap.add_argument("--max-user-msgs", type=int, default=20)
    ap.add_argument("--lang", choices=["zh", "en"], default="en")
    ap.add_argument("--full-path", action="store_true",
                    help="Treat <project> as full path to a directory whose cc sessions to read")
    ap.add_argument("--root", default=default_root(),
                    help="Plan manager root path (default: PLAN_MANAGER_ROOT, config.json root, then legacy fallback)")
    args = ap.parse_args()

    if args.full_path:
        p = Path(args.project)
        encoded = str(p).replace("/", "-").lstrip("-")
        sdir = Path.home() / ".claude" / "projects" / f"-{encoded}"
    else:
        sdir = session_dir(args.project, args.root)

    jsonl = pick_latest_jsonl(sdir)
    if jsonl is None:
        print("session: none")
        return 0

    session_id = jsonl.stem
    user_msgs, last_ai_text, corrupt, warning = digest(jsonl, args.max_user_msgs)

    # If session has no real user messages (only system noise), treat as no session.
    if not user_msgs:
        print("session: none")
        return 0

    last_ts = user_msgs[-1][0] if user_msgs else ""
    rel = relative_time(last_ts, args.lang) if last_ts else "?"

    print(f"session: {session_id}")
    print(f"file: {jsonl}")
    print(f"last_active: {last_ts}")
    print(f"relative_time: {rel}")
    print(f"user_msg_count: {len(user_msgs)}")
    print(f"corrupt_lines: {corrupt}")
    if warning:
        print(f"warning: {warning}")
    print()

    if user_msgs:
        title = "近期消息" if args.lang == "zh" else "Recent Messages"
        print(f"## {title}")
        for ts, content in user_msgs[-args.max_user_msgs:]:
            ts_short = ts[:16] if ts else "?"
            snippet = content[:USER_SNIPPET_CHARS].replace("\n", " ")
            if len(content) > USER_SNIPPET_CHARS:
                snippet += "…"
            print(f"- [{ts_short}] {snippet}")
        print()

    if last_ai_text:
        title = "最后 AI 回应" if args.lang == "zh" else "Last AI Response"
        print(f"## {title}")
        out = last_ai_text[:AI_SNIPPET_CHARS]
        if len(last_ai_text) > AI_SNIPPET_CHARS:
            out += "…"
        print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
