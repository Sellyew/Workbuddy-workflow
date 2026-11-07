# 上游同步维护手册

本仓库是 [`pedrohcgs/claude-code-my-workflow`](https://github.com/pedrohcgs/claude-code-my-workflow)
的**中文 / 腾讯 WorkBuddy 原生分支**。上游是一套面向 Claude Code 的科研工作流模板；
本仓库保留其方法论（规则、技能、代理、门禁、验证阶梯），运行载体采用 WorkBuddy 机制，
面向人的文字使用中文。上游方法、设计与原创内容的归属不变，引用信息见 `CITATION.cff`。

本手册规定同步契约：哪些文件可以直接覆盖，哪些必须人工合并，哪些由本仓库独立维护。

## 1. 远端配置

| 名字 | 指向 | 用途 |
|---|---|---|
| `origin` | 本仓库或其 fork | 日常提交与推送 |
| `upstream` | `pedrohcgs/claude-code-my-workflow` | 只读获取上游改进 |

首次配置：

```bash
git remote add upstream https://github.com/pedrohcgs/claude-code-my-workflow.git
git remote set-url --push upstream no_push
git remote -v
```

`upstream` 的 push URL 必须显示 `no_push`，避免误向上游推送。

## 2. 同步前检查

```bash
python scripts/sync-check.py
```

该命令除可选的 `git fetch upstream --tags` 外只读，完成四项检查：

1. 确认 `upstream` remote 存在并抓取标签；已有新鲜远端副本时可加 `--no-fetch`。
2. 列出上游领先的 commit 数及其触碰的文件。
3. 按第 4 节分类为「可直接覆盖 / 必须人工合并 / 本仓库独有」等类别。
4. 报告 `.claude/**`、`CLAUDE.md` 等**预期缺失**路径；它们不是同步故障，重新引入时不得合并。

退出码：`0` = 无必须人工合并的文件；`1` = 有必须人工合并或未分类的文件；`2` = 环境或网络问题。

## 3. 标准同步流程

```bash
python scripts/sync-check.py
git fetch upstream --tags
git log --oneline HEAD..upstream/main
git diff HEAD...upstream/main -- <path>
python scripts/backtest.py
python scripts/verify-count-gates.py
python scripts/normalize-model-tiers.py --dry-run
```

必须逐条阅读上游变更及其 diff，不能只凭 commit 标题决定合并方式。合并后归一化检查应报告
0 个待改文件；计数反证检查应让所有被植入的错误值被门禁捕获。

### `port-from-claude.py` 用法

机械移植脚本固定保留在 `scripts/port-from-claude.py`。它通过脚本位置解析仓库根目录，
不要移动该脚本。同步材料中存在 `.claude/` 源目录时，从仓库根目录运行：

```bash
python scripts/port-from-claude.py --dry-run   # 只报告，不写文件
python scripts/port-from-claude.py             # 执行机械移植
python scripts/port-from-claude.py --report    # 列出待人工处理的残留
```

脚本只从 `.claude/` 读取、只向 `.codebuddy/` 写入，不覆盖已有目标文件。它处理目录路径、
项目指令文件名、环境变量与解释器名称；模型路由、`/fork`、`Monitor` 和正文翻译仍需人工判断。
源目录不存在时脚本以 1 退出，已完成迁移且无新源文件时无需运行。

## 4. 文件分类契约

### 4.1 可直接覆盖

仅限本仓库没有本地实质改动的文件：

| 路径 | 理由 |
|---|---|
| `scripts/check-*.py` 中未被 4.2 点名的文件 | 判定逻辑与语言无关 |
| `scripts/quality_score.py` | 评分细则的单一真源 |
| `scripts/validate-findings.py`、`scripts/validate-setup.sh` | 无语言耦合 |
| `.codebuddy/references/finding-schema.json` | 机器 schema，不翻译 |
| `.codebuddy/skills/*/evals/cases/*.md` | 英文评测夹具，刻意保持英文 |
| `.github/workflows/**` | CI 定义 |

### 4.2 必须人工合并

| 路径 | 本地契约 | 合并重点 |
|---|---|---|
| `scripts/check-derived-counts.py` | 计数正则含中文分支；表面使用 `CODEBUDDY.md` | 上游新增或改写正则时同步补中文分支 |
| `scripts/check-surface-sync.py` | `SURFACES` 使用 `CODEBUDDY.md`；含中文复合断言 | 保留中文断言覆盖 |
| `scripts/check-skill-integrity.py` | 扫描根含 `CODEBUDDY.md`；允许中文字段 | 新检查须适用于中文正文 |
| `scripts/check-spec-conformance.py` | WorkBuddy 字段白名单与无对应语义提示 | 评估新增 Claude 专属字段的分类 |
| `scripts/check-staleness.py` | 无 POSIX `date` 依赖；规范化路径分隔符；含中文允许标记 | 新检查不得重新引入平台依赖 |
| `scripts/check-model-versions.sh` | 表面使用 `CODEBUDDY.md` | 保留平台入口 |
| `scripts/check-repo-hygiene.py` | 根目录白名单使用 `CODEBUDDY.md` | 维护附录不在根目录白名单中 |
| `.codebuddy/hooks/root-of-trust-guard.py` | 信任根包含 `.codebuddy` | 重新验证安全拒绝行为 |
| `.codebuddy/hooks/lib/hook-runner.sh` | 统一解释器探测、环境变量与 UTF-8 入口 | 本仓库独有，不覆盖 |
| `.codebuddy/settings.json` | 事件命令指向 `hook-runner.sh` | 逐条核对事件结构 |
| `.codebuddy/rules/model-routing.md` | 三档模型；代理与技能的 `effort` 语义不同 | 吸收路由思想，不照搬上游档位名 |
| `.codebuddy/rules/quality-gates.md` | 正文中文；rubric 区块与评分器一致 | 核对生成区块 |
| `README.md` / `guide/workflow-guide.qmd` | 中文正文与受门禁约束的计数断言 | 不新增未登记的计数站点 |

### 4.3 本仓库独有

| 路径 | 作用 |
|---|---|
| `CODEBUDDY.md` | WorkBuddy 项目指令入口 |
| `docs/translation-conventions.md` | 中文化与机器锚点契约 |
| `docs/maintenance/UPSTREAM.md` | 本维护手册 |
| `docs/starter-prompt.md` | 中文 Starter Prompt |
| `scripts/backtest.py` | 跨平台门禁编排器 |
| `scripts/check-hooks.py` | Windows 可运行的钩子行为回归集 |
| `scripts/normalize-model-tiers.py` | 归一化模型档位并按加载器契约处理 `effort` |
| `scripts/verify-count-gates.py` | 植入错误计数，反证门禁仍然有效 |
| `scripts/sync-check.py` | 上游同步分类检查 |
| `scripts/port-from-claude.py` | 可重复执行的机械移植工具 |
| `.codebuddy/skills/init-research-project/` | 项目初始化入口 |

### 4.4 预期缺失

| 上游路径 | 本仓库的处理 |
|---|---|
| `CLAUDE.md` | 不合并；本平台使用 `CODEBUDDY.md` |
| `.claude/**` | 不作为运行配置合并；配置根为 `.codebuddy/` |
| `scripts/hook-battery.sh` | 保留给 CI / macOS / Linux；Windows 使用 Python 回归集 |
| `scripts/check-hooks.sh` 等 `.sh` 门禁 | 保留跨平台入口；本地以对应 `.py` 检查为准 |

`sync-check.py` 将前两类标为 `EXPECTED-ABSENT`。它们被同步操作重新引入时应移除，不要合并成
第二套并行配置。

## 5. 持续维护约束

1. **模型档位不可照搬。** 本仓库使用 `default` / `lite` / `reasoning` 三档；`effort` 是代理
   frontmatter 的活字段，技能加载器不读它。路由事实见 `.codebuddy/rules/model-routing.md`。
2. **计数断言保持双语覆盖。** 英文识别分支不得删除；修改中文措辞时同步更新
   `check-derived-counts.py` 与 `check-surface-sync.py`。
3. **电池用例数由脚本计算。** 上游增加 `hook-battery.sh` 用例后，更新引用它的文档；
   `check-derived-counts.py` 会检查计数一致性。
4. **渲染产物本地重建。** 修改指南后运行 `quarto render`，将 HTML 同步到 `docs/`，再运行
   `python scripts/stamp-render.py`，最后由 `check-staleness.py` 核验。

## 6. 同步后验收

```bash
python scripts/backtest.py
python scripts/verify-count-gates.py
python scripts/normalize-model-tiers.py --dry-run
```

`backtest.py` 的 PASS 必须全绿，SKIPPED 必须能解释；计数反证必须全部被捕获；模型归一化
干跑必须报告 0 个待改文件。
