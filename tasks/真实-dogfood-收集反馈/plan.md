# Plan: 真实 dogfood 收集反馈
Task: PLA-015 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
以受控真跑方式，用 plan-manager 真实管理 YeBoZhai（未注册的真实 IP 战略项目），完整走一遍闭环并系统记录交互成本/摩擦点/缺陷，产出反馈报告驱动后续（兑现「反馈>功能」）。执行产出隔离在新任务目录，绝不改 YeBoZhai 既有内容。

## Success Criteria (COMPLETION PROMISE)
- [x] 预载 YeBoZhai 会话上下文（6天前/13条）作为真实背景
- [x] 真实走通：注册 YeBoZhai（含目标澄清）→ 设目标 → 建 1 个真实小任务 → 起草计划 → 审批 → 执行 → 完成
- [x] 执行产出仅落新任务自己的目录；YeBoZhai 既有文件（档案/介绍/公众号）零改动
- [x] 全程记录每阶段交互轮数 + 卡点 + AI 误解/意外行为
- [x] ≥5 条具体摩擦点，分「真bug」vs「体验粗糙」，各带场景+影响+建议+优先级
- [x] 产出 feedback-report.md（本任务目录），含 Top3 改进
- [x] 终态校验：YeBoZhai 既有内容 git 无改动；新增仅 .project + 新任务目录（受控、可回滚）

## Approach (AI DETERMINES)
YeBoZhai 已有 IP 战略真实素材但未注册 → 注册环节本身就是真测（含 office-hours/autoplan 目标澄清的真实体验）。以普通用户视角、只用自然语言驱动；建的真实小任务选「读现有素材产出一份小摘要/索引」之类只读输入、产出落任务目录的活，确保不动既有文件。用 git status 守护 YeBoZhai 既有内容零改动。观察归类(交互成本/正确性/稳健/文档)写 feedback-report.md。

## Steps (AI EXECUTES)
1. [x] 预载 YeBoZhai 会话 digest + 记录既有文件清单基线（git 状态快照）-> verify: 基线写入反馈日志
2. [x] 注册 YeBoZhai（project create + 目标澄清），记录此环节交互成本 -> verify: .project 生成、目标已设
3. [x] 建 1 个真实小任务（读既有素材→产出摘要/索引到任务目录）-> verify: 任务+目录创建
4. [x] 起草计划→审批→执行该任务，产出落任务目录 -> verify: 产出文件在任务目录、任务 completed
5. [x] 逐阶段记交互轮数/卡点/误解 -> verify: 反馈日志每阶段有条目
6. [x] 归类 ≥5 摩擦点(bug vs 体验, 场景+影响+建议+优先级)-> verify: ≥5 条、分类齐
7. [x] 写 feedback-report.md(含 Top3)-> verify: 报告存在且含 Top3
8. [x] 终态守护：git status 确认 YeBoZhai 既有文件零改动 -> verify: 既有文件无 modified；新增仅 .project + 新任务目录
9. [x] 记录 checkpoints/iterations.log -> verify: log 写入

## Risks & Mitigations
- 改到 YeBoZhai 既有素材 -> 真实小任务设计为只读输入、产出仅落任务目录；步骤 8 git 守护
- 注册引入不可回滚改动 -> 仅新增 .project + 任务目录，均可删除回滚
- 反馈空泛 -> 每条强制 场景+影响+建议+优先级
- 范围发散 -> 只跑一遍闭环 + 一个小任务，目标是反馈非产能

## Iteration Budget
max_iterations: 16
