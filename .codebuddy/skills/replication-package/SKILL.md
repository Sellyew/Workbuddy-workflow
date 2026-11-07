---
name: replication-package
description: 按 AEA Data and Code Availability Standard（DCAS）/ openICPSR / Social Science Reproduction Platform 的期望，组装可直接提交的复现包，包括标准复现 README、数据集清单、计算环境快照、表／图 → 脚本:行映射，以及机密数据的存放方案。用户说 "build the replication package"、"prepare the openICPSR deposit"、"make the AEA data and code package"、"DCAS compliance"、"assemble the deposit for the journal"、"整理复现包"、"准备 openICPSR 存放" 或 "组装期刊数据代码包"，或在论文被接收、期刊数据编辑索要复现包时使用。它**不是**数值核验器；打包前会调用 `/audit-reproducibility` 确认断言可复现。
description_zh: 按 AEA Data and Code Availability Standard（DCAS）/ openICPSR / Social Science Reproduction Platform 的期望，组装可直接提交的复现包，包括标准复现 README、数据集清单、计算环境快照、表／图 → 脚本:行映射，以及机密数据的存放方案。用户说 "build the replication package"、"prepare the openICPSR deposit"、"make the AEA data and code package"、"DCAS compliance"、"assemble the deposit for the journal"、"整理复现包"、"准备 openICPSR 存放" 或 "组装期刊数据代码包"，或在论文被接收、期刊数据编辑索要复现包时使用。它**不是**数值核验器；打包前会调用 `/audit-reproducibility` 确认断言可复现。
argument-hint: "[manuscript path] [outputs-dir] [--docker] (outputs-dir defaults to output/)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent", "Task", "Skill"]

---

# 复现包

本技能生成论文接收后提交给期刊的存放物：一棵包含 `data/`、`code/`、`output/`、`README` 的目录树，以及一份 DCAS 合规检查清单。目录结构遵循 [AEA Data and Code Availability Standard](https://datacodestandard.org/)、openICPSR 的存放期望和 [Social Science Reproduction Platform](https://www.socialsciencereproduction.org/) 的复现协议。`/audit-reproducibility` 负责证明数字可复现，本技能接着把第三方从零重跑所需的材料打包，**把仓库从「审计可复现性」推进到「产出存放物」**。

**核心原则：**陌生人只凭数据和 README 就能复现这份包，不需要隐性知识，也不必「去问作者」。每张表、每张图都要映射到生成它的确切脚本与行号。

## 何时使用

- **论文被接收时。**期刊数据编辑（AEA、REStud、JPE、EJ……）会在排版前要求符合 DCAS 的存放物。
- **上传到 openICPSR / Zenodo / Dataverse 之前。**先在本地建好目录树与 README，再通过网页上传。
- **投稿前试跑。**尽早发现「我没记下 Table 3 是哪来的」之类缺口，此时修复成本较低。
- **机密数据论文。**即使不能存放数据本身，也要提供受限数据说明和可在受限数据上运行的包。

## 输入

从 `$ARGUMENTS` 按顺序解析位置参数与可选的 `--docker`，分别将位置参数赋给 `manuscript_path` 与 `outputs_dir`，不要读取 shell 的位置参数。将仓库根目录赋给 `project_dir`，供 Phase 2 使用：

- `manuscript_path` —— 稿件路径（`.tex`、`.qmd`、`.md`、`.pdf`），必填，用作表／图清单的来源。校验文件存在、可读且扩展名受支持。
- `outputs_dir`（可选）—— 输出目录，默认为各语言流水线共用的 `output/`。也识别 `_targets/objects/`。若 `output/` 不存在，但存在 v2.6 之前的 `scripts/<lang>/_outputs/`，就使用后者并说明；否则校验目录存在且可读。
- `project_dir` —— 仓库根目录，必须是已存在、可读的目录。
- `--docker`（可选）—— 仅当显式传入时才转发给 `/capture-environment`，并要求生成 `Dockerfile`；未传入时不要求 `Dockerfile`。

缺少稿件、稿件路径或项目目录无效、出现第三个位置参数或未知选项时，停止并报告，不得猜测。

## 工作流

### Phase 0: 起飞前检查——探测语言与输出

1. 扫描 `scripts/R/*.R`（+ `renv.lock` / `DESCRIPTION`）、`scripts/stata/*.do`、`scripts/python/*.py`（+ `requirements.txt` / `environment.yml` / `pyproject.toml`），探测分析语言。项目可能**混用多种语言**，必须记录所有探测结果。
2. 定位 `outputs_dir` 与一键入口（`00_run_all.R`、`99_run_all.do`、`run.py`、`Makefile`）。若一个入口都没有，必须标出，因为 DCAS 要求总控脚本。
3. 若 `quality_reports/passports/<paper-slug>.yaml` 存在，加载它；其中 `claims:` 条目是 Phase 1 使用的权威表／图 → `source_file:source_line` 映射。

### Phase 1: 生成标准复现 README

写 `replication_package/README.md`，使用 AEA 模板和下列字段。无法推断的字段保留 `[FILL]`，绝不编造数据来源或授权条款。

- **概述／论文引文**：标题、作者和一句话摘要。
- **数据可得性声明**：逐个数据集说明 public / restricted / proprietary，以及是否在包内重新分发。这是 DCAS 中最常被拒的字段，必须写清楚。
- **数据集清单**：每个文件一行，表头为 `filename | description | source (URL/citation) | access (public / DUA / purchase) | license | provided in package? (Y/N)`。
- **计算需求**：操作系统、软件及版本（R / Stata / Python）、关键包、大致运行时长、内存，以及是否需要 HPC／集群。
- **逐步运行说明**：先给出调用总控脚本的一条命令，再列出预期产出。
- **表／图 → 脚本:行映射**：每个展品一行，字段为 `Exhibit | Program | Line | Output file`。有护照时从护照读取；否则在稿件中搜索 `\input{}` / `\includegraphics{}`，逐项追踪生成它的脚本。这张映射是复现者的操作依据，也是复现包的核心。

### Phase 2: 抓取计算环境

必须通过 `Skill` 工具调用 [`/capture-environment`](../capture-environment/SKILL.md)，只把 `"$project_dir"` 作为位置参数传入；仅当本技能显式收到 `--docker` 时，才转发该选项。不得把探测到的语言作为参数，也不得传入其他不受支持的参数。该调用不能由 shell 命令、阅读技能文档或直接生成文件替代。调用失败、超时、未返回明确完成状态，或任一预期环境产物缺失时，记录缺失项并停止；不得进入 Phase 4。

预期产物包括：

- **R** —— `renv::snapshot()` → `renv.lock`；`sessionInfo()` → `output/sessionInfo.txt`。
- **Python** —— `pip freeze` → `requirements.txt`（或导出 conda 的 `environment.yml`）；记录 `python --version`。
- **Stata** —— `creturn list` / `about` / `which` 列表 → `output/sessionInfo_stata.txt`，即 Stata 约定要求的环境记录；确认每个 `.do` 都钉住 `version NN`（依据 [`stata-code-conventions.md`](../../rules/stata-code-conventions.md)）。
- **容器（仅当显式指定 `--docker`）** —— 生成一个钉住基础镜像 + 语言版本的 `Dockerfile`。普通路径不把 `Dockerfile` 列为预期产物，其缺失不得触发失败闭锁。

### Phase 3: 打包前确认断言可复现

必须通过 `Skill` 工具调用 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md)，参数使用有名称的 `manuscript_path` 与 `outputs_dir`；若 YAML 存在，就按护照感知模式运行。不能用 shell 命令或自行审读代替这次技能调用。

- **调用失败、超时、未返回结构化判定或结果缺失：**停止并明确报告审计未完成；不得进入 Phase 4，缺失结果不能按 PASS 或 EXPLAINED 处理。
- **任何 FAIL**（超出容差且没有具名的替代解释）都**阻塞**打包。不得围绕无法复现的数字组装复现包；列出失败断言并停止。
- **EXPLAINED**（超出容差但有已记录的具名替代解释）允许继续；把该备注带入 README 的已知差异一节。
- 只有在技能调用成功、结果完整且为**全部 PASS / PASS + EXPLAINED** 时才进入 Phase 4。

### Phase 4: 组装目录树 + DCAS 检查清单

创建存放骨架。真实文件存在时复制或创建符号链接，否则保留 `[FILL]` 占位符：

```
replication_package/
├── README.md                # Phase 1
├── data/
│   ├── raw/                 # as-obtained (or a pointer + DUA note if restricted)
│   └── analysis/            # constructed analysis files
├── code/                    # numbered scripts + master script (00_run_all.* / 99_run_all.do)
└── output/                  # tables/, figures/, logs/, sessionInfo.txt (R) / sessionInfo_stata.txt (Stata), renv.lock / requirements.txt
```

随后生成 **DCAS 合规检查清单**（`replication_package/DCAS_checklist.md`），逐项检查：数据可得性声明齐备；每个数据集都有来源 + 访问方式 + 授权；总控脚本存在且可用一条命令运行；计算需求已写明；每张表／图都映射到 program:line；代码没有绝对路径／与机器相关的路径；任何随机步骤都设了种子；授权文件齐全，包括一份 BSD/MIT 等代码授权和一份数据使用声明。每项标为 PASS / FAIL / `[FILL]`。

### Phase 5: 机密数据的处理

依据 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md)，扫描清单中的受限、专有或含个人身份信息的输入，包括行政记录、IRS/Census RDC、专有面板和可链接的健康数据。

- **绝不把受限数据复制到 `replication_package/data/`。**用访问指针替代，写明提供方、申请／DUA 流程、获取成本和预计等待时间。
- 生成 `replication_package/data/access-restricted-data.md`，向复现者说明如何取得相同输入。
- 确认**代码仍照常随包交付**。即使数据不能存放，DCAS 也要求提供可在受限数据上运行的代码。还要确认任何提交的抽取结果在进入 `output/` 前已经过披露规避处理，例如单元格抑制／取整。

## 输出／报告格式

写 `quality_reports/replication_package_[paper-slug].md`：

```markdown
# Replication Package: [Paper Title]
**Date:** [YYYY-MM-DD]  **Languages:** [R / Stata / Python]  **Deposit target:** [openICPSR / Zenodo / Dataverse]

## DCAS checklist
| Item | Status |
|---|---|
| Data Availability Statement | PASS / FAIL / [FILL] |
| Dataset manifest (source · access · license) | ... |
| One-command master script | ... |
| Computational requirements | ... |
| Table/Figure → program:line map | ... |
| No machine-specific paths · seeds set | ... |
| Reproducibility audit (Phase 3) | PASS / EXPLAINED-only / FAIL (blocker) |
| Confidential-data note (if applicable) | ... |

## Skeleton built at
replication_package/  (tree + README + checklist)

## Open [FILL] items
[one line per unresolved field]
```

## 退出行为

- **清单各项全部 PASS（或 PASS + `[FILL]`）且审计为 PASS／仅 EXPLAINED：**退出码 0；打印目录树位置与所有待作者补全的 `[FILL]` 项。
- **任何审计 FAIL（Phase 3）：**退出码 1，立即停止打包，不存放无法复现的数字。
- **检测到受限数据但未生成获取说明：**退出码 1，并报告机密数据阻塞项；Phase 5 完成前不得继续打包。

## 交叉引用

- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 容差契约 + 护照 schema，即本技能打包前的上游核验。
- [`.codebuddy/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) —— Phase 3 的门禁，负责证明断言可复现。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— Phase 5 遵循的受限数据存放规则。
- [`templates/passport-template.yaml`](../../../templates/passport-template.yaml) —— 表／图 → program:line 映射的来源（若存在）。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) · [`.codebuddy/skills/stata-replication/SKILL.md`](../stata-replication/SKILL.md) —— 本技能打包这些 R / Stata 流水线的产出。
- [`.codebuddy/skills/simulation-study/SKILL.md`](../simulation-study/SKILL.md) —— 设了种子的蒙特卡洛输出按同样方式打包，种子 + 每次重复的原始结果应放进 `output/`。
- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md) —— 对 RCT，PAP 应与分析代码一起放入存放物。

## 本技能不做的事

- **不核验数字。**Phase 3 调用 `/audit-reproducibility` 完成核验。本技能只打包*已核验*的结果；遇到 FAIL 会停止，不会重新推导。
- **不上传到仓库。**它只创建本地目录树与 README；作者自行上传到 openICPSR / Zenodo / Dataverse 并获取 DOI。网页存放明确不在范围内。
- **不评判研究本身。**识别策略（DiD / event-study、IV、RCT、panel FE）是否站得住，由 `/review-paper` 审查。复现包可复现，不代表研究设计没有缺陷。
- **不给数据去标识化。**它会标记受限输入并拒绝存放，但不会对原始微观数据运行披露规避算法；那是作者和 RDC 的责任。
