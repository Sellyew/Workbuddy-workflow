---
name: lit-review
description: 结构化的文献检索 + 综述，含引文抽取、主题聚类与缺口识别。当用户说 "find papers on X"、"do a lit review"、"what's the literature on..."、"summarize what we know about..."、"where's the gap in this field"、"review recent work on Y" 时使用。产出一份可直接转成 BibTeX 引文的书面综述。用 WebSearch/WebFetch 获取近期成果。
description_zh: 结构化的文献检索 + 综述，含引文抽取、主题聚类与缺口识别。当用户说 "find papers on X"、"do a lit review"、"what's the literature on..."、"summarize what we know about..."、"where's the gap in this field"、"review recent work on Y" 时使用。产出一份可直接转成 BibTeX 引文的书面综述。用 WebSearch/WebFetch 获取近期成果。
argument-hint: "[topic, paper title, or research question] [--no-verify]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "WebFetch", "Agent", "Task"]
---

# 文献综述

围绕给定主题做一次结构化的文献检索与综述。

**输入：** `$ARGUMENTS` —— 一个主题、论文标题、研究问题，或要考察的现象。

---

## 步骤

1. **解析主题**，从 `$ARGUMENTS` 中提取。如果点名了某篇具体论文，就以它为锚点。

2. **检索相关研究**，使用可用的工具：
   - 检查 `master_supporting_docs/supporting_papers/` 里有没有已上传的论文
   - 用 `WebSearch` 找近期发表（若可用）
   - 用 `WebFetch` 访问工作论文库（若可用）
   - 读取项目里既有的任何 `.bib` 文件，看已有哪些论文

3. **把发现组织成这些类别：**
   - **理论贡献** —— 模型、框架、机制
   - **实证发现** —— 关键结果、效应量、数据来源
   - **方法创新** —— 新估计量、识别策略、推断方法
   - **悬而未决的争论** —— 文献中尚未解决的异议

4. **识别缺口与机会：**
   - 哪些问题仍未回答？
   - 什么数据或方法可能回应它们？
   - 哪些发现彼此冲突？
   - **支持有多独立？** 对你称为一致或已复现的任何发现，给出表面计数与独立计数——共用同一个实验、数据集、样本或研究团队的多个研究只算一次。
   - **反向的证据呢？** 对每个头条发现，检索零结果与失败的复现并报告出来，或者说明未找到，并给出所用检索词。

5. **抽取引文**，按 BibTeX 格式覆盖所有讨论到的论文。

6. **保存报告**到 `quality_reports/lit_review_[sanitized_topic].md`

---

## 输出格式

```markdown
# Literature Review: [Topic]

**Date:** [YYYY-MM-DD]
**Query:** [Original query from user]

## Summary

[2-3 paragraph overview of the state of the literature]

## Key Papers

### [Author (Year)] — [Short Title]
- **Main contribution:** [1-2 sentences]
- **Method:** [Identification strategy / data]
- **Key finding:** [Result with effect size if available]
- **Relevance:** [Why it matters for our research]

[Repeat for 5-15 papers, ordered by relevance]

## Thematic Organization

### Theoretical Contributions
[Grouped discussion]

### Empirical Findings
[Grouped discussion with comparison across studies]

### Methodological Innovations
[Methods relevant to the topic]

## Gaps and Opportunities

1. [Gap 1 — what's missing and why it matters]
2. [Gap 2]
3. [Gap 3]

## Suggested Next Steps

- [Concrete actions: papers to read, data to obtain, methods to consider]

## BibTeX Entries

```bibtex
@article{...}
```
```

---

## 落地后核验（强制，CoVe）

在把综述草稿交回用户之前，跑一遍 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 里的落地后核验协议。文献综述的幻觉风险**非常高**，因为 WebSearch 可能返回听起来合理却是编造的引文。CoVe 从架构上抓住这种情况。

### 步骤

1. **抽取断言**，从草稿中提取。每篇被引论文、每条转述的发现（"Smith 2019 shows X"）、每条否定性文献断言（"no prior work studies Y"）都是一条断言。
2. **为每条断言生成核验问题**。问题要具体：「Smith (2019, *JEL*) 第 3 节真的报告了 X 蕴含 Y 这个发现吗？发表处对吗？」
3. 通过 `Agent` 工具以 `subagent_type=claim-verifier` **生成 `claim-verifier`**，在独立上下文中——一次具名的 `Agent` 调用，而不是对话分叉，分叉会继承草稿。交给它：断言表、核验问题、源材料指针（论文 URL、DOI、`master_supporting_docs/` 路径）。**不要传草稿正文本身**——独立上下文的独立性才是 CoVe 生效的原因。
4. **对账：** 若核验者报 PASS，在输出末尾附上一个绿色的「落地后核验」块。若 PARTIAL，在 BibTeX 块里给无法核验的断言打上不确定标记。若 FAIL，在交回之前**删除或改写被推翻的引文**，用核验者给出的证据。

### 跳过条件

- `--no-verify` 参数 —— 用户为求速度主动退出。
- 用户交给你 ≤3 篇他们自己已经读过并确认的论文；对用户本人核过的内容，CoVe 是多余开销。

### 输出契约

在报告末尾追加一个「落地后核验」块（默认折叠）。格式见规则文档。

---

## 重要事项

- **对不确定性要诚实。** 若无法核验某条引文，就说明。
- **优先近期成果**（近 5-10 年），除非奠基性论文更早。
- **区分工作论文与已发表论文** —— 工作论文可能变。
- **不要编造引文。** 若对某篇论文的细节没把握，标出来让用户核验。落地后核验会自动抓住大部分编造；这条规则是兜底。
