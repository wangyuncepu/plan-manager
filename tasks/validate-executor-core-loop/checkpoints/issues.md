# Executor Core Loop Issues — PLS-001

## 发现的问题

### 1. 文件隔离与计划步骤冲突 (HIGH)

**位置**: SKILL.md File Isolation 表

**问题**: executor 模式严格限制"Write/edit ONLY within own task dir"。但 plan steps 可能会要求创建项目文件（如 Step 1: "创建临时测试项目"），这需要写入 `project/` 目录。当前规则没有"plan 授权的步骤可以突破隔离"的例外。

**建议**: 加一条规则：plan steps 中显式列出的跨目录写入操作，在执行该 step 时允许。或区分"输出物"（必须在 task dir 内）和"副作用"（plan 允许的跨目录写入）。

### 2. 无自动 checkpoint 机制 (HIGH)

**位置**: SKILL.md "Auto-checkpoint before major actions"

**问题**: 指令说"auto-checkpoint before major actions"但没有定义 checkpoint 是什么格式、写到哪里。实际执行中发现需要手动创建 checkpoints/ 目录和 iterations.log。如果 executor 不知道 checkpoint 格式，这条规则是空话。

**建议**: 明确 checkpoint 的最小格式——至少把当前的 plan.md step 状态 + 最后完成的 step 号写入 `checkpoints/snapshot.md`。

### 3. STATE.json 格式未与 .task 同步 (MEDIUM)

**位置**: SKILL.md STATE.json vs .task

**问题**: STATE.json 记录 `current_step`、`iterations` 等执行状态，但 `.task` 中也有 `status` 字段。执行时需要更新两个地方，却没有明确说明何时更新哪个。

**建议**: 明确 STATE.json 是 execution runtime 状态（临时），.task 是持久状态。STATE.json 在每次 iteration 后更新，.task 仅在状态转换（ready→in_progress→completed）时更新。

### 4. "Auto-continue" 行为未定义 (MEDIUM)

**位置**: SKILL.md "Auto-continue: when one task completes, pick next ready task"

**问题**: 指令说"auto-continue"但在 executor 模式的 Available operations 表中明确列出了"execute N projects"。这两种触发方式的关系是什么？如果 executor 只执行了 1 个 task 就自动 continue 到下一个，那么 parallelism 参数的意义是什么？

**建议**: 区分两种模式：
- execute 1 project: 完成当前 task 后停止
- execute N projects / auto: 完成当前 task 后自动选下一个 ready task

### 5. Crash recovery 前提条件未检查 (MEDIUM)

**位置**: SKILL.md Module 5 "Crash recovery"

**问题**: "On startup: check STATE.json for orphaned in_progress tasks → offer resume from checkpoint"——但 checkpoint 可能不存在（如本次执行），恢复逻辑不知道要回退到哪里。

**建议**: 如果没有 checkpoint 文件，fallback 到 "从 plan.md 的第一个未完成 step 重新开始"。

### 6. executor 写 STATE.json 但 strategist 也在分析时读取 (LOW)

**位置**: SKILL.md File Isolation 表

**问题**: STATE.json 的写入权限只有 executor（Module 4）。但在 TST-001 执行中，实际上需要通过 Updates to STATE.json 反映执行进度。这是合理的，但未说明 executor 应该在每次 iteration 后都更新 STATE.json。

**建议**: 在 Module 4 execution loop 第 4 步后加"更新 STATE.json 中的 iterations 和 current_step 字段"。
