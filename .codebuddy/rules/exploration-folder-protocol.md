---
paths:
  - "explorations/**"
---

# 探索目录规程

**所有实验性工作都先进 `explorations/`。**绝不直接放进生产目录。

## 目录结构

```
explorations/
├── ACTIVE_PROJECTS.md
├── [project]/
│   ├── README.md          # Goal, status, findings
│   ├── R/                 # Code (use _v1, _v2 for iterations)
│   ├── scripts/           # Test scripts
│   ├── output/            # Results
│   └── SESSION_LOG.md     # Progress notes
└── ARCHIVE/
    ├── completed_[project]/
    └── abandoned_[project]/
```

## 生命周期

1. **创建** —— `mkdir -p explorations/[name]/{R,scripts,output}` + 从 `templates/exploration-readme.md` 取的 README
2. **开发** —— 全部工作都在探索目录内完成
3. **决策：**

   - **升级为生产** —— 复制到 `R/`、`scripts/`；要求质量 >= 80、测试通过、代码清晰。移到 `ARCHIVE/completed_[project]/`
   - **继续探索** —— 在 README 里记下下一步
   - **放弃** —— 连同说明移到 `ARCHIVE/abandoned_[project]/`（用 `templates/archive-readme.md`）

## 升级清单

- [ ] 质量分 >= 80
- [ ] 所有测试通过
- [ ] 结果在容差内可复现
- [ ] 不看深层上下文也能读懂代码
- [ ] README 说明了做法与发现
