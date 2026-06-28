# Plan: 验证 executor 端到端执行链路
Task: PLA-001 | Project: PlanSkill
Plan Status: done | Created: 2026-06-08 | Updated: 2026-06-08

## Goal

用 plan-manager executor 模式跑通完整 Core Loop，验证 Module 4/5 的指令在实际执行中是否清晰可工作，记录所有卡点。

## Success Criteria (COMPLETION PROMISE)

- [x] 用 executor 模式完成一条完整链路：创建测试项目→加任务→制定计划→切换 executor→执行→标记完成
- [x] iterations.log 有 ≥1 条迭代记录，格式正确
- [x] STATE.json 在任务执行期间正确反映状态变化
- [x] 问题清单已输出到 checkpoints/，列出所有 skill 指令模糊/断裂点

## Approach

这是吃狗粮任务——用 plan-manager 验证 plan-manager。关键是观察 executor 模式的 runtime 行为是否符合 SKILL.md 的设计意图。

**不需要写代码**。需要的是：
1. 切换到 executor 角色
2. 以 executor 身份跑一遍执行流程
3. 观察和记录行为偏差

## Steps

1. [x] 创建一个临时测试项目（含一个简单任务+计划）→ verify: `.project` 和 `.task` 和 `plan.md` 存在
2. [x] switch to executor → verify: config.json 中 role=executor
3. [x] 执行测试项目 → verify: 观察 execution loop 8 步是否按 SKILL.md 描述执行
4. [x] 检查产出 → verify: iterations.log 存在且格式正确，STATE.json 状态正确
5. [x] 记录问题 → verify: checkpoints/issues.md 存在，列出发现的指令模糊点

## Risks & Mitigations

- executor 模式可能根本跑不起来（因为从未验证过）→ 这本身就是最有价值的发现
- SKILL.md 的指令在 executor 角色下可能有歧义 → 记录具体是哪个指令、哪行、导致了什么行为
- max_iterations=5 可能不够 → 如果正在取得进展且未超过，可以手动调整

## Iteration Budget
max_iterations: 5
