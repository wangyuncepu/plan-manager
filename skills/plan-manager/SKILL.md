---
name: plan-manager
version: 4.1.0
description: |
  Autonomous multi-project orchestration system. User sets goals and reviews
  plans; AI handles drafting, execution, and routine decisions. Intervenes
  only on major problems. Long-running overnight execution with max-iteration
  caps, completion promises, progress velocity, and crash recovery.
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
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /plan-manager - Autonomous Multi-Project Orchestration

## User Role & Autonomy Model

**User does:**
- Set project goals and priorities
- Review and approve AI-drafted plans
- Intervene on MAJOR problems (loops, deadlocks, unreachable goals)
- Edit non-running projects anytime; edit non-active tasks in running projects
- Abort/restart overnight runs

**AI does (autonomously, no user prompts):**
- Draft plans from task descriptions
- Execute tasks step by step, invoke other skills as needed
- Write/edit ONLY within the active task's own directory
- Read any file for context - read-only
- Auto-checkpoint before major actions
- Auto-continue: when one task completes, pick next ready task
- Handle minor problems internally (retry, course-correct)
- Track progress velocity; self-detect stalls and recover

## File Isolation (CRITICAL)

During execution, each task has a **sandbox** - its own task directory:

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

| Operation | Allowed during task execution? |
|-----------|-------------------------------|
| Read any file in any project | Yes - needed for context |
| Write/edit within own task directory | Yes - this is the work |
| Write/edit .project (own project) | Never - user owns project metadata |
| Write/edit other task's .task or plan.md | Never - each task is isolated |
| Write/edit other project (any file) | Never - cross-project isolation |
| Write `<root>/STATE.json` | Module 4 only, to update execution state |
| Write `<root>/DOCMAP.md` | Only when explicitly running "update doc index" |

User can freely create new tasks, edit plans of pending tasks, reorder priorities - even while other projects are executing.

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
  "overnight": false
}
```

| Config key | Default | Meaning |
|------------|---------|---------|
| `root` | (required) | Management root path |
| `parallelism` | 2 | Default N for "execute N projects" |
| `autonomy` | `full` | `full`=never ask; `plan-review`=ask before plan changes; `supervised`=ask before each task |
| `max_iterations_per_task` | 30 | Hard cap per task. Task pauses when hit. |
| `overnight` | false | Enable overnight mode: extended caps, no user prompts ever |

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

1. Read `~/.claude/plan-manager/config.json` -> `$ROOT`, `$PARALLELISM`, `$AUTONOMY`, `$MAX_ITER`, `$OVERNIGHT`
2. If missing: configure.

### Configure ("configure plan manager", "setup plan manager")

Ask user for root path. Create structure. Write config with defaults.

### Change settings

Update individual config keys. Examples: "set parallelism to 3", "max iterations 50", "overnight on".

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
4. Report: "Project `<name>` created with goal: `<goal>`"

### Show project ("show project <name>")

Read `.project`, list tasks with status, show active task details.

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
max_iterations: number      # per-task override of config default, or 0 = use default
```

### Task ordering (per project)
1. Dependency chain -> 2. Priority -> 3. `order` field

### List tasks ("list tasks", "task status")
Per-project table with status, plan existence, priority.

### Create task ("add task to <project>", "new task")
1. List projects if not specified. 2. Ask: title, priority, description, max_iterations (optional).
3. Auto-assign ID, slug, order. 4. Create `.task`. 5. Report created + suggest drafting plan.

---

## Module 3: PLAN - AI Drafts, User Reviews

**Principle:** AI writes the plan from task description + project goal. User reviews goal and success criteria.

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
3. Write `plan.md` with `Plan Status: draft`. Update `.task`.
4. **Show user the goal + success criteria.** "Does this look right?"
   - Yes -> `approved` + task `ready`
   - No -> user corrects -> approved + ready
5. Report: "Plan for `<ID>` approved. Task is `ready`."

### Review plan quality ("review plan for <ID>")

AI validates: goal clear + aligned? criteria measurable? steps verifiable? risks covered? iterations reasonable?

---

## Module 4: EXECUTE - Ralph-Style Autonomous Loop

**Principle:** Once started, AI runs autonomously. Each iteration builds on the last. Max-iteration cap prevents runaway. Completion promise gates exit.

**Inspired by:** Ralph Wiggum Loop pattern - the prompt never changes, but the codebase evolves each iteration.

### Start execution ("execute N projects", "run tasks", "auto", "overnight")

1. N = specified or config.parallelism default.
2. If "overnight": set config.overnight=true, double max_iterations, no user prompts EVER (even MAJOR problems auto-pause without asking in overnight mode).
3. Compute execution plan, display it, set tasks `in_progress`, update STATE.json.
4. **Begin executing immediately.**

### Execution loop (Ralph-style)

```
FOR each active task, in a continuous loop:

  ITERATION:
    1. Read plan.md -> find next unchecked step
    2. Execute step (invoke other skills as needed)
       CONSTRAINT: All Write/Edit ops target ONLY <own-task-dir>/
    3. Check step verification -> mark [x] or retry (max 3)
    4. Write iteration log:
       echo "[$(date -Iseconds)] iter:$N step:S/N action:$ACTION result:$RESULT" \
         >> <task-dir>/checkpoints/iterations.log
    5. Auto-validate: run tests/lint/type-check if applicable
       - PASS: continue
       - FAIL: fix + retry (max 3, then escalate)
    6. Check progress velocity (Module 5):
       - PROGRESS: steps advancing, files changing -> continue
       - STALL: same action 3x no change -> self-correct or pause
    7. IF all steps done AND all success criteria met:
       -> ITERATION LOG: "COMPLETED $(date -Iseconds)"
       -> mark task completed, update STATE.json
       -> auto-pick next ready task from same or next project
    8. IF iteration count >= max_iterations:
       -> PAUSE task. Log: "MAX_ITER reached. Checkpoint saved."
       -> Report to user (non-blocking in overnight mode)
```

### Iteration log format

```
[2026-05-21T03:15:00+08:00] iter:1 step:1/5 action:read-plan.md result:OK
[2026-05-21T03:15:30+08:00] iter:2 step:1/5 action:edit-SKILL.md result:OK
[2026-05-21T03:16:00+08:00] iter:3 step:1/5 action:run-tests result:FAIL
[2026-05-21T03:16:30+08:00] iter:4 step:1/5 action:fix-tests result:OK
[2026-05-21T03:17:00+08:00] iter:5 step:2/5 action:edit-helpers.sh result:OK
...
[2026-05-21T05:30:00+08:00] iter:28 step:5/5 action:final-verify result:OK
[2026-05-21T05:30:10+08:00] COMPLETED
```

### Completion promise

Task's **success criteria** in `plan.md` serve as the completion promise. When ALL criteria are checked `[x]` AND all plan steps are checked `[x]`, the task is complete. AI writes "COMPLETED" to the iteration log.

### Skill selection during execution

plan-manager is the **orchestrator**, not the doer. When executing a step, it tells Claude Code what to do. Claude Code then selects the best available skill based on the step's nature:

**Selection logic (Claude Code handles this automatically):**

| Step type | Example | Likely skill invoked |
|-----------|---------|---------------------|
| Write code / implement | "Build auth middleware" | `superpowers:test-driven-development` |
| Debug / fix | "Fix login bug" | `superpowers:systematic-debugging` |
| Review code | "Review PR changes" | `review` or `superpowers:requesting-code-review` |
| Write tests | "Add unit tests for API" | `superpowers:test-driven-development` |
| Plan / design | "Design database schema" | `superpowers:writing-plans` or `superpowers:brainstorming` |
| Write docs | "Document the API" | `document-generate` |
| Research | "Find best library for X" | `everything-claude-code:deep-research` |
| Ship / deploy | "Create PR and push" | `ship` or `land-and-deploy` |
| QA / test site | "Test the login flow" | `qa` or `qa-only` |
| Security audit | "Check for vulnerabilities" | `cso` or `security-review` |
| Git operations | "Commit and push" | `superpowers:finishing-a-development-branch` |
| Run app / verify | "Start dev server" | `run` or `verify` |

**Key principle:** plan-manager never explicitly names which skill to use in `plan.md` steps. It describes **what** needs to be done. Claude Code's skill routing system matches the intent to the best available skill.

**What plan-manager does control:**
- `plan.md` step descriptions should be clear about intent (e.g. "Write tests for X" not "Use TDD skill on X")
- File isolation: all skill output goes to `<task-dir>/`, plan-manager enforces this
- Step verification: after a skill completes, plan-manager checks the verification criteria

### Crash recovery (auto-resume)

On startup, check STATE.json for tasks with `status: in_progress`:
1. Read `<task-dir>/checkpoints/iterations.log` -> find last iteration
2. Read latest full checkpoint
3. Restore context from checkpoint
4. Continue from last incomplete step
5. Log: "RECOVERED $(date -Iseconds) from crash"

If session ended unexpectedly (power loss, network drop, process kill), the next invocation of any plan-manager trigger auto-detects the orphaned `in_progress` tasks and offers to resume.

### Auto-continue

When a task completes:
1. Check same project for next `ready` task -> auto-start it
2. If none: check other projects -> auto-start up to N
3. Update STATE.json. Report: "TASK-001 completed. Auto-starting TASK-002."
4. **No user prompt.** Continue.

### Max-iteration safety

| Scenario | Action |
|----------|--------|
| Iteration < 70% of max | Normal execution |
| Iteration 70-90% of max | Log warning. Increase checkpoint frequency. |
| Iteration >= max_iterations | Pause task. Save checkpoint. Flag for user review ("Task TASK-001 hit max iterations. Review progress and decide: continue, revise plan, or cancel.") |
| Overnight mode + max reached | Auto-pause. Leave clear checkpoint. Do NOT wake user. |

### Overnight mode ("overnight", "run overnight")

```
/plan-manager overnight
```

1. Sets `overnight: true` in STATE.json
2. Doubles config.max_iterations_per_task
3. All MAJOR problems auto-pause without user prompt (save checkpoint, move to next task)
4. On completion or stall-out: write a summary report to `<root>/OVERNIGHT-REPORT.md`
5. Morning: user runs "assistant" -> sees overnight report

### STATE.json (v4.1)

```json
{
  "updated": "2026-05-21T03:17:00+08:00",
  "mode": "executing",
  "overnight": false,
  "parallelism": 2,
  "active": {
    "PlanSkill": {
      "task_id": "PS-001",
      "started": "2026-05-21T03:15:00+08:00",
      "iterations": 28,
      "max_iterations": 30,
      "current_step": "5/5",
      "last_action": "final-verify",
      "velocity": "progressing"
    }
  },
  "completed_today": ["PS-001"],
  "paused": [],
  "history": [...]
}
```

---

## Module 5: CHECK - Progress Velocity & Crash Recovery

**Principle:** Detect stalls before they become loops. Auto-recover from crashes. Track progress velocity.

### Progress velocity tracking

After each iteration, classify task velocity:

| Velocity | Criteria | Action |
|----------|----------|--------|
| `progressing` | Steps advancing, files changing, tests passing more | Continue |
| `slow` | Same step 3+ iterations but still making small changes | Write detailed checkpoint. Continue. |
| `stalling` | Same action 2x same file, no test/criteria improvement | Self-correct: try different approach. |
| `stalled` | Same action 3x same file, zero progress | PAUSE. This is a MAJOR event. Save checkpoint. |

Velocity written to STATE.json after each iteration.

### MAJOR problems -> PAUSE + checkpoint

| Problem | Detection | Action |
|---------|-----------|--------|
| Stalled (3x same, no progress) | Velocity = `stalled` | Pause. Save checkpoint. Non-overnight: ask user. Overnight: auto-pause, continue next task. |
| Unreachable criteria | 3 different approaches fail | Pause. Report: "Criteria X unreachable because Y. Revise plan." |
| Cross-project deadlock | Circular `depends_on_cross` | Pause both. Report deadlock. |
| Plan restructured | User edits executing plan's structure | Pause. Re-read plan. Offer restart. |
| Max iterations reached | iter >= max_iterations | Pause. Save checkpoint. Flag for review. |
| Task isolation violated | Write/Edit targets outside own task dir | Immediately revert. If 3x: pause + MAJOR alert. |

### MINOR problems -> AI handles internally

| Problem | Auto-Fix |
|---------|----------|
| Step failed (1st try) | Analyze error, adjust approach, retry (max 3) |
| Test/lint failure | Fix code, re-run. 3x same failure -> escalate MAJOR |
| File conflict (user edited non-active) | Re-read file, continue |
| Slow but progressing (velocity=slow) | Write checkpoint, continue |
| Skill invocation error | Try alternative skill or manual approach |

### Crash recovery

On ANY plan-manager invocation, before executing the requested operation:

1. Read STATE.json
2. Find any tasks with `status: in_progress`
3. If found + STATE.json `mode: executing`:
   - Read iterations.log for each orphaned task
   - Report: "Found N orphaned tasks from previous session."
   - Offer: "Resume from last checkpoint?" (default: yes if overnight)
   - If yes: restore context from checkpoint, continue loop
   - If no: mark tasks `blocked`, reason: "session-ended"

### Overnight report

After overnight mode ends (all tasks complete or all stalled):
```markdown
# Overnight Report - 2026-05-21
Session: 03:15 - 05:30 (2h 15m)

## Completed
- PS-001: Rewrite SKILL.md (28 iterations, ~$3.50)
- EX-002: Research papers (15 iterations, ~$1.80)

## Paused (needs review)
- CD-001: Build auth - max iterations reached (30/30). Checkpoint saved.

## Total: 2 completed, 1 paused. ~$5.30 API cost.
```

---

## Module 6: ASSISTANT - Dashboard & Goal-Setting Guide

**Principle:** Show status. Don't interrogate. User comes for overview, not questions.

### Modes

| Trigger | Behavior |
|---------|----------|
| "assistant" / "project overview" | Full dashboard. No questions. |
| "what's next" / "what should I do" | Prioritized action list. |
| "review <project>" | Deep dive: plan quality, task status, goal alignment. |
| "review plans" | Scan ALL plans. Flag weak plans. Quality report. |
| "overnight report" | Show latest overnight run summary. |
| "iterate <project>" | Full cycle: status -> gaps -> next task -> offer draft. |

---

## File Reference

| File | Purpose |
|------|---------|
| `~/.claude/plan-manager/config.json` | Root path, parallelism, autonomy, max_iterations, overnight |
| `<root>/project/<proj>/.project` | Project metadata + goal |
| `<root>/project/<proj>/tasks/<task>/.task` | Task state machine |
| `<root>/project/<proj>/tasks/<task>/plan.md` | AI-drafted, user-reviewed plan (completion promise) |
| `<root>/project/<proj>/tasks/<task>/checkpoints/` | Auto-saved state + iterations.log |
| `<root>/STATE.json` | Global execution state, velocity tracking |
| `<root>/OVERNIGHT-REPORT.md` | Post-overnight summary |
| `<root>/DOCMAP.md` | Document index |

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `${CLAUDE_SKILL_DIR}/bin/update-docmap.sh <root>` | Regenerate DOCMAP.md |
| `${CLAUDE_SKILL_DIR}/bin/init-project.sh <root> <name>` | Create project scaffold |
| `${CLAUDE_SKILL_DIR}/bin/init-task.sh <root> <project> <title>` | Create task scaffold |
