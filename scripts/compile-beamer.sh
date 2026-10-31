#!/usr/bin/env bash
# =============================================================================
# compile-beamer.sh — 编译 Slides/ 下的一套 Beamer 幻灯片（XeLaTeX 3 遍 + bibtex）
#
# 用法：
#   scripts/compile-beamer.sh <名字>             # Slides/<名字>.tex
#   scripts/compile-beamer.sh Lecture1.tex
#   scripts/compile-beamer.sh Lecture1 --dry-run  # 只打印将要用的环境变量
#
# 为什么需要一个脚本，而不是在技能里写一行 xelatex
# -------------------------------------------------
# 这套幻灯片的主题在 Preambles/ 里，所以必须设 TEXINPUTS。而 kpathsea 的语义是：
#
#   TEXINPUTS 的值**替换**默认搜索路径，**除非它以路径分隔符结尾**（结尾表示
#   「在这之后追加默认值」）。默认值里含 '.'，也就是当前目录。
#
# 少写那个结尾分隔符，当前目录就从搜索路径里消失——于是连主文件都找不到：
#
#   ! I can't find file `Lecture1.tex'.
#   ! Emergency stop.
#
# 这条报错说的是「文件不存在」，而真实原因是「搜索路径里没有 .」。照它去查文件
# 会一无所获，因为文件就在那儿。
#
# 分隔符本身还是平台相关的：POSIX 的 kpathsea 用 ':'，**Windows 版 TeX Live 用 ';'**。
# 在 Windows 上写 ':' 不会被当成分隔符，等价于「没有结尾分隔符」，于是同样落到
# 上面那条误导性报错上。写死任何一个字符都会在另一个平台上坏掉。
#
# 不落自己的临时文件：xelatex 写 <名字>.log，bibtex 写 <名字>.blg，两者都在
# Slides/ 里，比脚本另建临时文件更可靠，也不用删。
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SLIDES="$ROOT/Slides"

# kpathsea 的路径分隔符。Git Bash 会导出 OS=Windows_NT；Linux 与 macOS 没有这个变量。
if [ "${OS:-}" = "Windows_NT" ]; then
    SEP=';'
else
    SEP=':'
fi

# 把 Preambles/ 放到搜索路径**前面**，并保证以 $SEP 结尾（见文件头）。
# 已有的 TEXINPUTS 接在后面；它自身的分隔符由调用者负责，这里只管前置。
texinputs() { printf '%s%s%s' "../Preambles" "$SEP" "${TEXINPUTS:-}"; }
bibinputs() { printf '%s%s%s' ".." "$SEP" "${BIBINPUTS:-}"; }

usage() {
    sed -n '3,9p' "$0" | sed 's/^# \{0,1\}//'
}

NAME=""
DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        -h|--help) usage; exit 0 ;;
        --dry-run) DRY_RUN=1 ;;
        -*) echo "compile-beamer: 不认识的选项 $arg" >&2; exit 2 ;;
        *) NAME="$arg" ;;
    esac
done

if [ -z "$NAME" ]; then
    echo "compile-beamer: 需要一个文件名（可带或不带 .tex）" >&2
    usage >&2
    exit 2
fi
NAME="${NAME%.tex}"

TEX="$SLIDES/$NAME.tex"
if [ ! -f "$TEX" ]; then
    echo "compile-beamer: 找不到 $TEX" >&2
    echo "            Slides/ 里有：" >&2
    for f in "$SLIDES"/*.tex; do
        [ -e "$f" ] && echo "              ${f##*/}" >&2
    done
    exit 2
fi

TEX_PATH="$(texinputs)"
BIB_PATH="$(bibinputs)"
LOG="$SLIDES/$NAME.log"
BLG="$SLIDES/$NAME.blg"
PDF="$SLIDES/$NAME.pdf"

# bibtex 只在真的引用过东西时才跑：aux 里没有 \citation 时 bibtex 会报错退出，
# 而那份报错与「你的幻灯片有问题」无关。
if grep -qE '\\(cite[a-zA-Z]*|bibliography|printbibliography)\b' "$TEX"; then
    NEEDS_BIB=1
else
    NEEDS_BIB=0
fi

if [ "$DRY_RUN" = "1" ]; then
    echo "file      : $TEX"
    echo "sep       : '$SEP'  (OS=${OS:-<unset>})"
    echo "TEXINPUTS : $TEX_PATH"
    echo "BIBINPUTS : $BIB_PATH"
    echo "bibtex    : $([ "$NEEDS_BIB" = 1 ] && echo yes || echo no)"
    exit 0
fi

command -v xelatex >/dev/null 2>&1 || {
    echo "compile-beamer: 找不到 xelatex。装 TeX Live 或在 PATH 里加上它的 bin 目录。" >&2
    exit 2
}

# 路径在 cd 之前就全部绝对化：$0 可能是相对路径，cd 之后再解析会指错地方。
cd "$SLIDES" || exit 2

# 上一次成功编译的 PDF 会留在原地。只看「PDF 存在」会把旧产物当成这次的成果，
# 所以用时间戳区分：mtime 早于本次开始的一律不算。
START=$(date +%s)

# 最后一遍 xelatex 的输出。不能只靠 <名字>.log 判断失败原因：找不到主文件时
# xelatex 会去写 texput.log，那个名字里没有 <名字>，于是用 $LOG 找线索会落空。
LAST_OUT=""

run_pass() {
    echo "── 第 $1 遍 xelatex ──"
    LAST_OUT="$(TEXINPUTS="$TEX_PATH" BIBINPUTS="$BIB_PATH" \
        xelatex -interaction=nonstopmode "$NAME.tex" 2>&1)"
    # 第一遍缺 aux 而退出非零是正常的；成败由最后的 PDF 与 log 判定。
    return 0
}

run_pass 1

if [ "$NEEDS_BIB" = "1" ]; then
    echo "── bibtex ──"
    TEXINPUTS="$TEX_PATH" BIBINPUTS="$BIB_PATH" bibtex "$NAME" >/dev/null 2>&1
    if [ ! -f "$BLG" ]; then
        echo "   bibtex 没有产出 .blg——它可能根本没启动"
    elif grep -qE "^(I couldn't open|I found no)" "$BLG"; then
        echo "   bibtex 报告了问题："
        grep -E "^(I couldn't open|I found no|Warning--)" "$BLG" | head -10 | sed 's/^/     /'
    fi
    run_pass 2
fi

run_pass 3

echo
if [ ! -f "$PDF" ] || [ "$(stat -c %Y "$PDF" 2>/dev/null || echo 0)" -lt "$START" ]; then
    if [ -f "$PDF" ]; then
        echo "✗ PDF 是上一次编译留下的，本次没有重新产出。" >&2
    else
        echo "✗ 没有产出 PDF。" >&2
    fi
    # 最常见的真实原因：TEXINPUTS 少了结尾分隔符 → 默认搜索路径（含 '.'）被丢掉
    # → 连主文件都找不到。报错写的是「文件不存在」，照它去查文件会一无所获。
    if printf '%s' "$LAST_OUT" | grep -q "I can't find file"; then
        echo "   xelatex 说找不到 $NAME.tex，但那个文件就在 Slides/ 里。" >&2
        echo "   这通常意味着 TEXINPUTS 没有以路径分隔符结尾，默认搜索路径被整个替换掉了。" >&2
        echo "   本次用的是：'$TEX_PATH'（分隔符 '$SEP'，OS=${OS:-<unset>}）" >&2
    fi
    echo "   最后一遍 xelatex 的输出尾部：" >&2
    printf '%s\n' "$LAST_OUT" | tail -25 | sed 's/^/    /' >&2
    exit 1
fi

ERRORS=$(grep -c '^!' "$LOG" 2>/dev/null || true)
OVERFULL=$(grep -c 'Overfull \\hbox' "$LOG" 2>/dev/null || true)
UNDEF_CITE=$(grep -c 'Citation .* undefined' "$LOG" 2>/dev/null || true)
UNDEF_REF=$(grep -c "Reference .* undefined" "$LOG" 2>/dev/null || true)
# 缺字形是这套工作流里最容易被当成「编译成功」的一种失败：没有 CJK 字体时，
# xelatex 为每个汉字打一条 Missing character，PDF 照常产出、退出码 0、错误数为 0，
# 打开一看正文全是空白。所以它必须出现在报告里，而不是留在 log 里等人 grep。
MISSING=$(grep -c 'Missing character' "$LOG" 2>/dev/null || true)
PAGES=$(sed -n 's/.*Output written on .* (\([0-9][0-9]*\) page.*/\1/p' "$LOG" | tail -1)

echo "────────────────────────────────────────────────"
printf 'PDF        : %s\n' "${PDF#"$ROOT"/}"
printf '页数       : %s\n' "${PAGES:-?}"
printf '错误       : %s\n' "${ERRORS:-0}"
printf 'Overfull   : %s 个 \\hbox\n' "${OVERFULL:-0}"
printf '未定义引文 : %s\n' "${UNDEF_CITE:-0}"
printf '未定义引用 : %s\n' "${UNDEF_REF:-0}"
printf '缺字形     : %s\n' "${MISSING:-0}"
echo "────────────────────────────────────────────────"

if [ "${MISSING:-0}" -gt 0 ]; then
    echo
    echo "缺字形：这些字符在 PDF 里是空白，而编译本身没报错。" >&2
    echo "  中文正文出现这一条，通常意味着没有加载 CJK 字体（Preambles/header.tex 里的" >&2
    echo "  xeCJK 段）；其他情形多半是某个符号字体缺失。前几个缺失字符：" >&2
    grep -o 'Missing character: There is no .* in font' "$LOG" 2>/dev/null \
        | sed 's/^/    /' | sort -u | head -5 >&2
fi

if [ "${ERRORS:-0}" -gt 0 ]; then
    echo
    echo "错误行（log 里以 '!' 开头的）：" >&2
    grep -A2 '^!' "$LOG" | head -30 | sed 's/^/    /' >&2
    exit 1
fi

if [ "${UNDEF_CITE:-0}" -gt 0 ] || [ "${UNDEF_REF:-0}" -gt 0 ]; then
    echo
    echo "引文/引用未解析——通常是漏跑 bibtex，或键名拼错："
    grep -E 'Citation .* undefined|Reference .* undefined' "$LOG" | sort -u | head -10 | sed 's/^/    /'
fi

exit 0
