#!/usr/bin/env bash
# notify.sh —— 会话需要用户注意时的桌面/终端提醒（Notification hook）
#
# 迁移自上游 .claude/hooks/notify.sh，改动三处，均为可移植性必需：
#
#   1. 去掉 jq 依赖。上游在 jq 缺失时直接 exit 0（静默失效），而 Windows
#      Git Bash 默认不带 jq，等于这条 hook 在本机永远不工作却看不出来。
#      改为「有 python 就用 python 解析，没有就用默认文案」——降级但不沉默。
#   2. 增加 MINGW/MSYS/CYGWIN 分支。上游 case 只认 Darwin/Linux，Windows
#      会落到 `*)` 只打一行到 stderr，在 GUI 里等于丢失。
#   3. 通知永远 best-effort：任何一步失败都 exit 0，绝不阻断会话。
#
# 用法（.codebuddy/settings.json）：
#   "Notification": [{ "hooks": [{ "type": "command",
#     "command": "bash .../.codebuddy/hooks/hook-runner.sh notify.sh" }] }]
#
# 输入：stdin 上的 hook JSON，取 .message / .title，两个都可缺省。
# 输出：无（副作用是桌面气泡、stderr 一行、或追加一行到通知日志）。
# 退出码：恒为 0。

set -uo pipefail

INPUT="$(cat 2>/dev/null || true)"

DEFAULT_MSG="WorkBuddy 需要你的注意"
DEFAULT_TITLE="WorkBuddy"
MESSAGE="$DEFAULT_MSG"
TITLE="$DEFAULT_TITLE"

# --- 解析 stdin JSON（无 jq 依赖）------------------------------------------
PARSE_PY=""
for cand in "${CODEBUDDY_PYTHON:-}" python python3 "py -3"; do
    [ -z "$cand" ] && continue
    if $cand -c 'import sys; sys.exit(0 if sys.version_info[0]==3 else 1)' >/dev/null 2>&1; then
        PARSE_PY="$cand"
        break
    fi
done

if [ -n "$INPUT" ] && [ -n "$PARSE_PY" ]; then
    PARSED="$(
        printf '%s' "$INPUT" | PYTHONUTF8=1 PYTHONIOENCODING=utf-8 $PARSE_PY -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
if not isinstance(d, dict):
    d = {}
msg = (d.get("message") or "").replace("\n", " ")
title = (d.get("title") or "").replace("\n", " ")
sys.stdout.write(title + "\x1f" + msg)
' 2>/dev/null
    )" || PARSED=""
    if [ -n "${PARSED:-}" ]; then
        TITLE_PART="${PARSED%%$'\x1f'*}"
        MSG_PART="${PARSED#*$'\x1f'}"
        [ -n "$TITLE_PART" ] && TITLE="$TITLE_PART"
        [ -n "$MSG_PART" ] && MESSAGE="$MSG_PART"
    fi
fi

# --- 分发 -------------------------------------------------------------------
UNAME_S="$(uname -s 2>/dev/null || echo unknown)"

case "$UNAME_S" in
    Darwin)
        MESSAGE="${MESSAGE//\"/\\\"}"
        TITLE="${TITLE//\"/\\\"}"
        osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\"" 2>/dev/null || true
        ;;
    Linux)
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "$TITLE" "$MESSAGE" 2>/dev/null || true
        else
            printf '[%s] %s\n' "$TITLE" "$MESSAGE" >&2
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        # Windows 无内置命令行气泡接口，且本工作流运行在 GUI 客户端内，
        # 会话状态本身就在界面上可见。这里退化为「stderr + 通知日志」，
        # 保证信息不丢，又不引入 PowerShell Toast 这类脆弱依赖。
        printf '[%s] %s\n' "$TITLE" "$MESSAGE" >&2
        ROOT="${CODEBUDDY_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-.}}"
        LOG_DIR="$ROOT/quality_reports/session_logs"
        if mkdir -p "$LOG_DIR" 2>/dev/null; then
            printf '%s\t[%s] %s\n' \
                "$(date '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo unknown-time)" \
                "$TITLE" "$MESSAGE" >> "$LOG_DIR/notifications.log" 2>/dev/null || true
        fi
        ;;
    *)
        printf '[%s] %s\n' "$TITLE" "$MESSAGE" >&2
        ;;
esac

exit 0
