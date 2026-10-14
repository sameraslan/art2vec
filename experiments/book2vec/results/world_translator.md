## Author or translator (6 Garnett books)

| block | nearest: author+translator | author only | translator only | neither | AUC author beats translator (14 vs 11) | AUC translation pair closer than same-author pair (10 vs 52) | ... than orig-English same-author pair (10 vs 33) | median d translation pair / median d same-author |
|---|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 2 | 0 | 3 | 1 | 0.33 | 1.00 | 1.00 | 0.10 |
| W1_qwen_maskA_c | 3 | 0 | 0 | 3 | 0.85 | 0.96 | 0.94 | 0.29 |
| W1_qwen_maskB_c | 3 | 0 | 0 | 3 | 0.85 | 0.93 | 0.91 | 0.30 |
| W0_tfidf_clean | 3 | 1 | 2 | 0 | 0.64 | 1.00 | 1.00 | 0.53 |
| W0_tfidf_maskB | 4 | 1 | 1 | 0 | 0.60 | 0.98 | 0.98 | 0.59 |

Nearest book that is not the same work, per Garnett book (ranks count from 1).

| block | anchor | nearest_not_same_work | shares | rank_nearest_same_author_other_translator | rank_nearest_garnett_other_author |
|---|---|---|---|---|---|
| W1_qwen_clean_c | dost_cp_garnett | dost_bk_garnett | author+translator | 5 | 2 |
| W1_qwen_clean_c | dost_bk_garnett | dost_cp_garnett | author+translator | 7 | 2 |
| W1_qwen_clean_c | dost_notes_garnett | zamyatin_we | neither | 10 | 8 |
| W1_qwen_clean_c | tolstoy_ak_garnett | gentlefolk_garnett | translator only | 8 | 1 |
| W1_qwen_clean_c | fathers_garnett | tolstoy_ak_garnett | translator only | 3 | 1 |
| W1_qwen_clean_c | gentlefolk_garnett | tolstoy_ak_garnett | translator only | 4 | 1 |
| W1_qwen_maskA_c | dost_cp_garnett | dost_bk_garnett | author+translator | 13 | 19 |
| W1_qwen_maskA_c | dost_bk_garnett | dost_cp_garnett | author+translator | 12 | 4 |
| W1_qwen_maskA_c | dost_notes_garnett | zamyatin_we | neither | 15 | 17 |
| W1_qwen_maskA_c | tolstoy_ak_garnett | gentlefolk_ralston | neither | 9 | 2 |
| W1_qwen_maskA_c | fathers_garnett | woolf_voyage | neither | 3 | 24 |
| W1_qwen_maskA_c | gentlefolk_garnett | fathers_garnett | author+translator | 3 | 2 |
| W1_qwen_maskB_c | dost_cp_garnett | dost_bk_garnett | author+translator | 14 | 21 |
| W1_qwen_maskB_c | dost_bk_garnett | dost_cp_garnett | author+translator | 18 | 6 |
| W1_qwen_maskB_c | dost_notes_garnett | zamyatin_we | neither | 16 | 21 |
| W1_qwen_maskB_c | tolstoy_ak_garnett | hardy_jude | neither | 15 | 4 |
| W1_qwen_maskB_c | fathers_garnett | woolf_voyage | neither | 5 | 27 |
| W1_qwen_maskB_c | gentlefolk_garnett | fathers_garnett | author+translator | 4 | 2 |
| W0_tfidf_clean | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| W0_tfidf_clean | dost_bk_garnett | dost_cp_garnett | author+translator | 3 | 2 |
| W0_tfidf_clean | dost_notes_garnett | dost_cp_garnett | author+translator | 3 | 4 |
| W0_tfidf_clean | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 2 |
| W0_tfidf_clean | fathers_garnett | tolstoy_ak_garnett | translator only | 8 | 1 |
| W0_tfidf_clean | gentlefolk_garnett | tolstoy_ak_garnett | translator only | 8 | 1 |
| W0_tfidf_maskB | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| W0_tfidf_maskB | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 3 |
| W0_tfidf_maskB | dost_notes_garnett | dost_cp_garnett | author+translator | 3 | 4 |
| W0_tfidf_maskB | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 2 |
| W0_tfidf_maskB | fathers_garnett | tolstoy_ak_garnett | translator only | 7 | 1 |
| W0_tfidf_maskB | gentlefolk_garnett | fathers_garnett | author+translator | 8 | 2 |
