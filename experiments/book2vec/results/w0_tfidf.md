## W0 TF-IDF

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 1.00 [1.00, 1.00] | 1.00 | 0.92 [0.88, 0.96] | 0.90 [0.84, 0.95] | 0.99 [0.98, 1.00] | 0.95 [0.92, 0.98] | 0.94 [0.88, 0.99] | 0.94 [0.89, 0.99] | 0.90 [0.80, 0.97] | 0.53 [0.50, 0.57] |
| W0_tfidf_clean | 1.00 [1.00, 1.00] | 1.00 | 0.93 [0.90, 0.96] | 0.92 [0.87, 0.96] | 0.99 [0.97, 1.00] | 0.95 [0.90, 0.99] | 0.98 [0.94, 1.00] | 0.96 [0.92, 0.99] | 0.90 [0.79, 0.98] | 0.54 [0.51, 0.58] |
| W0_tfidf_maskB_nostop | 1.00 [1.00, 1.00] | 1.00 | 0.92 [0.88, 0.96] | 0.90 [0.84, 0.95] | 0.99 [0.98, 1.00] | 0.95 [0.92, 0.98] | 0.94 [0.87, 0.99] | 0.94 [0.89, 0.99] | 0.90 [0.80, 0.97] | 0.53 [0.50, 0.57] |
| W0_tfidf_clean_nostop | 1.00 [1.00, 1.00] | 1.00 | 0.93 [0.90, 0.96] | 0.92 [0.87, 0.96] | 0.99 [0.97, 1.00] | 0.95 [0.90, 0.98] | 0.98 [0.93, 1.00] | 0.96 [0.92, 0.99] | 0.89 [0.79, 0.98] | 0.54 [0.51, 0.57] |
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.06 / 0.72 / 0.94 | 0.04 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 0.93 / 1.00 | 0.03 / 0.50 / 0.90 | 0.11 / 0.00 / 1.00 | 0.42 / 0.09 / 0.64 |
| W0_tfidf_clean | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.05 / 0.72 / 0.94 | 0.02 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 1.00 / 1.00 | 0.02 / 0.60 / 0.90 | 0.10 / 0.00 / 1.00 | 0.41 / 0.09 / 0.62 |
| W0_tfidf_maskB_nostop | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.06 / 0.72 / 0.94 | 0.04 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 0.93 / 1.00 | 0.03 / 0.50 / 0.90 | 0.11 / 0.00 / 1.00 | 0.42 / 0.09 / 0.64 |
| W0_tfidf_clean_nostop | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.05 / 0.72 / 0.94 | 0.02 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 1.00 / 1.00 | 0.02 / 0.60 / 0.90 | 0.10 / 0.00 / 1.00 | 0.41 / 0.09 / 0.62 |
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 87 | book bag | 0.93 | 0.90 | 0.07 (0.290) | 0.05 (0.565) | 0.01 | 0.03 (0.575) | 0.02 |
| W0_tfidf_clean | 87 | book bag | 0.93 | 0.96 | 0.08 (0.150) | 0.04 (0.635) | -0.00 | 0.04 (0.400) | 0.03 |
| W0_tfidf_maskB_nostop | 87 | book bag | 0.93 | 0.90 | 0.07 (0.270) | 0.05 (0.590) | 0.01 | 0.03 (0.575) | 0.02 |
| W0_tfidf_clean_nostop | 87 | book bag | 0.93 | 0.96 | 0.08 (0.180) | 0.04 (0.600) | -0.00 | 0.04 (0.425) | 0.03 |
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.130) | 0.03 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 0.37 / 0.02 | 0.32 / 0.12 | 31 / 56 | 0.79 / 0.78 | 2.58 | 0.08 | 34 (tolstoy_wp_maude) |
| W0_tfidf_clean | 0.37 / 0.02 | 0.33 / 0.12 | 31 / 56 | 0.78 / 0.78 | 2.76 | 0.06 | 35 (dickens_bleak) |
| W0_tfidf_maskB_nostop | 0.37 / 0.02 | 0.33 / 0.12 | 31 / 56 | 0.80 / 0.78 | 2.66 | 0.08 | 36 (tolstoy_wp_maude) |
| W0_tfidf_clean_nostop | 0.37 / 0.02 | 0.33 / 0.12 | 31 / 56 | 0.78 / 0.78 | 2.82 | 0.07 | 36 (dickens_bleak) |
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |

Spearman between the pair distances of two blocks, all pairs.

| block | W0_tfidf_maskB | W0_tfidf_clean | W0_tfidf_maskB_nostop | W0_tfidf_clean_nostop | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|
| W0_tfidf_maskB | 1.00 | 0.98 | 1.00 | 0.98 | 0.47 |
| W0_tfidf_clean | 0.98 | 1.00 | 0.98 | 1.00 | 0.46 |
| W0_tfidf_maskB_nostop | 1.00 | 0.98 | 1.00 | 0.98 | 0.47 |
| W0_tfidf_clean_nostop | 0.98 | 1.00 | 0.98 | 1.00 | 0.46 |
| P4_mfw500_tag3_rhythm | 0.47 | 0.46 | 0.47 | 0.46 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | W0_tfidf_maskB | W0_tfidf_clean | W0_tfidf_maskB_nostop | W0_tfidf_clean_nostop | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|
| W0_tfidf_maskB | 1.00 | 0.98 | 1.00 | 0.98 | 0.45 |
| W0_tfidf_clean | 0.98 | 1.00 | 0.98 | 1.00 | 0.43 |
| W0_tfidf_maskB_nostop | 1.00 | 0.98 | 1.00 | 0.98 | 0.45 |
| W0_tfidf_clean_nostop | 0.98 | 1.00 | 0.98 | 1.00 | 0.43 |
| P4_mfw500_tag3_rhythm | 0.45 | 0.43 | 0.45 | 0.43 | 1.00 |

