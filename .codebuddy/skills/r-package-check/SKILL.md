---
name: r-package-check
description: 运行完整的 R 包发布检查：重新生成文档、运行测试套件和 R CMD check --as-cran，并在发布或投稿前依据 CRAN 政策逐条处理 ERROR / WARNING / NOTE。用户说 "check my R package"、"R CMD check"、"is this package CRAN-ready"、"run devtools::check"、"prepare for CRAN submission"、"检查 R 包"、"准备提交 CRAN" 时，或指向含 DESCRIPTION 文件的目录时使用。检查报告和 CRAN 投稿清单保存在 `quality_reports/`。
description_zh: 运行完整的 R 包发布检查：重新生成文档、运行测试套件和 R CMD check --as-cran，并在发布或投稿前依据 CRAN 政策逐条处理 ERROR / WARNING / NOTE。用户说 "check my R package"、"R CMD check"、"is this package CRAN-ready"、"run devtools::check"、"prepare for CRAN submission"、"检查 R 包"、"准备提交 CRAN" 时，或指向含 DESCRIPTION 文件的目录时使用。检查报告和 CRAN 投稿清单保存在 `quality_reports/`。
argument-hint: "[path to package root, or blank to autodetect from DESCRIPTION]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Grep", "Glob", "Bash", "Agent", "TaskOutput"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/r-package-check` — R 包发布门禁

依次运行 document → test → check → triage，判断 R 包能否发布，再审查源码中 `R CMD check` 无法发现的问题。

**输入：** `$ARGUMENTS`，即包含 `DESCRIPTION` 的包根目录。留空时，从工作目录开始，在当前目录及上级目录中搜索 `DESCRIPTION`。

---

## 约束

- **遵循 [`.codebuddy/rules/r-package-conventions.md`](../../rules/r-package-conventions.md)。** CRAN 就绪标准就是发布门禁：0 errors、0 warnings，notes 均有解释。
- **把 `man/` 和 `NAMESPACE` 视为生成物。** 用 `devtools::document()` 重新生成，绝不手工编辑。
- **宣布包可发布前，必须用 `r-package-reviewer` 代理审查源码。**
- **不要升版本号，也不要向 CRAN 提交。** 本技能只检查，是否投稿由人决定。

---

## 工作流阶段

### Phase 0: 开始前报告

```markdown
## Pre-Flight Report — R Package Check

**Package:** [name + version from DESCRIPTION]
**Root:** [path]
**Exported functions:** [from NAMESPACE / `@export` count]
**Dependencies:** Imports [list] · Suggests [list] · Depends [list]
**Toolchain available:** devtools [✓/✗], roxygen2 [✓/✗], testthat [✓/✗], R CMD [✓/✗], covr [✓/✗]
**Plan:** document → test → check --as-cran → triage → review
```

先快速探测工具链。缺少 `devtools` 或 `R CMD` 时，停下并告诉用户需要安装什么。

```bash
Rscript -e 'cat("devtools:", requireNamespace("devtools", quietly=TRUE),
               "roxygen2:", requireNamespace("roxygen2", quietly=TRUE),
               "testthat:", requireNamespace("testthat", quietly=TRUE),
               "covr:", requireNamespace("covr", quietly=TRUE), "\n")'
```

### Phase 1: 生成文档

重新生成 `man/` 和 `NAMESPACE`，检查生成物是否未提交、是否与源码漂移：

```bash
Rscript -e 'devtools::document("[pkg]")'
git -C "[pkg]" status --short man/ NAMESPACE   # any diff = generated docs were stale
```

如果 `git status` 显示改动，说明已提交的 `man/`/`NAMESPACE` 与 roxygen 块不同步，必须标记。

### Phase 2: 跑测试

```bash
Rscript -e 'devtools::test("[pkg]")'
```

报告测试失败项；如果 `covr` 可用，还要按 Phase 4 报告导出函数的覆盖率。

### Phase 3: 检查（`--as-cran`）

运行完整检查。**这一步很慢**，可能需要几分钟。用 **Bash** 启动并设置 `run_in_background: true`，将程序 stdout 与 stderr 写入日志；不要在命令末尾加 `&`，也不要用 `nohup` 脱离任务管理：

```bash
Rscript -e 'devtools::check("[pkg]", args = "--as-cran")' > quality_reports/r-package-check.log 2>&1
```

收到后台任务的**完成通知**后，用 **TaskOutput** 读取任务结果并核对退出码，再用 Read 检查 `quality_reports/r-package-check.log` 的完整内容。不要用 `sleep` 轮询，也不要把旧日志当作本次结果。Bash 只负责运行程序和生成程序日志，不生成 Markdown 报告。

然后把每条结果填入下表，逐项分诊：

| 结果 | 层级 | CRAN 政策含义 | 处置 |
|---|---|---|---|
| … | ERROR / WARNING / NOTE | … | 修复 / 说明理由 |

- **ERROR / WARNING**：投稿前必须修复。
- **NOTE**：修复成本低就修；否则写下准备放入 `cran-comments.md` 的理由，例如 "New submission"、"Found the following (possibly) invalid URLs … the URL is correct and reachable"。

### Phase 4: 覆盖率（可选）

```bash
Rscript -e 'covr::package_coverage("[pkg]")'
```

逐函数报告覆盖率，并标出覆盖率为 0% 的导出函数。

### Phase 5: 源码审查

```
Delegate to the r-package-reviewer agent:
"Review the package source at [pkg]"
```

该代理只读，会返回报告。调用方用 **Write 工具**把报告保存到 `quality_reports/[pkg]_package_review.md`，并处理 Critical（违反 CRAN 政策）与 High（对应 check 的 WARNING）两类发现。不要用 Bash 重定向代理回复来生成这份报告。

### Phase 6: 发布门禁 + 报告

用 **Write 工具**把第二份报告保存到 `quality_reports/[package]_package_check.md`，并给出判定。该文件与 Phase 5 的源码审查报告都要存在；Bash 只写程序日志，不写这两份 Markdown 报告：

```markdown
## Release Gate — [package] [version]
- R CMD check --as-cran: E errors, W warnings, N notes
- Tests: P passed, F failed
- Coverage: X% of exported functions
- r-package-reviewer: C critical, H high
- **Verdict:** RELEASABLE / FIX-FIRST / POLICY-VIOLATION

### CRAN-submission checklist
[ ] 0 errors, 0 warnings; each note justified in cran-comments.md
[ ] Version bumped + NEWS.md updated
[ ] devtools::check_win_devel() / R-hub on other platforms (note: run separately)
[ ] Reverse-dependency check if this is an update (revdepcheck)
```

---

## 要点

- **必须使用 `--as-cran`。** 裸跑 `R CMD check` 会漏掉决定能否投稿的政策检查。
- **生成物只能重新生成。** 文档漂移时，应运行 `devtools::document()`，不要编辑 `.Rd`。
- **通过标准是 0/0/有解释。** 即 0 errors、0 warnings，每条剩余 note 都有理由；达不到就不能称为 "CRAN-ready"。
- **本技能不负责投稿。** 跨平台检查（win-devel、R-hub）和真正运行 `devtools::release()`，都由维护者决定。

## 长时间运行的检查：后台完成通知

`R CMD check --as-cran` 和 `covr` 可能运行几分钟，统一使用 Bash 的 `run_in_background: true`，把完整程序输出重定向到日志。收到完成通知后，用 TaskOutput 读取任务结果，再检查退出码、当前日志和预期产物。不要用 `sleep` 轮询，不要另起脱离任务管理的进程，也不要只过滤成功或失败行而让另一种终态保持静默。程序日志可以留在 `quality_reports/`，两份 Markdown 报告则分别由 Write 创建。
