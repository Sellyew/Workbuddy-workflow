---
name: replication-package
description: 按 AEA Data and Code Availability Standard（DCAS）/ openICPSR / Social Science Reproduction Platform 的期望，组装一份可直接投稿的复现包——标准复现 README、数据集清单、计算环境抓取、表／图 → 脚本:行的映射，以及机密数据的存放方案。当用户说 "build the replication package"、"prepare the openICPSR deposit"、"make the AEA data and code package"、"DCAS compliance"、"assemble the deposit for the journal"，或在论文被接收、期刊的数据编辑索要复现包时使用。它**不是**数值核验器——打包前它会调用 `/audit-reproducibility` 确认断言可复现。
description_zh: 按 AEA Data and Code Availability Standard（DCAS）/ openICPSR / Social Science Reproduction Platform 的期望，组装一份可直接投稿的复现包——标准复现 README、数据集清单、计算环境抓取、表／图 → 脚本:行的映射，以及机密数据的存放方案。当用户说 "build the replication package"、"prepare the openICPSR deposit"、"make the AEA data and code package"、"DCAS compliance"、"assemble the deposit for the journal"，或在论文被接收、期刊的数据编辑索要复现包时使用。它**不是**数值核验器——打包前它会调用 `/audit-reproducibility` 确认断言可复现。
argument-hint: "[manuscript path] [outputs-dir] (outputs-dir defaults to output/)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent", "Task"]

---

# 复现包

产出经济学家在论文被接收时交给期刊的那份存放物：一棵目录树（`data/`、`code/`、`output/`、`README`）加一份 DCAS 合规检查清单，按 [AEA Data and Code Availability Standard](https://datacodestandard.org/)、openICPSR 的存放期望与 [Social Science Reproduction Platform](https://www.socialsciencereproduction.org/) 的复现协议来构建。本技能**把仓库从「审计可复现性」推进到「产出存放物」**——`/audit-reproducibility` 负责证明数字；本技能负责把第三方从零重跑所需的全部东西打包好。

**核心原则：** 一个陌生人拿着数据和 README 就能复现这份包——不依赖隐性知识，没有「去问作者」这一步。每一张表、每一张图都映射到产出它的确切脚本与行号。

## 何时使用

- **论文被接收时。** 期刊的数据编辑（AEA、REStud、JPE、EJ……）在论文排版前要求一份符合 DCAS 的存放物。
- **上传到 openICPSR / Zenodo / Dataverse 之前。** 先在本地把目录树与 README 建一次，再走网页上传。
- **投稿前试跑。** 趁修起来还便宜，抓住「我从没写下来 Table 3 是哪来的」这类缺口。
- **机密数据论文。** 即使数据本身不能存放，也要产出受限数据说明，以及一份可在受限数据上运行的包。

## 输入

- `$0` —— 稿件路径（`.tex`、`.qmd`、`.md`、`.pdf`）。必填（表／图清单的来源）。
- `$1` —— 输出目录。默认为 `output/`，各语言的流水线都把结果写在这里。可识别的替代项：`_targets/objects/`。若 `output/` 不存在、但存在 v2.6 之前的 `scripts/<lang>/_outputs/`，就用它，并说明这一点。

## 工作流

### Phase 0: 起飞前检查——探测语言与输出

1. 通过扫描 `scripts/R/*.R`（+ `renv.lock` / `DESCRIPTION`）、`scripts/stata/*.do`、`scripts/python/*.py`（+ `requirements.txt` / `environment.yml` / `pyproject.toml`）探测分析语言。项目可能是**多语言混用**的——把所有探测到的语言都记下来。
2. 定位输出目录（`$1`）与一键入口（`00_run_all.R`、`99_run_all.do`、`run.py`、`Makefile`）。若一个都没有，标记出来——DCAS 要求有一个总控脚本。
3. 若 `quality_reports/passports/<paper-slug>.yaml` 存在，加载它；其中 `claims:` 条目就是 Phase 1 所用的权威表／图 → `source_file:source_line` 映射。

### Phase 1: 生成标准复现 README

写 `replication_package/README.md`（AEA 模板，字段见下）。任何推不出来的字段留一个 `[FILL]` 标记——绝不编造数据来源或授权条款。

- **概述／论文引文** —— 标题、作者、摘要一句话。
- **数据可得性声明** —— 对每个数据集：public / restricted / proprietary，以及是否在包内重新分发。这是 DCAS 里被拒得最多的字段；要写明确。
- **数据集清单** —— 一张表，每个文件一行：`filename | description | source (URL/citation) | access (public / DUA / purchase) | license | provided in package? (Y/N)`。
- **计算需求** —— 操作系统、软件及其版本（R / Stata / Python）、关键包、大致运行时长、内存、是否需要 HPC／集群。
- **逐步运行说明** —— 先给调用总控脚本的那一条命令，再给预期产出。
- **表／图 → 脚本:行映射** —— 每个展品一行：`Exhibit | Program | Line | Output file`。若护照存在就从护照读；否则在稿件里 grep `\input{}` / `\includegraphics{}`，逐个追到产出它的脚本。这张映射是复现者要照着走的东西；它是这份包的心脏。

### Phase 2: 抓取计算环境

为每种探测到的语言生成依赖锁文件与环境快照。若可用，优先用 [`/capture-environment`](../capture-environment/SKILL.md)；否则直接产出：

- **R** —— `renv::snapshot()` → `renv.lock`；`sessionInfo()` → `output/sessionInfo.txt`。
- **Python** —— `pip freeze` → `requirements.txt`（或导出 conda 的 `environment.yml`）；记录 `python --version`。
- **Stata** —— `creturn list` / `about` / `which` 列表 → `output/sessionInfo_stata.txt`，即 Stata 约定所要求的环境记录；确认每个 `.do` 都钉住 `version NN`（依据 [`stata-code-conventions.md`](../../rules/stata-code-conventions.md)）。
- **容器（DCAS 对非简单环境推荐）** —— 生成一个钉住基础镜像 + 语言版本的 `Dockerfile`。

### Phase 3: 打包前确认断言可复现

运行 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) `$0 $1`（若 YAML 存在则按护照感知）。

- **任何 FAIL**（超出容差且没有具名的替代解释）→ **阻塞**：不要围绕无法复现的数字去组装包。摆出失败的那些断言并停下。
- **EXPLAINED**（超出容差但有已记录的具名替代解释）→ 允许；把该备注带进 README 的已知差异一节。
- **全部 PASS / PASS + EXPLAINED** → 进入 Phase 4。

### Phase 4: 组装目录树 + DCAS 检查清单

建出存放骨架（真实文件存在就复制／做符号链接；否则留 `[FILL]` 占位符）：

```
replication_package/
├── README.md                # Phase 1
├── data/
│   ├── raw/                 # as-obtained (or a pointer + DUA note if restricted)
│   └── analysis/            # constructed analysis files
├── code/                    # numbered scripts + master script (00_run_all.* / 99_run_all.do)
└── output/                  # tables/, figures/, logs/, sessionInfo.txt (R) / sessionInfo_stata.txt (Stata), renv.lock / requirements.txt
```

然后产出 **DCAS 合规检查清单**（`replication_package/DCAS_checklist.md`）：数据可得性声明齐备 · 每个数据集都有来源 + 访问方式 + 授权 · 总控脚本存在且一条命令可跑 · 计算需求已写明 · 每张表／图都映射到 program:line · 代码里没有绝对路径／与机器相关的路径 · 任何随机步骤都设了种子 · 授权文件（一份如 BSD/MIT 的代码授权 + 一份数据使用声明）。逐项标记 PASS / FAIL / `[FILL]`。

### Phase 5: 机密数据的处理

依据 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md)，扫描清单中受限、专有或含个人身份信息的输入（行政记录、IRS/Census RDC、专有面板、可链接的健康数据）。

- **绝不把受限数据拷进 `replication_package/data/`。** 用一个指针替代它：提供方、申请／DUA 流程、获取成本、预计等待时间。
- 生成 `replication_package/data/access-restricted-data.md` —— 复现者照它去获取同样输入的受限数据说明。
- 确认**代码照常随包交付**（DCAS 要求即使数据不能存放，也要有可在受限数据上运行的代码），并确认任何提交的抽取结果在进入 `output/` 之前已通过披露规避处理（单元格抑制／取整）。

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

- **清单各项全部 PASS（或 PASS + `[FILL]`）且审计为 PASS／仅 EXPLAINED：** 退出码 0；打印目录树位置与所有待作者补全的 `[FILL]` 项。
- **任何审计 FAIL（Phase 3）：** 退出码 1；打包立即停止。无法复现的数字不予存放。
- **检测到受限数据但未生成获取说明：** 退出码 1，并给出机密数据阻塞项——Phase 5 跑完之前，打包不能继续。

## 交叉引用

- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 容差契约 + 护照 schema（本技能所打包的上游核验）。
- [`.codebuddy/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) —— Phase 3 的门禁；证明断言可复现。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 驱动 Phase 5 的受限数据存放规则。
- [`templates/passport-template.yaml`](../../../templates/passport-template.yaml) —— 表／图 → program:line 映射的来源（若存在）。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) · [`.codebuddy/skills/stata-replication/SKILL.md`](../stata-replication/SKILL.md) —— 本技能所打包其产出的 R / Stata 流水线。
- [`.codebuddy/skills/simulation-study/SKILL.md`](../simulation-study/SKILL.md) —— 设了种子的蒙特卡洛输出也按同样方式打包（种子 + 每次重复的原始结果应放进 `output/`）。
- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md) —— 对 RCT，PAP 应与分析代码一起放进存放物。

## 本技能不做的事

- **不核验数字。** 那是 `/audit-reproducibility`（在 Phase 3 调用）。本技能打包的是*已核验*的结果；遇到 FAIL 它阻塞，而不是重新推导。
- **不上传到仓库。** 它只建本地目录树与 README；openICPSR / Zenodo / Dataverse 的上传与获取 DOI 由作者完成。网页存放刻意不在范围内。
- **不评判研究本身。** 识别策略（DiD / event-study、IV、RCT、panel FE）是否站得住，是 `/review-paper` 的问题。一份可复现的包仍然可能装着一个有缺陷的设计。
- **不给你的数据做去标识化。** 它会标记受限输入并拒绝存放它们；它不会对原始微观数据跑披露规避算法——那是作者（以及 RDC）的责任。
