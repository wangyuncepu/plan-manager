# Plan: V4.5 面板与对话式 UX 回归验证
Task: PLA-006 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
固化本轮临时修复（对话式 UX、强制面板路由、富文本输出、config 计数），把全部 10 个固定面板 + 触发链路变成一次可重复的回归验证，确保 0.1.0 行为稳定、文档同步。

## Success Criteria (COMPLETION PROMISE)
- [x] 10 个固定面板（help/config/overview/projects/tasks/ready-queue/remote/github-status/trash/panels）逐一运行，零报错、输出非空
- [x] config 面板 Panel Registry 计数 = 实际固定面板数（当前 10），不再写死
- [x] help 面板为对话式（"对我说/我会做"），不含裸 CLI 命令、无未展开占位符
- [x] SKILL.md INTERACTION MODEL + FORCED PANEL ROUTING 与脚本实际行为一致（抽查 3 个面板词触发）
- [x] verify-panels.sh 与 verify-installation.sh 全绿
- [x] manual / references 与 0.1.0 行为一致（interaction model 段、面板清单、版本号）
- [x] 版本号在 SKILL/两个 plugin.json/STATE schema 全为 0.1.0

## Approach (AI DETERMINES)
以 panel-manage.py 为权威入口逐面板冒烟；用 verify-panels.sh / verify-installation.sh 做结构校验；用 grep 核对版本与文档一致性。只读验证为主，发现不一致就最小修复并记录到 checkpoints/iterations.log。

## Steps (AI EXECUTES)
1. [x] 逐一 `panel-manage.py run <name>` 跑完 10 个固定面板 -> verify: 每个 exit 0 且输出非空
2. [x] 检查 config 面板 fixed 计数 == `panel-manage.py list` 固定行数 -> verify: 两数相等
3. [x] 检查 help 面板无裸命令/占位符、为对话式 -> verify: grep 无 `--apply`/`${`，含"对我说"
4. [x] 抽查 3 个面板词（help/overview/trash）经 FORCED ROUTING 行为 -> verify: 均先出脚本结果
5. [x] 运行 verify-panels.sh + verify-installation.sh -> verify: 双双 ok
6. [x] 版本与文档一致性核对（grep 0.1.0 + manual 面板清单 vs registry）-> verify: 无旧版本号残留、清单对齐
7. [x] 记录结果到 checkpoints/iterations.log，发现的小问题就地修 -> verify: log 写入、回归全绿

## Risks & Mitigations
- 面板依赖 gh/网络（remote/github-status）可能超时 -> 接受 `github_unknown` 为非失败态，单独标注
- 直接改文档/脚本可能越界到任务目录外 -> 文档/脚本修复属本任务范围，按 write-exception 记录受影响路径

## Iteration Budget
max_iterations: 12
