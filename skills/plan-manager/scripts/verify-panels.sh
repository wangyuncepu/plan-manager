#!/usr/bin/env bash
# Verify plan-manager panel registry and fixed panels.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PANEL="$SCRIPT_DIR/panel-manage.py"

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

python3 -m py_compile "$PANEL" "$SCRIPT_DIR/config-panel.py" "$SCRIPT_DIR/_common.py"

"$PANEL" list >"$TMP"
for name in config overview projects tasks ready-queue remote github-status trash panels; do
  grep -q "| $name |" "$TMP" || { echo "missing fixed panel: $name"; exit 1; }
done

"$PANEL" run config | grep -q 'Core Config'
"$PANEL" run trash | grep -q 'Type'

echo "panel registry ok"
