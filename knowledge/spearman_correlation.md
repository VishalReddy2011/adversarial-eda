---
id: spearman_correlation
title: Spearman correlation
function_name: spearman_correlation
specialist: bivariate
arg_schema:
- x
- y
column_types:
  x: numeric
  y: numeric
returns:
- statistic
- p_value
- n
alternatives:
- pearson_correlation
tags:
- association
- nonparametric
  - numeric-correlation
---
## Purpose
Spearman's rank correlation measures the strength and direction of a
*monotonic* relationship between two variables. It answers: *When one
variable increases, does the other tend to increase (or decrease) consistently?
* The statistic (rho) ranges from -1 to 1, where values near +/-1 indicate a
strong monotonic association even if not strictly linear.
## When To Use
Use Spearman's correlation when at least one variable is ordinal or when the
relationship is not necessarily linear but is monotonic (always increasing or
always decreasing). It's especially appropriate if the data have outliers or are
not normally distributed. For example, if you rank students by scores on two
tests, Spearman's rho will measure how similarly the ranks align. Both variables
should be at least ordinal. Observations should be independent and paired.
## Do Not Use When
Do not use Spearman's rho if the relationship is linear and data are interval/
ratio-scale and normal (Pearson is more powerful in that case). Avoid it for
nominal categorical variables. If the two variables have a non-monotonic
relationship (e.g., U-shaped), Spearman's rho may not capture it well. Also, if
you have more than one independent variable or a predictive context, consider
regression instead.
## Assumptions
- **Ordinal or Continuous Data**: Variables are at least ordinal.
- **Monotonic Relationship**: The association between x and y should be
consistently increasing or decreasing (monotonic) even if not linear.
- **Independent Observations**: Each pair of values is independent of others
.
- **Similar Distribution Shape (for medians)**: To interpret differences in
central tendency (medians), the group distributions should have similar shape
.
- **Unpaired Groups**: Data should be unpaired (independent samples) if
comparing two groups.
## Alternatives
If data are continuous and meet Pearson's assumptions (linear relation,
normality), use **Pearson correlation**. For binary or nominal data, use
contingency-table tests. If you need to compare more than two independent groups
on a numeric outcome, use a rank-based test like Kruskal-Wallis instead.
## Interpretation
The `statistic` (rho) indicates rank correlation: +1 means perfect increasing
monotonic relationship, -1 perfect decreasing, and 0 no monotonic association.
The `p_value` tests the null hypothesis of no association in the population. A
small p-value suggests a statistically significant monotonic relationship. The
`n` is the number of paired observations. For example, rho = 0.65, p = 0.002, n =
30 indicates a strong positive monotonic correlation unlikely due to chance.
## Rejection Rules
If the p-value is not below the chosen alpha (e.g. p >= 0.05), do not reject the
null hypothesis; there's insufficient evidence of a monotonic association. If
the distributional assumption of similar shape is violated, be cautious in
interpreting rho as a median comparison. Also, if data are truly linear and
symmetric, Pearson's correlation might be preferred.
## Reporting Guidance
Report the Spearman rho and its p-value. For example: "Spearman's rho = 0.47, p
= 0.009, n = 25." Note that the interpretation is about ranked association. You
might say, "There was a moderate positive monotonic correlation between X and Y
(Spearman's rho = 0.47, p = 0.009)."
