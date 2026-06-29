# Plan: 跨项目管理 角色与隔离设计决策
Task: PLA-019 | Project: plan-manager
Plan Status: review | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
针对 dogfood 反馈 #1/#2（双角色墙 × 文件隔离墙在「用一个任务管理另一个项目」时冲突），产出一份设计决策文档：明确跨项目/外部项目管理的授权与护栏方案，先定方案再写码。本任务只出设计，不改行为代码。

## Success Criteria (COMPLETION PROMISE)
- [ ] 产出 design-decision.md（本任务目录），陈述问题、约束、候选方案、推荐
- [ ] 清楚复述冲突：executor 不能起草子计划 + 写入他项目属越界（来自 dogfood 实证）
- [ ] 列 ≥3 候选方案并评估（如：A 计划级 project-scope write-exception；B 单一被批准计划内允许 strategist 起草+executor 执行连续；C 工具级跨目录写入确认护栏；D 显式「外部项目管理模式」）
- [ ] 每候选给 利/弊/对前提(减少交互/反馈>功能/不崩)的影响
- [ ] 给出推荐方案 + 落地为后续任务的拆解（不在本任务实现）
- [ ] 不改任何行为脚本/SKILL（纯设计产出，落本任务目录）

## Approach (AI DETERMINES)
回顾 SKILL 的 INTERACTION MODEL / File Isolation / 双角色规则与 dogfood 实证，提炼冲突本质（隔离与编排的张力）。枚举候选授权/护栏机制，逐一评估对安全与交互成本的权衡，给推荐与实施拆解。纯文档，落 design-decision.md，不动代码。

## Steps (AI EXECUTES)
1. [ ] 复盘冲突与现有规则（File Isolation 表 + executor make-plan BLOCKED + write-exception）-> verify: 冲突陈述含具体规则引用
2. [ ] 枚举 ≥3 候选方案 -> verify: 候选数达标、各自机制清楚
3. [ ] 评估每候选 利/弊/对前提影响 -> verify: 每候选三项齐
4. [ ] 给推荐 + 后续任务拆解 -> verify: 推荐明确、拆解可执行
5. [ ] 写 design-decision.md -> verify: 文件存在、含问题/候选/推荐/拆解
6. [ ] 确认未改行为代码 -> verify: git status 仅本任务目录
7. [ ] 记录 checkpoints/iterations.log -> verify: log 写入

## Risks & Mitigations
- 设计空泛 -> 强制每候选 利/弊/前提影响 + 落地拆解
- 顺手改代码越界 -> 本任务纯文档，步骤 6 git 校验仅本任务目录
- 方案与安全冲突 -> 评估须含「是否削弱文件隔离安全」一栏

## Iteration Budget
max_iterations: 12
