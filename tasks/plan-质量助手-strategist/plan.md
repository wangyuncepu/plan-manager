# Plan: plan 质量助手 strategist
Task: PLA-016 | Project: plan-manager
Plan Status: review | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
给 strategist 一个可重复的「计划质量检查」脚本：自动评估 plan.md 是否目标对齐、标准可度量、步骤带 verify、必要时含 write-exception，输出评分+具体问题，辅助 make-plan / review-plans。

## Success Criteria (COMPLETION PROMISE)
- [ ] 新增脚本 scripts/plan-lint.py：输入 plan.md（或 task id），输出质量报告
- [ ] 检查项：① 有 Goal 且非空 ② success criteria ≥1 且“可度量”(含数字/文件/PASS 等线索，非“works”类空话) ③ 每个 step 含 `verify:` ④ 越界写入步骤是否声明 write-exception ⑤ Plan Status 合法
- [ ] 输出评分(如 N/5)+逐条问题+建议，zh/en 双语(--lang)
- [ ] 退出码：有 CRITICAL 问题非零，便于脚本化门控
- [ ] 接入：SKILL.md「review plans / make plan」指向用 plan-lint 做质量检查
- [ ] 自测：对一个好计划与一个故意残缺计划各跑一次，分数有区分
- [ ] verify-installation 仍绿；py_compile 通过

## Approach (AI DETERMINES)
纯标准库 + 复用 _common.py 读取风格。解析 plan.md 的分节(Goal/Success Criteria/Steps/Plan Status)，用启发式判可度量性(正则找数字/文件名/“PASS|exists|==”等，黑名单“works correctly|正常|完善”)。每检查项给 pass/warn/critical。报告 Markdown。仅新增脚本 + SKILL.md 接入说明(write-exception: SKILL.md)。

## Steps (AI EXECUTES)
1. [ ] 设计检查项与评分规则(写到脚本 docstring)-> verify: 5 项规则明确
2. [ ] 实现 plan-lint.py(解析+启发式+报告+exit code)-> verify: py_compile ok、能跑
3. [ ] 启发式可度量判定(数字/文件/PASS 线索 vs 空话黑名单)-> verify: 空话计划被标 warn/critical
4. [ ] zh/en 双语输出(--lang)-> verify: 两语均无对方语言残留(框架文案)
5. [ ] 自测：好计划(如本任务/PLA-011) vs 残缺计划，分数有区分 -> verify: 分数/问题不同
6. [ ] SKILL.md 接入：review plans/make plan 指向 plan-lint(write-exception: SKILL.md)-> verify: SKILL 含引用
7. [ ] verify-installation + py_compile -> verify: 双绿
8. [ ] 记录 checkpoints/iterations.log -> verify: log 写入

## Risks & Mitigations
- 启发式误判可度量性 -> 给 warn 而非硬 critical，提示人工确认；黑/白名单可扩
- 脚本越界写 SKILL.md -> 按 write-exception 记录该唯一外部文件
- 过度工程 -> 单文件、纯标准库、规则≤5，先简后扩

## Iteration Budget
max_iterations: 14
