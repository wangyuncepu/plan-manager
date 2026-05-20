#!/usr/bin/env bash
# Initialize a new task in a project.
# Usage: bash init-task.sh <root> <project-slug> <task-title>
set -euo pipefail

ROOT="${1:?Usage: init-task.sh <root> <project-slug> <task-title>}"
PROJ="${2:?Usage: init-task.sh <root> <project-slug> <task-title>}"
TITLE="${3:?Usage: init-task.sh <root> <project-slug> <task-title>}"
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-40)

PROJ_DIR="$ROOT/project/$PROJ"

if [ ! -d "$PROJ_DIR" ]; then
  echo "Project '$PROJ' not found at $PROJ_DIR"
  exit 1
fi

# Determine next task number
N=$(ls -1d "$PROJ_DIR/tasks/"*/ 2>/dev/null | wc -l)
N=$((N + 1))
TASK_ID=$(echo "$PROJ" | tr '[:lower:]' '[:upper:]' | sed 's/[^A-Z0-9]//g' | cut -c1-4)-$(printf "%03d" $N)
TASK_DIR="$PROJ_DIR/tasks/$SLUG"

if [ -d "$TASK_DIR" ]; then
  echo "Task '$SLUG' already exists at $TASK_DIR"
  exit 1
fi

mkdir -p "$TASK_DIR"

cat > "$TASK_DIR/.task" << EOF
id: $TASK_ID
slug: $SLUG
title: $TITLE
project: $PROJ
status: pending
priority: P2
order: $N
created: $(date +%Y-%m-%d)
deadline: ""
completed: ""
depends_on: []
depends_on_cross: []
description: |
  TODO: describe this task
notes: ""
plan_file: ""
EOF

echo "Task '$TASK_ID': '$TITLE' created in project '$PROJ'"
echo "Directory: $TASK_DIR"
echo "Next: make plan for $TASK_ID"
