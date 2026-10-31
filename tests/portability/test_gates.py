"""The gates and the scripts around them (issue #171): a case either pins a fix (it
fails on the code before the fix and passes after, on Linux and macOS alike) or is
a control, an ordinary input that passes both.

Windows is reached three ways. _winsim loads a real module with ntpath swapped in
(path separators). A subprocess is handed what Windows hands it: a pipe in a
code page (PYTHONIOENCODING=cp1252 / cp932), a locale that decodes with cp1252
(locale.getencoding patched before the script runs; Python 3.11+), or every
locale-default text read and write made an error (-X warn_default_encoding with
EncodingWarning raised; 3.10+). A case that needs one of the last two skips where
the interpreter lacks it. Line endings, BOMs, spaces, case and the index are not
Windows-specific and are exercised as they are.

Every subprocess gets the caller's environment WITHOUT its GIT_* variables: this
suite runs inside .githooks/pre-commit, which exports GIT_DIR and GIT_INDEX_FILE
at the user's repository, and a fixture's `git add` would otherwise land there.
A script run in-process (_winsim.run_main) reads os.environ itself; the gate
runner, scripts/portability-tests.py, clears those variables before any case runs.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import _winsim

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, "scripts")
# A few fixtures are POSIX constructs: a stand-in `gh` with no .exe, a mode bit, a
# battery run with Git Bash's ln and uname faked. On a Windows host they would
# measure the fixture, and the real gates run there natively anyway.
POSIX_HOST = unittest.skipIf(os.name == "nt", "simulates Windows on a POSIX host; Windows runs the real thing")
_DROP = ("PYTHONIOENCODING", "PYTHONUTF8", "PYTHONWARNDEFAULTENCODING", "PYTHONWARNINGS",
         "CLAUDE_PROJECT_DIR", "BACKTEST_SKIP_HOOK_BATTERY", "HOOK_DIR", "FILE_ISSUE")


def _env(**extra):
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("GIT_") and k != "GIT_EXEC_PATH") and k not in _DROP}
    env.update(extra)
    return env


def _run(cmd, cwd=None, timeout=300, **extra):
    """(exit code, stdout+stderr as UTF-8 text)."""
    r = subprocess.run(cmd, cwd=cwd, env=_env(**extra), stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=timeout)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def _write(base, rel, content, mode=None):
    p = os.path.join(base, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(content if isinstance(content, bytes) else content.encode("utf-8"))
    if mode is not None:
        os.chmod(p, mode)
    return p


def _copy_script(base, name):
    dst = os.path.join(base, "scripts", name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(os.path.join(SCRIPTS, name), dst)
    return dst


def _git(base, *args):
    r = subprocess.run(["git", "-C", base, *args], env=_env(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace')}")
    return r.stdout.decode("utf-8", "replace")


def _load(name):
    """Import a script from scripts/ as a plain module (no simulation)."""
    path = os.path.join(SCRIPTS, name)
    spec = importlib.util.spec_from_file_location("gates_" + re.sub(r"\W", "_", name), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _bin(base, **scripts):
    """A directory of executable stand-ins, for the front of PATH."""
    d = os.path.join(base, "bin")
    os.makedirs(d, exist_ok=True)
    for name, body in scripts.items():
        _write(d, name, body, mode=0o755)
    return d


class Tmp(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = os.path.realpath(self._td.name)

    def tearDown(self):
        self._td.cleanup()


# ── check-staleness.py / stamp-render.sh ──────────────────────────────────────

class StalenessSkipList(unittest.TestCase):
    def test_anti_pattern_catalogue_is_skipped_on_windows(self):
        # staleness-skip-regex-slash-only, -vs-relpath, -backslash: SKIP is written with
        # '/', relpath gives '\' on Windows, so defect-library.md was scanned and failed.
        mod = _winsim.load(os.path.join(SCRIPTS, "check-staleness.py"))
        names = [s.replace("\\", "/") for s in mod.surfaces()]
        self.assertTrue(any(n.endswith("/README.md") for n in names), "the scan found nothing at all")
        self.assertEqual([n for n in names if n.endswith("defect-library.md")], [])


@unittest.skipUnless(shutil.which("bash") and (shutil.which("python3") or shutil.which("python")),
                     "stamp-render.sh is a bash shim that forwards to stamp-render.py")
class RenderStampLineEndings(Tmp):
    FILES = ("guide/workflow-guide.qmd", "guide/workflow-guide.html", "docs/workflow-guide.html")

    def setUp(self):
        super().setUp()
        _copy_script(self.tmp, "check-staleness.py")
        _copy_script(self.tmp, "stamp-render.sh")
        # The shim forwards to this file; without it the fixture cannot stamp at all.
        # (Until it became a shim, the .sh carried its own perl+shasum implementation
        # and the case skipped wherever those two were missing — which is every
        # Git-for-Windows install, so the Windows half of this contract went untested.)
        _copy_script(self.tmp, "stamp-render.py")
        _write(self.tmp, "guide/workflow-guide.qmd", "---\ntitle: Guide\n---\n\nOne line.\nAnother.\n")
        for p in self.FILES[1:]:
            _write(self.tmp, p, "<html>\n<p>One line.</p>\n</html>\n")

    def stamp(self):
        rc, out = _run(["bash", os.path.join(self.tmp, "scripts", "stamp-render.sh")])
        self.assertEqual(rc, 0, out)
        with open(os.path.join(self.tmp, ".render-stamp"), "rb") as f:
            return f.read()

    def staleness(self):
        return _run([sys.executable, os.path.join(self.tmp, "scripts", "check-staleness.py")])

    def to_crlf(self):
        for p in self.FILES:
            fp = os.path.join(self.tmp, *p.split("/"))
            with open(fp, "rb") as f:
                b = f.read()
            with open(fp, "wb") as f:
                f.write(b.replace(b"\n", b"\r\n"))

    @unittest.skipIf(os.name == "nt", "builds PATH by symlinking; Windows needs dev mode for that "
                                     "(the Windows half is covered by the cases above running there "
                                     "for real — this host has neither perl nor shasum)")
    def test_shim_stamps_without_perl_or_shasum(self):
        # stamp-render.sh 曾经自带一份指纹实现：`perl -pe` 归一行尾再接 `shasum -a 256`。
        # 当时的理由写在注释里 ——「有 shasum 的地方就有 perl，因为 shasum 本身就是 perl
        # 脚本」。这个等式在 Git for Windows 上不成立：WorkBuddy 自带的 PortableGit 里
        # perl 与 shasum 都不存在，只有 python。于是 README、staleness 的报错、new-skill
        # 的流程都在教人敲一条必然失败的命令，而盖戳失败会让 staleness 门永远红着。
        #
        # 现在它是转发壳。把 PATH 收窄到只剩它真正需要的两样（dirname 与解释器），
        # perl/shasum 就不可见 —— 实现若被改回自带指纹，这例会红。
        py = shutil.which("python3") or shutil.which("python")
        bash = shutil.which("bash")
        dirname = shutil.which("dirname")
        self.assertTrue(py and bash and dirname, "fixture needs bash, dirname and python")
        bin_ = os.path.join(self.tmp, "noperl")
        os.makedirs(bin_, exist_ok=True)
        for name, src in (("python3", py), ("dirname", dirname)):
            link = os.path.join(bin_, name)
            if not os.path.exists(link):
                os.symlink(src, link)
        rc, out = _run([bash, os.path.join(self.tmp, "scripts", "stamp-render.sh")],
                       cwd=self.tmp, PATH=bin_)
        self.assertEqual(rc, 0, f"shim failed without perl/shasum on PATH:\n{out}")
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, ".render-stamp")), out)

    def test_crlf_checkout_is_not_a_stale_render(self):
        # staleness-crlf-hash, staleness-false-fail-on-autocrlf: an autocrlf clone of
        # an up-to-date tree read as STALE-RENDER.
        self.stamp()
        self.to_crlf()
        rc, out = self.staleness()
        self.assertNotIn("STALE-RENDER", out)
        self.assertEqual(rc, 0, out)

    def test_stamp_made_on_crlf_matches_the_lf_stamp(self):
        # The other direction: a stamp written in a CRLF checkout turned LF CI red.
        lf = self.stamp()
        self.to_crlf()
        self.assertEqual(self.stamp(), lf)

    def test_control_a_real_edit_is_still_stale(self):
        self.stamp()
        with open(os.path.join(self.tmp, "guide", "workflow-guide.qmd"), "ab") as f:
            f.write(b"A new paragraph.\n")
        rc, out = self.staleness()
        self.assertIn("STALE-RENDER", out)
        self.assertEqual(rc, 1)

    def test_a_finding_survives_a_cp932_pipe(self):
        # gate-stdout-emdash-codepage: the finding's em dash turned it into "internal error".
        self.stamp()
        with open(os.path.join(self.tmp, "guide", "workflow-guide.qmd"), "ab") as f:
            f.write(b"A new paragraph.\n")
        rc, out = _run([sys.executable, os.path.join(self.tmp, "scripts", "check-staleness.py")],
                       PYTHONIOENCODING="cp932")
        self.assertIn("STALE-RENDER", out)
        self.assertEqual(rc, 1, out)


# ── check-links.py / check-skill-integrity.py ─────────────────────────────────

class LinkResolution(Tmp):
    def repo(self, tracked, untracked=None):
        _copy_script(self.tmp, "check-links.py")
        _copy_script(self.tmp, "check-skill-integrity.py")
        for rel, text in tracked.items():
            _write(self.tmp, rel, text)
        _git(self.tmp, "init", "-q")
        _git(self.tmp, "add", "--", *tracked)
        for rel, text in (untracked or {}).items():
            _write(self.tmp, rel, text)

    def links(self):
        return _run([sys.executable, os.path.join(self.tmp, "scripts", "check-links.py")])

    def integrity(self):
        return _run([sys.executable, os.path.join(self.tmp, "scripts", "check-skill-integrity.py")])

    def test_encoded_and_angle_bracket_targets(self):
        # links-percent-encoding-and-angle-brackets: %20 and <a b.md> are the two ways
        # CommonMark puts a space in a link; the first failed, the second was skipped.
        self.repo({
            "templates/A b.md": "# A\n\n## Seção\n",
            "templates/links.md": ("[x](A%20b.md#se%C3%A7%C3%A3o)\n\n[y](<A b.md#seção>)\n\n"
                                   "[z](A%20b.md#seção \"t\")\n\n[v](<A b.md>)\n\n[w](<Missing file.md>)\n"),
        })
        rc, out = self.links()
        self.assertEqual(rc, 1, out)
        broken = [ln for ln in out.splitlines() if "->" in ln]
        self.assertEqual(len(broken), 1, out)
        self.assertIn("Missing file.md", broken[0])
        rc, out = self.integrity()
        self.assertNotIn("does not exist", out)
        self.assertNotIn("not found in", out)
        self.assertEqual(rc, 0, out)

    def test_untracked_target_is_missing(self):
        # gates-read-disk-not-index: green locally, red in a fresh clone.
        self.repo({"README.md": "[the note](templates/nota.md)\n"},
                  untracked={"templates/nota.md": "# Nota\n"})
        rc, out = self.links()
        self.assertEqual(rc, 1, out)
        self.assertIn("templates/nota.md", out)
        # ...and says why: "[missing file]" for a file `ls` shows invited a fix to a
        # correct link.
        self.assertIn("[not tracked by git (git add it; a clone and GitHub do not have it)]", out)
        self.assertNotIn("[missing file]", out)

    def test_wrong_case_target_is_missing(self):
        # links-gate-case-insensitive-exists: README.MD for README.md resolves on
        # APFS and NTFS, 404s on GitHub. (On a case-sensitive disk it failed anyway.)
        self.repo({"README.md": "# Read me\n", "guide.md": "[r](README.MD)\n\n[s](Templates/)\n",
                   "templates/t.md": "# T\n"})
        rc, out = self.links()
        self.assertEqual(rc, 1, out)
        self.assertIn("README.MD   [letter case differs from the tracked README.md]", out)
        self.assertIn("Templates/   [letter case differs from the tracked templates]", out)

    def test_untracked_markdown_is_not_scanned(self):
        # An untracked copy (a worktree under .codebuddy/) is not the repository's to judge.
        self.repo({"README.md": "# Fine\n"},
                  untracked={".codebuddy/worktrees/w/notes.md": "[gone](nowhere.md)\n"})
        rc, out = self.links()
        self.assertEqual(rc, 0, out)

    def test_untracked_markdown_is_named_not_silently_skipped(self):
        # A new doc before `git add` was left out in silence, under a coverage line
        # that read as the whole tree. A nested checkout is its own repository's.
        self.repo({"README.md": "# Fine\n"},
                  untracked={"templates/new.md": "[gone](nowhere.md)\n",
                             ".codebuddy/worktrees/w/notes.md": "[gone](nowhere.md)\n"})
        _git(os.path.join(self.tmp, ".codebuddy", "worktrees", "w"), "init", "-q")
        rc, out = self.links()
        self.assertEqual(rc, 0, out)                 # the verdict is still the index's
        self.assertIn("1 untracked markdown file(s) not scanned (git add to check them): "
                      "templates/new.md", out)
        self.assertNotIn("worktrees", out)

    def test_directory_link_to_tracked_content_resolves(self):
        self.repo({"README.md": "[t](templates/) and [s](templates/sub/)\n",
                   "templates/sub/t.md": "# T\n"})
        rc, out = self.links()
        self.assertEqual(rc, 0, out)

    @_winsim.needs_winsim
    def test_same_verdicts_under_windows_paths(self):
        # Judging against the index compares '/' paths: without the os.sep swap every
        # file on Windows would read as untracked, scanned or linked.
        self.repo({"README.md": "[t](templates/)\n",
                   "templates/A b.md": "## Seção\n",
                   "templates/links.md": "[x](A%20b.md#seção)\n\n[c](a%20B.md#seção)\n\n[w](<Missing file.md>)\n"})
        code, out, err = _winsim.run_main(os.path.join(self.tmp, "scripts", "check-links.py"))
        self.assertEqual(code, 1, out + err)
        broken = sorted(ln.split("->")[1].split("[")[0].strip() for ln in out.splitlines() if "->" in ln)
        self.assertEqual(broken, ["Missing file.md", "a%20B.md#seção"], out)
        code, out, err = _winsim.run_main(os.path.join(self.tmp, "scripts", "check-skill-integrity.py"))
        self.assertEqual(code, 1, out + err)
        self.assertIn("'a B.md' differs in letter case from the tracked templates/A b.md", out)
        self.assertNotIn("'A b.md'", out)

    def test_report_naming_an_accented_file_survives_a_cp932_pipe(self):
        self.repo({"README.md": "[n](<Falta seção.md>)\n"})
        rc, out = _run([sys.executable, os.path.join(self.tmp, "scripts", "check-links.py")],
                       PYTHONIOENCODING="cp932")
        self.assertEqual(rc, 1, out)
        self.assertIn("Falta se", out)
        self.assertIn("missing file", out)
        self.assertNotIn("Traceback", out)

    def test_skill_integrity_advisory_survives_a_cp932_pipe(self):
        # A P2 is advice, exit 0 — its em dash crashed the print, exit 1.
        self.repo({".codebuddy/skills/demo/SKILL.md":
                   '---\nname: demo\nargument-hint: "[--frobnicate]"\nallowed-tools: ["Bash"]\n---\n\nDoes a thing.\n'})
        rc, out = _run([sys.executable, os.path.join(self.tmp, "scripts", "check-skill-integrity.py")],
                       PYTHONIOENCODING="cp932")
        self.assertIn("P2", out)
        self.assertIn("--frobnicate", out)
        self.assertEqual(rc, 0, out)

    def test_skill_integrity_judges_anchor_targets_against_the_index(self):
        self.repo({"templates/A b.md": "## Seção\n",
                   "templates/links.md": "[a](A%20B.md#seção)\n\n[b](nota.md#top)\n"},
                  untracked={"templates/nota.md": "# top\n"})
        rc, out = self.integrity()
        self.assertEqual(rc, 1, out)
        # A P1 names the reason, as check-links does: both files are on the disk.
        self.assertIn("'A B.md' differs in letter case from the tracked templates/A b.md", out)
        self.assertIn("'nota.md' is not tracked by git (git add it; a clone and GitHub do not have it)", out)
        self.assertNotIn("does not exist", out)


# ── BOM before frontmatter ────────────────────────────────────────────────────

# [WorkBuddy 适配] `effort` 是**技能加载器不消费**的字段（代理的 `parseAgentFile()`
# 读它并施加到子会话；技能的不读，所以对 SKILL.md 而言它确实没有语义）。它在这里的作用是让
# check-spec-conformance 确实产出一条 advisory，从而测到「cp932 管道下 advisory
# 表头不崩」。原来用 argument-hint / allowed-tools 触发，但这两个字段 WorkBuddy
# 会读（见 WB_FIELDS），按本平台语义报成「无对应语义」才是错的。
SKILL = ('---\nname: demo\ndescription: "A demo skill that does one thing."\n'
         'argument-hint: "[x]"\nallowed-tools: ["Bash", "Agent"]\neffort: high\n---\n\nUse the Agent tool.\n')


class FrontmatterBom(Tmp):
    def test_skill_integrity_reads_frontmatter_behind_a_bom(self):
        # bom-frontmatter-misreport: a false P0, and a rule passing check 5 by omission.
        fm, body = _load("check-skill-integrity.py").parse_frontmatter("\ufeff" + SKILL)
        self.assertEqual(fm.get("allowed-tools"), ["Bash", "Agent"])
        self.assertEqual(fm.get("name"), "demo")

    def test_spec_conformance_reads_frontmatter_behind_a_bom(self):
        _copy_script(self.tmp, "check-spec-conformance.py")
        _write(self.tmp, ".codebuddy/skills/demo/SKILL.md", b"\xef\xbb\xbf" + SKILL.encode())
        rc, out = _run([sys.executable, os.path.join(self.tmp, "scripts", "check-spec-conformance.py")])
        self.assertNotIn("no YAML frontmatter", out)
        self.assertEqual(rc, 0, out)

    def test_a_bom_does_not_hide_the_first_heading(self):
        # The same BOM in front of a first '# Heading' kept the '#' off the line
        # start: both link gates called a valid link to its anchor broken.
        gates = ("check-links.py", "check-skill-integrity.py")
        for s in gates:
            _copy_script(self.tmp, s)
        _write(self.tmp, "templates/A.md", b"\xef\xbb\xbf# Intro\n\nText, and [back](#intro).\n\n## Second\n")
        _write(self.tmp, "templates/l.md", "[a](A.md#intro) and [b](A.md#second)\n")
        _git(self.tmp, "init", "-q")
        _git(self.tmp, "add", "--", "templates/A.md", "templates/l.md")
        for s in gates:
            rc, out = _run([sys.executable, os.path.join(self.tmp, "scripts", s)])
            self.assertNotIn("intro", out, s)
            self.assertEqual(rc, 0, (s, out))

    def test_spec_conformance_survives_a_cp932_pipe(self):
        # gate-stdout-emdash-codepage: the advisory header's em dash is not in cp932.
        _copy_script(self.tmp, "check-spec-conformance.py")
        _write(self.tmp, ".codebuddy/skills/demo/SKILL.md", SKILL)
        rc, out = _run([sys.executable, os.path.join(self.tmp, "scripts", "check-spec-conformance.py")],
                       PYTHONIOENCODING="cp932")
        self.assertIn("portability advisory", out)
        self.assertEqual(rc, 0, out)


# ── validate-findings.py ──────────────────────────────────────────────────────

_WARN = ["-X", "warn_default_encoding", "-W", "error::EncodingWarning"]
FINDING = {"file": "paper.md", "line": 1, "locus": "Results \u00b61", "lens": "results",
           "severity": "minor", "rule": "r", "claim": "c",
           "evidence": "The text reads \"effect is large \u2014 roughly 12 percent\" there.",
           "failing_case": "f", "suggested_fix": "s", "mechanical": False, "confidence": "high"}


class FindingIds(Tmp):
    def test_path_spelling_does_not_split_an_id(self):
        # finding-id-separator-sensitive
        fid = _load("validate-findings.py").finding_id
        want = fid("Slides/deck.tex", 12, "frame-3")
        self.assertEqual(want, "cd7e3f99d57dd867376fdffa97d2199a4d6ac496")   # canonical ids unchanged
        self.assertEqual(fid("Slides\\deck.tex", 12, "frame-3"), want)
        self.assertEqual(fid("./Slides/deck.tex", 12, "frame-3"), want)

    def test_check_quotes_reads_the_file_the_id_names(self):
        # The id folded Slides\deck.tex into Slides/deck.tex; --check-quotes joined
        # the raw spelling to --root and answered "file not found" on macOS and Linux.
        _write(self.tmp, "Slides/deck.tex", "The effect is large here.\n")
        vf = os.path.join(SCRIPTS, "validate-findings.py")
        for spelling in ("Slides\\deck.tex", "./Slides/deck.tex", "Slides/sub/../deck.tex"):
            f = dict(FINDING, file=spelling, evidence='The slide reads "The effect is large" there.')
            p = _write(self.tmp, "f.json", json.dumps([f]))
            rc, out = _run([sys.executable, vf, "--check-quotes", p, "--root", self.tmp])
            self.assertEqual(rc, 0, (spelling, out))
            self.assertIn("quotes OK (1 quote(s) checked)", out, spelling)

    def test_mixed_spelling_pair_is_a_duplicate(self):
        a = dict(FINDING, file="Slides/deck.tex", lens="visual")
        b = dict(FINDING, file="Slides\\deck.tex", lens="pedagogy")
        p = _write(self.tmp, "f.json", json.dumps([a, b]))
        rc, out = _run([sys.executable, os.path.join(SCRIPTS, "validate-findings.py"), "--fill-ids", p])
        self.assertEqual(rc, 1, out)
        self.assertIn("duplicate of findings[0]", out)


class FindingsQuoteCoverage(Tmp):
    """quotes-check-vacuous-pass: a quote gate that checked nothing reported OK.

    Evidence written as prose extracts no quotation, so the gate had no input: it
    printed "quotes OK (0 quote(s) checked)" and exited 0. Beating the invented-
    quotation check was therefore cheaper by not quoting than by lying. The two
    zeros are now different: no quote written is a failure, every quote left
    unchecked because its file could not be read is still a report, not a failure.
    """

    def _report(self, name, *evidence):
        rows = [dict(FINDING, line=i + 1, evidence=e) for i, e in enumerate(evidence)]
        _write(self.tmp, name, json.dumps(rows, ensure_ascii=False))
        return self.tmp, os.path.join(self.tmp, name)

    def test_prose_evidence_fails_instead_of_passing_vacuously(self):
        # quotes-check-vacuous-pass
        _write(self.tmp, "paper.md", "The estimated effect is large.\n")
        _, p = self._report("f.json", "The sentence on line 1 overstates the effect.")
        rc, out = _run([sys.executable, os.path.join(SCRIPTS, "validate-findings.py"),
                        "--check-quotes", p, "--root", self.tmp])
        self.assertEqual(rc, 1, out)
        self.assertIn("0 quotation(s) to check", out)
        self.assertNotIn("quotes OK", out)

    def test_one_quoted_finding_out_of_two_passes_but_reports_coverage(self):
        # Control, and the deliberate limit: the gate fails a report that quotes
        # nothing, not a report that leaves one finding unquoted. It says how many.
        _write(self.tmp, "paper.md", "The estimated effect is large \u2014 roughly 12 percent.\n")
        _, p = self._report(
            "f.json",
            'Written: "effect is large \u2014 roughly 12 percent".',
            "The second finding is stated in prose only.")
        rc, out = _run([sys.executable, os.path.join(SCRIPTS, "validate-findings.py"),
                        "--check-quotes", p, "--root", self.tmp])
        self.assertEqual(rc, 0, out)
        self.assertIn("1 of 2 finding(s) quoted", out)
        self.assertIn("no quotation: findings[1]", out)

    def test_unreadable_source_stays_a_report_not_a_failure(self):
        # Control: the other zero. A binary file leaves its quotes unchecked, and a
        # host without poppler has the same shape for PDFs — failing here would fail
        # every review on that machine, which is not what the vacuous-pass fix means.
        _write(self.tmp, "scan.bin", b"\x00\x01\x02binary, not text\x00")
        _, p = self._report("f.json", 'The line reads "a quotation nobody can read here".')
        with open(p, encoding="utf-8") as f:
            rows = json.load(f)
        rows[0]["file"] = "scan.bin"
        _write(self.tmp, "f.json", json.dumps(rows, ensure_ascii=False))
        rc, out = _run([sys.executable, os.path.join(SCRIPTS, "validate-findings.py"),
                        "--check-quotes", p, "--root", self.tmp])
        self.assertEqual(rc, 0, out)
        self.assertIn("left unchecked", out)

    def test_empty_report_is_not_a_vacuous_pass(self):
        # Control: zero findings is a clean manuscript, not a review that dodged the
        # check. Nothing to quote is different from refusing to quote.
        _write(self.tmp, "paper.md", "Clean.\n")
        _, p = self._report("f.json")
        rc, out = _run([sys.executable, os.path.join(SCRIPTS, "validate-findings.py"),
                        "--check-quotes", p, "--root", self.tmp])
        self.assertEqual(rc, 0, out)
        self.assertIn("quotes OK (0 quote(s) checked)", out)


class FindingsEncoding(Tmp):
    def test_fill_then_check_quotes_on_a_windows_code_page(self):
        # validate-findings-locale-read: the report and stdin were read, and the filled
        # report written, in the locale; a true quote read as invented, a '¶' locus
        # broke its own id. Not skipped below Python 3.10: the cp1252 pipe still pins
        # the stdout half there; only the file-read half needs EncodingWarning (#171 F3).
        _write(self.tmp, "paper.md", "The estimated effect is large \u2014 roughly 12 percent "
                                     "of the baseline for S\u00e3o Paulo firms.\n")
        block = _write(self.tmp, "block.json", json.dumps([FINDING], ensure_ascii=False))
        vf = os.path.join(SCRIPTS, "validate-findings.py")
        r = subprocess.run([sys.executable, *_WARN, vf, "--fill-ids", block], capture_output=True,
                           env=_env(PYTHONIOENCODING="cp1252", PYTHONUTF8="0"), timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace"))
        filled = _write(self.tmp, "r.json", r.stdout)
        with open(filled, encoding="utf-8") as f:
            got = json.load(f)[0]["id"]
        self.assertEqual(got, hashlib.sha1("paper.md:1:Results \u00b61".encode()).hexdigest())
        rc, out = _run([sys.executable, *_WARN, vf, "--check-quotes", filled, "--root", self.tmp],
                       PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        self.assertEqual(rc, 0, out)
        self.assertIn("quotes OK", out)


# ── file-issue.py ─────────────────────────────────────────────────────────────

FAKE_GH = """#!/usr/bin/env bash
echo "ARGS $*" >> "$FAKE_GH_LOG"
case "$1 ${2:-}" in
  "issue list")   cat "$FAKE_GH_HITS"; exit 0 ;;
  "issue create") echo "https://github.com/o/r/issues/99"; exit 0 ;;
esac
exit 1
"""
# Windows decodes a child's text output with the ANSI code page: patch the locale
# the subprocess module asks, then run the script.
CP1252_LOCALE = ("import locale, runpy, sys\n"
                 "locale.getencoding = lambda: 'cp1252'\n"
                 "locale.getpreferredencoding = lambda do_setlocale=True: 'cp1252'\n"
                 "sys.argv = sys.argv[1:]\n"
                 "runpy.run_path(sys.argv[0], run_name='__main__')\n")


@POSIX_HOST
class FileIssueEncoding(Tmp):
    TITLE = "Standard errors in Table 3 disagree with the log"

    def gh(self, title):
        fake = _bin(self.tmp, gh=FAKE_GH)
        hits = _write(self.tmp, "hits.json",
                      json.dumps([{"number": 31, "title": title, "state": "CLOSED", "url": "u31"}],
                                 ensure_ascii=False))            # gh prints raw UTF-8
        body = _write(self.tmp, "body.md", "Standard errors in Table 3 do not match the log.\n")
        log = os.path.join(self.tmp, "gh.log")
        env = dict(PATH=fake + os.pathsep + os.environ.get("PATH", ""), FAKE_GH_HITS=hits,
                   FAKE_GH_LOG=log, PYTHONUTF8="0")
        return body, log, env

    def created(self, log):
        with open(log, encoding="utf-8", errors="replace") as f:
            return sum(1 for ln in f if ln.startswith("ARGS issue create"))

    @_winsim.needs_getencoding
    def test_look_alike_with_curly_quotes_is_listed_not_lost(self):
        # file-issue-gh-decode: the ” in a candidate's title is not cp1252; the decode
        # failed, and on Windows the check read it as "no candidates" and filed.
        body, log, env = self.gh("Table 3 \u201cSEs\u201d disagree")
        fi = os.path.join(SCRIPTS, "file-issue.py")
        rc, out = _run([sys.executable, "-c", CP1252_LOCALE, fi, "--title", self.TITLE, "--body-file", body], **env)
        self.assertEqual(rc, 3, out)
        self.assertIn("#31 [closed] Table 3 \u201cSEs\u201d disagree", out)
        self.assertEqual(self.created(log), 0)

    def test_listing_survives_a_cp932_pipe(self):
        # The 'Possible duplicates —' line: no em dash in cp932, so any candidate crashed it.
        body, log, env = self.gh("Table 3 SEs disagree")
        fi = os.path.join(SCRIPTS, "file-issue.py")
        rc, out = _run([sys.executable, fi, "--title", self.TITLE, "--body-file", body],
                       PYTHONIOENCODING="cp932", **env)
        self.assertEqual(rc, 3, out)
        self.assertIn("#31 [closed] Table 3 SEs disagree", out)
        self.assertEqual(self.created(log), 0)


# ── slide-qa.py ───────────────────────────────────────────────────────────────

SLIDE_QA_RUNNER = r'''
import importlib.util, sys, types
script, deck, out, title, verdict = sys.argv[1:6]
sys.modules["playwright"] = types.ModuleType("playwright")      # measured below instead
spec = importlib.util.spec_from_file_location("slide_qa", script)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def measure_deck(html, out_dir, tol, screenshots):
    bad = verdict != "ok"
    return ([{"n": 1, "h": 0, "v": 0, "title": title, "verdict": verdict,
              "overflow_px": {"bottom": 5 if bad else 0, "right": 0, "top": 0, "left": 0},
              "offenders": [{"element": "p", "by_px": 5, "text": title}] if bad else [],
              "clipped": [], "images_not_loaded": [], "broken_images": [], "broken_assets": [],
              "screenshot": None, "defects": ["overflow"] if bad else []}],
            "stub", "none", (1050, 700), {"missing": [], "wrong_case": []})
m.measure_deck = measure_deck
sys.argv = [script, deck, "--out", out, "--no-screenshots"]
sys.exit(m.main())
'''


class SlideQaEncoding(Tmp):
    def run_qa(self, title, verdict):
        runner = _write(self.tmp, "runner.py", SLIDE_QA_RUNNER)
        deck = _write(self.tmp, "deck.html", "<html></html>\n")
        out = os.path.join(self.tmp, "out")
        rc, text = _run([sys.executable, *_WARN, runner, os.path.join(SCRIPTS, "slide-qa.py"), deck, out,
                         title, verdict], PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        return rc, text, os.path.join(out, "report.md")

    def test_clean_deck_exits_0_on_a_cp1252_pipe(self):
        # slide-qa-arrow-print: '→' is in no Windows ANSI code page; a clean deck exited 1.
        rc, out, md = self.run_qa("Intro", "ok")
        self.assertEqual(rc, 0, out)
        with open(md, "rb") as f:
            self.assertIn("1050\u00d7700", f.read().decode("utf-8"))

    @_winsim.needs_encoding_warning
    def test_report_is_utf8_whatever_the_locale(self):
        # report.md was written in the locale: cp1252 bytes, or empty on a β title.
        rc, out, md = self.run_qa("\u03b2 \u2192 estimates", "overflow")
        self.assertEqual(rc, 1, out)
        self.assertTrue(os.path.exists(md), out)
        with open(md, "rb") as f:
            self.assertIn("\u03b2 \u2192 estimates", f.read().decode("utf-8"))


# ── validate-setup.sh ─────────────────────────────────────────────────────────

class ValidateSetup(Tmp):
    # Stand-ins, so the tool checks answer at once instead of starting the real ones.
    STUB = "#!/bin/sh\necho stub 1.0\n"

    def setUp(self):
        super().setUp()
        self.repo = os.path.join(self.tmp, "template")
        _copy_script(self.repo, "validate-setup.sh")
        _write(self.repo, ".githooks/pre-commit", "#!/usr/bin/env bash\nexit 0\n", mode=0o755)
        _write(self.repo, ".codebuddy/hooks/guard.py", "print()\n", mode=0o644)     # run as `python3 <file>`
        _write(self.repo, ".codebuddy/hooks/notify.sh", "#!/usr/bin/env bash\n", mode=0o755)
        _git(self.repo, "init", "-q")
        stubs = _bin(self.tmp, xelatex=self.STUB, quarto=self.STUB, R=self.STUB, gh=self.STUB)
        self.path = stubs + os.pathsep + os.environ.get("PATH", "")

    def setup_out(self, cwd):
        rc, out = _run([shutil.which("bash"), os.path.join(self.repo, "scripts", "validate-setup.sh")],
                       cwd=cwd, PATH=self.path, SLIDE_QA_PYTHON="true")
        return out

    @_winsim.needs_posix_sh
    def test_equivalent_hookspath_spelling_is_active(self):
        # validate-setup-hookspath-string-equality
        for hp in ("./.githooks", ".githooks/", os.path.join(self.repo, ".githooks")):
            _git(self.repo, "config", "core.hooksPath", hp)
            out = self.setup_out(self.repo)
            self.assertIn("gate active", out, hp)
            self.assertNotIn("not activated", out, hp)

    @_winsim.needs_posix_sh
    def test_reads_its_own_repository_from_outside_it(self):
        # validate-setup-reads-cwd-repo, direction 1: run from a directory that is no repo.
        _git(self.repo, "config", "core.hooksPath", ".githooks")
        elsewhere = os.path.join(self.tmp, "elsewhere")
        os.makedirs(elsewhere)
        self.assertIn("gate active", self.setup_out(elsewhere))

    @_winsim.needs_posix_sh
    def test_another_repositorys_setting_is_not_its_own(self):
        # validate-setup-reads-cwd-repo, direction 2: the shell's repo has the gate on.
        other = os.path.join(self.tmp, "other")
        os.makedirs(os.path.join(other, ".githooks"))
        _git(other, "init", "-q")
        _git(other, "config", "core.hooksPath", ".githooks")
        out = self.setup_out(other)
        self.assertIn("not activated", out)
        self.assertNotIn("gate active", out)

    @POSIX_HOST
    def test_exec_bit_is_checked_only_where_it_matters(self):
        # validate-setup-false-exec-bit-warning: a 0644 .py hook run by python3 is fine.
        out = self.setup_out(self.repo)
        self.assertNotIn("hook script(s) not executable", out)
        self.assertIn("All hook scripts are executable", out)
        os.chmod(os.path.join(self.repo, ".codebuddy", "hooks", "notify.sh"), 0o644)
        self.assertIn("1 hook script(s) not executable", self.setup_out(self.repo))


# ── sync_to_docs.sh ───────────────────────────────────────────────────────────

class SyncToDocs(Tmp):
    def deploy(self, name, *decks):
        _copy_script(self.tmp, "sync_to_docs.sh")
        for d in decks:
            _write(self.tmp, "Quarto/" + d, "---\ntitle: x\n---\n")
        os.makedirs(os.path.join(self.tmp, "Figures"))
        os.makedirs(os.path.join(self.tmp, "docs"))
        log = os.path.join(self.tmp, "quarto.log")
        stub = _bin(self.tmp, quarto='#!/bin/sh\nprintf \'%s|\' "$@" >> "$QLOG"\n')
        rc, out = _run([shutil.which("bash"), os.path.join(self.tmp, "scripts", "sync_to_docs.sh"), name],
                       PATH=stub + os.pathsep + os.environ.get("PATH", ""), QLOG=log)
        rendered = ""
        if os.path.exists(log):
            with open(log, encoding="utf-8") as f:
                rendered = f.read()
        return rc, out, rendered

    @_winsim.needs_posix_sh
    def test_lecture_name_with_a_space(self):
        # sync-to-docs-unquoted-arg: 'Aula 1' split in two; with a stray 1.qmd it
        # rendered THAT deck.
        rc, out, rendered = self.deploy("Aula 1", "Aula 1.qmd", "1.qmd")
        self.assertEqual(rc, 0, out)
        self.assertEqual(rendered, "render|Aula 1.qmd|")

    @_winsim.needs_posix_sh
    def test_control_exact_name_still_wins_over_a_suffixed_one(self):
        rc, out, rendered = self.deploy("Lecture2", "Lecture2.qmd", "Lecture2_Intro.qmd")
        self.assertEqual(rc, 0, out)
        self.assertEqual(rendered, "render|Lecture2.qmd|")


# ── hook-battery.sh ───────────────────────────────────────────────────────────

BATTERY = os.path.join(SCRIPTS, "hook-battery.sh")
SYM_CASES = ("c57", "c58", "c59", "c60", "c61", "c62", "c63", "c64")


def _battery_cases():
    # The count check-derived-counts.py takes: expect_ call sites.
    with open(BATTERY, encoding="utf-8") as f:
        return len(re.findall(r'^[ \t]*expect_(?:deny|silent|contains)[ \t]', f.read(), re.M))


class BatteryEventRewrite(Tmp):
    """_ev (PR #152) rewrites an event's POSIX paths to the native spelling under Git
    Bash. The paths must go in literally: '&' in a replacement and '[ ]' or a trailing
    '$' in a pattern are sed syntax (battery-ev-sed-metachar)."""
    FAKE_CYGPATH = ('#!/bin/sh\n[ "$1" = "-m" ] && shift\n'
                    'case "$1" in /c/*) printf \'C:/%s\\n\' "${1#/c/}" ;;'
                    ' /*) printf \'C:/msys64%s\\n\' "$1" ;; *) printf \'%s\\n\' "$1" ;; esac\n')
    DRIVER = 'TMP="$1"; ROOT="$2"; . "$3"; cat "$(_ev "$4")"\n'

    @_winsim.needs_posix_sh
    def test_paths_are_rewritten_literally(self):
        with open(BATTERY, encoding="utf-8") as f:
            m = re.search(r"^if command -v cygpath >/dev/null 2>&1; then\n.*?^fi$", f.read(), re.S | re.M)
        self.assertIsNotNone(m, "hook-battery.sh has no cygpath event-rewrite block")
        block = _write(self.tmp, "block.sh", m.group(0) + "\n")
        driver = _write(self.tmp, "driver.sh", self.DRIVER)
        fake = _bin(self.tmp, cygpath=self.FAKE_CYGPATH)
        for tmp, root in (("/tmp/T&mp/hb.1", "/c/Users/R&D/proj"),
                          ("/tmp/hb.2", "/c/Users/dev/proj[1]"),
                          ("/tmp/hb.3", "/c/Users/dev/proj$"),
                          ("/tmp/a.b*c", "/c/Users/x^y/proj (1) {2} +3.v")):
            ev = _write(self.tmp, "ev.json", '{"cwd":"%s","f":"%s/repo","r":"%s/.codebuddy"}' % (root, tmp, root))
            rc, out = _run([shutil.which("bash"), driver, tmp, root, block, ev],
                           PATH=fake + os.pathsep + os.environ.get("PATH", ""))
            want = '{"cwd":"C:/%s","f":"C:/msys64%s/repo","r":"C:/%s/.codebuddy"}' % (root[3:], tmp, root[3:])
            self.assertEqual((rc, out), (0, want), (tmp, root))


class BatteryTotalCitation(unittest.TestCase):
    def test_comments_cite_the_total_as_it_is_computed(self):
        # The (e) comment still said the battery prints PASS+FAIL after UNREACH
        # joined the total; the derived-counts gate cites that roll-up by its text.
        with open(BATTERY, encoding="utf-8") as f:
            text = f.read()
        total = re.search(r"^TOTAL=\$\(\((.+)\)\)$", text, re.M)
        self.assertIsNotNone(total, "hook-battery.sh has no TOTAL roll-up")
        spelled = " + ".join(t.strip() for t in total.group(1).split("+"))
        for ln in text.splitlines():
            if ln.lstrip().startswith("#") and re.search(r"\bPASS ?\+ ?FAIL\b", ln):
                self.assertIn(spelled, ln)


@POSIX_HOST
@unittest.skipIf(os.environ.get("BACKTEST_SKIP_HOOK_BATTERY") == "1",
                 "pre-commit: no hook, hook setting or battery change is staged; CI runs these")
class BatteryPortability(unittest.TestCase):
    """Two full battery runs, side by side (each takes about half a minute)."""
    LN_COPIES = ('#!/usr/bin/env bash\n# MSYS2 / Git Bash default: ln -s makes a deep COPY.\n'
                 'if [ "${1:-}" = "-s" ]; then shift; exec cp -RL "$1" "$2"; fi\nexec /bin/ln "$@"\n')
    # Windows only to the battery itself: git's own shell helpers ask uname too, and
    # a MINGW answer swaps in their Windows code paths (c46's `submodule add` broke).
    UNAME_MINGW = ('#!/bin/sh\ncase "$(ps -o args= -p "$PPID" 2>/dev/null)" in\n'
                   '  *hook-battery.sh*) echo MINGW64_NT-10.0-19045 ;;\n  *) exec "%s" "$@" ;;\nesac\n')

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        tmp = os.path.realpath(cls._td.name)
        outside = os.path.join(tmp, "outside")
        foreign = os.path.join(tmp, "foreign-project")
        os.makedirs(outside)
        os.makedirs(foreign)
        shims = _bin(tmp, ln=cls.LN_COPIES, uname=cls.UNAME_MINGW % shutil.which("uname"))
        bash = shutil.which("bash")
        runs = {
            # battery-depends-on-invoker-cwd: by absolute path from outside the repo,
            # with a session's CLAUDE_PROJECT_DIR naming some other directory.
            "elsewhere": subprocess.Popen([bash, BATTERY], cwd=outside, env=_env(CLAUDE_PROJECT_DIR=foreign),
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT),
            # battery-symlink-cases-unreachable-on-windows: Git Bash's ln and uname.
            "windows": subprocess.Popen([bash, BATTERY], cwd=ROOT,
                                        env=_env(PATH=shims + os.pathsep + os.environ.get("PATH", "")),
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT),
        }
        cls.res = {}
        for k, p in runs.items():
            out, _ = p.communicate(timeout=900)
            cls.res[k] = (p.returncode, out.decode("utf-8", "replace"))
        cls.cases = _battery_cases()

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def tail(self, k):
        return "\n".join(self.res[k][1].splitlines()[-25:])

    def test_runs_from_outside_the_repo_with_a_foreign_project_dir(self):
        rc, out = self.res["elsewhere"]
        self.assertEqual(rc, 0, self.tail("elsewhere"))
        self.assertIn(f"hook-battery: ALL PASS ({self.cases} cases)", out)

    def test_symlink_cases_still_run_on_posix(self):
        # The same run: no shim, so c57-c64 are measured, not marked.
        rc, out = self.res["elsewhere"]
        for c in SYM_CASES:
            self.assertRegex(out, rf"(?m)^  PASS  {c} ", c)
        self.assertNotIn("UNREACHABLE", out)

    def test_symlink_cases_are_unreachable_not_failed_on_windows(self):
        rc, out = self.res["windows"]
        self.assertEqual(rc, 0, self.tail("windows"))
        for c in SYM_CASES:
            self.assertRegex(out, rf"(?m)^  UNREACHABLE  {c} ", c)
        self.assertNotRegex(out, r"(?m)^  FAIL  ")
        self.assertIn(f"ALL PASS ({self.cases} cases; 8 UNREACHABLE on this platform", out)


class NormalizeModelTiersEffort(Tmp):
    """`effort:` is a live field on an agent and an inert one on a skill, so the
    normalizer has to treat the two file kinds differently.

    normalizer-drops-agent-effort: until 2026-10-30 the script dropped it from BOTH,
    because the agent metadata schema (`agentMetadataSchema`, seven fields) has no
    slot for it and Effect Struct drops unknown keys. That schema is the payload of
    the *listing* RPC, not the definition used to spawn: `parseAgentFile()` does
    `normalizeReasoningEffort(frontmatter.effort)`, warns on an invalid value, and
    carries it through `...effort:eF` into the sub-session's thinking budget. 18
    agent files lost a working knob before anyone noticed.
    """

    AGENT = "---\nname: lens\ndescription: \"x\"\nmodel: sonnet\neffort: high\n---\n\nBody\n"
    SKILL = "---\nname: demo\ndescription: \"x\"\nmodel: sonnet\neffort: high\n---\n\nBody\n"

    def setUp(self):
        super().setUp()
        _copy_script(self.tmp, "normalize-model-tiers.py")
        self.agent = _write(self.tmp, ".codebuddy/agents/lens.md", self.AGENT)
        self.skill = _write(self.tmp, ".codebuddy/skills/demo/SKILL.md", self.SKILL)

    def _run_normalizer(self):
        return _run([sys.executable, os.path.join(self.tmp, "scripts", "normalize-model-tiers.py")])

    @staticmethod
    def _read(path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_agent_keeps_effort_while_skill_loses_it(self):
        rc, out = self._run_normalizer()
        self.assertEqual(rc, 0, out)
        agent = self._read(self.agent)
        skill = self._read(self.skill)
        self.assertIn("effort: high", agent,
                      "an agent's effort: is live — dropping it removes a real thinking-budget knob")
        self.assertNotIn("effort:", skill,
                         "a skill's effort: is inert — the skill loader never reads it")
        # Control: the tier rename still applies to both kinds.
        self.assertIn("model: default", agent)
        self.assertIn("model: default", skill)

    def test_rerun_changes_nothing(self):
        self._run_normalizer()
        before = self._read(self.agent)
        rc, out = self._run_normalizer()
        self.assertEqual(rc, 0, out)
        self.assertIn("0 file(s) changed", out)
        self.assertEqual(self._read(self.agent), before)


# ── quality_score.py / Quarto 引文扫描 ──────────────────────────────────────

class QuartoCitationCodeSpans(Tmp):
    """A `@scope/pkg` inside a code span is not a citation — Pandoc never parses one.

    The scanner used to read raw source, so the workflow guide's
    `npm i -g @tencent-ai/codebuddy-code` produced "citation key not in
    bibliography: tencent-ai/codebuddy-code" and held the guide at 85/100, below
    the 90 PR threshold. The tempting fix — adding the npm package to
    Bibliography_base.bib — would have silenced the report by putting a package
    name in the reference list. The detector was wrong, not the guide.
    """

    BIB = "@book{Example2024_book,\n  title = {T}\n}\n"

    def setUp(self):
        super().setUp()
        self.bib = pathlib.Path(self.tmp) / "refs.bib"
        _write(self.tmp, "refs.bib", self.BIB)
        self.scan = _load("quality_score.py").IssueDetector.check_quarto_citations

    def test_scoped_package_in_inline_code_is_not_a_citation(self):
        self.assertEqual(self.scan("装 `npm i -g @tencent-ai/codebuddy-code` 即可", self.bib), [])

    def test_fenced_block_is_not_scanned(self):
        src = "```bash\nnpm i @tencent-ai/codebuddy-code\n```\n"
        self.assertEqual(self.scan(src, self.bib), [])

    def test_real_missing_key_is_still_reported(self):
        # Controls: blanking code must not blank the document. Both citation
        # spellings that the detector supports keep working.
        self.assertEqual(sorted(self.scan("正如 @nope2099 所说", self.bib)), ["nope2099"])
        self.assertEqual(sorted(self.scan("[@Example2024_book; @nope2099]", self.bib)), ["nope2099"])

    def test_known_key_is_not_reported(self):
        self.assertEqual(self.scan("见 [@Example2024_book] 的做法", self.bib), [])

    def test_unclosed_backtick_does_not_swallow_the_rest(self):
        # Span matching stays on one line on purpose: with DOTALL a stray
        # backtick would eat the rest of the document and every later citation
        # error would vanish. A missed multi-line span costs a false positive;
        # a swallowed document costs a false negative.
        src = "`一个没闭合的反引号\n见 [@nope2099] 这里"
        self.assertEqual(sorted(self.scan(src, self.bib)), ["nope2099"])


# ── compile-beamer.sh / kpathsea 分隔符 ─────────────────────────────────────

@unittest.skipUnless(shutil.which("bash"), "needs bash")
class BeamerCompileEnv(Tmp):
    """`TEXINPUTS` must end in the platform's path separator.

    kpathsea's rule: the value *replaces* the default search path unless it ends
    in a separator (a trailing separator means "append the defaults after this").
    The defaults contain `.`, so dropping that trailing separator drops the current
    directory — and xelatex then cannot find the `.tex` it was just pointed at:

        ! I can't find file `Demo.tex'.

    That message says the file is missing. The file is right there. The separator
    is also platform-specific (POSIX `:`, Windows TeX Live `;`), so a hardcoded `:`
    is not merely a cosmetic difference on Windows: `:` there is not a separator,
    the trailing-separator guarantee evaporates, and the same misleading failure
    returns. The negative control for the second case below is to hardcode `:`;
    on Windows it goes red.

    These cases only read `--dry-run`, so they need no TeX installation.
    """

    def setUp(self):
        super().setUp()
        _copy_script(self.tmp, "compile-beamer.sh")
        _write(self.tmp, "Slides/Demo.tex", "\\documentclass{beamer}\n")
        self.script = os.path.join(self.tmp, "scripts", "compile-beamer.sh")

    def _dry(self, *args):
        return _run([shutil.which("bash"), self.script, *args], cwd=self.tmp)

    @staticmethod
    def _sep():
        # Deliberately not the script's own test (`$OS`): if the script ever picks
        # its separator by another route, this case should notice.
        return ";" if os.name == "nt" else ":"

    def _field(self, out, name):
        line = [ln for ln in out.splitlines() if ln.startswith(name)]
        return line[0].split(":", 1)[1].strip() if line else ""

    def test_separator_matches_the_platform(self):
        rc, out = self._dry("Demo", "--dry-run")
        self.assertEqual(rc, 0, out)
        # The line is `sep       : ';'  (OS=Windows_NT)`; only the quoted value matters.
        sep = self._field(out, "sep").split()[0].strip("'")
        self.assertEqual(sep, self._sep(), out)

    def test_texinputs_ends_with_the_separator(self):
        rc, out = self._dry("Demo", "--dry-run")
        self.assertEqual(rc, 0, out)
        value = self._field(out, "TEXINPUTS")
        self.assertTrue(value.endswith(self._sep()),
                        "TEXINPUTS %r does not end in %r — kpathsea will drop '.' "
                        "and report the .tex as missing" % (value, self._sep()))

    def test_bibinputs_ends_with_the_separator(self):
        rc, out = self._dry("Demo", "--dry-run")
        self.assertEqual(rc, 0, out)
        value = self._field(out, "BIBINPUTS")
        self.assertTrue(value.endswith(self._sep()), "BIBINPUTS %r ends wrongly" % value)

    def test_a_missing_deck_exits_2_and_says_what_is_there(self):
        rc, out = self._dry("NoSuchDeck")
        self.assertEqual(rc, 2, out)
        self.assertIn("Demo.tex", out)


# ── Preambles/header.tex / 中文支持 ─────────────────────────────────────────

class PreamblesCjk(unittest.TestCase):
    """A missing CJK setup does not fail — it just produces blank Chinese.

    Without xeCJK, xelatex emits one `Missing character` per Han glyph and still
    writes a PDF: exit code 0, correct page count, zero errors. The deck looks
    fine to every signal except the eyes. On a Chinese branch that is the worst
    possible failure shape, so the load is pinned here.
    """

    def setUp(self):
        with open(os.path.join(ROOT, "Preambles", "header.tex"), encoding="utf-8") as f:
            self.src = f.read()

    def test_cjk_loads_only_under_xetex(self):
        # pdflatex would fail outright on xeCJK, so the guard is part of the fix.
        self.assertIn("\\ifPDFTeX\\else", self.src)
        self.assertIn("\\usepackage{xeCJK}", self.src)

    def test_cjk_fonts_ship_with_texlive(self):
        # Only the actual font-setting commands count: the comment above them
        # names PingFang SC / Microsoft YaHei as the counter-example, and a
        # blanket `assertNotIn` would trip on that mention instead of the thing.
        self.assertIn("\\setCJKmainfont{Fandol", self.src)
        for system_font in ("PingFang", "Microsoft"):
            self.assertNotIn("\\setCJKmainfont{%s" % system_font, self.src)


if __name__ == "__main__":
    unittest.main()
