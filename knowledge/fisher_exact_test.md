---
id: fisher_exact_test
title: Fisher's exact test
function_name: fisher_exact_test
specialist: bivariate
arg_schema:
- x
- y
column_types:
  x: categorical
  y: categorical
returns:
- p_value
- n
alternatives:
- chi_square_independence
tags:
- association
  - categorical
---
## Purpose
Fisher's exact test evaluates the association between two categorical variables,
typically in a 2×2 table. It answers: *Is there a statistically significant
relationship between the row and column variables?* It is often used instead of
Chi-square when sample sizes are small.
## When To Use
Use when you have two categorical variables (usually binary, forming a 2×2
table) and the sample size is small or expected counts are low. It computes the
exact probability of observing the data assuming independence, so it's valid
even with small or unequal marginal totals.
## Do Not Use When
For large samples and all expected counts sufficiently high, Fisher's exact test
is unnecessary (Chi-square is simpler). Also, it can be computationally
intensive for large tables beyond 2×2, so alternatives or approximations are
preferred if the table is large.
## Assumptions
- **Categorical Data**: Both variables are categorical (often binary).
- **Fixed Margins**: It conditions on the row and column totals.
- **Independence**: Observations are independent, and each subject is counted
once.
- **Sample
Size**: Can be used for any size, but it is most beneficial for small samples
.
## Alternatives
The Chi-square test is an alternative for larger samples. For larger
contingency tables, Fisher's test generalizes (but is seldom used beyond 2×2 due
to complexity).
## Interpretation
Fisher's test reports an exact p-value (no test statistic). A small p-value
indicates that the observed table is unlikely under independence. For example, p
= 0.047 would lead to rejecting independence. The `n` is the total sample size.
## Rejection Rules
If p >= α, do not reject the null: conclude no significant association. If p < α,
reject null: conclude a significant association exists between the variables.
## Reporting Guidance
Report the p-value from Fisher's test. For example: "Fisher's exact test
indicated a significant association between Group and Outcome (p = 0.047)."
Mention the sample size and, if possible, the contingency table counts or
proportions. For clarity, you can also report an odds ratio or risk ratio as a
measure of effect size.
