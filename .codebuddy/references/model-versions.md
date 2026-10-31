<!-- CURRENT: default | lite | reasoning -->
<!-- 本平台的模型层是**三档**，不是具体型号：default / lite / reasoning。
     上游这一行原本写的是「Fable 5.1 | Opus 5.5 | Sonnet 5 | Haiku 4.5」，
     并配一张含价格、上下文长度、最低 CLI 版本的表格。那些事实属于 Claude Code，
     在本平台不成立；把它们留在这里，就是本仓库自己的门禁要抓的那种
     「把已失效的说法当作当前事实呈现」。 -->

# 当前模型档位（单一真源）

**最后核对：** 2026-10-29
**到期：** 2027-04-27 —— 过了这个日期，时效门禁会失败，直到重新核对为止。

本文件是**唯一**写明本平台模型档位的地方。模板里其余一切都应抽象地引用档位（「`reasoning` 档」「`lite` 档」），或者指到这里；**不要在任何地方硬编码模型型号**。

顶部那条机器可读的 `<!-- CURRENT: ... -->` 标记由检查器解析——改档位名就同步改它。

## 三档

| 档位 | 用来做什么 | 什么时候**不要**用 |
|---|---|---|
| `reasoning` | 高判断力：期刊编辑、审稿人、事实核查、对抗式批评、TikZ 空间推理 | 机械劳动（改名、格式转换、抽取）——付长程任务的价钱买单次判断 |
| `default` | 审读与批评的默认档：R 代码审查、版面审计、校对、AI 腔审计、Beamer↔Quarto 翻译 | 判断错一次代价高于跑一次代价的关卡（那些用 `reasoning`） |
| `lite` | 机械劳动：文件改名、引文格式转换、TikZ 抽取、文献库校验、查找替换 | 任何需要「读完整份材料再下结论」的活儿 |

**没有第四档。** 上游按四层 + `effort` 路由；本平台的三档是**选哪个模型**，另有
`effort`（`minimal`–`max`）作**同一档内的思考预算**。两根轴正交：代理可设 `effort`，
技能不可设。详见 [`../rules/model-routing.md`](../rules/model-routing.md)。

## 上游层级到本平台档位的映射

这张表只用于**读上游文档时做换算**，不是本仓库的配置——本仓库的配置就是 `model:` 里的三档。

| 上游层级 | 本平台 | 判断依据（不是名字，是职责） |
|---|---|---|
| Fable | `reasoning` | 上游把它留给人类亲自操盘的最难长程任务；本平台没有「第四个更贵的档」可对应，需要时就选 `reasoning` 并缩小上下文 |
| Opus | `reasoning` | 上游用它跑高判断力代理；本仓库的 9 个代理钉在这里 |
| Sonnet | `default` | 上游审读/批评的默认档；本仓库 8 个代理钉在这里 |
| Haiku | `lite` | 上游机械劳动档；本仓库 2 个代理钉在这里 |
| `effort: low/medium/high/xhigh/max` | **同名保留，但属于另一根轴** | 代理 frontmatter 的 `effort:` 会被读，并施加到子代理会话的思考预算；它不选模型，只调「想多深」。技能里写它无效 |

## 怎么改档位

改代理或技能 frontmatter 里的 `model:` 字段，取值只能是 `default` / `lite` / `reasoning`。

```yaml
---
name: quarto-fixer
model: default
---
```

写完跑一遍归一化脚本，确认没有残留的旧档位名：

```bash
python scripts/normalize-model-tiers.py --dry-run    # 应当报 0 个文件需要改
```

## 谁在把关

- `scripts/normalize-model-tiers.py`：把 `opus` / `sonnet` / `haiku` / `inherit` 归一化到三档，并删掉**技能**里无效的 `effort:`——代理的保留，那个字段是活的。幂等。
- `scripts/check-spec-conformance.py`：把 `effort` 标为「技能里无对应语义」的提示项——技能加载器不读它。（`model` **不在**这个名单里：技能写了它，加载器会拿它对模型目录校验。）
- `scripts/check-model-versions.sh`（上游原件）：在 POSIX bash 环境下解析本文件的 `<!-- CURRENT: ... -->` 标记。本仓库的档位名不含版本号，所以它在本仓库是**空转通过**；保留它是为了上游同步后仍然能跑。
