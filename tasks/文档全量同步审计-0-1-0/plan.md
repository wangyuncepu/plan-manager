# Plan: 文档全量同步审计 0.1.0
Task: PLA-007 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
让 SKILL.md + 全部 references 文档与 0.1.0 实际行为完全一致，消除过时描述，使开发者读文档即得真实用法。

## Success Criteria (COMPLETION PROMISE)
- [x] 全仓无过时版本号（grep 仅 0.1.0；无 4.x / 3.x 残留）
- [x] 全仓无旧 PLS- 任务前缀引用（示例/正文统一 PLA- 或泛化占位）
- [x] references 反映对话式 UX：至少 manual 含 INTERACTION MODEL 要点，不把脚本/`--apply` 当用户必做步骤
- [x] 固定面板清单在 SKILL.md + manual 一致，且 = 实际 10 个（help/config/overview/projects/tasks/ready-queue/remote/github-status/trash/panels）
- [x] architecture / state-and-checkpoints / panels-integration / installation 与当前脚本集和行为一致（无已删 wrapper、无失效路径）
- [x] 脚本表（SKILL.md Scripts 段）列出的脚本与 scripts/ 实际文件一一对应（含 _common.py、help-panel、config-panel；无幽灵条目）
- [x] verify-installation.sh + verify-panels.sh 全绿

## Approach (AI DETERMINES)
逐文件 diff 文档声明 vs 实际：用 grep 找版本/前缀/面板清单/脚本名残留；用 `ls scripts/` 与 `panel-manage.py list` 作权威源比对；发现不一致就最小修复（文档侧为主），记录到 checkpoints/iterations.log。只改文档与必要的注释，不动脚本逻辑。

## Steps (AI EXECUTES)
1. [x] 版本号扫描全仓 -> verify: grep 仅 0.1.0，无旧版本
2. [x] 任务前缀扫描（PLS-/旧示例 ID）-> verify: 无 PLS- 残留
3. [x] 面板清单核对：SKILL.md vs manual vs `panel-manage.py list` -> verify: 三处一致且 =10
4. [x] 脚本表核对：SKILL.md Scripts 段 vs `ls scripts/*.py *.sh` -> verify: 双向无差集
5. [x] references 行为核对（architecture/state/panels-integration/installation）：删除已移除 wrapper、修失效路径、补对话式说明 -> verify: 抽查无失效引用
6. [x] 跑 verify-installation.sh + verify-panels.sh -> verify: 双绿
7. [x] 记录到 checkpoints/iterations.log + 列出所有改动文件 -> verify: log 写入、审计全绿

## Risks & Mitigations
- 文档分散，易漏 -> 以 grep + 权威源（ls / panel list）做穷举，不靠肉眼
- 修复可能越出任务目录（改 SKILL.md/references）-> 属本审计任务范围，按 write-exception 记录受影响路径到 iterations.log

## Iteration Budget
max_iterations: 15
