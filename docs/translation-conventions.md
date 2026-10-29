# 中文化规范（Translation Conventions）

本文件是本仓库**全部中文文本的单一契约**。任何翻译本仓库文档的人或代理，动手前必须先读完本文件。
违反本文件的翻译即使「读起来更通顺」，也算缺陷——因为本仓库有一批**门禁脚本会读正文**，改写措辞会让门禁静默失去覆盖。

---

## 1. 总原则

1. **只译散文，不动机器。** 面向人的说明文字译成中文；面向机器的标识符、路径、命令、配置字段、正则、代码原样保留。
2. **一对一。** 不增删内容，不合并段落，不「顺手改进」，不补充原文没有的例子或结论。条目数、表格行数、编号必须与原文一致。
3. **术语统一。** 见 §5 术语表；首次出现可写「中文（English）」，其后只用中文。
4. **标题可译，但受 §3 机器锚点约束。** 译了标题就必须同步修正指向它的锚点链接（见 §7）。

---

## 2. 不翻译（原样保留，逐字节不动）

| 类别 | 例子 |
|---|---|
| YAML frontmatter 的键名 | `name:` `description:` `paths:` `tools:` `model:` `allowed-tools:` `argument-hint:` `alwaysApply:` `enabled:` `category:` `tags:` |
| YAML 中的机器值 | `model: lite`、`paths: - "Slides/**/*.tex"`、`allowed-tools: ["Read","Bash"]`、`name: deploy` |
| 代码块 | ` ```bash ` / ` ```yaml ` / ` ```python ` / ` ```latex ` 围栏内的**全部**内容，含注释 |
| 行内代码 | 所有 `` `...` `` 内的内容 |
| 路径与文件名 | `.codebuddy/rules/quality-gates.md`、`scripts/backtest.py`、`Preambles/header.tex` |
| 命令与参数 | `git commit`、`quarto render`、`xelatex -interaction=nonstopmode`、`--peer`、`--adversarial` |
| 技能 / 代理 / 钩子 / 脚本名 | `/review-paper`、`claim-verifier`、`git-guardrails.py`、`hook-runner.sh` |
| 字段名与枚举值 | `RUN_CONFIG`、`subagent_type`、`verdict: "confirmed"`、`mechanical: true` |
| 判定词（保留大写英文） | `PASS` / `REVISE` / `BLOCK` / `CRITICAL` / `MAJOR` / `MINOR` / `FINDING` / `SCORECARD` / `NEEDS-HUMAN` / `JUDGE-HALLUCINATED` |
| 工具名 | `Read` `Write` `Edit` `MultiEdit` `Bash` `Grep` `Glob` `Agent` `Task` `Skill` |
| 模型层名 | `Opus` `Sonnet` `Haiku` `Fable`（层名保留；本平台映射见 `.codebuddy/rules/model-routing.md`） |
| 外部专有名词 | GitHub、Quarto、Beamer、TikZ、LaTeX、XeLaTeX、RevealJS、Stata、CRAN、DOI、BibTeX |
| URL、DOI、引文条目 | 全部原样 |
| HTML 注释标记 | `<!-- ... -->` 内的**标记本身**；标记内的说明文字可译，但 `<!-- BEGIN rubric` / `<!-- END rubric` / `<!-- CURRENT:` / `<!-- model-allow -->` 这些**关键字不得改动** |
| Markdown 结构 | 表格分隔行 `|---|`、列表符号、引用符号 `>`、围栏 |

---

## 3. 机器锚点（结构标识，**必须保持英文原样**）

以下串被 `scripts/` 下的门禁脚本用正则抓取。译了它们，对应门禁会「匹配不到 → 判定为未覆盖 → 变红」，或更糟：静默失去覆盖。

| 锚点 | 位置 | 抓取者 | 必须保持的样子 |
|---|---|---|---|
| `## Phase N` | `.codebuddy/skills/translate-to-quarto/SKILL.md` | `check-derived-counts.py: n_translate_phases()` | 标题以 `Phase ` + 数字开头，如 `## Phase 1 — …` |
| `## Pattern N` | `guide/workflow-guide.qmd` | `check-derived-counts.py: n_patterns()` | 标题以 `Pattern ` + 数字开头，如 `## Pattern 7 — …` |
| `## Econ Top-5` | `.codebuddy/references/journal-profiles.md` | `n_econ_journals()` | 该二级标题**整行英文原样**（其下 `### ` 子标题数量即画像数） |
| `## Rung N — …` | `.codebuddy/references/verification-ladder.md` | `n_rungs()` | 每个阶梯标题以 `## Rung ` 开头，如 `## Rung 0 — Qualify the checker` |
| `**N. 标题。**` | `.codebuddy/references/research-agent-laws.md` | `n_laws()` | 每条法则段落以 `**数字.` 开头，**数字与点不可省**，如 `**1. …**` |
| `<!-- BEGIN rubric … -->` … `<!-- END rubric -->` | `.codebuddy/rules/quality-gates.md` | `rubric_parity()` | 标记之间的表格是 `scripts/quality_score.py --print-rubric` 的**生成物**，必须逐字节保留英文，**禁止翻译、禁止重排、禁止加空行** |
| `<!-- CURRENT: … -->` | `.codebuddy/references/model-versions.md` | `check-model-versions.sh` | 整行原样 |
| `\| N \|` 行首数字 | `.codebuddy/skills/seven-pass-review/SKILL.md` | `n_seven_pass()` | 七遍审读的表格每行以 `\| 数字 \|` 开头 |
| `\| `--flag` \| …` | 各 `SKILL.md` | `check-skill-integrity.py` | 参数说明表格每行首格必须是 `` `--flag` ``（见 §6） |

---

## 4. 受门禁约束的可计数断言：**标准中文措辞**

这些句子陈述「本模板有多少个 X」，被抓取后与磁盘实际数量比对。中文措辞必须**逐字**使用下表右列，否则该处脱离覆盖、门禁变红。

| 语义 | 必须写成（`N` 为阿拉伯数字） | 说明 |
|---|---|---|
| 门禁数量 | `N 个门禁` | 指 `scripts/backtest.sh` 的检查器数量 |
| 翻译阶段数 | `N 个翻译阶段` | `translate-to-quarto` 的阶段总数 |
| 期刊画像数 | `Top-5 期刊画像` | 数字紧跟 `Top-`，不要写「五大」 |
| 法则条数 | `N 条法则` | 指 `research-agent-laws.md` |
| 阶梯级数 | `N 级阶梯` | 指 `verification-ladder.md` 的 Rung 数 |
| 七遍审读的透镜数 | `N 个独立上下文子代理` | 必须是「独立上下文」四字连写 |
| 钩子测试用例数 | `N 个用例，秒级运行` | 逗号用中文全角；「秒级运行」四字连写；用于 CHANGELOG 当期段落与指南 |
| 工作流模式数 | `N 个模式构成参考书架` | 用于指南与落地页 |
| TikZ 片段数 | `N 个开箱即用的 TikZ 片段` | 用于指南 |
| 清单复合句 | `本模板 N 个代理、N 个技能、N 条规则、N 个钩子` | 四项齐全、顺序不变、用顿号分隔 |

清单复合句另有一个合法简写：`N 个技能、N 个专用代理、N 条规则`（落地页 og:description 用）。

> 若某处自然中文难以套用上表措辞，**保留原英文句子**并在报告里说明——宁可一处英文，不要一处脱管。

---

## 5. 术语表

| English | 中文 | 备注 |
|---|---|---|
| skill | 技能 | 指 `.codebuddy/skills/*/SKILL.md`；`/foo` 形式的调用名不译 |
| agent / subagent | 代理 / 子代理 | subagent 亦作「子代理」 |
| rule | 规则 | |
| hook | 钩子 | |
| gate / checker | 门禁 / 检查器 | |
| backtest | 门禁总检 | 指 `scripts/backtest.sh` 整套 |
| quality gate | 质量门禁 | |
| plan mode | 计划模式 | |
| fresh context | 独立上下文 | |
| fan-out | 扇出 | |
| reduce | 归并 | |
| loop-until-dry | 空轮收敛 | |
| dry round | 空轮 | 零新增 CRITICAL/MAJOR 的一轮 |
| ledger | 台账 | 指 `quality_reports/qualification/LEDGER.md` |
| provenance | 溯源 | |
| reproducibility | 可复现性 | |
| replication package | 复现包 | |
| preregistration | 预注册 | |
| estimand | 估计目标 | |
| identification | 识别策略 | |
| robustness | 稳健性 | |
| Monte Carlo | 蒙特卡洛 | |
| coverage | 覆盖率 | 统计语境 |
| oracle | 外部裁判 | 指 external oracle |
| referee | 审稿人 | |
| disposition | 审稿取向 | |
| adversarial | 对抗式 | |
| rubric | 评分细则 | |
| findings | 审查发现 | 单条为「发现」 |
| checkpoint | 检查点 | |
| handoff | 交接 | |
| scratch | 草稿区 | |
| placeholder | 占位符 | |
| single source of truth | 单一真源 | |
| root of trust | 信任根 | |
| guardrail | 防线 | |
| pre-flight | 起飞前检查 | |

---

## 6. 技能与代理 frontmatter 细则

### 6.1 `description`

- **译成中文。** 描述里引号内的英文触发词**原样保留**，例如：
  `description: 把 Quarto \`.qmd\` 幻灯片渲染为 HTML 并同步到 \`docs/\`。用户说 "deploy"、"publish the slides"、"推上线" 时使用。`
- 长度上限 1024 字符（`check-spec-conformance.py` 强制）。
- 可另加 `description_zh:`，内容与中文 `description` 一致；不加也合规。

### 6.2 `name`

**永不翻译。** 必须与目录名一致（`NAME_RE` 只接受 `[a-z0-9-]`）。

### 6.3 参数说明的写法（`check-skill-integrity.py` 会校验）

参数必须出现在**首格为代码跨度的表格行**，或**以代码跨度开头的列表项**：

```markdown
| 参数 | 作用 |
|---|---|
| `--peer` | 启用同行评审流程 |

- `--adversarial` 开启对抗式审读
```

不要只在散文里提参数（「也可以用 --peer 参数」）——中文散文里的参数不算已记录，门禁会报 `argument-hint advertises … never mentions`。

### 6.4 `allowed-tools`

原样保留，不译、不增删。

### 6.5 代理 frontmatter

`name` / `tools` / `model` 原样；`model` 只能是 `default` / `lite` / `reasoning`（本平台三档）。`description` 译成中文。

---

## 7. 锚点链接

若翻译了被 `[…](file.md#anchor)` 指向的标题：

1. 按 GitHub 规则重算锚点：转小写 → 去标点（保留 `\w`、空格、连字符；中文属 `\w`）→ 空格变 `-`。
   例：`## 技能总表` → `#技能总表`；`## Phase 1 — 起飞` → `#phase-1--起飞`。
2. 用新锚点改写**所有**指向它的链接（含其他目录里的文件）。
3. 本文件 §3 的机器锚点标题若被链接指向，链接里的锚点仍按**翻译后**的标题计算，但标题里被锚定的英文串不动。

`scripts/check-skill-integrity.py` 的 anchor resolution 检查会验证这些链接。

---

## 8. 交付自检（每次翻译完必须做）

```bash
python scripts/check-spec-conformance.py      # frontmatter 合规
python scripts/check-skill-integrity.py       # 参数/工具/锚点一致性
python scripts/check-links.py                 # 链接与引用
python scripts/check-derived-counts.py        # 可计数断言
```

四条全绿才算译完。任一条变红，先怀疑自己的措辞偏离了 §3/§4，再怀疑脚本。
