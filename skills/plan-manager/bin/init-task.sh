#!/usr/bin/env bash
# Initialize a task scaffold under an existing project
# Usage: init-task.sh <root> <project> <title>
set -euo pipefail

ROOT="${1:?Usage: init-task.sh <root> <project> <title>}"
PROJECT="${2:?Usage: init-task.sh <root> <project> <title>}"
TITLE="${3:?Usage: init-task.sh <root> <project> <title>}"
TODAY=$(date +%Y-%m-%d)

PROJ_DIR="$ROOT/project/$PROJECT"
if [ ! -d "$PROJ_DIR" ]; then
  echo "Error: project directory $PROJ_DIR does not exist"
  exit 1
fi

# Generate slug
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | tr -s '-' | sed 's/^-//;s/-$//')
# Auto-assign task ID
PREFIX=$(echo "$PROJECT" | tr '[:lower:]' '[:upper:]' | sed 's/[^A-Z0-9]//g' | head -c3)
LAST_NUM=$(find "$PROJ_DIR/tasks" -name ".task" -exec grep "^id:" {} \; 2>/dev/null | sed "s/id: $PREFIX-//" | sort -n | tail -1)
NEXT_NUM=$(printf "%03d" $(( ${LAST_NUM:-0} + 1 )))
TASK_DIR="$PROJ_DIR/tasks/$SLUG"

mkdir -p "$TASK_DIR/checkpoints"

cat > "$TASK_DIR/.task" << EOF
id: $PREFIX-$NEXT_NUM
title: $TITLE
project: $PROJECT
status: pending
priority: P1
order: $((NEXT_NUM + 0))
created: $TODAY
deadline:
completed:
depends_on: []
depends_on_cross: []
description: |
notes: |
plan_file:
max_iterations: 0
EOF

echo "Task $PREFIX-$NEXT_NUM '$TITLE' created at $TASK_DIR"
