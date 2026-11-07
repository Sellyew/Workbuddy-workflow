---
name: lit-review
description: 结构化的文献检索 + 综述，含引文抽取、主题聚类与缺口识别。当用户说 "find papers on X"、"do a lit review"、"what's the literature on..."、"summarize what we know about..."、"where's the gap in this field"、"review recent work on Y" 时使用。产出一份可直接转成 BibTeX 引文的书面综述。用 WebSearch/WebFetch 获取近期成果。
description_zh: 结构化的文献检索 + 综述，含引文抽取、主题聚类与缺口识别。当用户说 "find papers on X"、"do a lit review"、"what's the literature on..."、"summarize what we know about..."、"where's the gap in this field"、"review recent work on Y" 时使用。产出一份可直接转成 BibTeX 引文的书面综述。用 WebSearch/WebFetch 获取近期成果。
argument-hint: "[topic, paper title, or research question] [--no-verify]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "WebFetch", "Agent", "Task"]
---

# 文献综述

围绕给定主题，系统地检索文献并形成综述。

**输入：** `$ARGUMENTS` —— 一个主题、论文标题、研究问题，或要考察的现象。

---

## 步骤

1. **解析主题。** 从 `$ARGUMENTS` 中提取主题；如果用户点名某篇论文，就以它为检索锚点。

2. **检索相关研究。** 根据环境选用可用工具：
   - 检查 `master_supporting_docs/supporting_papers/` 中是否有已上传的论文。
   - 若可用，用 `WebSearch` 查找近期发表的研究。
   - 若可用，用 `WebFetch` 访问工作论文库。
   - 读取项目已有的 `.bib` 文件，确认已经收录哪些论文。

3. **按以下类别组织发现：**
   - **理论贡献** —— 模型、框架、机制。
   - **实证发现** —— 关键结果、效应量、数据来源。
   - **方法创新** —— 新估计量、识别策略、推断方法。
   - **悬而未决的争论** —— 文献中尚未解决的异议。

4. **识别缺口与机会：**
   - 哪些问题仍未回答？
   - 哪些数据或方法可能回答这些问题？
   - 哪些发现彼此冲突？
   - **支持有多独立？** 对任何被称为一致或已复现的发现，同时给出表面计数和独立计数。共用同一个实验、数据集、样本或研究团队的多项研究只计一次。
   - **反向的证据呢？** 对每个头条发现，检索零结果和失败复现。报告找到的证据；若未找到，也要说明并列出所用检索词。

5. **抽取引文。** 用 BibTeX 格式收录所有讨论到的论文。

6. **保存报告**到 `quality_reports/lit_review_[sanitized_topic].md`。

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

把综述草稿交给用户前，必须运行 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 中的落地后核验协议。文献综述的幻觉风险**非常高**：WebSearch 可能返回看似合理、实际编造的引文，CoVe 通过独立核验来拦截这类问题。

### 步骤

1. **从草稿中抽取断言。** 每篇被引论文、每条转述的发现（"Smith 2019 shows X"）、每条否定性文献断言（"no prior work studies Y"）都计为一条断言。
2. **为每条断言生成核验问题。** 问题必须具体，例如：「Smith (2019, *JEL*) 第 3 节真的报告了 X 蕴含 Y 这个发现吗？发表处对吗？」
3. 使用 `Agent` 工具并设置 `subagent_type=claim-verifier`，在独立上下文中启动 **`claim-verifier`**。这必须是一次具名的 `Agent` 调用，不能使用会继承草稿的对话分叉。只向它提供断言表、核验问题和源材料指针（论文 URL、DOI、`master_supporting_docs/` 路径），**不要提供草稿正文**；CoVe 依赖的正是这种独立性。
4. **核对结果。** 核验者报告 PASS 时，在输出末尾附上绿色的「落地后核验」块；报告 PARTIAL 时，在 BibTeX 块中给无法核验的断言标出不确定性；报告 FAIL 时，依据核验者提供的证据，在交付前**删除或改写被推翻的引文**。

### 跳过条件

- 用户为求速度，主动使用 `--no-verify` 参数退出核验。
- 用户提供的论文 ≤3 篇，且本人已经读过并确认；对这类已核验内容，CoVe 属于多余开销。

### 输出契约

在报告末尾追加一个「落地后核验」块，默认折叠，格式见规则文档。

---

## 重要事项

- **如实说明不确定性。** 无法核验某条引文时，要明确告诉用户。
- **优先近期成果**（近 5-10 年），但奠基性论文可以更早。
- **区分工作论文与已发表论文**，因为工作论文仍可能变化。
- **不要编造引文。** 不确定论文细节时，标出来请用户核验。落地后核验能自动发现大部分编造，这条规则是最后一道兜底。
