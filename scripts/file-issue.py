#!/usr/bin/env python3
"""Create a GitHub issue only after checking for duplicates — the one sanctioned route.

A tracker is only a memory if each problem lives in one place. Before anything is
created, this runs several searches over OPEN and CLOSED issues (one strict query on
the title's four most distinctive words, the top three of them alone in titles, every
--search term you pass, and up to three file paths the title or body names; at most
eight searches, and any dropped are reported) and lists what it finds. The issue is created only when every candidate has been reviewed and
judged distinct, which you record with --checked. The check and its verdict are
appended to the issue body, so the record shows the search was done.

The issue-guard hook blocks a raw `gh issue create` from Claude and points here.

Usage:
  python3 scripts/file-issue.py --title "..." --body-file body.md \
      [--label bug] [--search "extra terms"] [--checked 12,15] [--repo owner/name] [--dry-run]

Exit: 0 created (or, with --dry-run, ready to create); 3 candidates still to review
(listed on stdout, nothing created); 2 could not run — no gh, a search failed, or no
search could be built (nothing created: the check fails closed); 1 gh refused the
create.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

MAX_QUERIES = 8
SHOW = 10
STOP = set("""
a an and are as at be been but by can cannot could did do does doesn for from had has have how
if in into is it its it's may might must no not of on once only or our out over should so than
that the their them then there these this those to too under up use used uses using was we were
what when where which while who why will with without would yet you your
add adds added bug bugs error errors fail fails failed failing fix fixes fixed issue issues make
makes new now problem problems still wrong
""".split())
WORD = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-/]*[A-Za-z0-9_]|[A-Za-z0-9_]")
PATH = re.compile(r"(?<![\w/.-])(?:[\w.-]+/)*[\w.-]+\.(?:R|r|py|sh|tex|qmd|md|Rmd|do|ado|ipynb|"
                  r"json|ya?ml|csv|bib|html|js|css|scss|toml|txt)\b")


def keywords(title: str) -> list[str]:
    seen, out = set(), []
    for w in WORD.findall(title):
        k = w.lower().strip(".-/")
        if len(k) >= 3 and k not in STOP and k not in seen:
            seen.add(k)
            out.append(k)
    return sorted(out, key=len, reverse=True)       # longest first: usually the most specific


def build_queries(title: str, body: str, extra: list[str]) -> list[str]:
    kw = keywords(title)
    qs: list[str] = []
    if kw:
        qs.append(" ".join(kw[:4]) + " in:title,body")
        qs += [f"{k} in:title" for k in kw[:3]]
    qs += [s for s in extra if s.strip()]
    for p in list(dict.fromkeys(PATH.findall(title + "\n" + body)))[:3]:
        qs.append(f'"{p}"')
    return list(dict.fromkeys(qs))


def search(query: str, repo: str | None) -> list[dict]:
    cmd = ["gh", "issue", "list", "--state", "all", "--search", query, "--limit", "20",
           "--json", "number,title,state,url"]
    if repo:
        cmd += ["--repo", repo]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"`{' '.join(cmd[:4])} ... {query!r}` failed: "
                           f"{(r.stderr or r.stdout).strip()[:300]}")
    return json.loads(r.stdout or "[]")


def parse_checked(values: list[str]) -> set[int]:
    return {int(n) for v in values for n in re.findall(r"\d+", v)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--title", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--body-file")
    g.add_argument("--body")
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--search", action="append", default=[],
                    help="extra search terms (a section name, a function, a table label)")
    ap.add_argument("--checked", action="append", default=[],
                    help="issue numbers you reviewed and judged distinct, e.g. 12,15")
    ap.add_argument("--repo", help="owner/name (default: the repository gh infers)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not shutil.which("gh"):
        print("file-issue: CANNOT RUN — the GitHub CLI (gh) is not on PATH. Install it "
              "(brew install gh / apt install gh) and run `gh auth login`. Nothing was created.",
              file=sys.stderr)
        return 2
    try:
        body = open(a.body_file, encoding="utf-8").read() if a.body_file else a.body
    except OSError as e:
        print(f"file-issue: cannot read --body-file: {e}", file=sys.stderr)
        return 2

    queries = build_queries(a.title, body, a.search)
    if not queries:
        print("file-issue: CANNOT RUN — the title has no searchable words; pass --search "
              "with the terms a duplicate would contain. Nothing was created.", file=sys.stderr)
        return 2
    if len(queries) > MAX_QUERIES:
        print(f"file-issue: running the first {MAX_QUERIES} of {len(queries)} searches "
              f"(dropped: {queries[MAX_QUERIES:]})", file=sys.stderr)
        queries = queries[:MAX_QUERIES]

    found: dict[int, dict] = {}
    try:
        for q in queries:
            for it in search(q, a.repo):
                row = found.setdefault(it["number"], {**it, "hits": 0})
                row["hits"] += 1
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
        print(f"file-issue: CANNOT RUN — the duplicate search did not complete ({e}). "
              "Nothing was created: an unchecked issue is what this script exists to prevent.",
              file=sys.stderr)
        return 2

    checked = parse_checked(a.checked)
    ranked = sorted(found.values(), key=lambda r: (-r["hits"], -r["number"]))
    pending = [r for r in ranked if r["number"] not in checked]

    if pending:
        print(f"Possible duplicates — {len(pending)} not yet reviewed "
              f"({len(queries)} searches over open and closed issues):")
        for r in pending[:SHOW]:
            print(f"  #{r['number']} [{r['state'].lower()}] {r['title']}  "
                  f"(matched {r['hits']} of {len(queries)} searches)")
        if len(pending) > SHOW:
            print(f"  ... and {len(pending) - SHOW} more with fewer matches")
        print("\nRead each one (gh issue view N). If one is the same problem, add to it instead:")
        print("  gh issue comment N --body-file <file>    (and gh issue reopen N if it is back)")
        shown = ",".join(str(r["number"]) for r in pending[:SHOW])
        print(f"If the new issue is distinct from all of them, re-run with --checked {shown}")
        print("Nothing was created.")
        return 3

    today = _dt.date.today().isoformat()
    qlist = "; ".join(f"`{q}`" for q in queries)
    verdict = (f"reviewed and judged distinct: {', '.join(f'#{n}' for n in sorted(r['number'] for r in ranked))}"
               if ranked else "no candidates found")
    record = (f"\n\n---\nDuplicate check ({today}, scripts/file-issue.py): {len(queries)} searches "
              f"of open and closed issues ({qlist}); {verdict}.")
    full = body.rstrip("\n") + record + "\n"

    cmd = ["gh", "issue", "create", "--title", a.title]
    for lab in a.label:
        cmd += ["--label", lab]
    if a.repo:
        cmd += ["--repo", a.repo]

    if a.dry_run:
        print("Dry run — nothing created.")
        print(f"Title: {a.title}")
        print(f"Labels: {', '.join(a.label) or '(none)'}")
        print("Body:\n" + full)
        print("Would run: " + shlex.join(cmd + ["--body-file", "<body>"]))
        return 0

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(full)
        path = f.name
    r = subprocess.run(cmd + ["--body-file", path], capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        print(f"file-issue: gh refused the create (exit {r.returncode}); the body is at {path}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
