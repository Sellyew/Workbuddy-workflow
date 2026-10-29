# 代理船队清单

18 个专项子代理，各自负责什么、运行在哪个模型层级（[`model-routing.md`](../rules/model-routing.md)），以及由哪个技能派发它。这让船队变得可读——当某个扇出型技能挑选一个透镜时，这就是它从中挑人的花名册。审读器是**只读**的（它们按 [`orchestration-schemas.md`](orchestration-schemas.md) 报告 `FINDING`）；只有修复者会编辑文件。

> **让本表与 `.codebuddy/agents/*.md` 的 frontmatter（`model:` / `effort:`）以及 `model-routing.md` 保持同步。** 表面同步门禁会数代理数量，但还不会逐行比对本表，所以新增代理或改层级时要更新它。（本文件是 `references/` 下的文件，因此它本身不算作一个代理。）

## 高判断层级 —— Opus 层

这批代理里错一个「看起来没问题」代价很高（一封 desk-reject、一条幻觉引用、一个带偏误的估计量被交付）。永远不要为省钱而降级（[`model-routing.md`](../rules/model-routing.md) 反模式）。四个门禁代理固定 `effort: high`，比 Opus 默认高一级；其余跑在 `medium`（Opus 默认——见 `model-routing.md` § effort）。

| 代理 | 投入 | 职责 | 读/写 | 感知审稿取向 | 派发方 |
|---|---|---|---|---|---|
| `editor` | high | 初审、审稿人遴选、编辑综合 | 只读 | 选择审稿取向 | `/review-paper --peer` / `--variance` |
| `domain-referee` | high | 实质审稿人（贡献、定位、外部效度） | 只读 | 是（6 分法分类） | `/review-paper --peer` |
| `methods-referee` | high | 方法论审稿人（按论文类型区分识别／推断） | 只读 | 是（6 分法分类） | `/review-paper --peer` |
| `claim-verifier` | high | 独立上下文 CoVe 核验者（引用、数字、新颖性） | 只读 | 否 | `/verify-claims`，`/lit-review` · `/research-ideation` · `/respond-to-referees` · `/review-paper --peer` 的落地后检查；幻觉门禁 |
| `domain-reviewer` | medium | 对幻灯片或稿件某节做领域实质审读（5 个透镜；**模板——需自行定制**） | 只读 | 否 | `/slide-excellence`、`/seven-pass-review`（方法透镜） |
| `quarto-critic` | medium | 对抗式 Beamer↔Quarto 一致性批评者 | 只读 | 否 | `/qa-quarto`、`/slide-excellence`（一致性） |
| `tikz-reviewer` | medium | 基于度量的 TikZ 碰撞／美观审查 | 只读 | 否 | `/slide-excellence`（若有 TikZ）、`/extract-tikz`、`/new-diagram` |
| `sim-reviewer` | medium | 蒙特卡洛审查（DGP／估计目标、MCSE、覆盖率对真值） | 只读 | 否 | `/simulation-study` |
| `verifier` | medium | 端到端编译／渲染／部署验证门禁 | 只读 | 否 | `/commit` |

## 审读／批评层级 —— Sonnet 层，effort: high

| 代理 | 职责 | 读/写 | 派发方 |
|---|---|---|---|
| `r-reviewer` | R 代码质量、可复现性、惯用法 | 只读 | `/review-r`、`/slide-excellence`（若有 R）、`/data-analysis` |
| `r-package-reviewer` | R 包的 CRAN 就绪度（DESCRIPTION／NAMESPACE／roxygen／testthat／政策） | 只读 | `/r-package-check` |
| `slide-auditor` | 视觉布局审查（溢出、字体、间距） | 只读 | `/slide-excellence`（`/visual-audit` 内联跑同样的检查） |
| `proofreader` | 语法、错字、溢出、术语 | 只读 | `/proofread`、`/slide-excellence`、`/seven-pass-review`（散文透镜） |
| `pedagogy-reviewer` | 叙事弧线、前置要求、算例、记号、节奏 | 只读 | `/pedagogy-review`、`/slide-excellence` |
| `humanize-auditor` | AI 腔调特征检测（10 类） | 只读 | `/humanize` |

## 应用／翻译层级 —— Sonnet 层，effort: medium

| 代理 | 职责 | 读/写 | 派发方 |
|---|---|---|---|
| `quarto-fixer` | 应用 `quarto-critic` 的差异、重新渲染、验证 | **写入** | `/qa-quarto` |
| `beamer-translator` | Beamer→Quarto 逐页翻译 | **写入** | `/translate-to-quarto` |

## 机械／投票层级 —— Haiku 层（当前 Haiku 不支持 effort 设置；`effort: low` 这个固定值适用于将来支持它的后继模型）

| 代理 | 职责 | 读/写 | 派发方 |
|---|---|---|---|
| `promote-memory-council` | 对 `[LEARN]` 提升做五批评者投票（通用性／时效性／冗余度／证据／格式） | 只读 | `/promote-memory` |

## 审稿取向分类法

只有审稿人（`domain-referee`、`methods-referee`）以及给它们派活的 `editor` 感知审稿取向。6 分法分类是：**STRUCTURAL · CREDIBILITY · MEASUREMENT · POLICY · THEORY · SKEPTIC**。`--peer` 抽 2 个；`--variance N` 抽 N 个（有放回，N≥3 时至少 1 个 SKEPTIC）；`--stress` 强制 SKEPTIC×2。取向在启动前的 `RUN_CONFIG` 里就已固定（审稿人是分叉出来的，无法在运行中被重新提问）。

## 交叉引用

- [`.codebuddy/rules/model-routing.md`](../rules/model-routing.md) —— 分层理由 + 不得降级的反模式。
- [`.codebuddy/rules/orchestrator-protocol.md`](../rules/orchestrator-protocol.md) —— 船队如何扇出、归并、裁决。
- [`.codebuddy/references/orchestration-schemas.md`](orchestration-schemas.md) —— 每个审读器返回的 `FINDING`／`SCORECARD` 形状。
