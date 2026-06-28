---
name: plan-manager
preamble-tier: 3
version: 4.3.0
description: |
  Dual-role autonomous project orchestration system.
  strategist — analyze projects, review plans, discuss goals and direction.
  executor — execute task loops, auto-continue, overnight runs.
  Configurable via `role` in config.json. Switch anytime.
  1. Project — project registry and lifecycle
  2. Task — priority/dependency ordering, one active per project
  3. Plan — AI drafts plans from goals, user reviews and approves
  4. Execute — Ralph-style autonomous loop, max-iteration safety, auto-continue
  5. Check — progress velocity, loop detection, crash recovery
  6. Assistant — dashboard, plan quality review, goal-setting guide
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
  - plan for
  - execute tasks
  - run tasks
  - start execution
  - overnight
  - run overnight
  - check tasks
  - task health
  - assistant
  - plan assistant
  - what should I do
  - what's next
  - project overview
  - continue
  - resume
  - auto
  - auto mode
  - strategist
  - executor
  - switch to strategist
  - switch to executor
  - analyze project
  - discuss direction
  - review project
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
interactive: true
benefits-from:
  - office-hours
  - autoplan
---

# /plan-manager - Dual-Role Autonomous Project Orchestration

## Dual-Role System

plan-manager has two roles. Switch anytime with "switch to strategist" or "switch to executor".

### strategist — 决策者

**Purpose:** Strategic analysis and planning. Study the project holistically.

**Role behaviors:**
- Read and analyze all project files freely (no file-isolation write restriction applies since no execution)
- Discuss and clarify project goals with user
- Analyze current directory structure — what exists, what's missing
- Assess current project state: what's done, what's blocked, what's next
- Research and propose future development direction
- Identify concrete improvement actions → draft them as new tasks
- Review all plan.md files for quality (measurable criteria, clear goals)
- Write/update `.project` goal and description fields
- Create new tasks and draft plans for user review

**Available operations:**
| Trigger | Behavior |
|---------|----------|
| "analyze <project>" / "review <project>" | Deep analysis: structure, state, gaps, direction |
| "discuss direction for <project>" | Interactive goal-setting and roadmap discussion |
| "review plans" | Scan all plans, flag quality issues |
| "create project" / "add task" / "make plan" | Full Module 1-2-3 access |
| "project overview" / "assistant" | Full dashboard |
| "execute" / "overnight" | **BLOCKED** — switch to executor first |

**Analysis output format:**
```
# Project Analysis: <project-name>

## Goal
<current goal. If missing, propose one.>

## Directory Structure
<what exists, what's missing, suggestions.>

## Current State
- Completed: N tasks
- In Progress: 0 (strategist mode — nothing executing)
- Pending: N tasks
- Blocked: N tasks

## Plan Quality Review
| Task | Plan | Goal Clear | Criteria Measurable | Issues |
|------|------|------------|---------------------|--------|
| T-001 | ✓ | ✓ | ✗ | Criteria vague: "works correctly" |

## Recent Session Activity
<Run `${CLAUDE_SKILL_DIR}/scripts/session-digest.py <project> --lang <zh|en>` and inline
its output here. If output is exactly `session: none`, omit this entire section.>

## Future Direction
<proposed next steps, improvements, new features>

## Suggested Actions
1. <concrete action 1>
2. <concrete action 2>
```

### executor — 执行者

**Purpose:** Execute tasks and iterate projects. The working mode.

**Role behaviors:**
- Execute plan steps (Module 4 Ralph-style loop)
- Auto-checkpoint and auto-continue
- Strict file isolation: writes ONLY within active task directory
- Handle minor problems internally, pause on MAJOR problems
- Support overnight unattended execution
- Track progress velocity

**Available operations:**
| Trigger | Behavior |
|---------|----------|
| "execute N projects" / "auto" | Start autonomous execution loop |
| "overnight" | Start overnight unattended execution |
| "continue" / "resume" | Resume from checkpoint |
| "check tasks" / "task health" | Health report |
| "list tasks" / "task status" | Quick task status |
| "complete TASK-ID" / "start TASK-ID" | Manual task state change |
| "create project" / "add task" | Allowed (safe: only non-running projects) |
| "make plan" / "review plans" | Read-only plan review (edits only to non-executing tasks) |
| "analyze <project>" | Read-only analysis (no structural changes) |

**In executor mode, the AI actively works.** It doesn't just report — it executes.

### Role switching

```
switch to strategist    → checkpoint active work, set role: strategist, save to config.
switch to executor      → check orphaned work, set role: executor, save to config.
```

**Switch to strategist protocol:**
1. Check `STATE.json` and `.task` files for active `in_progress` tasks.
2. If none: update `~/.claude/plan-manager/config.json` role to `strategist`.
3. If active tasks exist: warn "Pausing execution for strategy review".
4. For each active task: write `checkpoints/snapshot.md`, update `STATE.json` with `velocity: paused`, `last_action: role-switch-checkpoint`, and checkpoint path.
5. Keep `.task` status as `in_progress` so crash recovery can resume; do not mark completed/blocked unless execution truly failed.
6. Update config role to `strategist` and report all checkpointed tasks.

**Switch to executor protocol:**
1. Read `STATE.json`; detect orphaned `in_progress` tasks or task states with missing checkpoints.
2. If orphaned tasks exist: offer resume from checkpoint, pause for user review, or cancel stale execution state.
3. Do not start new work until orphan handling is resolved.
4. Update config role to `executor` and report ready queue.

### Role comparison

| Aspect | strategist | executor |
|--------|-----------|----------|
| Primary action | Analyze, discuss, plan | Execute, build, iterate |
| File writes | `.project`, new `plan.md`, new `.task` only | Within active `<task-dir>/` only |
| Task execution | Never | Yes — Ralph-style loop |
| User interaction | High — discussion, goal-setting | Low — only on MAJOR problems |
| Overnight mode | N/A | Yes |
| Best for | Project kickoff, review, replanning | Daily work, overnight runs |

---

## User Role & Autonomy Model

**User does:**
- Set project goals and priorities
- Review and approve AI-drafted plans
- Intervene on MAJOR problems (loops, deadlocks, unreachable goals)
- Edit non-running projects anytime; edit non-active tasks in running projects
- Switch between strategist/executor roles as needed
- Abort/restart overnight runs

**AI does (autonomously, no user prompts):**
- strategist role: deep project analysis, plan quality review, direction proposals
- executor role: execute tasks step by step, invoke other skills as needed
- Write/edit ONLY within the active task's own directory (executor)
- Read any file for context - read-only
- Auto-checkpoint before major actions
- Auto-continue: when one task completes, pick next ready task
- Handle minor problems internally (retry, course-correct)
- Track progress velocity; self-detect stalls and recover
- **CRITICAL BOUNDARY: AI never creates files, tasks, or plans without explicit user request.**
  "Identify actions" = propose them for user approval, not auto-create.
  "Auto-continue" applies ONLY in executor mode with already-approved plans.
  In strategist mode: propose changes, never execute without user confirmation.

## File Isolation (CRITICAL)

During execution (executor role only), each task has a **sandbox** — its own task directory:

```
project/CDMSystem/
├── .project                    # Never written during execution
├── README.md                   # Never written during execution
└── tasks/
    ├── build-auth/             # Task "build-auth" writes HERE only
    │   ├── .task
    │   ├── plan.md
    │   └── checkpoints/
    └── other-task/             # Task "build-auth" never writes here
```

| Operation | strategist | executor |
|-----------|-----------|----------|
| Read any file | Yes | Yes |
| Write/edit within own task dir | N/A | Yes |
| Write .project | Yes (goal, desc, notes) | Never |
| Write new plan.md / .task | Yes | Only for non-executing tasks |
| Write other project files | Never | Never unless an approved `write-exception` lists exact paths |
| Write STATE.json | No, except role-switch checkpoint metadata | Yes (Module 4) |

> **Guarded plan-step exception:** When a plan step explicitly requires creating or modifying files outside the task directory, the approved `plan.md` step MUST include `write-exception: <exact path or narrow path pattern>`. The executor may write only those listed paths for that step, must log the exception in `checkpoints/iterations.log`, and must verify the path after execution. If the exception touches `.project`, another task directory, configuration files, credentials, external services, or destructive operations, pause and ask the user before writing.

---

## Architecture

```
<root>/
├── project/<proj>/
│   ├── .project               # project metadata + goal
│   ├── README.md              # project description
│   └── tasks/<task-slug>/
│       ├── .task              # task state machine
│       ├── plan.md            # REQUIRED: user-reviewed plan
│       └── checkpoints/       # auto-saved crash-recovery snapshots
├── STATE.json                 # global execution state
├── DOCMAP.md                  # document index (auto-generated)
└── .plan-manager/
```

**Config:** `~/.claude/plan-manager/config.json`
```json
{
  "root": "/path/to/root",
  "parallelism": 2,
  "autonomy": "full",
  "max_iterations_per_task": 30,
  "overnight": false,
  "language": "zh",
  "role": "strategist",
  "github": {
    "enabled": false,
    "owner": "",
    "repo_match": "project-name",
    "check_remote": true
  }
}
```

| Config key | Default | Meaning |
|------------|---------|---------|
| `root` | (required) | Management root path |
| `role` | `strategist` | `strategist`=analyze, plan, discuss; `executor`=execute, build, iterate |
| `parallelism` | 2 | Default N for "execute N projects" |
| `autonomy` | `full` | `full`=never ask; `plan-review`=ask before plan changes; `supervised`=ask before each task |
| `max_iterations_per_task` | 30 | Hard cap per task. Task pauses when hit. |
| `overnight` | false | Enable overnight mode: extended caps, no user prompts ever |
| `language` | `zh` | Output language: `zh` (Chinese) or `en` (English) |
| `github.enabled` | false | Show read-only GitHub remote panel/columns |
| `github.owner` | "" | Default GitHub user/org whose repos map to projects by name |
| `github.repo_match` | `project-name` | Repo mapping strategy (currently project directory name) |
| `github.check_remote` | true | Use `gh repo view` to verify expected repo existence |

**Core rules:**
- One task `in_progress` per project at a time
- Every task MUST have an approved `plan.md` before execution
- AI auto-continues: complete -> pick next -> execute, without asking
- File isolation: running task writes ONLY within its own directory unless approved `write-exception` applies

**STATE.json schema:**
```json
{
  "version": "4.3.0",
  "updated": "ISO-8601 timestamp",
  "mode": "strategist | executor",
  "active_tasks": ["TASK-ID"],
  "task_states": {
    "TASK-ID": {
      "project": "project-name",
      "task_dir": "<root>/project/<project>/tasks/<task-slug>",
      "current_step": 1,
      "iterations": 0,
      "velocity": "progressing | slow | stalling | stalled | paused",
      "last_action": "human-readable summary",
      "checkpoint": "checkpoints/snapshot.md"
    }
  }
}
```
Executor owns writes to `STATE.json`. Strategist reads it, except during role-switch checkpointing where it may record paused/checkpointed metadata before changing role.

**Task lifecycle:**
```
pending -> planned -> ready -> in_progress -> completed
  |         |          |          |
cancelled  (no plan) blocked   blocked
```

---

## Panel-first principle (read before any operation)

plan-manager is panel-centric. Dashboards are **panels** generated by scripts. Prefer running a named fixed/saved panel via `panel-manage.py run <name>` over ad-hoc script calls when a stable panel exists. All metadata writes go through CRUD scripts (dry-run by default, `--apply` to commit). Deletes are soft (move to trash); permanent removal is `trash-manage.py purge`. Full panel system: see "Module 6 → Panel Management" and `references/panels-integration.md`.

**Unsure what to do? Run `panel-manage.py run help`** (`/plan-manager help`) for a role-aware quick-flow + command index.

Module map:
- Module 1 — Project (registry, lifecycle) — defined under "Phase 0 → Project operations"
- Module 2 — Task (priority/dependency ordering)
- Module 3 — Plan (AI drafts, user approves)
- Module 4 — Execute (Ralph loop, executor only)
- Module 5 — Check (velocity, crash recovery)
- Module 6 — Assistant (dashboards, panels, routing)

## Phase 0: Configuration

### On every invocation

1. Read `~/.claude/plan-manager/config.json` -> all config keys
2. CHECK current role. Behavior branches:
   - `strategist`: no execution. Focus on analysis, planning, review.
   - `executor`: ready to execute. Check for orphaned tasks (crash recovery).
3. If missing: configure.
4. If invoked as bare `/plan-manager` with no specific operation (single source of truth for routing is "Module 6 → Invocation routing"):
   - If current working directory is inside `<root>/project/<project>`, show that project panel via `panel-manage.py run` equivalent: `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> --lang <zh|en> <project>`.
   - Otherwise show global overview: `${CLAUDE_SKILL_DIR}/scripts/panel-manage.py run overview`.

### Configure ("configure plan manager", "setup plan manager")

Run:
```bash
${CLAUDE_SKILL_DIR}/scripts/configure-plan-manager.sh --root <root> --language <zh|en> --role <strategist|executor> [--github-enabled true|false] [--github-owner OWNER] [--github-check-remote true|false]
```

If any argument is missing, ask the user first. The script validates the root, creates required directories, and writes `~/.claude/plan-manager/config.json` atomically. Review config any time with `configure-plan-manager.sh --show` or `panel-manage.py run config`.

### Language behavior

| Setting | Dashboard | Plan templates | Messages | AskUserQuestion |
|---------|-----------|----------------|----------|-----------------|
| `zh` | Chinese headers | Chinese labels | Chinese | Chinese |
| `en` | English headers | English labels | English | English |

### Change settings

Update individual config keys. Examples: "switch to executor", "set language to en", "set parallelism to 3", "max iterations 50", "overnight on".

### Metadata writes are script-only

Project/Task metadata writes MUST use scripts. Do not directly Edit `.project` or `.task` except when repairing broken metadata that no script can parse.

- Project CRUD: `${CLAUDE_SKILL_DIR}/scripts/project-manage.py`
- Task CRUD: `${CLAUDE_SKILL_DIR}/scripts/task-manage.py`
- Write operations are dry-run by default; pass `--apply` only after the intended diff/action is clear.



### .project format
```yaml
name: string
slug: string
status: active | idle | completed | archived
priority: P0 | P1 | P2 | P3
created: YYYY-MM-DD
goal: string          # user's one-sentence north star
description: string
notes: string
```

### Priority assignment

Priority is explicit metadata, not inferred silently.

**Project priority:**
| Priority | Meaning |
|----------|---------|
| P0 | Current strategic focus, shared infrastructure, or blocker for other projects |
| P1 | Important active project to advance soon |
| P2 | Useful but not urgent |
| P3 | Experiment, validation, or low-risk backlog |

**Task priority:**
| Priority | Meaning |
|----------|---------|
| P0 | Blocker, safety issue, core loop work, critical validation, or required for current project goal |
| P1 | Mainline feature or important improvement |
| P2 | Cleanup, documentation, quality improvement, non-blocking refactor |
| P3 | Experiment, low-risk test, optional backlog |

**Defaults and authority:**
- `create project` defaults to P1 unless user states priority or strategist recommends and user accepts another value.
- `add task` defaults to P1 unless user states priority or task clearly matches P0/P2/P3 criteria.
- Strategist may recommend priority changes during review, but must not silently reprioritize existing projects/tasks without user approval.
- Executor uses priority only for ready-queue ordering; it should not change priority while executing.


---

## Module 1: PROJECT

### List projects ("list projects", "project overview")

Run `${CLAUDE_SKILL_DIR}/scripts/panel-manage.py run overview` (panel-first) and use its table as the baseline. Add strategic interpretation and suggested actions after the script output. For a lightweight metadata-only list use `panel-manage.py run projects`.

### Create project ("create project <name>")

Use project CRUD script only:

```bash
${CLAUDE_SKILL_DIR}/scripts/project-manage.py create --root <root> --name <name> [--goal TEXT] [--priority P1]
${CLAUDE_SKILL_DIR}/scripts/project-manage.py create --root <root> --name <name> [--goal TEXT] [--priority P1] --apply
```

Procedure:
1. Dry-run `project-manage.py create` and inspect output.
2. Study existing content if the directory already exists or if user asks to register existing work.
3. Preload session context with `${CLAUDE_SKILL_DIR}/scripts/session-digest.py <name> --lang <zh|en>` when relevant.
4. Ask user for the initial goal, then clarify/refine with `office-hours` and `autoplan` if this is a new/unclear project.
5. Re-run `project-manage.py create ... --apply` only after the goal and priority are clear.
6. Use `project-manage.py update ... --apply` for later goal/status/priority/description/notes changes.

Validation is owned by `project-manage.py`; do not directly write `.project`.

### Show project ("show project <name>")

Use `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> --lang <zh|en> <project>`.

### Analyze project ("analyze <project>", "review <project>") — strategist primary

**Only in strategist mode.** Deep project analysis:

1. Read `.project`, all `.task` files, all `plan.md` files
1.5. Run `${CLAUDE_SKILL_DIR}/scripts/session-digest.py <project> --lang <zh|en>` to capture recent cc session activity. If output is `session: none`, skip; otherwise hold it for the report.
2. Map directory structure — what files exist, what's missing
3. Assess: completed vs pending vs blocked tasks
4. Review plan quality: goals clear? criteria measurable?
5. Compare current state against project goal — gaps?
6. Propose future direction and concrete next actions (informed by session activity if available)
7. Output full analysis report (see Dual-Role System section for format) — include the `## Recent Session Activity` section iff step 1.5 returned non-empty digest

### Discuss direction ("discuss direction for <project>") — strategist only

Interactive goal-setting and roadmap session:
0. **Preload session context:** Run `${CLAUDE_SKILL_DIR}/scripts/session-digest.py <project> --lang <zh|en>`.
   If session exists, review the recent user messages BEFORE asking step 1.
   Open the discussion with a context-aware line: "我看到你最近在该项目讨论了 `<主题>` (`<相对时间>`)。继续这个方向,还是换个角度?" / "I see you recently discussed `<topic>` here (`<relative_time>`). Continue, or pivot?"
1. Show current goal. Ask: still accurate? needs update?
2. Analyze completed work. Ask: what's the most valuable next step?
3. Propose concrete new tasks. Draft plans for user review.
4. Update `.project` goal if changed.

---

## Module 2: TASK

### .task format
```yaml
id: PRJ-001
title: string
project: string
status: pending | planned | ready | in_progress | completed | cancelled | blocked
priority: P0-P3
order: number
created: YYYY-MM-DD
deadline: YYYY-MM-DD
completed: YYYY-MM-DD
depends_on: []
depends_on_cross: []
description: string
notes: string
plan_file: string
max_iterations: number
```

### Task ordering (per project)
1. Dependency chain -> 2. Priority -> 3. `order` field

### List tasks ("list tasks", "task status")
Per-project table with status, plan existence, priority.

### Create task ("add task to <project>", "new task")

Use task CRUD script only:

```bash
${CLAUDE_SKILL_DIR}/scripts/task-manage.py create --root <root> --project <project> --title <title> [--priority P1]
${CLAUDE_SKILL_DIR}/scripts/task-manage.py create --root <root> --project <project> --title <title> [--priority P1] --apply
```

Procedure:
1. List/read project if needed to choose target.
2. Ask for title, priority, description, max_iterations if not provided.
3. Dry-run `task-manage.py create` and inspect assigned ID/path.
4. Re-run with `--apply` after validation.
5. Use `task-manage.py update/start/complete/block/cancel/delete/deps` for all later task metadata changes.

> **Only create tasks on explicit user request** ("add task", "create task", "new task").
> Do NOT create tasks from analysis suggestions unless user explicitly confirms.

---

## Module 3: PLAN — AI Drafts, User Reviews

### plan.md template
```markdown
# Plan: <task-title>
Task: <TASK-ID> | Project: <project-name>
Plan Status: draft | review | approved | executing | done
Created: YYYY-MM-DD | Updated: YYYY-MM-DD

## Goal
<One sentence. Must align with project goal.>

## Success Criteria (COMPLETION PROMISE)
- [ ] <measurable outcome 1>
- [ ] <measurable outcome 2>

## Approach (AI DETERMINES)
<Architecture, tools, skills to invoke, strategy.>

## Steps (AI EXECUTES)
1. [ ] <step 1> -> verify: <check>
2. [ ] <step 2> -> verify: <check>

## Risks & Mitigations
- <risk> -> <mitigation>

## Iteration Budget
max_iterations: <number or "default">
```

### Create plan ("make plan for <ID>", "plan for <ID>")

1. Find task. Read project `.project` for the goal.
2. **AI auto-drafts the full plan** from task description + project goal.
3. Write `plan.md`. Update `.task`.
4. **Show user the goal + success criteria.** Get approval.
5. Report created.

### Review plan quality ("review plan for <ID>", "review plans")

AI validates all plans. In strategist mode: full deep review. In executor mode: quick check.

---

## Module 4: EXECUTE — Ralph-Style Autonomous Loop

**executor role only.** In strategist mode, this module is disabled.

### Start execution ("execute N projects", "run tasks", "auto", "overnight")

If in strategist mode: "Cannot execute in strategist mode. Switch to executor first: 'switch to executor'."

Otherwise: compute execution plan, set tasks `in_progress`, update STATE.json, begin executing.

**Ready task definition:**
A task is ready only when all conditions hold:
- `.task` status is `ready`
- `plan.md` exists and `Plan Status` is `approved`
- all `depends_on` and `depends_on_cross` tasks are completed
- the project has no other `in_progress` task

**Task selection order:** run `${CLAUDE_SKILL_DIR}/scripts/ready-queue.py --root <root>` to compute deterministic ready queue. It sorts by priority (`P0` → `P3`) → dependency/order field → created date → project name.

**auto-continue behavior:**
- `execute <N> projects` with N=1 (or "execute", "start"): Complete current task, then STOP. Do not auto-start the next ready task.
- `execute <N> projects` with N>1: run up to N selected ready tasks, then STOP after those tasks complete or pause.
- `auto`: after a task completes, pick the next ready task automatically until no ready tasks remain or a MAJOR problem occurs.
- `overnight`: same as `auto`, with doubled max_iterations and no user prompts; if a prompt would be required, checkpoint and skip/stop according to safety rules.
- If a task fails or becomes blocked, report it explicitly. Do not silently mark it complete or hide it by continuing.

### Execution loop

1. Read plan.md → find next unchecked step
2. Execute step (invoke other skills as needed). All Write/Edit ops target ONLY `<own-task-dir>/` unless the approved plan step contains a matching `write-exception`
3. Check step verification → mark [x] or retry (max 3)
4. Write iteration log to `<task-dir>/checkpoints/iterations.log`
5. Update STATE.json: increment `iterations`, set `current_step`, set `last_action`, set `velocity`
6. Auto-validate: run tests/lint if applicable (PASS→continue, FAIL→fix+retry max 3)
7. Check progress velocity (Module 5): progressing→continue, stalled→pause
8. All steps done + all success criteria met → run `${CLAUDE_SKILL_DIR}/scripts/task-manage.py complete --root <root> <TASK-ID> --apply`, update STATE.json, auto-pick next ready task (see auto-continue rules)
9. Iteration count >= max_iterations → pause task, save checkpoint, update `.task` to `blocked`

### Crash recovery, auto-continue, overnight mode, STATE.json

Core: orphaned `in_progress` tasks auto-detected, resume from last checkpoint.

---

## Module 5: CHECK — Progress Velocity & Crash Recovery

### Progress velocity

| Velocity | Criteria | Action |
|----------|----------|--------|
| progressing | Steps advancing, files changing | Continue |
| slow | Same step 3+ iterations, small changes | Checkpoint, continue |
| stalling | Same action 2x same file, no improvement | Self-correct |
| stalled | Same action 3x same file, zero progress | PAUSE |

### MAJOR problems → PAUSE + checkpoint

| Problem | Action |
|---------|--------|
| Stalled (3x no progress) | Pause, save checkpoint, report |
| Unreachable criteria (3 approaches fail) | Pause, suggest plan revision |
| Max iterations reached | Pause, flag for user review |

### Checkpoint format

When saving a checkpoint, write `checkpoints/snapshot.md`:
```markdown
# Checkpoint — <timestamp>
Task: <TASK-ID> | Iteration: <N>/<max>
Last completed step: <N>
Plan step status:
- [x] step 1
- [ ] step 2
...
Last action: <what was done>
Last result: <OK/FAIL>
```
This is the minimum format. crash recovery reads `snapshot.md` to resume from the first unchecked step.

### MINOR problems → AI handles internally

- Step failed (1st try): retry max 3
- Test/lint failure: fix + re-run, 3x same → escalate
- Slow but progressing: checkpoint, continue

### Crash recovery

On startup: check STATE.json for orphaned `in_progress` tasks → offer resume.
1. If `checkpoints/snapshot.md` exists → restore from checkpoint (resume from first unchecked step).
2. If no checkpoint exists → fallback: read `plan.md`, find first unchecked step, restart from there.
3. If no plan.md either → mark task `blocked`, reason: "session-ended-no-plan".

### Overnight report

After overnight mode ends: summary to `<root>/OVERNIGHT-REPORT.md` (completed, paused, costs).

---

## Module 6: ASSISTANT — Dashboard & Goal-Setting Guide

### Modes

| Trigger | strategist behavior | executor behavior |
|---------|--------------------|--------------------|
| "assistant" / "project overview" | Full dashboard + analysis hints | Execution status dashboard |
| "what's next" / "what should I do" | Suggested analyses and plans to review | Prioritized task execution list |
| "review <project>" | Deep analysis (Module 1 analyze) | Read-only quick review |
| "review plans" | Full plan quality audit | Quick plan check |
| "overnight report" | N/A | Show latest overnight summary |
| "iterate <project>" | Propose direction + draft new tasks | Execute next ready task |

### Invocation routing

| Invocation | Behavior |
|---|---|
| `/plan-manager` | Show important config header + project overview using configured root. If current working directory maps to a managed project, prefer that project's panel. |
| `/plan-manager <PROJECT-NAME|PROJECT-TITLE|PROJECT-SLUG>` | Show important config header + project-specific panel |
| `/plan-manager <TASK-ID>` | Show important config header + task-specific panel |
| `/plan-manager <task-title-or-slug>` | Same task panel, matched by task title or task directory slug |
| `/plan-manager --task <TASK-ID>` | Same task panel, explicit form |

Implementation mapping:
- Bare `/plan-manager` from inside `<root>/project/<project>`: `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> --lang <zh|en> <project>`
- Bare `/plan-manager` outside a managed project: `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> --lang <zh|en>`
- Project panel: `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> --lang <zh|en> <project>`
- Task panel: `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> --lang <zh|en> <query>` or `--task <query>`

### Panel Management

plan-manager is panel-centric. Prefer running named panels instead of ad-hoc script calls when a stable panel exists.

Panel types:
- fixed panels: built into `${CLAUDE_SKILL_DIR}/scripts/panel-manage.py` (`help`, `config`, `overview`, `projects`, `tasks`, `ready-queue`, `remote`, `github-status`, `trash`, `panels`).
- saved panels: user-defined, persisted in `~/.claude/plan-manager/panels.json`.
- temporary panels: one-off generated panels via `panel-manage.py generate`.

Routing:
| Invocation | Behavior |
|------------|----------|
| `/plan-manager help` | Run fixed `help` panel (role-aware quick flow + command index) |
| `/plan-manager config` | Run fixed `config` panel |
| `/plan-manager overview` | Run fixed `overview` panel |
| `/plan-manager projects` | Run fixed `projects` panel (metadata-only list) |
| `/plan-manager tasks` | Run fixed `tasks` panel (all tasks) |
| `/plan-manager ready-queue` | Run fixed `ready-queue` panel |
| `/plan-manager remote` | Run fixed `remote` panel |
| `/plan-manager github-status` | Run fixed `github-status` panel |
| `/plan-manager trash` | Run fixed `trash` panel |
| `/plan-manager panels` | Show the panel-management panel (`panel-manage.py list`) |
| `/plan-manager panel <name>` | Run any fixed or saved panel (`panel-manage.py run <name>`) |

Common commands:
```bash
${CLAUDE_SKILL_DIR}/scripts/config-panel.py --lang <zh|en>
${CLAUDE_SKILL_DIR}/scripts/configure-plan-manager.sh --show
${CLAUDE_SKILL_DIR}/scripts/panel-manage.py list
${CLAUDE_SKILL_DIR}/scripts/panel-manage.py run overview
${CLAUDE_SKILL_DIR}/scripts/panel-manage.py add weekly --script project-overview.py --title "Weekly Overview" --description "每周总览" --args '["--root","$ROOT","--lang","$LANG"]' --apply
${CLAUDE_SKILL_DIR}/scripts/panel-manage.py remove weekly --apply
```


### Remote panel (GitHub)

If `github.enabled=true` and `github.owner` is set in config, `/plan-manager` MUST show read-only remote status:
- global overview adds a `Remote Status` column.
- project panel adds `Expected Repo`, `Origin`, `Remote Status`, `GitHub URL`, `Remote Message`.
- remote checks are read-only: no `git fetch`, no `git push`, no `git remote set-url`, no repo creation.
- fixes such as creating a repo or changing origin require explicit user request.

Status meanings:
| Status | Meaning |
|--------|---------|
| `ok` | origin points to expected `<owner>/<project>` and repo exists |
| `missing_origin` | local git repo has no origin |
| `not_git` | project directory is not a git repo |
| `repo_missing` | expected GitHub repo is missing or inaccessible |
| `origin_mismatch` | origin points to a different repo |
| `github_unknown` | GitHub check failed, timed out, or gh is not authenticated |

**GitHub management is script-driven.** Do NOT run ad-hoc `git remote`/`gh repo` commands for remote management; use `scripts/github-manage.sh`. Write subcommands are dry-run by default and only mutate with `--apply`:
| Command | Effect |
|---------|--------|
| `github-manage.sh status [--project NAME]` | Read-only remote status (delegates to github-verify.py) |
| `github-manage.sh list` | List GitHub repos for the owner |
| `github-manage.sh set-origin <project> [--apply]` | Set origin to `<owner>/<project>` |
| `github-manage.sh add-origin <project> [--apply]` | Add origin `<owner>/<project>` |
| `github-manage.sh create-repo <project> [--public] [--apply]` | Create GitHub repo `<owner>/<project>` |
| `github-manage.sh push <project> [--branch B] [--apply]` | Push current/named branch to origin |

Always show the dry-run output first and get user confirmation before re-running with `--apply`.


```
# Plan Manager — strategist

## 重要配置
| Root | Role | Language | Parallelism | Autonomy | Max Iterations | Overnight |
|------|------|----------|:-----------:|----------|:--------------:|:---------:|
| /home/wangyu/ClaudeCodeCLI | strategist | zh | 2 | full | 30 | false |

## 项目分析
| 项目 | 目标 | 计划质量 | 待分析 | 最近会话 | 建议 |
|------|------|:------:|:----:|---------|------|
| Xzs_app-dev | 小红书运营软件 | ✓ | 否 | 2天前, 17条 | 创建P0任务 |
| VIP | 未设定 | — | 是 | 无会话 | 注册项目 |
| ExophMetry | 未设定 | — | 是 | 5天前, 3条 | 讨论目标 |

## 待审查计划 (1)
- VIP: 无 .project 文件，需注册

## 建议行动
1. analyze VIP → 了解未注册项目内容
2. create project VIP → 注册项目并设定目标
3. add task to Xzs_app-dev → 创建 V1.2.0 P0 开发任务
```

**Populating the "最近会话" / "Last Session" column:**
Prefer `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> --lang <zh|en>` for the whole dashboard. For one project, run `${CLAUDE_SKILL_DIR}/scripts/session-digest.py <project> --lang <zh|en>`.
- If first line is `session: none`: show "无会话" / "no session"
- Otherwise extract `relative_time` and `user_msg_count`, format as `<relative_time>, <count>条` / `<relative_time>, <count> msgs`

### executor-mode dashboard

```
# Plan Manager — executor

## 执行中 (1/2)
| 项目 | 任务 | 步骤 | 迭代 | 速度 |
|------|------|------|------|------|
| PlanSkill | PS-001 | 3/5 | 4 | progressing |

## 就绪队列
| # | 项目 | 任务 | 优先级 |
|---|------|------|:------:|
| 1 | ExophMetry | EX-001 | P1 |

## 需要关注
- PlanSkill/PS-003 — 计划待审查
```

---

## File Reference

| File | Purpose |
|------|---------|
| `~/.claude/plan-manager/config.json` | Root path, role, parallelism, autonomy, max_iterations, overnight, language |
| `<root>/project/<proj>/.project` | Project metadata + goal |
| `<root>/project/<proj>/tasks/<task>/.task` | Task state machine |
| `<root>/project/<proj>/tasks/<task>/plan.md` | AI-drafted, user-reviewed plan |
| `<root>/project/<proj>/tasks/<task>/checkpoints/` | Auto-saved state + iterations.log |
| `<root>/STATE.json` | Global execution state |
| `<root>/.plan-manager/trash/projects/<name>-<timestamp>` | Trashed projects (restorable until purged) |
| `<root>/project/<proj>/tasks/.trash/<slug>-<timestamp>` | Trashed tasks (restorable until purged) |
| `<root>/OVERNIGHT-REPORT.md` | Post-overnight summary |
| `<root>/DOCMAP.md` | Document index |

## Scripts

| Script | Purpose |
|--------|---------|
| `${CLAUDE_SKILL_DIR}/scripts/help-panel.py [--lang zh\|en]` | Role-aware help panel: quick flows + command index + scenario nav |
| `${CLAUDE_SKILL_DIR}/scripts/config-panel.py [--lang zh\|en]` | Show full plan-manager configuration panel |
| `${CLAUDE_SKILL_DIR}/scripts/configure-plan-manager.sh [--root PATH] [--language zh\|en] [--role strategist\|executor] [--show]` | Configure plan-manager and write config.json; `--show` displays config panel |
| `${CLAUDE_SKILL_DIR}/scripts/project-manage.py <list\|read\|create\|update\|archive\|delete> --root <root> ... [--apply]` | Project CRUD; write ops dry-run unless `--apply` |
| `${CLAUDE_SKILL_DIR}/scripts/task-manage.py <list\|read\|create\|update\|start\|complete\|block\|cancel\|delete\|deps> --root <root> ... [--apply]` | Task CRUD/status/deps; write ops dry-run unless `--apply` |
| `${CLAUDE_SKILL_DIR}/scripts/trash-manage.py <list\|show\|restore\|purge\|empty> --root <root> ... [--apply] [--force]` | Trash management; restore is dry-run unless `--apply`; purge/empty require `--force` |
| `${CLAUDE_SKILL_DIR}/scripts/update-docmap.sh <root>` | Regenerate DOCMAP.md |
| `${CLAUDE_SKILL_DIR}/scripts/project-overview.py --root <root> [--lang zh\|en] [PROJECT\|TASK] [--task TASK]` | Generate config header plus project overview, project panel, or task-specific panel |
| `${CLAUDE_SKILL_DIR}/scripts/ready-queue.py --root <root> [--limit N]` | List ready tasks in execution order |
| `${CLAUDE_SKILL_DIR}/scripts/session-digest.py <project> [--max-user-msgs N] [--lang zh\|en]` | Extract cc session digest. Outputs `session: none` if no session exists. |
| `${CLAUDE_SKILL_DIR}/scripts/github-verify.py --root <root> --owner <owner> [--project NAME] [--json]` | Read-only GitHub remote verification for projects |
| `${CLAUDE_SKILL_DIR}/scripts/github-manage.sh <status\|list\|set-origin\|add-origin\|create-repo\|push> [--owner O] [--project NAME] [--apply]` | Script-driven GitHub management; write ops dry-run unless `--apply` |
| `${CLAUDE_SKILL_DIR}/scripts/panel-manage.py <list\|show\|run\|add\|remove\|generate> ... [--apply]` | Panel registry and panel-management panel; saved panel writes dry-run unless `--apply` |
| `${CLAUDE_SKILL_DIR}/scripts/verify-panels.sh` | Verify fixed panel registry and panel runner |
| `${CLAUDE_SKILL_DIR}/scripts/verify-installation.sh [--target PATH]` | Verify standard skill structure and installation health |

## References

- `references/manual.md` — full usage manual (panels, CRUD, GitHub, trash, config)
- `references/panels-integration.md` — panel registry and panel system
- `references/architecture.md` — role, directory, and trash-lifecycle architecture
- `references/state-and-checkpoints.md` — STATE.json and checkpoint format
- `references/installation.md` — Claude/Codex/Copilot install targets
