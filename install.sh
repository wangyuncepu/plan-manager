#!/usr/bin/env bash
# Install plan-manager skill
# Usage: bash install.sh [--target claude|codex|copilot] [--mode symlink|copy] [--force]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="plan-manager"
SKILL_PATH="$REPO_DIR/skills/$SKILL_NAME"
TARGET_KIND="claude"
MODE="symlink"
FORCE="false"

usage() {
  echo "Usage: bash install.sh [--target claude|codex|copilot] [--mode symlink|copy] [--force]" >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      TARGET_KIND="${2:?--target requires claude, codex, or copilot}"
      shift 2
      ;;
    --mode)
      MODE="${2:?--mode requires symlink or copy}"
      shift 2
      ;;
    --force)
      FORCE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument $1" >&2
      usage
      exit 1
      ;;
  esac
done

case "$TARGET_KIND" in
  claude) TARGET_BASE="$HOME/.claude/skills" ;;
  codex) TARGET_BASE="$HOME/.codex/skills" ;;
  copilot) TARGET_BASE="$HOME/.agents/skills" ;;
  *) echo "Error: --target must be claude, codex, or copilot" >&2; exit 1 ;;
esac

case "$MODE" in
  symlink|copy) ;;
  *) echo "Error: --mode must be symlink or copy" >&2; exit 1 ;;
esac

[ -d "$SKILL_PATH" ] || { echo "Error: skill path missing: $SKILL_PATH" >&2; exit 1; }
mkdir -p "$TARGET_BASE"
TARGET="$TARGET_BASE/$SKILL_NAME"

if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
  if [ "$FORCE" != "true" ]; then
    echo "plan-manager already installed at $TARGET"
    echo "Use --force to replace it."
    "$SKILL_PATH/scripts/verify-installation.sh" --target "$TARGET" || true
    exit 0
  fi
  rm -rf "$TARGET"
fi

chmod +x "$SKILL_PATH/scripts"/*

if [ "$MODE" = "symlink" ]; then
  ln -s "$SKILL_PATH" "$TARGET"
else
  cp -R "$SKILL_PATH" "$TARGET"
fi

"$SKILL_PATH/scripts/verify-installation.sh" --target "$TARGET"

echo ""
echo "plan-manager v4.4.0 installed."
echo "  Target: $TARGET_KIND"
echo "  Mode: $MODE"
echo "  Path: $TARGET"
echo ""
echo "Trigger phrases: 'assistant', 'add task to <project>', 'execute N projects'"
echo "First run: /reload-plugins then 'configure plan manager'"
