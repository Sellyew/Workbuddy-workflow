#!/bin/bash
# sync_to_docs.sh
# Renders Quarto slides and syncs everything to docs/ for GitHub Pages
#
# Usage: ./scripts/sync_to_docs.sh [lecture_name]
# Examples:
#   ./scripts/sync_to_docs.sh                    # Sync all lectures
#   ./scripts/sync_to_docs.sh Lecture2           # Sync only Lecture2

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUARTO_DIR="$REPO_ROOT/Quarto"
DOCS_DIR="$REPO_ROOT/docs"

echo "=== Syncing Quarto slides to docs/ ==="
echo "Repo root: $REPO_ROOT"

# 1. Render Quarto files
cd "$QUARTO_DIR"

if [ -n "$1" ]; then
    # Render specific lecture. 名字里带空格是合法的（"Aula 1"），所以每个展开都要
    # 加引号：`ls ${1}_*.qmd ${1}.qmd` 会把 "Aula 1" 拆成两段词，再去 glob 出
    # `1.qmd` —— 于是一次针对 Aula 1 的渲染，实际渲染了另一份讲义，且不报错。
    # 精确名优先于带后缀的：Lecture2.qmd 胜过 Lecture2_Intro.qmd。
    echo "Rendering $1..."
    matched_qmd=""
    if [ -f "${1}.qmd" ]; then
        matched_qmd="${1}.qmd"
    else
        for cand in "${1}"_*.qmd; do
            [ -f "$cand" ] && { matched_qmd="$cand"; break; }
        done
    fi
    if [ -n "$matched_qmd" ]; then
        quarto render "$matched_qmd"
    else
        echo "Error: No QMD file found matching '${1}'"
        exit 1
    fi
else
    # Render all QMD files (skip backups)
    echo "Rendering all Quarto files..."
    for qmd in *.qmd; do
        if [ -f "$qmd" ] && [[ ! "$qmd" == *"_backup"* ]]; then
            echo "  Rendering $qmd..."
            quarto render "$qmd" || echo "  Warning: Failed to render $qmd"
        fi
    done
fi

# 2. Sync HTML files and their _files directories to docs/slides/
echo "Syncing HTML and assets to docs/slides/..."
mkdir -p "$DOCS_DIR/slides"

for html in *.html; do
    if [ -f "$html" ]; then
        echo "  Copying $html..."
        cp "$html" "$DOCS_DIR/slides/"

        # Copy associated _files directory if it exists
        files_dir="${html%.html}_files"
        if [ -d "$files_dir" ]; then
            echo "  Copying $files_dir/..."
            rm -rf "$DOCS_DIR/slides/$files_dir"
            cp -r "$files_dir" "$DOCS_DIR/slides/"
        fi
    fi
done

# 3. Sync Beamer PDFs to docs/slides/
echo "Syncing Beamer PDFs..."
for pdf in "$REPO_ROOT/Slides/"*.pdf; do
    if [ -f "$pdf" ]; then
        echo "  Copying $(basename "$pdf")..."
        cp "$pdf" "$DOCS_DIR/slides/"
    fi
done

# 4. Sync R scripts to docs/files/code/
echo "Syncing R scripts..."
mkdir -p "$DOCS_DIR/files/code"
for rscript in "$REPO_ROOT/scripts/R/"*.R; do
    if [ -f "$rscript" ]; then
        echo "  Copying $(basename "$rscript")..."
        cp "$rscript" "$DOCS_DIR/files/code/"
    fi
done

# 5. Sync Figures directory (using rsync for efficiency)
echo "Syncing Figures/..."
if command -v rsync &> /dev/null; then
    rsync -av --delete "$REPO_ROOT/Figures/" "$DOCS_DIR/Figures/"
else
    rm -rf "$DOCS_DIR/Figures"
    cp -r "$REPO_ROOT/Figures" "$DOCS_DIR/Figures"
fi

echo ""
echo "=== Sync complete! ==="
echo "Files synced to: $DOCS_DIR/slides/"
