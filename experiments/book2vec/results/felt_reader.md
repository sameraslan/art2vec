## Felt: the reader's 24 word scores

### Is the scale used?

| source | share of 0s | share of 1s | share of 2s | share of 3s | mean | mean per-book sd |
|---|---|---|---|---|---|---|
| from text (24 books) | 0.14 | 0.39 | 0.36 | 0.12 | 1.45 | 0.83 |
| title only (23 books) | 0.38 | 0.33 | 0.19 | 0.11 | 1.03 | 0.95 |

Per word, from text.

| word | mean | sd across books | 0 | 1 | 2 | 3 | Spearman text vs title (23 books) |
|---|---|---|---|---|---|---|---|
| tense | 2.29 | 0.61 | 0 | 2 | 13 | 9 | 0.58 |
| anxious | 2.04 | 0.73 | 0 | 6 | 11 | 7 | 0.71 |
| melancholy | 1.92 | 0.70 | 0 | 7 | 12 | 5 | 0.85 |
| desolate | 1.88 | 0.93 | 2 | 6 | 9 | 7 | 0.80 |
| menacing | 1.79 | 0.87 | 1 | 9 | 8 | 6 | 0.89 |
| grotesque | 1.67 | 0.55 | 0 | 9 | 14 | 1 | 0.85 |
| cold | 1.67 | 0.99 | 4 | 5 | 10 | 5 | 0.80 |
| bitter | 1.67 | 0.75 | 2 | 6 | 14 | 2 | 0.93 |
| bleak | 1.67 | 0.85 | 2 | 8 | 10 | 4 | 0.79 |
| funny | 1.67 | 0.75 | 2 | 6 | 14 | 2 | 0.74 |
| wistful | 1.62 | 0.75 | 1 | 10 | 10 | 3 | 0.83 |
| tender | 1.62 | 0.63 | 0 | 11 | 11 | 2 | 0.82 |
| solemn | 1.42 | 0.70 | 3 | 8 | 13 | 0 | 0.67 |
| lush | 1.42 | 0.57 | 1 | 12 | 11 | 0 | 0.67 |
| eerie | 1.29 | 0.73 | 3 | 12 | 8 | 1 | 0.86 |
| playful | 1.25 | 0.83 | 4 | 12 | 6 | 2 | 0.83 |
| claustrophobic | 1.21 | 0.96 | 6 | 10 | 5 | 3 | 0.74 |
| exhilarating | 1.21 | 0.91 | 6 | 9 | 7 | 2 | 0.74 |
| dreamlike | 1.21 | 0.82 | 5 | 10 | 8 | 1 | 0.91 |
| warm | 1.08 | 0.81 | 5 | 14 | 3 | 2 | 0.68 |
| disorienting | 1.08 | 0.86 | 6 | 12 | 4 | 2 | 0.67 |
| hopeful | 1.04 | 0.79 | 5 | 15 | 2 | 2 | 0.74 |
| serene | 0.58 | 0.49 | 10 | 14 | 0 | 0 | 0.46 |
| cosy | 0.58 | 0.64 | 12 | 10 | 2 | 0 | 0.63 |

### Two independent readings of one work (and series / same-author pairs)

Pearson z = correlation after each word is z-scored across the 24 books, which takes out the profile all books share. Ranks are among the 23 other books (1 = nearest).

| set | pair | Pearson raw | Spearman raw | Pearson z | mean abs diff | exact agreement | rank of b from a (z) | rank of a from b (z) |
|---|---|---|---|---|---|---|---|---|
| translation_pair | fathers_garnett ~ fathers_hogarth | 0.81 | 0.79 | 0.65 | 0.29 | 0.71 | 3.00 | 3.00 |
| translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.79 | 0.77 | 0.76 | 0.29 | 0.71 | 2.00 | 2.00 |
| translation_pair | journey_1871 ~ journey_malleson | 0.82 | 0.82 | 0.68 | 0.29 | 0.71 | 1.00 | 1.00 |
| edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.91 | 0.92 | 0.84 | 0.17 | 0.83 | 1.00 | 1.00 |
| retelling | burnett_princess ~ burnett_sara_crewe | 0.76 | 0.73 | 0.84 | 0.25 | 0.75 | 1.00 | 1.00 |
| series | holmes_hound ~ holmes_study | 0.75 | 0.77 | 0.55 | 0.42 | 0.58 | 3.00 | 2.00 |
| series | oz_land ~ oz_wizard | 0.80 | 0.76 | 0.82 | 0.33 | 0.67 | 1.00 | 1.00 |
| series | tarzan_apes ~ tarzan_return | 0.83 | 0.82 | 0.71 | 0.33 | 0.67 | 1.00 | 1.00 |
| same_author_unrelated | fathers_garnett ~ gentlefolk_garnett | 0.79 | 0.79 | 0.72 | 0.33 | 0.67 | 2.00 | 3.00 |
| same_author_unrelated | fathers_garnett ~ gentlefolk_ralston | 0.83 | 0.84 | 0.78 | 0.21 | 0.79 | 1.00 | 1.00 |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_garnett | 0.86 | 0.89 | 0.76 | 0.21 | 0.79 | 1.00 | 1.00 |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_ralston | 0.76 | 0.79 | 0.68 | 0.33 | 0.67 | 2.00 | 3.00 |
| same_author_unrelated | wells_time ~ wells_worlds | 0.72 | 0.71 | 0.35 | 0.46 | 0.54 | 3.00 | 7.00 |
| negatives (median) | 263 pairs | 0.20 |  | -0.07 | 0.88 | 0.33 |  |  |

### From-text felt against title-only felt

| key | Pearson raw | Pearson z | rank of own title vector (z) | mean abs diff | exact agreement |
|---|---|---|---|---|---|
| wharton_frome | 0.92 | 0.80 | 1.00 | 0.33 | 0.67 |
| journey_1871 | 0.50 | 0.60 | 1.00 | 1.00 | 0.25 |
| oz_land | 0.77 | 0.88 | 1.00 | 0.42 | 0.62 |
| conrad_agent | 0.90 | 0.91 | 1.00 | 0.29 | 0.71 |
| tarzan_return | 0.78 | 0.77 | 2.00 | 0.38 | 0.62 |
| wells_worlds | 0.79 | 0.75 | 1.00 | 0.58 | 0.46 |
| zamyatin_we | 0.81 | 0.78 | 1.00 | 0.50 | 0.50 |
| fathers_garnett | 0.74 | 0.81 | 1.00 | 0.38 | 0.62 |
| christie_styles | 0.65 | 0.73 | 1.00 | 0.71 | 0.29 |
| wells_time | 0.77 | 0.53 | 1.00 | 0.58 | 0.50 |
| gentlefolk_ralston | 0.55 | 0.69 | 4.00 | 0.67 | 0.46 |
| holmes_hound | 0.64 | 0.59 | 4.00 | 0.67 | 0.38 |
| holmes_study | 0.67 | 0.63 | 1.00 | 0.79 | 0.25 |
| oz_wizard | 0.77 | 0.91 | 1.00 | 0.67 | 0.33 |
| hammett_falcon | 0.88 | 0.85 | 1.00 | 0.33 | 0.67 |
| frankenstein_1818 | 0.81 | 0.63 | 2.00 | 0.46 | 0.54 |
| gentlefolk_garnett | 0.67 | 0.80 | 3.00 | 0.58 | 0.54 |
| burnett_princess | 0.76 | 0.85 | 1.00 | 0.62 | 0.42 |
| journey_malleson | 0.68 | 0.79 | 1.00 | 0.71 | 0.33 |
| frankenstein_1831 | 0.86 | 0.65 | 1.00 | 0.38 | 0.62 |
| tarzan_apes | 0.72 | 0.77 | 2.00 | 0.71 | 0.29 |
| fathers_hogarth | 0.66 | 0.76 | 1.00 | 0.58 | 0.46 |
| burnett_sara_crewe | 0.82 | 0.89 | 1.00 | 0.46 | 0.54 |
| MEAN | 0.74 | 0.76 | 1.48 | 0.56 | 0.48 |

Own title-only vector is the nearest of the 23 for 17 of 23 books (same-work partners are among the candidates).

