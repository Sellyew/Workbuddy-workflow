#!/bin/bash
# Cross-platform desktop notification when Claude needs attention
# Triggers on: permission prompts, idle prompts, auth events
set -uo pipefail

INPUT="$(cat)"

# Defaults — used if INPUT is empty, jq is missing, or jq fails to parse it.
# (jq is optional: this used to exit when it was absent, so Git for Windows —
# which ships no jq — and a Linux desktop without it never notified at all.)
MESSAGE="Claude needs attention"
TITLE="Claude Code"

if [ -n "$INPUT" ] && command -v jq >/dev/null 2>&1; then
    if parsed_message="$(printf '%s' "$INPUT" | jq -r '.message // "Claude needs attention"' 2>/dev/null)"; then
        [ -n "$parsed_message" ] && MESSAGE="$parsed_message"
    fi
    if parsed_title="$(printf '%s' "$INPUT" | jq -r '.title // "Claude Code"' 2>/dev/null)"; then
        [ -n "$parsed_title" ] && TITLE="$parsed_title"
    fi
elif [ -n "$INPUT" ]; then
    # No jq — Git for Windows ships none, and neither does a slim container. The
    # fallback above is what keeps the notification *working*, but it leaves every
    # message identical, so the log below records "Claude needs attention" ten
    # times and tells you nothing about what needed attention. Pull the two
    # top-level string fields with sed instead: a nested or escaped quote simply
    # does not match, and the default stands. `q` rather than `head` so sed exits
    # on its own instead of dying of SIGPIPE, which `pipefail` would turn into a
    # 141 for the whole pipeline.
    _field() {
        printf '%s' "$INPUT" | tr -d '\r' \
            | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p;q"
    }
    parsed_message="$(_field message)"; [ -n "$parsed_message" ] && MESSAGE="$parsed_message"
    parsed_title="$(_field title)";     [ -n "$parsed_title" ]     && TITLE="$parsed_title"
fi

# Leave a trace on disk, before the notification itself: every other channel is
# invisible after the fact. stderr from a hook that exits 0 reaches only the debug
# log, and the OSC 9 sequence goes to whatever terminal happens to be attached —
# nothing, in an unattended run. Without a file, "Notification never fires" and
# "Notification fires and nobody is watching" are the same observation, which is
# the blind spot that let a broken hook-runner go unnoticed for a day. Never fatal:
# a missing directory or a read-only checkout must not turn a notification into a
# hook failure.
if _log_dir="${NOTIFY_LOG_DIR:-${CODEBUDDY_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-.}}/quality_reports/session_logs}"; [ -d "$_log_dir" ]; then
    printf '%s\t[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$TITLE" "$MESSAGE" \
        >>"$_log_dir/notifications.log" 2>/dev/null || true
fi

# NOTIFY_DRY_RUN=1 stops before the desktop notification but keeps the log line.
# scripts/check-hooks.py needs it: this is the only shell hook in the tree, and it
# used to be skipped by the wiring check for fear of popping a notification —
# which is exactly how it stayed broken (handed to Python, SyntaxError, silence)
# while every gate reported green.
[ "${NOTIFY_DRY_RUN:-0}" = "1" ] && exit 0

case "$(uname -s)" in
  Darwin)
    # Escape double quotes in message/title for osascript
    MESSAGE="${MESSAGE//\"/\\\"}"
    TITLE="${TITLE//\"/\\\"}"
    osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\"" 2>/dev/null
    ;;
  Linux)
    if command -v notify-send &>/dev/null; then
      notify-send "$TITLE" "$MESSAGE" 2>/dev/null
    else
      echo "[$TITLE] $MESSAGE" >&2
    fi
    ;;
  MINGW*|MSYS*|CYGWIN*)
    # Git Bash on Windows: no notifier binary and no /dev/tty, and stderr from a
    # hook that exits 0 reaches only the debug log. Hand Claude Code an OSC 9
    # terminal sequence (Windows Terminal, ConEmu, WezTerm) as hook JSON. The
    # JSON is escaped by hand, since jq may be absent; control characters are
    # dropped, because an ESC or BEL inside the body would end the sequence.
    body="$(printf '%s: %s' "$TITLE" "$MESSAGE" | tr -d '\000-\037\177')"
    body="${body//\\/\\\\}"
    body="${body//\"/\\\"}"
    printf '{"terminalSequence":"\\u001b]9;%s\\u0007"}\n' "$body"
    ;;
  *)
    echo "[$TITLE] $MESSAGE" >&2
    ;;
esac
exit 0
