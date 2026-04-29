---
id: shapiro_wilk
title: Shapiro-Wilk test
function_name: shapiro_wilk
specialist: univariate
arg_schema:
- x
column_types:
  x: numeric
returns:
- statistic
- p_value
- n
alternatives:
- kolmogorov_smirnov
tags:
- univariate
  - normality
---
## Purpose
The Shapiro-Wilk test assesses whether a single numeric sample comes from a
normally distributed population. It answers: *Is the data significantly
different from a normal distribution?* It is commonly used before parametric
tests that assume normality, especially for small samples.
## When To Use
Use Shapiro-Wilk on one continuous numeric column. It is most effective for
small to moderate sample sizes (e.g. n < 50). A histogram or Q-Q plot can be
used to visualize normality, but Shapiro-Wilk gives a formal p-value. Make sure
the data do not have strong ties (exact same values), which is typically rare
for continuous data.
## Do Not Use When
Avoid using Shapiro-Wilk on extremely large datasets (e.g. n > 5000) because it
may be too sensitive (often rejects normality for tiny deviations). Do not
use it for categorical or ordinal data. If data clearly deviate from normal, a
normality test is unnecessary.
## Assumptions
- **Independence**: Observations are independent of each other.
- **Continuous Data**: The data should be continuous.
- **Range**: The test can be applied for any range of values, but works best
when n >= 3.
## Alternatives
Other normality tests include the Kolmogorov-Smirnov, Anderson-Darling, or
Lilliefors tests. Graphical methods like Q-Q plots are also useful. For very
small n, Shapiro-Wilk is usually preferred among normality tests.
## Interpretation
The null hypothesis is that the data are from a normal distribution. The
`statistic` W (close to 1) reflects normality. The `p_value` indicates
significance. A large p-value (e.g. >= 0.05) means you fail to reject normality
(data are consistent with normal), while a small p-value means you reject
normality. The `n` is the sample size. For example, W = 0.98, p = 0.65
suggests no evidence against normality; W = 0.90, p = 0.02 suggests significant
deviation from normality.
## Rejection Rules
If p < α, reject the null of normality and conclude the data are not normally
distributed. If p >= α, there is not enough evidence to say the data are non-
normal (assume normality). Note that with large n, even small departures from
normality can lead to p < α.
## Reporting Guidance
Report W and p. For example: "Shapiro-Wilk test of normality: W = 0.983, p =
0.47, indicating no significant departure from normality." If p is significant,
say "the data significantly deviate from normality, p = ...". Typically mention
the variable and sample size.
