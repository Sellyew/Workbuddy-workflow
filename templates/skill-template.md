# 技能创建模板

**用这个模板为你的学术工作流创建领域专用的技能。**

---

## 什么时候该自建技能

当你发现自己出现下面这些情况时，就该建一个技能：
- 反复向 Claude 解释同一套 3 步以上的工作流
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
argument-hint: "[brief hint for user]"
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Agent"]
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

## 高级 frontmatter 字段

除了上面展示的基本字段，技能还支持额外的 YAML frontmatter，用于细粒度控制：

| 字段 | 用途 | 示例 |
|-------|---------|---------|
| `context` | 设为 `fork` 即在隔离子代理上下文里运行 | 保护主对话不被冗长输出淹没 |
| `agent` | 链接到 `.codebuddy/agents/` 里的代理定义 | `proofreader` |
| `hooks` | 技能专属钩子（语法同 settings.json） | 自定义前置/后置动作 |
| `model` | 强制指定某个模型档位 | `lite`（更便宜）、`reasoning`（更聪明） |
| `disable-model-invocation` | 阻止 Claude 自动触发 | `true`（只能经 `/skill-name` 调用） |
| `disallowed-tools` | 技能生效期间**移除** Claude 工具池里的工具——真正的限制机制（见下面的语义说明） | 只读审计用 `["Edit", "Write"]` |
| `paths` | glob 模式，划定技能何时自动激活——相当于路径作用域规则在技能层面的对应物 | `["scripts/**/*.R"]` |
| `when_to_use` | 自动调用时额外的路由上下文，超出 description 之外 | `"after any merge conflict"` |
| `arguments` | 供正文里 `$name` 替换的具名位置参数 | `[infile, outfile]` |

### `allowed-tools` vs `disallowed-tools` —— 语义很要紧 {#allowed-vs-disallowed}

**`allowed-tools` 是一份预先批准清单，不是沙箱。** 按官方文档的说法：它「在技能生效期间为所列工具授予权限，这样 Claude 使用它们时不必向你请求批准。**它不限制哪些工具可用：每个工具仍然可调用**」——没列出的工具只是走你正常的权限设置。把 `Bash` 从 `allowed-tools` 里省掉，**并不**会让技能变成只读。

**要真正移除工具，用 `disallowed-tools`。** 列在那里的工具会在技能生效期间被从 Claude 的可用池里拿走（限制在你下一条消息时解除）。对必须永不写入——或者永不因为一个提问而卡住后台循环——的自主型或 fork 型审读技能，就显式禁用：

```yaml
allowed-tools: ["Read", "Grep", "Glob"]        # pre-approve the read path (no prompts)
disallowed-tools: ["Edit", "Write", "Bash"]    # actually remove the write path
```

**动态内容**——技能可以用字符串替换注入实时数据：

- `$ARGUMENTS` —— 完整参数字符串（例如 `/skill-name Lecture01` → `Lecture01`）
- `$0`、`$1` —— 位置参数（从 0 开始）
- `${CLAUDE_SKILL_DIR}` —— 技能所在目录的路径（用于随技能打包的辅助文件）
- `` !`git log --oneline -5` `` —— 技能加载时注入的动态命令输出

细节与示例见[指南的技能 frontmatter 参考](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#skill-frontmatter)。

### 什么时候该设 `disable-model-invocation: true` {#when-to-disable-model-invocation}

凡是技能会写入**持久的、承重的文件**、而用户必须明确意图才能创建这类文件时，就设这个旗标。否则，Claude 可能在一条含糊匹配的提示词下自动触发该技能，产出一个不做手工清理就很难撤销的文件。

**以下技能要设：**

- 创建新的持久源文件（`/create-lecture` → 新的 `.tex`，`/new-diagram` → 新的 TikZ 源）。
- 写入会自我修改的产物（`/learn` → 新的 SKILL.md，`/checkpoint` → 状态快照，`/preregister` → 预注册文档）。
- 跑长时间的写文件循环（`/simulation-study` → 带种子的蒙特卡洛运行与结果，`/vaccinate` → 资格台账的一行，`/deep-audit` → 审计并修复的循环）。

**以下技能不要设：**

- 产出临时分析输出（`/proofread`、`/review-r`、`/visual-audit`——写在 `quality_reports/` 下，容易删）。
- 是只读诊断（`/permission-check`、`/context-status`）。
- 从既有源码编译 / 渲染 / 部署（`/compile-latex`、`/deploy`、`/extract-tikz`）。

这个旗标仍然允许用 `/skill-name` 直接调用——它只挡住模型凭启发式匹配自动触发。

### CODEBUDDY.md 的 `@import` 语法（Anthropic 2026 年 4 月）

Anthropic 的 `CODEBUDDY.md` 支持 `@path/to/import` 来引入额外文件。示例：

```markdown
See @README.md for project overview and @package.json for available commands.

# Personal overrides
@~/.workbuddy/my-project-instructions.md

# Domain-specific instructions
@docs/git-instructions.md
```

**本模板的 `CODEBUDDY.md` 刻意不用 `@import`** ——它刻意保持精简，而引入碎片会把入门上下文打碎（forker 期待的是「会话启动时加载一个文件」）。这里提一句，是给那些定制内容已经大到值得拆分的 forker；对简短的 CODEBUDDY.md，拆分往往弊大于利。

---

## 写出有效的描述

`description` 字段决定 Claude 何时加载你的技能。用这个结构：

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

```markdown
---
name: format-regression-tables
description: Converts R regression outputs to publication-ready LaTeX tables. Use when user runs regressions and says "make a table", "format results", or "export to LaTeX". Handles lm, glm, felm, and fixest objects. Applies field-specific conventions (standard errors in parentheses, stars for significance).
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
```

---

### 示例 3：实验协议校验器

**文件：** `.codebuddy/skills/validate-protocol/SKILL.md`

```markdown
---
name: validate-protocol
description: Validates experimental protocols against lab safety and reproducibility standards. Use when user provides lab protocol documents, asks to "check protocol", "validate procedure", or when reviewing .md or .docx experimental designs. Ensures required sections, safety notes, and replication details are present.
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
3. 技能会热重载——改动无需重启就会被检出
4. 触发技能：用你的一条触发短语
5. 核验：技能加载了、指令清楚、输出正确

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

**安全说明：** `allowed-tools` 只做预先批准——它**不**做限制（见[语义说明](#allowed-vs-disallowed)）。对真正只读的校验类技能，加 `disallowed-tools: ["Edit", "Write", "Bash"]`；对自主/后台技能，还要禁用 `AskUserQuestion`，免得循环卡在某个提问上。只把你会用到的工具列进 `allowed-tools` 仍是好卫生（它记录了意图、把静默的预先批准降到最少），但它不是沙箱。

---

## 这个模板住在哪

- **文件：** `templates/skill-template.md`
- **用途：** 领域专用技能的起点
- **用法：** 复制到 `.codebuddy/skills/[name]/SKILL.md`，按你的领域定制

已有技能的示例见 `.codebuddy/skills/` 目录（63 个技能，覆盖 LaTeX、R、Quarto 与研究工作流）。
