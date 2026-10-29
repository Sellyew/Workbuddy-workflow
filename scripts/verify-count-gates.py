#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[WorkBuddy 适配] 反证：双语计数断言真的在把关，不是装饰。

为什么需要这个脚本
------------------
中文化把 `scripts/check-derived-counts.py` 与 `check-surface-sync.py` 抓取的英文
句子换成了中文。若只把正则加一条中文分支就算完事，没有任何证据说明它真的生效
——一个永不匹配的正则和一个匹配后判定正确的正则，在「全绿」的输出里长得一模一样。

这个脚本用**植入错误值**来区分二者：把某一处中文断言里的数字改成 99，跑对应门禁，
要求它**必须变红**；然后原样恢复。红不了，说明该断言已经脱离覆盖。

它只碰文中的数字，恢复靠精确字符串回写，不依赖 git（工作区里的译文未提交，
`git checkout` 会把整份文件打回英文）。

退出码：0 = 每个用例都变红了（覆盖成立）；1 = 有用例没变红（覆盖有洞）。
"""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (说明, 文件, 原文, 植入后, 期望变红的门禁)
CASES = [
    ("门禁总数（README）",
     "README.md", "11 个门禁", "99 个门禁", "check-derived-counts.py"),
    ("翻译阶段数（README）",
     "README.md", "12 个翻译阶段", "99 个翻译阶段", "check-derived-counts.py"),
    ("期刊画像数（README）",
     "README.md", "Top-5 期刊画像", "Top-9 期刊画像", "check-derived-counts.py"),
    ("清单复合句·代理数（README）",
     "README.md", "19 个代理", "99 个代理", "check-surface-sync.py"),
    ("清单复合句·钩子数（README）",
     "README.md", "11 个钩子", "99 个钩子", "check-surface-sync.py"),
    ("法则条数（CODEBUDDY.md）",
     "CODEBUDDY.md", "21 条法则", "99 条法则", "check-derived-counts.py"),
    ("阶梯级数（CODEBUDDY.md）",
     "CODEBUDDY.md", "7 级阶梯", "99 级阶梯", "check-derived-counts.py"),
    ("七遍透镜数（seven-pass-review）",
     ".codebuddy/skills/seven-pass-review/SKILL.md", "7 个独立上下文子代理",
     "99 个独立上下文子代理", "check-derived-counts.py"),
    ("钩子用例数（指南）",
     "guide/workflow-guide.qmd", "312 个用例，秒级运行", "99 个用例，秒级运行",
     "check-derived-counts.py"),
    ("模式数（指南）",
     "guide/workflow-guide.qmd", "19 个模式构成参考书架", "99 个模式构成参考书架",
     "check-derived-counts.py"),
    ("TikZ 片段数（指南）",
     "guide/workflow-guide.qmd", "8 个开箱即用的 TikZ 片段", "99 个开箱即用的 TikZ 片段",
     "check-derived-counts.py"),
    ("落地页门禁数（docs/index.html）",
     "docs/index.html", "11 个门禁", "99 个门禁", "check-derived-counts.py"),
]


def run(gate):
    return subprocess.run([sys.executable, os.path.join(ROOT, "scripts", gate)],
                          capture_output=True, text=True, cwd=ROOT)


def main():
    rows, holes = [], []
    for label, rel, old, new, gate in CASES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            rows.append((label, "SKIP", "file missing"))
            continue
        with io.open(path, encoding="utf-8", newline="") as fh:
            original = fh.read()
        if old not in original:
            # 不是「通过」，是「找不到可植入的锚点」——同样说明该站点不在覆盖里。
            rows.append((label, "NO-ANCHOR", f"'{old}' not found in {rel}"))
            holes.append(label)
            continue
        planted = original.replace(old, new, 1)
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(planted)
            res = run(gate)
        finally:
            with io.open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(original)
        if res.returncode == 0:
            rows.append((label, "MISSED", f"{gate} stayed green on a planted 99"))
            holes.append(label)
        else:
            # 取第一行含 MISMATCH / asserts 的输出作为证据，便于贴进审计报告。
            ev = ""
            for line in (res.stdout + res.stderr).splitlines():
                low = line.lower()
                if "mismatch" in low or "asserts" in low or "ungated" in low:
                    ev = line.strip()[:96]
                    break
            rows.append((label, "RED", ev or f"{gate} rc={res.returncode}"))

    w = max(len(r[0]) for r in rows) + 2
    print(f"{'用例'.ljust(w)}{'结果':<12}证据")
    print("-" * (w + 60))
    for label, verdict, ev in rows:
        print(f"{label.ljust(w)}{verdict:<12}{ev}")
    print()
    if holes:
        print(f"{len(holes)} HOLE(S) — 这些中文断言已脱离覆盖：")
        for h in holes:
            print(f"  - {h}")
        return 1
    print(f"ALL {len(rows)} CASES GO RED — 每条中文计数断言都在把关。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
