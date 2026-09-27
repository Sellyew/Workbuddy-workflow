#!/usr/bin/env bash
# Flags SUPERSEDED Claude model versions that are presented as CURRENT in the
# template's user-facing surfaces. The single source of truth is the
# `<!-- CURRENT: ... -->` marker in .claude/references/model-versions.md.
#
# Historical references (CHANGELOG.md is excluded entirely) and explicit
# "prior generation" / comparison / "or later" lines are allowed via markers.
# Rendered HTML is derived from the .qmd, so we scan the source, not the HTML.
#
# Exit codes: 0 = clean, 1 = drift detected, 2 = internal error.
set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)"
if [ -z "$REPO" ] || [ ! -d "$REPO" ]; then
    echo "check-model-versions: cannot resolve repo root" >&2
    exit 2
fi

SSOT="$REPO/.claude/references/model-versions.md"
if [ ! -f "$SSOT" ]; then
    echo "check-model-versions: SSoT missing: $SSOT" >&2
    exit 2
fi

CURRENT_LINE="$(grep -E "<!-- CURRENT:" "$SSOT" | head -1)"
if [ -z "$CURRENT_LINE" ]; then
    echo "check-model-versions: no '<!-- CURRENT: ... -->' marker in $SSOT" >&2
    exit 2
fi

# Current-state surfaces to scan (sources; rendered HTML is derived from the qmd).
SURFACES=(
    "README.md"
    "CLAUDE.md"
    "TROUBLESHOOTING.md"
    "MEMORY.md"
    "guide/workflow-guide.qmd"
    "docs/index.html"
    ".claude/rules/model-routing.md"
    ".claude/references/agent-fleet.md"
    ".claude/scripts/statusline.sh"
)

# A line is allowed to name an older version if it carries one of these markers.
# NOTE (2026-08-21): 'GA 2026-0' was removed — it allowed ANY line carrying a GA date
# to present ANY superseded model as current, which is how two stale guide lines passed.
# Use an explicit <!-- model-allow --> comment for intentional historical mentions.
#
# KNOWN LIMITATION: ALLOW markers are LINE-scoped. One long paragraph containing a
# legitimate 'prior generation' mention will whitelist stale current-state claims on
# the same line. Prefer short lines in model-related prose, or point at the SSoT.
ALLOW='prior generation|prior gen|prior Opus|retire|migrat|historical|deprecat|was:|was |or later|incl\. 4\.|rolling out|beta|(Fable|Opus|Sonnet|Haiku) [0-9]+(\.[0-9]+)?.s |model-allow'

# A line that asserts a DEFAULT ("defaults to", "is the default") makes a claim about
# the current lineup, so the weak comparison markers ("4.7's", "was ", "or later") must
# not excuse it: "Opus 4.8 defaults to `high`, and its `high` does what Opus 4.7's
# `xhigh` did" passed this gate for a month on the strength of the "4.7's" in its own
# second clause. Only an explicit historical marker excuses a default claim.
DEFAULT_CLAIM='defaults? to([^a-z]|$)|is the default([^a-z]|$)|the default (model|on|for)([^a-z]|$)'
ALLOW_STRONG='prior generation|prior gen|historical|retire|deprecat|model-allow'

allowed() {  # allowed <line-text>
    if echo "$1" | grep -qiE "$DEFAULT_CLAIM"; then
        echo "$1" | grep -qiE "$ALLOW_STRONG"
    else
        echo "$1" | grep -qiE "$ALLOW"
    fi
}

# Version token: "4.8", "5", "5.1" — Fable has no minor version at launch, so
# the regex must accept a bare major (the old `4\.[0-9]+` silently skipped it).
VER='[0-9]+(\.[0-9]+)?'

# Model IDs name versions too ("claude-opus-4-8", "claude-haiku-4-5-20251001") and
# never matched "$tier $VER". Normalise each ID on a line to "Tier X.Y" (dropping a
# dated snapshot suffix) so it is checked like prose.
ids_as_versions() {  # ids_as_versions <line-text>  -> one "Tier X.Y" per ID
    echo "$1" | grep -oiE "claude-(fable|opus|sonnet|haiku)(-[0-9]+)+" \
      | sed -E 's/-[0-9]{6,}//g; s/^claude-//; s/-([0-9]+)-([0-9]+)$/ \1.\2/; s/-([0-9]+)$/ \1/' \
      | awk '{ printf "%s%s %s\n", toupper(substr($1,1,1)), tolower(substr($1,2)), $2 }'
}

drift=0
for tier in "Fable" "Opus" "Sonnet" "Haiku"; do
    current="$(echo "$CURRENT_LINE" | grep -oE "$tier $VER" | head -1)"
    [ -n "$current" ] || continue
    for f in "${SURFACES[@]}"; do
        [ -f "$REPO/$f" ] || continue
        while IFS=: read -r lineno text; do
            ver="$(echo "$text" | grep -oE "$tier $VER" | head -1)"
            [ -n "$ver" ] || continue
            [ "$ver" = "$current" ] && continue                 # names the current version → fine
            allowed "$text" && continue                         # allow-marked line → fine
            echo "  $f:$lineno  presents '$ver' (current $tier is '$current')" >&2
            echo "      → $(echo "$text" | sed -E 's/^[[:space:]]+//' | cut -c1-110)" >&2
            drift=1
        done < <(grep -nE "$tier $VER" "$REPO/$f")
    done
done

# Model-ID drift: the same check applied to hyphenated IDs.
for f in "${SURFACES[@]}"; do
    [ -f "$REPO/$f" ] || continue
    while IFS=: read -r lineno text; do
        allowed "$text" && continue
        while read -r idver; do
            [ -n "$idver" ] || continue
            tier="${idver%% *}"
            current="$(echo "$CURRENT_LINE" | grep -oE "$tier $VER" | head -1)"
            [ -n "$current" ] || continue
            [ "$idver" = "$current" ] && continue
            echo "  $f:$lineno  model ID names '$idver' (current $tier is '$current')" >&2
            echo "      → $(echo "$text" | sed -E 's/^[[:space:]]+//' | cut -c1-110)" >&2
            drift=1
        done < <(ids_as_versions "$text")
    done < <(grep -niE "claude-(fable|opus|sonnet|haiku)-[0-9]" "$REPO/$f")
done

# Superlative drift: "newest model" / "most capable" claims are SEMANTIC, not
# version strings — the 2026-06-09 Fable 5 launch made "Opus 4.8 is the newest"
# false while the version check above stayed green. Flag any superlative line
# that names a non-top tier (Opus/Sonnet/Haiku) without mentioning the top tier
# (Fable) and without an allow-marker. Tier-relative phrasings ("the newest
# Opus") are fine and excluded.
TOP_TIER="$(echo "$CURRENT_LINE" | sed -E 's/.*<!-- CURRENT: *//; s/ .*//')"   # e.g. "Fable"
for f in "${SURFACES[@]}"; do
    [ -f "$REPO/$f" ] || continue
    while IFS=: read -r lineno text; do
        echo "$text" | grep -qiE "$TOP_TIER" && continue                       # already credits the top tier
        echo "$text" | grep -qiE "newest (Opus|Sonnet|Haiku)" && continue      # tier-relative superlative → fine
        echo "$text" | grep -qiE "(Opus|Sonnet|Haiku) $VER" || continue        # only flag lines naming a versioned tier
        # NOTE: deliberately NOT short-circuiting on the general $ALLOW list here.
        # A superlative is a claim about the WHOLE lineup; an allow-marker earned by a
        # different clause in the same sentence ("Opus 4.7 is the prior generation",
        # a "GA 2026-.." date) must not suppress it — that exact interaction let
        # "Opus 4.8 is the newest model" slip past this check in v2.1 review. The only
        # explicit escape is an inline model-allow comment placed for THIS claim.
        echo "$text" | grep -q "model-allow" && continue
        echo "  $f:$lineno  superlative claim may be stale (top tier is now '$TOP_TIER'):" >&2
        echo "      → $(echo "$text" | sed -E 's/^[[:space:]]+//' | cut -c1-110)" >&2
        drift=1
    done < <(grep -niE "newest|most capable" "$REPO/$f")
done

if [ "$drift" -ne 0 ]; then
    echo "" >&2
    echo "MODEL-VERSION DRIFT: a superseded version is presented as current." >&2
    echo "Fix the surface to name the current version, or add an allow-marker" >&2
    echo "(e.g. 'prior generation', 'or later', a comparison) if the mention is intentional." >&2
    echo "A line that claims a DEFAULT ('defaults to', 'is the default') accepts only a historical" >&2
    echo "marker ('prior generation', 'historical', 'retire', 'deprecat') or an inline <!-- model-allow -->." >&2
    echo "Source of truth: .claude/references/model-versions.md" >&2
    exit 1
fi

echo "check-model-versions: current-state surfaces match $(echo "$CURRENT_LINE" | sed -E 's/.*<!-- CURRENT: *//; s/ *-->.*//')"
exit 0
