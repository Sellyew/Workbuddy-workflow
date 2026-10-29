#!/usr/bin/env python3
"""Scan for stale recommendations and drift the other gates cannot see.

The other gates check that surfaces agree WITH EACH OTHER. This one checks for
claims that were true once and are not any more, plus source/render divergence.

Exit: 0 clean, 1 stale content found, 2 internal error.
"""
import re, os, sys, glob, hashlib, subprocess
from datetime import date as _date_cls

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# defect-library.md is a CATALOGUE of anti-patterns to seed — it contains them by design.
SKIP = re.compile(r'(^|/)(CHANGELOG\.md|defect-library\.md|\.git/|node_modules/|quality_reports/)')

def render_fp(p):
    """Content fingerprint of a source or render: sha256 前 16 位，行尾先归一成 LF。

    必须与 scripts/stamp-render.py 的 fp() 给出同一个值。
    行尾归一成 LF 之后再算。不归一的话，Windows 上 Quarto 写出的 CRLF 产物盖的戳，
    在 LF 的**全新 clone** 上必然对不上，这道门就会在干净的树上一直红 —— 而「干净的
    树上一直红」唯一的教学效果是教人绕过它。归一是安全的：篡改一个字节仍然变红，
    见 tests/portability/test_scripts.py 里的两条用例。
    """
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()[:16]

def surfaces():
    out = []
    # glob.escape(ROOT)：路径含 `[` `]` `*` `?` 的检出（例如 `Paper [2026]/repo`）
    # 会让整条 pattern 变成一个匹配不到任何文件的字符类。见 check-links.py
    # 顶部同一处注释。
    glob_root = glob.escape(ROOT)
    for pat in ["*.md", ".codebuddy/**/*.md", "templates/**/*.md", "guide/*.qmd", "docs/*.html", ".github/**/*.md"]:
        out += glob.glob(os.path.join(glob_root, pat), recursive=True)
    # [WorkBuddy 适配] relpath 在 Windows 返回反斜杠，而 SKIP 正则按 `/` 写。
    # 不归一化的话，跳过清单在 Windows 上整体失效——「按设计含反面案例」的
    # defect-library.md 会被当成真实违规报出来（实测：本次迁移首次跑门 6 命中）。
    return [p for p in sorted(set(out))
            if not SKIP.search(os.path.relpath(p, ROOT).replace(os.sep, "/"))]

# (id, description, regex, allow-marker regex or None)
CHECKS = [
 ("STALE-TOOL", "names `Task` as the subagent tool (it is `Agent`)",
  r'via\s+`?Task`?\b|`Task`\s+subagent|spawn\w*\s+[^.\n]{0,30}\bvia\s+Task\b', r'legacy|prior|historical|alias|renamed|model-allow'),
 ("STALE-AUTOMODE", "describes auto mode as plan-gated (it is the Pro/Max/Team default since 2026-08-14)",
  r'auto mode\s+(requires|needs)\s+(Team|Enterprise)|rolling out to Max', r'UPDATED|no longer|was\b'),
 ("STALE-SUPERLATIVE", "unfalsifiable product claim",
  # [WorkBuddy 适配] 允许标记加中文同义说法：本模板的中文记忆与规则用「禁用 / 绝不 /
  # 反例 / 不要」来**点名**这些词是禁用的。只认英文时，一句「发布文案里禁用的词：
  # best-in-class」会被判成「你在做排他性断言」——把禁令读成了违规，正好读反。
  r'\bthe only (public )?(workflow|template|repo)\b|\bnobody else (has|can)\b|\bbest-in-class\b|\bthe first (public )?workflow\b', r'Banned|never claim|Seed|seed|anti-pattern|example of|禁用|禁止|绝不|反例|不要写'),
 ("STALE-BLOCKER", "cites a closed issue as an open blocker",
  r'blocked (on|by) .{0,40}#11278|#11278.{0,40}(blocker|quirk)', r'UNBLOCKED|closed'),
]

def main():
    files = surfaces()
    # 空扫描必须是错误，不是通过（见 check-links.py 同一处注释）。返回 2 而不是 1：
    # 1 表示「查了，有问题」，2 表示「没查成」。把两者混为一谈会让一次失效的
    # glob 看起来像一次干净的检查。
    if not files:
        print("check-staleness: nothing was checked — the glob matched no files. "
              "Refusing to report success on an empty scan.", file=sys.stderr)
        return 2
    hits = []
    for f in files:
        rel = os.path.relpath(f, ROOT)
        try: text = open(f, encoding="utf-8", errors="ignore").read()
        except Exception: continue
        for cid, desc, pat, allow in CHECKS:
            for i, line in enumerate(text.split("\n"), 1):
                if re.search(pat, line, re.I):
                    if allow and re.search(allow, line, re.I): continue
                    hits.append((cid, rel, i, desc, line.strip()[:90]))

    # source vs rendered divergence.
    #
    # NOT by mtime: git does not preserve timestamps, so on a fresh clone or a
    # detached worktree the checkout order decides which file looks newer. That
    # made this gate fail spuriously for every first-time forker and in CI.
    # (Codex review, PR #140 — confirmed by reproducing it in a fresh worktree.)
    #
    # Instead: compare a fingerprint of the SOURCE against the fingerprint the
    # last render recorded. Content, not clock.
    render = []
    stamp_path = os.path.join(ROOT, ".render-stamp")
    recorded = {}
    if os.path.exists(stamp_path):
        for line in open(stamp_path):
            parts = line.strip().split(":")
            if len(parts) == 3:
                recorded[parts[0]] = (parts[1], parts[2])   # (source_hash, output_hash)
    # 行尾归一在 render_fp 里（模块级，便于 tests/portability 直接比对两处实现）。
    for src, out in [("guide/workflow-guide.qmd", "guide/workflow-guide.html"),
                     ("guide/workflow-guide.qmd", "docs/workflow-guide.html")]:
        s_path, o_path = os.path.join(ROOT, src), os.path.join(ROOT, out)
        if not (os.path.exists(s_path) and os.path.exists(o_path)):
            continue
        src_hash = render_fp(s_path)
        out_hash = render_fp(o_path)
        rec = recorded.get(out)
        if rec is None:
            render.append(f"{out}: no render stamp — run scripts/stamp-render.sh after rendering")
        elif rec[0] != src_hash:
            render.append(f"{out}: stamped for a DIFFERENT source ({rec[0]} vs {src_hash}) — "
                          f"re-render: cd guide && quarto render workflow-guide.qmd, sync docs, "
                          f"then ./scripts/stamp-render.sh")
        elif rec[1] != out_hash:
            render.append(f"{out}: output modified since it was stamped ({rec[1]} vs {out_hash}) — "
                          f"either an unsynced copy or a hand-edit; re-render and re-stamp")

    # currency expiry — a verified_on date that has aged out
    expired = []
    mv = os.path.join(ROOT, ".codebuddy/references/model-versions.md")
    if os.path.exists(mv):
        t = open(mv, encoding='utf-8', errors='ignore').read()
        m = re.search(r'\*\*Expires:\*\*\s*(\d{4}-\d{2}-\d{2})', t)
        if m:
            # [WorkBuddy 适配] 原实现调外部 `date` 命令。Windows 没有 date.exe，
            # subprocess 直接抛 WinError 2，整个门禁以 rc=2 崩溃——看起来像
            # 「检查发现问题」，实际是「检查根本没跑」。用标准库取当天日期，
            # 无外部依赖，跨平台一致。
            today = _date_cls.today().isoformat()
            if today > m.group(1):
                expired.append(f"model-versions.md expired {m.group(1)} (today {today}) — re-verify against the docs")

    # guide version <-> CHANGELOG parity (Oracle review, 2026-08-22: the source
    # shipped with no version and a stale date; this pins it to the release).
    meta = []
    gq = os.path.join(ROOT, "guide/workflow-guide.qmd")
    cl = os.path.join(ROOT, "CHANGELOG.md")
    if os.path.exists(gq) and os.path.exists(cl):
        gt = open(gq, encoding='utf-8', errors='ignore').read(2000)
        ct = open(cl, encoding='utf-8', errors='ignore').read(4000)
        gv = re.search(r'^version:\s*"?v?(\d+\.\d+\.\d+)"?', gt, re.M)
        cv = re.search(r'^## v(\d+\.\d+\.\d+)', ct, re.M)
        if not gv:
            meta.append("guide frontmatter has no version: field — add one matching the CHANGELOG release")
        elif cv and gv.group(1) != cv.group(1):
            meta.append(f"guide version {gv.group(1)} != CHANGELOG latest v{cv.group(1)} — update the frontmatter")

    # reversed dynamic-injection syntax: `!cmd` (backtick-first) is inert; the
    # real grammar is !`cmd` (Oracle review, 2026-08-22 — the guide shipped the
    # reversed form and readers copy examples verbatim).
    inject = []
    scan = []
    for base in ("guide/workflow-guide.qmd", "templates/skill-template.md"):
        p = os.path.join(ROOT, base)
        if os.path.exists(p): scan.append(p)
    skdir = os.path.join(ROOT, ".codebuddy/skills")
    if os.path.isdir(skdir):
        for d in sorted(os.listdir(skdir)):
            p = os.path.join(skdir, d, "SKILL.md")
            if os.path.exists(p): scan.append(p)
    inj_pat = re.compile(r"`![a-z][a-z0-9._-]*(?:\s+[^`\n]*)?`")
    for p in scan:
        rel = os.path.relpath(p, ROOT)
        for i, line in enumerate(open(p, encoding='utf-8', errors='ignore'), 1):
            for m in inj_pat.finditer(line):
                frag = m.group(0)
                # R-code negations like `!anyNA(w)` and shell paths like
                # `!/shell/erase` are not injection attempts.
                if "(" in frag or frag.startswith("`!/"): continue
                inject.append(f"{rel}:{i}: {frag} — reversed injection syntax; write !`cmd`, not `!cmd`")

    print(f"check-staleness: {len(files)} surfaces scanned")
    bad = hits or render or expired or meta or inject
    for cid, rel, i, desc, line in hits: print(f"  [{cid}] {rel}:{i}  {desc}\n      {line}")
    for r in render:  print(f"  [STALE-RENDER] {r}")
    for e in expired: print(f"  [STALE-EXPIRY] {e}")
    for x in meta:    print(f"  [STALE-VERSION] {x}")
    for x in inject:  print(f"  [BAD-INJECT-SYNTAX] {x}")
    if not bad: print("No stale recommendations, no source/render divergence, no expired currency claims.")
    return 1 if bad else 0

if __name__ == "__main__":
    # Every finding line carries an em dash, which a cp932/cp949 pipe (Japanese,
    # Korean Windows) cannot encode: a real finding became "internal error" (#171).
    # errors=replace keeps the finding readable and the exit code honest; without
    # it the encode raises inside print, the handler below catches it, and a tree
    # with 3 real findings exits 2 ("could not check") instead of 1 ("stale").
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    try:
        sys.exit(main())
    except Exception as e:                      # promised exit 2 now exists
        print(f"check-staleness: internal error: {e}", file=sys.stderr)
        sys.exit(2)
