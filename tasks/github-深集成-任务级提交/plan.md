# Plan: GitHub 深集成 任务级提交
Task: PLA-017 | Project: plan-manager
Plan Status: review | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
在已就绪的 github-manage 写操作之上，提供「任务完成→提交其产出」的任务级 auto-commit 能力（可选 PR 联动），严守 dry-run/--apply 门控与安全边界，默认不自动触发。

## Success Criteria (COMPLETION PROMISE)
- [ ] github-manage.sh 新增 commit-task 子命令：为指定任务生成一次提交（限该任务目录改动）
- [ ] 默认 dry-run：显示将提交的文件 + 拟用 commit message，--apply 才真正提交
- [ ] commit message 规范：`feat(task): <TASK-ID> <title>`（或项目约定）
- [ ] 安全边界：只 add 该任务目录路径，绝不 `git add -A`；不 push（push 仍走显式 push 子命令）
- [ ] 不改变默认执行流：auto-commit 仅在用户显式要求时发生（executor 不自动提交）
- [ ] 可选 PR 联动设计为文档/占位（本任务先不强做真实 PR，除非低风险可达）
- [ ] 自测：用一个临时任务目录验证 dry-run 列表正确、--apply 真提交、范围不越界
- [ ] SKILL.md/manual 记录新子命令与安全约束；bash -n 通过

## Approach (AI DETERMINES)
扩展 github-manage.sh：commit-task <TASK-ID>，解析任务目录，`git add -- <task-dir>` 后 `git commit`（dry-run 仅 `git -c ... status --porcelain -- <task-dir>` + 打印拟提交信息）。严格路径限定，拒绝空改动。不碰 push。用临时任务自测后清理。仅改 github-manage.sh + 文档(write-exception: github-manage.sh 已属脚本；SKILL.md/manual 文档)。

## Steps (AI EXECUTES)
1. [ ] 设计 commit-task 接口与安全约束(docstring/usage)-> verify: 约束明确(仅任务目录、不 -A、不 push)
2. [ ] 实现 dry-run：列出任务目录内改动 + 拟 commit message -> verify: 临时任务有改动时正确列出
3. [ ] 实现 --apply：`git add -- <task-dir> && git commit` -> verify: 仅该任务目录文件入提交
4. [ ] 越界防护：空改动拒绝；路径限定校验 -> verify: 空改动报错、其他目录不被 add
5. [ ] 自测全流程(临时任务 dry-run→apply→检查提交范围)+ 清理 -> verify: 提交只含任务目录、临时物清理
6. [ ] PR 联动：文档化设计(占位)，标注后续 -> verify: manual 含 PR 设计说明
7. [ ] 文档接入 SKILL.md/manual + bash -n -> verify: 文档更新、语法 ok
8. [ ] 记录 checkpoints/iterations.log -> verify: log 写入

## Risks & Mitigations
- 误 `git add -A` 污染他处 -> 强制 `git add -- <task-dir>`，步骤 4 校验范围
- 自动提交破坏用户提交节奏 -> 仅显式触发，executor 不自动 commit
- 真实 PR 副作用 -> 本任务 PR 仅设计/占位，不强做真实 PR
- 改 github-manage.sh 影响现有命令 -> 只新增子命令，回归现有 status/push 行为

## Iteration Budget
max_iterations: 16
