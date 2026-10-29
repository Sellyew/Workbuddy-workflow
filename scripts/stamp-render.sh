#!/usr/bin/env bash
# stamp-render.sh — forward to scripts/stamp-render.py.
#
# 这个文件**不再自己算指纹**。唯一的实现在 `scripts/stamp-render.py`，
# 那也正是 `scripts/check-staleness.py` 用来比对的那个 `fp()`：
# 两份实现只要漂一点，门禁就会在「盖戳的」和「校验的」之间来回翻。
#
# 为什么改掉原来的实现：它靠 `perl -pe 's/\r\n\z/\n/' | shasum -a 256` 算指纹。
# 注释里当时的理由是「有 shasum 的地方就有 perl，因为 shasum 本身就是 perl 脚本」——
# 这个等式在 Git for Windows 上不成立。本机实测（WorkBuddy 自带的 PortableGit）：
#   perl     → 缺失
#   shasum   → 缺失
#   python   → 有
# 于是文档、门禁报错、以及 `validate-setup.sh` 的下一步提示里让人敲的这条命令，
# 在 Windows 上只会得到 `perl: command not found` 和一句「指纹失败」。而盖戳失败
# 会让 staleness 门永远红着——首跑的人第一次改指南就卡死在这里。
#
# Python 3 本来就是本模板的必需项（`validate-setup.sh` 的 required tools），
# 拿它当唯一实现，两个入口就不会再漂。
#
# 解释器：与 backtest.sh 同一套探测 —— 不查名字，查能不能真的跑，因为 Windows 上
# `python3` 常是 Microsoft Store 的 App Execution Alias（找得到，执行退 49）。
set -uo pipefail

DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -z "${DIR:-}" ] || [ ! -d "$DIR" ]; then
    echo "stamp-render: cannot resolve script directory" >&2; exit 2
fi

PY=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys' >/dev/null 2>&1; then
        PY="$cand"; break
    fi
done
if [ -z "$PY" ]; then
    echo "stamp-render: no working python interpreter on PATH (tried python3, python)" >&2
    echo "  Python 3 is a required tool — see scripts/validate-setup.sh." >&2
    exit 2
fi

exec "$PY" "$DIR/stamp-render.py" "$@"
