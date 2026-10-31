#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[WorkBuddy 适配] 上游同步体检：在 `git merge upstream/main` 之前，先看清会碰到什么。

为什么需要它
------------
本仓库是 `pedrohcgs/claude-code-my-workflow` 的中文 / WorkBuddy 原生分支。上游的任何一次
改进都值得吸收，但上游改的是一套 `.claude/` + 英文 + 四层模型档位的模板，而本仓库是
`.codebuddy/` + 中文 + 三档。于是每次同步都是一次**分类作业**：

  * 上游改了判定逻辑、本仓库没动过  -> 直接覆盖，越省越好；
  * 上游改了本仓库改造过的文件      -> 必须人工合并，覆盖会丢掉中文分支与安全改动；
  * 上游「重新引入」本仓库刻意删掉的文件 -> 直接删，不要合并。

跳过这一步的代价不是冲突（git 会告诉你冲突），而是**静默的覆盖**：本仓库给
`root-of-trust-guard.py` 加的保护、给 `check-derived-counts.py` 加的中文正则，
在 `git checkout upstream/main -- <file>` 之后一声不响地消失，而门禁仍然是绿的
——因为它检查的是「有没有断言」，不是「断言还在不在」。

只读：除了可选的 `git fetch`，不改工作区、不改索引、不提交。

退出码：0 = 无必须人工合并的文件；1 = 有；2 = 环境问题（无 upstream / git 不可用）。
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM_REF = "upstream/main"

# --- 分类表：与 UPSTREAM.md §4 必须保持一致 -----------------------------------
# （改这里就要改那里；两份不一致时，以 UPSTREAM.md 为准，因为那是给人读的契约。）

# 4.2 本仓库有实质改动，覆盖会丢东西
MUST_MERGE = {
    "scripts/check-derived-counts.py":   "计数正则的中文分支 + CODEBUDDY.md 表面",
    "scripts/check-surface-sync.py":     "COMPOUND_PHRASINGS 的 4 条中文断言",
    "scripts/check-skill-integrity.py":  "WorkBuddy 字段白名单 + 扫描根",
    "scripts/check-spec-conformance.py": "WB_FIELDS / INERT_FIELDS",
    "scripts/check-staleness.py":        "去掉 date 依赖 + 中文允许标记 + 分隔符规范化",
    "scripts/check-model-versions.sh":   "SURFACES 里的 CODEBUDDY.md",
    "scripts/check-repo-hygiene.py":     "ROOT_ALLOW 增加 CODEBUDDY.md / UPSTREAM.md",
    "scripts/check-links.py":            "本仓库无（占位：上游改动需人工确认）",
    "scripts/check-ledger-coverage.py":  "runner 间接调用 + 旧路径别名",
    ".codebuddy/hooks/root-of-trust-guard.py": "信任根扩到 .codebuddy（安全机制）",
    ".codebuddy/hooks/lib/hook-runner.sh":     "本仓库独有的统一入口",
    ".codebuddy/settings.json":                "事件命令指向 hook-runner.sh",
    ".codebuddy/rules/model-routing.md":       "按三档重写，effort 段按本平台改",
    ".codebuddy/rules/quality-gates.md":       "正文中文化，rubric 区块逐字节保留",
    "README.md":                               "全文中文 + 计数断言",
    "guide/workflow-guide.qmd":                "全文中文 + 计数断言 + Pattern 锚点",
    "docs/index.html":                         "落地页中文化",
    "CHANGELOG.md":                            "当期条目是中文的，且含发布清单数字",
    "TROUBLESHOOTING.md":                      "全文中文",
    ".github/CONTRIBUTING.md":                 "链接指向 CODEBUDDY.md",
    "quality_reports/qualification/LEDGER.md": "台账用例数与中文说明",
    "docs/translation-conventions.md":         "本仓库独有的中文化契约",
    "templates/skill-template.md":             "计数断言中文化",
    ".codebuddy/skills/commit/SKILL.md":       "清单复合断言中文化",
}

# 本地生成 / 渲染产物：上游的那一份对本仓库没有意义（路径与语言都不同），
# 永远本地重新生成，不要从上游取。
GENERATED = {
    ".render-stamp": "本地指纹，由 scripts/stamp-render.py 生成",
    "docs/workflow-guide.html": "quarto render 的产物，本地重新渲染",
    "guide/workflow-guide.html": "quarto render 的产物，本地重新渲染",
}

# 4.3 本仓库独有（上游没有）
LOCAL_ONLY = {
    "CODEBUDDY.md", "UPSTREAM.md",
    "docs/translation-conventions.md", "docs/starter-prompt.md",
    "scripts/backtest.py", "scripts/check-hooks.py", "scripts/normalize-model-tiers.py",
    "scripts/verify-count-gates.py", "scripts/sync-check.py", "scripts/port-from-claude.py",
    "scripts/stamp-render.py", "scripts/lib/py.sh", "scripts/backtest-report.md",
    ".codebuddy/WORKFLOW_QUICK_REF.md",
    ".codebuddy/skills/init-research-project/SKILL.md",
}

# 4.4 预期缺失：上游有、本仓库刻意没有。同步时被重新引入就删掉。
EXPECTED_ABSENT = [
    "CLAUDE.md",
    ".claude/",
]


def git(*args, check=False):
    res = subprocess.run(["git"] + list(args), cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or f"git {' '.join(args)} failed")
    return res


def classify(path):
    """把一个上游改动过的路径归到五类之一。

    顺序有意义：先判「本仓库刻意没有」，再判「本地生成」，再判「本仓库改造过」，
    最后才看「本地有没有这个文件」——否则一个上游新增的、恰好与本地改造同名的文件
    会被误判成 NEW-UPSTREAM。
    """
    p = path.replace(os.sep, "/")
    for absent in EXPECTED_ABSENT:
        if p == absent or p.startswith(absent):
            return "EXPECTED-ABSENT", "本仓库刻意没有；被重新引入就删掉"
    if p in GENERATED:
        return "GENERATED", GENERATED[p]
    if p in LOCAL_ONLY:
        return "LOCAL-ONLY", "本仓库独有；上游不应有同名文件"
    if p in MUST_MERGE:
        return "MUST-MERGE", MUST_MERGE[p]
    if not os.path.exists(os.path.join(ROOT, p)):
        return "NEW-UPSTREAM", "上游新增文件，可直接接收（除非与本地命名冲突）"
    if p.startswith(".codebuddy/skills/") and "/evals/cases/" in p:
        return "OVERWRITE-OK", "评测夹具（英文，不译）"
    if p.startswith(".github/workflows/"):
        return "OVERWRITE-OK", "CI 定义"
    if p in ("scripts/quality_score.py", "scripts/validate-findings.py",
             "scripts/validate-setup.sh", ".codebuddy/references/finding-schema.json"):
        return "OVERWRITE-OK", "无语言耦合的判定逻辑 / schema"
    if p.startswith("scripts/check-") and p.endswith(".py"):
        return "OVERWRITE-OK", "判定逻辑，未在本仓库改造（若上游改了本仓库改过的，请改 MUST_MERGE）"
    return "REVIEW", "未分类：人工判断"


def main():
    no_fetch = "--no-fetch" in sys.argv
    # 允许对着别的上游分支做同样的分类（例如预演一个还没合进 upstream/main 的 PR）：
    #   python scripts/sync-check.py --no-fetch --ref=upstream/some-branch
    # 直接改写模块级常量，后面所有用到它的地方自动跟着走——只改一处，
    # 避免「改了 6 个 f-string 漏掉第 7 个」这类静默不一致。
    global UPSTREAM_REF
    for arg in sys.argv[1:]:
        if arg.startswith("--ref="):
            UPSTREAM_REF = arg.split("=", 1)[1]

    if git("rev-parse", "--git-dir").returncode != 0:
        print("sync-check: 这里不是 git 仓库", file=sys.stderr)
        return 2
    remotes = git("remote").stdout.split()
    if "upstream" not in remotes:
        print("sync-check: 没有 upstream remote。先执行：", file=sys.stderr)
        print("  git remote add upstream https://github.com/pedrohcgs/claude-code-my-workflow.git",
              file=sys.stderr)
        return 2

    if not no_fetch:
        res = git("fetch", "upstream", "--tags")
        if res.returncode != 0:
            print(f"sync-check: git fetch 失败（可用 --no-fetch 跳过）:\n{res.stderr.strip()}",
                  file=sys.stderr)
            return 2
        print("sync-check: 已 fetch upstream")

    if git("rev-parse", "--verify", UPSTREAM_REF).returncode != 0:
        print(f"sync-check: 找不到 {UPSTREAM_REF}", file=sys.stderr)
        return 2

    ahead = git("rev-list", "--count", f"HEAD..{UPSTREAM_REF}").stdout.strip()
    behind = git("rev-list", "--count", f"{UPSTREAM_REF}..HEAD").stdout.strip()
    print(f"\n上游领先 {ahead} 个 commit，本仓库领先上游 {behind} 个。")

    if ahead == "0":
        print("同步状态：已追平上游。")
        return 0

    print("\n上游这些 commit 改了什么：")
    log = git("log", "--oneline", "--no-decorate", f"HEAD..{UPSTREAM_REF}").stdout.strip()
    for line in log.splitlines()[:25]:
        print(f"  {line}")
    if len(log.splitlines()) > 25:
        print(f"  … 另有 {len(log.splitlines()) - 25} 条，用 git log HEAD..{UPSTREAM_REF} 全看")

    files = git("diff", "--name-only", f"HEAD...{UPSTREAM_REF}").stdout.strip().splitlines()
    buckets = {}
    for f in files:
        verdict, why = classify(f)
        buckets.setdefault(verdict, []).append((f, why))

    order = ["MUST-MERGE", "REVIEW", "EXPECTED-ABSENT", "NEW-UPSTREAM",
             "GENERATED", "OVERWRITE-OK", "LOCAL-ONLY"]
    for verdict in order:
        rows = buckets.get(verdict)
        if not rows:
            continue
        print(f"\n── {verdict} ({len(rows)}) " + "─" * max(0, 46 - len(verdict)))
        for f, why in rows:
            print(f"  {f:<58} {why}")

    must = len(buckets.get("MUST-MERGE", [])) + len(buckets.get("REVIEW", []))
    print()
    if must:
        print(f"结论：{must} 个文件必须人工合并。不要用 `git checkout {UPSTREAM_REF} -- <file>` 覆盖它们。")
        print("下一步：逐条读 commit → 手工合并 → python scripts/backtest.py → "
              "python scripts/verify-count-gates.py")
        return 1
    print("结论：没有必须人工合并的文件，可以快进。仍需跑 backtest 与 verify-count-gates。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
