# plan-manager Architecture

plan-manager is a Claude skill for project-root orchestration under a managed root:

```text
<root>/
├── project/<project>/
│   ├── .project
│   └── tasks/
│       ├── <task>/
│       │   ├── .task
│       │   ├── plan.md
│       │   └── checkpoints/
│       └── .trash/<slug>-<timestamp>/   # soft-deleted tasks
├── STATE.json
├── OVERNIGHT-REPORT.md
├── DOCMAP.md
└── .plan-manager/
    └── trash/projects/<name>-<timestamp>/   # soft-deleted projects
```

## Roles

- `strategist`: analyze, plan, discuss direction, create project/task metadata after explicit user request.
- `executor`: execute approved task plans, maintain checkpoints, enforce file isolation.

## Standard Skill Layout

```text
skills/plan-manager/
├── SKILL.md
├── scripts/
├── templates/
└── references/
```

All Project/Task metadata writes should go through `scripts/project-manage.py` or `scripts/task-manage.py`. Direct edits to `.project` / `.task` are reserved for recovery from malformed files that the scripts cannot parse. Write operations dry-run by default and require `--apply`.

## Trash Management

Deletes are soft deletes:

- Project delete moves to `<root>/.plan-manager/trash/projects/<name>-<timestamp>`.
- Task delete moves to `<root>/project/<project>/tasks/.trash/<slug>-<timestamp>`.

Use `scripts/trash-manage.py` for trash lifecycle:

- `list` and `show` are read-only.
- `restore` is dry-run by default; `--apply` restores the item if the target path does not exist.
- `purge` and `empty` permanently delete trash items and require `--force`; they are still dry-run unless `--apply` is present.

Original names are inferred from the `<name>-YYYYMMDDHHMMSS` directory suffix. Trash management is root-scoped; never restore/purge paths outside the configured root.


## Remote Panel

GitHub remote management is read-only by default. Config lives in `~/.claude/plan-manager/config.json`:

```json
{
  "github": {
    "enabled": true,
    "owner": "wangyuncepu",
    "repo_match": "project-name",
    "check_remote": true
  }
}
```

When enabled, `scripts/github-verify.py` compares each `<root>/project/<name>` directory with expected repo `<owner>/<name>`, reads local `origin`, and optionally calls `gh repo view` to confirm remote existence. It never creates repos, changes remotes, fetches, or pushes.

GitHub management actions go through `scripts/github-manage.sh` (set-origin, add-origin, create-repo, push, status, list). All write subcommands are dry-run by default and only mutate with `--apply`. Avoid ad-hoc `git remote`/`gh repo` commands for remote management.
