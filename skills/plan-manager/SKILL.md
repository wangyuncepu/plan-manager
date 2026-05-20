---
name: plan-manager
version: 4.0.0
description: |
  Autonomous multi-project orchestration system. User sets goals and reviews
  plans; AI handles drafting, execution, and routine decisions. Intervenes
  only on major problems (loops, deadlocks, unreachable success criteria).
  Concurrent editing of non-running projects is always safe.
  1. Project — project registry and lifecycle
  2. Task — priority/dependency ordering, one active per project
  3. Plan — AI drafts plans from goals, user reviews and approves
  4. Execute — auto-start, auto-continue, zero-interaction execution
  5. Check — auto-checkpoint, loop detection, major/minor problem classification
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

# /plan-manager — Autonomous Multi-Project Orchestration

## User Role & Autonomy Model

**User does:**
- Set project goals and priorities
- Review and approve AI-drafted plans
- Intervene on MAJOR problems (loops, deadlocks, unreachable goals)
- Edit non-running projects anytime; edit non-active tasks in running projects

**AI does (autonomously, no user prompts):**
- Draft plans from task descriptions
- Execute tasks step by step, invoke other skills as needed
- Write/edit ONLY within the active task's own directory (`project/<proj>/tasks/<task-slug>/`)
- Read any file for context (other tasks, plans, project metadata) — read-only
- Auto-checkpoint before major actions
- Auto-continue: when one task completes, pick next ready task
- Handle minor problems internally (retry, course-correct, re-plan approach)

## File Isolation (CRITICAL)

During execution, each task has a **sandbox** — its own task directory:

```
project/CDMSystem/
├── .project                    ← 🔒 AI never writes here during execution
├── README.md                   ← 🔒 AI never writes here during execution
└── tasks/
    ├── build-auth/             ← ✅ Task "build-auth" writes HERE only
    │   ├── .task
    │   ├── plan.md
    │   └── checkpoints/
    └── other-task/             ← 🔒 Task "build-auth" never writes here
        ├── .task
        └── plan.md
```

| Operation | Allowed during task execution? |
|-----------|-------------------------------|
| Read any file in any project | ✅ Yes — needed for context |
| Write/edit within own task directory | ✅ Yes — this is the work |
| Write/edit `.project` (own project) | 🔴 Never — user owns project metadata |
| Write/edit other task's `.task` or `plan.md` | 🔴 Never — each task is isolated |
| Write/edit other project (any file) | 🔴 Never — cross-project isolation |
| Write `<root>/STATE.json` | ✅ Module 4 only, to update execution state |
| Write `<root>/DOCMAP.md` | ✅ Only when explicitly running "update doc index" |

---

## Architecture

```
<root>/
├── project/<proj>/
│   ├── .project               ← project metadata (YAML)
│   ├── README.md              ← project description
│   └── tasks/<task-slug>/
│       ├── .task              ← task metadata (YAML)
│       ├── plan.md            ← REQUIRED: user-reviewed execution plan
│       └── checkpoints/       ← auto-saved state snapshots
├── STATE.json                 ← global execution state
├── DOCMAP.md                  ← document index (auto-generated)
└── .plan-manager/
```

**Config:** `~/.claude/plan-manager/config.json`
```json
{
  "root": "/path/to/root",
  "parallelism": 2,
  "autonomy": "full"
}
```

| Config key | Default | Meaning |
|------------|---------|---------|
| `root` | (required) | Management root path |
| `parallelism` | 2 | Default N for "execute N projects" |
| `autonomy` | `full` | `full`=never ask during execution; `plan-review`=ask before plan changes; `supervised`=ask before each task |

**Core rules:**
- One task `in_progress` per project at a time
- Every task MUST have a `plan.md` with `Status: approved` before execution → otherwise status stays `planned`, not `ready`
- AI drafts plans; user reviews goals and success criteria
- AI auto-continues: complete → pick next → execute, without asking
- **File isolation:** A running task writes ONLY within its own task directory. Never edits other tasks, `.project`, or sibling folders in the same project. Read is unrestricted.

**Task lifecycle:**
```
pending → planned → ready → in_progress → completed
  ↓         ↓         ↓         ↓
cancelled  (no plan) blocked  blocked
```

---

## Phase 0: Configuration

### On every invocation

1. Read `~/.claude/plan-manager/config.json` → `$ROOT`, `$N` (parallelism), `$AUTONOMY`
2. If missing: configure.

### Configure ("configure plan manager", "setup plan manager")

Ask user for root path. Create structure. Write config with defaults.
```bash
mkdir -p "$ROOT/project"
cat > ~/.claude/plan-manager/config.json << EOF
{"root":"$ROOT","parallelism":2,"autonomy":"full"}
EOF
```

### Change settings ("set parallelism to N", "autonomy full/supervised")

Update individual config keys. Report new value.

---

## Module 1: PROJECT

### .project format
```yaml
name: string
slug: string
status: active | idle | completed | archived
priority: P0 | P1 | P2 | P3
created: YYYY-MM-DD
goal: string          # one-sentence project goal (user sets this)
description: string
notes: string
```

### List projects ("list projects", "project overview")

Show table:
```
| Project | Status | Goal | Tasks (active/total) | Priority |
|---------|--------|------|---------------------|----------|
| PlanSkill | active | Build plan-manager skill | 1/3 | P0 |
| ExophMetry | idle | Research exophthalmometry | 0/2 | P1 |
```

### Create project ("create project <name>")

1. Slugify name. Create folder structure.
2. **Ask user for the project goal** (one sentence). This is the user's only mandatory input.
3. Write `.project` with goal field.
4. Report created.

### Show project ("show project <name>")

Read `.project`, list tasks with status, show active task details.

---

## Module 2: TASK

### .task format
```yaml
id: PRJ-001
slug: string
title: string
project: string
status: pending | planned | ready | in_progress | completed | cancelled | blocked
priority: P0 | P1 | P2 | P3
order: number
created: YYYY-MM-DD
deadline: YYYY-MM-DD
completed: YYYY-MM-DD
depends_on: []
depends_on_cross: []
description: string        # AI can expand this into plan
notes: string
plan_file: string
```

### Task ordering (per project)
1. Dependency chain (blocked after deps)
2. Priority (P0 → P3)
3. `order` field

### List tasks ("list tasks", "task status")
Per-project table with status, plan existence (✓/✗), priority.

### Create task ("add task to <project>", "new task")

1. If project not specified, list projects.
2. Ask: title, priority, description.
3. Auto-assign ID, slug, order.
4. Create `.task` with `status: pending`, `plan_file: ""`.
5. Report: "Task `<ID>` created. Next: 'make plan for <ID>' to auto-draft a plan."

### Update task ("start/cancel/block <ID>")

Same as v3. "Complete" handled by Module 4 auto-continue.

---

## Module 3: PLAN — AI Drafts, User Reviews

**Principle:** AI writes the plan based on task description and project goal. User reviews the goal and success criteria. AI handles approach and steps autonomously.

### plan.md template

```markdown
# Plan: <task-title>
Task: <TASK-ID> | Project: <project-name>
Plan Status: draft | review | approved | executing | done
Created: YYYY-MM-DD | Updated: YYYY-MM-DD

## Goal
<One sentence: what does this task achieve? Must align with project goal.>

## Success Criteria (USER REVIEWS THIS SECTION)
- [ ] <measurable outcome 1>
- [ ] <measurable outcome 2>

## Approach (AI DETERMINES)
<Architecture, tools, skills to invoke, strategy.>

## Steps (AI EXECUTES)
1. [ ] <step 1> → verify: <check>
2. [ ] <step 2> → verify: <check>

## Risks & Mitigations (AI IDENTIFIES)
- <risk> → <mitigation>

## Notes
<Context, constraints, cross-project dependencies.>
```

### Create plan ("make plan for <ID>", "plan for <ID>")

1. Find task. Read project `.project` for the goal.
2. **AI auto-drafts the full plan** from task description + project goal.
   - Infer goal from task description if not explicit
   - Determine approach based on project context
   - Break into verifiable steps
3. Write `plan.md` with `Plan Status: draft`.
4. Update `.task`: `plan_file: plan.md`, `status: planned`.
5. **Show user the goal + success criteria. Ask: "Does this look right?"**
   - User says yes → set `Plan Status: approved`, task `status: ready`
   - User says no → user corrects goal/criteria → set approved/ready
   - User wants to edit approach/steps → they can, but AI handles those
6. Report: "Plan for `<ID>` approved. Task is `ready`."

### Review plan quality ("review plan for <ID>")

AI checks (no user needed unless problem found):
- Goal clear and aligned with project goal?
- Success criteria measurable?
- Steps have verifiable checkpoints?
- Risks identified with mitigations?
- Cross-project dependencies noted?

Report findings. If all good: "Plan looks solid. Approve with 'approve plan for <ID>'."

### User edits plan

User can edit `plan.md` of any non-active task at any time (see Concurrent Editing Safety). If Plan Status is `executing` and user edits, AI re-reads the plan on next checkpoint.

---

## Module 4: EXECUTE — Autonomous, Zero-Interaction

**Principle:** Once user says "execute N projects", AI runs autonomously. No confirm dialogs. No "should I continue?". Auto-continue to next task.

### Start execution ("execute N projects", "run tasks", "start execution", "auto")

1. If N not specified: use `config.parallelism` default.
2. Compute execution plan (no user confirm):
   - For each project: pick top `ready` task (dependency-sorted, priority-sorted)
   - Filter: projects with `in_progress` are skipped (one-task rule)
   - Pick top N projects by project priority
3. Display plan, set each task `status: in_progress`, update STATE.json.
4. **Begin executing immediately.** No confirmation step.

### Execution loop (autonomous)

```
LOOP:
  FOR each active task:
    1. Read plan.md → find next unchecked step
    2. Execute step (invoke other skills as needed)
       → CONSTRAINT: All Write/Edit ops target ONLY <own-task-dir>/
       → Read is unrestricted — read other tasks/plans for context freely
    3. Check step verification → mark [x] or retry
    4. Write checkpoint to <own-task-dir>/checkpoints/
    5. IF all steps done AND all success criteria met:
       → mark task completed, update STATE.json
       → auto-pick next ready task from SAME project (if exists)
       → if no ready tasks in project, pick from next priority project
  IF no active tasks remain:
    → report "All tasks complete. Active projects: 0."
    → suggest "assistant" for next actions
  ELSE:
    → continue loop
```

### Auto-continue

When a task completes:
1. Check same project for next `ready` task → auto-start it
2. If none: check other projects with `ready` tasks → auto-start up to N
3. Update STATE.json. Report: "PS-001 completed. Auto-starting PS-002."
4. **No user prompt.** Continue executing.

### User interrupts execution

User can say "stop", "pause all", or "pause <project>" at any time:
- Running tasks → checkpoint + set `status: blocked`
- STATE.json updated
- Report: "Paused. PS-001 at step 3/5. Resume with 'continue'."

### STATE.json (enhanced)

```json
{
  "updated": "...",
  "mode": "executing",
  "parallelism": 2,
  "active": {
    "PlanSkill": {"task_id": "PS-001", "started": "...", "iterations": 3, "current_step": "3/5", "last_action": "..."},
    "ExophMetry": {"task_id": "EX-002", "started": "...", "iterations": 1, "current_step": "1/4", "last_action": "..."}
  },
  "completed_today": ["PS-001"],
  "history": [...]
}
```

---

## Module 5: CHECK — Major vs Minor Problems

**Principle:** AI handles minor problems internally. Only MAJOR problems interrupt and ask user.

### MAJOR problems → PAUSE + ASK USER

| Problem | Detection | AI Action |
|---------|-----------|-----------|
| 🔴 Loop detected | Same action + same file 3x, no step progress | Pause task. Save checkpoint. Ask user: "PS-001 looped on step 3. Continue or revise plan?" |
| 🔴 Unreachable criteria | Step fails 3 different approaches, success criteria clearly can't be met | Pause task. Report: "Success criteria X cannot be met because Y. Revise plan?" |
| 🔴 Cross-project deadlock | Task A waits on Task B, Task B waits on Task A | Pause both. Report deadlock. Ask user to break the cycle. |
| 🔴 Plan needs rewrite | User edits plan.md of executing task, structure changed | Pause. Re-read plan. Ask: "Plan changed significantly. Restart from step 1?" |

### MINOR problems → AI handles internally

| Problem | AI Auto-Fix |
|---------|-------------|
| 🟡 Step failed (1st try) | Analyze error, adjust approach, retry (max 3 attempts) |
| 🟡 Test failure | Fix code, re-run. If 3x same failure → escalate to MAJOR |
| 🟡 File conflict (user edited non-active file) | Re-read file, continue. No pause. |
| 🟡 Slow progress | Write checkpoint, note in STATE.json, continue |
| 🟡 Skill invocation error | Try alternative skill or manual approach |
| 🟡 File isolation breach (self-detected) | Immediately revert. Re-read correct target. Redirect write to own task dir. Log incident. If 3x → escalate to MAJOR. |

### Auto-checkpoint

Before every Write/Edit/Bash during execution, write a 3-line checkpoint:
```bash
echo "step:3/5 action:edit-SKILL.md time:$(date -Iseconds)" >> "$CHECKPOINT_DIR/log.txt"
```

Full checkpoint (before risky operations or every 5 iterations):
```markdown
# CK: <TASK-ID> — Step 3/5
Time: ... | Iterations: 5
Done: Steps 1-2 complete. SKILL.md Module 4 rewritten.
Next: Step 3 — update helper scripts.
Blocker: none
```

### Health check ("check tasks", "task health")

Show running tasks with iteration count, current step, alerts. No user action needed unless MAJOR flagged.

---

## Module 6: ASSISTANT — Dashboard & Goal-Setting Guide

**Principle:** Show status. Don't interrogate. User comes to assistant for overview, not to answer questions.

### Assistant modes

| Trigger | Behavior |
|---------|----------|
| "assistant" / "project overview" | Full dashboard. No questions. |
| "what's next" / "what should I do" | Prioritized action list. User decides. |
| "review <project>" | Deep dive: plan quality, task status, goal alignment |
| "review plans" | Scan ALL plans across ALL projects. Flag weak plans (vague goals, unmeasurable criteria, missing risks). Show quality report. |
| "iterate <project>" | Full cycle: show status → identify gaps → suggest next task → offer to draft plan |

### Dashboard output (no questions)

```
# Plan Manager — Status

## 🏗️ Executing (2/2 parallel)
| Project | Task | Step | Iter | Status |
|---------|------|------|------|--------|
| PlanSkill | PS-001 — Rewrite SKILL.md | 3/5 | 4 | OK |
| ExophMetry | EX-002 — Research papers | 1/4 | 2 | OK |

## 📋 Ready Queue (3 tasks across 2 projects)
| # | Project | Task | Priority |
|---|---------|------|----------|
| 1 | PlanSkill | PS-002 — Update helpers | P1 |
| 2 | ExophMetry | EX-003 — Write summary | P2 |
| 3 | CDMSystem | CD-001 — Build auth | P1 |

## ⚠️ Needs User Attention
- **PlanSkill/PS-003** — Plan is still draft. Review and approve?
- **CDMSystem** — No tasks created. Set project goal first?

## 🟢 Completed Today
- PS-001 (partial — 3/5 steps)
```

### Plan quality review ("review plans")

AI scans all `plan.md` files. Flags:
- ❌ Goal missing or vague ("implement stuff")
- ❌ Success criteria not measurable ("works correctly")
- ⚠️ No risks identified
- ⚠️ Steps not verifiable
- ✅ Good plan (all sections strong)

Shows table. User decides which to fix.

### Goal-setting guide

When user says "I want to build X" or describes a new initiative:
1. Help user formulate a clear one-sentence goal
2. Offer to create project + auto-draft first task plan
3. "Project `<name>` created with goal: `<goal>`. First task plan drafted. Review with 'review plans'."

---

## File Reference

| File | Purpose |
|------|---------|
| `~/.claude/plan-manager/config.json` | Root path, parallelism, autonomy level |
| `<root>/project/<proj>/.project` | Project metadata + goal |
| `<root>/project/<proj>/tasks/<task>/.task` | Task state machine |
| `<root>/project/<proj>/tasks/<task>/plan.md` | AI-drafted, user-reviewed plan |
| `<root>/project/<proj>/tasks/<task>/checkpoints/` | Auto-saved state |
| `<root>/STATE.json` | Global execution state |
| `<root>/DOCMAP.md` | Document index |

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `${CLAUDE_SKILL_DIR}/bin/update-docmap.sh <root>` | Regenerate DOCMAP.md |
| `${CLAUDE_SKILL_DIR}/bin/init-project.sh <root> <name>` | Create project scaffold |
| `${CLAUDE_SKILL_DIR}/bin/init-task.sh <root> <project> <title>` | Create task scaffold |
