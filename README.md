# plan-manager

6-module project orchestration skill for Claude Code, Codex CLI, and Copilot CLI.
Project-centric, task-based execution with cross-project parallel coordination.

## Install

### Claude Code Plugin (recommended for Claude Code)

From within Claude Code:

```
/plugin marketplace add wangyuncepu/plan-manager
/plugin install plan-manager@plan-manager
```

Skill auto-registers immediately — no reload needed.

### Claude Code Manual (git clone)

```bash
git clone https://github.com/wangyuncepu/plan-manager.git
cd plan-manager
bash install.sh --target claude --mode symlink
/reload-plugins
```

`install.sh` creates a symlink or copy from the selected CLI skill directory to this repo. For Claude Code default: `~/.claude/skills/plan-manager` → this repo. Use `--target codex` or `--target copilot` for other CLIs.

### Codex CLI Plugin

From within Codex CLI:

```text
/plugins
```

Add this repository as a plugin marketplace if it is not listed yet:

```bash
codex plugin marketplace add wangyuncepu/plan-manager
```

Then search for `plan-manager` in `/plugins` and select `Install Plugin`.

The Codex plugin manifest lives at `.codex-plugin/plugin.json` and loads `skills/plan-manager`.

### Codex CLI Skill (manual)

Codex CLI can load standalone skills from `~/.codex/skills/`.

```bash
git clone https://github.com/wangyuncepu/plan-manager.git
cd plan-manager
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skills/plan-manager" ~/.codex/skills/plan-manager
```

If `~/.codex/skills/plan-manager` already exists, remove it first:

```bash
rm -rf ~/.codex/skills/plan-manager
```

If your Codex CLI environment does not support symlinked skills, copy the directory instead:

```bash
cp -R skills/plan-manager ~/.codex/skills/plan-manager
```

Restart Codex after installing. Invoke the skill with:

```text
$plan-manager
```

or open `/skills` and select `plan-manager`.

### Copilot CLI Plugin

From Copilot CLI:

```bash
copilot plugin marketplace add wangyuncepu/plan-manager
copilot plugin install plan-manager@plan-manager
```

Restart Copilot CLI if the skill does not appear immediately. The installed plugin loads `skills/plan-manager`.

Use the manual skill install below only if your Copilot CLI plugin marketplace install is unavailable.

Then invoke the skill with:

```text
$plan-manager
```

### Copilot CLI Skill (manual)

Copilot CLI can load skills from `~/.agents/skills/`.

```bash
git clone https://github.com/wangyuncepu/plan-manager.git
cd plan-manager
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/plan-manager" ~/.agents/skills/plan-manager
```

If `~/.agents/skills/plan-manager` already exists, remove it first:

```bash
rm -rf ~/.agents/skills/plan-manager
```

If your Copilot CLI environment does not support symlinked skills, copy the directory instead:

```bash
cp -R skills/plan-manager ~/.agents/skills/plan-manager
```

Restart Copilot CLI after installing. Invoke the skill with:

```text
$plan-manager
```

## Usage Manual

- [Full plan-manager manual](skills/plan-manager/references/manual.md)
- [Panel integration](skills/plan-manager/references/panels-integration.md)
- [Architecture](skills/plan-manager/references/architecture.md)


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
├── .codex-plugin/
│   └── plugin.json             ← Codex plugin manifest
├── skills/
│   └── plan-manager/
│       ├── SKILL.md            ← skill definition
│       ├── scripts/            ← deterministic helper scripts
│       ├── templates/          ← plan/project templates
│       └── references/         ← architecture, state, install notes
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
