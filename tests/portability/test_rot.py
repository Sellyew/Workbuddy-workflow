"""root-of-trust-guard.py: the spellings of a gate-defining path that the guard
used to allow while its literal twin denied (issue #171, and #151 claim 1).

Two kinds of case:

  * NATIVE — the real hook run as a subprocess with a PreToolUse event on stdin
    and CLAUDE_PROJECT_DIR set, exactly as scripts/hook-battery.sh fires it. The
    CR strip, the `.exe`/case fold on program names, the Unicode casefold, the
    stdin decoding and the scope half are all unconditional, so they are pinned
    here on Linux and macOS alike — and so is the ABSENCE of the backslash
    form, which here would misread an escaped `sed -i` script as a path.
  * WINDOWS — the real hook loaded through _winsim (os.path = ntpath) and its
    real main() driven with a Bash event. The project is a real fixture
    directory reached through its Windows spelling (C:\\...), so the scope half
    resolves on disk. A backslash as a separator, NTFS stream suffixes, MSYS
    drive paths (`/c/...`) and the `-C` composition only exist on Windows, so
    they are pinned here.

HOOK_DIR (the same variable hook-battery.sh reads) points the suite at another
copy of the hooks — that is how the pre-fix code is shown to fail these cases.

Every case is safe to run: the hook only DECIDES; nothing is ever executed.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unicodedata
import unittest

import _winsim

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOK_DIR = os.environ.get("HOOK_DIR") or os.path.join(ROOT, ".codebuddy", "hooks")
GUARD = os.path.join(HOOK_DIR, "root-of-trust-guard.py")
DENY = '"permissionDecision": "deny"'

_T = ""          # fixture base (realpath'd), built once in setUpModule
FX = {}          # fixture name -> absolute path


def _mkproj(path):
    os.makedirs(os.path.join(path, ".codebuddy", "hooks"), exist_ok=True)
    os.makedirs(os.path.join(path, ".codebuddy", "rules"), exist_ok=True)
    os.makedirs(os.path.join(path, ".githooks"), exist_ok=True)
    os.makedirs(os.path.join(path, "docs"), exist_ok=True)
    for rel, body in ((".codebuddy/hooks/git-guardrails.py", "# stub\n"),
                      (".codebuddy/settings.json", "{}\n"),
                      (".githooks/pre-commit", "#!/bin/sh\n")):
        with open(os.path.join(path, rel), "w", encoding="utf-8") as f:
            f.write(body)
    return path


def setUpModule():
    global _T
    _T = os.path.realpath(tempfile.mkdtemp(prefix="rot-port-"))
    FX["proj"] = _mkproj(os.path.join(_T, "Proj"))            # mixed case on purpose
    FX["projx"] = _mkproj(os.path.join(_T, "Projx"))          # sibling-prefix control
    FX["other"] = _mkproj(os.path.join(_T, "other"))
    FX["accent"] = _mkproj(os.path.join(_T, "proj-\u00e9"))   # NFC é
    FX["nfd"] = _mkproj(os.path.join(_T, unicodedata.normalize("NFD", "\u00e9t\u00e9")))
    # the Windows-simulated project and a second tree beside it
    FX["win"] = _mkproj(os.path.join(_T, "win", "proj"))
    FX["winother"] = _mkproj(os.path.join(_T, "win", "other"))
    # a project whose `.codebuddy` is a link to a shared config dir outside it
    shared = _mkproj(os.path.join(_T, "shared"))
    FX["shared"] = shared
    if not _winsim.CAN_SYMLINK:
        return       # #171 F4: the link fixtures' cases skip; the rest of the file runs
    FX["symproj"] = os.path.join(_T, "symproj")
    os.makedirs(FX["symproj"])
    os.symlink(os.path.join(shared, ".codebuddy"), os.path.join(FX["symproj"], ".codebuddy"))
    # ... whose `.codebuddy/hooks` alone is linked out
    FX["symhooks"] = os.path.join(_T, "symhooks")
    os.makedirs(os.path.join(FX["symhooks"], ".codebuddy"))
    os.symlink(os.path.join(shared, ".codebuddy", "hooks"),
               os.path.join(FX["symhooks"], ".codebuddy", "hooks"))
    # ... whose `.githooks` is linked out
    FX["symgit"] = os.path.join(_T, "symgit")
    os.makedirs(FX["symgit"])
    os.symlink(os.path.join(shared, ".githooks"), os.path.join(FX["symgit"], ".githooks"))
    # an ALIAS spelling of the symlinked project (CLAUDE_PROJECT_DIR through a link)
    FX["alias"] = os.path.join(_T, "alias")
    os.symlink(FX["symproj"], FX["alias"])


def tearDownModule():
    if _T:
        shutil.rmtree(_T, ignore_errors=True)


# ---- native: the hook as a subprocess ----------------------------------------
def _clean_env(extra):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_")
           and k not in ("ALLOW_ROOT_OF_TRUST_WRITE",
                         # [WorkBuddy 适配] 新旧两个变量都要隔离，理由同
                         # test_hooks.py 的 _SCRUB。
                         "CODEBUDDY_PROJECT_DIR", "CLAUDE_PROJECT_DIR",
                         "PYTHONIOENCODING", "PYTHONUTF8")}
    env.update(extra)
    return env


def fire(command, cwd, project, env=None, event_extra=None):
    """Run the guard on one Bash event; return its stdout (empty = allowed)."""
    ev = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd}
    ev.update(event_extra or {})
    raw = json.dumps(ev, ensure_ascii=False).encode("utf-8")   # what Node sends
    # [WorkBuddy 适配] 两个项目目录变量一起给：本仓库的守卫先读新的、再兜底旧的。
    # 只给旧的仍能工作（兼容层在），但那样测的是一条将来会被删掉的分支。
    r = subprocess.run([sys.executable, GUARD], input=raw, capture_output=True,
                       cwd=cwd, timeout=60,
                       env=_clean_env(dict(env or {},
                                           CODEBUDDY_PROJECT_DIR=project,
                                           CLAUDE_PROJECT_DIR=project)))
    if r.returncode != 0:
        raise AssertionError(f"hook exited {r.returncode}: {r.stderr.decode(errors='replace')}")
    return r.stdout.decode("utf-8", "replace")


# (id, fixture, command, expect_deny, env) — command may hold {P} {T} for paths;
# cwd and CLAUDE_PROJECT_DIR are the fixture.
NATIVE = [
    # -- a backslash is NOT a separator here (the Windows twins are win_bs_*).
    #    The first #171 cut read it as one everywhere, which denied the ordinary
    #    escaped `sed -i` / `perl -pi` script (rot-2 fix-up); on POSIX the `\`
    #    is part of the name, so these name no protected file.
    ("bs_posix_name_char",  "proj", r"rm -rf '.codebuddy\hooks'", False, None),
    ("bs_posix_redirect",   "proj", r"echo x > '.codebuddy\settings.json'", False, None),
    ("bs_sed_escaped_dot",  "proj", r"sed -i '' 's/\.githooks/githooks/' docs/x.md", False, None),
    ("bs_sed_escaped_to",   "proj", r"sed -i '' 's/scripts\/hooks/.codebuddy\/hooks/g' README.md",
     False, None),
    ("bs_sed_escaped_both", "proj",
     r"sed -i 's/\.codebuddy\/hooks\/old\.py/.codebuddy\/hooks\/new.py/g' docs/guide.md", False, None),
    ("bs_perl_escaped",     "proj", r"perl -pi -e 's/old\/dir/.codebuddy\/settings.json/g' README.md",
     False, None),
    ("bs_sed_escaped_gnu",  "proj", r"sed -i 's/foo/.codebuddy\/hooks/' notes.txt", False, None),
    ("bs_ctrl_sed_hash",    "proj", r"sed -i '' 's#scripts/hooks#.codebuddy/hooks#g' README.md",
     False, None),
    ("bs_ctrl_sed_print",   "proj", r"sed -n 's/x/.codebuddy\/hooks/p' README.md", False, None),
    ("bs_ctrl_unquoted",    "proj", r"echo x > .codebuddy\settings.json", False, None),
    ("bs_ctrl_read",        "proj", r"cat '.codebuddy\hooks\git-guardrails.py'", False, None),
    ("bs_ctrl_rules",       "proj", r"rm -rf '.codebuddy\rules'", False, None),
    ("stream_ctrl_posix",   "proj", "echo x > '.codebuddy/settings.json::$DATA'", False, None),
    # -- a CR inside a word (carriage-return-in-word-bypasses-guards)
    ("cr_rm",               "proj", "rm -rf .clau\rde/hooks", True, None),
    ("cr_redirect",         "proj", "echo CLOBBERED > .codebuddy/settings.js\ron", True, None),
    ("cr_wrapped_git",      "proj", "bash -c 'git reset --ha\rrd'", True, None),
    ("cr_ctrl_read",        "proj", "ls .clau\rde/hooks", False, None),
    # -- `.exe` and case-varied program names (exe-suffix-bypasses-guards)
    ("exe_rm",              "proj", "rm.exe -rf .codebuddy/hooks", True, None),
    ("exe_rm_upper",        "proj", "RM.EXE -rf .codebuddy/hooks", True, None),
    ("exe_rm_path",         "proj", "/usr/bin/rm.exe -rf .codebuddy/hooks", True, None),
    ("exe_cp",              "proj", "cp.exe /dev/null .codebuddy/settings.json", True, None),
    ("exe_git",             "proj", "git.exe rm -r .codebuddy/hooks", True, None),
    ("exe_bash_payload",    "proj", "bash.exe -c 'rm -rf .codebuddy/hooks'", True, None),
    ("exe_bash_git",        "proj", "bash.exe -c 'git reset --hard'", True, None),
    ("exe_sed",             "proj", "sed.exe -i s/a/b/ .codebuddy/settings.json", True, None),
    ("exe_env",             "proj", "env.exe rm -rf .codebuddy/hooks", True, None),
    ("exe_find_exec",       "proj", "find .codebuddy/hooks -exec rm.exe {} +", True, None),
    ("case_wrapper_nice",   "proj", "NICE rm -f .codebuddy/hooks/git-guardrails.py", True, None),
    ("case_wrapper_bash",   "proj", "BASH -c 'rm -f .codebuddy/hooks/git-guardrails.py'", True, None),
    ("exe_ctrl_status",     "proj", "git.exe status", False, None),
    ("exe_ctrl_cat",        "proj", "cat.exe .codebuddy/settings.json", False, None),
    ("exe_ctrl_bash_ls",    "proj", "bash.exe -c 'ls .codebuddy/hooks'", False, None),
    ("exe_ctrl_rm_other",   "proj", "rm.exe -f docs/tmp.txt", False, None),
    # -- Unicode casefold: APFS folds U+017F to `s` (rot-unicode-casefold)
    ("fold_hooks",          "proj", "rm -rf .codebuddy/hook\u017f", True, None),
    ("fold_settings",       "proj", "printf x > .codebuddy/setting\u017f.json", True, None),
    ("fold_githooks",       "proj", "rm -rf .githook\u017f", True, None),
    ("fold_writer_sed",     "proj", "\u017fed -i s/a/b/ .codebuddy/settings.json", True, None),
    ("fold_writer_install", "proj", "in\u017ftall /dev/null .codebuddy/hooks/git-guardrails.py", True, None),
    ("fold_ctrl_read",      "proj", "cat .codebuddy/setting\u017f.json", False, None),
    # -- stdin decoded as UTF-8, not the ANSI code page (guard-stdin-codepage-fail-open,
    #    guard-stdin-mojibake-scope-bypass, hook-stdin-ansi-codepage-fail-open)
    ("enc_cjk_pipe",        "proj", "echo \u4e2d|rm -rf .codebuddy/hooks", True,
     {"PYTHONIOENCODING": "cp936:surrogateescape"}),
    ("enc_curly_quote",     "proj", "rm -rf .codebuddy/hooks  # \u201d", True,
     {"PYTHONIOENCODING": "cp1252"}),
    ("enc_mojibake_scope",  "accent", "rm -rf {P}/.codebuddy/hooks", True,
     {"PYTHONIOENCODING": "cp1252:surrogateescape"}),
    ("enc_mojibake_redirect", "accent", "echo x > {P}/.codebuddy/settings.json", True,
     {"PYTHONIOENCODING": "cp1252:surrogateescape"}),
    # -- scope: case- and normalisation-varied spellings (rot-scope-string-compare,
    #    rotg-scope-case-sensitive-apfs)
    ("scope_case_prefix",   "proj", "rm -rf {T}/PROJ/.codebuddy/hooks", True, None),
    ("scope_case_redirect", "proj", "echo X > {T}/PROJ/.codebuddy/settings.json", True, None),
    ("scope_case_githooks", "proj", "rm -f {T}/PROJ/.githooks/pre-commit", True, None),
    ("scope_nfc_token",     "nfd",  "rm -rf {T}/\u00e9t\u00e9/.codebuddy/hooks", True, None),
    ("scope_ctrl_other",    "proj", "rm -rf {T}/other/.codebuddy/hooks", False, None),
    ("scope_ctrl_sibling",  "proj", "rm -rf {T}/Projx/.codebuddy/hooks", False, None),
    # -- scope: a link that carries the protected NAME (rot-symlinked-claude-dir)
    ("link_claude_hooks",   "symproj", "rm -rf .codebuddy/hooks", True, None),
    ("link_claude_settings", "symproj", "echo X > .codebuddy/settings.json", True, None),
    ("link_claude_dir",     "symproj", "rm -rf .codebuddy", True, None),
    ("link_hooks_file",     "symhooks", "rm -f .codebuddy/hooks/git-guardrails.py", True, None),
    ("link_githooks",       "symgit", "rm -f .githooks/pre-commit", True, None),
    ("link_ctrl_shared",    "symproj", "rm -rf {T}/shared/.codebuddy/hooks", False, None),
]


def _bash_path(p):
    """[WorkBuddy 适配] 插进 bash 命令行的路径一律用正斜杠。

    上游在 macOS 上写这些用例，`{T}` 是 `/tmp/...`，插进去天然合法。真 Windows
    宿主上 `{T}` 是 `C:\\Users\\...`，原样插进命令行会被 bash 当成转义序列吃掉
    （`\\U`、`\\A`、`\\L`…），命令里的路径就变成了一个不含分隔符的畸形串，于是
    `in_project` 把项目外的路径判成项目内相对路径，控制组用例（本应放行）被误拒。
    转成正斜杠对 bash 与 NTFS 都合法，且不改变被测语义。"""
    return p.replace("\\", "/") if os.sep == "\\" else p


def _native_case(fx, command, expect_deny, env):
    def test(self):
        cwd = FX[fx]
        cmd = command.replace("{P}", _bash_path(cwd)).replace("{T}", _bash_path(_T))
        out = fire(cmd, cwd, cwd, env)
        if expect_deny:
            self.assertIn(DENY, out, f"not denied: {cmd!r}")
        else:
            self.assertEqual(out, "", f"not silent: {cmd!r}")
    return test


class NativeTest(unittest.TestCase):
    """The real hook as a subprocess, on this machine's own path rules."""

    def test_enc_cp1252_profile_name(self):
        # guard-stdin-codepage-fail-open: an `Á` in transcript_path (every event
        # carries it) holds a byte cp1252 cannot decode; under a strict decoder
        # the guard failed open. (Windows' own pipe default is surrogateescape,
        # which garbles instead — enc_cjk_pipe and enc_mojibake_* pin that.)
        out = fire("rm -rf .codebuddy/hooks", FX["proj"], FX["proj"],
                   {"PYTHONIOENCODING": "cp1252"},
                   {"transcript_path": "C:\\Users\\\u00c1lvaro\\.codebuddy\\t.jsonl"})
        self.assertIn(DENY, out)

    @_winsim.needs_symlink
    def test_scope_alias_project_dir(self):
        # rot-symlinked-claude-dir, the verifier's gap: CLAUDE_PROJECT_DIR spelled
        # through an alias AND `.codebuddy` linked out of the tree.
        a = FX["alias"]
        self.assertIn(DENY, fire(f"rm -rf {a}/.codebuddy/hooks", a, a))

    def test_scope_case_varied_cwd(self):
        # rotg-scope-case-sensitive-apfs, second vector: the EVENT cwd arrives
        # case-varied (bash keeps a `cd` as typed), so a relative write resolved
        # outside the project. Where the volume is case-sensitive the spelled cwd
        # does not exist and the guard falls back to its own cwd, which is right.
        cwd = os.path.join(_T, "PROJ")
        ev = {"tool_name": "Bash", "tool_input": {"command": "rm -rf .codebuddy/hooks"},
              "cwd": cwd}
        r = subprocess.run([sys.executable, GUARD], cwd=FX["proj"], capture_output=True,
                           input=json.dumps(ev).encode(), timeout=60,
                           env=_clean_env({"CLAUDE_PROJECT_DIR": FX["proj"]}))
        self.assertIn(DENY, r.stdout.decode())

    def test_scope_project_at_filesystem_root(self):
        # rot-project-at-filesystem-root: `_PROJECT + os.sep` was `//`.
        self.assertIn(DENY, fire("echo X > /.codebuddy/settings.json", "/", "/"))
        self.assertIn(DENY, fire("rm -rf .codebuddy/hooks", "/", "/"))

    @unittest.skipUnless(sys.platform == "darwin", "macOS firmlinks")
    def test_scope_firmlink(self):
        # rot-scope-string-compare: /System/Volumes/Data/<p> IS <p> on macOS, and
        # realpath does not say so.
        fl = "/System/Volumes/Data" + FX["proj"]
        if not (os.path.exists(fl) and os.path.samefile(fl, FX["proj"])):
            self.skipTest("no Data-volume firmlink for the fixture")
        self.assertIn(DENY, fire(f"rm -rf {fl}/.codebuddy/hooks", FX["proj"], FX["proj"]))


# #171 F4: where the guard reads `\` as a separator and drops an NTFS stream suffix (its
# own test, root-of-trust-guard.py: os.sep, or a Cygwin/MSYS runtime) these POSIX
# expectations do not hold; the win_bs_* / win_stream_* cases pin that host instead.
BACKSLASH_SEPARATES = os.sep == "\\" or sys.platform in ("cygwin", "msys")
POSIX_RULES = {"bs_posix_name_char", "bs_posix_redirect", "bs_sed_escaped_dot",
               "bs_sed_escaped_to", "bs_sed_escaped_both", "bs_perl_escaped",
               "bs_sed_escaped_gnu", "stream_ctrl_posix"}
posix_rules = unittest.skipIf(BACKSLASH_SEPARATES, "a backslash is a separator on this host; "
                                                   "the win_bs_* / win_stream_* cases pin it")

for _id, _fx, _cmd, _deny, _env in NATIVE:
    _case = _native_case(_fx, _cmd, _deny, _env)
    if _fx.startswith("sym"):                       # a fixture made of symlinks
        _case = _winsim.needs_symlink(_case)
    if _id in POSIX_RULES:
        _case = posix_rules(_case)
    setattr(NativeTest, f"test_{_id}", _case)


# ---- Windows: the real main() under ntpath -----------------------------------
def win_fire(command, cwd=None, project=None):
    """Drive the real main() under _winsim; return stdout (empty = allowed)."""
    cwd = cwd or FX["win"]
    project = project or FX["win"]
    mod = _winsim.load(GUARD)
    ev = {"tool_name": "Bash", "tool_input": {"command": command},
          "cwd": _winsim.to_win(cwd)}
    raw = json.dumps(ev, ensure_ascii=False).encode("utf-8")
    saved = sys.stdin, sys.stdout, {k: os.environ.get(k) for k in
                                    ("CLAUDE_PROJECT_DIR", "ALLOW_ROOT_OF_TRUST_WRITE")}
    sys.stdin = io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8")
    sys.stdout = io.StringIO()
    os.environ.pop("ALLOW_ROOT_OF_TRUST_WRITE", None)
    os.environ["CLAUDE_PROJECT_DIR"] = _winsim.to_win(project)
    try:
        try:
            mod.main()
        except Exception:
            # The hook fails open by design: a crash leaves stdout empty, which
            # reads exactly like "allowed". That equivalence is why a broken
            # simulation and a real hole look identical from the assertion. On
            # CI the crash (and the resolved scope) goes to the real stderr so
            # the log distinguishes the two; local runs stay quiet.
            if os.environ.get("WB_WINSIM_DEBUG") or os.environ.get("CI"):
                import traceback
                traceback.print_exc(file=sys.__stderr__)
                print(f"[winsim] _PROJECT={getattr(mod, '_PROJECT', '<none>')!r} "
                      f"_CWD={getattr(mod, '_CWD', '<none>')!r}", file=sys.__stderr__)
        return sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout = saved[0], saved[1]
        for k, v in saved[2].items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# (id, command, expect_deny) — {W} is the project's Windows spelling (C:\...),
# {M} its Git Bash spelling without the drive (/c{M} is the MSYS path), {O}/{OM}
# the same for a tree beside it.
WINDOWS = [
    ("win_bs_rel",          r"rm -rf '.codebuddy\hooks'", True),
    ("win_bs_abs",          r"rm -rf '{W}\.codebuddy\hooks'", True),
    ("win_bs_redirect",     r"echo x > '.codebuddy\settings.json'", True),
    ("win_bs_githooks",     r"rm -f '.githooks\pre-commit'", True),
    ("win_bs_githooks_mv",  r"mv '.githooks\pre-commit' /tmp/x", True),
    ("win_bs_mixed",        r"rm -rf '.codebuddy/hooks\git-guardrails.py'", True),
    ("win_bs_git_dash_c",   r"git -C '.codebuddy\hooks' rm -f git-guardrails.py", True),
    ("win_bs_envvar",       r'rm -rf "$CLAUDE_PROJECT_DIR\.codebuddy\hooks"', True),
    # NTFS default streams: the file's contents, the directory itself (rot-2)
    ("win_stream_data",     r"cp /dev/null '.codebuddy\settings.json::$DATA'", True),
    ("win_stream_redirect", r"echo x > '.codebuddy\settings.json::$DATA'", True),
    ("win_stream_abs",      r"echo x > '{W}\.codebuddy\settings.json::$DATA'", True),
    ("win_stream_drive_fwd", "echo x > 'C:{M}/.codebuddy/settings.json::$data'", True),
    ("win_stream_i30",      r"rm -rf '.codebuddy\hooks:$I30:$INDEX_ALLOCATION'", True),
    ("win_stream_index",    r"rm -rf '.githooks::$INDEX_ALLOCATION'", True),
    ("win_msys",            "rm -rf /c{M}/.codebuddy/hooks", True),
    ("win_msys_redirect",   "echo x > /c{M}/.codebuddy/settings.json", True),
    ("win_msys_upper",      "rm -rf /C{M}/.codebuddy/hooks", True),
    ("win_cygdrive",        "rm -rf /cygdrive/c{M}/.codebuddy/hooks", True),
    ("win_proc_cygdrive",   "rm -rf /proc/cygdrive/c{M}/.codebuddy/hooks", True),
    ("win_proc_cygdrive_redirect", "echo x > /proc/cygdrive/c{M}/.codebuddy/settings.json", True),
    ("win_msys_git_dash_c", "git -C /c{M}/.codebuddy/hooks rm -f git-guardrails.py", True),
    ("win_dash_c_compose",  "git -C .codebuddy -C hooks rm -f git-guardrails.py", True),
    ("win_dash_c_msys",     "git -C C:/x -C /c{M}/.codebuddy rm -rf hooks", True),
    ("win_exe_full_path",   r"'C:\Program Files\Git\usr\bin\rm.exe' -rf .codebuddy/hooks", True),
    ("win_ctrl_other_msys", "rm -rf /c{OM}/.codebuddy/hooks", False),
    ("win_ctrl_other_proc", "rm -rf /proc/cygdrive/c{OM}/.codebuddy/hooks", False),
    ("win_ctrl_stream_rules", r"echo x > '.codebuddy\rules\x.md::$DATA'", False),
    ("win_ctrl_stream_read", r"cat '.codebuddy\settings.json::$DATA'", False),
    ("win_ctrl_stream_docs", r"echo x > 'docs\notes.md::$DATA'", False),
    ("win_ctrl_other_bs",   r"rm -rf '{O}\.codebuddy\hooks'", False),
    ("win_ctrl_read",       r"cat '.codebuddy\hooks\git-guardrails.py'", False),
    ("win_ctrl_build",      r"rm -rf 'build\out'", False),
    ("win_ctrl_dash_c_out", "git -C .codebuddy -C ../docs rm -rf .", False),
]


def _win_case(command, expect_deny):
    def test(self):
        cmd = (command.replace("{W}", _winsim.to_win(FX["win"]))
                      .replace("{OM}", FX["winother"])
                      .replace("{O}", _winsim.to_win(FX["winother"]))
                      .replace("{M}", FX["win"]))
        out = win_fire(cmd)
        if expect_deny:
            self.assertIn(DENY, out, f"not denied under ntpath: {cmd!r}")
        else:
            self.assertEqual(out, "", f"not silent under ntpath: {cmd!r}")
    return test


@unittest.skipIf(os.sep == "\\",
                 "本类在 POSIX 宿主上用 ntpath 模拟 Windows（_winsim.to_win 给 "
                 "POSIX 路径加 C: 盘符）。真 Windows 宿主上夹具路径已自带盘符，"
                 "再次转换会产生 `/cC:\\...` 这类双重前缀，模拟层自身先失真。"
                 "真 Windows 的原生行为由 NativeTest 覆盖（os.sep=='\\\\' 时它才"
                 "是真实路径规则）。")
class WindowsTest(unittest.TestCase):
    """The real hook under ntpath, against a real fixture reached as C:\\..."""

    def test_win_compose_joins_with_forward_slash(self):
        # #151 claim 1 / rot-dash-c-ospath-join / rotg-a54-compose-dash-C: git
        # composes -C values with `/`; os.path.join gave `.codebuddy\hooks`.
        m = _winsim.load(GUARD)
        self.assertEqual(m._compose_dash_c([".codebuddy", "hooks"]), ".codebuddy/hooks")
        self.assertTrue(m.matches_root_of_trust(m._compose_dash_c([".codebuddy", "hooks"])))

    def test_win_project_at_drive_root(self):
        # rot-project-at-filesystem-root, Windows spelling: a project at `C:\`.
        m = _winsim.load(GUARD)
        m._PROJECT = m._CWD = "C:\\"
        self.assertTrue(m.in_project("C:/.codebuddy/settings.json"))
        self.assertTrue(m.in_project(".codebuddy\\hooks"))

    def test_win_msys_python_reads_backslash(self):
        # rot-2: the Cygwin/MSYS runtime's own Python has os.sep == "/", yet `\`
        # is a separator to the shell it serves; this machine's Python (Linux,
        # macOS) must not read it as one.
        m = _load_native()
        here = os.sep == "\\" or sys.platform in ("cygwin", "msys")
        for platform, expect in (("msys", True), ("cygwin", True), (sys.platform, here)):
            m.sys = types.SimpleNamespace(platform=platform)
            self.assertEqual(m.matches_root_of_trust(".codebuddy\\hooks"), expect, platform)
            self.assertEqual(m.matches_root_of_trust(".codebuddy\\settings.json::$DATA"),
                             expect, platform)
            self.assertEqual(m.matches_root_of_trust("s/\\.githooks/githooks/"),
                             expect, platform)


for _id, _cmd, _deny in WINDOWS:
    setattr(WindowsTest, f"test_{_id}", _win_case(_cmd, _deny))


# ---- scope, with no disk to lean on -------------------------------------------
def _load_native():
    import importlib.util
    spec = importlib.util.spec_from_file_location("rot_native", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@unittest.skipIf(os.sep == "\\",
                 "本类用 `/` 分隔的**不存在**路径验证大小写敏感卷（Linux CI）上的"
                 "字符串修复。`_under()` 用 `os.sep` 拼前缀，真 Windows 上 "
                 "os.sep=='\\\\'，与这里的 `/` 路径拼写前提冲突，判定必然失败——"
                 "这是测试的宿主假设，不是守卫缺陷。")
class ScopeWithoutDiskTest(unittest.TestCase):
    """The scope half on paths that do not exist, as a case-sensitive volume
    (Linux CI) sees a case-varied spelling. On macOS the fixture cases above
    can also be rescued by the file-identity fallback; these cannot, so each
    string repair is pinned on its own."""

    ROOT_ = "/nonexistent-rot-scope"

    def test_case_folded(self):
        m = _load_native()
        m._PROJECT = m._CWD = self.ROOT_ + "/Proj"
        self.assertTrue(m.is_protected(self.ROOT_ + "/PROJ/.codebuddy/hooks"))
        self.assertFalse(m.is_protected(self.ROOT_ + "/Projx/.codebuddy/hooks"))

    def test_unicode_form_folded(self):
        m = _load_native()
        m._PROJECT = m._CWD = self.ROOT_ + "/" + unicodedata.normalize("NFD", "\u00e9t\u00e9")
        self.assertTrue(m.is_protected(self.ROOT_ + "/\u00e9t\u00e9/.codebuddy/hooks"))   # NFC

    def test_path_as_named_counts(self):
        # `.codebuddy` resolves elsewhere (a link), but is named inside the project.
        m = _load_native()
        m._PROJECT = m._CWD = self.ROOT_ + "/proj"
        m._real = lambda p: p.replace("/proj/.codebuddy", "/shared/.codebuddy")
        self.assertTrue(m.is_protected(".codebuddy/hooks"))
        self.assertFalse(m.is_protected(self.ROOT_ + "/shared/.codebuddy/hooks"))

    def test_share_root_is_its_own_prefix(self):
        # rot-project-at-filesystem-root: a project at a UNC share root keeps
        # its trailing separator, so `root + os.sep` doubled it.
        m = _winsim.load(GUARD)
        m._PROJECT = m._CWD = "\\\\server\\share\\"
        self.assertTrue(m.in_project("\\\\server\\share\\.codebuddy\\settings.json"))


if __name__ == "__main__":
    unittest.main()
