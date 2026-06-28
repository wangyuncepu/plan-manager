# Plan: trash 生命周期验证 0.1.0
Task: PLA-013 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
端到端验证 trash 子系统：项目/任务的 delete→list→show→restore→purge 全链，确认 dry-run/--apply/--force 门控、软删可恢复、purge 永久、safe_child 路径护栏，且验证后无残留、不动真实数据。

## Success Criteria (COMPLETION PROMISE)
- [x] 用专用临时项目 _pla013_proj 验证：delete（dry-run 不删 → --apply 移入 trash）
- [x] trash list 显示被删项；trash show 显示其详情
- [x] restore（dry-run 不恢复 → --apply 恢复）后项目回到 project/ 且可正常读
- [x] purge 需 --force（无 --force 拒绝）；--force --apply 后 trash 中永久消失
- [x] safe_child 护栏：trash restore/purge 传越界名（含 .. 或 /）被拒
- [x] 任务级 trash 同样验证一遍（临时任务 delete→trash→restore）
- [x] 终态：无 _pla013_* 残留于 project/ 或 trash/；真实项目/任务未受影响
- [x] trash-manage 写操作默认 dry-run（未传 --apply 不落地）

## Approach (AI DETERMINES)
建一个一次性临时项目（及一个临时任务）作靶子，全程只操作 _pla013_* 名字。每步对照 dry-run vs --apply 的实际文件系统差异（project/、.plan-manager/trash/ 下 ls 验证）。purge 用 --force 验证门控。safe_child 用恶意名（../x、a/b）验证被拒。结束确保靶子被 purge 干净、真实数据零改动（git status 仅本任务目录 + 预期的临时项目增删自洽）。

## Steps (AI EXECUTES)
1. [x] 创建临时项目 _pla013_proj（--apply）+ 一个临时任务 -> verify: project/_pla013_proj 存在
2. [x] project delete _pla013_proj（dry-run）-> verify: 项目仍在，未移动
3. [x] project delete _pla013_proj --force --apply -> verify: 移入 .plan-manager/trash/，project/ 中消失
4. [x] trash list + show -> verify: 列出且 show 有详情
5. [x] trash restore（dry-run 不动 → --apply 恢复）-> verify: 项目回 project/ 且可读
6. [x] safe_child 护栏：trash restore '../evil' 与 'a/b' -> verify: 被拒、无文件系统副作用
7. [x] 再 delete --apply → purge（无 --force 拒绝 → --force --apply 永久删）-> verify: trash 中彻底消失
8. [x] 任务级：临时项目复建 + 任务 delete --apply → trash → restore -> verify: 任务回归（或按实现确认任务 trash 路径）
9. [x] 清理：purge 所有 _pla013_* 靶子 -> verify: project/ 与 trash/ 无 _pla013_ 残留
10. [x] 终态校验真实数据未受影响 + 记录 iterations.log -> verify: 真实项目计数不变、log 写入

## Risks & Mitigations
- 误删真实项目/任务 -> 只操作 _pla013_* 专用名；每步 ls 确认目标
- purge 不可逆 -> 仅对临时靶子 purge；真实数据从不 purge
- safe_child 若未拦截越界名 -> 即为安全 bug，立即定位并修（记 write-exception）
- 临时项目残留 -> 步骤 9 purge 清理 + 步骤 10 校验

## Iteration Budget
max_iterations: 14
