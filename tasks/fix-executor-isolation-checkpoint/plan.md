# Plan: 修复 executor 文件隔离与 checkpoint 问题
Task: PLS-002 | Project: PlanSkill
Plan Status: done | Created: 2026-06-08 | Updated: 2026-06-08

## Goal

修复 PLS-001 发现的 6 个 executor 模式行为定义缺陷，全部在 SKILL.md 内修改，不创建新文件。

## Success Criteria (COMPLETION PROMISE)

- [ ] 文件隔离规则增加 plan-step 例外说明
- [ ] checkpoint 最小格式已定义在 Module 5 中
- [ ] STATE.json vs .task 更新时机已明确
- [ ] auto-continue 行为按 parallelism 区分
- [ ] crash recovery 有 checkpoint 缺失时的 fallback 逻辑
- [ ] Module 4 execution loop 包含 STATE.json 更新步骤

## Approach

每次修改只动 SKILL.md 的一个段落，改完验证上下文是否连贯。

## Steps

1. [x] 修复 #1: 文件隔离表加 plan-step 例外 → verify: File Isolation 段 `| Write outside task dir | Never | Only when plan step explicitly lists it |`
2. [x] 修复 #2: Module 5 定义 checkpoint 最小格式 → verify: 存在 `snapshot.md` 格式描述（done step N + remaining steps）
3. [x] 修复 #3: 区分 STATE.json 和 .task 更新时机 → verify: Module 4 loop 中每步说清楚更新哪个
4. [x] 修复 #4: auto-continue 区分 execute N 行为 → verify: Module 4 Start execution 段区分"execute 1 project"(停) vs"auto"(continue)
5. [x] 修复 #5: crash recovery fallback → verify: Module 5 Crash recovery 段存在"无 checkpoint→从 plan.md 首个未完成 step 恢复"
6. [x] 修复 #6: STATE.json 更新频率 → verify: Module 4 execution loop step 4 后多一句"更新 STATE.json"
7. [x] 全文检查 → verify: 无矛盾、无新增断裂引用

## Risks & Mitigations

- 修改可能引入新的歧义 → 每步修改后检查上下文连贯性
- 6 个修改有交叉依赖 → 按序号顺序修改，#1-#3 是独立的基础修改，#4-#6 依赖 #3

## Iteration Budget
max_iterations: 7
