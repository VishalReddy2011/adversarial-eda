---
id: mann_whitney_u
title: Mann-Whitney U test
function_name: mann_whitney_u
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
alternatives:
- independent_t_test
tags:
- group-comparison
- nonparametric
  - two-groups
---
## Purpose
The Mann-Whitney U test (also known as the Wilcoxon rank-sum test) compares two
independent groups on a continuous or ordinal outcome. It tests whether one
group tends to have higher values than the other without assuming normality.
It answers: *Is the distribution (or median) of Y different between group A and
group B?*
## When To Use
Use this test for one numeric (or ordinal) dependent variable and one
categorical independent variable with exactly two independent groups. It is
appropriate when the data are not normally distributed or when using ordinal
data (e.g., survey rankings). Each observation must be independent and belong to
only one group. For example, comparing pain scores between two types of
treatment in a small sample.
## Do Not Use When
Do not use Mann-Whitney if there are more than two groups (use Kruskal-Wallis
instead). Do not use if data are paired (use Wilcoxon signed-rank test). If
the data are truly interval/ratio and meet t-test assumptions, an independent t-
test may be more appropriate. Also, if the two group distributions have very
different shapes, Mann-Whitney results are harder to interpret in terms of
median difference.
## Assumptions
- **Independence**: Observations in each group are independent of one another
.
- **Ordinal or Continuous Scale**: The dependent variable should at least be
ordinal (ranks) or continuous.
- **Same-Shaped Distributions**: If you wish to interpret the test as comparing
medians, the two groups should have similarly shaped distributions.
- **Two Groups**: Exactly two independent groups are compared.
## Alternatives
If the normality assumption holds, an independent t-test is an alternative. For
more than two groups, use **Kruskal-Wallis**. If the data are matched, use the
Wilcoxon signed-rank test.
## Interpretation
The `statistic` typically refers to the U value. A low p-value indicates the
distributions differ significantly. Note: Mann-Whitney tests whether one
distribution tends to yield larger values; it is often described in terms of
medians when shapes are similar. The sample size `n` is total observations. For
example, U = 250, p = 0.015 suggests a significant difference in ranks (group
locations).
## Rejection Rules
If p >= α, do not reject the null hypothesis of equal distributions/medians. If p
< α, reject the null, concluding a significant difference. If the distributions
have markedly different shapes, this test may not be validly interpreted as a
median test.
## Reporting Guidance
Report the U statistic (if available) or simply report the effect in words:
e.g., "The Mann-Whitney U test showed a significant difference between groups (U
= 250, p = 0.015)." You can add group medians: "Group A had a higher median
score (10.5) than Group B (8.0)." Emphasize direction ("higher in one group")
since it's a two-sided test by default.
