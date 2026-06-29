# Plan: 注册既有项目体验打磨
Task: PLA-018 | Project: plan-manager
Plan Status: review | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
打磨「注册既有内容目录」体验（dogfood 反馈 #3/#4/#5）：自动从素材提议目标、对既有内容跳过或询问 README、dry-run 区分新建 vs 就地注册，降低交互成本。

## Success Criteria (COMPLETION PROMISE)
- [ ] create 检测目标目录已存在且非空时，dry-run 文案明确标注「就地注册既有目录（N 个已有文件）」而非「create at <path>」
- [ ] 既有内容目录注册时，不再无条件生成 README.md：已存在内容则跳过自动 README（或仅在缺 README 时生成）
- [ ] SKILL.md「create project」流程补充：检测到既有内容时，先从目录素材提议目标让用户确认，再 --apply
- [ ] 既有 README/内容文件零覆盖（仅新增 .project，必要时新增 README）
- [ ] 自测：对一个含文件的临时目录 vs 一个空目录分别 dry-run，文案有区分；含 README 的目录注册不被覆盖
- [ ] verify-installation + 相关脚本 py_compile/bash -n 通过

## Approach (AI DETERMINES)
改 project-manage.py create：注册前探测目录是否存在/是否非空/是否已有 README；dry-run 输出据此分支文案；README 生成改为「缺失才建」。SKILL.md 在 create 流程加「既有项目→提议目标」一步（行为约定）。纯改 project-manage.py + SKILL.md（write-exception: SKILL.md）。用临时目录自测，结束清理。

## Steps (AI EXECUTES)
1. [ ] 读 project-manage.py create 现有逻辑，定位 README 生成与 dry-run 文案 -> verify: 定位行号
2. [ ] dry-run 文案分支：空目录 vs 既有非空目录（标注已有文件数）-> verify: 两场景文案不同
3. [ ] README 生成改为「缺失才建」-> verify: 已有 README 的目录注册不覆盖、无 README 才生成
4. [ ] SKILL.md create 流程补「既有内容→从素材提议目标确认」-> verify: SKILL 含该步
5. [ ] 自测：临时空目录 / 临时含文件+README 目录，各 dry-run + apply -> verify: 文案区分、既有零覆盖
6. [ ] 清理临时目录 + verify-installation + py_compile -> verify: 绿、无残留
7. [ ] 记录 checkpoints/iterations.log -> verify: log 写入

## Risks & Mitigations
- 改 create 影响新建空项目主流程 -> 自测覆盖空目录场景，保证回归
- README 逻辑改动误删已有 README -> 只在缺失时生成，绝不覆盖；自测验证
- 越界改 SKILL.md -> write-exception 记录该唯一外部文件

## Iteration Budget
max_iterations: 14
