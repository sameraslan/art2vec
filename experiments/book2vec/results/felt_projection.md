## Felt from passage embeddings, against the reader

| projection | per word: mean Spearman over 24 words | words with Spearman > 0.4 | per book: mean Spearman, raw reader scores | per book: mean Spearman, both z-scored | ... against another book's reader scores | books where own reader vector is the best match |
|---|---|---|---|---|---|---|
| F_proj_plain | 0.46 | 15 | 0.47 | 0.54 | -0.02 | 6 |
| F_proj_plain_n20 | 0.44 | 11 | 0.47 | 0.51 | -0.02 | 6 |
| F_proj_inst | 0.50 | 17 | 0.44 | 0.49 | -0.02 | 5 |
| F_proj_inst_n20 | 0.48 | 16 | 0.43 | 0.47 | -0.02 | 4 |

Spearman per word across the 24 books (reader score against projection).

| word | reader sd | F_proj_plain | F_proj_plain_n20 | F_proj_inst | F_proj_inst_n20 |
|---|---|---|---|---|---|
| tender | 0.63 | 0.80 | 0.77 | 0.72 | 0.73 |
| wistful | 0.75 | 0.76 | 0.74 | 0.73 | 0.72 |
| solemn | 0.70 | 0.72 | 0.73 | 0.69 | 0.67 |
| cosy | 0.64 | 0.72 | 0.68 | 0.68 | 0.64 |
| eerie | 0.73 | 0.69 | 0.66 | 0.81 | 0.77 |
| dreamlike | 0.82 | 0.66 | 0.68 | 0.76 | 0.77 |
| melancholy | 0.70 | 0.64 | 0.70 | 0.78 | 0.77 |
| disorienting | 0.86 | 0.64 | 0.62 | 0.74 | 0.78 |
| desolate | 0.93 | 0.60 | 0.60 | 0.67 | 0.66 |
| warm | 0.81 | 0.53 | 0.54 | 0.42 | 0.41 |
| menacing | 0.87 | 0.52 | 0.50 | 0.69 | 0.61 |
| bleak | 0.85 | 0.45 | 0.40 | 0.58 | 0.54 |
| cold | 0.99 | 0.45 | 0.39 | 0.51 | 0.53 |
| anxious | 0.73 | 0.43 | 0.35 | 0.65 | 0.66 |
| bitter | 0.75 | 0.43 | 0.30 | 0.39 | 0.38 |
| claustrophobic | 0.96 | 0.38 | 0.29 | 0.47 | 0.42 |
| hopeful | 0.79 | 0.37 | 0.39 | 0.43 | 0.35 |
| grotesque | 0.55 | 0.34 | 0.28 | 0.07 | 0.08 |
| tense | 0.61 | 0.30 | 0.23 | 0.21 | 0.15 |
| serene | 0.49 | 0.26 | 0.29 | 0.46 | 0.46 |
| funny | 0.75 | 0.17 | 0.23 | 0.14 | 0.10 |
| exhilarating | 0.91 | 0.10 | 0.09 | 0.08 | 0.15 |
| lush | 0.57 | 0.09 | 0.10 | 0.21 | 0.18 |
| playful | 0.83 | 0.04 | 0.03 | 0.00 | 0.00 |

