#!/usr/bin/env python3
"""Portability suite: the path, encoding, line-ending and git-output cases that differ
between the author's macOS setup and everyone else's machine — Windows above all.

Runs every tests/portability/test_*.py with unittest. Windows behaviour is simulated:
tests/portability/_winsim.py loads a REAL module from this repo with `os.path` swapped
for `ntpath` (sep='\\'), so a case that fails here fails the same way on Windows. The
cases that are not Windows-specific (non-ASCII and quoted file names from git, CRLF
checkouts, case-varied paths on a case-insensitive disk, a BOM) run as they are.

Each case is one of three kinds. A PIN fails on the code before its fix (a defect from
issue #171 or #151, or a regression a first-cut fix introduced) and passes after. A
CONTROL is an ordinary command or clean input that passes before and after, so a fix
that refuses everything cannot pass. A HARNESS check tests the suite itself: that the
ntpath simulation is real, that each skip below guards a mechanism that bites where it
runs, and that this runner counts honestly (test_harness.py).

A case whose mechanism this host lacks is SKIPPED with its reason, never passed: a pass
there would pin nothing. The strict-encoding cases need Python 3.10 (EncodingWarning),
the patched-locale cases 3.11 (locale.getencoding, patched in a child held in locale
mode, since UTF-8 mode never asks it), the symlink cases a host that lets os.symlink run
(Windows needs Developer Mode or elevation). The verdict line counts the skips and
prints each reason, so a run that could not exercise a case says which.

When some cases are skipped they are named on their own lines, and one machine-readable
line says how much of the suite this host could not exercise:

    portability-ceiling: 100 of 234 cases not exercised on this host

That line is the contract scripts/backtest.py (gate 11) parses. It exists because a run
with skips is a PASS with a CEILING: it pins only the cases that ran, and a bare
"ALL PASS" would let a fork believe the whole suite is green on a host where most of it
never got the chance to speak. The ceiling is not a failure — a host that lacks a
mechanism cannot be blamed for it — but the orchestrator reports it separately rather
than folding it into PASS.

Exit: 0 all pass (skips named, ceiling printed if any), 1 a case failed,
      2 the suite could not run — no cases found, or every case was skipped.
"""
import os
import sys
import unittest
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = os.path.join(ROOT, "tests", "portability")


def main() -> int:
    if not os.path.isdir(SUITE):
        print(f"portability-tests: CANNOT RUN — {SUITE} is missing", file=sys.stderr)
        return 2
    # #171 G1: under .githooks/pre-commit git exports GIT_INDEX_FILE (absolute for
    # `commit -a`, `commit <paths>` and in a linked worktree, with GIT_DIR there too).
    # A case that runs a gate in-process (_winsim.run_main / load) then had its
    # fixture's `git -C tmp ls-files` read the user's index. Only this process drops
    # them: the real gates in backtest.sh must keep judging the index being committed.
    for k in [k for k in os.environ if k.startswith("GIT_") and k != "GIT_EXEC_PATH"]:
        del os.environ[k]
    # Same defect, one variable over: scripts/backtest.py exports
    # CODEBUDDY_PROJECT_DIR (and CLAUDE_PROJECT_DIR) pointing at THIS repository
    # to every child it starts, and root-of-trust-guard.py reads that variable
    # before anything else. So under the gate every case that fires the guard got
    # the real repo as its project, judged its own fixture to be "another tree",
    # and ALLOWED the write it was born to check — 24 cases passed on a Mac and
    # failed on Linux, where they actually run. hook-battery.sh already unsets
    # both for exactly this reason; a case that wants a project dir passes its own.
    for k in ("CODEBUDDY_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        os.environ.pop(k, None)
    sys.path.insert(0, SUITE)
    suite = unittest.defaultTestLoader.discover(SUITE, pattern="test_*.py", top_level_dir=SUITE)
    if suite.countTestCases() == 0:
        print("portability-tests: CANNOT RUN — no test cases found", file=sys.stderr)
        return 2
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
    # The total keeps the skipped cases, as hook-battery's does its UNREACHABLE ones;
    # an unexpected success is a declared failure that no longer fails (#171 G6).
    total = result.testsRun
    bad = len(result.failures) + len(result.errors) + len(result.unexpectedSuccesses)
    if bad:
        print(f"portability-tests: {bad} of {total} cases FAILED")
        return 1
    reasons = sorted(Counter(reason for _, reason in result.skipped).items())
    if result.skipped and len(result.skipped) == total:
        # A run where every case was skipped exercised nothing. Reported as a pass it
        # would be the same defect this repo refuses everywhere else: an empty scan
        # read as green. It is not a pass and not a failure of the code — it is a
        # suite that could not run, so exit 2, the code the caller already handles.
        print(f"portability-tests: CANNOT RUN — every one of {total} cases was skipped")
        for reason, n in reasons:
            print(f"  skipped {n}: {reason}")
        return 2
    if not result.skipped:
        print(f"portability-tests: ALL PASS ({total} cases)")
        return 0
    print(f"portability-tests: ALL PASS ({total} cases, {len(result.skipped)} skipped)")
    for reason, n in reasons:
        print(f"  skipped {n}: {reason}")
    # Stable one-line contract, parsed by gate 11 of scripts/backtest.py. Text before
    # the colon is what it looks for; the counts are what a reader needs.
    print(f"portability-ceiling: {len(result.skipped)} of {total} cases not exercised "
          f"on this host")
    return 0


if __name__ == "__main__":
    sys.exit(main())
