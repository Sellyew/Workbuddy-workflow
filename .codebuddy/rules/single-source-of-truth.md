---
paths:
  - "Figures/**/*"
  - "Quarto/**/*.qmd"
  - "Slides/**/*.tex"
---

# 单一真源：执行协议

**Beamer `.tex` 文件是所有内容的权威来源。** 其余一切都是派生。

## SSOT 链

```
Beamer .tex (SOURCE OF TRUTH)
  ├── extract_tikz.tex → PDF → SVGs (derived)
  ├── Quarto .qmd → HTML (derived)
  ├── Bibliography_base.bib (shared)
  └── Figures/LectureN/*.rds → plotly charts (data source)

NEVER edit derived artifacts independently.
ALWAYS propagate changes from source → derived.
```

---

## TikZ 新鲜度协议（强制）

**在 Quarto 幻灯片中使用任何 TikZ SVG 之前，先确认它与当前 Beamer 源一致。**

### 差异检查流程

1. 从 Beamer `.tex` 文件读取 TikZ 块
2. 从 `Figures/LectureN/extract_tikz.tex` 读取对应块
3. 逐一比对每个坐标、标签、颜色、不透明度与锚点
4. 只要存在任何差异：从 Beamer 更新 `extract_tikz.tex`，重新编译，重新生成 SVG
5. 只有到这时，才能在 QMD 中引用该 SVG

### 何时重新提取

出现以下情况时，重新提取全部 TikZ 图：
- 自上次提取之后 Beamer `.tex` 文件被修改过
- 开始一次新的 Quarto 转换
- 有任何与 TikZ 相关的质量问题被报告
- 在任何包含 QMD 改动的提交之前

---

## 环境对齐（强制）

**在转换开始之前，每个 Beamer 环境都必须有对应的 CSS。**

1. 扫描 Beamer 源，列出所有自定义环境
2. 逐一对照你的主题 SCSS 文件
3. 只要有任何环境在 SCSS 中缺失，就在翻译之前先创建它

---

## 内容保真清单

```
[ ] Frame count: Beamer frames == Quarto slides
[ ] Math check: every equation appears with identical notation
[ ] Citation check: every \cite has a @key in Quarto
[ ] Environment check: every Beamer box has CSS equivalent
[ ] Figure check: every \includegraphics has SVG or plotly equivalent
[ ] No added content: Quarto does not invent slides not in Beamer
[ ] No dropped content: every Beamer idea appears in Quarto
```
