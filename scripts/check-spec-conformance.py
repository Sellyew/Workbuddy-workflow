#!/usr/bin/env python3
"""Audit every skill against the Agent Skills spec (agentskills.io/specification).

Checks: name format + directory match, description length, SKILL.md body size,
fields that no consumer reads, and portability of the frontmatter.

Exit: 0 clean (advisories allowed), 1 spec violation, 2 internal error.
"""
import re, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_FIELDS = {"name","description","license","compatibility","metadata","allowed-tools"}
# Fields Claude Code 额外读取（上游原有判定，保留以便与上游对照）。
CC_ONLY = {"when_to_use","argument-hint","arguments","disable-model-invocation","user-invocable",
           "disallowed-tools","model","effort","context","agent","background","hooks","paths","shell"}
# [WorkBuddy 适配] WorkBuddy 自己会读取的 frontmatter 字段。
#
# 依据：WorkBuddy 的技能解析器识别 description_zh / description_en（中英双语描述）、
# category / tags / version / agent_created（技能市场与版本管理）、以及
# allowed-tools / argument-hint / user-invocable / disable-model-invocation / agent。
# 这些字段在本平台**是被消费的**，不属于「无人读取」，所以不计违规。
WB_FIELDS = {"description_zh","description_en","category","tags","version","agent_created",
             "allowed-tools","argument-hint","user-invocable","disable-model-invocation","agent"}
# 无对应语义：Claude Code 读、WorkBuddy 不读且不影响运行。保留不报错，但要提示。
INERT_FIELDS = {"effort","when_to_use","arguments","disallowed-tools","model","context",
                "background","hooks","paths","shell"}
NAME_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')

def main():
    errs, warns = [], []
    skills = sorted(glob.glob(os.path.join(glob.escape(ROOT), ".codebuddy/skills/*/SKILL.md")))
    if not skills:
        print("check-spec-conformance: no skills found", file=sys.stderr); return 2
    for f in skills:
        d = os.path.basename(os.path.dirname(f))
        rel = os.path.relpath(f, ROOT)
        # utf-8-sig 会丢掉行首 BOM（PowerShell 5.1 保存时就会写一个），否则完好的
        # frontmatter 会被读成「no YAML frontmatter」——而本平台的技能加载器是剥掉 BOM 的。
        s = open(f, encoding="utf-8-sig", errors="ignore").read()
        m = re.match(r'^---\n(.*?)\n---\n(.*)$', s, re.S)
        if not m:
            errs.append(f"{rel}: no YAML frontmatter"); continue
        fm, body = m.group(1), m.group(2)
        def field(k):
            # Value = rest of THIS line plus indented continuation lines only.
            # The old \s* skipped a blank value across the newline and returned
            # the NEXT key's line, so an empty description: passed (v2.5 audit).
            mm = re.search(rf'^{re.escape(k)}:[ \t]*(.*(?:\n[ \t]+\S.*)*)', fm, re.M)
            return mm.group(1).strip() if mm else None
        name = (field("name") or "").strip().strip('"\'')
        desc = field("description") or ""
        if not name:                       errs.append(f"{rel}: missing required 'name'")
        elif not NAME_RE.fullmatch(name):  errs.append(f"{rel}: name '{name}' violates spec format")
        elif name != d:                    errs.append(f"{rel}: name '{name}' != directory '{d}'")
        if not desc:                       errs.append(f"{rel}: missing required 'description'")
        elif len(desc) > 1024:             errs.append(f"{rel}: description {len(desc)} chars > 1024 spec max")
        n = body.count("\n")
        if n > 500:                        errs.append(f"{rel}: body {n} lines > 500 (spec guidance: split into references/)")
        keys = set(re.findall(r'^([a-zA-Z_-]+):', fm, re.M))
        known = SPEC_FIELDS | CC_ONLY | WB_FIELDS
        unknown = keys - known
        if unknown:
            errs.append(f"{rel}: field(s) {sorted(unknown)} read by neither the spec, "
                        f"Claude Code nor WorkBuddy — move under 'metadata:'")
        inert = keys & (INERT_FIELDS - WB_FIELDS)
        if inert:
            warns.append(f"{rel}: {sorted(inert)} 在 WorkBuddy 无对应语义（不报错，"
                         f"但也不会起作用——保留前请确认不是误以为它会生效）")
    print(f"check-spec-conformance: {len(skills)} skills audited")
    if errs:
        print(f"\n{len(errs)} SPEC VIOLATION(S):")
        for e in errs: print(f"  {e}")
    if warns:
        # 表头保留英文标签 `portability advisory`：它是机器可读的判定词汇，
        # 与 PASS/REVISE/BLOCK 同类；后面的破折号说明才是给人读的。
        print(f"\n{len(warns)} portability advisory(ies) — 不构成失败，是刻意的上限:")
        for w in warns[:5]: print(f"  {w}")
        if len(warns) > 5: print(f"  … 另有 {len(warns)-5} 条")
    if not errs: print("\nAll skills conform to the Agent Skills spec.")
    return 1 if errs else 0

if __name__ == "__main__":
    # advisory 表头每次都要打一个破折号。日文或韩文 Windows 的管道（cp932、cp949）
    # 编码不了它，print 直接把门禁崩掉——把编码不了的字符替换掉，而不是死。
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
