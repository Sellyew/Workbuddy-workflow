# Changelog

All notable current changes to this template are documented here. We follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and use loose semantic versioning: **major** when fork upgrades require manual migration, **minor** for new skills or features that are additive, **patch** for fixes and docs.

This public file keeps the current release and unreleased summary. Earlier release notes remain available in git tags and history.

---

## Unreleased — 公开模板与执行契约整理

### Changed

- 代理、技能、规则、模板、指南与入口文档统一为中文表达，保留配置字段、代码、模型档位、计数、锚点和实质限制。
- 按当前平台行为重校技能加载、权限、记忆、调度、钩子、无头评测与环境探测说明；未验证能力明确标注，不把静态检查写成运行时验证。
- 公开 MEMORY 只保留可迁移的通用经验；本机信息、个人裁定和单次事件留在本机或 git 历史。记忆晋升依据通用理由、适用边界和当前可复核证据。
- README 增加技能使用与维护入口；当前发布和升级说明集中在本文件，历史发布记录由 git tags/history 保存。

### Fixed

- 修正执行链路中的静默失效与假绿，包括钩子接线、子代理派发、字段白名单、编译与渲染、引文检查、内容不变量和派生计数。
- 强化独立核验、摘要一致性、双向资格认定、失败关闭与负例反证；缺少工具、空扫描或零匹配不再被当作通过。

---

## v3.0.1 — 2026-10-30（项目配置与文档对齐）

### Changed

- MCP 配置改用 WorkBuddy 的实际入口，并提供用户级、项目级 `mcpServers` 配置示例。
- 无头运行说明区分桌面客户端与 CodeBuddy Code CLI，给出独立配置目录和调用方式。
- 权限模式、会话续接、代理管理与版本查询说明统一为当前平台可用的操作入口。
- `run-skill-eval.sh` 支持 `EVAL_CLI`、`codebuddy`、`cbc`、`claude` 探测顺序，并兼容 Windows 的 Python 命令。
- 完善归属、上游引用、行为准则与仓库入口说明，保留原作者和许可证信息。

### Fixed

- 项目设置保留可用的 `permissions` 配置，指南同步说明 `allow` / `deny` 与钩子的实际行为。
- 修正 MCP、权限、续接、本地配置及规则目录中的失效命令和路径。
- 移除无效的 VS Code 扩展设置，受保护路径与当前 `.codebuddy` 配置保持一致。
- 权限说明改为桌面端提供的「默认权限」与「完全访问权限」两种模式。
- 计划位置统一为 `~/.workbuddy/plans/`，项目内留存计划需显式复制。
- 状态行说明不再承诺桌面端不会显示的信息，并提供可执行的替代查询方式。
- 修正夜间复现脚本中的平台名称，统一门禁说明、可移植性测试与资格台账。
- 钩子测试保持轻量：312 cases, seconds to run。

**Inventory at release: 63 skills, 19 agents, 37 rules, 11 hooks, 12 gates**

---

## Upgrading

若你 fork 了本模板并希望拉取后续更新，先提交或备份自己的改动，再配置一个中性远端占位：

```bash
git remote add template <TEMPLATE_REPOSITORY_URL>
git fetch template
git merge template/main           # 或按你的流程使用 git rebase template/main
```

`CODEBUDDY.md`、`.codebuddy/` 以及你定制的文档、模板和产物可能发生冲突。逐项审阅冲突，保留自己的项目设置，并有选择地采用基础设施改进；不要用整侧覆盖代替合并审查。

发布标签可通过 `git tag --list` 查看。需要固定到某个发布时使用 `git checkout <TAG>`；历史发布说明可通过 `git show <TAG>:CHANGELOG.md` 或 git history 阅读。
