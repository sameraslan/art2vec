## All blocks on the 24-book reader subset

AUC that a labelled pair is closer than a negative pair (263 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=26) |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 [0.99, 1.00] | 1.00 | 0.96 [0.89, 1.00] | 1.00 | 1.00 | 0.93 [0.84, 1.00] | 1.00 [0.99, 1.00] | 1.00 | 0.70 [0.60, 0.80] |
| T3_scalars_dtw20_sd | 1.00 [1.00, 1.00] | 1.00 | 0.76 [0.55, 0.93] | 0.37 | 0.96 | 0.82 [0.68, 0.95] | 0.64 [0.33, 0.91] | 0.99 | 0.65 [0.55, 0.75] |
| W1_qwen_maskB_c | 1.00 [1.00, 1.00] | 1.00 | 0.90 [0.84, 0.96] | 1.00 | 0.93 | 0.86 [0.79, 0.91] | 1.00 [1.00, 1.00] | 1.00 | 0.87 [0.82, 0.92] |
| W0_tfidf_maskB | 1.00 [1.00, 1.00] | 1.00 | 1.00 [1.00, 1.00] | 0.99 | 1.00 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 | 0.60 [0.50, 0.70] |
| W_digest_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 1.00] | 1.00 | 0.93 | 1.00 [0.99, 1.00] | 0.90 [0.69, 1.00] | 0.99 | 0.59 [0.48, 0.70] |
| S_story_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 1.00 | 0.99 | 0.97 [0.95, 0.98] | 0.98 [0.95, 1.00] | 1.00 | 0.82 [0.74, 0.89] |
| S_storychar_plain | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 0.99 | 0.99 [0.98, 0.99] | 0.99 [0.98, 1.00] | 1.00 | 0.82 [0.75, 0.88] |
| S_story_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.97, 1.00] | 1.00 | 0.57 [0.45, 0.69] |
| F_reader | 0.99 [0.99, 1.00] | 1.00 | 0.98 [0.94, 1.00] | 0.90 | 0.99 | 1.00 [1.00, 1.00] | 0.99 [0.98, 1.00] | 1.00 | 0.73 [0.62, 0.82] |
| F_proj_plain | 0.70 [0.15, 1.00] | 1.00 | 0.71 [0.52, 0.90] | 0.95 | 0.73 | 0.63 [0.35, 0.92] | 0.84 [0.68, 0.95] | 0.92 | 0.73 [0.65, 0.81] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=26) |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.50 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.50 / 1.00 | 0.08 / 0.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.32 / 0.12 / 0.88 |
| T3_scalars_dtw20_sd | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.28 / 0.00 / 0.67 | 0.48 / 0.00 / 0.50 | 0.11 / 0.00 / 1.00 | 0.27 / 0.00 / 0.50 | 0.36 / 0.00 / 0.33 | 0.05 / 0.50 / 1.00 | 0.28 / 0.41 / 0.82 |
| W1_qwen_maskB_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.17 / 1.00 | 0.02 / 0.50 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.17 / 0.24 / 0.82 |
| W0_tfidf_maskB | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.35 / 0.06 / 0.94 |
| W_digest_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.11 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.43 / 0.12 / 0.59 |
| S_story_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.24 / 0.82 |
| S_storychar_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.24 / 0.94 |
| S_story_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.41 / 0.24 / 0.65 |
| F_reader | 0.04 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.67 / 0.83 | 0.16 / 0.00 / 0.50 | 0.09 / 0.00 / 1.00 | 0.02 / 1.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.31 / 0.18 / 0.82 |
| F_proj_plain | 0.22 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.20 / 0.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.23 / 0.00 / 0.50 | 0.23 / 0.00 / 1.00 | 0.15 / 0.50 / 0.67 | 0.07 / 0.50 / 1.00 | 0.28 / 0.18 / 0.82 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 24 | ordered text | 0.88 | 0.77 | 0.32 (0.005) | 0.37 (0.005) | 0.34 | 0.06 (0.475) | 0.02 |
| T3_scalars_dtw20_sd | 24 | ordered text | 0.71 |  | 0.09 (0.300) | 0.14 (0.280) | 0.13 | 0.06 (0.505) | 0.02 |
| W1_qwen_maskB_c | 24 | ordered text | 0.94 | 0.88 | 0.17 (0.015) | 0.08 (0.340) | 0.03 | -0.04 (0.585) | -0.09 |
| W0_tfidf_maskB | 24 | book bag | 0.81 | 0.85 | 0.05 (0.640) | 0.09 (0.555) | 0.04 | 0.40 (0.010) | 0.39 |
| W_digest_plain | 24 | ordered text |  |  | 0.15 (0.010) | 0.07 (0.340) | 0.02 | -0.01 (0.790) | -0.07 |
| S_story_plain | 24 | ordered text |  |  | 0.09 (0.070) | -0.09 (0.245) | -0.15 | 0.01 (0.855) | -0.04 |
| S_storychar_plain | 24 | ordered text |  |  | 0.09 (0.080) | -0.07 (0.345) | -0.13 | 0.02 (0.725) | -0.03 |
| S_story_tfidf | 24 | ordered text |  |  | 0.14 (0.105) | 0.06 (0.645) | 0.00 | 0.12 (0.170) | 0.08 |
| F_reader | 24 | ordered text |  |  | 0.01 (0.835) | -0.03 (0.690) | -0.08 | -0.04 (0.305) | -0.10 |
| F_proj_plain | 24 | ordered text | 0.65 | 0.48 | 0.09 (0.225) | 0.02 (0.860) | -0.02 | -0.04 (0.645) | -0.06 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.29 / 0.06 | 0.43 / 0.15 | 22 / 33 | 0.41 / 0.42 | 0.85 | 0.00 | 12 (wells_worlds) |
| T3_scalars_dtw20_sd | 0.19 / 0.06 | 0.39 / 0.15 | 30 / 33 | 0.44 / 0.42 | 0.54 | 0.00 | 12 (merriman_barlasch) |
| W1_qwen_maskB_c | 0.29 / 0.06 | 0.54 / 0.15 | 24 / 33 | 0.41 / 0.42 | 0.80 | 0.00 | 9 (wells_worlds) |
| W0_tfidf_maskB | 0.29 / 0.06 | 0.38 / 0.15 | 25 / 33 | 0.33 / 0.42 | 0.87 | 0.12 | 16 (conrad_agent) |
| W_digest_plain | 0.27 / 0.06 | 0.31 / 0.15 | 24 / 33 | 0.37 / 0.42 | -0.18 | 0.00 | 8 (wells_worlds) |
| S_story_plain | 0.29 / 0.06 | 0.53 / 0.15 | 28 / 33 | 0.39 / 0.42 | -0.55 | 0.00 | 7 (wharton_frome) |
| S_storychar_plain | 0.29 / 0.06 | 0.50 / 0.15 | 25 / 33 | 0.36 / 0.42 | 0.06 | 0.00 | 8 (merriman_barlasch) |
| S_story_tfidf | 0.29 / 0.06 | 0.34 / 0.15 | 26 / 33 | 0.38 / 0.42 | 0.69 | 0.00 | 12 (fathers_garnett) |
| F_reader | 0.28 / 0.06 | 0.39 / 0.15 | 28 / 33 | 0.45 / 0.42 | 0.14 | 0.00 | 8 (zamyatin_we) |
| F_proj_plain | 0.21 / 0.06 | 0.43 / 0.15 | 31 / 33 | 0.42 / 0.42 | -0.21 | 0.00 | 8 (wharton_frome) |

Spearman between the pair distances of two blocks, all pairs.

| block | P4_mfw500_tag3_rhythm | T3_scalars_dtw20_sd | W1_qwen_maskB_c | W0_tfidf_maskB | W_digest_plain | S_story_plain | S_storychar_plain | S_story_tfidf | F_reader | F_proj_plain |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.39 | 0.56 | 0.54 | 0.28 | 0.35 | 0.31 | 0.26 | 0.25 | 0.26 |
| T3_scalars_dtw20_sd | 0.39 | 1.00 | 0.22 | 0.20 | 0.14 | 0.29 | 0.29 | 0.24 | 0.18 | 0.13 |
| W1_qwen_maskB_c | 0.56 | 0.22 | 1.00 | 0.40 | 0.43 | 0.59 | 0.56 | 0.27 | 0.50 | 0.54 |
| W0_tfidf_maskB | 0.54 | 0.20 | 0.40 | 1.00 | 0.25 | 0.31 | 0.30 | 0.38 | 0.27 | 0.17 |
| W_digest_plain | 0.28 | 0.14 | 0.43 | 0.25 | 1.00 | 0.37 | 0.35 | 0.32 | 0.27 | 0.21 |
| S_story_plain | 0.35 | 0.29 | 0.59 | 0.31 | 0.37 | 1.00 | 0.87 | 0.44 | 0.36 | 0.40 |
| S_storychar_plain | 0.31 | 0.29 | 0.56 | 0.30 | 0.35 | 0.87 | 1.00 | 0.40 | 0.46 | 0.38 |
| S_story_tfidf | 0.26 | 0.24 | 0.27 | 0.38 | 0.32 | 0.44 | 0.40 | 1.00 | 0.18 | 0.15 |
| F_reader | 0.25 | 0.18 | 0.50 | 0.27 | 0.27 | 0.36 | 0.46 | 0.18 | 1.00 | 0.41 |
| F_proj_plain | 0.26 | 0.13 | 0.54 | 0.17 | 0.21 | 0.40 | 0.38 | 0.15 | 0.41 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P4_mfw500_tag3_rhythm | T3_scalars_dtw20_sd | W1_qwen_maskB_c | W0_tfidf_maskB | W_digest_plain | S_story_plain | S_storychar_plain | S_story_tfidf | F_reader | F_proj_plain |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.34 | 0.50 | 0.48 | 0.18 | 0.25 | 0.21 | 0.15 | 0.15 | 0.21 |
| T3_scalars_dtw20_sd | 0.34 | 1.00 | 0.15 | 0.13 | 0.06 | 0.23 | 0.23 | 0.17 | 0.10 | 0.09 |
| W1_qwen_maskB_c | 0.50 | 0.15 | 1.00 | 0.31 | 0.36 | 0.54 | 0.49 | 0.17 | 0.43 | 0.52 |
| W0_tfidf_maskB | 0.48 | 0.13 | 0.31 | 1.00 | 0.14 | 0.21 | 0.20 | 0.28 | 0.16 | 0.10 |
| W_digest_plain | 0.18 | 0.06 | 0.36 | 0.14 | 1.00 | 0.29 | 0.26 | 0.22 | 0.17 | 0.16 |
| S_story_plain | 0.25 | 0.23 | 0.54 | 0.21 | 0.29 | 1.00 | 0.84 | 0.35 | 0.27 | 0.36 |
| S_storychar_plain | 0.21 | 0.23 | 0.49 | 0.20 | 0.26 | 0.84 | 1.00 | 0.31 | 0.37 | 0.34 |
| S_story_tfidf | 0.15 | 0.17 | 0.17 | 0.28 | 0.22 | 0.35 | 0.31 | 1.00 | 0.06 | 0.08 |
| F_reader | 0.15 | 0.10 | 0.43 | 0.16 | 0.17 | 0.27 | 0.37 | 0.06 | 1.00 | 0.37 |
| F_proj_plain | 0.21 | 0.09 | 0.52 | 0.10 | 0.16 | 0.36 | 0.34 | 0.08 | 0.37 | 1.00 |


Every labelled pair: rank of b from a / rank of a from b (1 = nearest), and in brackets the share of negative pairs that are farther apart.

| set | pair | P4_mfw500_tag3_rhythm | T3_scalars_dtw20_sd | W1_qwen_maskB_c | W0_tfidf_maskB | W_digest_plain | S_story_plain | S_storychar_plain | S_story_tfidf | F_reader | F_proj_plain |
|---|---|---|---|---|---|---|---|---|---|---|---|
| translation_pair | fathers_garnett ~ fathers_hogarth | 3 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 3 (0.99) | 18 / 13 (0.15) |
| translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 2 (1.00) | 1 / 1 (0.97) |
| translation_pair | journey_1871 ~ journey_malleson | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) |
| edition_pair | frankenstein_1818 ~ frankenstein_1831 | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| retelling | burnett_princess ~ burnett_sara_crewe | 1 / 1 (1.00) | 3 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 4 / 1 (0.92) |
| series | holmes_hound ~ holmes_study | 1 / 1 (1.00) | 10 / 19 (0.33) | 1 / 1 (1.00) | 1 / 1 (1.00) | 10 / 6 (0.69) | 1 / 3 (0.98) | 2 / 3 (0.98) | 2 / 3 (0.97) | 3 / 1 (0.98) | 1 / 1 (0.95) |
| series | oz_land ~ oz_wizard | 1 / 1 (0.99) | 3 / 4 (0.91) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 3 (0.90) |
| series | tarzan_apes ~ tarzan_return | 1 / 1 (1.00) | 9 / 8 (0.68) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.95) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 11 / 9 (0.68) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_garnett | 1 / 2 (1.00) | 3 / 4 (0.96) | 2 / 2 (0.93) | 2 / 2 (1.00) | 3 / 3 (0.93) | 2 / 3 (0.99) | 2 / 2 (0.99) | 2 / 2 (1.00) | 3 / 3 (0.99) | 10 / 2 (0.73) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_ralston | 2 / 2 (1.00) | 7 / 8 (0.83) | 3 / 2 (0.89) | 3 / 2 (1.00) | 2 / 3 (0.99) | 3 / 2 (0.98) | 3 / 2 (0.99) | 3 / 4 (0.97) | 1 / 1 (1.00) | 3 / 2 (0.92) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_garnett | 4 / 3 (0.84) | 2 / 5 (0.95) | 2 / 3 (0.91) | 3 / 3 (1.00) | 2 / 2 (1.00) | 3 / 4 (0.95) | 2 / 3 (0.98) | 2 / 3 (0.99) | 1 / 1 (1.00) | 3 / 4 (0.62) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_ralston | 2 / 3 (0.94) | 7 / 12 (0.68) | 3 / 4 (0.79) | 2 / 3 (1.00) | 3 / 2 (1.00) | 2 / 3 (0.98) | 3 / 3 (0.98) | 3 / 3 (0.98) | 2 / 3 (1.00) | 12 / 13 (0.35) |
| same_author_unrelated | wells_time ~ wells_worlds | 1 / 1 (1.00) | 4 / 19 (0.37) | 2 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.98) | 1 / 1 (0.98) | 3 / 6 (0.90) | 2 / 2 (0.95) |
