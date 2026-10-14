## World convergence (qwen_maskB; 12 books with every chunk embedded)

Means over 12 books x 5 draws. cos = cosine of the k-chunk book vector with the all-chunk vector; rho_dist = Spearman of the distances to the other 86 books.

| k | cos_raw | cos_centred | rho_dist | top5_overlap | same_nearest | worst cos_centred |
|---|---|---|---|---|---|---|
| 5 | 0.927 | 0.688 | 0.808 | 0.663 | 0.650 | 0.358 |
| 10 | 0.965 | 0.815 | 0.907 | 0.760 | 0.733 | 0.650 |
| 20 | 0.984 | 0.901 | 0.948 | 0.813 | 0.817 | 0.738 |
| 40 | 0.993 | 0.954 | 0.981 | 0.883 | 0.950 | 0.900 |
| 80 | 0.998 | 0.984 | 0.991 | 0.943 | 0.933 | 0.964 |

Per book at k = 40.

| key | n_chunks | cos_centred | rho_dist | top5_overlap | same_nearest |
|---|---|---|---|---|---|
| austen_emma | 158 | 0.955 | 0.995 | 0.920 | 1.000 |
| barset_towers | 198 | 0.963 | 0.990 | 1.000 | 1.000 |
| charterhouse_loyd | 199 | 0.961 | 0.979 | 0.800 | 1.000 |
| collins_moonstone | 197 | 0.935 | 0.958 | 0.920 | 0.800 |
| dickens_great | 186 | 0.913 | 0.955 | 0.800 | 1.000 |
| dost_cp_garnett | 199 | 0.931 | 0.964 | 0.640 | 1.000 |
| james_ambassadors | 165 | 0.954 | 0.990 | 1.000 | 1.000 |
| mystisland_kingston | 195 | 0.981 | 0.997 | 1.000 | 1.000 |
| mystisland_white | 162 | 0.977 | 0.997 | 1.000 | 1.000 |
| stoker_dracula | 161 | 0.941 | 0.980 | 0.840 | 0.600 |
| tolstoy_res_maude | 172 | 0.957 | 0.974 | 0.840 | 1.000 |
| wyss_swiss | 166 | 0.977 | 0.995 | 0.840 | 1.000 |
