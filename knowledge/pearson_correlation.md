---
id: pearson_correlation
title: Pearson correlation
function_name: pearson_correlation
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
- spearman_correlation
- linear_regression
tags:
- association
- parametric
  - numeric-correlation
---
## Purpose
The Pearson correlation measures the strength and direction of the *linear*
relationship between two numeric variables. It answers: *How well do changes
in one continuous variable predict proportional changes in another?* A value of
+1 or -1 indicates a perfect linear relation (positive or negative
respectively), while 0 indicates no linear correlation.
## When To Use
Use Pearson's correlation when both variables are continuous (interval or ratio
scale) and the relationship is expected to be linear. For example, it applies to
two numerical columns like height vs. weight. Data should be roughly normally
distributed if you plan to do significance testing. Each observation must
include a paired value for each variable, and there should be at least two data
points .
## Do Not Use When
Do not use Pearson correlation for ordinal or categorical data. It is
inappropriate when the relationship is non-monotonic or clearly non-linear (e.g.
U-shaped). Avoid using it on datasets with severe outliers or highly skewed
distributions, since outliers can distort the linear correlation heavily. In
such cases consider Spearman's correlation or a different model.
## Assumptions
- **Linearity**: The relationship between x and y must be linear.
- **Interval/Ratio Data**: Both variables are measured on an interval or ratio
scale .
- **Normality**: Each variable is roughly normally distributed (for inference)
.
- **Paired
Observations**: Each observation provides one x value and one y value (no
missing pairs).
- **No Extreme Outliers**: There are no extreme outliers that would unduly
influence the slope (outliers can drastically change the correlation).
## Alternatives
If data are not normally distributed or variables are ordinal, use **Spearman
correlation** (rank-based, monotonic association) instead. If you want to
model or predict Y from X, a **linear regression** may be more appropriate. For
non-linear but monotonic relationships, Spearman is preferred.
## Interpretation
The `statistic` (typically denoted r) ranges from -1 to 1. A positive r means a
positive linear relationship; a negative r means a negative linear relationship.
An absolute value near 1 indicates a strong linear association. The `p_value`
tests the null hypothesis that the true correlation is zero. A small p-value
(e.g. < 0.05) suggests a statistically significant linear association. The
sample size `n` is the number of paired observations. For example, r = 0.8 with
p = 0.01 and n = 50 would indicate a strong positive correlation that is
unlikely to be due to chance.
## Rejection Rules
Reject or question the result if assumptions are violated: for instance, if
scatter plots show a non-linear pattern or outliers, then Pearson's correlation
may not be valid. If the p-value is not below the significance threshold (e.g.,
p >= 0.05), do not reject the null; this indicates insufficient evidence of a
linear relationship. Also, if the estimated correlation is very close to 0, it
suggests no meaningful linear association.
## Reporting Guidance
When reporting, include the correlation coefficient and p-value. For example:
"Pearson's r(48) = 0.52, p = 0.003, indicating a moderate positive linear
relationship between X and Y." Emphasize the magnitude and direction of
association. Mention that r^2 (the square of the correlation) is the proportion
of variance in one variable explained by the other, if needed for context.
