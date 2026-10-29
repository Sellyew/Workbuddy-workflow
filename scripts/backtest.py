#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""backtest.py —— 全仓库一致性与「当前仍然为真」的总门禁

迁移自 `scripts/backtest.sh`。改成 Python 的唯一原因：原版是 Bash 编排器，
在 Windows 上不可执行，而一个跑不起来的总门禁等于没有总门禁。逐门语义与
原版一致，不做增删。

十一门（清单在 `scripts/gate-manifest.py` —— 唯一真源；编号沿用上游
backtest.sh 的注释，便于与上游对照）
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
  * 第 10 门：POSIX 宿主上跑上游 `hook-battery.sh`（全量用例）**并**跑
    `check-hooks.py`，两者取严；Windows 宿主上电池无法判定（见清单里的
    `posix_reason`），只跑 `check-hooks.py` 并记为 PARTIAL，上限原因逐条打印。
  * 第 9/10 门读的是 `.codebuddy/settings.json`（迁移后位置）。
  * **第 11 门是本地新增的**，上游只有十门。原因是迁移把脚本与 hook 从 macOS
    搬到了真 Windows：上游的十门里没有一门会在「换个宿主」这件事上变红，而
    本项目已经因为宿主差异交过几次学费（`text=True` 按代码页解码、`/` 与 `\\`
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
import importlib.util
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
MANIFEST = HERE / "gate-manifest.py"


def load_manifest() -> list[dict]:
    """读门禁清单 —— 全套门禁的**唯一真源**（scripts/gate-manifest.py）。

    三段文字曾经各自从 `scripts/backtest.sh` 的正则里推导这份清单：本文件跑它们，
    `check-derived-counts.py` 数它们，`check-ledger-coverage.py` 核对它们有没有
    台账行。加一门要同时满足三处隐含假设，漏一处就是静默少算 —— 新门不进台账、
    计数不涨、两道门各自绿着。清单现在只是数据，三个消费者读同一份。

    文件名叫 `gate-manifest.py` （带连字符）无法按包名 import，所以走
    spec_from_file_location。读不到清单不是「零道门」，是 CANNOT RUN：
    空扫描报绿是本仓库最贵的 bug 类型。
    """
    spec = importlib.util.spec_from_file_location("_gate_manifest", MANIFEST)
    if spec is None or spec.loader is None:
        sys.exit(f"backtest: 无法加载门禁清单 {MANIFEST} —— 清单缺失时继续跑等于空扫描报绿")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    gates = getattr(mod, "GATES", None)
    if not gates:
        sys.exit(f"backtest: {MANIFEST.name} 里没有 GATES —— 清单格式变了，继续跑等于空扫描报绿")
    return gates


def _expand(tokens: list[str]) -> list[str]:
    return [t.replace("{PY}", PY).replace("{BASH}", BASH or "")
             .replace("{SCRIPTS}", str(HERE)) for t in tokens]


def _missing_script(argv: list[str]) -> str | None:
    """argv 点到的、位于 scripts/ 下的脚本里，第一个不在盘上的。"""
    for tok in argv:
        if tok.startswith(str(HERE)) and not os.path.isfile(tok):
            return os.path.basename(tok)
    return None


def gate_specs() -> list[dict]:
    out: list[dict] = []
    for m in load_manifest():
        e = {
            "num": m["num"], "name": m["name"], "desc": m["desc"],
            "scripts": [HERE / s for s in m["scripts"]],
            "argv": None, "also": None, "skip": None, "note": None, "ceiling": None,
        }

        # pre-commit 会在「没暂存任何 hook / settings / 电池本身」时设这个变量。
        # 它必须表现为 SKIPPED（一次没跑的检查），绝不是 PASS —— 让被跳过的电池
        # 显示成绿，正是本仓库历史上最贵的 bug 类型。
        if m["name"] == "hook-battery" and os.environ.get("BACKTEST_SKIP_HOOK_BATTERY") == "1":
            e["skip"] = ("BACKTEST_SKIP_HOOK_BATTERY=1：pre-commit 判定没有暂存的 hook、"
                         "settings 或电池本身，CI 会跑全量 —— 本次未执行，不等于通过")
            out.append(e)
            continue

        host_block = bool(m.get("posix_only")) and os.name == "nt"
        shell_block = m.get("requires") == "bash" and BASH is None

        # 候选顺序：能跑就跑全量 → 退到子集 → 跳过并说明。
        # 退到子集时，PARTIAL 的上限必须逐条点名「为什么这台机器判定不了」，
        # 否则这一行只是另一种沉默。
        if not (host_block or shell_block):
            argv, also = _expand(m["run"]), (_expand(m["also"]) if m.get("also") else None)
            if _missing_script(argv) is None:
                e["argv"], e["also"] = argv, also
                out.append(e)
                continue
            e["skip"] = f"脚本不存在：{_missing_script(argv)}"
            out.append(e)
            continue

        if m.get("fallback") and _missing_script(_expand(m["fallback"])) is None:
            e["argv"] = _expand(m["fallback"])
            if host_block:
                e["ceiling"] = m.get("posix_reason")
            else:
                e["note"] = "该门需要 POSIX bash，本机改跑 fallback（迁移关键子集）—— 未执行的部分不代表通过"
            out.append(e)
            continue

        e["skip"] = (m.get("posix_reason") if host_block
                     else "该门是 Bash 脚本，本环境无 POSIX bash —— 未执行，不等于通过")
        out.append(e)

    out.sort(key=lambda d: d["num"])
    return out


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
            out = out + f"\n--- 附加：{os.path.basename(spec['also'][-1])} ---\n" + out2
            rc = max(rc, rc2)

        status = "PASS" if rc == 0 else "FAIL"
        # 通过但有上限，两种来源：门自己打印的用例上限（第 11 门），
        # 或清单声明这条门在本宿主上判定不了、只跑了子集（第 10 门在 Windows 上）。
        ceiling = (ceiling_of(out) or spec.get("ceiling")) if rc == 0 else None
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
