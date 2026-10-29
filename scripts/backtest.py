#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""backtest.py —— 全仓库一致性与「当前仍然为真」的总门禁

迁移自 `scripts/backtest.sh`。改成 Python 的唯一原因：原版是 Bash 编排器，
在 Windows 上不可执行，而一个跑不起来的总门禁等于没有总门禁。逐门语义与
原版一致，不做增删。

十一门（编号沿用原 backtest.sh 的注释，便于与上游对照）
--------------------------------------------------------
  1 surface-sync        计数与枚举表 ↔ 磁盘实际内容
  2 skill-integrity     frontmatter ↔ 正文工具一致性、锚点、flag 一致性
  3 model-versions      没有把已被取代的模型当作现行（对照模型 SSoT）
  4 links               每个相对链接与标题锚点都能解析
  5 spec-conformance    每个 skill 符合 Agent Skills 规范
  6 staleness           推荐已过期、源/渲染不一致、时效性失效
  7 repo-hygiene        无「草稿当正式」、无根目录杂物、归档有说明
  8 derived-counts      可枚举断言（期刊、模式、阶段、片段）对照自身真源
  9 ledger-coverage     资格台账 ↔ 实际运行的检查，双向一致；
                        且 settings.json 里每个 hook 都指向真实存在的文件
                         （路径拼错会静默禁用一条 hook）
 10 hook-battery        用合成事件驱动守卫 hook，每个必须仍在它针对的
                        失败模式上变红 —— 第 9 门证明「接上了」，
                        这一门证明「还在起作用」
 11 portability-tests   路径、编码、行尾、git 输出在别的机器上仍然成立 ——
                        第 1~10 门证明「在这台机器上是对的」，这一门证明
                        「换一台机器也不会静默变成另一个答案」

关于第 11 门的状态：它有三种结果，不是两种。
  PASS     本机把每一条用例都跑到了
  PARTIAL  跑完了，但有一部分用例因为本机缺少对应机制而跳过。这是一次
           **有上限的** PASS：它只钉住了跑到的那些用例，跳过的那些什么都没
           证明。上限的具体数字与原因逐条打印，汇总里单列，绝不并进 PASS
  FAIL     有用例失败，或整套用例一条都没跑到（exit 2）—— 后者是「空扫描
           报绿」，本仓库最贵的 bug 类型，所以不是 PASS 也不是 SKIPPED

与原版的差异（均为可移植性，不降低标准）
----------------------------------------
  * 第 3 门是 Bash 脚本，无 POSIX shell 时记为 SKIPPED 并明确报告，
    绝不记为 PASS。
  * 第 10 门：有 POSIX shell 时跑上游 `hook-battery.sh`（全量用例）；
    否则跑 `check-hooks.py`（迁移关键子集）。两者都跑时结果取严。
  * 第 9/10 门读的是 `.codebuddy/settings.json`（迁移后位置）。
  * **第 11 门是本地新增的**，上游只有十门。原因是迁移把脚本与 hook 从 macOS
    搬到了真 Windows：上游的十门里没有一门会在「换个宿主」这件事上变红，而
    本项目已经因为宿主差异交过几次学费（`text=True` 按代码页解码、`/` 与 `\`
    混用、`python3` 是 Microsoft Store 存根）。第 11 门把这类缺陷固定成用例，
    并且**把本机跑不到的用例显式记成上限**，而不是让它们悄悄消失。

退出码：所有门退出码的最大值；2 表示编排器自身异常。
任何一门 SKIPPED 都不影响退出码，但会在汇总里单独列出 —— 静默跳过是
本仓库历史上最贵的 bug 类型。PARTIAL 同理：它是一次有上限的通过，
不影响退出码，但在汇总里单列，并写明上限是多少。

用法
----
    python scripts/backtest.py
    python scripts/backtest.py -v          # 打印每门的完整输出
    python scripts/backtest.py --only 7,10 # 只跑指定门
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PY = sys.executable


def _has_posix_shell() -> str | None:
    """返回一个可用的 POSIX shell 路径，没有则 None。

    注意 `shutil.which("bash")` 在 Windows 上可能命中 Git Bash，那是真实可用的；
    但本项目的 hook 与测试电池大量使用 `[[ ]]`、数组、`local`，必须是 bash 而非
    任意 sh，所以只认 bash。
    """
    return shutil.which("bash")


BASH = _has_posix_shell()


def run(argv: list[str], stdin_text: str | None = None) -> tuple[int, str]:
    env = dict(os.environ)
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env["CODEBUDDY_PROJECT_DIR"] = str(ROOT)
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    try:
        p = subprocess.run(
            argv,
            input=(stdin_text.encode("utf-8") if stdin_text is not None else None),
            capture_output=True,
            cwd=str(ROOT),
            env=env,
            timeout=900,
        )
    except FileNotFoundError:
        return 127, f"命令不存在：{argv[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"超时（900s）：{' '.join(argv)}"
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    return p.returncode, out


def ceiling_of(out: str) -> str | None:
    """第 11 门打出的一行「本机没跑到多少用例」，有则返回其正文。

    这是 `portability-tests.py` 与编排器之间的契约行，不是给人读的美文：
    前缀固定为 `portability-ceiling:`，冒号后是本机没执行的用例数与总数。
    读它，而不是去数输出里的 `skipped` 行——数文本会在格式改动那天静默返回
    0，而 0 恰好是「全都跑到了」的意思。
    """
    for line in out.splitlines():
        if line.startswith("portability-ceiling:"):
            return line.split(":", 1)[1].strip()
    return None


# (编号, 名称, 说明, 构造函数 -> argv 或 None(表示跳过原因), 跳过原因)
def gate_specs() -> list[dict]:
    g: list[dict] = []

    def py_gate(num, name, script, desc):
        path = HERE / script
        g.append({
            "num": num, "name": name, "desc": desc,
            "argv": [PY, str(path)] if path.is_file() else None,
            "skip": None if path.is_file() else f"脚本不存在：{path.name}",
        })

    py_gate(1, "surface-sync", "check-surface-sync.py", "计数/枚举表 ↔ 磁盘")
    py_gate(2, "skill-integrity", "check-skill-integrity.py", "skill 结构与工具一致性")
    py_gate(4, "links", "check-links.py", "相对链接与锚点")
    py_gate(5, "spec-conformance", "check-spec-conformance.py", "Agent Skills 规范")
    py_gate(6, "staleness", "check-staleness.py", "推荐过期/源渲染不一致")
    py_gate(7, "repo-hygiene", "check-repo-hygiene.py", "根目录卫生与归档说明")
    py_gate(8, "derived-counts", "check-derived-counts.py", "可枚举断言对照真源")
    py_gate(9, "ledger-coverage", "check-ledger-coverage.py", "台账覆盖 + hook 接线")
    py_gate(11, "portability-tests", "portability-tests.py", "路径/编码/行尾/git 输出可移植性")

    # 第 3 门：Bash 脚本
    mv = HERE / "check-model-versions.sh"
    if not mv.is_file():
        g.append({"num": 3, "name": "model-versions", "desc": "模型版本一致性",
                  "argv": None, "skip": f"脚本不存在：{mv.name}"})
    elif BASH is None:
        g.append({"num": 3, "name": "model-versions", "desc": "模型版本一致性",
                  "argv": None,
                  "skip": "该门是 Bash 脚本，本环境无 POSIX bash —— 未执行，不等于通过"})
    else:
        g.append({"num": 3, "name": "model-versions", "desc": "模型版本一致性",
                  "argv": [BASH, str(mv)], "skip": None})

    # 第 10 门：hook 电池
    battery = HERE / "hook-battery.sh"
    pybat = HERE / "check-hooks.py"
    if BASH is not None and battery.is_file():
        g.append({"num": 10, "name": "hook-battery", "desc": "守卫 hook 仍会在目标失败模式上变红",
                  "argv": [BASH, str(battery)], "skip": None,
                  "also": [PY, str(pybat)] if pybat.is_file() else None})
    elif pybat.is_file():
        g.append({"num": 10, "name": "hook-battery", "desc": "守卫 hook 仍会在目标失败模式上变红",
                  "argv": [PY, str(pybat)], "skip": None,
                  "note": "上游 hook-battery.sh 需 POSIX bash，本环境改跑 check-hooks.py（迁移关键子集）"})
    else:
        g.append({"num": 10, "name": "hook-battery", "desc": "守卫 hook 仍会在目标失败模式上变红",
                  "argv": None, "skip": "hook-battery.sh 与 check-hooks.py 都不存在"})

    g.sort(key=lambda d: d["num"])
    return g


def main() -> int:
    ap = argparse.ArgumentParser(description="全仓库总门禁")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印每门完整输出")
    ap.add_argument("--only", default="", help="只跑指定门编号，逗号分隔，如 7,10")
    args = ap.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}

    print("═══ BACKTEST：本仓库是否内部一致、且当前仍然为真？ ═══")
    print(f"仓库根  ：{ROOT}")
    print(f"解释器  ：{PY}")
    print(f"POSIX   ：{BASH or '不可用'}")
    print()

    specs = gate_specs()
    if only:
        specs = [s for s in specs if str(s["num"]) in only]

    results = []          # (num, name, status, rc, output)
    worst = 0
    for spec in specs:
        num, name, desc = spec["num"], spec["name"], spec["desc"]
        print(f"── 门 {num}：{name} — {desc} ──")

        if spec["argv"] is None:
            print(f"   SKIPPED：{spec['skip']}")
            results.append((num, name, "SKIPPED", None, spec["skip"] or ""))
            print()
            continue

        rc, out = run(spec["argv"])
        # 「also」：两个电池都跑时取更严重的
        if spec.get("also"):
            rc2, out2 = run(spec["also"])
            out = out + "\n--- check-hooks.py ---\n" + out2
            rc = max(rc, rc2)

        status = "PASS" if rc == 0 else "FAIL"
        # 通过但有上限：第 11 门跑完了，却有用例因本机缺机制而跳过。
        ceiling = ceiling_of(out) if rc == 0 else None
        if ceiling:
            status = "PARTIAL"
        worst = max(worst, rc)
        results.append((num, name, status, rc, ceiling or out))
        print(f"   {status}（退出码 {rc}）")
        if ceiling:
            print(f"   上限：{ceiling}")
        if spec.get("note"):
            print(f"   注：{spec['note']}")
        if args.verbose or rc != 0:
            for line in out.splitlines():
                print(f"   | {line}")
        print()

    # findings-validator 冒烟（原版的收尾步骤）
    if not only or "99" in only:
        vf = HERE / "validate-findings.py"
        if vf.is_file():
            print("── findings-validator 冒烟 ──")
            rc, out = run([PY, str(vf)], stdin_text="[]")
            worst = max(worst, rc)
            results.append((99, "findings-validator", "PASS" if rc == 0 else "FAIL", rc, out))
            print(f"   {'PASS' if rc == 0 else 'FAIL'}（退出码 {rc}）")
            if args.verbose or rc != 0:
                for line in out.splitlines():
                    print(f"   | {line}")
            print()

    # ---- 汇总 ----
    print("═" * 64)
    print(f"{'门':<4}{'名称':<22}{'结果':<10}")
    print("-" * 64)
    for num, name, status, rc, _ in results:
        rc_txt = "" if rc is None else f"rc={rc}"
        print(f"{num:<4}{name:<22}{status:<10}{rc_txt}")

    passed = sum(1 for r in results if r[2] == "PASS")
    failed = [r for r in results if r[2] == "FAIL"]
    skipped = [r for r in results if r[2] == "SKIPPED"]
    partial = [r for r in results if r[2] == "PARTIAL"]
    print("-" * 64)
    head = f"PASS {passed}   FAIL {len(failed)}   SKIPPED {len(skipped)}"
    if partial:
        head += f"   PARTIAL {len(partial)}"
    print(head)

    if skipped:
        print("\n未执行的检查（不代表通过）：")
        for num, name, _, _, why in skipped:
            print(f"  门 {num} {name}：{why}")

    if partial:
        # 上限也要说清是「多少」，否则这一行只是另一种沉默。
        print("\n有上限的通过（跑完了，但没钉住全部用例）：")
        for num, name, _, _, why in partial:
            print(f"  门 {num} {name}：{why}")

    if failed:
        print("\n失败明细：")
        for num, name, _, rc, out in failed:
            print(f"\n[门 {num}] {name}（退出码 {rc}）")
            for line in out.splitlines()[:60]:
                print(f"  {line}")
        print("\n═══ BACKTEST FAILED —— 交付前必须修复 ═══")
        return worst

    if skipped or partial:
        print("\n═══ BACKTEST PASSED（存在未执行或有上限的门，见上）═══")
    else:
        print("\n═══ BACKTEST PASSED —— 仓库新鲜且内部一致 ═══")
    return 0


if __name__ == "__main__":
    sys.exit(main())
