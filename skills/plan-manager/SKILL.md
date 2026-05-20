---
name: plan-manager
version: 3.0.0
description: |
  6-module project orchestration system. Project-centric, task-based execution
  with cross-project parallel coordination.
  1. Project — project registry and lifecycle
  2. Task — task management with priority/dependency ordering, one active per project
  3. Plan — mandatory planning before execution, plan-task binding
  4. Execute — launch top-ranked tasks across N projects in parallel
  5. Check — infinite-loop detection, auto-checkpoint, debug state
  6. Assistant — interactive AI guide for project review and iteration
triggers:
  - manage plans
  - plan manager
  - project status
  - list projects
  - create project
  - add task
  - create task
  - new task
  - task status
  - list tasks
  - start task
  - complete task
  - make plan
  - create plan for
  - execute tasks
  - run tasks
  - start execution
  - check tasks
  - task health
  - assistant
  - plan assistant
  - what should I do
  - what's next
  - project overview
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /plan-manager — 6-Module Project Orchestration System

## Architecture

```
<root>/
├── project/                       ← all projects
│   └── <project-name>/
│       ├── .project               ← project metadata (YAML)
│       ├── README.md              ← project description
│       ├── tasks/                 ← project tasks
│       │   └── <task-slug>/
│       │       ├── .task          ← task metadata (YAML)
│       │       ├── plan.md        ← REQUIRED: execution plan
│       │       └── ...            ← task artifacts
│       └── ...
├── STATE.json                     ← global execution state + checkpoints
├── DOCMAP.md                      ← document index (auto-generated)
└── .plan-manager/
```

**Config:** `~/.claude/plan-manager/config.json` → `{"root": "/path/to/root"}`

**Core rules:**
- One project = one folder under `<root>/project/`
- One task can be `in_progress` per project at a time
- Every task MUST have a `plan.md` before it can be executed
- Tasks within a project are sorted by priority then dependency order
- User controls N = how many projects run simultaneously

**Task lifecycle:**
```
pending → planned → ready → in_progress → completed
  ↓         ↓                  ↓
cancelled  blocked          blocked
```

---

## Phase 0: Configuration

### On every invocation

1. Check `~/.claude/plan-manager/config.json` → read `$ROOT`
2. If missing: **MUST configure first** (see below). Do not proceed.

### Configure ("configure plan manager", "setup plan manager")

Ask user for management root path → create structure:
```bash
mkdir -p "$ROOT/project"
echo '{"root":"'"$ROOT"'"}' > ~/.claude/plan-manager/config.json
```

---

## Module 1: PROJECT — 项目管理

Project = folder under `<root>/project/`. The fundamental unit of work organization.

### .project file format (YAML in markdown frontmatter style)

```yaml
name: string          # display name
slug: string          # folder name
status: active | idle | completed | archived
priority: P0 | P1 | P2 | P3
created: YYYY-MM-DD
description: string
notes: string
```

### List projects ("list projects", "project status", "project overview")

```bash
for d in "$ROOT/project/"*/; do
  name=$(basename "$d")
  status=$(grep '^status:' "$d/.project" 2>/dev/null | cut -d: -f2 | xargs || echo "active")
  active=$(grep -c 'status: in_progress' "$d/tasks/"*/.task 2>/dev/null || echo "0")
  total=$(ls -1 "$d/tasks/" 2>/dev/null | wc -l || echo "0")
  echo "| $name | $status | $active/$total |"
done
```

Display:
```
| Project | Status | Tasks (active/total) | Priority |
|---------|--------|---------------------|----------|
| PlanSkill | active | 0/3 | P0 |
| ExophMetry | idle | 0/2 | P1 |
| CDMSystem | completed | 0/5 | P2 |
```

### Create project ("create project <name>")

1. Get project name, slugify (lowercase, hyphens)
2. Create:
```bash
mkdir -p "$ROOT/project/<slug>/tasks"
cat > "$ROOT/project/<slug>/.project" << 'EOF'
name: <display-name>
slug: <slug>
status: active
priority: P2
created: YYYY-MM-DD
description: |
  <user-provided description>
notes: ""
EOF
```
3. Report: "Project `<name>` created at `$ROOT/project/<slug>/`"

### Show project ("show project <name>")

1. Read `.project` metadata
2. List tasks with status
3. Show active task, pending count, completed count

---

## Module 2: TASK — 任务管理

Task = subfolder under `<project>/tasks/`. Basic unit of execution.

### .task file format

```yaml
id: TASK-XXX          # auto: PROJ-SLUG-001, PROJ-SLUG-002 ...
slug: string          # folder name (task brief slug)
title: string         # short actionable title
project: string       # parent project slug
status: pending | planned | ready | in_progress | completed | cancelled | blocked
priority: P0 | P1 | P2 | P3
order: number         # execution order within project (lower = first)
created: YYYY-MM-DD
deadline: YYYY-MM-DD  # optional
completed: YYYY-MM-DD
depends_on: []        # list of task IDs (same project) this depends on
depends_on_cross: []  # list of task IDs (other projects) this depends on
description: string
notes: string
plan_file: string     # path to plan.md, set when plan created
```

### Task ordering (per project)

Tasks sorted by:
1. `depends_on` — blocked tasks go after their dependencies
2. `priority` — P0 before P1 before P2 before P3
3. `order` — explicit ordering number

The **top task** = first task in sorted list with status `ready` (or `planned` if user allows).

### List tasks ("list tasks", "task status")

Show per-project task tables:
```
## PlanSkill Tasks
| # | ID | Title | Status | Plan | Priority |
|---|----|-------|--------|------|----------|
| 1 | PS-001 | Build 6 modules | in_progress | ✓ | P0 |
| 2 | PS-002 | Write tests | pending | ✗ | P1 |
| 3 | PS-003 | Add docs | pending | ✗ | P2 |

→ Next to execute: PS-002 (when PS-001 completes)
→ Blocked: none
```

### Create task ("add task to <project>", "create task in <project>", "new task")

1. List projects if not specified, ask which one.
2. **One-task check:** Warn if project already has an `in_progress` task.
3. Ask: title, priority, description, deadline.
4. Auto-assign: ID = `<PROJ>-<NNN>`, slug from title, order = next available.
5. Create:
```bash
mkdir -p "$ROOT/project/<project>/tasks/<slug>"
cat > "$ROOT/project/<project>/tasks/<slug>/.task" << 'EOF'
id: <ID>
slug: <slug>
title: <title>
project: <project>
status: pending
priority: <P0-P3>
order: <N>
created: <today>
deadline: <date or "">
completed: ""
depends_on: []
depends_on_cross: []
description: |
  <description>
notes: ""
plan_file: ""
EOF
```
6. Report: "Task `<ID>`: `<title>` created in project `<project>`. Status: pending. Next: create a plan with 'make plan for <ID>'."

### Update task ("start <TASK-ID>", "complete <TASK-ID>", "cancel <TASK-ID>", "block <TASK-ID>")

- **start <ID>**: Check plan exists. Check no other task in same project is `in_progress`. Set `status: in_progress`.
- **complete <ID>**: Set `status: completed`, `completed: today`.
- **cancel <ID>**: Set `status: cancelled`.
- **block <ID>**: Set `status: blocked`, ask reason → append to notes.

---

## Module 3: PLAN — 计划管理

Every task MUST have a `plan.md` before execution. No plan = not executable.

### Plan lifecycle

```
draft → approved → executing → done
```

The `plan.md` file lives in the task directory: `<root>/project/<proj>/tasks/<task>/plan.md`

### plan.md template

```markdown
# Plan: <task-title>
Task: <TASK-ID>
Project: <project-name>
Status: draft | approved | executing | done
Created: YYYY-MM-DD
Updated: YYYY-MM-DD

## Goal
<One sentence: what does this task achieve?>

## Success Criteria
- [ ] <measurable outcome 1>
- [ ] <measurable outcome 2>

## Approach
<How will this be done? Architecture, tools, strategy.>

## Steps
1. [ ] <step 1> → verify: <how to verify>
2. [ ] <step 2> → verify: <how to verify>
3. [ ] <step 3> → verify: <how to verify>

## Risks
- <risk 1> — mitigation: <how to handle>

## Notes
<context, references, constraints>
```

### Create plan ("make plan for <ID>", "create plan for <ID>")

1. Find task by ID, check it exists.
2. Ask user: goal, approach, steps (or auto-draft based on description).
3. Create `plan.md` in task directory.
4. Update `.task`: `plan_file: plan.md`, `status: planned`.
5. If plan looks complete: `status: ready`.
6. Report: "Plan created for `<ID>`. Task is now `ready` for execution."

### Check plan ("check plan for <ID>", "review plan for <ID>")

1. Read `plan.md`.
2. Validate: goal present? success criteria measurable? steps actionable? risks considered?
3. Report gaps.

### Approve plan ("approve plan for <ID>")

Set plan status to `approved`, task status to `ready`. Only `ready` tasks enter execution queue.

---

## Module 4: EXECUTE — 执行模块

### Execution model

User says: "execute N projects" → system picks top `ready` task from each of N highest-priority projects, starts them. If a project has an `in_progress` task already, it's skipped (one-task rule).

### How "top task" is determined per project

1. Read all tasks in project
2. Filter: `status == ready` AND `plan_file != ""`
3. Sort by: dependency chain → priority → order
4. Top = first in sorted list

### Cross-project ordering (which N projects to run)

1. List all projects
2. Filter: projects that have at least one `ready` task
3. Sort by: project priority → has in_progress task? (no first) → project name
4. Pick top N

### Start execution ("execute N projects", "run tasks", "start execution")

1. If N not specified, ask: "How many projects to run in parallel?"
2. Compute execution plan:
```
## Execution Plan
| # | Project | Task ID | Task Title | Priority |
|---|---------|---------|------------|----------|
| 1 | PlanSkill | PS-001 | Build 6 modules | P0 |
| 2 | ExophMetry | EX-002 | Research papers | P1 |
```
3. Confirm with user.
4. For each task in the plan:
   - Set `status: in_progress`
   - Update `.task`
   - Update STATE.json

### Execution STATE.json

```json
{
  "updated": "2026-05-20T12:00:00Z",
  "active": {
    "PlanSkill": {
      "task_id": "PS-001",
      "started": "2026-05-20T12:00:00Z",
      "iterations": 3,
      "last_action": "Editing SKILL.md",
      "checkpoint": "PS-001-checkpoint-001.md"
    }
  },
  "history": [
    {"project": "PlanSkill", "task_id": "PS-001", "action": "started", "time": "..."},
    {"project": "PlanSkill", "task_id": "PS-001", "action": "checkpoint", "time": "..."}
  ]
}
```

**IMPORTANT: The skill itself doesn't execute the tasks — Claude Code does.** The EXECUTE module orchestrates WHICH tasks to work on. When invoked, it tells the user (and this AI) what to work on next. The AI then switches to working on those tasks.

### Continue execution ("continue", "resume", "what's next")

1. Read STATE.json → find active or ready tasks
2. If active tasks exist: "Currently working on: ..."
3. If no active but ready tasks: suggest execution
4. If nothing ready: suggest "create plan for pending tasks"

---

## Module 5: CHECK — 监督模块

### Auto-checkpoint

Before every major tool call during task execution, write a checkpoint:

```bash
CHECKPOINT_DIR="$ROOT/project/<proj>/tasks/<task>/checkpoints"
mkdir -p "$CHECKPOINT_DIR"
```

Checkpoint file: `<timestamp>-<action>.md`

```markdown
# Checkpoint: <task-title>
Time: 2026-05-20 12:05:00
Task: <TASK-ID>
Iteration: 4
Last action: Updated SKILL.md line 50-80
Current state: Module 2 Task section written, Module 3 Plan started
Next action: Write Module 4 Execute section

## Context snapshot
<what was just done, what's next, any blockers>
```

### Infinite loop detection ("check tasks", "task health")

Check running tasks for:
1. **Same action repeated >3x** without progress → 🔴 LOOP DETECTED
2. **No checkpoint in >10 iterations** → suggest checkpoint
3. **Task runtime > user expectation** → ask if should continue
4. **File churn**: same file edited >5x in one task → suggest plan review

### Health check output

```
## Task Health Report
| Task | Project | Iterations | Status | Alert |
|------|---------|------------|--------|-------|
| PS-001 | PlanSkill | 15 | running | ⚠️ High iterations, checkpoint? |
| EX-001 | ExophMetry | 3 | running | OK |
```

### Loop recovery

When loop detected:
1. Pause task (set `status: blocked`, reason: "loop detected")
2. Save detailed checkpoint
3. Report: "Task `<ID>` paused: possible loop. Review checkpoint at `<path>`. Resume with 'resume <ID>'."

### Resume after pause ("resume <ID>")

1. Read latest checkpoint
2. Restore context
3. Set `status: in_progress`
4. Continue from checkpoint's "next action"

---

## Module 6: ASSISTANT — AI互动助手

The ASSISTANT module is the user-facing interface. When user says "assistant", "what should I do", "what's next", or "project overview", the ASSISTANT does:

### Interactive workflow

```
1. SHOW overview
   → All projects with task counts and status
   → Currently executing tasks
   → Blocked items

2. ASK guiding questions
   → "Project X has pending tasks without plans. Create plans for them?"
   → "Projects A, B, C have ready tasks. Execute N=2?"
   → "Project Y has been idle for 2 weeks. Archive or reactivate?"
   → "Task Z depends on cross-project task W. How to handle?"

3. SUGGEST next actions
   → Priority-sorted list of what to do next
   → "1. Approve plan for PS-002"
   → "2. Execute 2 projects (PlanSkill + ExophMetry)"
   → "3. Check health of running tasks"

4. DRIVE iteration
   → Review → identify gaps → create tasks → make plans → execute → review
```

### Assistant triggers

| User says | Assistant responds with |
|-----------|------------------------|
| "assistant" / "what should I do" | Full overview + prioritized suggestions |
| "project overview" | Project summary table |
| "what's next" | Next action list |
| "review <project>" | Deep dive on one project |
| "iterate <project>" | Full iteration cycle for one project |

### Assistant output format

```
# Plan Manager Assistant

## 🏗️ Active (2)
- **PlanSkill/PS-001** — Build 6 modules (P0, 15 iterations)
- **ExophMetry/EX-002** — Research papers (P1, 3 iterations)

## 📋 Ready to Execute (3)
| Project | Task | Priority |
|---------|------|----------|
| CDMSystem | CD-001 — Add auth | P1 |
| ExophMetry | EX-003 — Write summary | P2 |
| PlanSkill | PS-002 — Write tests | P1 |

## ⚠️ Needs Attention
- **PlanSkill/PS-003** — No plan yet. Create one?
- **CDMSystem/CD-002** — Blocked on CD-001
- **ExophMetry** — 2 weeks idle

## 💡 Suggested Next Action
> Execute 2 projects: CDMSystem + PlanSkill. Say "execute 2 projects".
```

---

## File Reference

| File | Location | Module | Purpose |
|------|----------|--------|---------|
| Config | `~/.claude/plan-manager/config.json` | 0 | Root path |
| `.project` | `<root>/project/<proj>/.project` | 1 | Project metadata |
| `.task` | `<root>/project/<proj>/tasks/<task>/.task` | 2 | Task metadata |
| `plan.md` | `<root>/project/<proj>/tasks/<task>/plan.md` | 3 | Execution plan |
| `STATE.json` | `<root>/STATE.json` | 4,5 | Global execution state |
| `DOCMAP.md` | `<root>/DOCMAP.md` | — | Document index |
| Checkpoints | `<root>/project/<proj>/tasks/<task>/checkpoints/` | 5 | Auto-saved state |

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `${CLAUDE_SKILL_DIR}/bin/update-docmap.sh <root>` | Regenerate DOCMAP.md |
| `${CLAUDE_SKILL_DIR}/bin/init-project.sh <root> <name>` | Create project scaffold |
| `${CLAUDE_SKILL_DIR}/bin/init-task.sh <root> <project> <title>` | Create task scaffold |
