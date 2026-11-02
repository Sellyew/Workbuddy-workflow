#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-box-density.py —— INV-7（每页最多 2 个彩色框）的机器检查。

为什么需要它
------------
INV-7 此前**只是散文**：`content-invariants.md` 写了一行，`slide-auditor` 的清单里
有一行，`visual-audit` 的说明里有一行。三处都是给模型看的，没有任何东西会去数。

2026-10-31 的幻灯片线验收埋了一页三个框。结果：`slide-auditor` 没有被派发，也没有
任何检查按 INV-7 报出它；**发现它的是像素度量**——那一页因此溢出了 26.5px。换一页
内容短一点的，框还在，溢出消失，这个缺陷就会安静地过关。

一条规则如果只有「有人认真读」才能生效，那它在匆忙的一轮里就是不存在的。

框的名单从哪来
--------------
从 `Quarto/theme-template.scss` 读，不在这里另立一份。SCSS 定义哪些类是彩色框，
检查器就数哪些——INV-1 已经要求配色两侧同步，名单没有第二个真源。
读不到名单时**退出码 2**，绝不返回「0 个违规」：一个匹配不到任何东西的检查器，
它的绿灯什么也不代表。

两侧都数
--------
  * `Slides/**/*.tex` —— 按 `\\begin{frame}…\\end{frame}` 分帧，数 `block` 家族
    （`block` / `alertblock` / `exampleblock`，经 `setbeamercolor` 上色）与任何以
    `box` 结尾的环境。
  * `Quarto/**/*.qmd` —— 按一/二级标题分页（RevealJS 里两者都是屏幕上的一页），
    数 `::: {.keybox}` 形式的 fenced div。

代码块、行内代码、HTML 注释、TeX 注释都先置空——代码里的 `::: {.keybox}` 是示例
文本，`#` 是注释而不是新的一页。

用法
----
  python scripts/check-box-density.py                # 默认查 Slides/ 与 Quarto/
  python scripts/check-box-density.py Quarto/L1.qmd
  python scripts/check-box-density.py --max 3        # 临时放宽上限
  python scripts/check-box-density.py --scss other.scss

退出码
------
  0 = 每页都不超过上限
  1 = 有页面超限（逐个列出 文件:行号、页标签、框数与类型）
  2 = 用法/输入错误（SCSS 读不到、名单为空、参数不认）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import slide_scan as scan  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCSS = ROOT / "Quarto" / "theme-template.scss"
DEFAULT_ROOTS = [ROOT / "Slides", ROOT / "Quarto"]
DEFAULT_MAX = 2  # INV-7

# SCSS 里定义彩色框的类：顶格或缩进写的 `.keybox {`、`.methodbox,` 等。
SCSS_BOX_CLASS_RE = re.compile(r"^\s*\.(?P<name>[a-z][a-z0-9-]*box)\b\s*[,{]", re.MULTILINE)

# QMD 的 fenced div：开 `::: {.keybox}` / `::: {.keybox .tight}` / `::: keybox`，
# 关是一行光秃秃的 `:::`。
QMD_DIV_OPEN_RE = re.compile(r"^(?P<fence>:{3,})[ \t]*(?P<rest>\{[^}]*\}|[A-Za-z][\w-]*)[ \t]*$",
                             re.MULTILINE)
QMD_CLASS_RE = re.compile(r"\.(?P<cls>[A-Za-z][\w-]*)")

# Beamer 侧：所有经 setbeamercolor 上色的 block 家族（Preambles/header.tex:104-105），
# 以及任何以 box 结尾的环境（\begin{keybox} 之类自定义盒）。
TEX_BLOCK_ENVS = ("block", "alertblock", "exampleblock")
TEX_BEGIN_RE = re.compile(r"\\begin\{(?P<env>[A-Za-z][\w*]*)\}")


def load_box_classes(scss: Path) -> set[str]:
    text = scss.read_text(encoding="utf-8", errors="replace")
    return {m.group("name") for m in SCSS_BOX_CLASS_RE.finditer(text)}


def count_qmd_slide(body: str, boxes: set[str]) -> dict[str, int]:
    """返回这一页里各类彩色框的个数。只在正文里数，代码已被置空。"""
    counts: dict[str, int] = {}
    for m in QMD_DIV_OPEN_RE.finditer(body):
        rest = m.group("rest")
        classes = QMD_CLASS_RE.findall(rest) if rest.startswith("{") else [rest]
        for cls in classes:
            if cls in boxes:
                counts[cls] = counts.get(cls, 0) + 1
    return counts


def count_tex_frame(body: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for m in TEX_BEGIN_RE.finditer(body):
        env = m.group("env").rstrip("*")
        if env in TEX_BLOCK_ENVS or env.endswith("box"):
            counts[env] = counts.get(env, 0) + 1
    return counts


def describe(counts: dict[str, int]) -> str:
    return ", ".join("%s ×%d" % (k, v) for k, v in sorted(counts.items()))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def main(argv: list[str]) -> int:
    scss = DEFAULT_SCSS
    limit = DEFAULT_MAX
    extra: set[str] = set()
    paths: list[Path] = []

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            print(__doc__.strip())
            return 0
        if arg == "--scss":
            if i + 1 >= len(argv):
                print("check-box-density: --scss 需要一个路径", file=sys.stderr)
                return 2
            scss = Path(argv[i + 1])
            i += 2
            continue
        if arg == "--max":
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                print("check-box-density: --max 需要一个非负整数", file=sys.stderr)
                return 2
            limit = int(argv[i + 1])
            i += 2
            continue
        if arg == "--box-class":
            if i + 1 >= len(argv):
                print("check-box-density: --box-class 需要一个类名", file=sys.stderr)
                return 2
            extra.add(argv[i + 1].lstrip("."))
            i += 2
            continue
        if arg.startswith("-"):
            print("check-box-density: 不认识的选项 %s" % arg, file=sys.stderr)
            return 2
        paths.append(Path(arg))
        i += 1

    if not paths:
        paths = [p for p in DEFAULT_ROOTS if p.exists()]

    if not scss.exists():
        print("check-box-density: 找不到 %s" % scss, file=sys.stderr)
        print("  框的名单以 SCSS 为准（INV-1 要求配色两侧同步）。找不到名单时本脚本不会"
              "退回一张写死的表——那会变成第二个真源。", file=sys.stderr)
        return 2

    try:
        boxes = load_box_classes(scss) | extra
    except OSError as e:
        print("check-box-density: 读不了 %s: %s" % (scss, e), file=sys.stderr)
        return 2

    if not boxes:
        # 名单空 = 每页永远是 0 个框 = 永远通过。这正是要拒绝的那种绿。
        print("check-box-density: 从 %s 里没有解析出任何彩色框类名" % scss,
              file=sys.stderr)
        return 2

    files = sorted(set(scan.iter_files(paths, ".tex")) | set(scan.iter_files(paths, ".qmd")))
    if not files:
        print("check-box-density: 没有找到 .tex 或 .qmd 文件（扫描了 %d 个路径）"
              % len(paths))
        return 0

    violations: list[tuple[Path, int, str, int, dict[str, int]]] = []
    pages = 0
    for path in files:
        try:
            text = scan.read_text(path)
        except OSError as e:
            print("check-box-density: 读不了 %s: %s" % (path, e), file=sys.stderr)
            return 2

        if path.suffix == ".qmd":
            text = scan.blank_html_comments(scan.blank_fenced_and_inline_code(text))
            units = [(label, line, count_qmd_slide(body, boxes))
                     for label, line, body in scan.split_qmd_slides(text)]
        else:
            text = scan.blank_tex_comments(scan.blank_fenced_and_inline_code(text))
            units = [(label, line, count_tex_frame(body))
                     for label, line, body in scan.split_tex_frames(text)]

        pages += len(units)
        for label, line, counts in units:
            total = sum(counts.values())
            if total > limit:
                violations.append((path, line, label, total, counts))

    if not violations:
        print("check-box-density: %d 个文件、%d 页，每页彩色框都不超过 %d 个（INV-7）"
              % (len(files), pages, limit))
        return 0

    print("\n每页彩色框超过 %d 个（INV-7，共 %d 页）：" % (limit, len(violations)),
          file=sys.stderr)
    for path, line, label, total, counts in violations:
        print("  %s:%d  「%s」 %d 个 —— %s" % (rel(path), line, label, total,
                                               describe(counts)), file=sys.stderr)
    print("\n框疲劳是设计问题，不是排版问题：把其中一两个改成正文段落、脚注，"
          "或者拆到下一页。", file=sys.stderr)
    print("上限是 %d，由 content-invariants.md 的 INV-7 规定；确实要更多时用 --max "
          "并在提交正文里说明理由。" % limit, file=sys.stderr)
    return 1


def _force_utf8_output() -> None:
    """让输出与宿主代码页无关（理由见 `check-citations.py` 的同名函数）。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    _force_utf8_output()
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:
        print("check-box-density.py 内部错误: %s" % e, file=sys.stderr)
        sys.exit(2)
