# Plan: 英文 en 输出回归 0.1.0
Task: PLA-008 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
确认 language=en 下所有面向用户的输出（面板、help、CRUD 提示、config）英文完整、无中文残留、无报错，保证开发者受众的英文体验可用。

## Success Criteria (COMPLETION PROMISE)
- [x] en 下 10 个固定面板逐一运行，exit 0、输出非空
- [x] en 面板/help/CRUD 输出无中文字符残留（CJK 扫描为零，数据内容如项目名除外）
- [x] help 面板 en 版为对话式（"Say / I do"），无裸 CLI、无占位符
- [x] config 面板 en 版字段标签为英文
- [x] CRUD dry-run 提示（project/task create）en 下英文
- [x] 回归期间临时改的 language 复原为 zh（不留副作用）
- [x] verify-panels.sh + verify-installation.sh 仍全绿

## Approach (AI DETERMINES)
临时把 config language 切 en（记录原值 zh），逐面板/命令跑 en 输出，用 CJK 正则扫描脚本“框架文案”是否残留中文（排除数据值如中文项目名/目标）。完成后复原 language=zh。发现英文缺失/硬编码中文就最小修复脚本文案，记录到 checkpoints/iterations.log。

## Steps (AI EXECUTES)
1. [x] 记录当前 language=zh，临时切 en -> verify: config 显示 en
2. [x] en 跑 10 固定面板 -> verify: 每个 exit 0、非空
3. [x] CJK 残留扫描 help/config/overview/projects/tasks/ready-queue/trash 的框架文案 -> verify: 无意外中文（数据值除外）
4. [x] en help 对话式 + 无裸 CLI/占位符 -> verify: 含 "Say"/"I do"，无 `--apply`/`${`
5. [x] en CRUD dry-run 提示检查（project/task create）-> verify: 英文
6. [x] 复原 language=zh -> verify: config 回 zh
7. [x] verify-panels + verify-installation + 记录 log -> verify: 双绿、log 写入；列出修改文件
8. [x] 如修了脚本文案，跑 py_compile -> verify: ok

## Risks & Mitigations
- 切 en 忘了复原 -> 步骤 6 强制复原，步骤 1 先记录原值
- 误把数据内的中文（项目名/目标）判为 bug -> 扫描只针对脚本静态文案，数据值人工排除
- 修脚本文案越界任务目录 -> 属本回归范围，按 write-exception 记录受影响脚本路径

## Iteration Budget
max_iterations: 12
