#!/usr/bin/env bash
# Initialize a plan-manager project scaffold
# Usage: init-project.sh <root> <name>
set -euo pipefail

ROOT="${1:?Usage: init-project.sh <root> <name>}"
NAME="${2:?Usage: init-project.sh <root> <name>}"
SLUG=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
TODAY=$(date +%Y-%m-%d)
PROJ_DIR="$ROOT/project/$NAME"

mkdir -p "$PROJ_DIR/tasks"

# .project
if [ ! -f "$PROJ_DIR/.project" ]; then
  cat > "$PROJ_DIR/.project" << EOF
name: $NAME
slug: $SLUG
status: active
priority: P1
created: $TODAY
goal:
description: |
notes: |
EOF
  echo "Created $PROJ_DIR/.project"
fi

# README.md
if [ ! -f "$PROJ_DIR/README.md" ]; then
  echo "# $NAME" > "$PROJ_DIR/README.md"
  echo "Created $PROJ_DIR/README.md"
fi

echo "Project '$NAME' scaffolded at $PROJ_DIR"
