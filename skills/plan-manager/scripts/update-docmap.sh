#!/usr/bin/env bash
# Regenerate DOCMAP.md index from all projects and tasks
# Usage: update-docmap.sh <root>
set -euo pipefail

ROOT="${1:?Usage: update-docmap.sh <root>}"
OUT="$ROOT/DOCMAP.md"

{
  echo "# Document Map"
  echo ""
  echo "Generated: $(date -Iseconds)"
  echo ""
  echo "## Projects"
  echo ""
  echo "| Project | Status | Goal | Tasks |"
  echo "|---------|--------|------|-------|"

  if [ -d "$ROOT/project" ]; then
    for proj_dir in "$ROOT"/project/*/; do
      [ -d "$proj_dir" ] || continue
      name=$(basename "$proj_dir")
      proj_file="$proj_dir/.project"
      if [ -f "$proj_file" ]; then
        status=$(grep "^status:" "$proj_file" | sed 's/^status:[[:space:]]*//')
        goal=$(grep "^goal:" "$proj_file" | head -1 | sed 's/^goal:[[:space:]]*//')
        task_count=$(find "$proj_dir" -name ".task" 2>/dev/null | wc -l)
        echo "| $name | $status | ${goal:-""} | $task_count |"
      else
        echo "| $name | unregistered | — | 0 |"
      fi
    done
  fi

  echo ""
  echo "## Tasks"
  echo ""
  if [ -d "$ROOT/project" ]; then
    while IFS= read -r task_file; do
      id=$(grep "^id:" "$task_file" | sed 's/id: //')
      title=$(grep "^title:" "$task_file" | sed 's/title: //')
      status=$(grep "^status:" "$task_file" | sed 's/status: //')
      project=$(grep "^project:" "$task_file" | sed 's/project: //')
      echo "- **$id** [$status] $title ($project)"
    done < <(find "$ROOT/project" -name ".task" 2>/dev/null | sort)
  fi
} > "$OUT"

echo "DOCMAP.md regenerated at $OUT"
