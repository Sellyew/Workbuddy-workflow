#!/usr/bin/env bash
# hook-runner.sh —— WorkBuddy hook 统一入口
#
# 职责（三件，只做这三件）：
#   1. 解释器探测：Windows 上 `python` 可能是 Microsoft Store 存根（返回 9009），
#      必须用 `-c` 真实执行探测，不能用 `command -v` 判断。
#   2. 环境变量注入：同时导出 CODEBUDDY_PROJECT_DIR 与 CLAUDE_PROJECT_DIR（兼容层），
#      使既有 hook 脚本无需修改即可工作。
#   3. UTF-8 强制：Windows cp936 控制台下中文输出会抛 UnicodeEncodeError，
#      被 hook 内部的 except 吞掉后表现为"提示消失"。
#
# 用法（在 .codebuddy/settings.json 中注册）：
#   bash "$CODEBUDDY_PROJECT_DIR/.codebuddy/hooks/hook-runner.sh" <hook 文件名> [参数...]
#
# 退出码策略：解释器缺失时 exit 0（fail-open）。hook 不可用绝不允许阻断会话，
# 但必须在 stderr 留下可诊断的一行——静默失败是本仓库历史上最贵的 bug 类型。

set -uo pipefail

# --- 1. 由脚本自身位置推导仓库根，不依赖调用方 cwd ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

export CODEBUDDY_PROJECT_DIR="${CODEBUDDY_PROJECT_DIR:-$ROOT}"
export CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$ROOT}"

# --- 2. UTF-8 ---
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# --- 3. 参数 ---
HOOK="${1:-}"
if [ -z "$HOOK" ]; then
  echo "hook-runner: 缺少 hook 文件名参数（期望形如 git-guardrails.py）" >&2
  exit 0
fi
shift

HOOK_PATH="$ROOT/.codebuddy/hooks/$HOOK"
if [ ! -f "$HOOK_PATH" ]; then
  echo "hook-runner: hook 文件不存在：$HOOK_PATH" >&2
  exit 0
fi

# --- 4. 解释器探测 ---
# 顺序：显式指定 > python > python3 > py -3
# 每一项都要真实跑一次 import sys 才算可用。
PY=""
for cand in "${CODEBUDDY_PYTHON:-}" python python3 "py -3"; do
  [ -z "$cand" ] && continue
  if $cand -c 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)' >/dev/null 2>&1; then
    PY="$cand"
    break
  fi
done

if [ -z "$PY" ]; then
  echo "hook-runner: 未找到可用的 Python 3 解释器（试过 CODEBUDDY_PYTHON / python / python3 / py -3）。" >&2
  echo "hook-runner: 本 hook 已跳过，会话继续。修复方式见 TROUBLESHOOTING.md 的 Windows 专章。" >&2
  exit 0
fi

# --- 5. 转发 stdin，执行 hook ---
exec $PY "$HOOK_PATH" "$@"
