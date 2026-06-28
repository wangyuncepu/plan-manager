#!/usr/bin/env python3
"""Read-only GitHub remote verification for plan-manager projects."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


GITHUB_RE = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?/?$")


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 10) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)


def parse_github_url(url: str) -> tuple[str, str] | None:
    match = GITHUB_RE.search(url.strip())
    if not match:
        return None
    return match.group("owner"), match.group("repo")


def github_repo(owner: str, repo: str, check_remote: bool) -> dict:
    result = {
        "expected": f"{owner}/{repo}",
        "exists": None,
        "url": "",
        "visibility": "",
        "archived": None,
        "error": "",
    }
    if not check_remote:
        return result

    code, out, err = run(["gh", "repo", "view", f"{owner}/{repo}", "--json", "nameWithOwner,url,visibility,isArchived"], timeout=12)
    if code != 0:
        result["exists"] = False
        result["error"] = err or out
        return result

    try:
        data = json.loads(out)
    except json.JSONDecodeError as exc:
        result["error"] = str(exc)
        return result

    result.update(
        {
            "exists": True,
            "url": data.get("url", ""),
            "visibility": data.get("visibility", ""),
            "archived": data.get("isArchived"),
        }
    )
    return result


def verify_project(project_dir: Path, owner: str, check_remote: bool) -> dict:
    name = project_dir.name
    expected = github_repo(owner, name, check_remote)
    item = {
        "project": name,
        "path": str(project_dir),
        "git": False,
        "origin": "",
        "origin_owner": "",
        "origin_repo": "",
        "expected_repo": expected["expected"],
        "github_exists": expected["exists"],
        "github_url": expected["url"],
        "github_error": expected["error"],
        "status": "not_git",
        "message": "not a git repository",
    }

    code, _, _ = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=project_dir)
    if code != 0:
        return item

    item["git"] = True
    code, origin, err = run(["git", "remote", "get-url", "origin"], cwd=project_dir)
    if code != 0 or not origin:
        item.update({"status": "missing_origin", "message": err or "missing origin"})
        return item

    item["origin"] = origin
    parsed = parse_github_url(origin)
    if parsed:
        item["origin_owner"], item["origin_repo"] = parsed

    if not parsed:
        item.update({"status": "origin_mismatch", "message": "origin is not a GitHub URL"})
    elif parsed != (owner, name):
        item.update({"status": "origin_mismatch", "message": f"origin points to {parsed[0]}/{parsed[1]}"})
    elif expected["exists"] is True:
        item.update({"status": "ok", "message": "origin matches expected repo"})
    elif expected["exists"] is False:
        if "Could not resolve to a Repository" in expected["error"] or "Not Found" in expected["error"]:
            item.update({"status": "repo_missing", "message": "expected repo not found or no access"})
        else:
            item.update({"status": "github_unknown", "message": expected["error"] or "GitHub check failed"})
    else:
        item.update({"status": "github_unknown", "message": "GitHub check disabled"})

    return item


def projects(root: Path, project: str | None) -> list[Path]:
    base = root / "project"
    if project:
        return [base / project]
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if p.is_dir())


def print_markdown(items: list[dict], lang: str) -> None:
    print("## Remote Panel" if lang == "en" else "## 远程仓库")
    print("| Project | Status | Expected | Origin | GitHub | Message |")
    print("|---------|--------|----------|--------|--------|---------|")
    for item in items:
        github = item["github_url"] or ("exists" if item["github_exists"] else "—")
        print(
            f"| {item['project']} | {item['status']} | {item['expected_repo']} | "
            f"{item['origin'] or '—'} | {github} | {item['message']} |"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify project GitHub remotes without mutating anything")
    ap.add_argument("--root", required=True)
    ap.add_argument("--owner", required=True)
    ap.add_argument("--project")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-remote-check", action="store_true")
    args = ap.parse_args()

    items = [verify_project(path, args.owner, not args.no_remote_check) for path in projects(Path(args.root), args.project)]
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        print_markdown(items, args.lang)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
