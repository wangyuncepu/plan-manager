#!/usr/bin/env bash
# Script-driven GitHub management for plan-manager projects.
# Read commands run immediately. Write commands are dry-run by default; pass --apply to execute.
#
# Usage:
#   github-manage.sh status   [--root R] [--owner O] [--project NAME]
#   github-manage.sh list     [--owner O]
#   github-manage.sh set-origin <project> [--root R] [--owner O] [--apply]
#   github-manage.sh add-origin <project> [--root R] [--owner O] [--apply]
#   github-manage.sh create-repo <project> [--owner O] [--private|--public] [--apply]
#   github-manage.sh push <project> [--root R] [--branch B] [--apply]
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$HOME/.claude/plan-manager/config.json"

ROOT=""
OWNER=""
PROJECT=""
BRANCH=""
VISIBILITY="--private"
APPLY="false"

config_value() {
  # config_value <dotted.key>
  [ -f "$CONFIG_FILE" ] || return 0
  node -e "
    try {
      const c = require(process.argv[1]);
      const keys = process.argv[2].split('.');
      let v = c;
      for (const k of keys) { v = (v == null ? undefined : v[k]); }
      if (v != null && v !== '') process.stdout.write(String(v));
    } catch (e) {}
  " "$CONFIG_FILE" "$1" 2>/dev/null || true
}

die() { echo "Error: $*" >&2; exit 1; }

validate_owner() {
  [[ "$1" =~ ^[A-Za-z0-9]([-A-Za-z0-9]{0,38})$ ]] || die "invalid owner: $1"
}

validate_project_name() {
  case "$1" in
    *"/"*|*".."*) die "invalid project name: $1" ;;
  esac
  [[ "$1" =~ ^[A-Za-z0-9._-]+$ ]] || die "invalid project name: $1"
}

validate_branch() {
  [[ "$1" =~ ^[A-Za-z0-9._/-]+$ ]] || die "invalid branch name: $1"
}

run_or_echo() {
  # run_or_echo <description> <cmd...>
  local desc="$1"; shift
  if [ "$APPLY" = "true" ]; then
    echo "RUN: $desc"
    "$@"
  else
    echo "DRY-RUN: $desc"
    printf '       '
    printf '%q ' "$@"
    printf '\n'
  fi
}

project_dir() {
  echo "$ROOT/project/$1"
}

resolve_common() {
  [ -n "$ROOT" ] || ROOT="$(config_value root)"
  [ -n "$ROOT" ] || ROOT="$(pwd)"
  [ -n "$OWNER" ] || OWNER="$(config_value github.owner)"
}

require_owner() {
  [ -n "$OWNER" ] || die "owner required (pass --owner or set github.owner in config)"
  validate_owner "$OWNER"
}

require_project_dir() {
  validate_project_name "$1"
  local dir; dir="$(project_dir "$1")"
  [ -d "$dir" ] || die "project directory not found: $dir"
}

cmd_status() {
  resolve_common
  require_owner
  local verify="$SKILL_DIR/github-verify.py"
  [ -x "$verify" ] || die "github-verify.py not found"
  local lang
  lang="$(config_value language)"; [ -n "$lang" ] || lang="zh"
  if [ -n "$PROJECT" ]; then
    "$verify" --root "$ROOT" --owner "$OWNER" --project "$PROJECT" --lang "$lang"
  else
    "$verify" --root "$ROOT" --owner "$OWNER" --lang "$lang"
  fi
}

cmd_list() {
  resolve_common
  require_owner
  gh repo list "$OWNER" --limit 100
}

cmd_set_origin() {
  local project="$1"
  resolve_common
  require_owner
  require_project_dir "$project"
  local dir url; dir="$(project_dir "$project")"
  url="git@github.com:$OWNER/$project.git"
  run_or_echo "set origin of $project -> $url" git -C "$dir" remote set-url origin "$url"
}

cmd_add_origin() {
  local project="$1"
  resolve_common
  require_owner
  require_project_dir "$project"
  local dir url; dir="$(project_dir "$project")"
  url="git@github.com:$OWNER/$project.git"
  run_or_echo "add origin of $project -> $url" git -C "$dir" remote add origin "$url"
}

cmd_create_repo() {
  local project="$1"
  resolve_common
  require_owner
  validate_project_name "$project"
  run_or_echo "create GitHub repo $OWNER/$project ($VISIBILITY)" gh repo create "$OWNER/$project" "$VISIBILITY"
}

cmd_push() {
  local project="$1"
  resolve_common
  require_project_dir "$project"
  local dir; dir="$(project_dir "$project")"
  [ -n "$BRANCH" ] || BRANCH="$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
  validate_branch "$BRANCH"
  run_or_echo "push $project ($BRANCH) to origin" git -C "$dir" push -u origin "$BRANCH"
}

has_own_git() {
  # true if <dir>/.git exists as a real git dir for this project (not the parent monorepo)
  local dir="$1"
  local gd
  gd="$(git -C "$dir" rev-parse --absolute-git-dir 2>/dev/null || echo "")"
  [ "$gd" = "$dir/.git" ]
}

cmd_init_split() {
  # Turn a monorepo subdirectory into its own standalone git repo with an initial commit.
  local project="$1"
  resolve_common
  require_project_dir "$project"
  local dir; dir="$(project_dir "$project")"
  if has_own_git "$dir"; then
    echo "SKIP: $project already has its own git repo"
    return 0
  fi
  local ignore=".gstack/
STATE.json
.claude/
__pycache__/
"
  if [ "$APPLY" = "true" ]; then
    echo "RUN: init-split $project"
    git -C "$dir" init -b main
    if [ -e "$dir/.gitignore" ]; then
      echo "       SKIP .gitignore (already exists, leaving untouched)"
    else
      printf '%s' "$ignore" > "$dir/.gitignore"
    fi
    git -C "$dir" add -A
    git -C "$dir" commit -m "Initial import of $project" >/dev/null
    echo "       committed $(git -C "$dir" rev-list --count HEAD) commit"
  else
    echo "DRY-RUN: init-split $project"
    echo "       git -C $dir init -b main"
    if [ -e "$dir/.gitignore" ]; then
      echo "       KEEP existing $dir/.gitignore (will not overwrite)"
    else
      echo "       write $dir/.gitignore (.gstack/, STATE.json, .claude/, __pycache__/)"
    fi
    echo "       git -C $dir add -A && git -C $dir commit -m 'Initial import of $project'"
  fi
}

[ "$#" -ge 1 ] || die "missing subcommand (status|list|set-origin|add-origin|create-repo|push)"
SUB="$1"; shift

POSITIONAL=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2:?--root requires a path}"; shift 2 ;;
    --owner) OWNER="${2:?--owner requires an owner}"; shift 2 ;;
    --project) PROJECT="${2:?--project requires a name}"; shift 2 ;;
    --branch) BRANCH="${2:?--branch requires a name}"; shift 2 ;;
    --private) VISIBILITY="--private"; shift ;;
    --public) VISIBILITY="--public"; shift ;;
    --apply) APPLY="true"; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "unknown option $1" ;;
    *) POSITIONAL="$1"; shift ;;
  esac
done

case "$SUB" in
  status) cmd_status ;;
  list) cmd_list ;;
  set-origin) [ -n "$POSITIONAL" ] || die "set-origin requires <project>"; cmd_set_origin "$POSITIONAL" ;;
  add-origin) [ -n "$POSITIONAL" ] || die "add-origin requires <project>"; cmd_add_origin "$POSITIONAL" ;;
  create-repo) [ -n "$POSITIONAL" ] || die "create-repo requires <project>"; cmd_create_repo "$POSITIONAL" ;;
  init-split) [ -n "$POSITIONAL" ] || die "init-split requires <project>"; cmd_init_split "$POSITIONAL" ;;
  push) [ -n "$POSITIONAL" ] || die "push requires <project>"; cmd_push "$POSITIONAL" ;;
  *) die "unknown subcommand: $SUB" ;;
esac
