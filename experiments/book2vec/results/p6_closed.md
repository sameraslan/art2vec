## P6 closed-class control

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |
| P1_mfw500_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.94, 0.99] | 0.95 [0.90, 0.99] | 0.68 [0.65, 0.72] |
| P6_closed_nopron | 0.99 [0.97, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.98 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.93 [0.87, 0.98] | 1.00 [1.00, 1.00] | 0.90 [0.83, 0.96] | 0.99 [0.98, 1.00] | 0.63 [0.59, 0.66] |
| P6_closed_pron | 1.00 [0.99, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.95 [0.92, 0.98] | 1.00 [1.00, 1.00] | 0.92 [0.86, 0.97] | 0.98 [0.96, 1.00] | 0.65 [0.61, 0.69] |
| P6_pron_only | 1.00 [1.00, 1.00] | 1.00 | 0.87 [0.82, 0.91] | 0.85 [0.79, 0.91] | 0.90 [0.81, 0.99] | 0.88 [0.83, 0.93] | 0.92 [0.84, 0.98] | 0.84 [0.75, 0.92] | 0.75 [0.56, 0.89] | 0.65 [0.61, 0.68] |

AUC difference from `P1_mfw500_all_noprop_nocull` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | +0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.01, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [-0.00, +0.01] | -0.00 [-0.00, +0.00] | -0.24 [-0.47, -0.02] | -0.01 [-0.02, +0.00] | -0.07 [-0.10, -0.05] |
| P6_closed_nopron | -0.01 [-0.03, -0.00] |  | -0.02 [-0.03, -0.01] | -0.01 [-0.02, -0.00] | -0.00 [-0.00, +0.00] | -0.05 [-0.09, -0.01] | +0.00 [+0.00, +0.00] | -0.07 [-0.14, -0.03] | +0.03 [+0.01, +0.08] | -0.06 [-0.07, -0.04] |
| P6_closed_pron | -0.00 [-0.01, -0.00] |  | -0.01 [-0.02, -0.00] | -0.01 [-0.01, +0.00] | +0.00 [-0.00, +0.00] | -0.03 [-0.04, -0.01] | +0.00 [+0.00, +0.00] | -0.05 [-0.10, -0.02] | +0.03 [+0.01, +0.06] | -0.03 [-0.05, -0.02] |
| P6_pron_only | +0.00 [+0.00, +0.00] |  | -0.12 [-0.17, -0.08] | -0.14 [-0.20, -0.08] | -0.10 [-0.19, -0.01] | -0.10 [-0.16, -0.04] | -0.08 [-0.16, -0.02] | -0.13 [-0.22, -0.04] | -0.21 [-0.36, -0.08] | -0.03 [-0.07, +0.01] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |
| P1_mfw500_all_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 1.00 | 0.01 / 0.81 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.07 / 0.00 / 1.00 | 0.33 / 0.19 / 0.79 |
| P6_closed_nopron | 0.01 / 0.82 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.69 / 0.94 | 0.02 / 0.81 / 0.94 | 0.01 / 0.71 / 1.00 | 0.07 / 0.12 / 0.81 | 0.00 / 0.86 / 1.00 | 0.13 / 0.20 / 0.50 | 0.04 / 0.17 / 1.00 | 0.38 / 0.08 / 0.62 |
| P6_closed_pron | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.67 / 0.94 | 0.02 / 0.78 / 0.91 | 0.01 / 0.86 / 1.00 | 0.06 / 0.06 / 0.88 | 0.00 / 1.00 / 1.00 | 0.09 / 0.20 / 0.70 | 0.05 / 0.17 / 1.00 | 0.36 / 0.11 / 0.68 |
| P6_pron_only | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.13 / 0.48 / 0.62 | 0.14 / 0.56 / 0.66 | 0.10 / 0.29 / 0.71 | 0.11 / 0.19 / 0.50 | 0.07 / 0.43 / 0.50 | 0.13 / 0.10 / 0.50 | 0.26 / 0.00 / 0.83 | 0.36 / 0.19 / 0.72 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.180) | 0.03 |
| P1_mfw500_all_noprop_nocull | 87 | ordered text | 0.97 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.005) | 0.04 |
| P6_closed_nopron | 87 | book bag | 0.93 | 0.88 | 0.17 (0.005) | 0.23 (0.005) | 0.20 | 0.06 (0.005) | 0.05 |
| P6_closed_pron | 87 | book bag | 0.95 | 0.89 | 0.18 (0.005) | 0.22 (0.005) | 0.19 | 0.05 (0.020) | 0.04 |
| P6_pron_only | 87 | book bag | 0.68 | 0.52 | 0.11 (0.005) | 0.06 (0.025) | 0.03 | 0.02 (0.175) | 0.01 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |
| P1_mfw500_all_noprop_nocull | 0.41 / 0.02 | 0.47 / 0.12 | 32 / 56 | 0.63 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P6_closed_nopron | 0.38 / 0.02 | 0.36 / 0.12 | 33 / 56 | 0.66 / 0.78 | 0.20 | 0.06 | 12 (sinclair_olivier) |
| P6_closed_pron | 0.38 / 0.02 | 0.39 / 0.12 | 33 / 56 | 0.68 / 0.78 | 0.13 | 0.06 | 13 (sinclair_olivier) |
| P6_pron_only | 0.24 / 0.02 | 0.27 / 0.12 | 37 / 56 | 0.73 / 0.78 | 0.41 | 0.00 | 11 (gentlefolk_garnett) |

Spearman between the pair distances of two blocks, all pairs.

| block | P4_mfw500_tag3_rhythm | P1_mfw500_all_noprop_nocull | P6_closed_nopron | P6_closed_pron | P6_pron_only |
|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.74 | 0.67 | 0.69 | 0.39 |
| P1_mfw500_all_noprop_nocull | 0.74 | 1.00 | 0.86 | 0.88 | 0.46 |
| P6_closed_nopron | 0.67 | 0.86 | 1.00 | 0.95 | 0.32 |
| P6_closed_pron | 0.69 | 0.88 | 0.95 | 1.00 | 0.57 |
| P6_pron_only | 0.39 | 0.46 | 0.32 | 0.57 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P4_mfw500_tag3_rhythm | P1_mfw500_all_noprop_nocull | P6_closed_nopron | P6_closed_pron | P6_pron_only |
|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.72 | 0.66 | 0.67 | 0.36 |
| P1_mfw500_all_noprop_nocull | 0.72 | 1.00 | 0.85 | 0.87 | 0.43 |
| P6_closed_nopron | 0.66 | 0.85 | 1.00 | 0.95 | 0.30 |
| P6_closed_pron | 0.67 | 0.87 | 0.95 | 1.00 | 0.55 |
| P6_pron_only | 0.36 | 0.43 | 0.30 | 0.55 | 1.00 |

