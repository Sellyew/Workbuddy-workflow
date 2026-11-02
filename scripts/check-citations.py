#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-citations.py —— INV-5（单一文献库）的机器检查：每个引文键都要有对应条目。

为什么需要它
------------
在此之前，一个拼错的引文键的后果是这样的：

  * xelatex 打一条 `Citation 'x' undefined` 警告，**退出码仍是 0**；
  * `quarto render` 的 citeproc 打一条 WARNING，**退出码仍是 0**；
  * 产出的 PDF / HTML 里印着 `(notinbib2026?)`，页面看起来是好的。

2026-10-31 的幻灯片线验收埋了 `\\cite{notinbib2026}`：三处都报了，但没有一处判失败。
只看退出码的人会以为那份幻灯片是干净的。评分模型给的 −15 分也只有在有人主动去算分
的时候才存在。**一条只出现在日志里的告警，等于没有告警。**

本脚本把这件事变成一个退出码。它跑得很早（渲染之前）、很快（纯文本），两侧都查：

  * `Slides/**/*.tex`：`\\cite` / `\\citep` / `\\citet` / `\\parencite` … 家族
  * `Quarto/**/*.qmd`：Pandoc 的 `@key` / `[@a; @b]` / `[-@a]` 语法

两处都先置空代码块与行内代码——Pandoc 不解析代码里的引文，`@scope/pkg` 是字面文本。
这个假阳性曾经把指南钉在 85/100（见 `lib/slide_scan.py` 的说明）。

用法
----
  python scripts/check-citations.py                  # 默认查 Slides/ 与 Quarto/
  python scripts/check-citations.py Slides/L1.tex    # 指定文件或目录
  python scripts/check-citations.py --bib other.bib

退出码
------
  0 = 所有键都能在文献库里解析到
  1 = 有解析不到的键（逐个列出 文件:行号 与键名）
  2 = 用法/输入错误（文献库读不到、参数不认）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import slide_scan as scan  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIB = ROOT / "Bibliography_base.bib"
DEFAULT_ROOTS = [ROOT / "Slides", ROOT / "Quarto"]

# TeX 侧的引文命令：\cite、\citep、\citet、\citealp、\citeauthor、\parencite、
# \textcite、\autocite、\footcite、\nocite … 一律以 cite 结尾，可带 * 与最多两个
# 可选参数（natbib 的 [pre][post]、biblatex 的 [page]）。
TEX_CITE_RE = re.compile(
    r"\\(?P<cmd>[a-zA-Z]*cite[a-zA-Z]*)\*?(?:\[[^\]]*\]){0,2}\{(?P<keys>[^{}]*)\}"
)

# Pandoc 的引文键：可带一个前缀 `-`（抑制作者名），键以字母数字或下划线开头，
# 内部可含 `- _ . : # $ % & + ? < > ~ /`。前置断言 `(?<![\w@])` 挡掉邮箱
# （`foo@bar.com` 里的 `@bar` 不是引文）。
QMD_CITE_RE = re.compile(r"(?<![\w@])-?@(?P<key>[A-Za-z0-9_][A-Za-z0-9_:.#$%&+?<>~/.-]*)")

# 句子末尾的标点不属于键名（Pandoc 也这么切）：`see @smith2020.` → `smith2020`
TRAILING_JUNK = ".,;:!?)"

BIB_ENTRY_RE = re.compile(r"@(?P<type>[A-Za-z]+)\s*[{(]\s*(?P<key>[^,\s{}]+)\s*,")
BIB_NON_ENTRY = {"string", "comment", "preamble"}

QMD_BIB_FIELD_RE = re.compile(r"^bibliography\s*:\s*(?P<value>.+)$", re.MULTILINE)


def load_bib_keys(bib: Path) -> set[str]:
    """从 .bib 里取出所有条目的键名。解析失败（读不到）由调用方转成退出码 2。"""
    text = bib.read_text(encoding="utf-8", errors="replace")
    return {
        m.group("key")
        for m in BIB_ENTRY_RE.finditer(text)
        if m.group("type").lower() not in BIB_NON_ENTRY
    }


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def collect_tex(text: str) -> list[tuple[int, str, str]]:
    """返回 [(行号, 键名, 命令名)]。已置空注释。"""
    text = scan.blank_tex_comments(scan.blank_fenced_and_inline_code(text))
    found: list[tuple[int, str, str]] = []
    for m in TEX_CITE_RE.finditer(text):
        for key in m.group("keys").split(","):
            key = key.strip()
            if not key or key == "*":
                # \nocite{*} 是「全引」，没有具体键
                continue
            found.append((line_of(text, m.start()), key, "\\" + m.group("cmd")))
    return found


def collect_qmd(text: str) -> list[tuple[int, str, str]]:
    """返回 [(行号, 键名, "@")]。已置空代码与 HTML 注释。"""
    text = scan.blank_fenced_and_inline_code(scan.blank_html_comments(text))
    found: list[tuple[int, str, str]] = []
    for m in QMD_CITE_RE.finditer(text):
        key = m.group("key").rstrip(TRAILING_JUNK)
        if not key:
            continue
        found.append((line_of(text, m.start()), key, "@"))
    return found


def qmd_bibliography_fields(text: str) -> list[tuple[int, str]]:
    """YAML frontmatter 里声明的 `bibliography:`。INV-5 要求它指向唯一那份库。"""
    end = text.find("\n---", 3)
    front = text[: end if end > 0 else 0]
    return [
        (line_of(front, m.start()), m.group("value").strip().strip("'\"[]"))
        for m in QMD_BIB_FIELD_RE.finditer(front)
    ]


def usage() -> None:
    print(__doc__.strip(), file=sys.stderr)


def main(argv: list[str]) -> int:
    bib = DEFAULT_BIB
    paths: list[Path] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            usage()
            return 0
        if arg == "--bib":
            if i + 1 >= len(argv):
                print("check-citations: --bib 需要一个路径", file=sys.stderr)
                return 2
            bib = Path(argv[i + 1])
            i += 2
            continue
        if arg.startswith("-"):
            print("check-citations: 不认识的选项 %s" % arg, file=sys.stderr)
            return 2
        paths.append(Path(arg))
        i += 1

    if not paths:
        paths = [p for p in DEFAULT_ROOTS if p.exists()]

    if not bib.exists():
        print("check-citations: 找不到文献库 %s" % bib, file=sys.stderr)
        print("  INV-5 规定库在仓库根目录、名字固定；本脚本不会自己去猜位置。",
              file=sys.stderr)
        return 2

    try:
        known = load_bib_keys(bib)
    except OSError as e:
        print("check-citations: 读不了文献库 %s: %s" % (bib, e), file=sys.stderr)
        return 2

    if not known:
        # 空库会让「每个键都能解析」变成「什么都匹配不到」——那是最坏的绿。
        print("check-citations: %s 里没有解析出任何条目，拒绝判为通过" % bib,
              file=sys.stderr)
        return 2

    tex_files = scan.iter_files(paths, ".tex")
    qmd_files = scan.iter_files(paths, ".qmd")
    files = sorted(set(tex_files) | set(qmd_files))

    if not files:
        print("check-citations: 没有找到 .tex 或 .qmd 文件（扫描了 %d 个路径）" %
              len(paths))
        return 0

    unresolved: list[tuple[Path, int, str, str]] = []
    per_file = 0
    for path in files:
        try:
            text = scan.read_text(path)
        except OSError as e:
            print("check-citations: 读不了 %s: %s" % (path, e), file=sys.stderr)
            return 2
        entries = collect_qmd(text) if path.suffix == ".qmd" else collect_tex(text)
        per_file += len(entries)
        for line, key, via in entries:
            if key not in known:
                unresolved.append((path, line, key, via))

        if path.suffix == ".qmd":
            for line, value in qmd_bibliography_fields(text):
                name = Path(value.split()[0]).name if value else ""
                if name and name != bib.name:
                    print("%s:%d   bibliography 指向 %s，而 INV-5 要求 %s"
                          % (rel(path), line, value, bib.name), file=sys.stderr)
                    return 1

    if not unresolved:
        print("check-citations: %d 个文件、%d 处引用，全部能在 %s 里解析到"
              % (len(files), per_file, bib.name))
        return 0

    print("\n引文键在 %s 里找不到条目（%d 处）：" % (bib.name, len(unresolved)),
          file=sys.stderr)
    by_key: dict[str, list[tuple[Path, int, str]]] = {}
    for path, line, key, via in unresolved:
        by_key.setdefault(key, []).append((path, line, via))
    for key in sorted(by_key):
        spots = by_key[key]
        where = "、".join("%s:%d" % (rel(p), ln) for p, ln, _ in spots)
        print("  %-28s %s  (%s)" % (key, where, spots[0][2]), file=sys.stderr)
        near = sorted(k for k in known if k.lower() == key.lower())
        if near:
            print("      %s 与库里的 %s 只差大小写——多半是拼写问题，不是缺条目"
                  % (key, near[0]), file=sys.stderr)

    print("\n修法：(1) 键名拼错了就改键；(2) 真缺文献就往 %s 补一条。"
          % bib.name, file=sys.stderr)
    print("      绝不要为了消掉这条报错，把无关的东西（包名、变量名）塞进文献库。",
          file=sys.stderr)
    return 1


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _force_utf8_output() -> None:
    """让输出与宿主代码页无关。

    管道里的 Python 在中文 Windows 上默认用 cp936 写 stdout；调用方（CI、测试、
    另一个脚本）按 UTF-8 解码时得到的全是乱码。同一条报错在 Linux 上可读、在
    Windows 上不可读，而**内容是对的**——这种缺陷只有人肉看一眼才会发现，
    所以在这里钉死编码，不靠环境变量。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    _force_utf8_output()
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # 解析异常必须可见，不能静默放行
        print("check-citations.py 内部错误: %s" % e, file=sys.stderr)
        sys.exit(2)
