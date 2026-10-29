---
name: deploy
description: 把 Quarto `.qmd` 幻灯片渲染为 HTML 并同步到 `docs/`，用于 GitHub Pages。用户说 "deploy"、"publish the slides"、"ship to pages"、"push the lecture live"、"render and publish" 时使用，或在 Quarto 改动需要上线之后使用。不用于仅本地渲染 Quarto——那种情况直接用 `quarto render`。
description_zh: 把 Quarto `.qmd` 幻灯片渲染为 HTML 并同步到 `docs/`，用于 GitHub Pages。用户说 "deploy"、"publish the slides"、"ship to pages"、"push the lecture live"、"render and publish" 时使用，或在 Quarto 改动需要上线之后使用。不用于仅本地渲染 Quarto——那种情况直接用 `quarto render`。
argument-hint: "[LectureN or 'all']"
allowed-tools: ["Read", "Bash"]
---

# 把幻灯片部署到 GitHub Pages

渲染 Quarto 幻灯片，并把所有文件同步到 `docs/`，供 GitHub Pages 部署。

## 步骤

1. **跑同步脚本：**
   - 若提供了 `$ARGUMENTS`（如 "Lecture4"）：`./scripts/sync_to_docs.sh $ARGUMENTS`
   - 若没有参数：`./scripts/sync_to_docs.sh`（同步全部讲次）

2. **核验部署：**
   - 检查 `docs/slides/` 里有 HTML 文件
   - 检查 `_files/` 目录被拷过去了（RevealJS 资源）
   - 检查 `docs/Figures/` 是从 `Figures/` 同步来的
   - 检查 `docs/files/code/` 里有 R 脚本（若 `scripts/R/` 里有的话）

3. **核验交互图表**（如适用）：
   - 在渲染后的 HTML 里 grep 交互式组件的数量
   - 确认数量与预期一致

4. **核验 TikZ SVG**（如适用）：
   - 检查所有被引用的 SVG 文件都存在于 `docs/Figures/LectureN/`

5. **在浏览器里打开**做目视核验：
   - `open docs/slides/LectureX_Name.html`          # macOS
   - `# xdg-open docs/slides/LectureX_Name.html`    # Linux
   - 确认幻灯片能渲染、图片能显示、导航可用

6. **向用户报告结果**

## 同步脚本做什么：
- 渲染 `Quarto/` 里的所有 `.qmd` 文件（跳过 `*_backup*` 文件）
- 把 HTML 与 `_files/` 目录拷到 `docs/slides/`
- 把 `Slides/` 里的 Beamer PDF 拷到 `docs/slides/`
- 用 rsync 把 `Figures/` 同步到 `docs/Figures/`
- 把每个 `scripts/R/*.R` 拷进 `docs/files/code/`（与幻灯片一并发布）
