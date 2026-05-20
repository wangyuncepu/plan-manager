#!/usr/bin/env bash
# Generate DOCMAP.md — scan project for documentation files and produce index.
# Usage: bash update-docmap.sh [project-root]

set -euo pipefail
ROOT="${1:-.}"
cd "$ROOT"

OUT="DOCMAP.md"
NOW=$(date "+%Y-%m-%d %H:%M")

echo "# Document Directory" > "$OUT"
echo "" >> "$OUT"
echo "> Auto-generated: $NOW. Rebuild: \"update doc index\"" >> "$OUT"
echo "" >> "$OUT"

# Collect doc files
mapfile -t FILES < <(find . -type f \( -name "*.md" -o -name "*.pdf" -o -name "*.pptx" -o -name "*.txt" -o -name "*.rst" \) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/.claude/skills/*" ! -path "*/DOCMAP.md" ! -path "*/PLANS.md" 2>/dev/null | sort)

# Build category map
declare -A CATEGORIES
for f in "${FILES[@]}"; do
  dir=$(dirname "$f")
  # Extract top-level category
  if [[ "$dir" == "." ]]; then
    cat="Root"
  else
    cat=$(echo "$dir" | cut -d'/' -f2)
    # Capitalize first letter
    cat="${cat^}"
  fi
  CATEGORIES["$cat"]+="$f"$'\n'
done

# Count
TOTAL=${#FILES[@]}
echo "## Summary" >> "$OUT"
echo "" >> "$OUT"
echo "- **$TOTAL** documents across **${#CATEGORIES[@]}** categories" >> "$OUT"
echo "" >> "$OUT"

echo "## By Category" >> "$OUT"
echo "" >> "$OUT"

for cat in $(echo "${!CATEGORIES[@]}" | tr ' ' '\n' | sort); do
  echo "### $cat" >> "$OUT"
  echo "" >> "$OUT"
  echo "| File | Title | Modified |" >> "$OUT"
  echo "|------|-------|----------|" >> "$OUT"

  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    # Get title: first # heading
    title=$(head -50 "$f" 2>/dev/null | grep -m1 '^# ' | sed 's/^# //' || echo "")
    [[ -z "$title" ]] && title=$(basename "$f" | sed 's/\.[^.]*$//')
    # Get git last modified
    mdate=$(git log -1 --format="%ad" --date=short -- "$f" 2>/dev/null || date -r "$f" "+%Y-%m-%d" 2>/dev/null || echo "-")
    echo "| [$(basename "$f")]($f) | $title | $mdate |" >> "$OUT"
  done <<< "${CATEGORIES[$cat]}"

  echo "" >> "$OUT"
done

echo "## Flat File Index" >> "$OUT"
echo "" >> "$OUT"
echo "| Path | Title | Category | Modified |" >> "$OUT"
echo "|------|-------|----------|----------|" >> "$OUT"

for f in "${FILES[@]}"; do
  dir=$(dirname "$f")
  if [[ "$dir" == "." ]]; then
    cat="Root"
  else
    cat=$(echo "$dir" | cut -d'/' -f2)
    cat="${cat^}"
  fi
  title=$(head -50 "$f" 2>/dev/null | grep -m1 '^# ' | sed 's/^# //' || echo "")
  [[ -z "$title" ]] && title=$(basename "$f" | sed 's/\.[^.]*$//')
  mdate=$(git log -1 --format="%ad" --date=short -- "$f" 2>/dev/null || date -r "$f" "+%Y-%m-%d" 2>/dev/null || echo "-")
  echo "| [$f]($f) | $title | $cat | $mdate |" >> "$OUT"
done

echo "" >> "$OUT"

echo "DOCMAP.md generated: $TOTAL files, ${#CATEGORIES[@]} categories."
