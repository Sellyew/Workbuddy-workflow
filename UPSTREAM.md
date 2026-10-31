# 上游同步说明（UPSTREAM）

本仓库是 [`pedrohcgs/claude-code-my-workflow`](https://github.com/pedrohcgs/claude-code-my-workflow)
的**中文 / 腾讯 WorkBuddy 原生分支**。上游是一套面向 Claude Code 的科研工作流模板；
本仓库保留它的全部方法论（规则、技能、代理、门禁、验证阶梯），把运行载体换成本平台的机制，
并把面向人的文字译成中文。

**这个文件只有一个目的：让下一次同步上游时，你知道哪些文件能直接覆盖、哪些必须人工合并、
哪些是本仓库独有的。**

---

## 1. 三方关系

| 名字 | 是什么 | 你怎么用它 |
|---|---|---|
| `origin` | 本仓库（你的 fork） | 日常提交推这里 |
| `upstream` | `pedrohcgs/claude-code-my-workflow` | 只读：拉上游的改进 |

一次性接好（本仓库已配好则可跳过）：

```bash
git remote add upstream https://github.com/pedrohcgs/claude-code-my-workflow.git
git remote -v          # 应当看到 origin 与 upstream 两行
```

## 2. 同步前先体检

```bash
python scripts/sync-check.py
```

它做四件事，全部只读：

1. 确认 `upstream` remote 存在，并抓取（`git fetch upstream --tags`，可加 `--no-fetch` 跳过）；
2. 列出上游领先本仓库的 commit 数，以及这些 commit 触碰了哪些文件；
3. 把触碰到的文件按**下方第 4 节的分类**打上「可直接覆盖 / 必须人工合并 / 本仓库独有」标签；
4. 报告哪些上游文件在本仓库**已经不存在**（例如 `.claude/**`、`CLAUDE.md`）——这些是**预期缺失**，
   不是同步故障，但会被同步脚本反复重新引入，必须显式忽略。

退出码：`0` = 可以安全快进（无冲突文件）；`1` = 有必须人工合并的文件；`2` = 环境/网络问题。

## 3. 同步的标准动作

```bash
python scripts/sync-check.py            # 1. 看清会碰到什么
git fetch upstream --tags               # 2. 取上游
git log --oneline HEAD..upstream/main   # 3. 逐条读上游改了什么（不要只看标题）
python scripts/port-from-claude.py --dry-run   # 4. 预演路径/字段移植
python scripts/port-from-claude.py             # 5. 落地移植（可重复执行）
python scripts/backtest.py                     # 6. 门禁必须全绿
python scripts/verify-count-gates.py           # 7. 计数断言仍在把关
```

**第 3 步不能省。** 上游的 commit message 经常只写结论（「A reviewed submission stays unsendable
after redaction」），而真正要合并的是它改了哪几行判定。只看标题合并，会把上游修好的洞重新打开。

## 4. 文件分类（同步时按这张表决策）

### 4.1 可直接覆盖（上游改了就照抄，本仓库没有本地改动）

| 路径 | 为什么安全 |
|---|---|
| `scripts/check-*.py` 中**未被下面 4.2 点名**的 | 纯判定逻辑，与语言无关 |
| `scripts/quality_score.py` | 评分细则的单一真源；`quality-gates.md` 的表格由它生成 |
| `scripts/validate-findings.py`、`scripts/validate-setup.sh` | 无语言耦合 |
| `.codebuddy/references/finding-schema.json` | 机器 schema，不译 |
| `.codebuddy/skills/*/evals/cases/*.md` | 评测夹具（`## Prompt` / `## Assert`），**刻意保持英文** |
| `.github/workflows/**` | CI 定义 |

### 4.2 必须人工合并（本仓库有实质改动，覆盖会丢东西）

| 路径 | 本仓库改了什么 | 合并时看什么 |
|---|---|---|
| `scripts/check-derived-counts.py` | 每条计数正则加了中文分支；表面 `CLAUDE.md` → `CODEBUDDY.md` | 上游新增/改写的正则要**同时**补中文支，否则中文站点静默脱管 |
| `scripts/check-surface-sync.py` | `SURFACES` 换 `CODEBUDDY.md`；`COMPOUND_PHRASINGS` 加 4 条中文复合断言 | 同上 |
| `scripts/check-skill-integrity.py` | 扫描根加 `CODEBUDDY.md`；中文版 `description_zh` 等字段入白名单 | 上游若新增检查项，确认它对中文正文仍然有效 |
| `scripts/check-spec-conformance.py` | 增加 WorkBuddy 字段白名单（`description_zh` / `category` / `tags` / `version`）与「无对应语义」提示 | 上游若扩 `CC_ONLY`，评估是否该并入 `INERT_FIELDS` |
| `scripts/check-staleness.py` | 去掉 `date` 子进程依赖（Windows 无此命令）；路径分隔符规范化；超话断言的中文允许标记 | 上游若加新检查行，检查它是否又引入了 POSIX 依赖 |
| `scripts/check-model-versions.sh` | `CLAUDE.md` → `CODEBUDDY.md` | — |
| `.codebuddy/hooks/root-of-trust-guard.py` | 信任根从 `.claude` 扩到 `.codebuddy`（`CONFIG_DIR_NAMES`） | **这是安全机制**。上游若改判定结构，必须重新验证「改 `.codebuddy/` 会被拒」确实生效 |
| `.codebuddy/hooks/lib/hook-runner.sh` | 本仓库独有的统一入口（解释器探测 + 双环境变量 + UTF-8） | 上游没有这个文件 |
| `.codebuddy/settings.json` | 事件命令全部指向 `hook-runner.sh` | 上游改事件结构时要逐条对 |
| `.codebuddy/rules/model-routing.md` | 按本平台**三档**（`default`/`lite`/`reasoning`）重写；`effort` 段按本平台改写（代理生效、技能无效） | 上游改路由思想可以吸收，**档位名不能照搬** |
| `.codebuddy/rules/quality-gates.md` | 正文中文化，`<!-- BEGIN rubric -->` 区块**逐字节保留** | 区块必须仍然等于 `python scripts/quality_score.py --print-rubric` |
| `README.md` / `guide/workflow-guide.qmd` | 全文中文；计数断言按 `docs/translation-conventions.md` §4 | 上游的新卖点要译，且**不要新增计数站点** |

### 4.3 本仓库独有（上游没有，同步时不要被删）

| 路径 | 作用 |
|---|---|
| `CODEBUDDY.md` | 项目指令入口。**上游的 `CLAUDE.md` 在本仓库已删除**（本平台不读它） |
| `docs/translation-conventions.md` | 中文化契约：不译项、机器锚点、标准中文措辞、锚点重算规则 |
| `scripts/backtest.py` | 跨平台门禁编排器（上游只有 `backtest.sh`，需 POSIX bash） |
| `scripts/check-hooks.py` | 钩子行为回归集（25 条用例），替代无法在 Windows 上跑的 `hook-battery.sh` |
| `scripts/normalize-model-tiers.py` | 把 opus/sonnet/haiku 归一化到三档，并删除 `effort:` |
| `scripts/verify-count-gates.py` | 向 12 处中文计数断言植入错误值，反证门禁真的在把关 |
| `scripts/sync-check.py` | 本文件第 2 节那个体检工具 |
| `scripts/port-from-claude.py` | 可重复执行的移植工具（路径 / 字段 / 环境变量） |
| `docs/starter-prompt.md` | 中文 Starter Prompt |
| `.codebuddy/skills/init-research-project/` | `/init-research-project` 初始化入口 |
| `UPSTREAM.md` | 本文件 |

### 4.4 预期缺失（上游有、本仓库刻意没有）

| 上游路径 | 为什么不在这里 |
|---|---|
| `CLAUDE.md` | 本平台的指令文件是 `CODEBUDDY.md`；两个并存会产生互相矛盾的指令 |
| `.claude/**` | 本平台的配置根是 `.codebuddy/`，内容已全部移植（git 历史里仍可查到） |
| `scripts/hook-battery.sh` | 需要 POSIX bash；本环境用 `check-hooks.py` 覆盖关键子集，`.sh` 保留给 CI / macOS / Linux |
| `scripts/check-hooks.sh` 等 `.sh` 门禁 | 同上：保留，但本地以 `.py` 为准 |

**同步时如果这些文件被上游「重新引入」，直接删除，不要合并。** `sync-check.py` 会把它们标成
`EXPECTED-ABSENT`，不是错误。

## 5. 已知的上游依赖与本地偏差

1. **模型档位不可照搬。** 上游按 opus / sonnet / haiku / fable 四层 + `effort` 轴路由；
   本平台只有三档；`effort` 是代理 frontmatter 的活字段，技能加载器不读它。`model-routing.md` 已重写，`.codebuddy/agents/*.md` 的
   `model:` 已归一化（可由 `scripts/normalize-model-tiers.py` 幂等重跑）。
2. **计数断言是双语的。** 上游的英文措辞仍然被识别（英文分支永不删），中文分支按本仓库的措辞约定。
   改中文措辞必须同步改 `check-derived-counts.py` / `check-surface-sync.py`，否则该站点脱管。
3. **`hook-battery.sh` 的用例数（312）由上游维护。** 本仓库没有改动它，只在中文化文档里引用这个数。
   上游加用例后，本仓库的中文句子要跟着改 —— `check-derived-counts.py` 会变红提醒你。
4. **`.render-stamp` 是本地生成的。** 上游没有这个机制；同步后要重跑
   `quarto render` → 同步到 `docs/` → `python scripts/stamp-render.py`，否则 `check-staleness` 会报
   `STALE-RENDER`。

## 6. 同步之后必须跑的三条

```bash
python scripts/backtest.py           # 门禁全绿（PASS 全绿 / SKIPPED 要能解释为什么）
python scripts/verify-count-gates.py # 12/12 变红
python scripts/normalize-model-tiers.py --dry-run   # 应当 0 个文件需要改
```

第三条是防线：如果上游把 `model:` 写回了 `opus` 之类，`--dry-run` 会非零列出文件，
提醒你在提交前归一化，而不是等到运行时发现档位无效。
