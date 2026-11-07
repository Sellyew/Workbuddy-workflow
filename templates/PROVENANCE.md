# 溯源

<!--
  复制到 quality_reports/PROVENANCE.md 并填写。不要放在根目录，否则仓库卫生门禁会失败。本文件要回答的是：数字虽然对上了，但究竟与什么对上了？
  协议：.codebuddy/references/provenance-and-ground-truth.md
-->

**状态：** [draft | frozen for release X.Y.Z]
**最近核验：** YYYY-MM-DD

## 参照物的角色

逐一列出每个单一真源，说明它的用途，并记录准确的 commit。版本号可能被重新标记，不能单独用来固定参照物；commit 不会变化。

| 参照物 | 角色 | 观察到的 ref |
| --- | --- | --- |
| `owner/canonical-package` | 统计与 API 的首要外部裁判 | HEAD `<sha>`；版本 X.Y.Z |
| `owner/second-implementation` | 更深层测试的来源 | HEAD `<sha>` |
| `owner/legacy` | 旧行为的来源 | HEAD `<sha>` |
| `owner/published-paper` | 实证验收套件 | HEAD `<sha>` |
| `owner/engineering-ref` | 工程参照（仅风格/架构） | HEAD `<sha>` |

**开始度量前，先声明参照物相互矛盾时采用哪一份：**

> 以 `<primary>` 为准。`<secondary>` 报错而 `<primary>` 警告的地方，以 `<primary>` 为准。

## 许可说明

记录每份参照物的许可。许可信息若有含糊之处，也要如实写明。

- `<ref>` 在其元数据里声明 `License: <X>`。
- *（值得记录的含糊例子：分类器说 Apache，而 `setup.py` 说 MIT。澄清之前，以 MIT 为准。）*

## 净室边界

- 可以阅读参照代码，以了解公开行为、测试、架构与风格。
- **不要复制实现代码**。确需复制或改编时，必须在下面记录源路径、commit、许可、涉及的行、理由，以及为什么这样使用与许可兼容。
- **生成的数值输出、清单、行为描述与公开文档，可以作为测试的外部裁判使用。**
- 可以在设计中借鉴工程参照的*模式*；代码片段仍受上述规则约束。

> 使用材料前必须先确认许可兼容。不得在不遵守 copyleft 条款的情况下，把 copyleft 文本或代码复制进采用宽松许可的仓库；否则应独立重新实现，或取得许可并记入台账。

## 产物台账

| 产物类别 | 允许的来源 | 复制政策 |
| --- | --- | --- |
| 契约文档 | 从观察到的行为原创综合 | 本仓库自有 |
| 参照锁定 | 公开仓库的 commit/版本元数据 | 本仓库自有 |
| fixture 输入 | 在此生成 | 自有；生成器已记录 |
| 参照的期望输出 | 从钉死的裁判生成 | 可作为测试的外部裁判 |
| 实现代码 | 在此新写 | 除非下面有一条记录，否则不得复制 |

## 容差登记表

| 比较 | 容差 | 为什么 |
| --- | --- | --- |
| `<estimate>` vs `<oracle>` | 相对 `1e-8` | 解析上恒等；超过此容差即为缺陷 |
| `<bootstrap SE>` vs `<oracle>` | 相对 `5e-2` | bootstrap 标准误的抽样噪声约为 SE/√(2(B−1))，B = 999 时约 2.2%；再翻一倍留余量。（只有两侧的种子和 RNG 流都对齐，`1e-3` 的容差才合理。） |

必须在比较**之前**确定容差。比较失败后才放宽容差，会使检验失去约束作用。若确需放宽，必须在这里记录为一次已批准的分歧。

> **R 提示：`all.equal` 的尺度陷阱。** 当目标量级低于 `tolerance` 时，`all.equal` 会静默退化成**绝对**比较。因此，小标准误的格子即使相对误差没有上界，也可能通过。请传 `scale = max(mean(abs(target)), .Machine$double.eps)`。

## 分歧台账

差异不一定都是 bug。详见 `inst/spec/divergence-kinds.csv`，也可参考下表。

| id | 种类 | 摘要 |
| --- | --- | --- |
| `F001-DIV001` | `behavioral-default` | 本移植默认 X；参照物默认 Y。已记录，不修 |
| `F002-DIV001` | `language-surface` | 该构造在目标语言中没有对应物 |
| `F003-DIV001` | `upstream-conflict` | 参照物相互矛盾；以 `<primary>` 为准 |

种类：`behavioral-default` · `language-surface` · `api-surface` · `internal-api` ·
`test-placement` · `upstream-conflict`。

## 未来的台账条目

每次经许可越过净室边界，都要在这里追加记录。
