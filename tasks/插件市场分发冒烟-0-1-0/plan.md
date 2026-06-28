# Plan: 插件市场分发冒烟 0.1.0
Task: PLA-009 | Project: plan-manager
Plan Status: done | Created: 2026-06-29 | Updated: 2026-06-29

## Goal
验证从干净环境安装 plan-manager 0.1.0 后「首次即用、首次不崩」：install.sh 两种模式可用、verify 通过、面板与 config 在全新副本上正常运行。

## Success Criteria (COMPLETION PROMISE)
- [x] install.sh copy 模式安装到临时目标成功，verify-installation 通过
- [x] install.sh symlink 模式安装到临时目标成功，verify-installation 通过
- [x] 全新副本（copy）上跑 help/overview/config/panels 面板：exit 0、非空、不崩
- [x] 全新副本脚本不依赖源码绝对路径（__file__ 解析正确，无硬编码 /home 路径泄漏到行为）
- [x] plugin.json（claude + codex）version=0.1.0 且结构合法 JSON
- [x] install.sh 自带 verify 步骤运行通过；--force 重装逻辑可用
- [x] 临时目标安装完成后清理，不污染真实 ~/.claude 安装

## Approach (AI DETERMINES)
用临时目录作安装目标（不碰真实 ~/.claude/skills/plan-manager symlink）。直接调用脚本逻辑：copy 模式 = 复制 skills/plan-manager 到 tmp，跑 verify-installation --target tmp + 面板冒烟；symlink 模式 = 在 tmp 建 symlink 指向源并 verify。校验 plugin.json JSON 合法性与版本。全程在 scratchpad 临时目录，结束清理。

## Steps (AI EXECUTES)
1. [x] 建临时目标目录（scratchpad），copy skills/plan-manager 过去 -> verify: 目录存在、文件齐
2. [x] verify-installation.sh --target <tmp-copy> -> verify: ok
3. [x] 全新副本跑 help/overview/config/panels -> verify: 各 exit 0、非空
4. [x] 检查副本脚本 __file__ 解析（help-panel 脚本目录行指向副本而非源）-> verify: 路径=副本
5. [x] symlink 模式：tmp symlink -> 源，verify-installation --target <tmp-link> -> verify: ok
6. [x] plugin.json claude+codex：python json.load 合法 + version==0.1.0 -> verify: 双 ok
7. [x] 跑真实 install.sh 的 verify 段（--target 现有安装）+ 确认 --force 分支存在 -> verify: ok
8. [x] 清理所有临时目标 -> verify: scratchpad 无残留；真实安装未动
9. [x] 记录到 checkpoints/iterations.log + 列改动/产出 -> verify: log 写入

## Risks & Mitigations
- 误改真实 ~/.claude 安装 -> 全部用 scratchpad 临时目标，绝不写 ~/.claude/skills
- copy 副本路径依赖导致面板崩 -> 正是要测的点；若崩则定位硬编码并修脚本（记 write-exception）
- install.sh 对固定 TARGET_BASE 假设 -> 不跑会改真实环境的安装路径，只复用其 verify 逻辑/手动模拟

## Iteration Budget
max_iterations: 12
