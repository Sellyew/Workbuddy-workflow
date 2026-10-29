"""The harness itself: a case that cannot fail proves nothing. So this checks that a
module loaded through _winsim really sees Windows path rules, that the host-capability
skips in _winsim let a case run only where its mechanism can bite, and that the gate
runner, scripts/portability-tests.py, counts honestly and hands its cases a clean
git environment (issue #171)."""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import _winsim

SUITE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(SUITE))
GATE = os.path.join(ROOT, "scripts", "portability-tests.py")


def _clean(**extra):
    env = {k: v for k, v in os.environ.items()
           if (not k.startswith("GIT_") or k == "GIT_EXEC_PATH")
           and k not in ("HOOK_DIR", "PYTHONPATH", "PYTHONWARNINGS", "PYTHONUTF8")}
    env.update(extra)
    return env


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env=_clean(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull))


# The git reader check-repo-hygiene.py (tracked) and check-ledger-coverage.py
# (tracked_files) had at 08a7641: text=True, so the locale's code page on Windows.
PRE_FIX_READER = ('import subprocess\n'
                  'ROOT = "."\n'
                  'def tracked():\n'
                  '    r = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True)\n'
                  '    return [f for f in r.stdout.split("\\n") if f]\n'
                  'tracked_files = tracked\n')


class HarnessTest(unittest.TestCase):
    # [宿主适配] _winsim 的设计是「POSIX 宿主 + ntpath 模拟」：它的 _real() 把模拟
    # 路径还原成 pathlib.PosixPath 才落到真实文件系统，真 Windows 上这个类无法实例化。
    # 同一条限制见 P4 报告 §3.5。
    @_winsim.needs_winsim
    def test_loaded_module_sees_ntpath(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "probe.py")
            with open(src, "w", encoding="utf-8") as f:
                f.write("import os\nJOINED = os.path.join('a', 'b')\nSEP = os.sep\n")
            mod = _winsim.load(src)
        self.assertEqual(mod.SEP, "\\")
        self.assertEqual(mod.JOINED, "a\\b")

    def test_paths_round_trip(self):
        self.assertEqual(_winsim.to_posix(_winsim.to_win("/tmp/x/y")), "/tmp/x/y")


class HostMechanisms(unittest.TestCase):
    """Each skip in _winsim guards a mechanism; wherever it lets a case run, the
    mechanism must actually turn the old behaviour into a failure (#171 F3)."""

    @_winsim.needs_encoding_warning
    def test_strict_flags_turn_a_locale_default_read_into_an_error(self):
        r = subprocess.run([sys.executable, "-X", "warn_default_encoding", "-W", "error::EncodingWarning",
                            "-c", "import os\nopen(os.devnull).close()\n"],
                           capture_output=True, env=_clean(), timeout=60)
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"EncodingWarning", r.stderr)

    @_winsim.needs_getencoding
    def test_a_patched_getencoding_decides_subprocess_text(self):
        # Through _winsim.in_code_page, where the code-page cases patch it; this probe
        # once forced PYTHONUTF8=0 while two of them patched in UTF-8 mode (#171 F3).
        # U+201D as UTF-8 ends in 0x9D, which cp1252 does not define.
        code = ("import subprocess, sys\n"
                "subprocess.run([sys.executable, '-c', "
                "'import sys; sys.stdout.buffer.write(bytes([0xe2, 0x80, 0x9d]))'],"
                " capture_output=True, text=True)\n")
        r = _winsim.in_code_page("cp1252", code, env=_clean(), timeout=60)
        # [宿主适配] Python 3.14 起，text=True 的解码失败发生在 subprocess 的
        # reader 线程里：异常打到 stderr，但**不再让主进程退出码非零**（3.11/3.12
        # 上是非零）。这条自检要证明的是「cp1252 确实解不了 U+201D」，退出码只是
        # 当时顺手用的观察方式，换成直接看解码失败本身。
        self.assertIn(b"UnicodeDecodeError", r.stderr,
                      b"cp1252 cannot decode U+201D, so the read must fail: " + r.stderr)

    @_winsim.needs_getencoding
    def test_the_code_page_cases_bite_in_utf8_mode(self):
        # #171 F3: in UTF-8 mode (PYTHONUTF8=1, -X utf8, Python 3.15's default) subprocess
        # decodes as UTF-8 without asking locale.getencoding, and the two test_gitout
        # cases that patched it in-process passed on the pre-fix gates. Here they run in
        # UTF-8 mode against a stand-in that reads git's list as those gates did.
        cases = ["test_gitout.HygieneLocaleDecode.test_tracked_names_survive_a_cp1252_locale",
                 "test_gitout.LedgerGitOutput.test_a_non_ascii_hook_reads_as_tracked_under_cp1252"]
        run = ("import sys, unittest\n"
               "import test_gitout\n"
               "test_gitout.HYGIENE = test_gitout.LEDGER = sys.argv.pop(1)\n"
               "unittest.main(module=None, argv=['utf8'] + sys.argv[1:], verbosity=2)\n")
        with tempfile.TemporaryDirectory() as d:
            stub = os.path.join(d, "pre_fix_gate.py")
            with open(stub, "w", encoding="utf-8") as f:
                f.write(PRE_FIX_READER)
            r = subprocess.run([sys.executable, "-X", "utf8", "-c", run, stub, *cases],
                               cwd=SUITE, capture_output=True, env=_clean(), timeout=300)
        out = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
        for case in cases:
            # \r?$: unittest 的 verbosity=2 输出在 Windows 上是 CRLF，`$` 只认 \n，
            # 于是两条明明 FAIL 的用例一条都匹配不上——自检把自己误判成失败。
            self.assertRegex(out, rf"(?m)^{case.rsplit('.', 1)[1]} \(.*\) \.\.\. (FAIL|ERROR)\r?$", out)
        # ...and for the reason each pins: Á (C3 81) has no cp1252 reading, ã comes back as Ã£.
        self.assertIn("UnicodeDecodeError", out)
        self.assertIn("lembrete_sessÃ£o.py", out)

    @_winsim.needs_posix_sh
    def test_the_suite_runs_where_os_symlink_is_refused(self):
        # #171 F4: Windows without Developer Mode refuses os.symlink (WinError 1314).
        # test_rot's setUpModule made four links unguarded, so every case in the file
        # errored; notify.sh's fixture linked cat and tr. Here the link cases skip and
        # the rest run.
        refuse = ("import os, sys, unittest\n"
                  "def symlink(*a, **k):\n"
                  "    raise OSError(1314, 'A required privilege is not held by the client')\n"
                  "os.symlink = symlink\n"
                  "unittest.main(module=None, argv=['refused'] + sys.argv[1:], verbosity=2)\n")
        expect = [("test_rot", "NativeTest", "test_link_claude_hooks", "skipped"),
                  ("test_rot", "NativeTest", "test_scope_alias_project_dir", "skipped"),
                  ("test_rot", "NativeTest", "test_exe_ctrl_status", "ok"),
                  ("test_hooks", "NotifyWithoutJqAndOnWindows", "test_no_jq_still_notifies", "ok"),
                  ("test_gitout", "PreCommitQualityGate", "test_dangling_symlink_is_named_as_a_symlink",
                   "skipped")]
        r = subprocess.run([sys.executable, "-c", refuse, *(".".join(e[:3]) for e in expect)],
                           cwd=SUITE, capture_output=True, env=_clean(), timeout=300)
        out = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, out)
        for _, _, name, verdict in expect:
            self.assertRegex(out, rf"(?m)^{name} \(.*\) \.\.\. {verdict}", out)


class GateRunner(unittest.TestCase):
    """scripts/portability-tests.py: its own main(), handed a stand-in suite."""

    def run_gate(self, *cases):
        spec = importlib.util.spec_from_file_location("portability_gate", GATE)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in cases)
        out = io.StringIO()
        with mock.patch.object(unittest.defaultTestLoader, "discover", return_value=suite), \
                mock.patch.object(sys, "path", list(sys.path)), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = gate.main()
        return rc, out.getvalue()

    @_winsim.needs_winsim
    def test_cases_do_not_read_the_callers_index(self):
        # #171 G1: under `git commit -a`, `commit <paths>` or in a linked worktree the
        # pre-commit hook hands the gate an absolute GIT_INDEX_FILE (and GIT_DIR). A
        # script run in-process then had its fixture's `git -C tmp ls-files` list the
        # user's index. GIT_EXEC_PATH only says where git's own programs are: kept.
        with tempfile.TemporaryDirectory() as d:
            d = os.path.realpath(d)
            fixture, other = os.path.join(d, "fixture"), os.path.join(d, "other")
            for repo, name in ((fixture, "a.md"), (other, "b.md")):
                os.makedirs(repo)
                with open(os.path.join(repo, name), "w", encoding="utf-8") as f:
                    f.write("x\n")
                _git(repo, "init", "-q")
                _git(repo, "add", name)
            exec_path = subprocess.run(["git", "--exec-path"], capture_output=True,
                                       env=_clean()).stdout.decode().strip()
            seen = {}

            class Probe(unittest.TestCase):
                def test_ls_files_in_process(self):
                    r = _winsim.fsub.run(["git", "-C", fixture, "ls-files", "-z"], capture_output=True)
                    seen["listed"] = r.stdout.decode("utf-8").split("\0")[:-1]
                    seen["exec_path"] = os.environ.get("GIT_EXEC_PATH")

            hook = {"GIT_DIR": os.path.join(other, ".git"),
                    "GIT_INDEX_FILE": os.path.join(other, ".git", "index"),
                    "GIT_EXEC_PATH": exec_path}
            with mock.patch.dict(os.environ, hook):
                rc, out = self.run_gate(Probe)
        self.assertEqual(rc, 0, out)
        self.assertEqual(seen["listed"], ["a.md"], "the in-process git read the caller's index")
        self.assertEqual(seen["exec_path"], exec_path)

    def test_skipped_cases_are_counted_and_named(self):
        # #171 G6: 'OK (skipped=3)' was reported as 'ALL PASS (216 cases)'.
        class Probe(unittest.TestCase):
            def test_runs(self):
                pass

            @unittest.skip("no such mechanism on this host")
            def test_cannot_run(self):
                pass

        rc, out = self.run_gate(Probe)
        self.assertEqual(rc, 0, out)
        self.assertIn("portability-tests: ALL PASS (2 cases, 1 skipped)", out)
        self.assertRegex(out, r"(?m)^  skipped 1: no such mechanism on this host$")

    def test_a_run_where_everything_was_skipped_cannot_pass(self):
        # A suite that exercised nothing is the empty-scan defect this repo refuses
        # elsewhere: PASS there is a green light no case lit. Reported as CANNOT RUN.
        class Probe(unittest.TestCase):
            @unittest.skip("no such mechanism on this host")
            def test_cannot_run(self):
                pass

            @unittest.skip("no such mechanism on this host")
            def test_also_cannot_run(self):
                pass

        rc, out = self.run_gate(Probe)
        self.assertEqual(rc, 2, out)
        self.assertIn("portability-tests: CANNOT RUN", out)
        self.assertIn("every one of 2 cases was skipped", out)
        self.assertNotIn("ALL PASS", out)

    def test_a_partial_run_prints_the_ceiling_gate_11_parses(self):
        # The line is a contract: scripts/backtest.py reads the text before the colon
        # and reports it as PARTIAL. A skip with no ceiling line would let a run that
        # exercised a third of the suite be summarised as a plain PASS.
        class Probe(unittest.TestCase):
            def test_runs(self):
                pass

            @unittest.skip("no such mechanism on this host")
            def test_cannot_run(self):
                pass

            @unittest.skip("needs a host that allows os.symlink")
            def test_needs_symlink(self):
                pass

        rc, out = self.run_gate(Probe)
        self.assertEqual(rc, 0, out)
        self.assertIn("portability-ceiling: 2 of 3 cases not exercised on this host", out)

    def test_an_unexpected_success_fails_the_gate(self):
        # #171 G6: a case declared to fail that passes has lost what it pinned.
        class Probe(unittest.TestCase):
            @unittest.expectedFailure
            def test_declared_to_fail(self):
                pass

        rc, out = self.run_gate(Probe)
        self.assertEqual(rc, 1, out)
        self.assertIn("portability-tests: 1 of 1 cases FAILED", out)

    def test_a_clean_run_reads_as_before(self):
        # Control: with nothing skipped the verdict line is the one it always was.
        class Probe(unittest.TestCase):
            def test_runs(self):
                pass

        rc, out = self.run_gate(Probe)
        self.assertEqual(rc, 0, out)
        self.assertRegex(out, r"(?m)^portability-tests: ALL PASS \(1 cases\)$")
        # Control for the line above: nothing skipped, no ceiling to declare. If this
        # line appeared unconditionally it would say 0 of 1 and mean nothing.
        self.assertNotIn("portability-ceiling:", out)


if __name__ == "__main__":
    unittest.main()
