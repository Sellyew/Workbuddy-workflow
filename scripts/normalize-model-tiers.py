#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[WorkBuddy 适配] 把 Claude Code 的模型档位归一化到本平台的三档。

WorkBuddy 的子代理/技能 frontmatter 只认三档：
    default | lite | reasoning
而上游模板写的是 opus / sonnet / haiku（外加 inherit）。不换，字段就是无效噪音：
模型不会被路由，而读文件的人会以为它被路由了。

映射依据（不是拍脑袋，是职责对应）：
    opus    -> reasoning   高判断力：编辑、审稿人、事实核查、对抗式批评
    sonnet  -> default     审读与批评的默认档
    haiku   -> lite        机械劳动：改名、格式转换、抽取、校验
    inherit -> default     继承会话，等价于不钉

同时删除 `effort:` 字段：本平台没有 effort 轴（只由模型档位决定深度），
留着它会让读者以为存在一个实际不存在的成本杠杆。

`effort:` 起初只从技能里删，代理留着——理由是「上游的船队表按 effort 分层」。
2026-10-30 复核推翻了这个理由：引擎的代理元数据 schema
（`name`/`description`/`path`/`source`/`model`/`tools`/`color`）里没有 `effort`，
Effect Struct 会把未知键剥掉，所以代理文件里的 `effort:` 一个字都没被读过
（证据与命令见 `.codebuddy/references/platform-facts.md`）。留着它的实际效果是：
`agent-fleet.md` 用一整列「投入」让读者相信存在一个成本旋钮，而
`model-routing.md` 第 10 行写着「本平台没有 effort 字段」——两处自相矛盾。
现在两边都删，代理与技能一视同仁。

幂等：重复运行不改变任何东西。退出码 0 = 完成，1 = 有文件无法解析。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_MAP = {
    "opus": "reasoning",
    "sonnet": "default",
    "haiku": "lite",
    "inherit": "default",
}
VALID = {"default", "lite", "reasoning"}

MODEL_RE = re.compile(r"^(model:[ \t]*)([A-Za-z][\w.-]*)[ \t\r]*$", re.M)
# 行尾写 [ \t\r]* 而不是 [ \t]*：这些文件是 CRLF，`\r` 会挡在 `$` 前面，
# 用 [ \t]* 时整条正则匹配不上、脚本静默地一个文件都不改（已实测踩到）。
EFFORT_RE = re.compile(r"^effort:[ \t]*[\w.-]+[ \t\r]*(?:\r?\n|\Z)", re.M)
# 结尾写 (?:\r?\n|\Z) 而不是 \r?\n：frontmatter 切片的末尾**不含**闭合行的
# 那个 `\n`，所以当 `effort:` 是最后一个键时，切片以 `\r` 收尾、没有换行符。
# 只要求 \r?\n 会漏掉这类文件（16 个里漏了 12 个，已实测）。


def frontmatter_span(text):
    """(start, end) of the frontmatter body, or None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return 3, end


def process(path, drop_effort):
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    span = frontmatter_span(text)
    if span is None:
        return "no frontmatter", text, text
    s, e = span
    fm = text[s:e]

    def map_model(m):
        key, val = m.group(1), m.group(2)
        if val in VALID:
            return m.group(0)
        new = MODEL_MAP.get(val.lower())
        if new is None:
            return m.group(0)
        return key + new

    new_fm = MODEL_RE.sub(map_model, fm)
    note = []
    if new_fm != fm:
        note.append("model normalized")
        fm = new_fm
    if drop_effort and EFFORT_RE.search(fm):
        fm = EFFORT_RE.sub("", fm)
        # 切片**不含**闭合行前的那个换行（见 EFFORT_RE 上方的注释），所以当
        # `effort:` 是最后一个键时，删掉整行会在末尾**留下一个空行**，frontmatter
        # 以空行收尾。第一版就是这么干出 18 个「多了个空行」的 diff 的。
        # 规范形是「以最后一个键的文字收尾」，由 text[e:] 那个换行接上 `---`。
        fm = fm.rstrip("\r\n")
        note.append("dropped effort:")
    return ("; ".join(note) or "unchanged"), text, text[:s] + fm + text[e:]


def main():
    dry = "--dry-run" in sys.argv
    targets = []
    agents = os.path.join(ROOT, ".codebuddy", "agents")
    for name in sorted(os.listdir(agents)):
        if name.endswith(".md"):
            targets.append((os.path.join(agents, name), True))
    skills = os.path.join(ROOT, ".codebuddy", "skills")
    for name in sorted(os.listdir(skills)):
        p = os.path.join(skills, name, "SKILL.md")
        if os.path.isfile(p):
            targets.append((p, True))

    changed = 0
    for path, drop_effort in targets:
        note, old, new = process(path, drop_effort)
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        if note in ("no frontmatter", "unchanged"):
            continue
        changed += 1
        print(f"  {rel:<52} {note}")
        if not dry:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
    print(f"\n{changed} file(s) {'would change' if dry else 'changed'} "
          f"of {len(targets)} scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
