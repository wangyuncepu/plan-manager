#!/usr/bin/env bash
# Install plan-manager as a Claude Code plugin
# Usage: bash install.sh
# Or via Claude Code: /plugin install github:wangyuncepu/plan-manager
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="plan-manager"
SKILL_PATH="$SKILL_DIR/skills/$SKILL_NAME"

# Method 1: Symlink to ~/.claude/skills/ (manual install)
TARGET="$HOME/.claude/skills/$SKILL_NAME"
if [ -L "$TARGET" ] || [ -d "$TARGET" ]; then
  echo "plan-manager already installed at $TARGET"
  echo "To reinstall: rm -rf $TARGET && bash install.sh"
  exit 0
fi

ln -s "$SKILL_PATH" "$TARGET"
chmod +x "$SKILL_PATH/bin/"*.sh 2>/dev/null || true

echo ""
echo "plan-manager v3.0.0 installed."
echo "  Symlink: $TARGET → $SKILL_PATH"
echo ""
echo "Trigger phrases: 'assistant', 'add task to <project>', 'execute N projects'"
echo "First run: /reload-plugins then 'configure plan manager'"
