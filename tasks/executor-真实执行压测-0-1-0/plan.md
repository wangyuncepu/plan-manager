# Plan: executor 真实执行压测 0.1.0
Task: PLA-011 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
用一个真有产出的多步任务，在真实条件下压测 executor 核心机制（Ralph 循环、逐步标记、iterations.log、checkpoint、crash recovery、velocity），证明执行链路在非自测任务上稳定可用。所有写入仅限本任务目录。

## Success Criteria (COMPLETION PROMISE)
- [x] 在本任务目录 `artifact/` 下产出一个自包含小模块 + 测试，测试通过
- [x] 每个执行步在 `checkpoints/iterations.log` 留一条记录（≥5 步）
- [x] 中途写一次 `checkpoints/snapshot.md`（符合 checkpoint 格式：步骤勾选状态 + last action/result）
- [x] 模拟 crash recovery：从 snapshot 读出首个未勾选步并据此续跑，记录恢复点
- [x] velocity 至少记录一次（progressing），无 stalled
- [x] 全程写入不越出 `tasks/executor-真实执行压测-0-1-0/`（无 write-exception）
- [x] 收尾跑一次模块测试 PASS

## Approach (AI DETERMINES)
TDD 式：先写失败测试(RED)，再实现(GREEN)，再小重构(IMPROVE)。把每步当一次 Ralph 迭代：执行→验证→标记[x]→写 log→（中途）写 snapshot。做一次“假装中断”：写完 snapshot 后，不靠记忆、改为从 snapshot.md 解析首个未勾选步来决定下一步，验证恢复路径真实可用。产物放 artifact/，纯标准库，无外部依赖。

## Steps (AI EXECUTES)
1. [x] 建 artifact/ 目录，写失败测试 test_calc.py（RED：断言 add/divide 行为，含除零）-> verify: 运行测试 FAIL（红）
2. [x] 写 calc.py 最小实现（add）-> verify: add 测试通过、divide 仍失败
3. [x] 写 checkpoint snapshot.md（步骤勾选到 step2，last result OK）-> verify: snapshot.md 存在且格式合规
4. [x] **模拟 crash recovery**：解析 snapshot.md 找首个未勾选步=step4，据此续跑实现 divide(含除零 ValueError)-> verify: 恢复点=step4 记入 log；divide 测试通过
5. [x] 全量测试 + 小重构（类型注解/docstring）-> verify: 全测试 PASS、velocity=progressing
6. [x] 写 artifact/README 说明该产物用途 + 列最终 plan 勾选状态到 log -> verify: README 存在、log ≥5 条
7. [x] 隔离校验：确认本次所有改动路径都在任务目录内 -> verify: git status 仅本任务目录有改动

## Risks & Mitigations
- 误写任务目录外 -> 步骤 7 用 git status 校验路径；只用相对 artifact/ 与 checkpoints/
- crash recovery 走过场（其实靠记忆）-> 步骤 4 强制从 snapshot.md 解析未勾选步，恢复点写入 log 留证
- 引入外部依赖致测试不稳 -> 仅用 Python 标准库 unittest

## Iteration Budget
max_iterations: 10
