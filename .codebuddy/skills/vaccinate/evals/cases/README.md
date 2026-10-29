# 评测用例

一个用例一个文件。提示词是 `## Prompt` 与 `## Assert` 之间的一切；断言
是 `## Assert` **到下一个标题**之间的那些 `- ` 行——所以把备注写在
`## Prompt` 之上，或放在断言块之后它们自己的标题下。

```markdown
## Prompt
The exact user message to send, verbatim. Write what a real user would type,
not a well-specified instruction — the point is to test the skill's triggering
and its instructions, not your prompt-writing.

## Assert
- a literal substring that must appear in a correct answer
- another one
```

**断言是字面子串，大小写不敏感地匹配。** 这是故意做粗的：一个本身是模型的
评分器，会引入正在被测量的那种失效模式。如果一个用例没法用子串评分，它大概
不是一个用例——而是一个判断，判断归你自己。

## 写出能测到东西的用例

- **提示词要逼真。** "review this" 胜过 "using the seven-pass protocol, review this"，
  因为后者测的是你对技能的记忆，而不是技能本身。
- **断言落在实质上，不落在形状上。** 断言某个具体缺陷被点名，而不是断言
  答案里含 "## Findings"。
- **要有本不该触发的用例。** 一个什么都触发的技能，和一个从不触发的技能一样坏。
  把它们命名为 `nottrigger-*.md`，并断言该技能的招牌输出是*缺席*的。
- **两到三次重复。** 单次运行分不开真实的改进与抽样噪声。

## 优先级顺序

按**出错的代价**排序，不按使用频率：
`/review-paper --peer` → `claim-verifier` → `/audit-reproducibility` → `/challenge`。
