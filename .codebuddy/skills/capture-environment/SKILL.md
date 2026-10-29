---
name: capture-environment
description: 为复现包对计算环境做快照 —— 探测分析技术栈（R / Stata / Python），输出相应的锁文件（renv.lock + sessionInfo.txt、requirements.txt / environment.yml / uv.lock、Stata 版本 + ado 包清单），记录随机种子与 RNG 类型，可选地写一份用于钉住版本的 Dockerfile，并产出一段可直接粘贴的「Computational requirements」块。当用户说 "capture the environment"、"snapshot my dependencies"、"pin the versions"、"make a renv.lock / requirements.txt"、"make this byte-reproducible"，或在向 openICPSR / AEA Data Editor 发布复现包之前使用。
description_zh: 为复现包对计算环境做快照 —— 探测分析技术栈（R / Stata / Python），输出相应的锁文件（renv.lock + sessionInfo.txt、requirements.txt / environment.yml / uv.lock、Stata 版本 + ado 包清单），记录随机种子与 RNG 类型，可选地写一份用于钉住版本的 Dockerfile，并产出一段可直接粘贴的「Computational requirements」块。当用户说 "capture the environment"、"snapshot my dependencies"、"pin the versions"、"make a renv.lock / requirements.txt"、"make this byte-reproducible"，或在向 openICPSR / AEA Data Editor 发布复现包之前使用。
argument-hint: "[project-dir] [--docker] [--no-verify] (project-dir defaults to repo root)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]

---

# `/capture-environment` —— 对计算环境做快照

一个在 2026 年能在作者笔记本上跑、2029 年在别处跑不起来的复现包，不算可复现。本技能采集*精确的*计算环境 —— 语言版本、包版本、随机种子、RNG 类型，以及（可选）操作系统层 —— 好让审稿人、AEA Data Editor 或未来的你能重建它。它探测项目用的是哪套技术栈，产出那套生态所期待的东西，然后核验锁文件能干净安装。

**核心原则：** 结果依赖的一切都要钉住。除了展示层的取整，在钉住的环境上重跑应当把论文复现到 [`replication-protocol.md`](../../rules/replication-protocol.md) 的容差之内 —— 用上可选的 Dockerfile 时是*逐字节一致*。

## 何时使用

- **在发布复现包之前**（到 openICPSR、Zenodo、Dataverse 或某份期刊的归档）—— AEA Data Editor / DCAS 标准期待一个有文档、版本钉住的环境。
- **投稿前**，与 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 配合 —— 那个技能查*数字*；本技能采集产出这些数字的*环境*（它对 `sessionInfo.txt` 的要求由本技能满足）。
- **项目中途新增或升级了某个包之后** —— 重新快照，免得锁文件与代码实际加载的东西脱节。
- **把项目交给共同作者或 RA 时**，他需要重建你的技术栈。

## 输入

- `$0` —— 项目目录。默认是仓库根目录。技能会在 `scripts/R/`、`scripts/stata/`、`scripts/python/` 下查找。
- `--docker` —— 同时产出一份 `Dockerfile`，钉住操作系统 + 语言版本 + 系统库，以实现逐字节复现。
- `--no-verify` —— 跳过 Phase 3（尽力而为的干净安装检查）。在 CI 里，或本地没装该工具链时有用。

## 工作流

### Phase 0：探测技术栈

对技术栈信号做 glob，决定跑哪些采集路径（一个项目可以多语言 —— R 里做 DiD，Stata 里做 IV 稳健性检查）：

| 信号 | 技术栈 | 采集路径 |
|---|---|---|
| `scripts/R/*.R`、`DESCRIPTION`、`renv/`、`*.Rproj` | **R** | renv + sessionInfo |
| `scripts/python/*.py`、`*.ipynb`、`pyproject.toml`、`requirements.txt`、`environment.yml`、`uv.lock` | **Python** | pip / conda / uv |
| `scripts/stata/*.do` | **Stata** | version + ado list |

找不到任何信号就报告并停下 —— 没有环境可采。

### Phase 1：按语言采集

**R** —— 产出两份产物：
- `renv.lock`，经 `renv::snapshot()`（若项目未由 renv 管理，先跑 `renv::init(bare = TRUE)`；snapshot 会记录每个包 + 版本 + 来源/远端以及 R 版本）。遵守 [`r-code-conventions.md`](../../rules/r-code-conventions.md) 的播种约定。
- `sessionInfo.txt`，经 `Rscript -e "writeLines(capture.output(sessionInfo()), 'output/sessionInfo.txt')"` —— 即 `/audit-reproducibility` 要找的那份人类可读伴侣文件。

**Python** —— 产出与项目现有工具链相符的那一份（不要发明新的）：
- `uv.lock`（存在 `pyproject.toml` + `uv` 时优先 —— 完全解析、带哈希、跨平台）：`uv lock` / `uv export --format requirements-txt > requirements.txt`。
- `requirements.txt`，venv/pip 项目用 `pip freeze`（或 `python -m pip freeze`）—— 用 `==` 精确钉住。
- `environment.yml`，conda 项目用 `conda env export --no-builds`。
并始终在报告里记录解释器版本（`python --version`）。

**Stata** —— Stata 没有锁文件，所以采集最接近的等价物（与 [`stata-code-conventions.md`](../../rules/stata-code-conventions.md) §3 镜像）：
- 每个 `.do` 文件声明的钉住 `version` 行（例如 `version 18`）—— grep `scripts/stata/*.do`，报告实际钉住的版本。
- 一份 ado/plus 包清单：一个小 `.do`，对流水线用到的用户安装命令（`reghdfe`、`ivreg2`、`estout`/`esttab`、`rdrobust`、`csdid`、…）跑 `which`，外加 `ado dir` 与 `about`，日志写到 `output/sessionInfo_stata.txt`。
- 一条说明：Stata 的版本钉住是*语义性的*（`version 18` 固定命令行为），不是二进制钉住 —— Dockerfile（Phase 2）在这里帮不上忙，因为 Stata 是许可证授权、不可再分发；在报告里记录确切的 Stata 版本 + 版本型（SE/MP/IC）+ 更新级别，好让复现者能对上。

### Phase 1b：记录随机种子与 RNG

grep 分析脚本里的主种子与 RNG 类型，好让「Computational requirements」块能写出它们：
- **R**：`set.seed(YYYYMMDD)`，以及 `RNGkind()` —— 若有并行/蒙特卡洛工作，标出 `"L'Ecuyer-CMRG"`（见 [`simulation-conventions.md`](../../rules/simulation-conventions.md)）。
- **Stata**：`set seed` 与 `set sortseed`。
- **Python**：`numpy.random.default_rng(seed)` / `random.seed()` / 框架种子。

若流水线含随机化工作（bootstrap、MC、RCT 重随机化、置换推断）却**没有**找到种子，把它作为 WARNING 摆出 —— 未播种的随机结果不可复现。

### Phase 2：Dockerfile（仅 `--docker` 时）

产出一份 `Dockerfile`，钉住操作系统 + 语言版本 + 系统库，以实现逐字节复现：
- **R** → `FROM rocker/r-ver:<X.Y.Z>`（Rocker 钉住 R 版本）、`COPY renv.lock`、`RUN R -e "renv::restore()"`，外加 `apt-get install` 装这些包需要的系统库（例如 `libcurl4-openssl-dev`；空间分析用 `libgdal-dev`）。
- **Python** → `FROM python:<X.Y.Z>-slim`、`COPY requirements.txt` / `uv.lock`、`RUN pip install -r requirements.txt`（或 `uv sync --frozen`）。
- **Stata** → 无法钉住那个带许可证的二进制；产出一份 `Dockerfile` 骨架，记录预期的 Stata 版本 + 版本型，并把 `stata` 的安装/许可步骤留给复现者（附一条注释指向 AEA 关于 Stata 镜像的指引）。

尽可能钉住 digest（`FROM image@sha256:…`），这样基础镜像无法漂移。

### Phase 3：核验锁文件能干净安装（尽力而为；`--no-verify` 跳过）

在一个一次性位置尝试干净还原，并报告 PASS / FAIL —— 绝不覆盖工作环境：
- **R**：`renv::restore()` 到临时库，或 `Rscript -e "renv::status()"` 做干跑检查。
- **Python**：在一个全新 venv 里 `uv sync --frozen` / `pip install --dry-run -r requirements.txt`。
- **Docker**（若 `--docker`）：对镜像跑 `docker build`。

此处 FAIL 意味着锁文件引用了某个解析不出来的包版本（被撤回的发行版、私有远端、平台特定的 wheel）。报告它；不要自动改锁文件。

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

软件/包/种子那几行从采到的产物预填；运行时长留给作者确认。

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
- **随机化流水线上缺种子的 WARNING：** 退出 0，并把警告摆出来 —— 可复现性受损，但快照仍然写下了。
- **核验 FAIL（锁文件解析不了）：** 退出 1，这样本技能可以为发布前的 `/commit` 设门禁。报告解析不出的包；不要悄悄「修」锁文件。
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

- **重跑你的分析或核对你的数字。** 它采集环境；[`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 把稿件的数值论断与产出做核验。
- **打包数据或做去标识化。** 锁文件描述的是软件，不是数据。披露规避、去标识化与数据可用性声明不在范围内 —— 见 [`confidential-data.md`](../../rules/confidential-data.md)。
- **升级或「修」你的依赖。** 它记录代码当前使用的东西。若核验 FAIL 暴露出某个被撤回的版本，由你决定是否钉一个替代。
- **钉住 Stata 二进制。** Stata 是许可证授权、不可再分发；技能记录确切的版本/版本型/更新级别好让复现者对上，但无法把它容器化。
