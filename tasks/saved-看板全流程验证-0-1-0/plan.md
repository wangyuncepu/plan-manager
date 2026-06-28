# Plan: saved 看板全流程验证 0.1.0
Task: PLA-012 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
端到端验证 saved 看板子系统：add/run/remove 全流程、dry-run→--apply 门控、变量展开、generate 临时看板、saved 不污染 fixed，且验证后无残留。

## Success Criteria (COMPLETION PROMISE)
- [x] add 一个 saved 看板：dry-run 不落盘，--apply 后落盘
- [x] list 中出现该 saved 看板（type=saved）
- [x] run 该 saved 看板：exit 0、输出非空、变量（$ROOT/$LANG）已展开（无字面 $ROOT）
- [x] add 不能覆盖 fixed 名（尝试同名 fixed 应被拒）
- [x] generate 临时看板：输出正常且不写入 panels.json
- [x] remove：dry-run 不删，--apply 后从 list 消失
- [x] 收尾 panels.json saved 为空（或恢复原状），fixed 计数仍=10
- [x] verify-panels.sh 全绿

## Approach (AI DETERMINES)
用临时看板名（如 _pla012_tmp）做完整 CRUD，先看 panels.json 原状以便复原。每步对照 dry-run vs --apply 的落盘差异（读 panels.json 验证）。run 时 grep 确认变量展开。验证 add 拒绝 fixed 同名（期望非零退出/报错）。generate 后确认 panels.json 未变。结束 remove --apply 清理，确认回到初始。只动 panels.json（saved 区）与读操作。

## Steps (AI EXECUTES)
1. [x] 读 panels.json 初始 saved 状态存档 -> verify: 记录初始 saved keys
2. [x] add _pla012_tmp（dry-run）-> verify: panels.json saved 未变
3. [x] add _pla012_tmp（--apply）-> verify: panels.json saved 含该名
4. [x] list -> verify: 出现 | saved | _pla012_tmp
5. [x] run _pla012_tmp -> verify: exit 0、非空、无字面 $ROOT/$LANG（已展开）
6. [x] add overview（fixed 同名，--apply）-> verify: 被拒（非零/报错，fixed 未被覆盖）
7. [x] generate 临时看板 -> verify: 输出正常且 panels.json saved 未新增
8. [x] remove _pla012_tmp（dry-run 不删 → --apply 删）-> verify: list 不再出现
9. [x] 终态校验 + verify-panels.sh -> verify: saved 回初始、fixed=10、panel registry ok
10. [x] 记录 checkpoints/iterations.log -> verify: log 写入

## Risks & Mitigations
- 残留临时看板污染 panels.json -> 步骤 1 存初始、步骤 8 删除、步骤 9 校验回初始
- 误删用户已有 saved 看板 -> 只操作专用临时名 _pla012_tmp，不碰其他
- add 覆盖 fixed -> 正是要测的护栏；若真能覆盖则为 bug，定位并修

## Iteration Budget
max_iterations: 12
