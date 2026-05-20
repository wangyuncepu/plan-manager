#!/usr/bin/env bash
# Initialize a new project in the plan-manager root.
# Usage: bash init-project.sh <root> <project-name>
set -euo pipefail

ROOT="${1:?Usage: init-project.sh <root> <project-name>}"
NAME="${2:?Usage: init-project.sh <root> <project-name>}"
SLUG=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

PROJ_DIR="$ROOT/project/$SLUG"

if [ -d "$PROJ_DIR" ]; then
  echo "Project '$SLUG' already exists at $PROJ_DIR"
  exit 1
fi

mkdir -p "$PROJ_DIR/tasks"

cat > "$PROJ_DIR/.project" << EOF
name: $NAME
slug: $SLUG
status: active
priority: P2
created: $(date +%Y-%m-%d)
description: |
  TODO: describe this project
notes: ""
EOF

cat > "$PROJ_DIR/README.md" << EOF
# $NAME

TODO: Project description and goals.
EOF

echo "Project '$NAME' ($SLUG) created at $PROJ_DIR"
