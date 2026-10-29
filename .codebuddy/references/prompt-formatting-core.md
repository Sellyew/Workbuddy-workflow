# 提示词格式化核心 —— 已退役（v2.6）

本文件曾存放 `/prompt` 与 `/prompt-only` 两个技能使用的六段式提示词骨架（Role／Task／Context／Constraints／Output format／Bookend），这两个技能已在 v2.0 退役。文件在 v2.6 被移除：它的脚手架（以禁止为主的约束、固定的行数与句数上限、强制性的收尾自检）正是当前 Claude 模型会照字面过度执行的那种规定，而它唯一还活着的指针与取代它的规则相互矛盾。

它描述的习惯现在活在一条简短的规则里：[`prompt-shaping.md`](../rules/prompt-shaping.md)。这具存根留着，是为了历史 CHANGELOG 里的链接还能解析。
