#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""port-from-claude.py —— 把 Claude Code 目录迁移为 WorkBuddy 目录（可重复执行）

为什么是工具而不是一次性脚本
----------------------------
上游 `pedrohcgs/claude-code-my-workflow` 仍在更新。每次同步上游后，新增或改动
的 skills / agents / rules 都要重做同一套「机械适配」。把这套适配写成可重复
执行的工具，而不是手工 sed，是让这套模板能长期独立维护的前提。

它只做**机械可判定**的改写
--------------------------
1. 目录/路径        `.claude/` → `.codebuddy/`，`~/.claude` → `~/.workbuddy`
2. 项目指令文件名   `CLAUDE.md` → `CODEBUDDY.md`
3. 环境变量         `CLAUDE_PROJECT_DIR` → `CODEBUDDY_PROJECT_DIR`
4. 解释器           `python3` → `python`（跳过 shebang 行；Windows 上 python3
                    是 Microsoft Store 存根，执行返回 9009）

它**故意不做**的改写（这些必须逐文件人工判断，机械改会破坏语义）
--------------------------------------------------------------
* 模型名 `opus` / `sonnet` / `haiku` → WorkBuddy 只有 default/lite/reasoning
  三档，且模型池不同。映射关系取决于 agent 职责，见 .codebuddy/rules/model-routing.md。
* `/fork` 对话分叉 —— WorkBuddy 无此机制，需改写为「派发独立子代理」的等价流程。
* `Monitor` 工具 —— WorkBuddy 无此工具，需改写为轮询或子代理。
* 正文中文化 —— 属翻译决策，不是路径改写。
以上四类由人工精修，工具只在报告里列出残留清单，方便逐个收口。

用法
----
    python scripts/port-from-claude.py --dry-run    # 只报告，不写文件
    python scripts/port-from-claude.py              # 执行
    python scripts/port-from-claude.py --report     # 列出待人工处理的残留

安全约定
--------
* 只从 `.claude/` 读，只往 `.codebuddy/` 写。
* 目标已存在的文件**不覆盖**（保护已手工适配过的文件，如 settings.json、
  rules/_smoke.md、skills/hello、agents/ping.md）。
* 退出码：0 正常；1 源目录缺失；2 参数错误。
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / ".claude"
DST = ROOT / ".codebuddy"

# 需要迁移的子目录（.codebuddy 下同名）
SUBDIRS = ["rules", "agents", "skills", "references", "output-styles", "scripts"]

# 不随迁移走的文件：settings.json 由 WorkBuddy 版手工维护，格式语义不同
SKIP_FILES = {"settings.json"}

# 需要一起搬的顶层文档
TOP_FILES = ["WORKFLOW_QUICK_REF.md"]

# --- 机械改写规则：(正则, 替换, 说明) -------------------------------------
# 顺序敏感：`~/.claude` 必须早于 `.claude`，否则会被改成 `~/.codebuddy`，
# 而 WorkBuddy 的**用户级**目录实际叫 `~/.workbuddy`。
RULES: list[tuple[str, str, str]] = [
    (r"~/\.claude", "~/.workbuddy", "用户级目录"),
    (r"\.claude/", ".codebuddy/", "项目级目录"),
    (r"(?<![\w.])\.claude(?![\w])", ".codebuddy", "项目级目录（无斜杠写法）"),
    (r"CLAUDE_PROJECT_DIR", "CODEBUDDY_PROJECT_DIR", "环境变量"),
    (r"CLAUDE\.md", "CODEBUDDY.md", "项目指令文件名"),
]

PYTHON3_RE = re.compile(r"\bpython3\b")

# --- 待人工处理的残留：(正则, 说明) ---------------------------------------
MANUAL_PATTERNS: list[tuple[str, str]] = [
    (r"\bopus\b", "模型名 opus → reasoning/default/lite，需按职责判定"),
    (r"\bsonnet\b", "模型名 sonnet → default，需按职责判定"),
    (r"\bhaiku\b", "模型名 haiku → lite，需按职责判定"),
    (r"/fork\b", "对话分叉 /fork → WorkBuddy 无此机制，需改为派生子代理"),
    (r"\bMonitor\b", "Monitor 工具 → WorkBuddy 无此工具"),
]

TEXT_SUFFIXES = {".md", ".sh", ".json", ".yml", ".yaml", ".txt", ".py", ".R", ".tex"}


def transform(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    for pat, rep, label in RULES:
        text, n = re.subn(pat, rep, text)
        if n:
            counts[label] = counts.get(label, 0) + n

    # python3 → python，逐行处理以便跳过 shebang
    out_lines = []
    py_n = 0
    for line in text.splitlines(keepends=True):
        if line.startswith("#!") and "python3" in line:
            out_lines.append(line)          # shebang 保持原样，不影响显式调用
            continue
        new_line, n = PYTHON3_RE.subn("python", line)
        py_n += n
        out_lines.append(new_line)
    if py_n:
        counts["解释器 python3→python"] = py_n

    return "".join(out_lines), counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Claude Code → WorkBuddy 目录迁移")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写文件")
    ap.add_argument("--report", action="store_true",
                    help="列出需要人工判断的残留（模型名、/fork、Monitor）")
    args = ap.parse_args()

    if not SRC.is_dir():
        print(f"[致命] 源目录不存在：{SRC}", file=sys.stderr)
        print("       如果你已经完成迁移并删除了 .claude/，本工具无需再运行。",
              file=sys.stderr)
        return 1

    if args.report:
        return report()

    total = {"copied": 0, "kept": 0, "rules": {}}
    manual_hits: list[tuple[Path, int, str, str]] = []

    for sub in SUBDIRS:
        s = SRC / sub
        if not s.is_dir():
            continue
        for f in sorted(s.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(SRC)
            target = DST / rel
            if target.exists():
                total["kept"] += 1
                continue
            if f.suffix.lower() not in TEXT_SUFFIXES:
                if not args.dry_run:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)
                total["copied"] += 1
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                print(f"  [跳过] 非 UTF-8：{rel}")
                continue
            new_text, counts = transform(text)
            for k, v in counts.items():
                total["rules"][k] = total["rules"].get(k, 0) + v
            for pat, why in MANUAL_PATTERNS:
                for m in re.finditer(pat, new_text):
                    line_no = new_text.count("\n", 0, m.start()) + 1
                    manual_hits.append((rel, line_no, m.group(0), why))
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(new_text, encoding="utf-8")
            total["copied"] += 1

    for name in TOP_FILES:
        f = SRC / name
        if f.is_file() and not (DST / name).exists():
            text, counts = transform(f.read_text(encoding="utf-8"))
            for k, v in counts.items():
                total["rules"][k] = total["rules"].get(k, 0) + v
            if not args.dry_run:
                (DST / name).write_text(text, encoding="utf-8")
            total["copied"] += 1

    print(f"{'[dry-run] ' if args.dry_run else ''}迁移完成")
    print(f"  新写入文件数 ：{total['copied']}")
    print(f"  已存在跳过数 ：{total['kept']}（保护手工适配过的文件）")
    print("  机械改写统计 ：")
    for k, v in sorted(total["rules"].items(), key=lambda kv: -kv[1]):
        print(f"    {k:<24} {v}")
    print(f"  待人工处理   ：{len(manual_hits)} 处（用 --report 查看清单）")
    return 0


def report() -> int:
    """扫描 .codebuddy/ 下仍需人工判断的残留。"""
    if not DST.is_dir():
        print(f"[致命] 目标目录不存在：{DST}", file=sys.stderr)
        return 2
    hits: dict[str, list[str]] = {why: [] for _, why in MANUAL_PATTERNS}
    for f in sorted(DST.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if "hooks" in f.parts:      # hook 是上游原样代码，单独处理
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = f.relative_to(ROOT).as_posix()
        for pat, why in MANUAL_PATTERNS:
            for m in re.finditer(pat, text):
                line_no = text.count("\n", 0, m.start()) + 1
                hits[why].append(f"{rel}:{line_no}  {m.group(0)}")

    total = 0
    for why, items in hits.items():
        if not items:
            continue
        total += len(items)
        print(f"\n=== {why} —— {len(items)} 处 ===")
        for it in items:
            print(f"  {it}")
    if total == 0:
        print("无待人工处理的残留。")
    else:
        print(f"\n合计 {total} 处。这些不能用机械替换处理，必须逐条判断语义。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
