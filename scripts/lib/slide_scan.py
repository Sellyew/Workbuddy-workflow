#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slide_scan.py —— 幻灯片源码的「清扫」工具：先置空非内容，再按页切开。

为什么需要它
------------
本仓库有两个检查器要在幻灯片源码里数东西：引文键（INV-5）与彩色框（INV-7）。
两者都会撞上同一个问题——**源码里有很多看起来像内容、其实不是内容的东西**：

  * Pandoc 不解析代码里的引文。`` `@scope/pkg` `` 是字面文本，不是引用。
    `quality_score.py` 曾把它读成引文键，把指南钉在 85 分（见 CHANGELOG v3.0.1）。
  * TeX 的 `%` 之后是注释。`% \\cite{old-key}` 不是引用。
  * 代码块里的 `#` 是注释，不是 Markdown 标题，更不是新的一页。
  * 代码块里的 `::: {.keybox}` 是示例文本，不是真的框。

**置空而不是删除**，是为了保住字符偏移：行号、列号仍然对得上原文，
报错才能指回人去读的那一行。

与 `quality_score.py` 的关系
----------------------------
`quality_score.py` 里有一份等价的私有实现 `_blank_code()`，它带着 100/100 的资格
记录（见 `quality_reports/qualification/LEDGER.md`）。本模块不替换它——动一个已经
合格化的检查器要重跑资格，收益不抵风险。**但两份实现必须行为一致**：改动这里的
围栏正则时，请一并核对 `quality_score.py:402`。
"""

from __future__ import annotations

import re
from pathlib import Path


def blank_fenced_and_inline_code(text: str) -> str:
    """把围栏代码块与行内代码替换成等长空格，换行保留。"""
    def _blank(match: re.Match) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    # 围栏代码块：``` 或 ~~~，可带 info string（如 ```{python}、```r）。
    text = re.sub(
        r"(?ms)^[ \t]*(?:`{3,}|~{3,})[^\n]*\n.*?^[ \t]*(?:`{3,}|~{3,})[ \t]*$",
        _blank, text)
    # 行内代码：N 个反引号，由同样长度的反引号闭合。刻意不跨行——
    # DOTALL 下一个孤立的反引号会吞掉整篇文档（quality_score.py 里记着这次事故）。
    text = re.sub(r"(`+)(?!`)[^`\n]*?(?<!`)\1(?!`)", _blank, text)
    return text


def blank_tex_comments(text: str) -> str:
    """把 TeX 行内注释（未转义的 % 之后）置空，**长度与换行都保持原样**。

    `\\%` 是字面的百分号，不是注释起点；反斜杠自身也可能被转义（`\\\\%` 仍是注释）。

    长度必须逐字符相等：调用方靠字符偏移算行号（见 `line_of`）。第一版在这里
    对没有注释的行也补了一个换行，于是每行多出一个 `\\n`，所有报出的行号整体后移。
    这是「置空」类函数最容易犯的错——它在清理内容的同时改变了坐标。
    """
    out = []
    for line in text.splitlines(keepends=True):
        has_nl = line.endswith("\n")
        body = line[:-1] if has_nl else line
        cut = len(body)
        i = 0
        while i < len(body):
            if body[i] == "%":
                # 数一数前面连续的反斜杠：偶数个 → 这个 % 没被转义
                backslashes = 0
                j = i - 1
                while j >= 0 and body[j] == "\\":
                    backslashes += 1
                    j -= 1
                if backslashes % 2 == 0:
                    cut = i
                    break
            i += 1
        out.append(body[:cut] + " " * (len(body) - cut) + ("\n" if has_nl else ""))
    return "".join(out)


def blank_html_comments(text: str) -> str:
    """把 HTML 注释置空（`.qmd` 里常用 `<!-- ... -->` 写备忘）。"""
    def _blank(match: re.Match) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    return re.sub(r"(?s)<!--.*?-->", _blank, text)


TEX_FRAME_RE = re.compile(
    r"\\begin\{frame\}(?P<opts>\[[^\]]*\])?(?P<title>\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})?"
    r"(?P<body>.*?)\\end\{frame\}",
    re.DOTALL,
)


def split_tex_frames(text: str) -> list[tuple[str, int, str]]:
    """按 `\\begin{frame}…\\end{frame}` 切分，返回 [(标签, 起始行号, 帧正文)]。

    标签优先取 `\\begin{frame}{标题}` 的标题，其次帧内第一个 `\\frametitle{…}`，
    都没有则用帧序号。行号是帧开始那一行（1 起）。
    """
    frames: list[tuple[str, int, str]] = []
    for idx, m in enumerate(TEX_FRAME_RE.finditer(text), start=1):
        body = m.group("body") or ""
        title = (m.group("title") or "").strip()
        if title.startswith("{") and title.endswith("}"):
            title = title[1:-1].strip()
        if not title:
            ft = re.search(r"\\frametitle\s*\{(.{0,80}?)\}", body, re.DOTALL)
            if ft:
                title = re.sub(r"\s+", " ", ft.group(1)).strip()
        label = title or "第 %d 帧" % idx
        line = text.count("\n", 0, m.start()) + 1
        frames.append((label, line, body))
    return frames


QMD_HEADING_RE = re.compile(r"^(#{1,2})[ \t]+(?P<title>.+?)[ \t]*#*[ \t]*$", re.MULTILINE)


def split_qmd_slides(text: str) -> list[tuple[str, int, str]]:
    """按一/二级标题切分 RevealJS 页面，返回 [(标签, 起始行号, 页正文)]。

    RevealJS 里 `#` 是横向页、`##` 是纵向页，两者都是屏幕上的一页，所以都切。
    第一个标题之前的内容（YAML frontmatter 之后）也保留为一个片段，标签为
    「文首」——那里放彩色框同样是每页上限的一部分。
    """
    slides: list[tuple[str, int, str]] = []
    marks = list(QMD_HEADING_RE.finditer(text))
    if not marks:
        return [("全文", 1, text)]

    head = text[: marks[0].start()]
    if head.strip():
        slides.append(("文首", 1, head))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        label = re.sub(r"\s+", " ", m.group("title")).strip()
        line = text.count("\n", 0, m.start()) + 1
        slides.append((label, line, text[m.end(): end]))
    return slides


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def iter_files(roots: list[Path], suffix: str) -> list[Path]:
    """展开路径列表：目录递归取指定后缀，文件直接收（后缀不符也收，显式指定即认）。"""
    out: list[Path] = []
    for root in roots:
        if root.is_dir():
            out.extend(sorted(p for p in root.rglob("*" + suffix) if p.is_file()))
        elif root.exists():
            out.append(root)
    return out
