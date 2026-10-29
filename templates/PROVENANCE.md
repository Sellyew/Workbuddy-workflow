# 溯源

<!--
  复制到 quality_reports/PROVENANCE.md 并填写（放在根目录的 PROVENANCE.md 会让仓库卫生门禁变红）。这是对「数字对上了——对上的是『什么』？」这个问题的回答。
  协议：.codebuddy/references/provenance-and-ground-truth.md
-->

**状态：** [draft | frozen for release X.Y.Z]
**最近核验：** YYYY-MM-DD

## 参照物的角色

逐一列出每个单一真源、它的角色，以及确切的 commit。只写版本号不够——
版本会被重新打标签，commit 不会。

| 参照物 | 角色 | 观察到的 ref |
| --- | --- | --- |
| `owner/canonical-package` | 统计与 API 的首要外部裁判 | HEAD `<sha>`；版本 X.Y.Z |
| `owner/second-implementation` | 更深层测试的来源 | HEAD `<sha>` |
| `owner/legacy` | 旧行为的来源 | HEAD `<sha>` |
| `owner/published-paper` | 实证验收套件 | HEAD `<sha>` |
| `owner/engineering-ref` | 工程参照（仅风格/架构） | HEAD `<sha>` |

**参照物相互矛盾时的优先级——在开始度量之前就声明：**

> 以 `<primary>` 为准。`<secondary>` 报错而 `<primary>` 警告的地方，以 `<primary>` 为准。

## 许可说明

记录每一份参照物的许可，包括那些诚实存在的含糊之处。

- `<ref>` 在其元数据里声明 `License: <X>`。
- *（值得记录的含糊例子：分类器说 Apache，而 `setup.py` 说 MIT——
  在澄清之前，以 MIT 为准。）*

## 净室边界

- 参照代码可以**读**，用来理解公开行为、测试、架构与风格。
- **不要复制实现代码**，除非下面有一条记录写明了：源路径、commit、
  许可、复制/改编的行、理由，以及一个与许可兼容的决定。
- **生成的数值输出、清单、行为描述与公开文档，可以作为测试的外部裁判使用。**
- 工程参照的*模式*可以在设计层面采纳；代码片段受同样的规则约束。

> 许可兼容性是一道门禁，不是脚注。把 copyleft 材料引入一个
> 宽松许可的仓库就是违规，无论它多有用。

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
| `<estimate>` vs `<oracle>` | 相对 `1e-8` | 解析恒等；比这更大的都是缺陷 |
| `<bootstrap SE>` vs `<oracle>` | 相对 `5e-2` | bootstrap 标准误的抽样噪声约为 SE/√(2(B−1))，B = 999 时约 2.2%；再翻一倍留余量。（`1e-3` 的容差只有在两侧种子/RNG 流都对齐时才站得住。） |

在比较**之前**把容差定下来。比较失败之后才放宽的容差，把证据变成了装饰；
若确实必须放宽，就在此把它记为一次已批准的分歧。

> **R 提示——`all.equal` 的尺度陷阱。** 当目标量级低于 `tolerance` 时，`all.equal`
> 会静默退化成**绝对**比较，于是小标准误的格子可以在无界相对误差下通过。
> 请传 `scale = max(mean(abs(target)), .Machine$double.eps)`。

## 分歧台账

并非每一处差异都是 bug。见 `inst/spec/divergence-kinds.csv`（或下表）。

| id | 种类 | 摘要 |
| --- | --- | --- |
| `F001-DIV001` | `behavioral-default` | 本移植默认 X；参照物默认 Y——已记录，不修 |
| `F002-DIV001` | `language-surface` | 该构造在目标语言里没有对应物 |
| `F003-DIV001` | `upstream-conflict` | 参照物相互矛盾；以 `<primary>` 为准 |

种类：`behavioral-default` · `language-surface` · `api-surface` · `internal-api` ·
`test-placement` · `upstream-conflict`。

## 未来的台账条目

每当在获得许可的情况下越过净室边界，就在这里追加。
