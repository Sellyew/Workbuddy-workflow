"""The gates, the pre-commit hook and validate-setup outside the author's setup
(issue #171, group "scripts"): each case fails on 6cbebe1 and passes after the fix.

A clone's own path is spliced into every glob pattern, so a folder named
"Paper [2026]" read as a character class. A tree whose tracked paths differ only
by case or Unicode form is dirty for good on a macOS or Windows disk, and the
hook's stash could never pop; so is a CRLF blob under a later `eol=lf` rule, on
every disk. A stash push that made no stash had the hook pop the user's own.
validate-setup asked the shell's repository for the git identity, not its own.

Every git run gets the caller's environment WITHOUT its GIT_* variables (this suite
runs inside .githooks/pre-commit, which exports GIT_DIR and GIT_INDEX_FILE at the
user's repository) and with no global or system config, so a user's own
core.hooksPath or identity cannot reach a fixture.
"""
import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASH = shutil.which("bash")
HOOK = os.path.join(ROOT, ".githooks", "pre-commit")
_DROP = ("PYTHONIOENCODING", "PYTHONUTF8", "PYTHONWARNDEFAULTENCODING", "PYTHONWARNINGS",
         "CLAUDE_PROJECT_DIR", "BACKTEST_SKIP_HOOK_BATTERY", "SKIP_QUALITY_GATE", "HOOK_DIR")


def _env(**extra):
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("GIT_") and k != "GIT_EXEC_PATH") and k not in _DROP}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    env.update(extra)
    return env


def _run(cmd, cwd=None, input=None, timeout=300, **extra):
    """(exit code, stdout+stderr as UTF-8 text)."""
    r = subprocess.run(cmd, cwd=cwd, env=_env(**extra), input=input, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=timeout)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def _git(base, *args, input=None):
    r = subprocess.run(["git", "-C", base, *args], env=_env(), input=input, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace')}")
    return r.stdout


def _write(base, rel, content, mode=None):
    p = os.path.join(base, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(content if isinstance(content, bytes) else content.encode("utf-8"))
    if mode is not None:
        os.chmod(p, mode)
    return p


# ── the gates at a clone path with brackets ───────────────────────────────────

class BracketedClonePath(unittest.TestCase):
    """gates-glob-unescaped-root (G3): check-links and check-staleness matched nothing
    and passed on 0 files, check-spec-conformance found "no skills", and
    check-derived-counts counted 0 of everything."""

    # Each gate, and the count its pass line must show above zero (None: rc says it).
    GATES = (("check-links.py", r"\((\d+) files scanned\)"),
             ("check-staleness.py", r"(\d+) surfaces scanned"),
             ("check-spec-conformance.py", None),
             ("check-derived-counts.py", None))

    @classmethod
    def setUpClass(cls):
        # A clone of the WORKING TREE, not `git clone` of HEAD: under the pre-commit
        # hook HEAD still holds the gates being replaced, and the case would measure them.
        cls._td = tempfile.TemporaryDirectory()
        cls.repo = os.path.join(os.path.realpath(cls._td.name), "Paper [2026]", "repo")
        names = [n for n in _git(ROOT, "ls-files", "-z").decode("utf-8", "surrogateescape").split("\0") if n]
        kept = []
        for rel in names:
            src = os.path.join(ROOT, *rel.split("/"))
            if not os.path.isfile(src):          # deleted in the working tree
                continue
            dst = os.path.join(cls.repo, *rel.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            kept.append(rel)
        _git(cls.repo, "init", "-q")
        # update-index, not add: a force-added file the .gitignore names is tracked all the same.
        _git(cls.repo, "update-index", "--add", "-z", "--stdin",
             input="\0".join(kept).encode("utf-8", "surrogateescape") + b"\0")

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def gate(self, name):
        return _run([sys.executable, os.path.join(self.repo, "scripts", name)], cwd=self.repo)

    def test_the_gates_scan_files_and_pass(self):
        for name, count in self.GATES:
            with self.subTest(gate=name):
                rc, out = self.gate(name)
                self.assertEqual(rc, 0, out)
                if count:
                    m = re.search(count, out)
                    self.assertTrue(m and int(m.group(1)) > 0, out)

    def test_a_broken_link_is_still_found(self):
        # The false pass itself: the broken link read as "all ... resolve (0 files scanned)".
        readme = os.path.join(self.repo, "README.md")
        with open(readme, "rb") as f:
            kept = f.read()
        self.addCleanup(_write, self.repo, "README.md", kept)
        with open(readme, "ab") as f:
            f.write(b"\n[broken](does-not-exist-xyz.md)\n")
        rc, out = self.gate("check-links.py")
        self.assertEqual(rc, 1, out)
        self.assertIn("does-not-exist-xyz.md   [missing file]", out)


class EmptyScan(unittest.TestCase):
    """A scan that finds nothing is a broken gate (exit 2), not a clean tree (exit 0):
    whatever next hides the files from the glob cannot pass in silence again."""

    def test_nothing_to_scan_is_an_error(self):
        with tempfile.TemporaryDirectory() as td:
            base = os.path.realpath(td)
            for name in ("check-links.py", "check-staleness.py"):
                dst = os.path.join(base, "scripts", name)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(ROOT, "scripts", name), dst)
            _git(base, "init", "-q")
            for name in ("check-links.py", "check-staleness.py"):
                with self.subTest(gate=name):
                    rc, out = _run([sys.executable, os.path.join(base, "scripts", name)], cwd=base)
                    self.assertEqual(rc, 2, out)
                    self.assertIn("nothing was checked", out)


# ── .githooks/pre-commit on a tree whose paths collide ────────────────────────

@unittest.skipUnless(BASH, "needs bash")
class PreCommitCollidingPaths(unittest.TestCase):
    """precommit-stash-leak-on-colliding-paths (G5): on a macOS or Windows disk the pair
    is one file, the tree is dirty for good, the EXIT-trap pop failed, and every commit
    left a "pre-commit-gate" stash holding the user's unstaged work. On a Linux disk
    the pair is two files and the round trip succeeded: the warning is the pin there."""

    PAIRS = (("templates/session-log.md", "templates/Session-Log.md"),
             ("notes/" + unicodedata.normalize("NFC", "seção.md"),
              "notes/" + unicodedata.normalize("NFD", "seção.md")))

    def commit_with_hook(self, pair):
        tmp = os.path.realpath(tempfile.mkdtemp(prefix="precommit-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        src, clone, hooks = (os.path.join(tmp, d) for d in ("src", "clone", "hooks"))
        os.makedirs(src)
        _write(src, "README.md", "# Seed\n")
        # The gate suite is not under test: a stand-in that passes.
        _write(src, "scripts/backtest.sh", "#!/bin/sh\nexit 0\n", mode=0o755)
        _git(src, "init", "-q")
        _git(src, "add", "--", "README.md", "scripts/backtest.sh")
        args = []
        for i, rel in enumerate(pair):
            blob = _git(src, "hash-object", "-w", "--stdin", input=f"copy {i}\n".encode()).decode().strip()
            args += ["--add", "--cacheinfo", f"100644,{blob},{rel}"]
        # precomposeunicode off, or macOS git turns the NFD argument into the NFC one.
        _git(src, "-c", "core.precomposeunicode=false", "update-index", *args)
        _git(src, "commit", "-q", "--no-verify", "-m", "seed")
        rc, out = _run(["git", "clone", "-q", src, clone])   # "paths have collided" on APFS / NTFS
        self.assertEqual(rc, 0, out)
        os.makedirs(hooks)
        shutil.copy2(HOOK, os.path.join(hooks, "pre-commit"))
        os.chmod(os.path.join(hooks, "pre-commit"), 0o755)
        # The user's work: an unstaged edit, and a staged new file.
        _write(clone, "README.md", "# Seed\n\nUnstaged work in progress.\n")
        _write(clone, "notes.md", "x\n")
        _git(clone, "add", "--", "notes.md")
        rc, out = _run(["git", "-c", f"core.hooksPath={hooks}", "commit", "-m", "x"], cwd=clone)
        stashes = _git(clone, "stash", "list").decode("utf-8", "replace")
        with open(os.path.join(clone, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        return rc, out, stashes, readme

    def test_no_stash_is_left_behind(self):
        for pair in self.PAIRS:
            with self.subTest(pair=pair[1]):
                rc, out, stashes, readme = self.commit_with_hook(pair)
                self.assertEqual(stashes, "", out)
                self.assertIn("Unstaged work in progress.", readme, out)
                self.assertNotIn("could not auto-restore", out)
                self.assertIn("differ only by case or Unicode form", out)
                self.assertEqual(rc, 0, out)


def _hook_dir(tmp):
    hooks = os.path.join(tmp, "hooks")
    os.makedirs(hooks)
    shutil.copy2(HOOK, os.path.join(hooks, "pre-commit"))
    os.chmod(os.path.join(hooks, "pre-commit"), 0o755)
    return hooks


def _seed(repo):
    _write(repo, "README.md", "# Seed\n")
    # The gate suite is not under test: a stand-in that passes.
    _write(repo, "scripts/backtest.sh", "#!/bin/sh\nexit 0\n", mode=0o755)


@unittest.skipUnless(BASH, "needs bash")
class PreCommitDirtyForGood(unittest.TestCase):
    """precommit-stash-leak-on-dirty-tree (G5, the cause the collision pre-check does not
    cover): run.sh committed with CRLF before `*.sh text eol=lf` (the template's own rule)
    stays modified after `stash push --keep-index`, on every OS. The EXIT-trap pop failed,
    the commit went through, and each one moved the user's unstaged work into another
    "pre-commit-gate" stash. Restoring only the paths the stash had cleaned would still
    lose an edit to run.sh itself: the edited case pins that."""

    def commit_with_hook(self, edit_the_dirty_path):
        tmp = os.path.realpath(tempfile.mkdtemp(prefix="precommit-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        repo = os.path.join(tmp, "repo")
        _seed(repo)
        run = _write(repo, "run.sh", b"echo one\r\necho two\r\n")
        _write(repo, "old.txt", "kept\n")
        _git(repo, "init", "-q")
        _git(repo, "add", "--", "README.md", "scripts/backtest.sh", "run.sh", "old.txt")
        _git(repo, "commit", "-q", "--no-verify", "-m", "seed")
        _write(repo, ".gitattributes", "*.sh text eol=lf\n")
        _git(repo, "add", "--", ".gitattributes")
        _git(repo, "commit", "-q", "--no-verify", "-m", "attrs")
        # A changed mtime: while the stat cache vouches for run.sh, git never rehashes it.
        st = os.stat(run)
        os.utime(run, (st.st_atime, st.st_mtime - 100))
        self.assertIn(b"run.sh", _git(repo, "diff", "--name-only"))   # dirty before any edit
        hooks = _hook_dir(tmp)
        # The user's work: unstaged edits (and a deletion), and a staged new file.
        _write(repo, "README.md", "# Seed\n\nUnstaged work in progress.\n")
        if edit_the_dirty_path:
            _write(repo, "run.sh", b"echo one\r\necho two\r\necho three\r\n")
            os.remove(os.path.join(repo, "old.txt"))
        _write(repo, "notes.md", "x\n")
        _git(repo, "add", "--", "notes.md")
        rc, out = _run(["git", "-c", f"core.hooksPath={hooks}", "commit", "-m", "x"], cwd=repo)
        stashes = _git(repo, "stash", "list").decode("utf-8", "replace")
        return repo, rc, out, stashes

    def test_the_unstaged_work_stays_in_the_tree(self):
        for edited in (False, True):
            with self.subTest(edit_the_dirty_path=edited):
                repo, rc, out, stashes = self.commit_with_hook(edited)
                self.assertEqual(stashes, "", out)
                with open(os.path.join(repo, "README.md"), encoding="utf-8") as f:
                    self.assertIn("Unstaged work in progress.", f.read(), out)
                if edited:
                    with open(os.path.join(repo, "run.sh"), "rb") as f:
                        self.assertIn(b"echo three", f.read(), out)
                    self.assertFalse(os.path.exists(os.path.join(repo, "old.txt")), out)
                self.assertNotIn("could not auto-restore", out)
                self.assertIn("stays modified after stashing", out)
                self.assertEqual(rc, 0, out)
                # Restored to the working tree only: the commit carries the staged file alone.
                self.assertEqual(_git(repo, "show", "--format=", "--name-only", "HEAD"), b"notes.md\n")
                self.assertEqual(_git(repo, "diff", "--cached", "--name-only"), b"")


@unittest.skipUnless(BASH, "needs bash")
class PreCommitMadeNoStash(unittest.TestCase):
    """precommit-pops-a-stash-it-did-not-make: with nothing staged (`commit --amend`) and a
    submodule's own dirty content as the only unstaged change, `stash push` exits 0 having
    made no stash, and the EXIT trap popped the user's own newest stash into the tree."""

    def test_the_users_stash_is_left_alone(self):
        tmp = os.path.realpath(tempfile.mkdtemp(prefix="precommit-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        sub_src, repo = os.path.join(tmp, "subsrc"), os.path.join(tmp, "repo")
        _write(sub_src, "s.txt", "s\n")
        _git(sub_src, "init", "-q")
        _git(sub_src, "add", "--", "s.txt")
        _git(sub_src, "commit", "-q", "-m", "s")
        _seed(repo)
        _git(repo, "init", "-q")
        _git(repo, "add", "--", "README.md", "scripts/backtest.sh")
        _git(repo, "commit", "-q", "--no-verify", "-m", "seed")
        _git(repo, "-c", "protocol.file.allow=always", "submodule", "add", "-q", sub_src, "sub")
        _git(repo, "commit", "-q", "--no-verify", "-m", "sub")
        # The user's own stash, made long before this commit.
        _write(repo, "README.md", "# Seed\n\nOlder work, stashed.\n")
        _git(repo, "stash", "push", "-q", "-m", "users-own-stash")
        _write(repo, "sub/s.txt", "s\ndirty\n")
        self.assertEqual(_git(repo, "diff", "--name-only"), b"sub\n")
        hooks = _hook_dir(tmp)
        rc, out = _run(["git", "-c", f"core.hooksPath={hooks}", "commit", "--amend", "-m", "reworded"],
                       cwd=repo)
        stashes = _git(repo, "stash", "list").decode("utf-8", "replace")
        self.assertIn("users-own-stash", stashes, out)
        with open(os.path.join(repo, "README.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# Seed\n", out)
        self.assertEqual(rc, 0, out)


# ── validate-setup.sh ─────────────────────────────────────────────────────────

@unittest.skipUnless(BASH, "needs bash")
class ValidateSetupIdentity(unittest.TestCase):
    """validate-setup-identity-reads-cwd-repo (G8): run from outside its clone, a
    repo-local identity read as "not set", or another repository's was reported."""

    STUB = "#!/bin/sh\necho stub 1.0\n"

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = os.path.realpath(self._td.name)
        self.repo = os.path.join(self.tmp, "template")
        dst = os.path.join(self.repo, "scripts", "validate-setup.sh")
        os.makedirs(os.path.dirname(dst))
        shutil.copy2(os.path.join(ROOT, "scripts", "validate-setup.sh"), dst)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.name", "tester")
        _git(self.repo, "config", "user.email", "t@example.invalid")
        stubs = os.path.join(self.tmp, "bin")
        # `claude` is not consumed by validate-setup any more (the desktop app has
        # no command line), so this stub is inert for the three tests below. The
        # last rung of run-skill-eval's probe chain is pinned by
        # SkillEvalCliProbe.test_falls_back_to_claude_as_last_rung, not here.
        for name in ("claude", "xelatex", "quarto", "R", "gh"):
            _write(stubs, name, self.STUB, mode=0o755)
        self.home = os.path.join(self.tmp, "home")        # no ~/.gitconfig
        os.makedirs(self.home)
        self.path = stubs + os.pathsep + os.environ.get("PATH", "")

    def setup_out(self, cwd, **extra):
        rc, out = _run([BASH, os.path.join(self.repo, "scripts", "validate-setup.sh")], cwd=cwd,
                       PATH=self.path, SLIDE_QA_PYTHON="true", HOME=self.home,
                       XDG_CONFIG_HOME=os.path.join(self.home, ".config"), **extra)
        return out

    def test_reads_its_own_identity_from_outside_it(self):
        elsewhere = os.path.join(self.tmp, "elsewhere")
        os.makedirs(elsewhere)
        out = self.setup_out(elsewhere)
        self.assertIn("git user: tester <t@example.invalid>", out)
        self.assertNotIn("user.email not set", out)

    def test_another_repositorys_identity_is_not_its_own(self):
        other = os.path.join(self.tmp, "other")
        os.makedirs(other)
        _git(other, "init", "-q")
        _git(other, "config", "user.name", "otheruser")
        _git(other, "config", "user.email", "o@example.invalid")
        out = self.setup_out(other)
        self.assertIn("git user: tester <t@example.invalid>", out)
        self.assertNotIn("otheruser", out)

    def test_control_an_exported_copy_falls_back_to_the_global_identity(self):
        shutil.rmtree(os.path.join(self.repo, ".git"))
        glob_cfg = _write(self.tmp, "global.gitconfig", "[user]\n\tname = global\n\temail = g@example.invalid\n")
        out = self.setup_out(self.tmp, GIT_CONFIG_GLOBAL=glob_cfg)
        self.assertIn("git user: global <g@example.invalid>", out)


class RenderStampLineEndings(unittest.TestCase):
    """A CRLF render stamped here and checked out as LF is the same content.

    `.gitattributes` says `* text=auto eol=lf`, so the repository stores LF and a clone
    materialises LF — while Quarto on Windows writes CRLF. A fingerprint over raw bytes
    therefore records the working copy that produced the render, not the render: commit
    it and gate 6 (staleness) is red on every fresh clone, for a tree nobody touched.
    Two scripts compute that fingerprint independently and the comment in each says they
    must agree, so the cases below check the property and the agreement together.
    """

    CONTENT_LF = b"<html>\n<body>hi</body>\n</html>\n"
    CONTENT_CRLF = b"<html>\r\n<body>hi</body>\r\n</html>\r\n"

    def _mods(self):
        def load(path, name):
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        return (load(os.path.join(ROOT, "scripts", "stamp-render.py"), "probe_stamp_render"),
                load(os.path.join(ROOT, "scripts", "check-staleness.py"), "probe_check_staleness"))

    def test_the_two_implementations_agree_and_ignore_line_endings(self):
        stamp, stale = self._mods()
        with tempfile.TemporaryDirectory() as d:
            lf, crlf = os.path.join(d, "lf.html"), os.path.join(d, "crlf.html")
            _write(d, "lf.html", self.CONTENT_LF)
            _write(d, "crlf.html", self.CONTENT_CRLF)
            readings = {stamp.fp(pathlib.Path(lf)), stamp.fp(pathlib.Path(crlf)),
                        stale.render_fp(lf), stale.render_fp(crlf)}
        self.assertEqual(len(readings), 1,
                         f"one content read four ways gave {sorted(readings)} — the two "
                         f"scripts must hash the same bytes, and line endings are not content")

    def test_control_one_changed_byte_still_changes_both(self):
        # Without this the case above would also pass if both functions ignored the file.
        stamp, stale = self._mods()
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.html", self.CONTENT_LF)
            _write(d, "b.html", self.CONTENT_LF.replace(b"hi", b"ho"))
            a, b = os.path.join(d, "a.html"), os.path.join(d, "b.html")
            self.assertNotEqual(stamp.fp(pathlib.Path(a)), stamp.fp(pathlib.Path(b)))
            self.assertNotEqual(stale.render_fp(a), stale.render_fp(b))

    def test_a_stamp_survives_the_checkout_rewriting_line_endings(self):
        # PIN: on the script before the fix the second run exits 1 and reports the output
        # as modified, which is what every first clone of this repo would have seen.
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "scripts"))
            shutil.copyfile(os.path.join(ROOT, "scripts", "stamp-render.py"),
                            os.path.join(d, "scripts", "stamp-render.py"))
            script = os.path.join(d, "scripts", "stamp-render.py")
            for rel in ("guide/workflow-guide.qmd", "guide/workflow-guide.html",
                        "docs/workflow-guide.html"):
                _write(d, rel, self.CONTENT_CRLF.replace(b"<html>", b"<html data-src>"))
            rc, out = _run([sys.executable, script])
            self.assertEqual(rc, 0, out)
            # What git does on checkout: same content, LF on disk.
            for rel in ("guide/workflow-guide.qmd", "guide/workflow-guide.html",
                        "docs/workflow-guide.html"):
                _write(d, rel, self.CONTENT_LF.replace(b"<html>", b"<html data-src>"))
            rc, out = _run([sys.executable, script, "--check"])
        self.assertEqual(rc, 0, out)


# ── run-skill-eval.sh: which headless binary it calls ────────────────────────

@unittest.skipUnless(BASH, "needs bash")
class SkillEvalCliProbe(unittest.TestCase):
    """The harness hardcoded `claude`. On this platform the desktop app has no
    command line at all — headless runs come from a separately installed CLI whose
    binary is `codebuddy` (or `cbc`) — so the binary is now resolved, and the four
    flags the measurement depends on must survive that: `-p`, `--disallowedTools`,
    `--output-format text`, and `--setting-sources user` on the without-arm alone.
    """

    STUB = ("#!/bin/sh\n"
            'printf "%s|%s\\n" "${0##*/}" "$*" >> "$ARGV_LOG"\n'
            'case "$*" in\n'
            '  *"--setting-sources user"*) echo "no skill here" ;;\n'
            '  *"Reply with exactly: OK"*) echo OK ;;\n'
            '  *) echo "MARKER-PHRASE" ;;\n'
            "esac\n")

    # POSIX tools the harness shells out to. Resolving their directories lets PATH
    # exclude whatever CLI the host happens to have, so "no CLI installed" is real.
    TOOLS = ("timeout", "sed", "grep", "awk", "date", "basename", "seq",
             "dirname", "cat", "head", "mkdir", "python3", "python")

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = os.path.realpath(self._td.name)
        self.repo = os.path.join(self.tmp, "repo")
        with open(os.path.join(ROOT, "scripts", "run-skill-eval.sh"), encoding="utf-8") as f:
            _write(self.repo, "scripts/run-skill-eval.sh", f.read())
        # marker.txt sits beside the cases dir; one case, one assertion.
        _write(self.repo, "skills/demo/evals/marker.txt", "q\nMARKER-PHRASE\n")
        _write(self.repo, "skills/demo/evals/cases/c1.md",
               "## Prompt\nhi\n\n## Assert\n- MARKER-PHRASE\n")
        self.cases = os.path.join(self.repo, "skills", "demo", "evals", "cases")
        self.log = os.path.join(self.tmp, "argv.log")
        self.bin = os.path.join(self.tmp, "bin")
        os.makedirs(self.bin)
        self.path = os.pathsep.join([self.bin, self._tool_dirs()])

    def _tool_dirs(self):
        dirs = []
        for tool in self.TOOLS:
            found = shutil.which(tool)
            if found and os.path.dirname(found) not in dirs:
                dirs.append(os.path.dirname(found))
        return os.pathsep.join(dirs)

    def _stub(self, name):
        return _write(self.bin, name, self.STUB, mode=0o755)

    def _run_eval(self, **extra):
        return _run([BASH, os.path.join(self.repo, "scripts", "run-skill-eval.sh"),
                     "demo", self.cases], PATH=self.path, ARGV_LOG=self.log, **extra)

    def _calls(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log, encoding="utf-8") as f:
            # $0 is whatever the caller passed: a bare name from PATH, or an
            # absolute EVAL_CLI path (Windows keeps its backslashes).
            return [(os.path.basename(name), argv)
                    for name, argv in (line.rstrip("\n").split("|", 1) for line in f if line.strip())]

    def test_probes_cbc_and_keeps_the_flag_contract(self):
        self._stub("cbc")
        rc, out = self._run_eval()
        self.assertEqual(rc, 0, out)
        calls = self._calls()
        self.assertTrue(calls, "the harness never invoked the binary it probed")
        self.assertEqual({name for name, _ in calls}, {"cbc"}, out)
        for _, argv in calls:
            self.assertIn("-p ", argv + " ", out)
            self.assertIn("--disallowedTools Write,Edit,MultiEdit,NotebookEdit,Bash", argv)
            self.assertIn("--output-format text", argv)
        # The manipulation check is a difference between the arms: dropping the
        # flag from the with-arm makes every number below it meaningless. The case
        # loop's without-arm is also the only one that drops the `/skill ` prefix.
        self.assertTrue([a for _, a in calls
                         if a.startswith("-p /demo hi ") and "--setting-sources" not in a], out)
        self.assertTrue([a for _, a in calls
                         if a.startswith("-p hi --setting-sources user ")], out)

    def test_prefers_codebuddy_over_cbc(self):
        self._stub("codebuddy")
        self._stub("cbc")
        rc, out = self._run_eval()
        self.assertEqual(rc, 0, out)
        self.assertEqual({name for name, _ in self._calls()}, {"codebuddy"}, out)

    def test_eval_cli_override_wins(self):
        self._stub("codebuddy")
        other = self._stub("some-other-cli")
        rc, out = self._run_eval(EVAL_CLI=other)
        self.assertEqual(rc, 0, out)
        self.assertEqual({name for name, _ in self._calls()}, {"some-other-cli"}, out)

    def test_falls_back_to_claude_as_last_rung(self):
        # `claude` stays in the probe chain as the last resort: someone who already
        # has the upstream CLI installed should not have to install a second one.
        # Nothing else pins that rung — without this test, deleting it from
        # run-skill-eval.sh would leave the suite green.
        self._stub("claude")
        rc, out = self._run_eval()
        self.assertEqual(rc, 0, out)
        self.assertEqual({name for name, _ in self._calls()}, {"claude"}, out)

    def test_no_cli_exits_2_and_names_the_real_install(self):
        rc, out = self._run_eval()
        self.assertEqual(rc, 2, out)
        self.assertIn("no headless CLI", out)
        self.assertIn("@tencent-ai/codebuddy-code", out)
        self.assertEqual(self._calls(), [], out)


if __name__ == "__main__":
    unittest.main()
