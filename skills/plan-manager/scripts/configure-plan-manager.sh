#!/usr/bin/env bash
# Configure plan-manager root, language, role, and optional GitHub remote owner
# Usage: configure-plan-manager.sh [--root PATH] [--language zh|en] [--role strategist|executor] [--github-enabled true|false] [--github-owner OWNER] [--github-check-remote true|false]
set -euo pipefail

ROOT=""
LANGUAGE="zh"
ROLE="strategist"
GITHUB_ENABLED="false"
GITHUB_OWNER=""
GITHUB_CHECK_REMOTE="true"
CONFIG_DIR="$HOME/.claude/plan-manager"
CONFIG_FILE="$CONFIG_DIR/config.json"

usage() {
  echo "Usage: configure-plan-manager.sh [--root PATH] [--language zh|en] [--role strategist|executor] [--github-enabled true|false] [--github-owner OWNER] [--github-check-remote true|false]" >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --root)
      ROOT="${2:?--root requires a path}"
      shift 2
      ;;
    --language|--lang)
      LANGUAGE="${2:?--language requires zh or en}"
      shift 2
      ;;
    --role)
      ROLE="${2:?--role requires strategist or executor}"
      shift 2
      ;;
    --github-enabled)
      GITHUB_ENABLED="${2:?--github-enabled requires true or false}"
      shift 2
      ;;
    --github-owner)
      GITHUB_OWNER="${2:?--github-owner requires an owner}"
      shift 2
      ;;
    --github-check-remote)
      GITHUB_CHECK_REMOTE="${2:?--github-check-remote requires true or false}"
      shift 2
      ;;
    --show)
      LANG_FROM_CONFIG=$(node -e "try{const c=require('$CONFIG_FILE');process.stdout.write(c.language||'zh')}catch(e){process.stdout.write('zh')}" 2>/dev/null || echo zh)
      "$(cd "$(dirname "$0")" && pwd)/config-panel.py" --lang "$LANG_FROM_CONFIG"
      exit 0
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

if [ -z "$ROOT" ]; then
  printf "Plan manager root: " >&2
  read -r ROOT
fi

if [ -z "$ROOT" ]; then
  echo "Error: root path is required" >&2
  exit 1
fi

if [ "$LANGUAGE" != "zh" ] && [ "$LANGUAGE" != "en" ]; then
  echo "Error: language must be zh or en" >&2
  exit 1
fi

if [ "$ROLE" != "strategist" ] && [ "$ROLE" != "executor" ]; then
  echo "Error: role must be strategist or executor" >&2
  exit 1
fi

if [ "$GITHUB_ENABLED" != "true" ] && [ "$GITHUB_ENABLED" != "false" ]; then
  echo "Error: github-enabled must be true or false" >&2
  exit 1
fi

if [ "$GITHUB_CHECK_REMOTE" != "true" ] && [ "$GITHUB_CHECK_REMOTE" != "false" ]; then
  echo "Error: github-check-remote must be true or false" >&2
  exit 1
fi

mkdir -p "$ROOT/project" "$ROOT/.plan-manager" "$CONFIG_DIR"

if [ ! -w "$ROOT" ]; then
  echo "Error: root directory $ROOT is not writable" >&2
  exit 1
fi

node -e "
const fs = require('fs');
const cfg = {
  root: process.argv[1],
  role: process.argv[2],
  parallelism: 2,
  autonomy: 'full',
  max_iterations_per_task: 30,
  overnight: false,
  language: process.argv[3],
  github: {
    enabled: process.argv[4] === 'true',
    owner: process.argv[5],
    repo_match: 'project-name',
    check_remote: process.argv[6] === 'true'
  }
};
const target = process.argv[7];
const tmp = target + '.tmp';
fs.writeFileSync(tmp, JSON.stringify(cfg, null, 2) + '\n');
fs.renameSync(tmp, target);
" "$ROOT" "$ROLE" "$LANGUAGE" "$GITHUB_ENABLED" "$GITHUB_OWNER" "$GITHUB_CHECK_REMOTE" "$CONFIG_FILE"

echo "Configured plan-manager: $CONFIG_FILE"
echo "root: $ROOT"
echo "role: $ROLE"
echo "language: $LANGUAGE"
echo "github.enabled: $GITHUB_ENABLED"
echo "github.owner: ${GITHUB_OWNER:-—}"
