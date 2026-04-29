---
id: choosing_categorical_categorical_test
title: Choosing a categorical-categorical test
function_name: null
specialist: bivariate
tags:
- decision-guide
  - categorical
---
## Purpose
Help choose the correct test for assessing association between two categorical
variables.
## Decision Rules
Use `chi_square_independence` when you have two categorical variables and most
expected cell counts are sufficiently large.
Use `fisher_exact_test` when sample size is small or expected counts in the
contingency table are below 5.
