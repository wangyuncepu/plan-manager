# plan-manager

6-module project orchestration skill for Claude Code.
Project-centric, task-based execution with cross-project parallel coordination.

## Install

### Option A: Claude Code Plugin (recommended)

From within Claude Code:

```
/plugin marketplace add wangyuncepu/plan-manager
/plugin install plan-manager@plan-manager
```

Skill auto-registers immediately — no reload needed.

### Option B: Manual (git clone)

```bash
git clone https://github.com/wangyuncepu/plan-manager.git
cd plan-manager
bash install.sh
/reload-plugins
```

`install.sh` creates a symlink from `~/.claude/skills/plan-manager` → this repo. Only needed for manual installs; plugin install handles everything automatically.

## Modules

| # | Module | Role |
|---|--------|------|
| 1 | **Project** | Project registry, lifecycle (active/idle/completed/archived) |
| 2 | **Task** | Task CRUD, priority/dependency ordering, 1 active per project |
| 3 | **Plan** | Mandatory plan.md per task, plan approval before execution |
| 4 | **Execute** | Launch top-ranked tasks across N projects in parallel |
| 5 | **Check** | Loop detection, auto-checkpoint, state persistence |
| 6 | **Assistant** | Interactive AI guide — overview, suggestions, iteration |

## Quick start

```
configure plan manager          → set root directory
create project <name>           → add a project
add task to <project>           → create a task (status: pending)
make plan for <TASK-ID>         → write plan.md (status: ready)
execute 2 projects              → run top tasks from 2 projects
assistant                       → overview + what to do next
```

## Directory structure

```
plan-manager/
├── .claude-plugin/
│   ├── plugin.json             ← plugin manifest
│   └── marketplace.json        ← marketplace listing
├── skills/
│   └── plan-manager/
│       ├── SKILL.md            ← skill definition
│       ├── bin/                ← helper scripts
│       └── templates/          ← plan/project templates
├── install.sh
└── README.md
```

## Management root structure

```
<root>/
├── project/<proj>/
│   ├── .project                ← project metadata
│   ├── tasks/<task>/
│   │   ├── .task               ← task metadata
│   │   └── plan.md             ← required execution plan
│   └── ...
├── STATE.json                  ← execution state + checkpoints
└── DOCMAP.md                   ← document index
```
