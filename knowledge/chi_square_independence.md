---
id: chi_square_independence
title: Chi-square test of independence
function_name: chi_square_independence
specialist: bivariate
arg_schema:
- x
- y
column_types:
  x: categorical
  y: categorical
returns:
- statistic
- p_value
- n
alternatives:
- fisher_exact_test
tags:
- association
  - categorical
---
## Purpose
The Chi-square test of independence assesses whether two categorical variables
are associated or independent. It answers: *Is the distribution of one
categorical variable different across the levels of another?* For example,
testing whether gender is related to a voting preference.
## When To Use
Use when you have two categorical variables and a contingency table of counts.
Observations should be independent (each case contributes to one cell).
Typically, each variable has two or more categories. A sample size large enough
that expected counts in cells are reasonably high (>=5) is required.
## Do Not Use When
Do not use Chi-square if any cell has a very low expected count (especially <5)
, or if your data are paired. In those cases, use Fisher's exact test (for
2×2 or small tables) or McNemar's test (for paired binary data).
## Assumptions
- **Categorical Data**: Both variables are categorical (nominal or ordinal)
.
- **Independence**: Each observation is independent; no individual appears in
more than one cell.
- **Mutually Exclusive Cells**: Each case falls into exactly one cell of the
table .
- **Expected Count**: Generally, expected frequency >= 5 in at least 80% of
cells, and no cell with expected <1.
## Alternatives
If the expected counts are small (<5), use **Fisher's exact test** instead
. For ordinal associations, consider measures like the Mantel-Haenszel test.
For two related samples on two categories, use McNemar's test.
## Interpretation
The output includes a Chi-square statistic (χ^2) and p-value. A small p-value
indicates evidence of association (not independent) between the variables. The
`n` is the total sample size. Degrees of freedom are (rows–1)*(columns–1). For
example, χ^2(2) = 5.67, p = 0.058. If p < α, reject the null hypothesis of
independence.
## Rejection Rules
If p >= α, do not reject the null: conclude no significant association (variables
appear independent). If p < α, reject the null: evidence suggests the
categorical variables are associated. Beware of violating assumptions
(especially low expected counts); if assumptions fail, prefer Fisher's exact
test.
## Reporting Guidance
Report χ^2, df, and p. For example: "Chi-square test showed no significant
association between Treatment and Outcome, χ^2(1) = 0.34, p = 0.56." If
significant, you can say "There was a significant association." Always mention
sample size and that counts (or percentages) were used.
