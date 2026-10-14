## From-text against title-only blocks, 23 books

AUC that a labelled pair is closer than a negative pair (240 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=24) |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 1.00 | 0.99 | 0.97 [0.96, 0.99] | 0.98 [0.95, 1.00] | 1.00 | 0.84 [0.76, 0.91] |
| SM_story_plain | 1.00 [1.00, 1.00] | 1.00 | 0.94 [0.91, 0.96] | 0.98 | 0.89 | 0.94 [0.91, 0.96] | 0.97 [0.91, 1.00] | 1.00 | 0.83 [0.74, 0.90] |
| S_storychar_plain | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 0.99 | 0.98 [0.98, 0.99] | 0.99 [0.98, 1.00] | 1.00 | 0.83 [0.77, 0.90] |
| SM_storychar_plain | 1.00 [1.00, 1.00] | 1.00 | 0.94 [0.92, 0.95] | 0.95 | 0.91 | 0.94 [0.93, 0.95] | 0.97 [0.95, 1.00] | 1.00 | 0.79 [0.70, 0.87] |
| S_story_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.98, 0.99] | 0.98 | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.97, 1.00] | 1.00 | 0.57 [0.45, 0.69] |
| SM_story_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.91 [0.77, 0.98] | 0.62 | 0.97 | 0.98 [0.97, 0.98] | 1.00 [0.99, 1.00] | 1.00 | 0.62 [0.51, 0.73] |
| W_digest_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 1.00] | 1.00 | 0.94 | 1.00 [0.99, 1.00] | 0.90 [0.69, 1.00] | 0.99 | 0.60 [0.48, 0.71] |
| WM_digest_plain | 1.00 [1.00, 1.00] | 1.00 | 1.00 [1.00, 1.00] | 1.00 | 1.00 | 1.00 [1.00, 1.00] | 0.83 [0.50, 1.00] | 1.00 | 0.67 [0.57, 0.76] |
| F_reader | 0.99 [0.99, 1.00] | 1.00 | 0.97 [0.93, 1.00] | 0.89 | 0.99 | 1.00 [1.00, 1.00] | 0.99 [0.98, 1.00] | 1.00 | 0.77 [0.68, 0.85] |
| FM_title | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 1.00] | 0.97 | 1.00 | 1.00 [1.00, 1.00] | 0.97 [0.91, 1.00] | 1.00 | 0.80 [0.72, 0.88] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=24) |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.29 / 1.00 |
| SM_story_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.08 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.14 / 0.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.03 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.29 / 1.00 |
| S_storychar_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.29 / 1.00 |
| SM_storychar_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.17 / 0.00 / 0.50 | 0.10 / 0.00 / 1.00 | 0.03 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.23 / 0.29 / 1.00 |
| S_story_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.10 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.41 / 0.21 / 0.71 |
| SM_story_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.15 / 0.00 / 0.67 | 0.48 / 0.00 / 0.00 | 0.10 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.01 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.36 / 0.21 / 0.71 |
| W_digest_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.10 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.10 / 0.67 / 0.83 | 0.00 / 1.00 / 1.00 | 0.43 / 0.14 / 0.64 |
| WM_digest_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.17 / 1.00 | 0.02 / 0.50 / 1.00 | 0.07 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.25 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.38 / 0.07 / 0.71 |
| F_reader | 0.04 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.67 / 0.83 | 0.17 / 0.00 / 0.50 | 0.10 / 0.00 / 1.00 | 0.02 / 1.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.27 / 0.21 / 1.00 |
| FM_title | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.23 / 0.21 / 0.93 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 23 | ordered text |  |  | 0.11 (0.065) | -0.06 (0.440) | -0.14 | -0.00 (0.915) | -0.06 |
| SM_story_plain | 23 | ordered text |  |  | 0.11 (0.070) | 0.03 (0.750) | -0.04 | 0.02 (0.660) | -0.03 |
| S_storychar_plain | 23 | ordered text |  |  | 0.10 (0.100) | -0.05 (0.550) | -0.13 | -0.01 (0.795) | -0.07 |
| SM_storychar_plain | 23 | ordered text |  |  | 0.14 (0.020) | -0.01 (0.895) | -0.08 | -0.01 (0.900) | -0.07 |
| S_story_tfidf | 23 | ordered text |  |  | 0.14 (0.075) | 0.05 (0.720) | -0.02 | 0.09 (0.305) | 0.04 |
| SM_story_tfidf | 23 | ordered text |  |  | 0.10 (0.245) | 0.01 (0.945) | -0.04 | 0.02 (0.830) | -0.04 |
| W_digest_plain | 23 | ordered text |  |  | 0.16 (0.015) | 0.12 (0.130) | 0.06 | 0.00 (0.935) | -0.06 |
| WM_digest_plain | 23 | ordered text |  |  | 0.23 (0.005) | 0.16 (0.065) | 0.11 | -0.02 (0.785) | -0.08 |
| F_reader | 23 | ordered text |  |  | 0.03 (0.585) | -0.01 (0.855) | -0.08 | -0.04 (0.275) | -0.11 |
| FM_title | 23 | ordered text |  |  | 0.06 (0.275) | -0.01 (0.930) | -0.08 | -0.06 (0.255) | -0.12 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| S_story_plain | 0.29 / 0.07 | 0.56 / 0.16 | 27 / 34 | 0.44 / 0.42 | -0.49 | 0.00 | 7 (wharton_frome) |
| SM_story_plain | 0.29 / 0.07 | 0.53 / 0.16 | 28 / 34 | 0.40 / 0.42 | -0.49 | 0.00 | 7 (fathers_garnett) |
| S_storychar_plain | 0.29 / 0.07 | 0.51 / 0.16 | 24 / 34 | 0.39 / 0.42 | 0.00 | 0.00 | 8 (wells_time) |
| SM_storychar_plain | 0.28 / 0.07 | 0.51 / 0.16 | 27 / 34 | 0.41 / 0.42 | 0.55 | 0.00 | 9 (wells_time) |
| S_story_tfidf | 0.29 / 0.07 | 0.35 / 0.16 | 26 / 34 | 0.40 / 0.42 | 1.17 | 0.00 | 14 (fathers_garnett) |
| SM_story_tfidf | 0.27 / 0.07 | 0.34 / 0.16 | 24 / 34 | 0.41 / 0.42 | 0.90 | 0.00 | 13 (wharton_frome) |
| W_digest_plain | 0.28 / 0.07 | 0.33 / 0.16 | 25 / 34 | 0.38 / 0.42 | 0.10 | 0.00 | 8 (wells_worlds) |
| WM_digest_plain | 0.27 / 0.07 | 0.29 / 0.16 | 26 / 34 | 0.39 / 0.42 | 0.27 | 0.00 | 8 (wharton_frome) |
| F_reader | 0.28 / 0.07 | 0.42 / 0.16 | 28 / 34 | 0.46 / 0.42 | 0.52 | 0.00 | 9 (zamyatin_we) |
| FM_title | 0.28 / 0.07 | 0.46 / 0.16 | 31 / 34 | 0.45 / 0.42 | 0.34 | 0.00 | 8 (conrad_agent) |

Spearman between the pair distances of two blocks, all pairs.

| block | S_story_plain | SM_story_plain | S_storychar_plain | SM_storychar_plain | S_story_tfidf | SM_story_tfidf | W_digest_plain | WM_digest_plain | F_reader | FM_title |
|---|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 | 0.68 | 0.86 | 0.67 | 0.45 | 0.35 | 0.37 | 0.41 | 0.37 | 0.36 |
| SM_story_plain | 0.68 | 1.00 | 0.70 | 0.89 | 0.42 | 0.51 | 0.46 | 0.56 | 0.41 | 0.48 |
| S_storychar_plain | 0.86 | 0.70 | 1.00 | 0.72 | 0.40 | 0.33 | 0.34 | 0.37 | 0.48 | 0.46 |
| SM_storychar_plain | 0.67 | 0.89 | 0.72 | 1.00 | 0.43 | 0.46 | 0.35 | 0.48 | 0.42 | 0.48 |
| S_story_tfidf | 0.45 | 0.42 | 0.40 | 0.43 | 1.00 | 0.43 | 0.33 | 0.32 | 0.18 | 0.17 |
| SM_story_tfidf | 0.35 | 0.51 | 0.33 | 0.46 | 0.43 | 1.00 | 0.34 | 0.45 | 0.29 | 0.27 |
| W_digest_plain | 0.37 | 0.46 | 0.34 | 0.35 | 0.33 | 0.34 | 1.00 | 0.61 | 0.30 | 0.27 |
| WM_digest_plain | 0.41 | 0.56 | 0.37 | 0.48 | 0.32 | 0.45 | 0.61 | 1.00 | 0.37 | 0.35 |
| F_reader | 0.37 | 0.41 | 0.48 | 0.42 | 0.18 | 0.29 | 0.30 | 0.37 | 1.00 | 0.84 |
| FM_title | 0.36 | 0.48 | 0.46 | 0.48 | 0.17 | 0.27 | 0.27 | 0.35 | 0.84 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | S_story_plain | SM_story_plain | S_storychar_plain | SM_storychar_plain | S_story_tfidf | SM_story_tfidf | W_digest_plain | WM_digest_plain | F_reader | FM_title |
|---|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 | 0.63 | 0.84 | 0.61 | 0.36 | 0.24 | 0.28 | 0.32 | 0.26 | 0.25 |
| SM_story_plain | 0.63 | 1.00 | 0.65 | 0.87 | 0.33 | 0.44 | 0.38 | 0.50 | 0.32 | 0.39 |
| S_storychar_plain | 0.84 | 0.65 | 1.00 | 0.68 | 0.29 | 0.22 | 0.24 | 0.27 | 0.39 | 0.37 |
| SM_storychar_plain | 0.61 | 0.87 | 0.68 | 1.00 | 0.34 | 0.37 | 0.25 | 0.41 | 0.32 | 0.40 |
| S_story_tfidf | 0.36 | 0.33 | 0.29 | 0.34 | 1.00 | 0.34 | 0.23 | 0.22 | 0.04 | 0.03 |
| SM_story_tfidf | 0.24 | 0.44 | 0.22 | 0.37 | 0.34 | 1.00 | 0.24 | 0.38 | 0.18 | 0.16 |
| W_digest_plain | 0.28 | 0.38 | 0.24 | 0.25 | 0.23 | 0.24 | 1.00 | 0.56 | 0.20 | 0.16 |
| WM_digest_plain | 0.32 | 0.50 | 0.27 | 0.41 | 0.22 | 0.38 | 0.56 | 1.00 | 0.28 | 0.25 |
| F_reader | 0.26 | 0.32 | 0.39 | 0.32 | 0.04 | 0.18 | 0.20 | 0.28 | 1.00 | 0.82 |
| FM_title | 0.25 | 0.39 | 0.37 | 0.40 | 0.03 | 0.16 | 0.16 | 0.25 | 0.82 | 1.00 |


Every labelled pair: rank of b from a / rank of a from b (1 = nearest), and in brackets the share of negative pairs that are farther apart.

| set | pair | S_story_plain | SM_story_plain | S_storychar_plain | SM_storychar_plain | S_story_tfidf | SM_story_tfidf | W_digest_plain | WM_digest_plain | F_reader | FM_title |
|---|---|---|---|---|---|---|---|---|---|---|---|
| translation_pair | fathers_garnett ~ fathers_hogarth | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 3 (0.99) | 1 / 1 (1.00) |
| translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 2 (1.00) | 1 / 1 (1.00) |
| translation_pair | journey_1871 ~ journey_malleson | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) |
| edition_pair | frankenstein_1818 ~ frankenstein_1831 | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| retelling | burnett_princess ~ burnett_sara_crewe | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | holmes_hound ~ holmes_study | 1 / 3 (0.99) | 3 / 3 (0.91) | 2 / 3 (0.98) | 3 / 3 (0.95) | 2 / 3 (0.97) | 2 / 1 (0.99) | 10 / 5 (0.69) | 17 / 16 (0.50) | 3 / 1 (0.98) | 1 / 3 (0.91) |
| series | oz_land ~ oz_wizard | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.97) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | tarzan_apes ~ tarzan_return | 1 / 1 (0.95) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_garnett | 2 / 2 (0.99) | 4 / 4 (0.89) | 2 / 2 (0.99) | 3 / 6 (0.91) | 2 / 2 (1.00) | 3 / 3 (0.97) | 3 / 3 (0.94) | 2 / 3 (1.00) | 3 / 3 (0.99) | 3 / 2 (1.00) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_ralston | 3 / 2 (0.99) | 2 / 4 (0.91) | 3 / 2 (0.99) | 2 / 5 (0.93) | 3 / 4 (0.97) | 2 / 3 (0.97) | 2 / 3 (0.99) | 3 / 3 (1.00) | 1 / 1 (1.00) | 2 / 2 (1.00) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_garnett | 3 / 3 (0.96) | 3 / 3 (0.95) | 2 / 3 (0.98) | 3 / 3 (0.95) | 2 / 3 (0.99) | 3 / 2 (0.97) | 2 / 2 (1.00) | 2 / 2 (1.00) | 1 / 1 (1.00) | 3 / 2 (1.00) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_ralston | 2 / 3 (0.98) | 2 / 3 (0.96) | 3 / 3 (0.98) | 2 / 3 (0.95) | 3 / 3 (0.98) | 2 / 2 (0.98) | 3 / 2 (1.00) | 3 / 2 (1.00) | 2 / 3 (1.00) | 2 / 2 (1.00) |
| same_author_unrelated | wells_time ~ wells_worlds | 1 / 1 (1.00) | 1 / 1 (0.98) | 1 / 1 (0.98) | 1 / 1 (0.95) | 1 / 1 (0.98) | 11 / 11 (0.62) | 1 / 1 (1.00) | 1 / 2 (1.00) | 3 / 6 (0.89) | 1 / 1 (0.97) |
