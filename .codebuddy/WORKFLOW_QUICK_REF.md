# 工作流速查

**模型：** 承包商（你指挥，Claude 执行编排）

---

## 那个循环

```
Your instruction
    ↓
[PLAN] (if multi-file or unclear) → Show plan → Your approval
    ↓
[EXECUTE] Implement, verify, done
    ↓
[REPORT] Summary + what's ready
    ↓
Repeat
```

---

## 我什么时候问你

- **设计分叉：**「A 方案（快）vs B 方案（稳）。选哪个？」
- **代码含糊：**「规格里 X 没说清。按 Y 假设？」
- **复现的边角情形：**「刚好差一点没进容差。要查吗？」
- **范围问题：**「顺手把 Y 也重构了，还是只做 X？」

---

## 我什么时候直接做

- 代码修法是显然的（bug、套用已有模式）
- 验证（容差检查、测试、编译）
- 文档（日志、提交）
- 画图（按既定标准）
- 部署（你批准之后，我自动发布）

---

## 质量门禁（没有例外）

| 分数 | 动作 |
|-------|--------|
| >= 80 | 可以提交 |
| < 80  | 修掉阻断问题 |

---

## 不容商量的事（请改成你的）

<!-- 换成你所在项目锁定下来的偏好 -->

- [YOUR PATH CONVENTION]（例如 R 用 `here::here()`，LaTeX 用相对路径）
- [YOUR SEED CONVENTION]（例如随机代码在顶部 `set.seed()` 一次）
- [YOUR FIGURE STANDARDS]（例如白底、300 DPI、自定义主题）
- [YOUR COLOR PALETTE]（例如机构配色）
- [YOUR TOLERANCE THRESHOLDS]（例如点估计用 1e-6）

---

## 偏好

<!-- 你摸清自己的工作方式后就填上 -->

**视觉：** [你想怎么处理图/绘图]
**报告：** [要点式简短？成段详述？按需给细节？]
**会话日志：** 总是（计划后、增量、会话结束）
**复现：** [多严？靠近容差就标出来？]

---

## 探索模式

做实验性工作时，用**快速通道**工作流：
- 在 `explorations/` 目录里做事
- 质量阈值 60/100（生产级是 80/100）
- 不需要计划——只做一次研究价值检查（2 分钟）
- 见 `.codebuddy/rules/exploration-fast-track.md`

---

## 下一步

你给任务 → 我（必要时）做计划 → 你批准 → 执行 → 完成。
