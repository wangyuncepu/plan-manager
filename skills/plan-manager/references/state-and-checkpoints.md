# State and Checkpoints

## STATE.json

```json
{
  "version": "0.1.0",
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

Executor owns writes to `STATE.json`. Strategist reads it, except role-switch checkpoint metadata.

## Checkpoint Format

```markdown
# Checkpoint — <timestamp>
Task: <TASK-ID> | Iteration: <N>/<max>
Last completed step: <N>
Plan step status:
- [x] step 1
- [ ] step 2
Last action: <what was done>
Last result: <OK/FAIL>
```

Crash recovery resumes from `checkpoints/snapshot.md` first, then falls back to first unchecked `plan.md` step.
