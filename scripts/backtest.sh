#!/usr/bin/env bash
# backtest.sh — forward to scripts/backtest.py.
#
# 这个文件**不再列举任何门禁**。清单的唯一真源是 `scripts/gate-manifest.py`，
# 执行者是 `scripts/backtest.py`。此前三段文字各自从本文件的 `run "..."` 行里
# 推导门禁清单（编排器跑它们、派生计数数它们、台账覆盖核对它们），于是加一门
# 要同时满足三处解析器的隐含假设，漏一处就是静默少算。
#
# 为什么还留一个 `.sh`：CI 的两个 workflow、`.githooks/pre-commit`、以及文档
# 与上游习惯都写 `./scripts/backtest.sh`。删掉它会把「跑门禁」这件事从 bash 用户
# 和从上游 fork 过来的人手里拿走。它只做转发，参数与退出码原样透传 ——
# 于是「两套编排器」变成「一个实现，两个入口」。
#
# 解释器：python3 优先，退回 python。Windows 上 `python3` 常常是 Microsoft Store
# 的 App Execution Alias —— `command -v` 找得到、执行时只打印一句提示并以 49
# 退出。本仓库的目标宿主就是 Windows，所以这里探一次能不能真的跑，而不是查名字。
set -uo pipefail

DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -z "${DIR:-}" ] || [ ! -d "$DIR" ]; then
    echo "backtest: cannot resolve script directory" >&2; exit 2
fi

PY=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys' >/dev/null 2>&1; then
        PY="$cand"; break
    fi
done
if [ -z "$PY" ]; then
    echo "backtest: no working python interpreter on PATH (tried python3, python)" >&2
    echo "  A gate suite that cannot start is not a passing gate suite." >&2
    exit 2
fi

exec "$PY" "$DIR/backtest.py" "$@"
