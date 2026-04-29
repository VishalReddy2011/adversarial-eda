---
id: choosing_group_comparison_test
title: Choosing a group comparison test
function_name: null
specialist: bivariate
tags:
- decision-guide
  - group-comparison
---
## Purpose
Help choose the correct test for comparing a numeric outcome across groups.
## Decision Rules
Use `independent_t_test` for one numeric outcome across exactly two independent
groups when data are approximately normal.
Use `mann_whitney_u` for exactly two independent groups when a rank-based or
nonparametric comparison is more appropriate.
Use `one_way_anova` for one numeric outcome across three or more independent
groups when parametric assumptions are met.
Use `kruskal_wallis` for three or more independent groups when a rank-based or
nonparametric comparison is more appropriate.
