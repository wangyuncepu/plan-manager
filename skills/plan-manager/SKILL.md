---
name: plan-manager
version: 4.2.0
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
switch to strategist    → role: strategist. Save to config.
switch to executor      → role: executor. Save to config.
```

If active executor tasks exist when switching to strategist: warn, checkpoint all tasks, pause them.

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
| Write other project files | Yes (analysis only) | Never |
| Write STATE.json | No | Yes (Module 4) |

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
  "role": "strategist"
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

**Core rules:**
- One task `in_progress` per project at a time
- Every task MUST have an approved `plan.md` before execution
- AI auto-continues: complete -> pick next -> execute, without asking
- File isolation: running task writes ONLY within its own directory

**Task lifecycle:**
```
pending -> planned -> ready -> in_progress -> completed
  |         |          |          |
cancelled  (no plan) blocked   blocked
```

---

## Phase 0: Configuration

### On every invocation

1. Read `~/.claude/plan-manager/config.json` -> all config keys
2. CHECK current role. Behavior branches:
   - `strategist`: no execution. Focus on analysis, planning, review.
   - `executor`: ready to execute. Check for orphaned tasks (crash recovery).
3. If missing: configure.

### Configure ("configure plan manager", "setup plan manager")

1. Ask user for root path.
2. Ask user for language: `zh` (Chinese) or `en` (English). Default `zh`.
3. Ask user for default role: `strategist` or `executor`. Default `strategist`.
4. Create structure. Write config with defaults:
```bash
cat > ~/.claude/plan-manager/config.json << EOF
{"root":"$ROOT","role":"$ROLE","parallelism":2,"autonomy":"full","max_iterations_per_task":30,"overnight":false,"language":"$LANG"}
EOF
```

### Language behavior

| Setting | Dashboard | Plan templates | Messages | AskUserQuestion |
|---------|-----------|----------------|----------|-----------------|
| `zh` | Chinese headers | Chinese labels | Chinese | Chinese |
| `en` | English headers | English labels | English | English |

### Change settings

Update individual config keys. Examples: "switch to executor", "set language to en", "set parallelism to 3", "max iterations 50", "overnight on".

---

## Module 1: PROJECT

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

### List projects ("list projects", "project overview")

Table with project name, status, goal, tasks (active/total), priority.

### Create project ("create project <name>")

1. Slugify name. 2. Ask user for the goal. 3. Write `.project`.
4. Report created.

### Show project ("show project <name>")

Read `.project`, list tasks with status, show active task details.

### Analyze project ("analyze <project>", "review <project>") — strategist primary

**Only in strategist mode.** Deep project analysis:

1. Read `.project`, all `.task` files, all `plan.md` files
2. Map directory structure — what files exist, what's missing
3. Assess: completed vs pending vs blocked tasks
4. Review plan quality: goals clear? criteria measurable?
5. Compare current state against project goal — gaps?
6. Propose future direction and concrete next actions
7. Output full analysis report (see Dual-Role System section for format)

### Discuss direction ("discuss direction for <project>") — strategist only

Interactive goal-setting and roadmap session:
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
1. List projects if not specified. 2. Ask: title, priority, description, max_iterations (optional).
3. Auto-assign ID, slug, order. 4. Create `.task`. 5. Report created.

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

Otherwise: same as v4.1 — compute execution plan, set tasks `in_progress`, begin executing.

### Execution loop, iteration log, completion promise, crash recovery, auto-continue, max-iteration safety, overnight mode, STATE.json

All unchanged from v4.1. See previous version for full details.

---

## Module 5: CHECK — Progress Velocity & Crash Recovery

### Progress velocity tracking, MAJOR/MINOR problems, crash recovery, overnight report

All unchanged from v4.1. See previous version for full details.

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

### strategist-mode dashboard

```
# Plan Manager — strategist

## 项目分析
| 项目 | 目标 | 计划质量 | 待分析 | 建议 |
|------|------|:------:|:----:|------|
| PlanSkill | Build skill | ⚠️ | 是 | 检查plan.md |
| ExophMetry | 未设定 | — | 是 | 需讨论目标 |

## 待审查计划 (3)
- CDMSystem: 无计划
- PlanSkill: plan.md 目标模糊
- ExophMetry: 无项目目标

## 建议行动
1. analyze PlanSkill → 审查代码和计划
2. discuss direction for ExophMetry → 明确研究方向
```

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
| `<root>/OVERNIGHT-REPORT.md` | Post-overnight summary |
| `<root>/DOCMAP.md` | Document index |

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `${CLAUDE_SKILL_DIR}/bin/update-docmap.sh <root>` | Regenerate DOCMAP.md |
| `${CLAUDE_SKILL_DIR}/bin/init-project.sh <root> <name>` | Create project scaffold |
| `${CLAUDE_SKILL_DIR}/bin/init-task.sh <root> <project> <title>` | Create task scaffold |
