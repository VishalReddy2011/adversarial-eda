---
id: choosing_statistical_test_for_eda
title: Choosing a statistical test for EDA
function_name: null
specialist: null
tags:
- decision-guide
  - eda
---
## Purpose
Explain how to choose a statistical test based on the column types available in
a dataset.
## Decision Rules
For numeric + numeric columns, consider `pearson_correlation`,
`spearman_correlation`, or `linear_regression`.
For numeric + categorical columns, consider `independent_t_test` or
`one_way_anova` (parametric comparisons) or `mann_whitney_u` or
`kruskal_wallis` (nonparametric) .
For categorical + categorical columns, consider `chi_square_independence` (for
larger samples) or `fisher_exact_test` (when samples are small).
For a single numeric column, consider `shapiro_wilk` to test for normality.
Sources: We referenced standard statistical guides and tutorials for each test (e.g., Statology, Laerd
Statistics, Biology Statistics Prime, and others) to ensure accurate descriptions of purposes, assumptions,
and usage rules . Each Decision Rules and test description above summarizes these
authoritative references.
The Five Assumptions for Pearson Correlation
https://www.statology.org/pearson-correlation-assumptions/
Spearman's rank correlation coefficient - Wikipedia
https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient
GraphPad Prism 11 Statistics Guide - Mann-Whitney test
https://www.graphpad.com/guides/prism/latest/statistics/stat_checklist_mannwhitney.htm
Independent T-Test - An introduction to when to use this test and what are the
variables required | Laerd Statistics
https://statistics.laerd.com/statistical-guides/independent-t-test-statistical-guide.php
One-way ANOVA - An introduction to when you should run this test and the test hypothesis | Laerd
Statistics
https://statistics.laerd.com/statistical-guides/one-way-anova-statistical-guide.php
One-way ANOVA - Its preference to multiple t-tests and the assumptions needed to run this test |
Laerd Statistics
https://statistics.laerd.com/statistical-guides/one-way-anova-statistical-guide-2.php
One-way ANOVA - Violations to the assumptions of this test and how to report the results | Laerd
Statistics
https://statistics.laerd.com/statistical-guides/one-way-anova-statistical-guide-3.php
Kruskal-Wallis H Test in SPSS Statistics | Procedure, output and interpretation of the
output using a relevant example.
https://statistics.laerd.com/spss-tutorials/kruskal-wallis-h-test-using-spss-statistics.php
The Four Assumptions of a Chi-Square Test
https://www.statology.org/chi-square-test-assumptions/
Chi-Square and Fisher's Exact Test | Easy Guide
https://www.biostatprime.com/chi-square-and-fisher-exact-test
Fisher's Exact Test: Using & Interpreting - Statistics By Jim
https://statisticsbyjim.com/hypothesis-testing/fishers-exact-test/
Understanding the Assumptions of Linear Regression Analysis
https://www.statisticssolutions.com/free-resources/directory-of-statistical-analyses/assumptions-of-linear-regression/
An Introduction to the Shapiro-Wilk Test for Normality | Built In
https://builtin.com/data-science/shapiro-wilk-test
