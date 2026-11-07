# 技能创建模板

**用这个模板为你的学术工作流创建领域专用的技能。**

---

## 先选创建方式与存放位置

`.codebuddy/skills/` 是 WorkBuddy 官方支持的项目技能目录，技能随仓库共享，项目级优先于用户级；用户技能库用于跨项目复用。

- 本仓库的 `/new-skill` 是项目技能，按本仓库约定生成项目技能。WorkBuddy 内置的 `/skill-creator` 才是通用创建器，GUI 入口是**技能 → 添加技能 → 创建技能**。
- 市场安装、上传，以及通用创建器创建的技能，默认进入用户技能库，不会自动进入当前项目。要随仓库共享，必须显式把技能放到 `.codebuddy/skills/<name>/SKILL.md`。
- 界面或菜单不显示某项，不等于引擎没有发现它，也不等于不能用 `/name` 显式调用。
- 技能元数据用于匹配，正文在触发时加载，附属材料按需读取；不要把它理解成每轮从磁盘读取所有描述。

---

## 什么时候该自建技能

当你发现自己出现下面这些情况时，就该建一个技能：

- 反复向 WorkBuddy 解释同一套 3 步以上的工作流
- 需要领域专用的质量检查（引用格式、记号一致性、实验室规程）
- 要强制领域专用的输出格式（学位论文结构、期刊模板、实验记录本）
- 要协调多工具工作流（Figma → R → LaTeX、数据 → 分析 → 稿件）

**以下情形不要建技能：**

- 一次性任务
- 变动频繁的工作流
- 简单的 1-2 步操作

---

## 模板结构

把下面的结构复制到 `.codebuddy/skills/[your-skill-name]/SKILL.md`：

```markdown
---
name: your-skill-name
description: [What it does] + [When to use it] + [Key capabilities]. Use when user asks for "[trigger phrase 1]", "[trigger phrase 2]", or "[context]".
description_zh: [与 description 同义的中文；引号内的英文触发词原样保留]
argument-hint: "[brief hint for user]"
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Agent"]
version: "0.1.0"
category: [所属类别]
tags: [标签]
---

# [Skill Name]

[One sentence: what this skill accomplishes and why it exists]

## Instructions

Step 1: [First major action with clear explanation]
   - Detail: [Important consideration]
   - Example: [Concrete example]

Step 2: [Second major action]
   - Detail: [Important consideration]

Step 3: [Final action and verification]
   - Verify: [What to check]
   - Output: [What user receives]

## Examples

### Example 1: [Common Scenario Name]
**Context:** [When this occurs]
**User says:** "[Typical user request]"
**Actions:**
1. [What skill does first]
2. [What skill does second]
3. [Final output]
**Result:** [What user receives]

### Example 2: [Another Common Scenario]
**Context:** [Different situation]
**User says:** "[Alternative phrasing]"
**Actions:**
1. [Different path through the skill]
**Result:** [Expected outcome]

## Troubleshooting

**Error:** [Common error message or symptom]
**Cause:** [Why this happens]
**Solution:** [How to fix it]

**Error:** [Another common issue]
**Cause:** [Root cause]
**Solution:** [Fix steps]
```

---

## 字段参考（单一真源）

技能 frontmatter 的字段语义——会读 / 写了不生效 / 被读但有害——完整清单在
[`.codebuddy/references/skill-fields.md`](../.codebuddy/references/skill-fields.md)，
由门禁 `check-field-docs.py` 校验、与本模板保持一致。写新技能前先看那一份；这里只列最易记错的：

- **必填**：`name`（小写连字符、与目录名一致）、`description`（≤1024 字符，决定何时自动加载）。
- **会读**：`allowed-tools`、`argument-hint`、`model`（`default`/`lite`/`reasoning`）、`agent`、`disable-model-invocation`、`user-invocable`、`description_zh`/`description_en`、`category`、`tags`、`version`。
- **别写**（写了不生效）：`disallowed-tools`、`paths`、`hooks`、`when_to_use`、`arguments`、`effort`、`background`、`shell`；`context: fork` 有害（失去 `Agent`）。

### `allowed-tools` 是工具白名单 {#allowed-tools}

**官方语义是白名单 / 限制。** [WorkBuddy 开放平台](https://open.workbuddy.cn/docs/skill)把它定义为「工具白名单（逗号分隔）」，[CodeBuddy Code CLI 文档](https://www.workbuddy.ai/docs/cli/skills)写明 “Allowlist of permitted tools” 与 “Restrict which tools a Skill can use”。因此，只把技能允许使用的工具列入 `allowed-tools`；未列出的工具不在该技能的白名单内。当前没有桌面端相反行为的 L3 证据；若某版本实测不同，必须单列客户端版本、最小探针与实际输出，不能改写官方默认语义。

`disallowed-tools` 在这里无对应语义，写了不生效；不要用黑名单思路，直接收窄 `allowed-tools` 白名单。要让一个技能「只读」，使用两层约束：

1. `allowed-tools` 只列只读工具（`Read`/`Grep`/`Glob`），利用白名单排除写入工具；
2. 在正文里写一句明确的只读约束：「本技能不修改被审文件；如需写报告，只写到 `quality_reports/` 下」。

这两层降低误写风险，但**不是绝对安全保证**：仍须核验模型实际调用、项目 `permissions.allow` / `permissions.deny` 与 PreToolUse 钩子；高风险写入保护应再加拒绝规则或钩子（见 `permission-check`）。

**动态内容**——已实测的字符串替换与尚未实测的命令注入：

- `$ARGUMENTS` —— 完整参数字符串（例如 `/skill-name Lecture01` → `Lecture01`）【已实测生效】
- `` !`git log --oneline -5` `` —— 该语法是否在技能加载时执行并注入输出尚未实测，不得断言命令必然运行。确需使用时，先用无副作用命令做探针，记录客户端与技能版本及实际结果，再据此决定是否采用。

上游的 `${CLAUDE_SKILL_DIR}` 和 `$0`/`$1` 位置参数在 WorkBuddy 里没有对应物，别用。

细节与示例见[指南的技能 frontmatter 参考](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#skill-frontmatter)。

### 什么时候该设 `disable-model-invocation: true` {#when-to-disable-model-invocation}

凡是技能会写入**持久的、承重的文件**、而用户必须明确意图才能创建这类文件时，就设这个旗标。否则，WorkBuddy 可能在一条含糊匹配的提示词下自动触发该技能，产出一个不做手工清理就很难撤销的文件。

**以下技能要设：**

- 创建新的持久源文件（`/create-lecture` → 新的 `.tex`，`/new-diagram` → 新的 TikZ 源）。
- 写入会自我修改的产物（`/learn` → 新的 SKILL.md，`/checkpoint` → 状态快照，`/preregister` → 预注册文档）。
- 跑长时间的写文件循环（`/simulation-study` → 带种子的蒙特卡洛运行与结果，`/vaccinate` → 资格台账的一行，`/deep-audit` → 审计并修复的循环）。

**以下技能不要设：**

- 产出临时分析输出（`/proofread`、`/review-r`、`/visual-audit`——写在 `quality_reports/` 下，容易删）。
- 是只读诊断（`/permission-check`、`/context-status`）。
- 从既有源码编译 / 渲染 / 部署（`/compile-latex`、`/deploy`、`/extract-tikz`）。

这个旗标仍然允许用 `/skill-name` 直接调用——它只挡住模型凭启发式匹配自动触发。

### `@import` 是上游 Claude Code 的 CLAUDE.md 特性，WorkBuddy 不读

上游 Claude Code 的 `CLAUDE.md` 支持 `@path/to/import` 引入额外文件；**WorkBuddy 的 `CODEBUDDY.md` 不读 `@import`**。要拆分指令文件，用普通 markdown 链接（如 `CODEBUDDY.md` 里写 `[MEMORY.md](MEMORY.md)`），不要用 `@` 导入。

本模板的 `CODEBUDDY.md` 刻意保持精简，不拆分指令文件——forker 期待的是「会话启动时加载一个文件」，拆碎反而把入门上下文打散。

---

## 写出有效的描述

`description` 等元数据用于匹配你的技能；匹配并触发后才加载正文，附属材料再按需读取。用这个结构写描述：

```
[What it does] + [When to use it] + [Key capabilities]
```

### 好的示例（领域专用）

**引用格式强制（APA 心理学）：**

```yaml
description: Enforces APA 7th edition citation format in manuscripts. Use when user asks to "check citations", "fix references", "apply APA style", or when reviewing .tex or .qmd files with bibliography. Checks author-year format, DOI formatting, and reference list completeness.
```

**实验记录本条目生成（湿实验室生物学）：**

```yaml
description: Generates structured lab notebook entries from experimental notes. Use when user provides "experiment notes", "protocol results", or asks to "format lab entry". Ensures date, hypothesis, materials, procedure, observations, and conclusions are documented.
```

**学位论文章节结构检查（研究生）：**

```yaml
description: Validates thesis chapter structure against institutional requirements. Use when user asks to "check chapter format", "validate thesis structure", or when editing thesis .tex or .docx files. Verifies required sections, heading levels, and citation density.
```

**计量设定审读（经济学）：**

```yaml
description: Reviews econometric specifications for common errors. Use when user shares regression code in R or Stata, or asks to "check model spec", "review estimation". Validates: standard error clustering, fixed effects structure, missing covariates, and replication commands.
```

### 坏的示例（太泛）

❌ `description: Helps with citations`  
→ 太含糊，没说明风格，也没说明何时触发

❌ `description: Checks lab notebooks`  
→ 缺触发短语，没有格式说明

❌ `description: Reviews thesis chapters`  
→ 没说清查哪些方面，也没说何时激活

---

## 学术领域的示例

### 示例 1：引用交叉核对器

**文件：** `.codebuddy/skills/validate-citations/SKILL.md`

```markdown
---
name: validate-citations
description: Cross-references in-text citations against bibliography entries. Use when user asks to "check citations", "validate references", or when working on .tex, .qmd, or .md files with bibliographies. Identifies missing entries, unused references, and formatting inconsistencies.
description_zh: 交叉核对正文引文与文献库条目。用户说 "check citations"、"validate references" 时，或处理带文献库的 .tex/.qmd/.md 文件时使用。
argument-hint: "[file or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write"]
---

# Validate Citations

Ensures all in-text citations have corresponding bibliography entries and identifies unused references.

## Instructions

Step 1: **Extract in-text citations**
   - Use Grep to find citation commands: `\cite{...}`, `\citep{...}`, `[@...]`
   - Build list of cited keys

Step 2: **Parse bibliography file**
   - Read Bibliography_base.bib (or specified .bib file)
   - Extract all `@article{key,`, `@book{key,` entries

Step 3: **Cross-reference**
   - Missing in bib: citations without entries
   - Unused in bib: entries never cited

Step 4: **Report findings**
   - Save to `quality_reports/citation_validation.md`
   - List missing entries (CRITICAL)
   - List unused entries (for cleanup)
   - Check DOI formatting if present

## Examples

### Example 1: Manuscript with Missing Citation
**User says:** "Check if all my citations are in the bib file"
**Actions:**
1. Grep for `\citep{` in manuscript.tex
2. Extract keys: `Smith2020`, `Jones2019`, `Lee2021`
3. Parse Bibliography_base.bib
4. Find `Lee2021` missing
**Result:** Report: "Missing entry: Lee2021. Add to bibliography before submission."

## Troubleshooting

**Error:** Citation format not recognized
**Cause:** Non-standard citation command
**Solution:** Add pattern to Step 1 grep (e.g., `\citeauthor`, `\citeyear`)
```

---

### 示例 2：回归输出排版器

**文件：** `.codebuddy/skills/format-regression-tables/SKILL.md`

````markdown
---
name: format-regression-tables
description: Converts R regression outputs to publication-ready LaTeX tables. Use when user runs regressions and says "make a table", "format results", or "export to LaTeX". Handles lm, glm, felm, and fixest objects. Applies field-specific conventions (standard errors in parentheses, stars for significance).
description_zh: 把 R 回归输出转成可发表的 LaTeX 表格。用户跑完回归说 "make a table"、"format results"、"export to LaTeX" 时使用。
argument-hint: "[model object name]"
allowed-tools: ["Read", "Write", "Bash"]
---

# Format Regression Tables

Converts R regression objects into publication-ready LaTeX tables with proper formatting.

## Instructions

Step 1: **Identify model objects**
   - User provides R object names (e.g., `model1`, `model2`)
   - Read corresponding .rds files from output/

Step 2: **Extract coefficients and statistics**
   - Coefficient estimates
   - Standard errors (in parentheses)
   - Significance stars: * p<0.10, ** p<0.05, *** p<0.01
   - R-squared, N observations

Step 3: **Generate LaTeX table**
   - Use booktabs style (no vertical lines)
   - Align on decimal points
   - Add notes for standard errors and significance

Step 4: **Save and verify**
   - Save to `output/tables/regression_results.tex`
   - Verify compiles in standalone .tex document

## Examples

### Example 1: Panel Regression with Fixed Effects
**User says:** "Format my regression results for the paper"
**Context:** User has run `felm(y ~ x | firm + year | 0 | firm, data=df)`
**Actions:**
1. Read saved model object
2. Extract: coefficients, clustered SEs, R², N
3. Generate LaTeX:
   ```latex
   \begin{table}[htbp]
   \caption{Effect of X on Y}
   \begin{tabular}{lc}
   \toprule
   & (1) \\
   \midrule
   X & 0.523*** \\
     & (0.089) \\
   \midrule
   Firm FE & Yes \\
   Year FE & Yes \\
   \midrule
   Observations & 1,234 \\
   R-squared & 0.678 \\
   \bottomrule
   \multicolumn{2}{l}{\footnotesize Clustered SEs in parentheses.} \\
   \multicolumn{2}{l}{\footnotesize * p<0.10, ** p<0.05, *** p<0.01}
   \end{tabular}
   \end{table}
   ```
**Result:** Ready to `\input` in manuscript.tex

## Troubleshooting

**Error:** Model object not found  
**Cause:** .rds file not in expected location  
**Solution:** Check output/ directory, verify saveRDS() was called

**Error:** Standard errors missing  
**Cause:** Model didn't specify clustering/robust SEs  
**Solution:** Re-run with vcov specification, document assumption
````

---

### 示例 3：实验协议校验器

**文件：** `.codebuddy/skills/validate-protocol/SKILL.md`

```markdown
---
name: validate-protocol
description: Validates experimental protocols against lab safety and reproducibility standards. Use when user provides lab protocol documents, asks to "check protocol", "validate procedure", or when reviewing .md or .docx experimental designs. Ensures required sections, safety notes, and replication details are present.
description_zh: 校验实验协议是否符合实验室安全与可复现性标准。用户提供协议文档、说 "check protocol"、"validate procedure" 时使用。
argument-hint: "[protocol file]"
allowed-tools: ["Read", "Write"]
---

# Validate Experimental Protocol

Checks experimental protocols for completeness, safety documentation, and reproducibility.

## Instructions

Step 1: **Parse protocol document**
   - Extract sections: Objective, Materials, Procedure, Safety, Expected Results
   - Check for required metadata: Date, Version, Author

Step 2: **Validate required elements**
   - Materials list complete (catalog numbers, suppliers)
   - Safety warnings for hazardous materials
   - Quantitative measurements (volumes, temperatures, times)
   - Controls specified

Step 3: **Reproducibility check**
   - Equipment specifications listed
   - Randomization described (if applicable)
   - Sample sizes justified
   - Data recording method specified

Step 4: **Generate report**
   - PASS/FAIL for each section
   - Missing elements highlighted
   - Suggestions for improvement

## Examples

### Example 1: Cell Culture Protocol
**User says:** "Check if my protocol is complete before submitting to IRB"
**Context:** Protocol for isolating primary neurons
**Actions:**
1. Read protocol.md
2. Check Materials: ✓ catalog numbers present
3. Check Safety: ✗ missing biosafety level designation
4. Check Procedure: ✓ quantitative (37°C, 5% CO₂, 10 mL media)
**Result:** Report: "Missing: BSL-2 designation. Add before IRB submission."

## Troubleshooting

**Error:** Cannot parse sections
**Cause:** Non-standard heading format
**Solution:** Add heading patterns to Step 1 (e.g., "### Safety Notes")
```

---

## 测试你的技能

### 第 1 步：手工测试

1. 创建技能目录：`mkdir -p .codebuddy/skills/your-skill-name`
2. 复制 SKILL.md 模板并定制
3. 修改后的热重载尚未证实；若运行没有反映新正文，记录客户端与技能版本，新开会话复测
4. 触发技能：用你的一条真实中文触发短语，再用 `/name` 做显式调用对照
5. 核验：区分引擎发现、自动调用、显式调用与 UI 可见性，并检查指令和输出

### 第 2 步：迭代

- **技能不触发：** 用更具体的触发短语改 description
- **指令不清：** 给 Steps 补更多示例与细节
- **输出不对：** 加校验步骤、加故障排查一节

### 第 3 步：成功标准

- ✅ 技能在 90%+ 的相关查询上触发
- ✅ 用预期步数走完整个工作流
- ✅ 正常运行时零 API 错误
- ✅ 同一任务跨会话产出一致

---

## 领域定制清单

把本模板适配到你的领域时：

- [ ] 用你领域的术语替换示例触发短语
- [ ] 加上领域特有的文件类型（`.R`、`.py`、`.ipynb`、`.tex`、`.stan`）
- [ ] 写进领域惯例（记号、格式、引用风格）
- [ ] 引用标准工具（`ggplot2`、`pandas`、`TikZ`、`Stata`）
- [ ] 加上你工具链里常见的错误信息
- [ ] 写进机构要求（学位论文格式、期刊模板）

---

## 允许工具参考

| 工具 | 用于 |
|------|---------|
| `Read` | 读文件内容（脚本、稿件、数据） |
| `Write` | 创建新文件（报告、表格、输出） |
| `Edit` | 原地修改既有文件 |
| `Grep` | 搜索文件内容（引用、函数名） |
| `Glob` | 按模式找文件（*.R、*.tex、*.csv） |
| `Bash` | 跑命令（R 脚本、LaTeX 编译、git） |
| `Agent` | 派生子代理（用于复杂的多步工作流） |

**安全说明：** `allowed-tools` 是限制技能可用工具的白名单（见[语义说明](#allowed-tools)）。只列实际需要的工具；「只读技能」应只列只读工具，并在正文写一句「不修改被审文件」。`disallowed-tools` 无对应语义。白名单与正文约束能降低误写风险，但不是绝对安全保证；仍须核验模型实际调用、权限规则与钩子。

---

## 这个模板住在哪

- **文件：** `templates/skill-template.md`
- **用途：** 领域专用技能的起点
- **用法：** 复制到 `.codebuddy/skills/[name]/SKILL.md`，按你的领域定制

已有技能的示例见 `.codebuddy/skills/` 目录（63 个技能，覆盖 LaTeX、R、Quarto 与研究工作流）。
