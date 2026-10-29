---
paths:
  - "scripts/**/*.R"
  - "explorations/**"
  - "Figures/**/*.R"
---

# 研究项目编排器（简化版）

**用于 R 脚本、模拟和数据分析** -- 用这个简化循环，而不是完整的多代理编排器。

## 简化循环

```
R / analysis task (user-requested)
  │
  Step 1: IMPLEMENT — Execute plan steps
  │
  Step 2: VERIFY — Run code, check outputs
  │         R scripts: Rscript runs without error
  │         Simulations: set.seed reproducibility
  │         Plots: PDF/PNG created, correct format
  │         If verification fails → fix → re-verify
  │
  Step 3: SCORE — Apply quality-gates rubric
  │
  └── Score >= 80?
        YES → Done (commit when user signals)
        NO  → Fix blocking issues, re-verify, re-score
```

**一个代理，不做审读扇出：** 写、跑、核验、评分。只有当某个技能调用它时（例如 `/review-r`、`/simulation-study`），才去用 `orchestrator-protocol.md` 里的扇出运行时。

## 核验清单

- [ ] 脚本无错误运行
- [ ] 所有包在文件顶部加载
- [ ] 没有硬编码的绝对路径
- [ ] 若为随机过程，在顶部调用 `set.seed()` 一次
- [ ] 输出文件创建在预期路径
- [ ] 容差检查通过（如适用）
- [ ] 质量分 >= 80
