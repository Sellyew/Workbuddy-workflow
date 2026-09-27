#!/usr/bin/env python3
"""
Issue Guard Hook (PreToolUse, Bash, scoped with `"if": "Bash(gh *)"`)

Every new GitHub issue has to pass a duplicate check first. The check lives in
scripts/file-issue.py, which searches open and closed issues several ways and
creates the issue only when no candidate is left unreviewed. This guard makes
that the only route Claude takes: it denies a Bash command that would create an
issue directly and names the script instead.

Denied (each as a simple command, anywhere in a compound line or a $(...)):
  - gh issue create / gh issue new        (global -R/--repo flags allowed anywhere)
  - gh api ... repos/<o>/<r>/issues       with POST (explicit -X/--method, or
                                          implied by -f/-F/--field/--raw-field/--input)
  - gh api graphql ... createIssue

Allowed and silent: everything else, including gh issue list/view/comment/close/
reopen/edit, and python3 scripts/file-issue.py (its own `gh issue create` runs
as a child process, which hooks never see).

What this is not: a security boundary. `/path/to/gh`, `sh -c '...'` or a
script of your own can still create an issue. It stops the usual form Claude
writes, which is the one that skips the check by accident.

Cost: the `if` filter (Claude Code >= 2.1.85; compound commands >= 2.1.89)
spawns this hook only for commands that run `gh`. On an older version the
filter is ignored and the hook runs on every Bash call, still correctly.

No network, no git, no disk: a guard that stalls or crashes fails OPEN, so it
decides from the command text alone.

Output: deny → exit 0 + JSON {"hookSpecificOutput": {"hookEventName":
"PreToolUse", "permissionDecision": "deny", "permissionDecisionReason"}}.
Anything else → exit 0, no output. Fail-open: any error → exit 0, silent.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys

REASON = (
    "Blocked: a new GitHub issue must pass the duplicate check first. Write the body to a "
    "file and run `python3 scripts/file-issue.py --title \"...\" --body-file <file> "
    "[--label ...] [--search \"...\"]`. It searches open and closed issues and creates the "
    "issue only when every candidate it finds has been reviewed (re-run with --checked N,M "
    "once you have judged them distinct). If the problem is already tracked, use "
    "`gh issue comment <N>` (and `gh issue reopen <N>` if it is back) instead. "
    "See .claude/skills/issues/SKILL.md."
)

# Operators that end one simple command and start the next.
SEPARATORS = {";", "&&", "||", "|", "|&", "&", "(", ")", "\n"}
# Words that run the command after them.
WRAPPERS = {"command", "builtin", "exec", "nohup", "time", "env", "sudo"}
# gh flags that take a value (skipped when finding the subcommand words).
GH_VALUE_FLAGS = {"-R", "--repo", "--hostname"}
API_BODY_FLAGS = {"-f", "-F", "--field", "--raw-field", "--input"}
ISSUES_ENDPOINT = re.compile(r"^/?repos/[^/\s]+/[^/\s]+/issues/?(\?.*)?$")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# A heredoc opener (<<EOF, <<-'EOF', <<"EOF"), not a here-string (<<<) or a shift.
HEREDOC = re.compile(r"(?<!<)<<-?(?!<)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def strip_heredocs(command: str) -> str:
    """Drop heredoc bodies: they are a command's input, not commands.

    Without this, writing a file that merely CONTAINS the text `gh issue create`
    (a test, a doc, this hook's own battery) was denied. A heredoc fed to a shell
    (`bash <<EOF ... EOF`) is not inspected; like `sh -c`, that is outside what
    this guard claims to stop.
    """
    lines = command.split("\n")
    kept, i = [], 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            delim = m.group(2)
            while i < len(lines) and lines[i].strip() != delim:
                i += 1
            i += 1                          # the closing delimiter line
    return "\n".join(kept)


def deny(reason: str) -> None:
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, sys.stdout)


def simple_commands(command: str) -> list[list[str]]:
    """Split a shell line into the word lists of its simple commands.

    $( and backticks open a nested command, so they are turned into separators:
    `echo $(gh issue create ...)` yields the gh command as its own segment.
    """
    text = command.replace("$(", " ( ").replace("`", " ; ")
    lex = shlex.shlex(text, posix=True, punctuation_chars=";&|()\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    segments, cur = [], []
    for tok in lex:
        if tok in SEPARATORS or set(tok) <= set(";&|()\n"):
            if cur:
                segments.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        segments.append(cur)
    return segments


def substitutions(text: str) -> list[str]:
    """Bodies of $(...) and `...` the shell would run — including inside double quotes.

    shlex keeps "…$(cmd)…" as one quoted word, so a create hidden in a quoted
    substitution needs this separate pass. Single-quoted text is literal and skipped;
    $(( )) is arithmetic and skipped.
    """
    out: list[str] = []
    i, n, in_s, in_d = 0, len(text), False, False
    while i < n:
        c = text[i]
        if c == "\\" and not in_s:
            i += 2
            continue
        if c == "'" and not in_d:
            in_s = not in_s
        elif c == '"' and not in_s:
            in_d = not in_d
        elif not in_s and text.startswith("$((", i):
            i += 3
            continue
        elif not in_s and text.startswith("$(", i):
            depth, j = 1, i + 2
            while j < n and depth:
                depth += {"(": 1, ")": -1}.get(text[j], 0)
                j += 1
            body = text[i + 2:j - 1]
            out += [body, *substitutions(body)]
            i = j
            continue
        elif not in_s and c == "`":
            j = text.find("`", i + 1)
            if j < 0:
                break
            out.append(text[i + 1:j])
            i = j + 1
            continue
        i += 1
    return out


def strip_prefix(words: list[str]) -> list[str]:
    """Drop leading VAR=value assignments and wrapper words (env, command, ...)."""
    i = 0
    while i < len(words):
        w = words[i]
        if ASSIGNMENT.match(w):
            i += 1
        elif w in WRAPPERS:
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 1                      # env -i, sudo -E, ...
        else:
            break
    return words[i:]


def gh_positionals(args: list[str]) -> list[str]:
    """gh's non-flag words, skipping the values of flags that take one."""
    out, i = [], 0
    while i < len(args):
        a = args[i]
        if a in GH_VALUE_FLAGS:
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        out.append(a)
        i += 1
    return out


def creates_issue(words: list[str]) -> bool:
    words = strip_prefix(words)
    if not words or os.path.basename(words[0]) != "gh":
        return False
    args = words[1:]
    pos = gh_positionals(args)
    if len(pos) >= 2 and pos[0] == "issue" and pos[1] in ("create", "new"):
        return True
    if pos and pos[0] == "api":
        joined = " ".join(args)
        if len(pos) >= 2 and pos[1] == "graphql":
            return "createIssue" in joined
        method = None
        for i, a in enumerate(args):
            if a in ("-X", "--method") and i + 1 < len(args):
                method = args[i + 1].upper()
            elif a.startswith("--method="):
                method = a.split("=", 1)[1].upper()
            elif a.startswith("-X") and len(a) > 2:
                method = a[2:].upper()
        has_body = any(a in API_BODY_FLAGS or any(a.startswith(f + "=") for f in API_BODY_FLAGS
                                                   if f.startswith("--"))
                       for a in args)
        is_post = method == "POST" or (method is None and has_body)
        return is_post and any(ISSUES_ENDPOINT.match(p) for p in pos[1:])
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return 0
    if not isinstance(data, dict) or data.get("tool_name") != "Bash":
        return 0
    command = (data.get("tool_input") or {}).get("command") or ""
    if "gh" not in command:
        return 0
    try:
        text = strip_heredocs(command)
        segments = [seg for t in [text, *substitutions(text)] for seg in simple_commands(t)]
    except ValueError:
        # Unbalanced quotes: shlex cannot split it, and neither can the shell.
        return 0
    if any(creates_issue(seg) for seg in segments):
        deny(REASON)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open — a guard bug must not block unrelated work
        sys.exit(0)
