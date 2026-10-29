#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""stamp-render.py —— 记录并校验「哪个源生成了当前渲染产物」

迁移自 `scripts/stamp-render.sh`。改成 Python 的原因是可移植性，不是功能变化：

* 原版用 `shasum -a 256`，Windows Git Bash 默认没有 shasum（有的是 sha256sum），
  指纹算不出来时原版 exit 2；而在 CI 上它又是正常的，所以这个故障只在本地出现。
* 原版用 `cmp -s` 比较两个 HTML，Windows 上没有 cmp。

语义与退出码严格对齐上游：
  0  已盖戳
  1  REFUSING：guide/ 与 docs/ 的 HTML 不一致（stamp 存在的意义就是抓这个）
  2  文件缺失或无法计算指纹

用法
----
    python scripts/stamp-render.py            # 盖戳（渲染并同步之后运行）
    python scripts/stamp-render.py --check    # 只校验，不写文件

为什么要同时盖源和产物两个指纹：只盖源的话，「渲染了但忘了同步 docs/」
或「手工改了 HTML」都会让戳仍然匹配——那正是这个机制要防的两种失败。
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "guide" / "workflow-guide.qmd"
GUIDE = ROOT / "guide" / "workflow-guide.html"
DOCS = ROOT / "docs" / "workflow-guide.html"
STAMP = ROOT / ".render-stamp"


def fp(path: Path) -> str:
    """源/产物的内容指纹：sha256 前 16 位十六进制，**行尾归一成 LF 之后**再算。

    与上游 `shasum -a 256 | cut -c1-16` 在 LF 文件上完全一致，所以两版可互换运行，
    已有的 .render-stamp（在 macOS 上盖的）不会被这次迁移判定为失效。

    为什么必须先归一：`.gitattributes` 是 `* text=auto eol=lf`，所以仓库里存的是 LF，
    而 Windows 上的 Quarto 写出的是 CRLF。按原始字节算，戳记的是**产出这份产物的工作
    副本**，不是内容——一旦提交，任何一次全新 clone 拿到的是 LF，于是 `--check` 在一棵
    干净的树上报「产物被改过」。行尾属于检出策略，不是关于源的事实，不该进入指纹。
    """
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser(description="渲染产物指纹盖戳/校验")
    ap.add_argument("--check", action="store_true", help="只校验，不写文件")
    args = ap.parse_args()

    for p in (SRC, GUIDE, DOCS):
        if not p.is_file():
            print(f"stamp-render: 缺少文件 {p.relative_to(ROOT)}", file=sys.stderr)
            return 2

    # docs/ 应当是 guide/ 的副本。不一致就拒绝盖戳——这正是戳要抓的失败。
    if GUIDE.read_bytes() != DOCS.read_bytes():
        print("stamp-render: 拒绝盖戳 —— guide/ 与 docs/ 的 HTML 不一致。", file=sys.stderr)
        print("  先同步：Copy-Item guide/workflow-guide.html docs/workflow-guide.html",
              file=sys.stderr)
        return 1

    sh, gh = fp(SRC), fp(GUIDE)
    dh = fp(DOCS)

    expected = (f"guide/workflow-guide.html:{sh}:{gh}\n"
                f"docs/workflow-guide.html:{sh}:{dh}\n")

    if args.check:
        current = STAMP.read_text(encoding="utf-8") if STAMP.is_file() else ""
        if current.strip() == expected.strip():
            print(f"stamp-render: 指纹一致 source={sh}")
            return 0
        print("stamp-render: 指纹不一致 —— 渲染产物与源不同步，需要重新渲染。",
              file=sys.stderr)
        return 1

    STAMP.write_text(expected, encoding="utf-8")
    print(f"stamp-render: 已盖戳 source={sh} output={gh}（guide/docs 一致，两者均已盖戳）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
