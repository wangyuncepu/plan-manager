#!/usr/bin/env bash
# Verify plan-manager skill installation and standard folder format
# Usage: verify-installation.sh [--target PATH]
set -euo pipefail

TARGET="$(cd "$(dirname "$0")/.." && pwd)"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      TARGET="${2:?--target requires a path}"
      shift 2
      ;;
    -h|--help)
      echo "Usage: verify-installation.sh [--target PATH]"
      exit 0
      ;;
    *)
      echo "Error: unknown argument $1" >&2
      exit 1
      ;;
  esac
done

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[ -d "$TARGET" ] || fail "target does not exist: $TARGET"
[ -f "$TARGET/SKILL.md" ] || fail "missing SKILL.md"
[ -d "$TARGET/scripts" ] || fail "missing scripts/"
[ ! -d "$TARGET/bin" ] || fail "legacy bin/ directory still exists"
[ -d "$TARGET/templates" ] || fail "missing templates/"
[ -d "$TARGET/references" ] || fail "missing references/"

grep -q '^name: plan-manager$' "$TARGET/SKILL.md" || fail "missing name frontmatter"
grep -q '^preamble-tier:' "$TARGET/SKILL.md" || fail "missing preamble-tier frontmatter"
grep -q '^interactive:' "$TARGET/SKILL.md" || fail "missing interactive frontmatter"

if grep -R '<%=' "$TARGET/templates" >/dev/null 2>&1 || grep -R '%>' "$TARGET/templates" >/dev/null 2>&1; then
  fail "legacy template syntax found"
fi

if grep -R 'bin/' "$TARGET/SKILL.md" >/dev/null 2>&1; then
  fail "SKILL.md still references bin/"
fi

for script in configure-plan-manager.sh update-docmap.sh github-manage.sh verify-installation.sh verify-panels.sh; do
  [ -x "$TARGET/scripts/$script" ] || fail "script not executable: scripts/$script"
done

for script in project-overview.py ready-queue.py project-manage.py task-manage.py trash-manage.py panel-manage.py config-panel.py github-verify.py; do
  [ -x "$TARGET/scripts/$script" ] || fail "script not executable: scripts/$script"
done

[ -f "$TARGET/scripts/_common.py" ] || fail "missing scripts/_common.py shared lib"

echo "plan-manager installation ok: $TARGET"
