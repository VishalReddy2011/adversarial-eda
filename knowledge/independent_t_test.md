---
id: independent_t_test
title: Independent t-test
function_name: independent_t_test
specialist: bivariate
arg_schema:
- numeric
- group
column_types:
  numeric: numeric
  group: categorical
group_count: exactly_2
min_sample:
  per_group: 2
returns:
- statistic
- p_value
- n
- group_a
- group_b
- group_a_n
- group_b_n
- cohen_d
alternatives:
- mann_whitney_u
- one_way_anova
tags:
- group-comparison
- parametric
  - two-groups
---
## Purpose
The independent t-test compares the means of a numeric outcome between two
independent groups. It answers: *Is the average value of Y in group A
statistically different from the average in group B?* For example, it can test
if blood pressure differs between two treatment groups.
## When To Use
Use this test when you have one numeric (continuous) dependent variable and one
categorical independent variable with exactly two independent groups. Each
subject appears in only one group (e.g., male vs. female, or treatment vs.
control). Each group should have at least two observations. The data in each
group should be roughly normally distributed for inference, although the t-test
is fairly robust to mild deviations.
## Do Not Use When
Do not use an independent t-test if the groups are related (e.g., paired or
repeated measures). If there are more than two groups, use ANOVA. Avoid it if
the outcome is ordinal or nominal. If the dependent variable is heavily non-
normal and groups are unbalanced, a nonparametric alternative like the Mann-
Whitney U test is preferable.
## Assumptions
- **Independence**: Observations in each group are independent of each other
. No participant is in both groups.
- **Normality**: The numeric outcome is approximately normally distributed
within each group (especially important if sample sizes are small).
- **Homogeneity of Variance**: The two groups have equal population variances
. This can be tested (e.g. Levene's test) and adjusted for (Welch's t-test)
if violated.
- **Group Size**: Ideally at least 2 per group, though more is better for
reliable inference.
## Alternatives
If the normality assumption is violated, use **Mann-Whitney U** for two groups
. If variances are unequal, use **Welch's t-test**. For paired data, use the
paired t-test instead. For more than two groups, use ANOVA or its nonparametric
counterpart (Kruskal-Wallis).
## Interpretation
The `statistic` is the t-value comparing group means. The `p_value` tests the
null hypothesis that the group means are equal. A small p-value indicates a
significant difference in means. Output also includes `n` (total sample size),
`group_a` and `group_b` labels, and their sizes (`group_a_n`, `group_b_n`). The
`cohen_d` gives a standardized effect size. For example, t(48) = 2.30, p = 0.025
might indicate the mean in group A is significantly higher than group B.
## Rejection Rules
If the p-value >= α (e.g. 0.05), do not reject the null: conclude no significant
difference. If assumptions (normality or equal variance) are clearly violated,
the t-test result may not be valid, and a nonparametric test should be
considered. A very small p-value (p < α) leads to rejecting the null, suggesting
a significant mean difference.
## Reporting Guidance
Report the t-statistic, degrees of freedom, p-value, and group means. For
example: "The independent t-test comparing scores for Group A (M=10.5, SD=2.1)
and Group B (M=8.3, SD=1.9) was significant, t(48) = 2.30, p = 0.025, Cohen's d
= 0.65. This indicates Group A's mean score was significantly higher." Use
phrasing like "significantly different" or "no significant difference" to
describe the result.
