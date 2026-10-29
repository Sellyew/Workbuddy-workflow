# 预注册模板

本模板由 `.codebuddy/skills/preregister/SKILL.md` 消费。它含三套风格的段落（OSF、AsPredicted、AEA RCT 登记处）。技能依据 `--style` 或该领域的默认值选一套。

**输出约定。** 技能把所选风格填好的表单写到 `quality_reports/preregistrations/YYYY-MM-DD_<slug>.md`（已 gitignore）。由用户自己上传到登记处；本模板*不是*一个登记处提交工具。

**标注图例。** 每个字段都带一个标记：

- **MUST** —— 登记处强制要求；没有它文档无法提交。
- **SHOULD** —— 强烈建议；审阅者期待它有。
- **MAY** —— 可选；相关才写。

对任何**输入描述没有提供**的 **MUST** 字段，写 `[CLARIFY: <具体问题>]`。不要编造。

---

## 风格 1 —— OSF（Open Science Framework）

OSF 的「Preregistration」模板。政治学、心理学与广义社会科学研究的默认选择。在 `osf.io/registries` 上传。

```markdown
---
title: <Study title>
authors: <Author1, Author2, ...>
date: YYYY-MM-DD
version: 1
style: osf
source-spec: <path to quality_reports/specs/... if applicable>
---

# Preregistration — <Study title>

## 1. Study Information (MUST)

### 1.1 Title
<Concise title that names the design and outcome>

### 1.2 Authors
<List with affiliations>

### 1.3 Description
<2–4 sentence study summary: what, why, who, when>

### 1.4 Hypotheses (MUST — directional)
**H1.** <Directional claim, e.g., "Treatment T increases outcome Y compared to control C">.
**H2.** <…>

## 2. Design (MUST)
- **Type:** experimental / quasi-experimental / observational
- **Manipulation (if any):** <description>
- **Randomisation unit:** individual / group / cluster / time
- **Blinding:** <single / double / open>

## 3. Sampling Plan (MUST)
- **Population:** <who>
- **Recruitment / data source:** <where from>
- **Target N:** <number, with justification>
- **Stopping rule:** <e.g., "stop at N=1,200 or 4 weeks, whichever first">
- **Power calculation:** <effect size assumed, alpha, power, resulting N>

## 4. Variables (MUST)
- **Primary outcome (Y):** <name, measurement, units>
- **Treatment (T):** <name, levels, encoding>
- **Pre-registered covariates:** <list>

## 5. Analysis Plan (MUST)
- **Primary estimator:** <e.g., "OLS with treatment dummies and pre-registered covariates, HC2 robust SEs">
- **Inference criterion:** <e.g., "two-sided alpha = 0.05; we will conclude H1 supported if the OLS coefficient on T is positive and statistically significant at this threshold">
- **Pre-registered specifications:** numbered (1, 2, 3) with explicit functional form for each
- **Multiple-testing correction (if H > 1):** <Bonferroni / Benjamini-Hochberg / none + justification>

## 6. Inference Criteria (MUST)
- **Confirmatory test of H1:** <exact decision rule>
- **What would make us reject H1:** <quantitative threshold>
- **Equivalence test (if used):** <bounds>

## 7. Data Exclusions (MUST — ex ante)
- **Outliers:** <e.g., "exclude observations with completion time < 60 seconds">
- **Failed manipulation checks:** <rule>
- **Other:** <rule>

## 8. Missing Data (MUST)
- **Treatment of missingness:** <listwise / multiple imputation / MAR assumption>
- **If MI: imputation model:** <specification>

## 9. Exploratory Analyses (MAY)
> Anything below this point is **exploratory** and not part of the confirmatory test.

- <Optional analyses, clearly labelled>

## 10. Other (MAY)
- **Pilot data already collected?** Yes / No (if yes: were the pilot results used to set H1? Disclose.)
- **Conflicts of interest:** <disclosure>
- **Funding source:** <disclosure>
```

---

## 风格 2 —— AsPredicted

AsPredicted 的 9 问表单（aspredicted.org）。为实验室心理学与短周期实验研究而设。在 `aspredicted.org/create.php` 上传。

```markdown
---
title: <Study title>
date: YYYY-MM-DD
style: aspredicted
source-spec: <path>
---

# AsPredicted — <Study title>

## 1. Have any data been collected for this study yet? (MUST)
<Yes — describe pilot status / No>

## 2. What's the main question being asked or hypothesis being tested? (MUST — directional)
<H1: directional claim>

## 3. Describe the key dependent variable(s) specifying how they will be measured. (MUST)
<Y, with measurement and units>

## 4. How many and which conditions will participants be assigned to? (MUST)
<List conditions, randomisation procedure, allocation ratio>

## 5. Specify exactly which analyses you will conduct to examine the main question/hypothesis. (MUST)
<Estimator, primary specification, inference rule>

## 6. Describe exactly how outliers will be defined and handled, and your precise rule(s) for excluding observations. (MUST)
<Ex-ante rules>

## 7. How many observations will be collected, or what will determine sample size? (MUST)
<Target N or stopping rule, with power-calc justification>

## 8. Anything else you would like to pre-register? (MAY)
<Robustness specs, secondary outcomes, equivalence tests>

## 9. Name (NOTE: this is for the study, not the paper). (MUST)
<short codename>
```

---

## 风格 3 —— AEA RCT 登记处

美国经济学会的 RCT 登记处（socialscienceregistry.org）。自 2018 年起，向 AEA 系列期刊投任何随机干预研究都**必须**登记。在 `socialscienceregistry.org/trials/create` 上传。

```markdown
---
title: <Trial title>
investigators: <PI names + affiliations>
date: YYYY-MM-DD
style: aea-rct
source-spec: <path>
---

# AEA RCT Registry — <Trial title>

## Trial Information (MUST)
- **Status:** Not yet on the air / In development / On going / Completed
- **Start date:** YYYY-MM-DD
- **End date (planned):** YYYY-MM-DD
- **Geographic region:** <Country, sub-national region>

## Intervention (MUST)
- **Description:** <what is delivered, by whom, when>
- **Comparison group(s):** <pure control / placebo / active control>
- **Implementation partners:** <NGO, government agency, etc.>

## Primary Outcomes (MUST)
- **Y1 (primary):** <name, measurement, time of measurement>
- **Y2 (secondary, optional):** <…>

## Primary Hypotheses (MUST — directional)
**H1.** <Directional claim about Y1 under T vs C>

## Sample (MUST)
- **Target N:** <number>
- **Eligibility criteria:** <inclusion / exclusion>
- **Randomisation unit:** individual / household / village / school / clinic
- **Randomisation method:** <stratified, paired, blocked, simple>
- **Allocation ratio:** <e.g., 1:1>

## Power Calculation (SHOULD)
- **Assumed effect size:** <SD units>
- **Alpha / power:** <0.05 / 0.80>
- **Resulting N (and ICC if clustered):** <…>

## Pre-Analysis Plan (MAY — attach as PDF)
- **Estimator:** <ANCOVA / panel FE / cluster-robust OLS>
- **Specifications:** numbered, with controls listed
- **Multiple testing:** <correction or family-wise rule>
- **Heterogeneity analyses:** <pre-specified subgroups>
- **Sensitivity / robustness:** <bounds analysis, alternative SEs, attrition adjustments>

## IRB / Ethical Approval (MUST for AEA submission)
- **IRB:** <institution>
- **Approval number:** <#>
- **Date of approval:** YYYY-MM-DD

## Data Sharing (SHOULD)
- **Public data plan:** <yes / no / restricted>
- **Replication code:** <will be deposited in the AEA Data and Code Repository (openICPSR) — see AEA Data and Code Availability Policy>

## Conflicts of Interest (MUST)
<Disclosure>

## Funding (MUST)
<Source(s)>
```

---

## 风格映射（跨登记处）

对需要在某个登记处发布、却要按另一家的惯例报告结果的用户，大致映射是：

| OSF 小节 | AsPredicted 问题 | AEA RCT 字段 |
|---|---|---|
| 1.4 假设 | Q2 | Primary Hypotheses |
| 2 设计 | Q4（条件） | Intervention |
| 3 抽样计划 | Q7 | Sample + Power Calc |
| 4 变量 | Q3（因变量） | Primary Outcomes |
| 5 分析计划 | Q5 | Pre-Analysis Plan |
| 7 数据排除 | Q6 | （在 PAP 附件里） |
| 6 推断判据 | （隐含在 Q5 中） | （在 PAP 附件里） |

这张映射是近似的——各登记处的粒度不同。拿不准时，直接用该登记处自己的原生模板。

---

## 这个模板住在哪

- **文件：** `templates/preregistration-template.md`
- **消费者：** `.codebuddy/skills/preregister/SKILL.md`
- **输出：** `quality_reports/preregistrations/YYYY-MM-DD_<slug>.md`（已 gitignore）
- **登记处网址：** OSF（osf.io/registries）、AsPredicted（aspredicted.org）、AEA RCT（socialscienceregistry.org）
