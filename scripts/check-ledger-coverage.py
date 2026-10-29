#!/usr/bin/env python3
"""Make the qualification ledger load-bearing: what runs and what is recorded must agree.

The ledger's own rule is that a checker with no row is unqualified and its green
light means nothing. Until now nothing enforced that rule — the ledger could drift
from the repo in either direction and every gate stayed green.

Both directions fail here:

  1. a check that RUNS but has no ledger row — an unmeasured green light. A row in
     the "Not yet qualified" section counts as VISIBLE DEBT and only warns: the job
     is to prevent SILENT absence, not to force instant qualification.
  2. a ledger row naming a checker that is no longer on disk — a qualification for
     a ghost, which reads as coverage the repo does not have.

Plus wiring: a mistyped path in `.codebuddy/settings.json` costs you the GUARDING,
and no other gate in the suite notices — nothing else reads the settings file
against the disk, so a hook can be wired to nothing while every check stays green.
That is the failure this checker exists to catch. The symptom is not silence, and
it is not legible either: `python3 <missing-path>` exits 2, which a PreToolUse hook
means as BLOCK, so a typo on a guard denies every matching call with an interpreter
error nobody reads as a config error; a bare path exits 127 (126 if present but not
executable), a non-blocking error that scrolls past while the guard stops guarding.

Registered checks are derived LIVE from three sources of truth — the gate list in
`scripts/gate-manifest.py`, the hook commands in `.codebuddy/settings.json`, and the
`.githooks/pre-commit` entry point. Never a hardcoded list: a list here would drift
exactly the way the ledger does, and this checker would be the last to notice.

[WorkBuddy 适配] The gate list used to be re-derived here from the `run "..."`
lines of `scripts/backtest.sh`. That made this file a SECOND parser of the same
text: adding a gate meant satisfying `backtest.py` AND this regex, and a gate whose
line shape the regex missed would silently have no ledger requirement at all.
It now reads the manifest's `scripts` column, which is declared **host-independent**
on purpose — on a machine without bash gate 3 does not RUN, but
`check-model-versions.sh` is still a registered check that owes a ledger row.

Exit: 0 agreement (warnings allowed), 1 disagreement, 2 could not run.
"""
import importlib.util, json, os, re, shlex, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")

LEDGER = "quality_reports/qualification/LEDGER.md"
SETTINGS = ".codebuddy/settings.json"
MANIFEST = "scripts/gate-manifest.py"
PRECOMMIT = ".githooks/pre-commit"


def load_gates():
    """The gate list — one source of truth for what the suite runs.

    A missing or unreadable manifest is CANNOT RUN, not "zero gates": reporting
    agreement against an empty set is the empty-scan-passes-green failure this
    repo treats as its most expensive bug class.
    """
    path = os.path.join(ROOT, MANIFEST)
    spec = importlib.util.spec_from_file_location("_gate_manifest", path)
    if spec is None or spec.loader is None:
        raise CannotRun(f"{MANIFEST}: cannot load the gate manifest")
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except OSError as e:
        raise CannotRun(f"{MANIFEST}: cannot read ({e.strerror or e})")
    except Exception as e:                      # a broken manifest must not read as "no gates"
        raise CannotRun(f"{MANIFEST}: cannot import ({type(e).__name__}: {e})")
    gates = getattr(mod, "GATES", None)
    if not gates:
        raise CannotRun(f"{MANIFEST}: no GATES — the manifest format changed and this checker "
                        "is now blind to every gate")
    return gates

# The ledger section that records checks known to be unqualified. A name there is
# debt someone can see and schedule; a name nowhere at all is the failure.
DEBT_HEADING = "not yet qualified"

# A command whose first word is one of these runs the NEXT argument as a script,
# so the script itself needs only to exist and be readable — not to be executable.
INTERPRETERS = {"python", "python3", "bash", "sh", "zsh", "node", "Rscript", "perl", "ruby", "uv"}

# What counts as a checker name in a ledger cell. Deliberately narrow: ledger rows
# also backtick artifacts, flags, and shell fragments, and none of those are checks.
# Extension-less entry points (git's own hook names) carry no signature of their own,
# so they are admitted only by matching something that demonstrably runs.
SCRIPT_TOKEN = re.compile(r'^[\w./-]+\.(?:py|sh)$')

# Where an unqualified (directory-less) ledger name may live.
SEARCH_DIRS = ["", "scripts", ".codebuddy/hooks", ".codebuddy/scripts", ".githooks"]


class CannotRun(Exception):
    """A source of truth could not be read. A check that could not run is not a passing check."""


def read(rel):
    try:
        return open(os.path.join(ROOT, rel), encoding="utf-8").read()
    except OSError as e:
        raise CannotRun(f"{rel}: cannot read ({e.strerror or e})")


def expand(tok):
    """Resolve the path variables the harness and the gate runner inject.

    [WorkBuddy 适配] 新增两种写法：
      * `${CODEBUDDY_PROJECT_DIR}` / `$CODEBUDDY_PROJECT_DIR` —— WorkBuddy 的变量名
      * `${CODEBUDDY_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-.}}` —— 本仓库 hook 命令
        实际使用的「带默认值的嵌套展开」写法。不识别它的话，settings.json 里
        每条 hook 都会被解析成一个字面量路径，WIRING 检查整体失效——
        而 WIRING 是唯一能发现「hook 接在不存在文件上」的检查。
    """
    tok = re.sub(
        r"\$\{CODEBUDDY_PROJECT_DIR:-\$\{(?:CODEBUDDY|CLAUDE)_PROJECT_DIR:-\.\}\}",
        lambda _m: ROOT, tok)   # lambda：ROOT 是 Windows 路径，直接当替换串会让 re 解释 \w \t
    for var in ("CODEBUDDY_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        tok = tok.replace("${%s}" % var, ROOT).replace("$%s" % var, ROOT)
    return tok.replace("${DIR}", SCRIPTS).replace("$DIR", SCRIPTS)


# [WorkBuddy 适配] hook 统一入口：`.codebuddy/hooks/hook-runner.sh <hook 文件名>`。
# 真实脚本是它后面的那个参数，不是 runner 本身。
HOOK_RUNNER = "hook-runner.sh"


def script_of(command, where):
    """The script a shell command actually runs, and the interpreter it runs under."""
    try:
        toks = shlex.split(command)
    except ValueError as e:
        raise CannotRun(f"{where}: cannot tokenize command ({e})")
    if not toks:
        raise CannotRun(f"{where}: empty command")
    interp, i = None, 0
    if os.path.basename(toks[0]) in INTERPRETERS:
        interp, i = os.path.basename(toks[0]), 1
        while i < len(toks) and toks[i].startswith("-"):
            i += 1
    if i >= len(toks):
        raise CannotRun(f"{where}: no script path in command: {command}")
    p = expand(toks[i])
    p = os.path.normpath(p if os.path.isabs(p) else os.path.join(ROOT, p))
    # 跟随 runner 间接调用，否则每条 hook 都会被记成 hook-runner.sh，
    # 台账里 11 条 hook 的记录会全部「对不上」，而门禁看起来仍是绿的。
    #
    # runner 位于 `.codebuddy/hooks/lib/`，但它把参数解析成
    # `$ROOT/.codebuddy/hooks/<hook>`（见 hook-runner.sh 的 HOOK_PATH），
    # 即相对 **hooks/** 而不是相对自己的 **lib/**。按 lib/ 解析会让 12 条 hook
    # 全部报 MISSING——这正是本检查存在的意义：接线错了要喊出来。
    if os.path.basename(p) == HOOK_RUNNER and i + 1 < len(toks):
        inner = expand(toks[i + 1])
        if os.path.isabs(inner):
            p = os.path.normpath(inner)
        else:
            base = os.path.dirname(p)
            if os.path.basename(base) == "lib":
                base = os.path.dirname(base)
            p = os.path.normpath(os.path.join(base, inner))
    return p, interp


def registered():
    """Every check that actually runs, derived live. Returns (source, path, interpreter, where)."""
    out = []

    gates = load_gates()
    for spec in gates:
        # One row per SCRIPT, not per gate: gate 10 runs two batteries, and both
        # are checks that run and therefore owe the ledger a row.
        for name in spec["scripts"]:
            out.append(("backtest gate", os.path.join(SCRIPTS, name), None, spec["name"]))

    try:
        cfg = json.loads(read(SETTINGS))
    except json.JSONDecodeError as e:
        raise CannotRun(f"{SETTINGS}: invalid JSON ({e})")
    hooks = cfg.get("hooks")
    if not isinstance(hooks, dict) or not hooks:
        raise CannotRun(f"{SETTINGS}: no `hooks` object — the session hooks are registered there, "
                        "and an empty one means either a broken file or silently no hooks at all")
    for event in sorted(hooks):
        for group in hooks[event] or []:
            for h in group.get("hooks") or []:
                if h.get("type") != "command":
                    continue
                path, interp = script_of(h.get("command", ""), f"{SETTINGS} {event}")
                out.append(("settings hook", path, interp, event))

    out.append(("entry point", os.path.join(ROOT, PRECOMMIT), None, "pre-commit"))
    return out


def ledger_names(known):
    """Checker names the ledger claims, split into qualified rows and visible debt.

    `known` is the set of registered basenames, which is what lets an extension-less
    entry point be recognised without hardcoding git's hook names here.

    Name-extraction is SCOPED BY SECTION, not applied to every table row: a token
    is read as a qualification claim only inside the debt section (`## Not yet
    qualified`) or a section whose heading records qualification (`qualif` in it,
    including the top-level `# Qualification Ledger`). A stray backticked hook path
    in an unrelated table — a future change-log or reproduction table pasted in —
    is therefore NOT silently read as a qualified checker. And a missing debt
    heading is treated as format drift (CannotRun), the same as the other two
    format dependencies, so a reworded debt section cannot silently promote every
    unmeasured checker to qualified.
    """
    qualified, debt = {}, {}
    section_qual = section_debt = seen_debt = False
    for line in read(LEDGER).split("\n"):
        head = re.match(r'^#+\s+(.*)', line)
        if head:
            h = head.group(1).strip().lower()
            section_debt = DEBT_HEADING in h
            section_qual = (not section_debt) and ("qualif" in h)
            if section_debt:
                seen_debt = True
            continue
        if not line.lstrip().startswith("|"):
            continue
        if not (section_qual or section_debt):
            continue
        bucket = debt if section_debt else qualified
        for tok in (t.strip() for t in re.findall(r'`([^`]+)`', line)):
            # r21: a checker NAME is one path and never contains whitespace. A row
            # may legitimately backtick a COMMAND that happens to end in a known
            # checker's basename — the r20 rows quote `rm -f .clau\de/hooks/…` and
            # `rm -f .githook\s/pre-commit` as the measured bypass spellings — and
            # before this guard both were read as qualification claims naming a file
            # that does not exist, failing the gate on prose rather than on coverage.
            # Splitting on whitespace is the whole fix: it cannot hide a real claim,
            # because a real one has no space to split on.
            if re.search(r'\s', tok):
                continue
            if SCRIPT_TOKEN.match(tok) or os.path.basename(tok) in known:
                bucket.setdefault(os.path.basename(tok), set()).add(tok)
    if not seen_debt:
        raise CannotRun(f"{LEDGER}: no '{DEBT_HEADING}' section heading found — the debt-section "
                        "heading changed or was removed, so every unqualified checker would "
                        "silently read as qualified; refusing to report agreement")
    if not qualified and not debt:
        raise CannotRun(f"{LEDGER}: no checker name found in any qualification or debt table row — "
                        "the ledger format changed and this checker is now blind to every row")
    return qualified, debt


def named_by(path, names):
    """Does `names` (basename -> {tokens}) name this path? A token with a directory must match it.

    [WorkBuddy 适配] 历史台账行写的是迁移前的 `.claude/hooks/…` 拼写。台账是
    历史记录，不得改写（见 meta-governance.md「Historical records are never
    edited」），所以这里按别名双向比对：同一个文件搬了目录，资质仍对应它。
    """
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    rel_legacy = rel.replace(".codebuddy/", ".claude/", 1)
    return any("/" not in tok or rel.endswith(tok) or rel_legacy.endswith(tok)
               for tok in names.get(os.path.basename(path), ()))


def resolve(tok):
    """Where a ledger name lives on disk, or None."""
    cands = [os.path.join(ROOT, tok)] if "/" in tok else \
            [os.path.join(ROOT, d, tok) for d in SEARCH_DIRS]
    found = next((os.path.normpath(c) for c in cands if os.path.isfile(c)), None)
    if found:
        return found
    # [WorkBuddy 适配] 迁移前的拼写 → 迁移后的位置（单向别名，不改写台账）
    tok2 = tok.replace(".claude/", ".codebuddy/", 1)
    if tok2 == tok:
        return None
    cands2 = [os.path.join(ROOT, tok2)] if "/" in tok2 else \
             [os.path.join(ROOT, d, tok2) for d in SEARCH_DIRS]
    return next((os.path.normpath(c) for c in cands2 if os.path.isfile(c)), None)


def tracked_files():
    # -z 加显式 UTF-8 解码：普通 `ls-files` 会把非 ASCII 文件名 C-quote 成
    # （".codebuddy/hooks/lembrete_sess\303\243o.py"），于是已入库的钩子被读成
    # UNTRACKED；而 text=True 用 Windows 代码页解码，遇到它会变成乱码或直接崩。
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True)
    files = {f for f in r.stdout.decode("utf-8", "surrogateescape").split("\0") if f}
    if not files:
        raise CannotRun("git ls-files returned nothing (not a git repo?) — cannot verify that "
                        "the registered checks survive a fresh clone")
    return files


def main():
    # 报告每次都会打一个破折号。cp932 或 Latin-1 的 stdout（日文 Windows 上的管道、
    # 老式 POSIX locale）编码不了它，门禁就会因为一个控制台细节以 exit 1 死掉——
    # 无论控制台是什么，都按 UTF-8 打。
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
    try:
        checks = registered()
        qualified, debt = ledger_names({os.path.basename(p) for _, p, _, _ in checks})
        tracked = tracked_files()
    except CannotRun as e:
        print(f"check-ledger-coverage: CANNOT RUN — {e}", file=sys.stderr)
        print("  A check that could not run is not a passing check.", file=sys.stderr)
        return 2

    rel = lambda p: os.path.relpath(p, ROOT).replace(os.sep, "/")
    errs, warns = [], []
    n = lambda src: sum(1 for s, _, _, _ in checks if s == src)
    art = lambda src: ("an " if src[0] in "aeiou" else "a ") + src

    print("check-ledger-coverage: the qualification ledger vs. what actually runs")
    print(f"  derived live from source: {n('backtest gate')} backtest gate(s), "
          f"{n('settings hook')} settings.json hook(s), {n('entry point')} entry point(s)")

    print("\n  DIRECTION 1 — every registered check needs a ledger row")
    for source, path, _, where in checks:
        # Debt wins over a qualified mention: an explicit 'not yet qualified' row
        # is a stronger statement than any incidental backticked reference.
        if named_by(path, debt):
            status = "visible debt — 'Not yet qualified'"
            warns.append(f"{rel(path)}: relied upon as {art(source)} ('{where}') and never measured")
        elif named_by(path, qualified):
            status = "ledger row"
        else:
            status = "NO LEDGER ROW"
            errs.append(f"{rel(path)}: runs as {art(source)} ('{where}') but the ledger does not "
                        "name it — qualify it, or list it under 'Not yet qualified' as visible debt")
        print(f"    {source:<14} {rel(path):<42} {status}")

    print("\n  DIRECTION 2 — every checker the ledger names must still exist")
    for kind, names in (("row", qualified), ("debt row", debt)):
        for base in sorted(names):
            for tok in sorted(names[base]):
                found = resolve(tok)
                print(f"    {kind:<14} {tok:<42} {'-> ' + rel(found) if found else 'NOT ON DISK'}")
                if not found:
                    errs.append(f"{tok}: named by a ledger {kind} but no such file exists — the "
                                "qualification is recorded for a checker that is gone")

    print("\n  WIRING — a mistyped path here leaves a check wired to nothing")
    for source, path, interp, where in checks:
        if source == "backtest gate":
            continue                      # a dead gate path is loud: backtest.py skips it by name
        r = rel(path)
        if not os.path.isfile(path):
            print(f"    {where:<14} {r:<42} MISSING — never runs")
            errs.append(f"{r}: registered as {art(source)} ('{where}') but no such file exists — "
                        "it is wired to nothing, and the invocation fails in a way nobody reads "
                        "as a config error (interpreted: exit 2, which PreToolUse means as BLOCK; "
                        "bare path: exit 127, non-blocking, guard gone)")
            continue
        notes = []
        if interp:
            if os.access(path, os.R_OK):
                notes.append(f"readable, run by {interp}")
            else:
                notes.append(f"NOT READABLE by {interp}")
                errs.append(f"{r}: invoked via {interp} but is not readable — the invocation exits 2, "
                            "which PreToolUse means as BLOCK, so every matching call is denied by a "
                            "permission error that is really a config typo")
        elif os.access(path, os.X_OK):
            notes.append("executable")
        else:
            notes.append("NOT EXECUTABLE")
            errs.append(f"{r}: invoked directly but is not executable — the invocation exits 126 with "
                        f"a shell error, which does not block anything, so the hook stops guarding "
                        f"while the session looks normal (fix: chmod +x {r})")
        if r in tracked:
            notes.append("tracked")
        else:
            notes.append("UNTRACKED")
            errs.append(f"{r}: not tracked by git — it does not survive a fresh clone, so the check "
                        "is present here and absent for everyone else")
        print(f"    {where:<14} {r:<42} {', '.join(notes)}")

    if warns:
        print(f"\n{len(warns)} VISIBLE DEBT — listed in the ledger, not yet measured:")
        for w in warns:
            print(f"  {w}")
    if errs:
        print(f"\n{len(errs)} COVERAGE FAILURE(S):")
        for e in errs:
            print(f"  {e}")
        print("\nThe ledger and the running checks disagree. An unqualified check's green light "
              "means nothing — see verification-ladder rung 0.")
        return 1

    print(f"\nLedger and running checks agree: {len(checks)} registered check(s) accounted for, "
          "every named checker on disk, every wiring live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
