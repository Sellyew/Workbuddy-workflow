---
name: r-package-check
description: 运行完整的 R 包发布门禁——重新生成文档、跑测试套件、运行 R CMD check --as-cran，并在发布或投稿前把每一条 ERROR / WARNING / NOTE 对照 CRAN 政策做分诊。当用户说 "check my R package"、"R CMD check"、"is this package CRAN-ready"、"run devtools::check"、"prepare for CRAN submission"，或指向一个含 DESCRIPTION 文件的目录时使用。产出检查报告 + CRAN 投稿清单，存到 `quality_reports/`。
description_zh: 运行完整的 R 包发布门禁——重新生成文档、跑测试套件、运行 R CMD check --as-cran，并在发布或投稿前把每一条 ERROR / WARNING / NOTE 对照 CRAN 政策做分诊。当用户说 "check my R package"、"R CMD check"、"is this package CRAN-ready"、"run devtools::check"、"prepare for CRAN submission"，或指向一个含 DESCRIPTION 文件的目录时使用。产出检查报告 + CRAN 投稿清单，存到 `quality_reports/`。
argument-hint: "[path to package root, or blank to autodetect from DESCRIPTION]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Task", "Monitor"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/r-package-check` — R 包发布门禁

运行 document → test → check → triage 流水线，判定一个 R 包能否发布，然后审查源码中 `R CMD check` 看不见的问题。

**输入：** `$ARGUMENTS` —— 包根目录（含 `DESCRIPTION` 的目录）。若为空，则在工作目录内及向上搜索 `DESCRIPTION` 自动探测。

---

## 约束

- **遵循 [`.codebuddy/rules/r-package-conventions.md`](../../rules/r-package-conventions.md)** —— CRAN 就绪标准（0 errors、0 warnings、notes 有解释）就是门禁。
- **把 `man/` 与 `NAMESPACE` 当作生成物** —— 用 `devtools::document()` 重新生成；绝不手工编辑。
- **在宣布包可发布之前，对源码运行 `r-package-reviewer` 代理。**
- **不要升版本号，也不要向 CRAN 提交。** 本技能只负责*检查*；何时投稿由人决定。

---

## 工作流阶段

### Phase 0: 起飞前报告

```markdown
## Pre-Flight Report — R Package Check

**Package:** [name + version from DESCRIPTION]
**Root:** [path]
**Exported functions:** [from NAMESPACE / `@export` count]
**Dependencies:** Imports [list] · Suggests [list] · Depends [list]
**Toolchain available:** devtools [✓/✗], roxygen2 [✓/✗], testthat [✓/✗], R CMD [✓/✗], covr [✓/✗]
**Plan:** document → test → check --as-cran → triage → review
```

先用一次快速探测检查工具链；若缺 `devtools`/`R CMD`，停下并告诉用户要装什么。

```bash
Rscript -e 'cat("devtools:", requireNamespace("devtools", quietly=TRUE),
               "roxygen2:", requireNamespace("roxygen2", quietly=TRUE),
               "testthat:", requireNamespace("testthat", quietly=TRUE),
               "covr:", requireNamespace("covr", quietly=TRUE), "\n")'
```

### Phase 1: 生成文档

重新生成 `man/` + `NAMESPACE`，并检测漂移（生成物未提交）：

```bash
Rscript -e 'devtools::document("[pkg]")'
git -C "[pkg]" status --short man/ NAMESPACE   # any diff = generated docs were stale
```

若 `git status` 显示有改动，标记出来：已提交的 `man/`/`NAMESPACE` 与 roxygen 块不同步。

### Phase 2: 跑测试

```bash
Rscript -e 'devtools::test("[pkg]")'
```

报告失败项，以及（若 `covr` 可用，见 Phase 4）导出函数的覆盖率。

### Phase 3: 检查（`--as-cran`）

运行完整检查。**这一步很慢**（几分钟）——用 **Monitor 工具**后台启动并流式读取，而不是阻塞等待：

```bash
Rscript -e 'devtools::check("[pkg]", args = "--as-cran")'
# or: R CMD build [pkg] && R CMD check --as-cran [pkg]_*.tar.gz
```

然后**把每一条结果分诊**进一张表：

| 结果 | 层级 | CRAN 政策含义 | 处置 |
|---|---|---|---|
| … | ERROR / WARNING / NOTE | … | 修复 / 说明理由 |

- **ERROR / WARNING** → 投稿前必须修复。
- **NOTE** → 修起来便宜就修；否则写下你会放进 `cran-comments.md` 的理由（例如 "New submission"、"Found the following (possibly) invalid URLs … the URL is correct and reachable"）。

### Phase 4: 覆盖率（可选）

```bash
Rscript -e 'covr::package_coverage("[pkg]")'
```

报告逐函数覆盖率；标出覆盖率为 0% 的导出函数。

### Phase 5: 源码审查

```
Delegate to the r-package-reviewer agent:
"Review the package source at [pkg]"
```

该代理是只读的，会返回它的报告；把它存到 `quality_reports/[pkg]_package_review.md`。处理 Critical（违反 CRAN 政策）与 High（对应 check 的 WARNING）两类审查发现。

### Phase 6: 发布门禁 + 报告

把报告存到 `quality_reports/[package]_package_check.md`，并给出判定：

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

- **不带 `--as-cran` 就不算数。** 裸跑 `R CMD check` 会漏掉真正决定能否投稿的政策检查。
- **生成物就是生成物。** 若文档漂移，修法是 `devtools::document()`，不是去编辑 `.Rd`。
- **门禁是 0/0/有解释。** 0 errors、0 warnings、每一条剩余 note 都有理由——低于这个标准就谈不上 "CRAN-ready"。
- **本技能不负责投稿。** 跨平台检查（win-devel、R-hub）以及真正的 `devtools::release()` 是维护者的决定。

## 长时间运行的检查：使用 Monitor 工具

`R CMD check --as-cran` 与 `covr` 可能跑几分钟。不要阻塞等待，也不要用 `sleep` 轮询：启动 **Monitor 工具**，让它的命令直接运行检查、把完整输出 tee 到日志、只打印你会据以行动的那些行，例如 `Rscript -e 'devtools::check("[pkg]", args = "--as-cran")' 2>&1 | tee quality_reports/r-package-check.log | grep --line-buffered -E 'ERROR|WARNING|NOTE|Status:|[Ee]rror'`。检查退出时监视即结束；把 `timeout_ms` 设到默认 5 分钟以上（上限 3600000）。过滤器必须同时匹配失败与成功，因为静默看起来和「还在跑」一模一样。若你只想要检查结束时的一声提示，改用 Bash 的 `run_in_background: true` 跑它，等作业报告退出后再读日志。Monitor 没有 job-id 参数，无法挂到已在后台运行的作业上；日志加 tail 的变体见 [`data-analysis/SKILL.md`](../data-analysis/SKILL.md)。
