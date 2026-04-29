---
id: linear_regression
title: Linear regression
function_name: linear_regression
specialist: regression
arg_schema:
- x
- y
column_types:
  x: numeric
  y: numeric
returns:
- intercept
- slope
- r_squared
- p_value
- n
alternatives:
- pearson_correlation
- spearman_correlation
tags:
- regression
  - association
---
## Purpose
Linear regression models the relationship between a numeric predictor (x) and a
numeric outcome (y) by fitting a straight line. It answers: *How much does Y
change for a unit change in X, and is this relationship statistically
significant?* For example, predicting weight (y) from height (x).
## When To Use
Use when both variables are continuous and you want to predict or explain one
from the other. The relationship should be approximately linear. For instance, a
simple linear regression fits Y = β₀ + β₁X. Requires at least two data points.
Often used when one variable is considered independent and the other dependent,
although roles can be interchangeable for association.
## Do Not Use When
Do not use linear regression if the outcome is categorical (use logistic
regression). Avoid it when the relationship is non-linear (consider
transformations or non-linear models). It is also sensitive to outliers; if
extreme values exist, they can strongly affect the fit. If data are
heteroscedastic (variance changes with X), consider weighted or robust
regression.
## Assumptions
- **Linearity**: The relationship between X and Y is linear.
- **Normality of Residuals**: The errors (differences between observed and
fitted values) are normally distributed.
- **Homoscedasticity**: The variance of residuals is constant across all levels
of X .
- **Independence**: Observations are independent of each other.
- **No Multicollinearity**: (For simple regression with one predictor, not
applicable; for multiple regression, predictors should not be highly correlated
with each other.)
## Alternatives
For association only, **Pearson correlation** gives the strength of linear
relationship without fitting an intercept. For ordinal or non-normal data,
consider **Spearman correlation**. For non-linear relations, use polynomial or
generalized additive models. If Y is categorical, use logistic regression.
## Interpretation
The output includes an intercept and slope (regression coefficients), R^2, and p-
value for the slope. The `slope` (β₁) indicates the estimated change in Y for a
one-unit increase in X. The `intercept` (β₀) is the estimated Y when X = 0. R^2
indicates the proportion of variance in Y explained by X. A small `p_value` for
the slope suggests the linear relationship is statistically significant. For
example, slope = 2.5 (p=0.01) with R^2 = 0.45 means each unit increase in X is
associated with 2.5-unit increase in Y, and 45% of variance in Y is explained by
X.
## Rejection Rules
If the p-value for the slope >= α, we fail to reject the null hypothesis that the
slope is zero (no linear effect). If assumptions (especially linearity,
normality of errors) are violated, the inference may not be valid. In such
cases, results should be interpreted with caution or a different model chosen.
## Reporting Guidance
Report the regression equation or slope with its confidence interval and p-
value, and R^2. For example: "Linear regression showed that for each additional
unit of X, Y increases by β̂ = 2.5 (95% CI: 1.0–4.0, p = 0.01). The model
explains 45% of variance (R^2 = 0.45)." Indicate the direction and strength of
the association and whether it is significant.
