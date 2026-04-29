---
id: kruskal_wallis
title: Kruskal-Wallis test
function_name: kruskal_wallis
specialist: bivariate
arg_schema:
- numeric
- group
column_types:
  numeric: numeric
  group: categorical
group_count: at_least_3
min_sample:
  per_group: 2
returns:
- statistic
- p_value
- n
alternatives:
- one_way_anova
tags:
- group-comparison
- nonparametric
  - multiple-groups
---
## Purpose
The Kruskal-Wallis H test is a nonparametric method for comparing the
distributions of a numeric outcome across three or more independent groups. 27
It answers: *Are there statistically significant differences in the median or
rank-sums of the groups?* It does not assume normality, so it can be used when
ANOVA's assumptions are violated.
## When To Use
Use Kruskal-Wallis when you have one numeric (or ordinal) dependent variable and
one categorical independent variable with three or more independent groups. It
is suitable if data are not normally distributed or if sample sizes are small.
For example, use it to compare exam performance across several teaching methods
when scores are skewed.
## Do Not Use When
Do not use it if you only have two groups (use Mann-Whitney instead). Do not use
it for dependent (paired) data (use Friedman's test for repeated measures). If
the data are normally distributed, one-way ANOVA is more powerful.
## Assumptions
- **Ordinal/Continuous Data**: Dependent variable is at least ordinal.
- **Independent Groups**: Each subject is in only one group; observations are
independent.
- **Similar Distribution Shapes**: To interpret differences in medians, the
group distributions should have similar shapes (e.g., spreads).
- **No Normality Assumption**: Does not require normally distributed data
(unlike ANOVA).
## Alternatives
One-way ANOVA is the parametric alternative (if normality holds). For two
groups, use Mann-Whitney. If you want to test for a trend across ordered groups,
the Jonckheere-Terpstra test is an option.
## Interpretation
The test statistic `H` (sometimes reported as `statistic`) and `p_value`
indicate whether at least one group differs. If p < α, conclude that not all
group distributions are equal (omnibus test). For example, H(2) = 7.53, p =
0.023 suggests a significant difference among three groups. The total sample
size is `n`.
## Rejection Rules
If p >= α, do not reject the null: no evidence of difference among groups. If p <
α, reject the null hypothesis that all groups have the same distribution. Note
that Kruskal-Wallis doesn't indicate which groups differ; use post-hoc
comparisons (e.g., pairwise Mann-Whitney tests with adjustment) if significant.
## Reporting Guidance
Report the H statistic and p-value. E.g.: "A Kruskal-Wallis test indicated a
significant difference between the three groups (H(2) = 7.53, p = 0.023)."
Include median (or mean rank) values for each group. If significant, report
follow-up tests or state which groups differ.
