#!/usr/bin/env python3
"""字段文档一致性门禁。

校验三处文档对技能 frontmatter 字段的表述与机器真源 `scripts/lib/skill_fields.py`
一致——抓「文档把无对应语义字段（disallowed-tools/paths/hooks/…）当有效字段教」
这类致命矛盾，避免再靠人重读才发现。

四条断言（全部机械，不靠措辞启发式）：
  A. `skill-fields.md` 的三张标记表格与机器真源的集合完全相等（人类真源永不漂移）。
  B. guide 的 `{#skill-frontmatter}` 小节不把 inert/hazardous 字段当有效教（整节
     词边界扫描 + 表格字段名 ⊆ 有效字段）。
  C. 死替换项：`${CLAUDE_SKILL_DIR}` / `${CLAUDE_SESSION_ID}` 在 guide 里零命中；
     `$0`/`$1`/`$N` 在 `{#skill-dynamic-content}` 小节里零命中。
  D. README 的「技能 frontmatter」bullet 不含 inert/hazardous 字段名。

退出：0 全绿；1 有断言违反；2 内部错误（解析失败/缺标记——响亮失败，绝不静默绿）。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_fields():
    # 机器真源：scripts/check-spec-conformance.py 里的 WB_FIELDS / INERT_FIELDS。
    # 用 importlib 加载（文件名带连字符，无法按包名 import），与 gate-manifest.py 同款。
    import importlib.util
    from types import SimpleNamespace
    spec = importlib.util.spec_from_file_location(
        "_spec_conf", os.path.join(ROOT, "scripts", "check-spec-conformance.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return SimpleNamespace(
        WB_FIELDS=mod.WB_FIELDS,
        INERT_FIELDS=mod.INERT_FIELDS,
        HAZARDOUS_FIELDS={"context"},
        VALID_SKILL_FIELDS=mod.WB_FIELDS | {"name", "description", "model"},
        DEAD_SUBSTITUTIONS={"${CLAUDE_SKILL_DIR}", "${CLAUDE_SESSION_ID}", "$0", "$1", "$N"},
    )


def read(rel):
    with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


def _table_field_names(md):
    """抽出一段 markdown 里每行第一列的 `` `反引号` `` 字段名（可多个）。"""
    names = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        first = line.strip("|").split("|")[0].strip()
        names.extend(re.findall(r"`([a-z0-9_-]+)`", first))
    return names


def check_A(fields):
    ref = read(".codebuddy/references/skill-fields.md")
    for tag, want in (("valid", fields.VALID_SKILL_FIELDS),
                      ("inert", fields.INERT_FIELDS),
                      ("hazardous", fields.HAZARDOUS_FIELDS)):
        m = re.search(rf"<!-- BEGIN skill-fields-{tag} -->\n(.*?)<!-- END skill-fields-{tag} -->",
                      ref, re.S)
        if not m:
            return False, f"skill-fields.md: {tag} 标记缺失"
        got = set(_table_field_names(m.group(1)))
        if got != want:
            return False, (f"skill-fields.md {tag} 集合 ≠ 机器真源："
                           f"缺 {sorted(want - got)}，多 {sorted(got - want)}")
    return True, "skill-fields.md 三张表 == check-spec-conformance.py 的字段集合"


def check_B(fields):
    guide = read("guide/workflow-guide.qmd")
    m = re.search(r"### Frontmatter 完整参考 \{#skill-frontmatter\}\n(.*?)(?=\n### )",
                  guide, re.S)
    if not m:
        return False, "guide: {#skill-frontmatter} 小节未找到"
    body = m.group(1)
    bad = [f for f in sorted(fields.INERT_FIELDS | fields.HAZARDOUS_FIELDS)
           if re.search(r"(?<![A-Za-z0-9_-])" + re.escape(f) + r"(?![A-Za-z0-9_-])", body)]
    if bad:
        return False, f"guide {{#skill-frontmatter}} 小节把无对应语义/有害字段当有效教：{bad}"
    unknown = set(_table_field_names(body)) - fields.VALID_SKILL_FIELDS
    if unknown:
        return False, f"guide {{#skill-frontmatter}} 字段表含不在真源里的字段：{sorted(unknown)}"
    return True, "guide 字段小节干净"


def check_C(fields):
    guide = read("guide/workflow-guide.qmd")
    errs = [s for s in ("${CLAUDE_SKILL_DIR}", "${CLAUDE_SESSION_ID}") if s in guide]
    m = re.search(r"### 技能里的动态内容 \{#skill-dynamic-content\}\n(.*?)(?=\n### )",
                  guide, re.S)
    if not m:
        return False, "guide: {#skill-dynamic-content} 小节未找到"
    body = m.group(1)
    for tok in ("`$0`", "`$1`", "`$N`"):
        if tok in body:
            errs.append(f"guide 动态内容小节仍教位置参数 {tok}")
    return (not errs), ("; ".join(errs) if errs else "无死替换项")


def check_D(fields):
    readme = read("README.md")
    for ln in readme.splitlines():
        if "技能 frontmatter" in ln:
            bad = [f for f in sorted(fields.INERT_FIELDS | fields.HAZARDOUS_FIELDS)
                   if re.search(r"(?<![A-Za-z0-9_-])" + re.escape(f) + r"(?![A-Za-z0-9_-])", ln)]
            if bad:
                return False, f"README「技能 frontmatter」bullet 把无对应语义/有害字段当有效：{bad}"
            return True, "README bullet 干净"
    return False, "README 里没找到「技能 frontmatter」bullet"


def main():
    fields = _load_fields()
    errs = []
    for name, fn in (("A", check_A), ("B", check_B), ("C", check_C), ("D", check_D)):
        ok, msg = fn(fields)
        print(f"  [{name}] {'OK ' if ok else 'FAIL'} {msg}")
        if not ok:
            errs.append(msg)
    if errs:
        print("field-docs: 字段文档与机器真源不一致")
        return 1
    print("field-docs: 字段文档与机器真源一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
