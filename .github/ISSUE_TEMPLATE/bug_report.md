---
name: Bug report
about: Report a bug in the template (skill, agent, hook, rule, doc, or script).
title: "[BUG] "
labels: bug
---

## What happened?

<!-- Brief description. Include the exact command or skill you ran. -->

## What did you expect?

<!-- One or two sentences. -->

## Steps to reproduce

1.
2.
3.

## Environment

- **OS:** macOS / Linux / Windows
- **WorkBuddy version:** 客户端「关于」页显示的版本号（桌面端没有 `--version` 命令）
- **Quarto version:** `quarto --version` (if relevant)
- **XeLaTeX version:** `xelatex --version | head -1` (if relevant)
- **Template version/commit:** `git log --oneline -1` or `git describe --tags`

## Logs / output

<!-- Paste relevant terminal output, error messages, or screenshots. Trim to the relevant section. -->

```text

```

## Have you checked

- [ ] `./scripts/validate-setup.sh` exits cleanly
- [ ] The bug is in the **template** (not in your fork's customizations)
- [ ] The bug is reproducible from a clean clone
