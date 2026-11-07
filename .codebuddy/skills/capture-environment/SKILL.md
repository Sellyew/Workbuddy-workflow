---
name: capture-environment
description: 为复现包对计算环境做快照 —— 探测分析技术栈（R / Stata / Python），输出相应的锁文件（renv.lock + sessionInfo.txt、requirements.txt / environment.yml / uv.lock、Stata 版本 + ado 包清单），记录随机种子与 RNG 类型，可选地写一份用于钉住版本的 Dockerfile，并产出一段可直接粘贴的「Computational requirements」块。当用户说 "capture the environment"、"snapshot my dependencies"、"pin the versions"、"make a renv.lock / requirements.txt"、"make this byte-reproducible"，或在向 openICPSR / AEA Data Editor 发布复现包之前使用。
description_zh: 为复现包对计算环境做快照 —— 探测分析技术栈（R / Stata / Python），输出相应的锁文件（renv.lock + sessionInfo.txt、requirements.txt / environment.yml / uv.lock、Stata 版本 + ado 包清单），记录随机种子与 RNG 类型，可选地写一份用于钉住版本的 Dockerfile，并产出一段可直接粘贴的「Computational requirements」块。当用户说 "capture the environment"、"snapshot my dependencies"、"pin the versions"、"make a renv.lock / requirements.txt"、"make this byte-reproducible"，或在向 openICPSR / AEA Data Editor 发布复现包之前使用。
argument-hint: "[project-dir] [--docker] [--no-verify] (project-dir defaults to repo root)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]

---

# `/capture-environment` —— 对计算环境做快照

复现包如果能在 2026 年的作者笔记本上运行，却无法在 2029 年的其他环境中运行，就谈不上可复现。本技能记录*精确的*计算环境，包括语言版本、包版本、随机种子、RNG 类型，以及可选的操作系统层，让审稿人、AEA Data Editor 或未来的你能够重建环境。它先识别项目技术栈，再生成相应生态所需的文件，最后核验锁文件能否干净安装。

**核心原则：** 凡会影响结果的内容都要钉住。除展示时的取整外，在钉住的环境中重跑，应将论文结果复现到 [`replication-protocol.md`](../../rules/replication-protocol.md) 规定的容差内；使用可选的 Dockerfile 时，应达到*逐字节一致*。

## 何时使用

- **发布复现包之前**（发布到 openICPSR、Zenodo、Dataverse 或期刊归档）：AEA Data Editor / DCAS 标准要求环境有文档且版本已钉住。
- **投稿前**：与 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 配合。后者核对*数字*，本技能记录产生这些数字的*环境*，并生成后者要求的 `sessionInfo.txt`。
- **项目中途新增或升级包之后**：重新采集快照，避免锁文件与代码实际加载的依赖脱节。
- **把项目交给共同作者或 RA 时**：帮助对方重建你的技术栈。

## 输入

从 `$ARGUMENTS` 解析项目目录与选项，将项目目录赋给命名变量 `project_dir`，不要读取 shell 的位置参数。校验 `project_dir` 是已存在、可读的目录；出现额外位置参数或未知选项时，停止并报告。由 `project_dir` 拼接出的路径在命令中始终加引号。

- `project_dir`（可选）—— 项目目录，默认为仓库根目录。技能会查找 `scripts/R/`、`scripts/stata/`、`scripts/python/`。
- `--docker` —— 同时生成 `Dockerfile`，钉住操作系统 + 语言版本 + 系统库，以实现逐字节复现。
- `--no-verify` —— 跳过 Phase 3 的尽力而为干净安装检查，适用于 CI 或本地未安装相应工具链的情况。

## 工作流

### Phase 0：探测技术栈

用 glob 检查技术栈信号，决定执行哪些采集路径。一个项目可以使用多种语言，例如用 R 做 DiD，用 Stata 做 IV 稳健性检查。

| 信号 | 技术栈 | 采集路径 |
|---|---|---|
| `scripts/R/*.R`、`DESCRIPTION`、`renv/`、`*.Rproj` | **R** | renv + sessionInfo |
| `scripts/python/*.py`、`*.ipynb`、`pyproject.toml`、`requirements.txt`、`environment.yml`、`uv.lock` | **Python** | pip / conda / uv |
| `scripts/stata/*.do` | **Stata** | version + ado list |

如果找不到任何信号，报告搜索不到可采集的环境并停下。

### Phase 1：按语言采集

**R** —— 生成两份产物：
- 通过 `renv::snapshot()` 生成 `renv.lock`。如果项目尚未由 renv 管理，先运行 `renv::init(bare = TRUE)`。snapshot 会记录每个包 + 版本 + 来源/远端以及 R 版本。随机种子遵守 [`r-code-conventions.md`](../../rules/r-code-conventions.md) 的约定。
- 通过 `Rscript -e "writeLines(capture.output(sessionInfo()), 'output/sessionInfo.txt')"` 生成 `sessionInfo.txt`，作为 `/audit-reproducibility` 所需的人类可读配套文件。

**Python** —— 只生成与项目现有工具链相符的文件，不要引入新工具链：
- 如果已有 `pyproject.toml` + `uv`，优先生成 `uv.lock`，它能完全解析依赖、记录哈希并支持跨平台：`uv lock` / `uv export --format requirements-txt > requirements.txt`。
- venv/pip 项目使用 `pip freeze`（或 `python -m pip freeze`）生成 `requirements.txt`，用 `==` 精确钉住版本。
- conda 项目使用 `conda env export --no-builds` 生成 `environment.yml`。
无论使用哪种工具链，都要在报告中记录解释器版本（`python --version`）。

**Stata** —— Stata 没有锁文件，因此采集最接近的等价信息，与 [`stata-code-conventions.md`](../../rules/stata-code-conventions.md) §3 保持一致：
- 用 grep 检查 `scripts/stata/*.do`，报告每个 `.do` 文件实际声明的 `version` 行，例如 `version 18`。
- 编写一个小 `.do` 文件，对流水线使用的用户安装命令（`reghdfe`、`ivreg2`、`estout`/`esttab`、`rdrobust`、`csdid`、…）运行 `which`，并运行 `ado dir` 与 `about`，将 ado/plus 包清单日志写入 `output/sessionInfo_stata.txt`。
- 明确说明：Stata 的 `version 18` 属于*语义*版本钉住，只固定命令行为，不固定二进制。由于 Stata 受许可证限制且不可再分发，Phase 2 的 Dockerfile 无法解决这一问题。报告中要记录确切的 Stata 版本 + 版本型（SE/MP/IC）+ 更新级别，供复现者核对。

### Phase 1b：记录随机种子与 RNG

用 grep 查找分析脚本中的主种子和 RNG 类型，并写入「Computational requirements」块：
- **R**：`set.seed(YYYYMMDD)` 和 `RNGkind()`；如果有并行/蒙特卡洛工作，标出 `"L'Ecuyer-CMRG"`，见 [`simulation-conventions.md`](../../rules/simulation-conventions.md)。
- **Stata**：`set seed` 与 `set sortseed`。
- **Python**：`numpy.random.default_rng(seed)` / `random.seed()` / 框架种子。

如果流水线包含随机化工作（bootstrap、MC、RCT 重随机化、置换推断）却**没有**找到种子，必须显示 WARNING，因为未播种的随机结果不可复现。

### Phase 2：Dockerfile（仅 `--docker` 时）

生成 `Dockerfile`，钉住操作系统 + 语言版本 + 系统库，以实现逐字节复现：
- **R** → 使用 `FROM rocker/r-ver:<X.Y.Z>` 让 Rocker 钉住 R 版本，加入 `COPY renv.lock`、`RUN R -e "renv::restore()"`，并用 `apt-get install` 安装包所需系统库，例如 `libcurl4-openssl-dev`；空间分析使用 `libgdal-dev`。
- **Python** → 使用 `FROM python:<X.Y.Z>-slim`、`COPY requirements.txt` / `uv.lock`、`RUN pip install -r requirements.txt`（或 `uv sync --frozen`）。
- **Stata** → 无法钉住带许可证的二进制，只生成 `Dockerfile` 骨架，记录预期的 Stata 版本 + 版本型，把 `stata` 的安装/许可步骤留给复现者，并在注释中指向 AEA 关于 Stata 镜像的指引。

尽可能钉住 digest（`FROM image@sha256:…`），防止基础镜像漂移。

### Phase 3：核验锁文件能干净安装（尽力而为；`--no-verify` 跳过）

在一次性位置尝试干净还原并报告 PASS / FAIL，绝不能覆盖工作环境：
- **R**：将 `renv::restore()` 还原到临时库，或运行 `Rscript -e "renv::status()"` 做干跑检查。
- **Python**：在全新 venv 中运行 `uv sync --frozen` / `pip install --dry-run -r requirements.txt`。
- **Docker**（若 `--docker`）：运行 `docker build` 构建镜像。

FAIL 表示锁文件引用了无法解析的包版本，例如发行版已撤回、远端为私有或 wheel 仅支持特定平台。报告具体原因，不要自动修改锁文件。

### Phase 4：报告

打印一段可直接粘贴的块，并写到 `output/computational_requirements.md`：

```markdown
## Computational requirements

**Software:** R 4.4.1 (or: Stata 18.0 SE, update 2026-01-15; Python 3.12.3)
**OS used:** macOS 15.5 (arm64) — Dockerfile pins Ubuntu 24.04 for portability
**Key packages:** fixest 0.12.1, did 2.1.2 (full list in renv.lock)
**Random seeds:** set.seed(20260609); RNGkind("L'Ecuyer-CMRG") for the bootstrap
**Approx. runtime:** [author confirms — e.g. ~12 min, 8 cores]
**Lockfiles in package:** renv.lock, output/sessionInfo.txt[, Dockerfile]
```

软件、包和种子行根据采集产物预填，运行时长由作者确认。

## 输出 / 产物

| 技术栈 | 写出的文件 |
|---|---|
| R | `renv.lock`、`output/sessionInfo.txt` |
| Python | `requirements.txt` *或* `environment.yml` *或* `uv.lock`（与项目工具链相符） |
| Stata | `output/sessionInfo_stata.txt`（版本 + ado 清单；这样命名是为了在混合项目里不覆盖 R 的那份） |
| 任意（`--docker`） | `Dockerfile` |
| 始终 | `output/computational_requirements.md`（那段可直接粘贴的块） |

## 退出行为

- **所有采集成功、核验 PASS（或 `--no-verify`）：** 退出 0，打印 requirements 块。
- **随机化流水线上缺种子的 WARNING：** 退出 0 并显示警告。快照仍会写入，但可复现性已经受损。
- **核验 FAIL（锁文件解析不了）：** 退出 1，使本技能可以作为发布前 `/commit` 的门禁。报告无法解析的包，不要悄悄「修」锁文件。
- **Phase 0 没探测到技术栈：** 退出 1，并列出搜索过的目录。

## 交叉引用

- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 钉住环境旨在复现的那份容差契约。
- [`.codebuddy/rules/r-code-conventions.md`](../../rules/r-code-conventions.md) —— 本技能读取的 R 播种 + 输出路径约定。
- [`.codebuddy/rules/stata-code-conventions.md`](../../rules/stata-code-conventions.md) —— Stata 路径镜像的 §3 `sessionInfo_stata.txt` + `version` 钉住。
- [`.codebuddy/rules/simulation-conventions.md`](../../rules/simulation-conventions.md) —— 可复现并行/MC 工作用的 L'Ecuyer 流。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 原始数据受限时，*环境*仍然要随包发布，尽管数据不发；把 README 的「data availability」章节与本块对齐。
- [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) —— 消费本技能产出的 `sessionInfo.txt`；在之后运行它。
- [`/data-analysis`](../data-analysis/SKILL.md)、[`/stata-replication`](../stata-replication/SKILL.md)、[`/simulation-study`](../simulation-study/SKILL.md) —— 本技能为其环境做快照的那些流水线。
- [AEA Data Editor checklist](https://aeadataeditor.github.io/) / [openICPSR](https://www.openicpsr.org/) / DCAS —— 本技能对外瞄准的外部标准。

## 本技能不做的事

- **不重跑分析，也不核对数字。** 本技能只采集环境；稿件数值论断与产出的核验由 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 负责。
- **打包数据或做去标识化。** 锁文件描述的是软件，不是数据。披露规避、去标识化与数据可用性声明不在范围内 —— 见 [`confidential-data.md`](../../rules/confidential-data.md)。
- **升级或「修」你的依赖。** 它记录代码当前使用的东西。若核验 FAIL 暴露出某个被撤回的版本，由你决定是否钉一个替代。
- **钉住 Stata 二进制。** Stata 是许可证授权、不可再分发；技能记录确切的版本/版本型/更新级别好让复现者对上，但无法把它容器化。
