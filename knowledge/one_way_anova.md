---
id: one_way_anova
title: One-way ANOVA
function_name: one_way_anova
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
- kruskal_wallis
tags:
- group-comparison
- parametric
  - multiple-groups
---
## Purpose
One-way ANOVA tests whether the means of a numeric outcome differ across three
or more independent groups. It answers:
*Is there a statistically significant difference among group means?* It is an
extension of the t-test to multiple groups. For example, it can test if average
exam scores differ among students with low, medium, and high study habits.
## When To Use
Use ANOVA when you have one numeric dependent variable and one categorical
independent variable with three or more independent groups. Each subject is
in one group only. The dependent variable should be continuous. You need at
least two observations per group, though more is better.
## Do Not Use When
If you only have two groups, use a t-test instead. Do not use one-way ANOVA if
the groups are not independent (use repeated-measures ANOVA). If the outcome is
non-normal or variances are unequal (and especially with unbalanced samples),
consider a nonparametric test (Kruskal-Wallis).
## Assumptions
-
**Normality**: The outcome is approximately normally distributed in each group
(or residuals are normal).
- **Equal Variances**: Population variances are equal across groups
(homoscedasticity).
-
**Independence**: Observations within and across groups are independent (study
design must ensure this).
- **Group Size**: At least 2 per group; in practice, larger samples improve
robustness.
## Alternatives
If normality is violated, ANOVA is fairly robust, but for severely non-normal
data use **Kruskal-Wallis H test**. If variances are unequal, use Welch's
ANOVA or the Brown-Forsythe test. For pairwise group comparisons after a
significant ANOVA, use post-hoc tests (e.g., Tukey HSD).
## Interpretation
ANOVA yields an F statistic and p-value. A significant result (p < α) means at
least two group means differ (omnibus test). It does not tell which groups
differ. The sample size `n` is the total across all groups. Report
F( df_between, df_within ) = X, p = Y. For example, F(2, 27) = 4.47, p = 0.021
would indicate a significant effect of group on the outcome. You should then
conduct post-hoc comparisons to identify specific differences.
## Rejection Rules
If p >= α, conclude no statistically significant difference between any group
means. If p < α, reject the null that all group means are equal. If assumptions
of normality or equal variances are clearly violated, the ANOVA result may be
unreliable; in such cases use a nonparametric test.
## Reporting Guidance
Report the F statistic, degrees of freedom, and p-value. For example: "A one-way
ANOVA revealed a significant effect of condition on score, F(3, 116) = 5.12, p =
0.002." Also report group means and standard deviations and mention the
direction: e.g., which group had higher/lower means. If significant, state that
at least one group differs and usually follow up with post-hoc analysis.
