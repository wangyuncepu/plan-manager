# Plan: README 产品化重写 0.1.0
Task: PLA-010 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
把 README 重写为面向插件市场的产品落地页：开发者扫一眼就懂「是什么、解决什么、怎么用」，并准确反映 0.1.0 的对话式 UX + dual-role + 面板中心。

## Success Criteria (COMPLETION PROMISE)
- [x] 顶部有清晰一句话价值主张 + 3-5 条核心卖点（对话式、dual-role、面板中心、脚本化安全写入、跨项目编排）
- [x] 新增「How you use it」段：用户说意图、AI 跑脚本，给 2-3 个对话示例（非 CLI 教程）
- [x] 新增 dual-role 简介（strategist 规划 / executor 执行 + 一键切换）
- [x] 新增面板简介（fixed/saved/temp，列主要 fixed 面板）
- [x] 保留并复用现有安装章节（Claude/Codex/Copilot，三种方式不丢）
- [x] 与 0.1.0 一致：无过时版本号、无 PLS-/PlanSkill、面板数/概念与实际相符
- [x] 链接到 references/manual 等既有文档，不重复正文
- [x] Markdown 结构清晰，标题层级合理

## Approach (AI DETERMINES)
保留 README 的 Install / Directory structure 等仍有效章节，重写顶部定位 + 插入产品化新段（价值主张、How you use it、dual-role、panels、quick start 对话示例）。以 SKILL.md INTERACTION MODEL/面板清单为事实源，确保描述与脚本行为一致。只动 README.md（write-exception）。

## Steps (AI EXECUTES)
1. [x] 读全 README + SKILL.md 关键段，列保留/重写/新增清单 -> verify: 清单覆盖全部 success criteria
2. [x] 重写顶部：价值主张 + 卖点列表 -> verify: 含 ≥3 卖点、含对话式与 dual-role
3. [x] 插入「How you use it」对话示例段 -> verify: ≥2 自然语言示例、无要求用户敲 CLI
4. [x] 插入 dual-role + 面板简介段 -> verify: 两角色 + fixed/saved/temp 三类齐
5. [x] 校验保留安装章节完整（Claude/Codex/Copilot ×plugin/manual）-> verify: 章节数不减
6. [x] 一致性扫描：无 4.x/3.x、无 PLS-/PlanSkill、面板概念对齐 -> verify: grep 干净
7. [x] 通读结构 + 链接有效性 -> verify: 标题层级合理、引用文件存在
8. [x] 记录到 checkpoints/iterations.log + 列改动 -> verify: log 写入

## Risks & Mitigations
- 重写丢失现有有效内容（安装步骤）-> 步骤 5 强制校验安装章节完整
- 文案与实际行为漂移 -> 以 SKILL.md 为事实源核对
- 改动越界（只应动 README）-> write-exception: README.md 仅此一文件

## Iteration Budget
max_iterations: 12
