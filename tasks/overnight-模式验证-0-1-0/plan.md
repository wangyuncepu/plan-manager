# Plan: overnight 模式验证 0.1.0
Task: PLA-014 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
验证 overnight 模式契约在真实条件下成立：标志开关、max_iterations 加倍、无人值守连续执行、结束生成 OVERNIGHT-REPORT.md，且验证后无残留、overnight 复原 false。

## Success Criteria (COMPLETION PROMISE)
- [x] config overnight 标志可开/可关（开后 config 面板显示 overnight=true）
- [x] 加倍语义核对：overnight 下任务有效 max_iterations = 配置值×2（用一个临时任务的 max_iterations 推演验证）
- [x] 受控无人值守跑：临时项目下 2 个小就绪任务在 overnight 模式连续完成，全程无 AskUserQuestion（无用户提示）
- [x] 结束生成 `<root>/OVERNIGHT-REPORT.md`，含 完成/暂停/成本(或迭代) 小节
- [x] 安全：需提示的情形下应 checkpoint+停而非乱猜（用文字核对该规则，不制造破坏性场景）
- [x] 清理：临时项目 purge；OVERNIGHT-REPORT.md 为本次验证产物（保留或删，记录选择）
- [x] 复原：overnight=false；真实项目未受影响

## Approach (AI DETERMINES)
建一次性临时项目 _pla014_proj，放 2 个极小就绪任务（各 1-2 步、纯 echo/文件写在各自任务目录）。开 overnight，executor 连续执行两者（auto 语义），不发任何提示；完成后汇总写 <root>/OVERNIGHT-REPORT.md（write-exception）。加倍语义用临时任务 max_iterations 字段推演（如配置 30 → overnight 有效 60）。safety「需提示则 checkpoint+停」以文字核对契约，不实造破坏场景。结束 purge 临时项目、复原 overnight=false。

## Steps (AI EXECUTES)
1. [x] 记录初始 overnight 值；开 overnight=true -> verify: config 面板 overnight=true
2. [x] 建 _pla014_proj + 2 个就绪小任务（含已批准 1-2 步 plan，产出落各自任务目录）-> verify: ready-queue 含 2 任务
3. [x] overnight 连续执行两任务（无人值守、无提示）-> verify: 两任务 completed、无 AskUserQuestion 发生
4. [x] 加倍语义核对 -> verify: overnight 下有效上限 = 配置 max_iterations×2（文字+字段推演一致）
5. [x] 生成 <root>/OVERNIGHT-REPORT.md（write-exception: <root>/OVERNIGHT-REPORT.md）-> verify: 文件存在且含 完成/暂停/成本 小节
6. [x] safety 契约核对：需提示→checkpoint+停 -> verify: 规则与 SKILL 一致，记录
7. [x] 清理 _pla014_proj（delete+purge）+ 复原 overnight=false -> verify: 无 _pla014 残留、overnight=false
8. [x] 记录 checkpoints/iterations.log + 真实项目计数不变 -> verify: log 写入、真实项目数不变

## Risks & Mitigations
- overnight 卡 true 留副作用 -> 步骤 1 记录初始、步骤 7 强制复原
- 临时任务残留 -> 步骤 7 purge + 步骤 8 校验
- OVERNIGHT-REPORT.md 写在 root（越界）-> 属 overnight 既定行为，按 write-exception 记录该唯一外部路径
- 无人值守误触发破坏操作 -> 临时任务仅 echo/写自身目录，无危险操作

## Iteration Budget
max_iterations: 12
