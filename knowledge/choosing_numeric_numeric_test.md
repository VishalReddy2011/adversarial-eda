---
id: choosing_numeric_numeric_test
title: Choosing a numeric-numeric test
function_name: null
specialist: bivariate
tags:
- decision-guide
  - correlation-regression
---
## Purpose
Help choose the correct test for analyzing relationships between two numeric
variables.
## Decision Rules
Use `pearson_correlation` when both variables are continuous and assumptions of
linearity and normality are reasonable.
Use `spearman_correlation` when variables are ordinal or when the relationship
is monotonic but not necessarily linear.
Use `linear_regression` when you want to predict one numeric outcome from
another and quantify the linear slope between them.
