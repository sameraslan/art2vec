## Story leak: from-text digests against title-only digests

### (a) Does the from-text digest retrieve its own title-only digest?

| field | cosine | books | own title digest is rank 1 | mean rank | mean cos to own | mean cos to others | smallest margin over best other |
|---|---|---|---|---|---|---|---|
| story | raw | 23 | 22 | 1.04 | 0.75 | 0.43 | -0.06 |
| story | centred | 23 | 22 | 1.04 | 0.54 | -0.05 | -0.01 |
| characters | raw | 23 | 19 | 1.87 | 0.72 | 0.48 | -0.07 |
| characters | centred | 23 | 19 | 1.35 | 0.42 | -0.06 | -0.13 |
| world | raw | 23 | 22 | 1.04 | 0.78 | 0.56 | -0.09 |
| world | centred | 23 | 22 | 1.04 | 0.47 | -0.04 | -0.03 |
| subjects | raw | 23 | 20 | 1.17 | 0.73 | 0.46 | -0.08 |
| subjects | centred | 23 | 21 | 1.09 | 0.47 | -0.05 | -0.10 |

Per book, story field, centred cosine (best other includes the same work in another translation).

| id | key | recognised | at part | title-only memory | cos to own title digest | best other | rank of own |
|---|---|---|---|---|---|---|---|
| b01 | wharton_frome | True | 1 | confident | 0.58 | 0.21 | 1.00 |
| b02 | journey_1871 | True | 1 | confident | 0.58 | 0.54 | 1.00 |
| b03 | oz_land | True | 1 | partial | 0.43 | 0.39 | 1.00 |
| b04 | conrad_agent | True | 1 | confident | 0.58 | 0.12 | 1.00 |
| b05 | tarzan_return | True | 1 | partial | 0.18 | 0.19 | 2.00 |
| b06 | wells_worlds | True | 1 | confident | 0.62 | 0.20 | 1.00 |
| b07 | zamyatin_we | True | 1 | confident | 0.66 | 0.16 | 1.00 |
| b08 | fathers_garnett | True | 1 | confident | 0.50 | 0.47 | 1.00 |
| b09 | christie_styles | True | 3 | confident | 0.39 | 0.18 | 1.00 |
| b10 | merriman_barlasch | False | 0 | none |  | 0.15 |  |
| b11 | wells_time | True | 1 | confident | 0.64 | 0.24 | 1.00 |
| b12 | gentlefolk_ralston | True | 1 | confident | 0.57 | 0.39 | 1.00 |
| b13 | holmes_hound | True | 1 | confident | 0.64 | 0.20 | 1.00 |
| b14 | holmes_study | True | 1 | confident | 0.55 | 0.47 | 1.00 |
| b15 | oz_wizard | True | 1 | confident | 0.85 | 0.38 | 1.00 |
| b16 | hammett_falcon | True | 3 | confident | 0.69 | 0.27 | 1.00 |
| b17 | frankenstein_1818 | True | 1 | confident | 0.43 | 0.45 | 1.00 |
| b18 | gentlefolk_garnett | True | 1 | confident | 0.42 | 0.48 | 1.00 |
| b19 | burnett_princess | True | 1 | confident | 0.67 | 0.61 | 1.00 |
| b20 | journey_malleson | True | 1 | confident | 0.49 | 0.54 | 1.00 |
| b21 | frankenstein_1831 | True | 1 | confident | 0.61 | 0.63 | 1.00 |
| b22 | tarzan_apes | True | 1 | confident | 0.46 | 0.36 | 1.00 |
| b23 | fathers_hogarth | True | 1 | confident | 0.44 | 0.46 | 1.00 |
| b24 | burnett_sara_crewe | True | 1 | confident | 0.54 | 0.62 | 1.00 |

### (b) Two independent readings of one work, against memory

If `text a ~ text b` is above both `text ~ title` columns, the two readings agree with each other more than either agrees with what the model remembers from the title.

| field | cosine | set | pair | text a ~ text b | text a ~ title a | text b ~ title b | text a ~ title b | text b ~ title a | title a ~ title b | median text ~ text, all pairs |
|---|---|---|---|---|---|---|---|---|---|---|
| story | raw | translation_pair | fathers_garnett ~ fathers_hogarth | 0.85 | 0.77 | 0.73 | 0.77 | 0.74 | 0.91 | 0.47 |
| story | raw | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.80 | 0.68 | 0.76 | 0.71 | 0.68 | 0.86 | 0.47 |
| story | raw | translation_pair | journey_1871 ~ journey_malleson | 0.91 | 0.77 | 0.69 | 0.72 | 0.76 | 0.85 | 0.47 |
| story | raw | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.78 | 0.74 | 0.83 | 0.75 | 0.84 | 0.90 | 0.47 |
| story | raw | retelling | burnett_princess ~ burnett_sara_crewe | 0.83 | 0.83 | 0.75 | 0.80 | 0.80 | 0.87 | 0.47 |
| story | centred | translation_pair | fathers_garnett ~ fathers_hogarth | 0.68 | 0.50 | 0.44 | 0.47 | 0.46 | 0.80 | -0.04 |
| story | centred | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.60 | 0.42 | 0.57 | 0.48 | 0.39 | 0.76 | -0.04 |
| story | centred | translation_pair | journey_1871 ~ journey_malleson | 0.81 | 0.58 | 0.49 | 0.54 | 0.54 | 0.78 | -0.04 |
| story | centred | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.46 | 0.43 | 0.61 | 0.45 | 0.63 | 0.78 | -0.04 |
| story | centred | retelling | burnett_princess ~ burnett_sara_crewe | 0.66 | 0.67 | 0.54 | 0.61 | 0.62 | 0.76 | -0.04 |
| characters | raw | translation_pair | fathers_garnett ~ fathers_hogarth | 0.92 | 0.65 | 0.60 | 0.65 | 0.63 | 0.88 | 0.53 |
| characters | raw | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.80 | 0.76 | 0.72 | 0.74 | 0.72 | 0.91 | 0.53 |
| characters | raw | translation_pair | journey_1871 ~ journey_malleson | 0.79 | 0.71 | 0.71 | 0.68 | 0.70 | 0.91 | 0.53 |
| characters | raw | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.79 | 0.78 | 0.75 | 0.62 | 0.87 | 0.80 | 0.53 |
| characters | raw | retelling | burnett_princess ~ burnett_sara_crewe | 0.86 | 0.85 | 0.77 | 0.83 | 0.78 | 0.96 | 0.53 |
| characters | centred | translation_pair | fathers_garnett ~ fathers_hogarth | 0.82 | 0.19 | 0.15 | 0.22 | 0.18 | 0.76 | -0.03 |
| characters | centred | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.52 | 0.42 | 0.37 | 0.36 | 0.37 | 0.80 | -0.03 |
| characters | centred | translation_pair | journey_1871 ~ journey_malleson | 0.49 | 0.36 | 0.44 | 0.35 | 0.39 | 0.84 | -0.03 |
| characters | centred | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.54 | 0.54 | 0.45 | 0.22 | 0.70 | 0.59 | -0.03 |
| characters | centred | retelling | burnett_princess ~ burnett_sara_crewe | 0.69 | 0.64 | 0.49 | 0.58 | 0.51 | 0.91 | -0.03 |
| world | raw | translation_pair | fathers_garnett ~ fathers_hogarth | 0.81 | 0.85 | 0.81 | 0.85 | 0.82 | 0.98 | 0.59 |
| world | raw | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.85 | 0.85 | 0.84 | 0.83 | 0.84 | 0.96 | 0.59 |
| world | raw | translation_pair | journey_1871 ~ journey_malleson | 0.85 | 0.76 | 0.79 | 0.76 | 0.80 | 0.93 | 0.59 |
| world | raw | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.87 | 0.80 | 0.80 | 0.79 | 0.77 | 0.92 | 0.59 |
| world | raw | retelling | burnett_princess ~ burnett_sara_crewe | 0.74 | 0.78 | 0.79 | 0.77 | 0.82 | 0.98 | 0.59 |
| world | centred | translation_pair | fathers_garnett ~ fathers_hogarth | 0.44 | 0.51 | 0.42 | 0.55 | 0.43 | 0.92 | -0.04 |
| world | centred | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.57 | 0.59 | 0.57 | 0.55 | 0.53 | 0.91 | -0.04 |
| world | centred | translation_pair | journey_1871 ~ journey_malleson | 0.55 | 0.38 | 0.50 | 0.44 | 0.48 | 0.85 | -0.04 |
| world | centred | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.68 | 0.53 | 0.47 | 0.49 | 0.42 | 0.80 | -0.04 |
| world | centred | retelling | burnett_princess ~ burnett_sara_crewe | 0.26 | 0.35 | 0.42 | 0.33 | 0.50 | 0.93 | -0.04 |

| field | cosine | pairs where the readings agree more | pairs |
|---|---|---|---|
| characters | centred | 4 | 5 |
| characters | raw | 5 | 5 |
| story | centred | 3 | 5 |
| story | raw | 3 | 5 |
| world | centred | 2 | 5 |
| world | raw | 3 | 5 |

### (c) From-text against title-only pair similarities

| field | books | pairs | Spearman, from-text vs title-only pair similarity |
|---|---|---|---|
| story | 23 | 253 | 0.66 |
| characters | 23 | 253 | 0.53 |
| world | 23 | 253 | 0.56 |
| subjects | 23 | 253 | 0.59 |

