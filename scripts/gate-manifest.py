#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate-manifest.py —— 门禁清单的唯一真源。

为什么它是一个独立模块，而不是写在 `backtest.py` 里
------------------------------------------------------
清单有三个消费者，此前各自从 `scripts/backtest.sh` 的文本里推导：

  * `scripts/backtest.py`        —— 跑这些门
  * `scripts/check-derived-counts.py` —— 数它们（「11 个门禁」这句话对不对）
  * `scripts/check-ledger-coverage.py` —— 核对每一条都在资格台账里有行

三处都在解析同一段 Bash：一个用 `^run "` 数行数，一个用同一条正则取脚本路径。
于是「加一门」要同时满足三个解析器的隐含假设，而任何一个没跟上都是**静默少算**：
新门不进台账、计数不涨、两道门各自绿着。这不是假设的失效方式——
`check-derived-counts.py` 的注释里记着 7-vs-8 那次漂移，正是这个形状。

所以清单搬到这里，变成**纯数据**：导入它不跑任何门、不开子进程、不碰网络。
`backtest.py` 只负责把数据变成 argv 并执行；另外两个消费者只读不执行。

字段
----
  num          门编号。沿用上游 `backtest.sh` 的编号，便于与上游对照；
               99 保留给编排器的收尾冒烟（不在本清单里）。
  name         报告里的短名。
  desc         一行说明，打印在门标题后面。
  scripts      这条门会**调用**的脚本文件名（相对 `scripts/`）。
               **与宿主无关**：没有 bash 的机器上第 3 门不执行，但它调用的
               脚本仍然是一个「注册在案、必须上台账」的检查。台账核对读这一列，
               绝不读 run/tokens —— 否则 Windows 上的台账会凭空少掉两条。
  run          真的执行时的 argv 模板。占位符：{PY} {BASH} {SCRIPTS}。
  requires     运行前提。"bash" 表示需要一个 POSIX bash；缺了就退到 fallback。
  fallback     前提不满足时的替代 argv（子集），可省。
  also         主命令之外**再跑一遍**的 argv，结果取严；可省。
  posix_only   该门依赖 POSIX 宿主机制（symlink、timeout(1)、事件里的 POSIX
               路径能被解释器解析）。为真时，Windows 宿主上退到 fallback 并把
               状态记成 PARTIAL —— 一次**有上限**的通过，原因逐条打印。
  posix_reason posix_only 为真时打印给用户的话。要写清「为什么在这台机器上
               判定不了」，而不是「跳过了」。
"""

from __future__ import annotations

# 占位符由 backtest.py 展开；这里不 import 任何东西，方便两个消费者只读数据。
GATES = [
    {
        "num": 1,
        "name": "surface-sync",
        "desc": "计数/枚举表 ↔ 磁盘",
        "scripts": ["check-surface-sync.py"],
        "run": ["{PY}", "{SCRIPTS}/check-surface-sync.py"],
    },
    {
        "num": 2,
        "name": "skill-integrity",
        "desc": "skill 结构与工具一致性",
        "scripts": ["check-skill-integrity.py"],
        "run": ["{PY}", "{SCRIPTS}/check-skill-integrity.py"],
    },
    {
        "num": 3,
        "name": "model-versions",
        "desc": "模型版本一致性（对照模型 SSoT；时效由第 6 门管）",
        "scripts": ["check-model-versions.sh"],
        "run": ["{BASH}", "{SCRIPTS}/check-model-versions.sh"],
        "requires": "bash",
    },
    {
        "num": 4,
        "name": "links",
        "desc": "相对链接与锚点",
        "scripts": ["check-links.py"],
        "run": ["{PY}", "{SCRIPTS}/check-links.py"],
    },
    {
        "num": 5,
        "name": "spec-conformance",
        "desc": "Agent Skills 规范",
        "scripts": ["check-spec-conformance.py"],
        "run": ["{PY}", "{SCRIPTS}/check-spec-conformance.py"],
    },
    {
        "num": 6,
        "name": "staleness",
        "desc": "推荐过期 / 源渲染不一致 / 时效失效",
        "scripts": ["check-staleness.py"],
        "run": ["{PY}", "{SCRIPTS}/check-staleness.py"],
    },
    {
        "num": 7,
        "name": "repo-hygiene",
        "desc": "根目录卫生与归档说明",
        "scripts": ["check-repo-hygiene.py"],
        "run": ["{PY}", "{SCRIPTS}/check-repo-hygiene.py"],
    },
    {
        "num": 8,
        "name": "derived-counts",
        "desc": "可枚举断言对照真源",
        "scripts": ["check-derived-counts.py"],
        "run": ["{PY}", "{SCRIPTS}/check-derived-counts.py"],
    },
    {
        "num": 9,
        "name": "ledger-coverage",
        "desc": "台账覆盖 + hook 接线",
        "scripts": ["check-ledger-coverage.py"],
        "run": ["{PY}", "{SCRIPTS}/check-ledger-coverage.py"],
    },
    {
        "num": 10,
        "name": "hook-battery",
        "desc": "守卫 hook 仍会在它针对的失败模式上变红",
        "scripts": ["hook-battery.sh", "check-hooks.py"],
        "run": ["{BASH}", "{SCRIPTS}/hook-battery.sh"],
        "also": ["{PY}", "{SCRIPTS}/check-hooks.py"],
        "requires": "bash",
        "fallback": ["{PY}", "{SCRIPTS}/check-hooks.py"],
        "posix_only": True,
        "posix_reason": (
            "hook-battery.sh 依赖三件 POSIX 宿主机制：建 symlink 的夹具、"
            "timeout(1) 驱动「git 卡住」的场景、以及事件 JSON 里的 POSIX 路径"
            "能被解释器直接解析。本机是 Windows，这三件都不成立——电池自己会把"
            "建不出夹具的用例记成 UNREACHABLE，剩下的仍会因宿主差异判错"
            "（同一棵脏树把事件 cwd 换成 C:/… 就正确变红，已对照验证）。"
            "所以本机只跑 check-hooks.py —— 迁移关键子集；全量用例由 POSIX CI 执行。"
        ),
    },
    {
        "num": 11,
        "name": "portability-tests",
        "desc": "路径/编码/行尾/git 输出可移植性",
        "scripts": ["portability-tests.py"],
        "run": ["{PY}", "{SCRIPTS}/portability-tests.py"],
    },
]
