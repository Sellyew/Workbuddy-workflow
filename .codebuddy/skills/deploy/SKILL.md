---
name: deploy
description: 把 Quarto `.qmd` 幻灯片渲染为 HTML 并同步到 `docs/`，用于 GitHub Pages。用户说 "deploy"、"publish the slides"、"ship to pages"、"push the lecture live"、"render and publish" 时使用，或在 Quarto 改动需要上线之后使用。不用于仅本地渲染 Quarto——那种情况直接用 `quarto render`。
description_zh: 把 Quarto `.qmd` 幻灯片渲染为 HTML 并同步到 `docs/`，用于 GitHub Pages。用户说 "deploy"、"publish the slides"、"ship to pages"、"push the lecture live"、"render and publish" 时使用，或在 Quarto 改动需要上线之后使用。不用于仅本地渲染 Quarto——那种情况直接用 `quarto render`。
argument-hint: "[LectureN or 'all']"
allowed-tools: ["Read", "Bash"]
---

# 把幻灯片部署到 GitHub Pages

先渲染 Quarto 幻灯片，再把所需文件同步到 `docs/`，交由 GitHub Pages 发布。

## 步骤

1. **运行同步脚本：**
   - 如果提供了 `$ARGUMENTS`（如 "Lecture4"），运行 `./scripts/sync_to_docs.sh $ARGUMENTS`。
   - 如果没有参数，运行 `./scripts/sync_to_docs.sh`，同步全部讲次。

2. **检查部署文件：**
   - 确认 `docs/slides/` 中已生成 HTML 文件。
   - 确认 `_files/` 目录已复制，其中包含 RevealJS 资源。
   - 确认 `docs/Figures/` 已与 `Figures/` 同步。
   - 如果 `scripts/R/` 中有 R 脚本，确认它们已复制到 `docs/files/code/`。

3. **检查交互图表**（如适用）：
   - 在渲染后的 HTML 中用 grep 统计交互式组件。
   - 确认实际数量符合预期。

4. **检查 TikZ SVG**（如适用）：
   - 确认所有被引用的 SVG 文件都存在于 `docs/Figures/LectureN/`。

5. **在浏览器中打开并检查：**
   - `open docs/slides/LectureX_Name.html`          # macOS
   - `# xdg-open docs/slides/LectureX_Name.html`    # Linux
   - 确认幻灯片正常渲染、图片正常显示、导航可以使用。

6. **向用户报告结果**

## 同步脚本做什么：
- 渲染 `Quarto/` 中的所有 `.qmd` 文件，但跳过 `*_backup*` 文件。
- 将 HTML 与 `_files/` 目录复制到 `docs/slides/`。
- 将 `Slides/` 中的 Beamer PDF 复制到 `docs/slides/`。
- 用 rsync 将 `Figures/` 同步到 `docs/Figures/`。
- 将每个 `scripts/R/*.R` 复制到 `docs/files/code/`，随幻灯片一起发布。
