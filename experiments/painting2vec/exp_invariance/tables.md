
#### H1. Headline: the chosen variant of each block

Both directions pooled for ranks and d/NN-other.

| variant | pairs | R@1 | R@1 95% CI | R@5 | R@10 | median rank | p90 rank | d/NN-other med | p75 | p90 | d/step med | p90  | share under 1 step | Jaccard@10 | RBO | overlap@10 | overlap 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| subject: DINOv2-L cls, tile, centred cosine | clean 214 | 0.993 | 0.984-1.000 | 0.995 | 0.998 | 1 | 1 | 0.321 | 0.425 | 0.537 | 0.318 | 0.545 | 0.986 | 0.726 | 0.799 | 0.824 | 0.802-0.844 |
| subject: DINOv2-L cls, tile, centred cosine | all primary 274 | 0.969 | 0.949-0.985 | 0.989 | 0.993 | 1 | 1 | 0.322 | 0.454 | 0.719 | 0.319 | 0.72 | 0.971 | 0.705 | 0.779 | 0.804 | 0.784-0.825 |
| subject: DINOv2-L cls, tile, centred cosine | all rows 563 | 0.962 | 0.943-0.979 | 0.978 | 0.982 | 1 | 1 | 0.343 | 0.529 | 0.785 | 0.356 | 0.798 | 0.956 | 0.673 | 0.752 | 0.778 | 0.756-0.801 |
| subject (text-trained): SigLIP 2 embed, tile, centred | clean 214 | 0.988 | 0.972-1.000 | 0.991 | 0.993 | 1 | 1 | 0.444 | 0.562 | 0.693 | 0.432 | 0.675 | 0.991 | 0.646 | 0.738 | 0.768 | 0.749-0.786 |
| subject (text-trained): SigLIP 2 embed, tile, centred | all primary 274 | 0.94 | 0.914-0.962 | 0.964 | 0.973 | 1 | 1 | 0.445 | 0.591 | 0.829 | 0.432 | 0.808 | 0.938 | 0.628 | 0.714 | 0.745 | 0.721-0.765 |
| subject (text-trained): SigLIP 2 embed, tile, centred | all rows 563 | 0.92 | 0.895-0.944 | 0.955 | 0.966 | 1 | 1 | 0.485 | 0.656 | 0.935 | 0.472 | 0.95 | 0.917 | 0.601 | 0.69 | 0.721 | 0.698-0.743 |
| manner: CSD style, tile, PCA-64 whitened | clean 214 | 0.932 | 0.902-0.963 | 0.967 | 0.974 | 1 | 1 | 0.608 | 0.768 | 0.921 | 0.59 | 0.899 | 0.944 | 0.468 | 0.563 | 0.601 | 0.571-0.634 |
| manner: CSD style, tile, PCA-64 whitened | all primary 274 | 0.885 | 0.850-0.922 | 0.942 | 0.951 | 1 | 2 | 0.616 | 0.805 | 1.03 | 0.594 | 0.963 | 0.905 | 0.462 | 0.552 | 0.588 | 0.558-0.618 |
| manner: CSD style, tile, PCA-64 whitened | all rows 563 | 0.821 | 0.783-0.860 | 0.891 | 0.91 | 1 | 7 | 0.696 | 0.907 | 1.17 | 0.67 | 1.13 | 0.829 | 0.42 | 0.505 | 0.539 | 0.508-0.571 |
| manner (alt.): DINOv2-L gram_late, tile, cosine | clean 214 | 0.984 | 0.965-0.998 | 0.993 | 0.993 | 1 | 1 | 0.378 | 0.483 | 0.627 | 0.366 | 0.64 | 0.986 | 0.61 | 0.7 | 0.73 | 0.705-0.757 |
| manner (alt.): DINOv2-L gram_late, tile, cosine | all primary 274 | 0.922 | 0.889-0.949 | 0.949 | 0.956 | 1 | 1 | 0.382 | 0.551 | 0.847 | 0.378 | 0.844 | 0.92 | 0.579 | 0.66 | 0.693 | 0.665-0.722 |
| manner (alt.): DINOv2-L gram_late, tile, cosine | all rows 563 | 0.925 | 0.897-0.949 | 0.949 | 0.956 | 1 | 1 | 0.41 | 0.606 | 0.886 | 0.411 | 0.864 | 0.915 | 0.554 | 0.64 | 0.672 | 0.646-0.699 |
| colour: std hist+sw, PCA-64 whitened | clean 214 | 0.547 | 0.481-0.610 | 0.612 | 0.647 | 1 | 461 | 0.955 | 1.29 | 1.52 | 0.961 | 1.55 | 0.561 | 0.221 | 0.281 | 0.32 | 0.285-0.353 |
| colour: std hist+sw, PCA-64 whitened | all primary 274 | 0.529 | 0.473-0.591 | 0.584 | 0.615 | 1 | 888 | 0.966 | 1.35 | 1.65 | 0.967 | 1.65 | 0.54 | 0.23 | 0.288 | 0.323 | 0.289-0.359 |
| colour: std hist+sw, PCA-64 whitened | all rows 563 | 0.451 | 0.395-0.504 | 0.522 | 0.563 | 4 | 1.19e+03 | 1.08 | 1.39 | 1.76 | 1.04 | 1.78 | 0.478 | 0.2 | 0.25 | 0.283 | 0.252-0.313 |
| colour (as built): raw palette_hist, Hellinger | clean 214 | 0.292 | 0.234-0.355 | 0.364 | 0.428 | 26.5 | 743 | 1.41 | 1.95 | 2.52 | 1.37 | 2.31 | 0.294 | 0.148 | 0.177 | 0.214 | 0.179-0.251 |
| colour (as built): raw palette_hist, Hellinger | all primary 274 | 0.325 | 0.268-0.378 | 0.392 | 0.442 | 24 | 843 | 1.39 | 1.98 | 2.64 | 1.39 | 2.48 | 0.332 | 0.172 | 0.209 | 0.241 | 0.206-0.277 |
| colour (as built): raw palette_hist, Hellinger | all rows 563 | 0.25 | 0.210-0.293 | 0.309 | 0.346 | 70 | 1.17e+03 | 1.59 | 2.12 | 2.74 | 1.54 | 2.68 | 0.252 | 0.134 | 0.161 | 0.19 | 0.164-0.216 |
| composition: grid8_an, PCA-128 whitened | clean 214 | 0.953 | 0.925-0.979 | 0.97 | 0.977 | 1 | 1 | 0.394 | 0.555 | 0.801 | 0.386 | 0.77 | 0.981 | 0.582 | 0.677 | 0.709 | 0.682-0.734 |
| composition: grid8_an, PCA-128 whitened | all primary 274 | 0.872 | 0.830-0.909 | 0.887 | 0.894 | 1 | 20 | 0.401 | 0.63 | 1.15 | 0.394 | 0.986 | 0.901 | 0.564 | 0.653 | 0.686 | 0.659-0.712 |
| composition: grid8_an, PCA-128 whitened | all rows 563 | 0.869 | 0.835-0.900 | 0.883 | 0.893 | 1 | 24 | 0.467 | 0.712 | 1.15 | 0.463 | 1.04 | 0.888 | 0.526 | 0.616 | 0.656 | 0.635-0.678 |
| composition (as built): ALL parts, Euclidean | clean 214 | 0.925 | 0.890-0.956 | 0.951 | 0.96 | 1 | 1 | 0.475 | 0.656 | 0.916 | 0.462 | 0.916 | 0.925 | 0.446 | 0.539 | 0.569 | 0.534-0.606 |
| composition (as built): ALL parts, Euclidean | all primary 274 | 0.849 | 0.803-0.889 | 0.883 | 0.896 | 1 | 12.9 | 0.491 | 0.731 | 1.19 | 0.484 | 1.18 | 0.854 | 0.429 | 0.511 | 0.543 | 0.509-0.580 |
| composition (as built): ALL parts, Euclidean | all rows 563 | 0.836 | 0.796-0.872 | 0.877 | 0.886 | 1 | 24 | 0.556 | 0.836 | 1.19 | 0.547 | 1.19 | 0.84 | 0.387 | 0.467 | 0.502 | 0.474-0.534 |

#### H2. Distribution of the margins, clean primary pairs (214)

| variant | ratio | p5 | p25 | p50 | p75 | p90 | p95 | p99 | max | share >= 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| subject: DINOv2-L cls, tile, centred cosine | d(A,B) / d(A, nearest other painting) | 0.119 | 0.22 | 0.321 | 0.425 | 0.537 | 0.633 | 0.88 | 1.2 | 0.00701 |
| subject: DINOv2-L cls, tile, centred cosine | d(A,B) / median pilot NN distance | 0.127 | 0.224 | 0.318 | 0.41 | 0.545 | 0.615 | 1.04 | 1.15 | 0.014 |
| subject (text-trained): SigLIP 2 embed, tile, centred | d(A,B) / d(A, nearest other painting) | 0.213 | 0.343 | 0.444 | 0.562 | 0.693 | 0.762 | 1.04 | 1.19 | 0.0117 |
| subject (text-trained): SigLIP 2 embed, tile, centred | d(A,B) / median pilot NN distance | 0.219 | 0.334 | 0.432 | 0.558 | 0.675 | 0.787 | 0.978 | 1.13 | 0.00935 |
| manner: CSD style, tile, PCA-64 whitened | d(A,B) / d(A, nearest other painting) | 0.288 | 0.47 | 0.608 | 0.768 | 0.921 | 1.04 | 1.39 | 1.9 | 0.0678 |
| manner: CSD style, tile, PCA-64 whitened | d(A,B) / median pilot NN distance | 0.26 | 0.422 | 0.59 | 0.73 | 0.899 | 1.03 | 1.28 | 1.53 | 0.0561 |
| manner (alt.): DINOv2-L gram_late, tile, cosine | d(A,B) / d(A, nearest other painting) | 0.133 | 0.272 | 0.378 | 0.483 | 0.627 | 0.697 | 1.1 | 1.34 | 0.0164 |
| manner (alt.): DINOv2-L gram_late, tile, cosine | d(A,B) / median pilot NN distance | 0.142 | 0.27 | 0.366 | 0.476 | 0.64 | 0.738 | 1.01 | 1.31 | 0.014 |
| colour: std hist+sw, PCA-64 whitened | d(A,B) / d(A, nearest other painting) | 0.369 | 0.662 | 0.955 | 1.29 | 1.52 | 1.7 | 2.19 | 3.15 | 0.453 |
| colour: std hist+sw, PCA-64 whitened | d(A,B) / median pilot NN distance | 0.371 | 0.645 | 0.961 | 1.3 | 1.55 | 1.73 | 2.06 | 3.24 | 0.439 |
| colour (as built): raw palette_hist, Hellinger | d(A,B) / d(A, nearest other painting) | 0.496 | 0.93 | 1.41 | 1.95 | 2.52 | 2.89 | 3.75 | 5.46 | 0.708 |
| colour (as built): raw palette_hist, Hellinger | d(A,B) / median pilot NN distance | 0.575 | 0.941 | 1.37 | 1.85 | 2.31 | 2.51 | 3.01 | 3.15 | 0.706 |
| composition: grid8_an, PCA-128 whitened | d(A,B) / d(A, nearest other painting) | 0.14 | 0.25 | 0.394 | 0.555 | 0.801 | 0.975 | 1.28 | 1.67 | 0.0467 |
| composition: grid8_an, PCA-128 whitened | d(A,B) / median pilot NN distance | 0.14 | 0.255 | 0.386 | 0.55 | 0.77 | 0.9 | 1.23 | 1.38 | 0.0187 |
| composition (as built): ALL parts, Euclidean | d(A,B) / d(A, nearest other painting) | 0.144 | 0.269 | 0.475 | 0.656 | 0.916 | 1.14 | 1.49 | 2.2 | 0.0748 |
| composition (as built): ALL parts, Euclidean | d(A,B) / median pilot NN distance | 0.139 | 0.279 | 0.462 | 0.666 | 0.916 | 1.05 | 1.52 | 1.9 | 0.0748 |

#### C. Colour, raw Euclidean, normalisation x part: R@1 (clean)

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 0.266 | 0.357 | 0.381 | 0.269 | 0.437 |
| L+C+H | 0.241 | 0.311 | 0.227 | 0.227 | 0.327 |
| chroma | 0.035 | 0.0561 | 0.107 | 0.0561 | 0.107 |
| hist+H | 0.311 | 0.311 | 0.371 | 0.278 | 0.388 |
| hist+L+C+H | 0.271 | 0.339 | 0.357 | 0.269 | 0.409 |
| hist+sw | 0.262 | 0.386 | 0.472 | 0.285 | 0.486 |
| hue | 0.21 | 0.194 | 0.178 | 0.194 | 0.178 |
| lightness | 0.0958 | 0.248 | nan | 0.101 | 0.248 |
| palette_hist | 0.287 | 0.386 | 0.47 | 0.292 | 0.47 |
| palette_kmeans | 0.0771 | 0.0911 | 0.0397 | 0.0818 | 0.0701 |
| palette_sw | 0.161 | 0.376 | 0.439 | 0.175 | 0.463 |
| sw+H | 0.278 | 0.322 | 0.339 | 0.262 | 0.336 |

#### C. Colour, raw Euclidean, normalisation x part: R@10 (clean)

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 0.395 | 0.465 | 0.584 | 0.411 | 0.594 |
| L+C+H | 0.362 | 0.432 | 0.376 | 0.381 | 0.493 |
| chroma | 0.101 | 0.129 | 0.245 | 0.129 | 0.245 |
| hist+H | 0.43 | 0.435 | 0.505 | 0.432 | 0.521 |
| hist+L+C+H | 0.393 | 0.456 | 0.547 | 0.406 | 0.577 |
| hist+sw | 0.39 | 0.493 | 0.608 | 0.411 | 0.635 |
| hue | 0.341 | 0.334 | 0.299 | 0.334 | 0.299 |
| lightness | 0.21 | 0.379 | nan | 0.215 | 0.379 |
| palette_hist | 0.411 | 0.481 | 0.619 | 0.428 | 0.647 |
| palette_kmeans | 0.124 | 0.131 | 0.0561 | 0.154 | 0.126 |
| palette_sw | 0.285 | 0.472 | 0.561 | 0.329 | 0.594 |
| sw+H | 0.402 | 0.458 | 0.486 | 0.404 | 0.502 |

#### C. Colour, raw Euclidean, normalisation x part: median d(A,B)/d(A, nearest other) (clean)

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 1.42 | 1.29 | 1.14 | 1.39 | 1.06 |
| L+C+H | 1.49 | 1.37 | 1.48 | 1.45 | 1.2 |
| chroma | 5.22 | 3.63 | 2.23 | 3.63 | 2.23 |
| hist+H | 1.4 | 1.33 | 1.19 | 1.38 | 1.17 |
| hist+L+C+H | 1.41 | 1.29 | 1.16 | 1.38 | 1.09 |
| hist+sw | 1.46 | 1.25 | 1.07 | 1.47 | 1.02 |
| hue | 1.8 | 2.02 | 1.88 | 2.02 | 1.88 |
| lightness | 2.42 | 1.93 | nan | 2.41 | 1.93 |
| palette_hist | 1.36 | 1.27 | 1.06 | 1.41 | 1.04 |
| palette_kmeans | 2.76 | 4.28 | 4.98 | 2.74 | 2.46 |
| palette_sw | 2.1 | 1.38 | 1.15 | 1.86 | 1.06 |
| sw+H | 1.5 | 1.38 | 1.26 | 1.57 | 1.21 |

#### C. Colour, raw Euclidean, normalisation x part: share of pairs under one step (clean)

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 0.285 | 0.355 | 0.379 | 0.28 | 0.439 |
| L+C+H | 0.252 | 0.304 | 0.266 | 0.248 | 0.327 |
| chroma | 0.0421 | 0.0514 | 0.0841 | 0.0514 | 0.0841 |
| hist+H | 0.304 | 0.322 | 0.379 | 0.285 | 0.393 |
| hist+L+C+H | 0.29 | 0.35 | 0.355 | 0.276 | 0.411 |
| hist+sw | 0.271 | 0.379 | 0.439 | 0.257 | 0.486 |
| hue | 0.215 | 0.164 | 0.168 | 0.164 | 0.168 |
| lightness | 0.103 | 0.243 | nan | 0.107 | 0.243 |
| palette_hist | 0.299 | 0.374 | 0.486 | 0.294 | 0.519 |
| palette_kmeans | 0.0841 | 0.0935 | 0.0607 | 0.0888 | 0.0607 |
| palette_sw | 0.173 | 0.355 | 0.402 | 0.196 | 0.43 |
| sw+H | 0.285 | 0.318 | 0.322 | 0.229 | 0.35 |

#### C. Colour, raw Euclidean, normalisation x part: top-10 overlap (clean)

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 0.178 | 0.239 | 0.271 | 0.209 | 0.297 |
| L+C+H | 0.182 | 0.216 | 0.203 | 0.185 | 0.249 |
| chroma | 0.0752 | 0.0977 | 0.167 | 0.0977 | 0.167 |
| hist+H | 0.207 | 0.226 | 0.25 | 0.212 | 0.251 |
| hist+L+C+H | 0.183 | 0.228 | 0.263 | 0.202 | 0.276 |
| hist+sw | 0.194 | 0.277 | 0.312 | 0.207 | 0.322 |
| hue | 0.178 | 0.186 | 0.169 | 0.186 | 0.169 |
| lightness | 0.136 | 0.254 | nan | 0.14 | 0.254 |
| palette_hist | 0.198 | 0.256 | 0.295 | 0.214 | 0.304 |
| palette_kmeans | 0.0925 | 0.0939 | 0.0519 | 0.101 | 0.0963 |
| palette_sw | 0.158 | 0.279 | 0.294 | 0.185 | 0.329 |
| sw+H | 0.201 | 0.229 | 0.249 | 0.206 | 0.268 |

#### C. Colour, raw Euclidean, normalisation x part: R@1 (all primary)

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 0.301 | 0.376 | 0.394 | 0.303 | 0.44 |
| L+C+H | 0.276 | 0.336 | 0.257 | 0.266 | 0.348 |
| chroma | 0.073 | 0.0821 | 0.139 | 0.0821 | 0.139 |
| hist+H | 0.332 | 0.33 | 0.385 | 0.31 | 0.396 |
| hist+L+C+H | 0.305 | 0.359 | 0.374 | 0.301 | 0.418 |
| hist+sw | 0.305 | 0.402 | 0.467 | 0.319 | 0.482 |
| hue | 0.235 | 0.219 | 0.203 | 0.219 | 0.203 |
| lightness | 0.141 | 0.266 | nan | 0.144 | 0.266 |
| palette_hist | 0.321 | 0.392 | 0.465 | 0.325 | 0.467 |
| palette_kmeans | 0.0876 | 0.0931 | 0.0401 | 0.0967 | 0.073 |
| palette_sw | 0.208 | 0.389 | 0.44 | 0.219 | 0.464 |
| sw+H | 0.297 | 0.338 | 0.359 | 0.292 | 0.352 |

#### C. Colour, raw Euclidean, normalisation x part: participation ratio on pilot

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 5.95 | 8.64 | 11.2 | 6.5 | 11 |
| L+C+H | 6.61 | 8.84 | 6.78 | 8.35 | 9.44 |
| chroma | 1.87 | 2.95 | 2.94 | 2.95 | 2.94 |
| hist+H | 10.4 | 9.2 | 11.8 | 9.8 | 12.1 |
| hist+L+C+H | 7.46 | 9.43 | 10.2 | 8.79 | 11.6 |
| hist+sw | 2.92 | 6.7 | 8.74 | 3.31 | 9.33 |
| hue | 6.97 | 6.43 | 5.79 | 6.43 | 5.79 |
| lightness | 3.45 | 3.5 | nan | 3.41 | 3.5 |
| palette_hist | 5.89 | 8.78 | 13.5 | 7.29 | 14.1 |
| palette_kmeans | 4.6 | 3.81 | 3.61 | 4.62 | 5.5 |
| palette_sw | 1.54 | 4.37 | 5.46 | 1.62 | 5.82 |
| sw+H | 4.86 | 7.97 | 9.7 | 4.67 | 10.1 |

#### C. Colour, raw Euclidean, normalisation x part: TwoNN intrinsic dimension on pilot

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 12.1 | 12.2 | 14.5 | 11.7 | 14.7 |
| L+C+H | 12.3 | 11.8 | 11.7 | 11.9 | 12.7 |
| chroma | 4.85 | 5.06 | 7.52 | 5.06 | 7.52 |
| hist+H | 11.7 | 11.8 | 14.7 | 11.9 | 14.8 |
| hist+L+C+H | 12.5 | 12.4 | 14.8 | 12.1 | 14.6 |
| hist+sw | 11.2 | 11.7 | 14.5 | 10.9 | 14.7 |
| hue | 9.87 | 7.7 | 9.97 | 7.7 | 9.97 |
| lightness | 7.39 | 7.33 | nan | 7.18 | 7.33 |
| palette_hist | 12 | 11.7 | 16 | 11.3 | 15.3 |
| palette_kmeans | 6.91 | 5.91 | 4.97 | 7.24 | 7.49 |
| palette_sw | 8.81 | 10.4 | 11.9 | 8.91 | 12.1 |
| sw+H | 10.3 | 11 | 12.6 | 9.89 | 12.8 |

#### C. Colour, raw Euclidean, normalisation x part: AUC: colour-different versions further apart than clean repro pairs

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 0.761 | 0.822 | 0.808 | 0.798 | 0.81 |
| L+C+H | 0.731 | 0.789 | 0.75 | 0.77 | 0.777 |
| chroma | 0.725 | 0.755 | 0.704 | 0.755 | 0.704 |
| hist+H | 0.753 | 0.798 | 0.809 | 0.786 | 0.809 |
| hist+L+C+H | 0.75 | 0.81 | 0.797 | 0.788 | 0.803 |
| hist+sw | 0.796 | 0.861 | 0.843 | 0.836 | 0.845 |
| hue | 0.704 | 0.731 | 0.743 | 0.731 | 0.743 |
| lightness | 0.671 | 0.771 | nan | 0.672 | 0.771 |
| palette_hist | 0.801 | 0.854 | 0.851 | 0.838 | 0.855 |
| palette_kmeans | 0.643 | 0.55 | 0.591 | 0.624 | 0.581 |
| palette_sw | 0.768 | 0.861 | 0.83 | 0.794 | 0.83 |
| sw+H | 0.741 | 0.801 | 0.796 | 0.773 | 0.793 |

#### C. Colour, raw Euclidean, normalisation x part: median version-pair distance in steps

| part | greyworld | lstd | rank | raw | std |
|---|---|---|---|---|---|
| ALL5 | 1.9 | 1.79 | 1.6 | 1.9 | 1.49 |
| L+C+H | 1.87 | 1.86 | 1.97 | 1.93 | 1.7 |
| chroma | 6.95 | 5.26 | 3.43 | 5.26 | 3.43 |
| hist+H | 1.79 | 1.96 | 1.6 | 1.92 | 1.56 |
| hist+L+C+H | 1.79 | 1.78 | 1.59 | 1.84 | 1.52 |
| hist+sw | 2.11 | 1.84 | 1.61 | 2.08 | 1.48 |
| hue | 2.32 | 2.91 | 2.5 | 2.91 | 2.5 |
| lightness | 3.37 | 3.16 | nan | 3.32 | 3.16 |
| palette_hist | 1.95 | 1.79 | 1.5 | 1.86 | 1.42 |
| palette_kmeans | 3.1 | 4.66 | 5.66 | 2.78 | 2.58 |
| palette_sw | 3.07 | 2.05 | 1.84 | 2.75 | 1.69 |
| sw+H | 1.97 | 1.93 | 1.76 | 2.15 | 1.65 |

#### C. Colour: mean over all colour features, by treatment

| treat | n variants | clean_r1 | clean_r10 | clean_rnn_med | clean_rstep_lt1 | clean_ov10 | clean_rbo | twonn | auc_colver_vs_repro |
|---|---|---|---|---|---|---|---|---|---|
| cen | 67 | 0.294 | 0.419 | 1.68 | 0.304 | 0.206 | 0.175 | 11.2 | 0.784 |
| cos | 67 | 0.287 | 0.413 | 1.7 | 0.286 | 0.215 | 0.183 | 11.2 | 0.77 |
| euc | 67 | 0.283 | 0.409 | 1.71 | 0.282 | 0.213 | 0.181 | 11.2 | 0.774 |
| hist_circ_emd | 5 | 0.123 | 0.252 | 3.04 | 0.117 | 0.154 | 0.125 | 6.54 | 0.724 |
| hist_emd | 9 | 0.0955 | 0.186 | 4.73 | 0.0862 | 0.133 | 0.108 | 5.06 | 0.752 |
| hist_hellinger | 14 | 0.14 | 0.248 | 2.55 | 0.131 | 0.162 | 0.133 | 7.41 | 0.728 |
| pca128 | 43 | 0.353 | 0.49 | 1.28 | 0.353 | 0.245 | 0.21 | 12.5 | 0.811 |
| pca128w | 43 | 0.425 | 0.53 | 1.08 | 0.446 | 0.285 | 0.245 | 23.1 | 0.777 |
| pca32 | 48 | 0.322 | 0.467 | 1.35 | 0.322 | 0.236 | 0.202 | 11.1 | 0.802 |
| pca32w | 48 | 0.385 | 0.522 | 1.17 | 0.395 | 0.258 | 0.223 | 13.8 | 0.783 |
| pca64 | 47 | 0.341 | 0.48 | 1.31 | 0.342 | 0.241 | 0.206 | 12 | 0.806 |
| pca64w | 47 | 0.416 | 0.536 | 1.11 | 0.433 | 0.273 | 0.237 | 17.9 | 0.772 |
| plain_euc | 5 | 0.289 | 0.429 | 1.5 | 0.286 | 0.231 | 0.195 | 10.3 | 0.789 |
| sinkhorn_emd | 5 | 0.184 | 0.325 | 1.65 | 0.164 | 0.144 | 0.114 | 10.5 | 0.8 |
| summary5 | 9 | 0.0561 | 0.142 | 6.27 | 0.0473 | 0.113 | 0.0909 | 3.9 | 0.715 |
| tv_l1 | 5 | 0.355 | 0.496 | 1.31 | 0.354 | 0.234 | 0.196 | 11.3 | 0.845 |
| zs | 67 | 0.281 | 0.41 | 1.54 | 0.278 | 0.221 | 0.186 | 12 | 0.769 |

#### C. Colour: R@1 (clean) by treatment for the main parts

| store | part | cen | cos | euc | pca128 | pca128w | pca32 | pca32w | pca64 | pca64w | plain_euc | tv_l1 | zs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| colour__rank | ALL5 | 0.425 | 0.381 | 0.381 | 0.376 | 0.498 | 0.341 | 0.411 | 0.369 | 0.474 | nan | nan | 0.435 |
| colour__rank | hist+sw | 0.474 | 0.47 | 0.472 | 0.467 | 0.54 | 0.421 | 0.507 | 0.449 | 0.53 | nan | nan | 0.435 |
| colour__rank | palette_hist | 0.488 | 0.47 | 0.47 | 0.474 | 0.484 | 0.437 | 0.481 | 0.47 | 0.502 | 0.386 | 0.46 | 0.406 |
| colour__rank | palette_sw | 0.435 | 0.444 | 0.439 | 0.439 | 0.5 | 0.406 | 0.521 | 0.428 | 0.526 | nan | nan | 0.425 |
| colour__raw | ALL5 | 0.283 | 0.271 | 0.269 | 0.269 | 0.322 | 0.245 | 0.29 | 0.259 | 0.292 | nan | nan | 0.252 |
| colour__raw | hist+sw | 0.301 | 0.301 | 0.285 | 0.285 | 0.381 | 0.264 | 0.348 | 0.28 | 0.353 | nan | nan | 0.234 |
| colour__raw | palette_hist | 0.285 | 0.292 | 0.292 | 0.292 | 0.213 | 0.29 | 0.325 | 0.292 | 0.29 | 0.196 | 0.241 | 0.208 |
| colour__raw | palette_sw | 0.292 | 0.269 | 0.175 | 0.173 | 0.477 | 0.173 | 0.486 | 0.173 | 0.491 | nan | nan | 0.238 |
| colour__std | ALL5 | 0.47 | 0.437 | 0.437 | 0.43 | 0.474 | 0.383 | 0.439 | 0.418 | 0.465 | nan | nan | 0.451 |
| colour__std | hist+sw | 0.512 | 0.491 | 0.486 | 0.486 | 0.514 | 0.467 | 0.526 | 0.488 | 0.547 | nan | nan | 0.444 |
| colour__std | palette_hist | 0.493 | 0.47 | 0.47 | 0.467 | 0.451 | 0.446 | 0.488 | 0.46 | 0.495 | 0.4 | 0.481 | 0.4 |
| colour__std | palette_sw | 0.484 | 0.465 | 0.463 | 0.463 | 0.505 | 0.444 | 0.502 | 0.463 | 0.542 | nan | nan | 0.453 |

#### C. Colour: top-10 overlap (clean) by treatment for the main parts

| store | part | cen | cos | euc | pca128 | pca128w | pca32 | pca32w | pca64 | pca64w | plain_euc | tv_l1 | zs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| colour__rank | ALL5 | 0.251 | 0.271 | 0.271 | 0.269 | 0.312 | 0.264 | 0.275 | 0.271 | 0.292 | nan | nan | 0.299 |
| colour__rank | hist+sw | 0.286 | 0.314 | 0.312 | 0.309 | 0.336 | 0.311 | 0.324 | 0.306 | 0.315 | nan | nan | 0.302 |
| colour__rank | palette_hist | 0.282 | 0.295 | 0.295 | 0.291 | 0.315 | 0.286 | 0.284 | 0.298 | 0.286 | 0.282 | 0.279 | 0.288 |
| colour__rank | palette_sw | 0.298 | 0.297 | 0.294 | 0.295 | 0.345 | 0.294 | 0.333 | 0.295 | 0.328 | nan | nan | 0.299 |
| colour__raw | ALL5 | 0.206 | 0.208 | 0.209 | 0.209 | 0.254 | 0.204 | 0.209 | 0.208 | 0.241 | nan | nan | 0.199 |
| colour__raw | hist+sw | 0.204 | 0.221 | 0.207 | 0.207 | 0.254 | 0.198 | 0.228 | 0.204 | 0.253 | nan | nan | 0.191 |
| colour__raw | palette_hist | 0.2 | 0.214 | 0.214 | 0.214 | 0.183 | 0.214 | 0.215 | 0.213 | 0.217 | 0.171 | 0.189 | 0.174 |
| colour__raw | palette_sw | 0.222 | 0.22 | 0.185 | 0.185 | 0.329 | 0.186 | 0.31 | 0.185 | 0.327 | nan | nan | 0.193 |
| colour__std | ALL5 | 0.284 | 0.296 | 0.297 | 0.293 | 0.31 | 0.285 | 0.287 | 0.296 | 0.3 | nan | nan | 0.315 |
| colour__std | hist+sw | 0.314 | 0.323 | 0.322 | 0.319 | 0.316 | 0.318 | 0.322 | 0.318 | 0.32 | nan | nan | 0.32 |
| colour__std | palette_hist | 0.296 | 0.304 | 0.304 | 0.303 | 0.294 | 0.308 | 0.302 | 0.304 | 0.301 | 0.311 | 0.296 | 0.284 |
| colour__std | palette_sw | 0.324 | 0.33 | 0.329 | 0.329 | 0.352 | 0.325 | 0.356 | 0.328 | 0.337 | nan | nan | 0.316 |

#### C. Histogram distances (raw and std normalisation)

euc on a stored part is Hellinger for the square-rooted histograms; tv_l1 and plain_euc undo the square root; hist_emd is 1-D Wasserstein on the 16 bins; hist_circ_emd is circular; sinkhorn_emd is the entropic approximation of the palette EMD; palette_sw is itself a sliced-Wasserstein embedding.

| store | part | treat | clean_r1 | clean_r10 | clean_rnn_med | clean_ov10 | twonn | auc_colver_vs_repro |
|---|---|---|---|---|---|---|---|---|
| colour__raw | chroma | euc | 0.0561 | 0.129 | 3.63 | 0.0977 | 5.06 | 0.755 |
| colour__raw | chroma | hist_emd | 0.0374 | 0.0864 | 6.52 | 0.0692 | 4.05 | 0.778 |
| colour__raw | chroma | hist_hellinger | 0.0537 | 0.129 | 3.63 | 0.0972 | 4.98 | 0.755 |
| colour__raw | chroma | summary5 | 0.035 | 0.0724 | 7.05 | 0.0715 | 3.96 | 0.772 |
| colour__raw | hue | euc | 0.194 | 0.334 | 2.02 | 0.186 | 7.7 | 0.731 |
| colour__raw | hue | hist_circ_emd | 0.129 | 0.252 | 3.61 | 0.16 | 5.51 | 0.713 |
| colour__raw | hue | hist_hellinger | 0.194 | 0.283 | 2.19 | 0.183 | 7.43 | 0.733 |
| colour__raw | lightness | euc | 0.101 | 0.215 | 2.41 | 0.14 | 7.18 | 0.672 |
| colour__raw | lightness | hist_emd | 0.0794 | 0.159 | 3.64 | 0.122 | 5.35 | 0.725 |
| colour__raw | lightness | hist_hellinger | 0.107 | 0.222 | 2.32 | 0.146 | 7.45 | 0.67 |
| colour__raw | lightness | summary5 | 0.0607 | 0.152 | 5.37 | 0.118 | 4.07 | 0.675 |
| colour__raw | palette_hist | euc | 0.292 | 0.428 | 1.41 | 0.214 | 11.3 | 0.838 |
| colour__raw | palette_hist | plain_euc | 0.196 | 0.332 | 1.75 | 0.171 | 8.42 | 0.778 |
| colour__raw | palette_hist | tv_l1 | 0.241 | 0.386 | 1.5 | 0.189 | 9.26 | 0.847 |
| colour__raw | palette_kmeans | euc | 0.0818 | 0.154 | 2.74 | 0.101 | 7.24 | 0.624 |
| colour__raw | palette_kmeans | sinkhorn_emd | 0.157 | 0.325 | 1.69 | 0.155 | 10.4 | 0.799 |
| colour__raw | palette_sw | euc | 0.175 | 0.329 | 1.86 | 0.185 | 8.91 | 0.794 |
| colour__std | chroma | euc | 0.107 | 0.245 | 2.23 | 0.167 | 7.52 | 0.704 |
| colour__std | chroma | hist_emd | 0.0864 | 0.222 | 3.12 | 0.144 | 5.59 | 0.708 |
| colour__std | chroma | hist_hellinger | 0.105 | 0.243 | 2.23 | 0.168 | 7.54 | 0.705 |
| colour__std | chroma | summary5 | 0.035 | 0.138 | 6.15 | 0.112 | 3.87 | 0.659 |
| colour__std | hue | euc | 0.178 | 0.299 | 1.88 | 0.169 | 9.97 | 0.743 |
| colour__std | hue | hist_circ_emd | 0.117 | 0.238 | 2.69 | 0.147 | 7.43 | 0.763 |
| colour__std | hue | hist_hellinger | 0.168 | 0.273 | 1.98 | 0.163 | 9.67 | 0.744 |
| colour__std | lightness | euc | 0.248 | 0.379 | 1.93 | 0.254 | 7.33 | 0.771 |
| colour__std | lightness | hist_emd | 0.213 | 0.327 | 2.37 | 0.227 | 6.02 | 0.805 |
| colour__std | lightness | hist_hellinger | 0.238 | 0.379 | 1.93 | 0.252 | 7.34 | 0.774 |
| colour__std | lightness | summary5 | 0.121 | 0.243 | 4.97 | 0.186 | 3.62 | 0.754 |
| colour__std | palette_hist | euc | 0.47 | 0.647 | 1.04 | 0.304 | 15.3 | 0.855 |
| colour__std | palette_hist | plain_euc | 0.4 | 0.556 | 1.14 | 0.311 | 12.3 | 0.798 |
| colour__std | palette_hist | tv_l1 | 0.481 | 0.624 | 1.03 | 0.296 | 13.6 | 0.856 |
| colour__std | palette_kmeans | euc | 0.0701 | 0.126 | 2.46 | 0.0963 | 7.49 | 0.581 |
| colour__std | palette_kmeans | sinkhorn_emd | 0.313 | 0.484 | 1.25 | 0.182 | 12.2 | 0.864 |
| colour__std | palette_sw | euc | 0.463 | 0.594 | 1.06 | 0.329 | 12.1 | 0.83 |

#### C. Cross-normalisation combinations

| part | treat | dim | clean_r1 | clean_r10 | clean_rnn_med | clean_ov10 | twonn | auc_colver_vs_repro |
|---|---|---|---|---|---|---|---|---|
| hist[raw+std] | euc | 972 | 0.474 | 0.586 | 1.04 | 0.283 | 15.4 | 0.866 |
| hist[raw+std] | pca64w | 64 | 0.491 | 0.633 | 1.01 | 0.297 | 17.9 | 0.832 |
| hist[greyworld+lstd] | euc | 972 | 0.374 | 0.486 | 1.25 | 0.245 | 12.4 | 0.844 |
| hist[greyworld+lstd] | pca64w | 64 | 0.423 | 0.521 | 1.13 | 0.265 | 16.4 | 0.79 |
| hist[greyworld+std] | euc | 972 | 0.453 | 0.572 | 1.07 | 0.276 | 15.3 | 0.849 |
| hist[greyworld+std] | pca64w | 64 | 0.493 | 0.608 | 1.01 | 0.29 | 18 | 0.821 |
| hist[all5] | euc | 2430 | 0.463 | 0.572 | 1.06 | 0.276 | 15.3 | 0.863 |
| hist[all5] | pca64w | 64 | 0.488 | 0.631 | 1.01 | 0.298 | 17.2 | 0.831 |
| sw[greyworld+std] | euc | 768 | 0.395 | 0.556 | 1.19 | 0.277 | 12.4 | 0.822 |
| sw[greyworld+std] | pca64w | 64 | 0.509 | 0.628 | 0.979 | 0.316 | 18.5 | 0.783 |
| hist[std]+sw[std]+hue[greyworld] | euc | 895 | 0.409 | 0.558 | 1.12 | 0.279 | 14.9 | 0.799 |
| hist[std]+sw[std]+hue[greyworld] | pca64w | 64 | 0.467 | 0.61 | 1.04 | 0.299 | 18.4 | 0.804 |
| hist[std]+L[raw]+C[raw] | euc | 528 | 0.36 | 0.502 | 1.18 | 0.214 | 15.1 | 0.814 |
| hist[std]+L[raw]+C[raw] | pca64w | 64 | 0.465 | 0.586 | 1.04 | 0.275 | 18.7 | 0.765 |
| hist[std]+L[greyworld]+C[greyworld]+H[greyworld] | euc | 553 | 0.348 | 0.502 | 1.2 | 0.217 | 14.9 | 0.777 |
| hist[std]+L[greyworld]+C[greyworld]+H[greyworld] | pca64w | 64 | 0.449 | 0.547 | 1.08 | 0.26 | 19.5 | 0.768 |

#### C. The twelve most photograph-proof colour variants (by clean R@1, of 596)

| store | part | treat | dim | clean_r1 | clean_r10 | clean_rank_med | clean_rnn_med | clean_rnn_p90 | clean_rstep_lt1 | clean_ov10 | clean_rbo | twonn | auc_colver_vs_repro |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| colour__std | hist+sw | pca64w | 64 | 0.547 | 0.647 | 1 | 0.956 | 1.52 | 0.561 | 0.32 | 0.281 | 17.2 | 0.825 |
| colour__std | palette_sw | pca64w | 64 | 0.542 | 0.652 | 1 | 0.954 | 1.69 | 0.533 | 0.337 | 0.297 | 18.1 | 0.794 |
| colour__rank | hist+sw | pca128w | 128 | 0.54 | 0.656 | 1 | 0.96 | 1.4 | 0.57 | 0.336 | 0.285 | 23.4 | 0.857 |
| colour__rank | hist+sw | pca64w | 64 | 0.53 | 0.659 | 1 | 0.964 | 1.55 | 0.542 | 0.315 | 0.289 | 18.3 | 0.854 |
| colour__rank | palette_sw | pca64w | 64 | 0.526 | 0.661 | 1 | 0.966 | 1.55 | 0.528 | 0.328 | 0.29 | 17.4 | 0.846 |
| colour__std | hist+sw | pca32w | 32 | 0.526 | 0.666 | 1 | 0.969 | 1.72 | 0.528 | 0.322 | 0.28 | 13.7 | 0.847 |
| colour__rank | palette_sw | pca32w | 32 | 0.521 | 0.673 | 1 | 0.988 | 1.76 | 0.523 | 0.333 | 0.294 | 13.7 | 0.855 |
| colour__std | hist+sw | pca128w | 128 | 0.514 | 0.638 | 1 | 0.972 | 1.46 | 0.533 | 0.316 | 0.271 | 22.6 | 0.827 |
| colour__cross | sw[greyworld+std] | pca128w | 128 | 0.514 | 0.598 | 1 | 0.99 | 1.53 | 0.542 | 0.336 | 0.292 | 24.4 | 0.793 |
| colour__lstd | palette_sw | pca64w | 64 | 0.514 | 0.619 | 1 | 0.982 | 1.79 | 0.519 | 0.338 | 0.295 | 18 | 0.791 |
| colour__std | hist+sw | cen | 870 | 0.512 | 0.652 | 1 | 0.985 | 1.78 | 0.547 | 0.314 | 0.266 | 14.5 | 0.871 |
| colour__cross | sw[greyworld+std] | pca64w | 64 | 0.509 | 0.628 | 1 | 0.979 | 1.7 | 0.514 | 0.316 | 0.278 | 18.5 | 0.783 |

#### K. Composition, part x treatment: R@1 (clean)

| part | cen | euc | pca128w | pca64w | zs |
|---|---|---|---|---|---|
| ALL | 0.928 | 0.925 | 0.956 | 0.935 | 0.944 |
| ALL-aspect | 0.928 | 0.925 | 0.956 | 0.932 | 0.944 |
| aspect | nan | 0.236 | nan | nan | nan |
| balance | 0.435 | 0.467 | nan | nan | 0.472 |
| edges | 0.451 | 0.437 | nan | nan | 0.57 |
| globals | 0.858 | 0.851 | nan | 0.93 | 0.939 |
| globals-saliency | 0.755 | 0.759 | nan | nan | 0.773 |
| grid4_an | 0.888 | 0.881 | nan | nan | 0.897 |
| grid4_an[C] | 0.619 | 0.622 | nan | nan | 0.626 |
| grid4_an[E] | 0.853 | 0.799 | nan | nan | 0.797 |
| grid4_an[L] | 0.832 | 0.839 | nan | nan | 0.848 |
| grid4_ap | 0.874 | 0.867 | nan | nan | 0.878 |
| grid4_ap[C] | 0.619 | 0.628 | nan | nan | 0.626 |
| grid4_ap[E] | 0.799 | 0.773 | nan | nan | 0.762 |
| grid4_ap[L] | 0.808 | 0.822 | nan | nan | 0.822 |
| grid8_an | 0.937 | 0.928 | 0.953 | 0.932 | 0.937 |
| grid8_an+ap | 0.944 | 0.944 | 0.96 | 0.93 | 0.935 |
| grid8_an+aspect | 0.939 | 0.953 | 0.96 | 0.939 | 0.939 |
| grid8_an+globals | 0.906 | 0.902 | 0.958 | 0.937 | 0.951 |
| grid8_an+globals+aspect | 0.916 | 0.916 | 0.958 | 0.939 | 0.951 |
| grid8_an+saliency | 0.96 | 0.958 | 0.965 | 0.96 | 0.953 |
| grid8_an[C] | 0.82 | 0.806 | nan | nan | 0.804 |
| grid8_an[E] | 0.914 | 0.895 | nan | nan | 0.888 |
| grid8_an[L] | 0.911 | 0.914 | nan | nan | 0.911 |
| grid8_ap | 0.939 | 0.925 | 0.928 | 0.925 | 0.914 |
| grid8_ap+globals | 0.909 | 0.902 | 0.946 | 0.932 | 0.942 |
| grid8_ap[C] | 0.832 | 0.804 | nan | nan | 0.778 |
| grid8_ap[E] | 0.899 | 0.883 | nan | nan | 0.834 |
| grid8_ap[L] | 0.925 | 0.918 | nan | nan | 0.902 |
| grids_an | 0.923 | 0.911 | 0.958 | 0.935 | 0.935 |
| grids_ap | 0.925 | 0.918 | 0.928 | 0.928 | 0.909 |
| saliency | 0.942 | 0.944 | nan | 0.951 | 0.951 |
| spectrum | 0.0911 | 0.259 | nan | nan | 0.236 |
| symmetry | 0.243 | 0.341 | nan | nan | 0.332 |

#### K. Composition, part x treatment: top-10 overlap (clean)

| part | cen | euc | pca128w | pca64w | zs |
|---|---|---|---|---|---|
| ALL | 0.566 | 0.569 | 0.628 | 0.565 | 0.603 |
| ALL-aspect | 0.54 | 0.551 | 0.626 | 0.57 | 0.606 |
| aspect | nan | 0.331 | nan | nan | nan |
| balance | 0.364 | 0.39 | nan | nan | 0.387 |
| edges | 0.382 | 0.393 | nan | nan | 0.466 |
| globals | 0.521 | 0.513 | nan | 0.549 | 0.576 |
| globals-saliency | 0.497 | 0.504 | nan | nan | 0.48 |
| grid4_an | 0.536 | 0.549 | nan | nan | 0.548 |
| grid4_an[C] | 0.428 | 0.417 | nan | nan | 0.42 |
| grid4_an[E] | 0.564 | 0.546 | nan | nan | 0.535 |
| grid4_an[L] | 0.583 | 0.582 | nan | nan | 0.584 |
| grid4_ap | 0.543 | 0.543 | nan | nan | 0.539 |
| grid4_ap[C] | 0.418 | 0.423 | nan | nan | 0.415 |
| grid4_ap[E] | 0.536 | 0.532 | nan | nan | 0.532 |
| grid4_ap[L] | 0.571 | 0.583 | nan | nan | 0.581 |
| grid8_an | 0.536 | 0.569 | 0.709 | 0.607 | 0.568 |
| grid8_an+ap | 0.562 | 0.597 | 0.717 | 0.642 | 0.602 |
| grid8_an+aspect | 0.59 | 0.628 | 0.716 | 0.623 | 0.571 |
| grid8_an+globals | 0.531 | 0.528 | 0.599 | 0.549 | 0.57 |
| grid8_an+globals+aspect | 0.553 | 0.556 | 0.595 | 0.549 | 0.569 |
| grid8_an+saliency | 0.596 | 0.605 | 0.678 | 0.616 | 0.609 |
| grid8_an[C] | 0.435 | 0.464 | nan | nan | 0.46 |
| grid8_an[E] | 0.554 | 0.578 | nan | nan | 0.558 |
| grid8_an[L] | 0.583 | 0.613 | nan | nan | 0.613 |
| grid8_ap | 0.567 | 0.61 | 0.769 | 0.647 | 0.601 |
| grid8_ap+globals | 0.529 | 0.526 | 0.62 | 0.566 | 0.63 |
| grid8_ap[C] | 0.473 | 0.464 | nan | nan | 0.479 |
| grid8_ap[E] | 0.593 | 0.596 | nan | nan | 0.583 |
| grid8_ap[L] | 0.633 | 0.642 | nan | nan | 0.61 |
| grids_an | 0.526 | 0.557 | 0.715 | 0.609 | 0.568 |
| grids_ap | 0.555 | 0.571 | 0.768 | 0.629 | 0.592 |
| saliency | 0.585 | 0.598 | nan | 0.604 | 0.611 |
| spectrum | 0.25 | 0.462 | nan | nan | 0.458 |
| symmetry | 0.292 | 0.327 | nan | nan | 0.326 |

#### K. Composition, part x treatment: median d(A,B)/d(A, nearest other) (clean)

| part | cen | euc | pca128w | pca64w | zs |
|---|---|---|---|---|---|
| ALL | 0.471 | 0.475 | 0.444 | 0.468 | 0.456 |
| ALL-aspect | 0.473 | 0.494 | 0.441 | 0.473 | 0.457 |
| aspect | nan | 7.94e+09 | nan | nan | nan |
| balance | 1.17 | 1.1 | nan | nan | 1.06 |
| edges | 1.16 | 1.15 | nan | nan | 0.881 |
| globals | 0.56 | 0.555 | nan | 0.47 | 0.41 |
| globals-saliency | 0.676 | 0.675 | nan | nan | 0.658 |
| grid4_an | 0.473 | 0.508 | nan | nan | 0.492 |
| grid4_an[C] | 0.741 | 0.759 | nan | nan | 0.754 |
| grid4_an[E] | 0.476 | 0.525 | nan | nan | 0.533 |
| grid4_an[L] | 0.456 | 0.45 | nan | nan | 0.447 |
| grid4_ap | 0.497 | 0.509 | nan | nan | 0.528 |
| grid4_ap[C] | 0.807 | 0.795 | nan | nan | 0.784 |
| grid4_ap[E] | 0.499 | 0.551 | nan | nan | 0.546 |
| grid4_ap[L] | 0.479 | 0.463 | nan | nan | 0.467 |
| grid8_an | 0.411 | 0.426 | 0.394 | 0.421 | 0.44 |
| grid8_an+ap | 0.413 | 0.423 | 0.395 | 0.43 | 0.455 |
| grid8_an+aspect | 0.415 | 0.405 | 0.39 | 0.413 | 0.436 |
| grid8_an+globals | 0.517 | 0.513 | 0.441 | 0.456 | 0.425 |
| grid8_an+globals+aspect | 0.504 | 0.493 | 0.442 | 0.453 | 0.425 |
| grid8_an+saliency | 0.384 | 0.402 | 0.4 | 0.401 | 0.417 |
| grid8_an[C] | 0.553 | 0.564 | nan | nan | 0.57 |
| grid8_an[E] | 0.342 | 0.397 | nan | nan | 0.409 |
| grid8_an[L] | 0.348 | 0.355 | nan | nan | 0.356 |
| grid8_ap | 0.418 | 0.435 | 0.433 | 0.439 | 0.489 |
| grid8_ap+globals | 0.516 | 0.511 | 0.456 | 0.467 | 0.458 |
| grid8_ap[C] | 0.54 | 0.559 | nan | nan | 0.576 |
| grid8_ap[E] | 0.347 | 0.4 | nan | nan | 0.428 |
| grid8_ap[L] | 0.336 | 0.344 | nan | nan | 0.365 |
| grids_an | 0.431 | 0.453 | 0.394 | 0.423 | 0.448 |
| grids_ap | 0.441 | 0.451 | 0.435 | 0.452 | 0.486 |
| saliency | 0.39 | 0.41 | nan | 0.434 | 0.394 |
| spectrum | 8.67 | 1.97 | nan | nan | 2.07 |
| symmetry | 1.92 | 1.52 | nan | nan | 1.53 |

#### K. Composition, part x treatment: R@1 (all primary)

| part | cen | euc | pca128w | pca64w | zs |
|---|---|---|---|---|---|
| ALL | 0.85 | 0.849 | 0.878 | 0.861 | 0.863 |
| ALL-aspect | 0.847 | 0.849 | 0.88 | 0.86 | 0.863 |
| aspect | nan | 0.246 | nan | nan | nan |
| balance | 0.431 | 0.464 | nan | nan | 0.458 |
| edges | 0.431 | 0.416 | nan | nan | 0.527 |
| globals | 0.79 | 0.781 | nan | 0.854 | 0.861 |
| globals-saliency | 0.697 | 0.699 | nan | nan | 0.703 |
| grid4_an | 0.81 | 0.803 | nan | nan | 0.814 |
| grid4_an[C] | 0.593 | 0.597 | nan | nan | 0.6 |
| grid4_an[E] | 0.774 | 0.726 | nan | nan | 0.726 |
| grid4_an[L] | 0.766 | 0.768 | nan | nan | 0.775 |
| grid4_ap | 0.803 | 0.792 | nan | nan | 0.803 |
| grid4_ap[C] | 0.6 | 0.604 | nan | nan | 0.599 |
| grid4_ap[E] | 0.734 | 0.708 | nan | nan | 0.697 |
| grid4_ap[L] | 0.752 | 0.759 | nan | nan | 0.757 |
| grid8_an | 0.85 | 0.841 | 0.872 | 0.852 | 0.854 |
| grid8_an+ap | 0.856 | 0.856 | 0.876 | 0.85 | 0.849 |
| grid8_an+aspect | 0.856 | 0.867 | 0.878 | 0.858 | 0.856 |
| grid8_an+globals | 0.829 | 0.829 | 0.878 | 0.861 | 0.876 |
| grid8_an+globals+aspect | 0.839 | 0.843 | 0.88 | 0.865 | 0.876 |
| grid8_an+saliency | 0.88 | 0.874 | 0.88 | 0.876 | 0.874 |
| grid8_an[C] | 0.755 | 0.745 | nan | nan | 0.743 |
| grid8_an[E] | 0.841 | 0.823 | nan | nan | 0.818 |
| grid8_an[L] | 0.83 | 0.834 | nan | nan | 0.832 |
| grid8_ap | 0.856 | 0.838 | 0.849 | 0.847 | 0.83 |
| grid8_ap+globals | 0.834 | 0.829 | 0.87 | 0.86 | 0.865 |
| grid8_ap[C] | 0.765 | 0.743 | nan | nan | 0.719 |
| grid8_ap[E] | 0.832 | 0.816 | nan | nan | 0.766 |
| grid8_ap[L] | 0.845 | 0.838 | nan | nan | 0.825 |
| grids_an | 0.836 | 0.829 | 0.876 | 0.856 | 0.85 |
| grids_ap | 0.843 | 0.832 | 0.847 | 0.847 | 0.829 |
| saliency | 0.863 | 0.861 | nan | 0.869 | 0.867 |
| spectrum | 0.0803 | 0.256 | nan | nan | 0.235 |
| symmetry | 0.259 | 0.348 | nan | nan | 0.339 |

#### K. Composition, part x treatment: AUC versions vs repro

| part | cen | euc | pca128w | pca64w | zs |
|---|---|---|---|---|---|
| ALL | 0.856 | 0.837 | 0.859 | 0.838 | 0.855 |
| ALL-aspect | 0.854 | 0.837 | 0.86 | 0.839 | 0.855 |
| aspect | nan | 0.75 | nan | nan | nan |
| balance | 0.778 | 0.776 | nan | nan | 0.758 |
| edges | 0.71 | 0.662 | nan | nan | 0.668 |
| globals | 0.832 | 0.801 | nan | 0.835 | 0.847 |
| globals-saliency | 0.804 | 0.767 | nan | nan | 0.732 |
| grid4_an | 0.845 | 0.857 | nan | nan | 0.858 |
| grid4_an[C] | 0.789 | 0.818 | nan | nan | 0.816 |
| grid4_an[E] | 0.857 | 0.836 | nan | nan | 0.838 |
| grid4_an[L] | 0.839 | 0.871 | nan | nan | 0.872 |
| grid4_ap | 0.834 | 0.847 | nan | nan | 0.837 |
| grid4_ap[C] | 0.784 | 0.808 | nan | nan | 0.802 |
| grid4_ap[E] | 0.836 | 0.828 | nan | nan | 0.82 |
| grid4_ap[L] | 0.823 | 0.871 | nan | nan | 0.868 |
| grid8_an | 0.863 | 0.871 | 0.907 | 0.877 | 0.869 |
| grid8_an+ap | 0.862 | 0.872 | 0.884 | 0.862 | 0.854 |
| grid8_an+aspect | 0.872 | 0.872 | 0.907 | 0.875 | 0.869 |
| grid8_an+globals | 0.845 | 0.819 | 0.872 | 0.835 | 0.869 |
| grid8_an+globals+aspect | 0.846 | 0.82 | 0.872 | 0.836 | 0.869 |
| grid8_an+saliency | 0.885 | 0.894 | 0.907 | 0.883 | 0.882 |
| grid8_an[C] | 0.811 | 0.832 | nan | nan | 0.831 |
| grid8_an[E] | 0.87 | 0.853 | nan | nan | 0.848 |
| grid8_an[L] | 0.863 | 0.889 | nan | nan | 0.889 |
| grid8_ap | 0.862 | 0.868 | 0.885 | 0.851 | 0.832 |
| grid8_ap+globals | 0.845 | 0.821 | 0.855 | 0.831 | 0.841 |
| grid8_ap[C] | 0.812 | 0.835 | nan | nan | 0.818 |
| grid8_ap[E] | 0.856 | 0.842 | nan | nan | 0.81 |
| grid8_ap[L] | 0.86 | 0.893 | nan | nan | 0.873 |
| grids_an | 0.856 | 0.866 | 0.907 | 0.879 | 0.867 |
| grids_ap | 0.85 | 0.859 | 0.883 | 0.86 | 0.833 |
| saliency | 0.878 | 0.892 | nan | 0.913 | 0.891 |
| spectrum | 0.754 | 0.797 | nan | nan | 0.796 |
| symmetry | 0.731 | 0.732 | nan | nan | 0.734 |

#### K. Composition, part x treatment: median version-pair distance, in steps

| part | cen | euc | pca128w | pca64w | zs |
|---|---|---|---|---|---|
| ALL | 0.844 | 0.843 | 0.792 | 0.826 | 0.853 |
| ALL-aspect | 0.834 | 0.858 | 0.796 | 0.838 | 0.854 |
| aspect | nan | 3.13e+10 | nan | nan | nan |
| balance | 2.18 | 1.88 | nan | nan | 1.76 |
| edges | 2.58 | 2.02 | nan | nan | 1.61 |
| globals | 0.984 | 0.971 | nan | 0.879 | 0.881 |
| globals-saliency | 1.18 | 1.12 | nan | nan | 1.02 |
| grid4_an | 0.979 | 1.01 | nan | nan | 0.976 |
| grid4_an[C] | 1.49 | 1.55 | nan | nan | 1.54 |
| grid4_an[E] | 1.25 | 1.21 | nan | nan | 1.2 |
| grid4_an[L] | 1.27 | 1.27 | nan | nan | 1.27 |
| grid4_ap | 1 | 1.08 | nan | nan | 1.06 |
| grid4_ap[C] | 1.57 | 1.64 | nan | nan | 1.67 |
| grid4_ap[E] | 1.36 | 1.27 | nan | nan | 1.3 |
| grid4_ap[L] | 1.24 | 1.27 | nan | nan | 1.26 |
| grid8_an | 0.838 | 0.901 | 0.874 | 0.819 | 0.887 |
| grid8_an+ap | 0.803 | 0.878 | 0.84 | 0.843 | 0.88 |
| grid8_an+aspect | 0.867 | 0.848 | 0.869 | 0.799 | 0.883 |
| grid8_an+globals | 0.905 | 0.893 | 0.82 | 0.836 | 0.832 |
| grid8_an+globals+aspect | 0.891 | 0.859 | 0.819 | 0.828 | 0.83 |
| grid8_an+saliency | 0.793 | 0.837 | 0.842 | 0.845 | 0.848 |
| grid8_an[C] | 1.02 | 1.11 | nan | nan | 1.1 |
| grid8_an[E] | 0.913 | 0.936 | nan | nan | 0.947 |
| grid8_an[L] | 0.886 | 0.905 | nan | nan | 0.914 |
| grid8_ap | 0.807 | 0.895 | 0.913 | 0.878 | 0.921 |
| grid8_ap+globals | 0.906 | 0.883 | 0.823 | 0.834 | 0.841 |
| grid8_ap[C] | 1.02 | 1.16 | nan | nan | 1.17 |
| grid8_ap[E] | 0.918 | 0.989 | nan | nan | 1.04 |
| grid8_ap[L] | 0.872 | 0.937 | nan | nan | 0.952 |
| grids_an | 0.891 | 0.935 | 0.873 | 0.854 | 0.896 |
| grids_ap | 0.876 | 0.942 | 0.931 | 0.908 | 0.933 |
| saliency | 0.925 | 1.01 | nan | 0.983 | 0.989 |
| spectrum | 26.1 | 5.42 | nan | nan | 4.84 |
| symmetry | 3.44 | 2.64 | nan | nan | 2.73 |

#### K. Composition, raw Euclidean, every part

| part | dim | pr | twonn | rel_contrast | clean_r1 | clean_r5 | clean_r10 | clean_rank_med | clean_rnn_med | clean_rnn_p90 | clean_rstep_lt1 | clean_jacc | clean_rbo | clean_ov10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| grid8_an | 192 | 32.1 | 28.3 | 0.665 | 0.928 | 0.956 | 0.963 | 1 | 0.426 | 0.892 | 0.944 | 0.445 | 0.534 | 0.569 |
| grid8_ap | 192 | 36 | 32.7 | 0.655 | 0.925 | 0.956 | 0.956 | 1 | 0.435 | 0.91 | 0.939 | 0.485 | 0.568 | 0.61 |
| grid4_an | 48 | 16 | 19.1 | 0.549 | 0.881 | 0.923 | 0.932 | 1 | 0.508 | 1.03 | 0.892 | 0.419 | 0.507 | 0.549 |
| grid4_ap | 48 | 16.4 | 18.6 | 0.535 | 0.867 | 0.909 | 0.914 | 1 | 0.509 | 1.14 | 0.851 | 0.417 | 0.51 | 0.543 |
| symmetry | 6 | 3.84 | 5.85 | 0.21 | 0.341 | 0.46 | 0.528 | 8 | 1.52 | 4.02 | 0.341 | 0.243 | 0.292 | 0.327 |
| balance | 9 | 5.7 | 8.3 | 0.308 | 0.467 | 0.586 | 0.649 | 2 | 1.1 | 2.4 | 0.444 | 0.285 | 0.346 | 0.39 |
| edges | 13 | 2.79 | 6.84 | 0.182 | 0.437 | 0.549 | 0.615 | 3 | 1.15 | 3.2 | 0.411 | 0.306 | 0.348 | 0.393 |
| spectrum | 3 | 2.26 | 2.92 | 0.068 | 0.259 | 0.486 | 0.619 | 6 | 1.97 | 7.54 | 0.224 | 0.364 | 0.39 | 0.462 |
| saliency | 67 | 11.6 | 21.7 | 0.528 | 0.944 | 0.965 | 0.97 | 1 | 0.41 | 0.88 | 0.921 | 0.467 | 0.559 | 0.598 |
| aspect | 1 | 1 | 2.07 | 0 | 0.236 | 0.266 | 0.325 | 26.5 | 7.94e+09 | 2.72e+10 | 0.234 | 0.306 | 0.293 | 0.331 |
| grid8_an[L] | 64 | 11.7 | 18.7 | 0.553 | 0.914 | 0.93 | 0.944 | 1 | 0.355 | 0.893 | 0.944 | 0.504 | 0.57 | 0.613 |
| grid8_an[C] | 64 | 15.1 | 22.9 | 0.582 | 0.806 | 0.853 | 0.86 | 1 | 0.564 | 1.34 | 0.827 | 0.36 | 0.422 | 0.464 |
| grid8_an[E] | 64 | 19.1 | 25.2 | 0.56 | 0.895 | 0.923 | 0.93 | 1 | 0.397 | 1.05 | 0.883 | 0.465 | 0.547 | 0.578 |
| grid8_ap[L] | 64 | 14.1 | 18.8 | 0.548 | 0.918 | 0.937 | 0.949 | 1 | 0.344 | 0.919 | 0.939 | 0.531 | 0.607 | 0.642 |
| grid8_ap[C] | 64 | 17.1 | 20.6 | 0.577 | 0.804 | 0.844 | 0.865 | 1 | 0.559 | 1.33 | 0.808 | 0.355 | 0.43 | 0.464 |
| grid8_ap[E] | 64 | 19.5 | 22.6 | 0.544 | 0.883 | 0.911 | 0.925 | 1 | 0.4 | 1.08 | 0.846 | 0.479 | 0.551 | 0.596 |
| grid4_an[L] | 16 | 6.3 | 11.4 | 0.388 | 0.839 | 0.883 | 0.888 | 1 | 0.45 | 1.31 | 0.855 | 0.469 | 0.559 | 0.582 |
| grid4_an[C] | 16 | 7.48 | 11.6 | 0.404 | 0.622 | 0.724 | 0.755 | 1 | 0.759 | 1.92 | 0.664 | 0.317 | 0.373 | 0.417 |
| grid4_an[E] | 16 | 8.4 | 12.3 | 0.401 | 0.799 | 0.86 | 0.888 | 1 | 0.525 | 1.31 | 0.846 | 0.43 | 0.502 | 0.546 |
| grid4_ap[L] | 16 | 6.76 | 10.3 | 0.382 | 0.822 | 0.869 | 0.883 | 1 | 0.463 | 1.42 | 0.846 | 0.474 | 0.547 | 0.583 |
| grid4_ap[C] | 16 | 7.74 | 11 | 0.397 | 0.628 | 0.71 | 0.736 | 1 | 0.795 | 1.93 | 0.64 | 0.319 | 0.382 | 0.423 |
| grid4_ap[E] | 16 | 8.17 | 11.8 | 0.384 | 0.773 | 0.834 | 0.86 | 1 | 0.551 | 1.57 | 0.771 | 0.418 | 0.504 | 0.532 |
| grids_an | 240 | 22.5 | 25.6 | 0.622 | 0.911 | 0.949 | 0.953 | 1 | 0.453 | 0.949 | 0.935 | 0.435 | 0.512 | 0.557 |
| grids_ap | 240 | 24.3 | 26.3 | 0.617 | 0.918 | 0.935 | 0.939 | 1 | 0.451 | 0.951 | 0.921 | 0.445 | 0.543 | 0.571 |
| grid8_an+ap | 384 | 36.1 | 30 | 0.674 | 0.944 | 0.963 | 0.967 | 1 | 0.423 | 0.89 | 0.953 | 0.47 | 0.565 | 0.597 |
| globals | 98 | 13 | 19.1 | 0.516 | 0.851 | 0.906 | 0.921 | 1 | 0.555 | 1.12 | 0.851 | 0.393 | 0.485 | 0.513 |
| globals-saliency | 31 | 9.77 | 13.6 | 0.439 | 0.759 | 0.841 | 0.858 | 1 | 0.675 | 1.41 | 0.729 | 0.388 | 0.464 | 0.504 |
| grid8_an+globals | 290 | 17.3 | 22.9 | 0.581 | 0.902 | 0.928 | 0.932 | 1 | 0.513 | 0.983 | 0.902 | 0.405 | 0.487 | 0.528 |
| grid8_ap+globals | 290 | 17.5 | 23 | 0.58 | 0.902 | 0.93 | 0.932 | 1 | 0.511 | 0.979 | 0.897 | 0.405 | 0.493 | 0.526 |
| grid8_an+globals+aspect | 291 | 15 | 22.3 | 0.573 | 0.916 | 0.93 | 0.951 | 1 | 0.493 | 0.959 | 0.906 | 0.435 | 0.519 | 0.556 |
| grid8_an+saliency | 259 | 27.1 | 29.9 | 0.655 | 0.958 | 0.972 | 0.974 | 1 | 0.402 | 0.762 | 0.967 | 0.473 | 0.57 | 0.605 |
| grid8_an+aspect | 193 | 3.85 | 25.4 | 0.594 | 0.953 | 0.967 | 0.97 | 1 | 0.405 | 0.874 | 0.958 | 0.503 | 0.588 | 0.628 |
| ALL | 579 | 22.8 | 23.4 | 0.61 | 0.925 | 0.951 | 0.96 | 1 | 0.475 | 0.916 | 0.925 | 0.446 | 0.539 | 0.569 |
| ALL-aspect | 578 | 25.6 | 24.6 | 0.622 | 0.925 | 0.944 | 0.953 | 1 | 0.494 | 0.931 | 0.921 | 0.43 | 0.517 | 0.551 |

#### L. Learned, treatment cos: R@1 (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.981 | 0.979 |
| clip_l | embed | nan | 0.984 | 0.984 |
| csd_l | backbone | nan | 0.881 | 0.895 |
| csd_l | content | nan | 0.904 | 0.914 |
| csd_l | style | nan | 0.89 | 0.911 |
| dinov2_b | cls | 0.995 | 0.986 | 0.991 |
| dinov2_b | gram_early | 0.862 | 0.818 | 0.813 |
| dinov2_b | gram_late | 0.977 | 0.979 | 0.972 |
| dinov2_b | gram_mid | 0.939 | 0.906 | 0.885 |
| dinov2_b | meanstd_early | 0.797 | 0.79 | 0.755 |
| dinov2_b | meanstd_late | 0.988 | 0.988 | 0.986 |
| dinov2_b | meanstd_mid | 0.965 | 0.949 | 0.946 |
| dinov2_b | patch_mean | 0.991 | 0.986 | 0.986 |
| dinov2_l | cls | nan | 0.988 | 0.993 |
| dinov2_l | gram_early | nan | 0.86 | 0.851 |
| dinov2_l | gram_late | nan | 0.993 | 0.984 |
| dinov2_l | gram_mid | nan | 0.965 | 0.967 |
| dinov2_l | meanstd_early | nan | 0.822 | 0.755 |
| dinov2_l | meanstd_late | nan | 0.986 | 0.986 |
| dinov2_l | meanstd_mid | nan | 0.965 | 0.97 |
| dinov2_l | patch_mean | nan | 0.986 | 0.984 |
| siglip2_b | embed | 0.991 | 0.986 | 0.988 |
| siglip2_b | patch_mean | 0.984 | 0.977 | 0.981 |

#### L. Learned, treatment cos: R@1 (all primary)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.931 | 0.934 |
| clip_l | embed | nan | 0.936 | 0.942 |
| csd_l | backbone | nan | 0.838 | 0.85 |
| csd_l | content | nan | 0.858 | 0.863 |
| csd_l | style | nan | 0.847 | 0.865 |
| dinov2_b | cls | 0.954 | 0.949 | 0.953 |
| dinov2_b | gram_early | 0.794 | 0.761 | 0.754 |
| dinov2_b | gram_late | 0.923 | 0.914 | 0.911 |
| dinov2_b | gram_mid | 0.878 | 0.843 | 0.836 |
| dinov2_b | meanstd_early | 0.734 | 0.73 | 0.701 |
| dinov2_b | meanstd_late | 0.947 | 0.934 | 0.932 |
| dinov2_b | meanstd_mid | 0.892 | 0.874 | 0.872 |
| dinov2_b | patch_mean | 0.943 | 0.927 | 0.929 |
| dinov2_l | cls | nan | 0.958 | 0.969 |
| dinov2_l | gram_early | nan | 0.788 | 0.781 |
| dinov2_l | gram_late | nan | 0.927 | 0.921 |
| dinov2_l | gram_mid | nan | 0.903 | 0.898 |
| dinov2_l | meanstd_early | nan | 0.754 | 0.699 |
| dinov2_l | meanstd_late | nan | 0.931 | 0.929 |
| dinov2_l | meanstd_mid | nan | 0.898 | 0.905 |
| dinov2_l | patch_mean | nan | 0.925 | 0.925 |
| siglip2_b | embed | 0.947 | 0.94 | 0.94 |
| siglip2_b | patch_mean | 0.936 | 0.914 | 0.929 |

#### L. Learned, treatment cos: p90 of d(A,B)/d(A, nearest other) (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.75 | 0.725 |
| clip_l | embed | nan | 0.752 | 0.712 |
| csd_l | backbone | nan | 1.02 | 1.02 |
| csd_l | content | nan | 0.996 | 0.972 |
| csd_l | style | nan | 1.01 | 0.984 |
| dinov2_b | cls | 0.624 | 0.635 | 0.583 |
| dinov2_b | gram_early | 1.07 | 1.11 | 1.12 |
| dinov2_b | gram_late | 0.737 | 0.773 | 0.756 |
| dinov2_b | gram_mid | 0.91 | 0.972 | 1.02 |
| dinov2_b | meanstd_early | 1.17 | 1.13 | 1.22 |
| dinov2_b | meanstd_late | 0.62 | 0.628 | 0.613 |
| dinov2_b | meanstd_mid | 0.807 | 0.859 | 0.846 |
| dinov2_b | patch_mean | 0.597 | 0.644 | 0.606 |
| dinov2_l | cls | nan | 0.59 | 0.534 |
| dinov2_l | gram_early | nan | 1.05 | 1.07 |
| dinov2_l | gram_late | nan | 0.633 | 0.627 |
| dinov2_l | gram_mid | nan | 0.824 | 0.826 |
| dinov2_l | meanstd_early | nan | 1.11 | 1.2 |
| dinov2_l | meanstd_late | nan | 0.6 | 0.589 |
| dinov2_l | meanstd_mid | nan | 0.778 | 0.807 |
| dinov2_l | patch_mean | nan | 0.589 | 0.579 |
| siglip2_b | embed | 0.692 | 0.697 | 0.687 |
| siglip2_b | patch_mean | 0.6 | 0.67 | 0.579 |

#### L. Learned, treatment cos: share under one step (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.977 | 0.967 |
| clip_l | embed | nan | 0.981 | 0.981 |
| csd_l | backbone | nan | 0.902 | 0.888 |
| csd_l | content | nan | 0.906 | 0.911 |
| csd_l | style | nan | 0.906 | 0.916 |
| dinov2_b | cls | 0.977 | 0.986 | 0.986 |
| dinov2_b | gram_early | 0.818 | 0.804 | 0.785 |
| dinov2_b | gram_late | 0.977 | 0.972 | 0.972 |
| dinov2_b | gram_mid | 0.949 | 0.921 | 0.878 |
| dinov2_b | meanstd_early | 0.785 | 0.776 | 0.678 |
| dinov2_b | meanstd_late | 0.991 | 0.986 | 0.991 |
| dinov2_b | meanstd_mid | 0.967 | 0.944 | 0.944 |
| dinov2_b | patch_mean | 0.991 | 0.986 | 0.991 |
| dinov2_l | cls | nan | 0.977 | 0.981 |
| dinov2_l | gram_early | nan | 0.836 | 0.804 |
| dinov2_l | gram_late | nan | 0.986 | 0.986 |
| dinov2_l | gram_mid | nan | 0.967 | 0.953 |
| dinov2_l | meanstd_early | nan | 0.804 | 0.71 |
| dinov2_l | meanstd_late | nan | 0.981 | 0.981 |
| dinov2_l | meanstd_mid | nan | 0.963 | 0.967 |
| dinov2_l | patch_mean | nan | 0.986 | 0.986 |
| siglip2_b | embed | 0.995 | 0.986 | 0.986 |
| siglip2_b | patch_mean | 0.991 | 0.977 | 0.991 |

#### L. Learned, treatment cos: top-10 overlap (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.768 | 0.805 |
| clip_l | embed | nan | 0.769 | 0.817 |
| csd_l | backbone | nan | 0.535 | 0.556 |
| csd_l | content | nan | 0.538 | 0.583 |
| csd_l | style | nan | 0.535 | 0.578 |
| dinov2_b | cls | 0.761 | 0.768 | 0.785 |
| dinov2_b | gram_early | 0.417 | 0.412 | 0.428 |
| dinov2_b | gram_late | 0.628 | 0.612 | 0.643 |
| dinov2_b | gram_mid | 0.48 | 0.45 | 0.484 |
| dinov2_b | meanstd_early | 0.458 | 0.447 | 0.443 |
| dinov2_b | meanstd_late | 0.793 | 0.775 | 0.803 |
| dinov2_b | meanstd_mid | 0.661 | 0.629 | 0.628 |
| dinov2_b | patch_mean | 0.788 | 0.79 | 0.803 |
| dinov2_l | cls | nan | 0.817 | 0.817 |
| dinov2_l | gram_early | nan | 0.435 | 0.449 |
| dinov2_l | gram_late | nan | 0.687 | 0.73 |
| dinov2_l | gram_mid | nan | 0.528 | 0.547 |
| dinov2_l | meanstd_early | nan | 0.485 | 0.449 |
| dinov2_l | meanstd_late | nan | 0.81 | 0.822 |
| dinov2_l | meanstd_mid | nan | 0.702 | 0.686 |
| dinov2_l | patch_mean | nan | 0.794 | 0.817 |
| siglip2_b | embed | 0.783 | 0.769 | 0.781 |
| siglip2_b | patch_mean | 0.799 | 0.772 | 0.818 |

#### L. Learned, treatment cen: R@1 (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.984 | 0.977 |
| clip_l | embed | nan | 0.981 | 0.984 |
| csd_l | backbone | nan | 0.888 | 0.902 |
| csd_l | content | nan | 0.906 | 0.911 |
| csd_l | style | nan | 0.902 | 0.906 |
| dinov2_b | cls | 0.995 | 0.988 | 0.993 |
| dinov2_b | gram_early | 0.848 | 0.851 | 0.815 |
| dinov2_b | gram_late | 0.977 | 0.974 | 0.97 |
| dinov2_b | gram_mid | 0.953 | 0.916 | 0.904 |
| dinov2_b | meanstd_early | 0.79 | 0.799 | 0.75 |
| dinov2_b | meanstd_late | 0.991 | 0.988 | 0.986 |
| dinov2_b | meanstd_mid | 0.97 | 0.949 | 0.946 |
| dinov2_b | patch_mean | 0.991 | 0.986 | 0.986 |
| dinov2_l | cls | nan | 0.991 | 0.993 |
| dinov2_l | gram_early | nan | 0.872 | 0.867 |
| dinov2_l | gram_late | nan | 0.991 | 0.984 |
| dinov2_l | gram_mid | nan | 0.97 | 0.972 |
| dinov2_l | meanstd_early | nan | 0.82 | 0.75 |
| dinov2_l | meanstd_late | nan | 0.986 | 0.984 |
| dinov2_l | meanstd_mid | nan | 0.972 | 0.974 |
| dinov2_l | patch_mean | nan | 0.984 | 0.984 |
| siglip2_b | embed | 0.991 | 0.986 | 0.988 |
| siglip2_b | patch_mean | 0.986 | 0.979 | 0.981 |

#### L. Learned, treatment cen: R@1 (all primary)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.936 | 0.934 |
| clip_l | embed | nan | 0.936 | 0.943 |
| csd_l | backbone | nan | 0.847 | 0.858 |
| csd_l | content | nan | 0.86 | 0.869 |
| csd_l | style | nan | 0.856 | 0.861 |
| dinov2_b | cls | 0.96 | 0.951 | 0.956 |
| dinov2_b | gram_early | 0.785 | 0.788 | 0.757 |
| dinov2_b | gram_late | 0.923 | 0.911 | 0.912 |
| dinov2_b | gram_mid | 0.889 | 0.854 | 0.85 |
| dinov2_b | meanstd_early | 0.735 | 0.735 | 0.704 |
| dinov2_b | meanstd_late | 0.942 | 0.94 | 0.936 |
| dinov2_b | meanstd_mid | 0.903 | 0.88 | 0.876 |
| dinov2_b | patch_mean | 0.943 | 0.931 | 0.932 |
| dinov2_l | cls | nan | 0.962 | 0.969 |
| dinov2_l | gram_early | nan | 0.797 | 0.796 |
| dinov2_l | gram_late | nan | 0.931 | 0.921 |
| dinov2_l | gram_mid | nan | 0.907 | 0.912 |
| dinov2_l | meanstd_early | nan | 0.754 | 0.703 |
| dinov2_l | meanstd_late | nan | 0.932 | 0.931 |
| dinov2_l | meanstd_mid | nan | 0.903 | 0.905 |
| dinov2_l | patch_mean | nan | 0.923 | 0.927 |
| siglip2_b | embed | 0.949 | 0.943 | 0.94 |
| siglip2_b | patch_mean | 0.943 | 0.92 | 0.929 |

#### L. Learned, treatment cen: p90 of d(A,B)/d(A, nearest other) (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.75 | 0.727 |
| clip_l | embed | nan | 0.747 | 0.692 |
| csd_l | backbone | nan | 1.03 | 0.994 |
| csd_l | content | nan | 0.989 | 0.976 |
| csd_l | style | nan | 0.998 | 0.988 |
| dinov2_b | cls | 0.617 | 0.611 | 0.585 |
| dinov2_b | gram_early | 1.05 | 1.1 | 1.09 |
| dinov2_b | gram_late | 0.739 | 0.787 | 0.759 |
| dinov2_b | gram_mid | 0.904 | 0.965 | 0.983 |
| dinov2_b | meanstd_early | 1.16 | 1.14 | 1.23 |
| dinov2_b | meanstd_late | 0.613 | 0.636 | 0.605 |
| dinov2_b | meanstd_mid | 0.826 | 0.844 | 0.859 |
| dinov2_b | patch_mean | 0.593 | 0.638 | 0.6 |
| dinov2_l | cls | nan | 0.586 | 0.537 |
| dinov2_l | gram_early | nan | 1.02 | 1.04 |
| dinov2_l | gram_late | nan | 0.622 | 0.619 |
| dinov2_l | gram_mid | nan | 0.807 | 0.792 |
| dinov2_l | meanstd_early | nan | 1.12 | 1.2 |
| dinov2_l | meanstd_late | nan | 0.593 | 0.573 |
| dinov2_l | meanstd_mid | nan | 0.758 | 0.812 |
| dinov2_l | patch_mean | nan | 0.581 | 0.575 |
| siglip2_b | embed | 0.68 | 0.689 | 0.693 |
| siglip2_b | patch_mean | 0.601 | 0.68 | 0.585 |

#### L. Learned, treatment cen: share under one step (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.977 | 0.977 |
| clip_l | embed | nan | 0.977 | 0.977 |
| csd_l | backbone | nan | 0.897 | 0.906 |
| csd_l | content | nan | 0.902 | 0.911 |
| csd_l | style | nan | 0.906 | 0.921 |
| dinov2_b | cls | 0.991 | 0.986 | 0.991 |
| dinov2_b | gram_early | 0.878 | 0.846 | 0.846 |
| dinov2_b | gram_late | 0.981 | 0.963 | 0.977 |
| dinov2_b | gram_mid | 0.977 | 0.949 | 0.953 |
| dinov2_b | meanstd_early | 0.808 | 0.804 | 0.776 |
| dinov2_b | meanstd_late | 0.991 | 0.991 | 0.991 |
| dinov2_b | meanstd_mid | 0.981 | 0.967 | 0.967 |
| dinov2_b | patch_mean | 0.991 | 0.991 | 0.991 |
| dinov2_l | cls | nan | 0.986 | 0.986 |
| dinov2_l | gram_early | nan | 0.888 | 0.892 |
| dinov2_l | gram_late | nan | 0.995 | 0.991 |
| dinov2_l | gram_mid | nan | 0.986 | 0.991 |
| dinov2_l | meanstd_early | nan | 0.855 | 0.776 |
| dinov2_l | meanstd_late | nan | 0.991 | 0.986 |
| dinov2_l | meanstd_mid | nan | 0.972 | 0.986 |
| dinov2_l | patch_mean | nan | 0.991 | 0.986 |
| siglip2_b | embed | 0.995 | 0.991 | 0.991 |
| siglip2_b | patch_mean | 0.991 | 0.981 | 0.991 |

#### L. Learned, treatment cen: top-10 overlap (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.754 | 0.795 |
| clip_l | embed | nan | 0.751 | 0.802 |
| csd_l | backbone | nan | 0.521 | 0.559 |
| csd_l | content | nan | 0.545 | 0.587 |
| csd_l | style | nan | 0.532 | 0.57 |
| dinov2_b | cls | 0.766 | 0.773 | 0.789 |
| dinov2_b | gram_early | 0.394 | 0.402 | 0.402 |
| dinov2_b | gram_late | 0.642 | 0.611 | 0.647 |
| dinov2_b | gram_mid | 0.464 | 0.456 | 0.464 |
| dinov2_b | meanstd_early | 0.465 | 0.455 | 0.435 |
| dinov2_b | meanstd_late | 0.776 | 0.768 | 0.792 |
| dinov2_b | meanstd_mid | 0.66 | 0.617 | 0.629 |
| dinov2_b | patch_mean | 0.778 | 0.775 | 0.803 |
| dinov2_l | cls | nan | 0.804 | 0.824 |
| dinov2_l | gram_early | nan | 0.414 | 0.413 |
| dinov2_l | gram_late | nan | 0.683 | 0.717 |
| dinov2_l | gram_mid | nan | 0.506 | 0.523 |
| dinov2_l | meanstd_early | nan | 0.48 | 0.446 |
| dinov2_l | meanstd_late | nan | 0.789 | 0.832 |
| dinov2_l | meanstd_mid | nan | 0.692 | 0.686 |
| dinov2_l | patch_mean | nan | 0.799 | 0.821 |
| siglip2_b | embed | 0.76 | 0.771 | 0.768 |
| siglip2_b | patch_mean | 0.794 | 0.773 | 0.806 |

#### L. Learned, treatment pca64w: R@1 (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.979 | 0.974 |
| clip_l | embed | nan | 0.977 | 0.977 |
| csd_l | backbone | nan | 0.906 | 0.921 |
| csd_l | content | nan | 0.916 | 0.93 |
| csd_l | style | nan | 0.916 | 0.932 |
| dinov2_b | cls | 0.991 | 0.984 | 0.993 |
| dinov2_b | gram_early | 0.851 | 0.801 | 0.822 |
| dinov2_b | gram_late | 0.97 | 0.944 | 0.965 |
| dinov2_b | gram_mid | 0.937 | 0.902 | 0.892 |
| dinov2_b | meanstd_early | 0.827 | 0.858 | 0.799 |
| dinov2_b | meanstd_late | 0.988 | 0.988 | 0.984 |
| dinov2_b | meanstd_mid | 0.958 | 0.937 | 0.946 |
| dinov2_b | patch_mean | 0.986 | 0.984 | 0.984 |
| dinov2_l | cls | nan | 0.991 | 0.984 |
| dinov2_l | gram_early | nan | 0.851 | 0.853 |
| dinov2_l | gram_late | nan | 0.988 | 0.981 |
| dinov2_l | gram_mid | nan | 0.96 | 0.965 |
| dinov2_l | meanstd_early | nan | 0.841 | 0.801 |
| dinov2_l | meanstd_late | nan | 0.981 | 0.981 |
| dinov2_l | meanstd_mid | nan | 0.972 | 0.977 |
| dinov2_l | patch_mean | nan | 0.986 | 0.981 |
| siglip2_b | embed | 0.988 | 0.986 | 0.984 |
| siglip2_b | patch_mean | 0.986 | 0.977 | 0.984 |

#### L. Learned, treatment pca64w: R@1 (all primary)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.92 | 0.938 |
| clip_l | embed | nan | 0.923 | 0.938 |
| csd_l | backbone | nan | 0.854 | 0.872 |
| csd_l | content | nan | 0.869 | 0.88 |
| csd_l | style | nan | 0.863 | 0.885 |
| dinov2_b | cls | 0.951 | 0.936 | 0.951 |
| dinov2_b | gram_early | 0.785 | 0.75 | 0.765 |
| dinov2_b | gram_late | 0.912 | 0.883 | 0.905 |
| dinov2_b | gram_mid | 0.863 | 0.832 | 0.832 |
| dinov2_b | meanstd_early | 0.761 | 0.788 | 0.745 |
| dinov2_b | meanstd_late | 0.945 | 0.938 | 0.932 |
| dinov2_b | meanstd_mid | 0.89 | 0.865 | 0.878 |
| dinov2_b | patch_mean | 0.936 | 0.925 | 0.927 |
| dinov2_l | cls | nan | 0.96 | 0.956 |
| dinov2_l | gram_early | nan | 0.781 | 0.785 |
| dinov2_l | gram_late | nan | 0.918 | 0.911 |
| dinov2_l | gram_mid | nan | 0.896 | 0.896 |
| dinov2_l | meanstd_early | nan | 0.774 | 0.746 |
| dinov2_l | meanstd_late | nan | 0.925 | 0.925 |
| dinov2_l | meanstd_mid | nan | 0.903 | 0.9 |
| dinov2_l | patch_mean | nan | 0.925 | 0.92 |
| siglip2_b | embed | 0.949 | 0.934 | 0.931 |
| siglip2_b | patch_mean | 0.938 | 0.92 | 0.934 |

#### L. Learned, treatment pca64w: p90 of d(A,B)/d(A, nearest other) (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.806 | 0.777 |
| clip_l | embed | nan | 0.791 | 0.728 |
| csd_l | backbone | nan | 0.979 | 0.943 |
| csd_l | content | nan | 0.945 | 0.923 |
| csd_l | style | nan | 0.953 | 0.921 |
| dinov2_b | cls | 0.608 | 0.586 | 0.566 |
| dinov2_b | gram_early | 1.11 | 1.15 | 1.12 |
| dinov2_b | gram_late | 0.787 | 0.818 | 0.821 |
| dinov2_b | gram_mid | 0.921 | 0.996 | 1.01 |
| dinov2_b | meanstd_early | 1.08 | 1.1 | 1.12 |
| dinov2_b | meanstd_late | 0.582 | 0.611 | 0.594 |
| dinov2_b | meanstd_mid | 0.863 | 0.902 | 0.899 |
| dinov2_b | patch_mean | 0.592 | 0.618 | 0.614 |
| dinov2_l | cls | nan | 0.568 | 0.536 |
| dinov2_l | gram_early | nan | 1.08 | 1.08 |
| dinov2_l | gram_late | nan | 0.634 | 0.629 |
| dinov2_l | gram_mid | nan | 0.863 | 0.843 |
| dinov2_l | meanstd_early | nan | 1.08 | 1.12 |
| dinov2_l | meanstd_late | nan | 0.57 | 0.614 |
| dinov2_l | meanstd_mid | nan | 0.766 | 0.83 |
| dinov2_l | patch_mean | nan | 0.575 | 0.617 |
| siglip2_b | embed | 0.701 | 0.734 | 0.722 |
| siglip2_b | patch_mean | 0.611 | 0.668 | 0.615 |

#### L. Learned, treatment pca64w: share under one step (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.977 | 0.972 |
| clip_l | embed | nan | 0.981 | 0.972 |
| csd_l | backbone | nan | 0.939 | 0.944 |
| csd_l | content | nan | 0.939 | 0.944 |
| csd_l | style | nan | 0.939 | 0.944 |
| dinov2_b | cls | 0.991 | 0.981 | 0.991 |
| dinov2_b | gram_early | 0.855 | 0.832 | 0.851 |
| dinov2_b | gram_late | 0.967 | 0.949 | 0.958 |
| dinov2_b | gram_mid | 0.949 | 0.93 | 0.93 |
| dinov2_b | meanstd_early | 0.851 | 0.865 | 0.836 |
| dinov2_b | meanstd_late | 0.991 | 0.991 | 0.991 |
| dinov2_b | meanstd_mid | 0.977 | 0.963 | 0.967 |
| dinov2_b | patch_mean | 0.986 | 0.991 | 0.986 |
| dinov2_l | cls | nan | 0.986 | 0.986 |
| dinov2_l | gram_early | nan | 0.869 | 0.841 |
| dinov2_l | gram_late | nan | 0.995 | 0.986 |
| dinov2_l | gram_mid | nan | 0.967 | 0.981 |
| dinov2_l | meanstd_early | nan | 0.855 | 0.841 |
| dinov2_l | meanstd_late | nan | 0.986 | 0.986 |
| dinov2_l | meanstd_mid | nan | 0.981 | 0.986 |
| dinov2_l | patch_mean | nan | 0.986 | 0.986 |
| siglip2_b | embed | 0.986 | 0.995 | 0.981 |
| siglip2_b | patch_mean | 0.991 | 0.981 | 0.991 |

#### L. Learned, treatment pca64w: top-10 overlap (clean)

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.73 | 0.779 |
| clip_l | embed | nan | 0.74 | 0.778 |
| csd_l | backbone | nan | 0.564 | 0.597 |
| csd_l | content | nan | 0.572 | 0.606 |
| csd_l | style | nan | 0.575 | 0.601 |
| dinov2_b | cls | 0.746 | 0.735 | 0.763 |
| dinov2_b | gram_early | 0.35 | 0.357 | 0.356 |
| dinov2_b | gram_late | 0.598 | 0.575 | 0.609 |
| dinov2_b | gram_mid | 0.435 | 0.426 | 0.426 |
| dinov2_b | meanstd_early | 0.374 | 0.391 | 0.366 |
| dinov2_b | meanstd_late | 0.752 | 0.745 | 0.772 |
| dinov2_b | meanstd_mid | 0.545 | 0.527 | 0.525 |
| dinov2_b | patch_mean | 0.757 | 0.742 | 0.777 |
| dinov2_l | cls | nan | 0.788 | 0.809 |
| dinov2_l | gram_early | nan | 0.362 | 0.357 |
| dinov2_l | gram_late | nan | 0.642 | 0.699 |
| dinov2_l | gram_mid | nan | 0.444 | 0.478 |
| dinov2_l | meanstd_early | nan | 0.398 | 0.356 |
| dinov2_l | meanstd_late | nan | 0.779 | 0.802 |
| dinov2_l | meanstd_mid | nan | 0.596 | 0.587 |
| dinov2_l | patch_mean | nan | 0.779 | 0.79 |
| siglip2_b | embed | 0.694 | 0.709 | 0.702 |
| siglip2_b | patch_mean | 0.751 | 0.738 | 0.778 |

#### L. Learned, cosine: AUC versions vs repro

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 0.861 | 0.863 |
| clip_l | embed | nan | 0.862 | 0.864 |
| csd_l | backbone | nan | 0.804 | 0.8 |
| csd_l | content | nan | 0.808 | 0.801 |
| csd_l | style | nan | 0.807 | 0.796 |
| dinov2_b | cls | 0.875 | 0.888 | 0.88 |
| dinov2_b | gram_early | 0.789 | 0.793 | 0.752 |
| dinov2_b | gram_late | 0.879 | 0.859 | 0.858 |
| dinov2_b | gram_mid | 0.858 | 0.851 | 0.816 |
| dinov2_b | meanstd_early | 0.797 | 0.793 | 0.773 |
| dinov2_b | meanstd_late | 0.893 | 0.895 | 0.892 |
| dinov2_b | meanstd_mid | 0.886 | 0.865 | 0.866 |
| dinov2_b | patch_mean | 0.888 | 0.889 | 0.888 |
| dinov2_l | cls | nan | 0.869 | 0.882 |
| dinov2_l | gram_early | nan | 0.817 | 0.767 |
| dinov2_l | gram_late | nan | 0.883 | 0.88 |
| dinov2_l | gram_mid | nan | 0.891 | 0.883 |
| dinov2_l | meanstd_early | nan | 0.802 | 0.784 |
| dinov2_l | meanstd_late | nan | 0.875 | 0.866 |
| dinov2_l | meanstd_mid | nan | 0.89 | 0.887 |
| dinov2_l | patch_mean | nan | 0.876 | 0.87 |
| siglip2_b | embed | 0.884 | 0.868 | 0.87 |
| siglip2_b | patch_mean | 0.91 | 0.885 | 0.909 |

#### L. Learned, cosine: TwoNN intrinsic dimension on pilot

| model | part | center | pad | tile |
|---|---|---|---|---|
| clip_l | backbone | nan | 18.2 | 16 |
| clip_l | embed | nan | 17.2 | 14.9 |
| csd_l | backbone | nan | 18.8 | 17.3 |
| csd_l | content | nan | 17.9 | 16.4 |
| csd_l | style | nan | 17.8 | 16.2 |
| dinov2_b | cls | 20.7 | 20.4 | 19.1 |
| dinov2_b | gram_early | 37.5 | 40.1 | 33.5 |
| dinov2_b | gram_late | 26 | 27.1 | 24.1 |
| dinov2_b | gram_mid | 41.8 | 42.8 | 37.1 |
| dinov2_b | meanstd_early | 21.1 | 21.3 | 19.4 |
| dinov2_b | meanstd_late | 21.1 | 21.5 | 20.3 |
| dinov2_b | meanstd_mid | 25.3 | 25.9 | 23.2 |
| dinov2_b | patch_mean | 20.2 | 20.1 | 19.3 |
| dinov2_l | cls | nan | 17.7 | 16.9 |
| dinov2_l | gram_early | nan | 37.9 | 33.1 |
| dinov2_l | gram_late | nan | 26.2 | 25.1 |
| dinov2_l | gram_mid | nan | 45.4 | 39.2 |
| dinov2_l | meanstd_early | nan | 20.3 | 18.6 |
| dinov2_l | meanstd_late | nan | 19.1 | 17.8 |
| dinov2_l | meanstd_mid | nan | 26.3 | 23.3 |
| dinov2_l | patch_mean | nan | 17.1 | 16.4 |
| siglip2_b | embed | 17.8 | 17.7 | 17 |
| siglip2_b | patch_mean | 15.9 | 15.9 | 15.1 |

#### L. Learned: mean over the 56 store x part features, by treatment

| treat | clean_r1 | prim_r1 | clean_rnn_med | clean_rstep_lt1 | clean_ov10 | clean_rbo | twonn |
|---|---|---|---|---|---|---|---|
| cen | 0.94 | 0.887 | 0.514 | 0.949 | 0.648 | 0.614 | 21.9 |
| cos | 0.938 | 0.883 | 0.517 | 0.932 | 0.655 | 0.62 | 23.2 |
| euc | 0.933 | 0.878 | 0.523 | 0.924 | 0.658 | 0.621 | 23.4 |
| pca128 | 0.93 | 0.876 | 0.493 | 0.941 | 0.65 | 0.615 | 17.4 |
| pca128w | 0.959 | 0.907 | 0.483 | 0.968 | 0.599 | 0.575 | 22.4 |
| pca32 | 0.884 | 0.828 | 0.524 | 0.895 | 0.633 | 0.591 | 12.4 |
| pca32w | 0.899 | 0.842 | 0.524 | 0.911 | 0.606 | 0.569 | 13.2 |
| pca64 | 0.915 | 0.86 | 0.5 | 0.926 | 0.646 | 0.608 | 15 |
| pca64w | 0.941 | 0.885 | 0.491 | 0.951 | 0.611 | 0.581 | 17.2 |
| zs | 0.929 | 0.876 | 0.539 | 0.918 | 0.644 | 0.61 | 27.4 |

#### K. Composition: mean over features, by treatment

| treat | clean_r1 | prim_r1 | clean_rnn_med | clean_rstep_lt1 | clean_ov10 | clean_rbo | twonn |
|---|---|---|---|---|---|---|---|
| cen | 0.804 | 0.74 | 0.813 | 0.812 | 0.515 | 0.479 | 17.3 |
| cos | 0.795 | 0.73 | 0.848 | 0.792 | 0.517 | 0.476 | 19.5 |
| euc | 0.79 | 0.728 | 2.33e+08 | 0.792 | 0.527 | 0.489 | 18.5 |
| pca128 | 0.921 | 0.84 | 0.459 | 0.924 | 0.572 | 0.535 | 24.5 |
| pca128w | 0.952 | 0.872 | 0.422 | 0.963 | 0.678 | 0.631 | 45.7 |
| pca32 | 0.873 | 0.795 | 0.518 | 0.867 | 0.545 | 0.511 | 16.7 |
| pca32w | 0.899 | 0.82 | 0.492 | 0.892 | 0.559 | 0.522 | 19.3 |
| pca64 | 0.905 | 0.825 | 0.476 | 0.904 | 0.562 | 0.527 | 20.9 |
| pca64w | 0.936 | 0.858 | 0.443 | 0.938 | 0.595 | 0.557 | 30.1 |
| zs | 0.815 | 0.75 | 0.596 | 0.812 | 0.541 | 0.498 | 20.9 |

#### L. DINOv2-B: mean over parts and treatments, by view

| view | clean_r1 | prim_r1 | clean_rnn_med | clean_ov10 |
|---|---|---|---|---|
| center | 0.925 | 0.868 | 0.523 | 0.602 |
| pad | 0.913 | 0.854 | 0.528 | 0.593 |
| tile | 0.904 | 0.849 | 0.523 | 0.604 |

#### B. Breakdown by flag, source pair and pixel difference: R@1

| group | n | colour (as built): raw palette_hist | colour: std hist+sw | composition (as built): ALL parts | composition: grid8_an | manner (alt.): DINOv2-L gram_late | manner: CSD style | subject (text-trained): SigLIP 2 embed | subject: DINOv2-L cls |
|---|---|---|---|---|---|---|---|---|---|
| all primary | 274 | 0.325 | 0.529 | 0.849 | 0.872 | 0.922 | 0.885 | 0.94 | 0.969 |
| no flag | 214 | 0.292 | 0.547 | 0.925 | 0.953 | 0.984 | 0.932 | 0.988 | 0.993 |
| flag low_diff_maybe_same_master (primary) | 27 | 0.889 | 0.963 | 1 | 1 | 1 | 1 | 1 | 1 |
| flag low_diff_maybe_same_master (all rows) | 37 | 0.919 | 0.973 | 1 | 1 | 1 | 1 | 1 | 1 |
| flag high_diff_check_frame_or_crop (primary) | 30 | 0.0833 | 0.0667 | 0.167 | 0.2 | 0.4 | 0.483 | 0.55 | 0.8 |
| flag high_diff_check_frame_or_crop (all rows) | 70 | 0.05 | 0.0429 | 0.286 | 0.35 | 0.543 | 0.457 | 0.571 | 0.779 |
| flag bw_reproduction (primary) | 3 | 0 | 0 | 0.833 | 0.667 | 1 | 0.5 | 0.833 | 0.667 |
| flag bw_reproduction (all rows) | 17 | 0 | 0.0294 | 0.471 | 0.5 | 0.941 | 0.147 | 0.676 | 0.941 |
| commons|commons2 (primary) | 134 | 0.224 | 0.448 | 0.836 | 0.869 | 0.907 | 0.825 | 0.907 | 0.966 |
| commons|met (primary) | 66 | 0.25 | 0.379 | 0.75 | 0.78 | 0.886 | 0.902 | 0.955 | 0.947 |
| commons|nga (primary) | 36 | 0.667 | 0.806 | 0.972 | 0.972 | 0.986 | 0.986 | 1 | 1 |
| commons|rijksmuseum (primary) | 21 | 0.595 | 0.857 | 0.952 | 1 | 1 | 1 | 1 | 1 |
| commons|aic (primary) | 9 | 0.444 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| commons|cleveland (primary) | 3 | 0.167 | 0.333 | 0.667 | 0.333 | 0.667 | 0.667 | 0.667 | 0.833 |
| commons vs museum (primary) | 135 | 0.426 | 0.607 | 0.856 | 0.87 | 0.933 | 0.941 | 0.97 | 0.97 |
| commons vs museum, no flag | 102 | 0.363 | 0.583 | 0.887 | 0.922 | 0.975 | 0.961 | 0.985 | 0.985 |
| commons vs commons, no flag | 112 | 0.228 | 0.513 | 0.96 | 0.982 | 0.991 | 0.906 | 0.991 | 1 |
| lab_diff 1-3 (primary) | 67 | 0.836 | 0.978 | 1 | 1 | 1 | 1 | 1 | 1 |
| lab_diff 3-6 (primary) | 82 | 0.287 | 0.646 | 0.963 | 0.97 | 0.988 | 0.982 | 1 | 0.994 |
| lab_diff 6-9 (primary) | 56 | 0.107 | 0.304 | 0.938 | 0.964 | 0.982 | 0.911 | 0.982 | 0.991 |
| lab_diff 9-12 (primary) | 38 | 0.0263 | 0.197 | 0.75 | 0.855 | 0.961 | 0.776 | 0.961 | 0.987 |
| lab_diff 12-99 (primary) | 31 | 0.0806 | 0.0645 | 0.177 | 0.194 | 0.419 | 0.468 | 0.548 | 0.774 |

#### B. Breakdown by flag, source pair and pixel difference: overlap@10

| group | n | colour (as built): raw palette_hist | colour: std hist+sw | composition (as built): ALL parts | composition: grid8_an | manner (alt.): DINOv2-L gram_late | manner: CSD style | subject (text-trained): SigLIP 2 embed | subject: DINOv2-L cls |
|---|---|---|---|---|---|---|---|---|---|
| all primary | 274 | 0.241 | 0.323 | 0.543 | 0.686 | 0.693 | 0.588 | 0.745 | 0.804 |
| no flag | 214 | 0.214 | 0.32 | 0.569 | 0.709 | 0.73 | 0.601 | 0.768 | 0.824 |
| flag low_diff_maybe_same_master (primary) | 27 | 0.659 | 0.656 | 0.804 | 0.881 | 0.833 | 0.833 | 0.881 | 0.907 |
| flag low_diff_maybe_same_master (all rows) | 37 | 0.676 | 0.665 | 0.808 | 0.881 | 0.851 | 0.83 | 0.865 | 0.911 |
| flag high_diff_check_frame_or_crop (primary) | 30 | 0.0833 | 0.0767 | 0.137 | 0.367 | 0.297 | 0.313 | 0.467 | 0.577 |
| flag high_diff_check_frame_or_crop (all rows) | 70 | 0.0486 | 0.0886 | 0.151 | 0.409 | 0.341 | 0.294 | 0.487 | 0.564 |
| flag bw_reproduction (primary) | 3 | 0 | 0.0667 | 0.4 | 0.5 | 0.733 | 0.167 | 0.6 | 0.733 |
| flag bw_reproduction (all rows) | 17 | 0 | 0.0235 | 0.206 | 0.471 | 0.582 | 0.0882 | 0.5 | 0.7 |
| commons|commons2 (primary) | 134 | 0.157 | 0.27 | 0.505 | 0.666 | 0.675 | 0.509 | 0.704 | 0.769 |
| commons|met (primary) | 66 | 0.229 | 0.255 | 0.417 | 0.582 | 0.618 | 0.592 | 0.732 | 0.803 |
| commons|nga (primary) | 36 | 0.428 | 0.442 | 0.747 | 0.811 | 0.819 | 0.714 | 0.85 | 0.886 |
| commons|rijksmuseum (primary) | 21 | 0.448 | 0.562 | 0.7 | 0.814 | 0.781 | 0.719 | 0.795 | 0.876 |
| commons|aic (primary) | 9 | 0.322 | 0.578 | 0.722 | 0.867 | 0.789 | 0.833 | 0.822 | 0.9 |
| commons|cleveland (primary) | 3 | 0.333 | 0.267 | 0.533 | 0.667 | 0.433 | 0.6 | 0.8 | 0.533 |
| commons vs museum (primary) | 135 | 0.324 | 0.374 | 0.572 | 0.7 | 0.704 | 0.661 | 0.781 | 0.837 |
| commons vs museum, no flag | 102 | 0.279 | 0.346 | 0.563 | 0.695 | 0.724 | 0.647 | 0.782 | 0.832 |
| commons vs commons, no flag | 112 | 0.154 | 0.296 | 0.575 | 0.721 | 0.737 | 0.56 | 0.755 | 0.817 |
| lab_diff 1-3 (primary) | 67 | 0.551 | 0.6 | 0.794 | 0.854 | 0.83 | 0.801 | 0.864 | 0.901 |
| lab_diff 3-6 (primary) | 82 | 0.233 | 0.365 | 0.612 | 0.737 | 0.763 | 0.639 | 0.763 | 0.83 |
| lab_diff 6-9 (primary) | 56 | 0.107 | 0.186 | 0.487 | 0.661 | 0.696 | 0.512 | 0.743 | 0.773 |
| lab_diff 9-12 (primary) | 38 | 0.0395 | 0.153 | 0.361 | 0.579 | 0.611 | 0.445 | 0.726 | 0.811 |
| lab_diff 12-99 (primary) | 31 | 0.0806 | 0.0742 | 0.142 | 0.368 | 0.306 | 0.303 | 0.461 | 0.574 |

#### B. Breakdown by flag, source pair and pixel difference: d/NN med

| group | n | colour (as built): raw palette_hist | colour: std hist+sw | composition (as built): ALL parts | composition: grid8_an | manner (alt.): DINOv2-L gram_late | manner: CSD style | subject (text-trained): SigLIP 2 embed | subject: DINOv2-L cls |
|---|---|---|---|---|---|---|---|---|---|
| all primary | 274 | 1.39 | 0.966 | 0.491 | 0.401 | 0.382 | 0.616 | 0.445 | 0.322 |
| no flag | 214 | 1.41 | 0.955 | 0.475 | 0.394 | 0.378 | 0.608 | 0.444 | 0.321 |
| flag low_diff_maybe_same_master (primary) | 27 | 0.51 | 0.394 | 0.186 | 0.177 | 0.244 | 0.283 | 0.246 | 0.166 |
| flag low_diff_maybe_same_master (all rows) | 37 | 0.49 | 0.325 | 0.182 | 0.177 | 0.229 | 0.283 | 0.242 | 0.166 |
| flag high_diff_check_frame_or_crop (primary) | 30 | 2.05 | 1.48 | 1.32 | 1.28 | 1.05 | 1.01 | 0.966 | 0.786 |
| flag high_diff_check_frame_or_crop (all rows) | 70 | 2.12 | 1.44 | 1.22 | 1.23 | 0.958 | 1.02 | 0.935 | 0.776 |
| flag bw_reproduction (primary) | 3 | 2.79 | 2.12 | 0.822 | 0.678 | 0.607 | 1.1 | 0.707 | 0.45 |
| flag bw_reproduction (all rows) | 17 | 2.85 | 2 | 1.06 | 0.99 | 0.681 | 1.33 | 0.887 | 0.596 |
| commons|commons2 (primary) | 134 | 1.63 | 1.09 | 0.561 | 0.458 | 0.409 | 0.697 | 0.485 | 0.352 |
| commons|met (primary) | 66 | 1.56 | 1.17 | 0.649 | 0.552 | 0.462 | 0.642 | 0.503 | 0.357 |
| commons|nga (primary) | 36 | 0.799 | 0.589 | 0.201 | 0.212 | 0.248 | 0.414 | 0.355 | 0.24 |
| commons|rijksmuseum (primary) | 21 | 0.855 | 0.603 | 0.228 | 0.215 | 0.345 | 0.467 | 0.374 | 0.279 |
| commons|aic (primary) | 9 | 1.27 | 0.485 | 0.306 | 0.189 | 0.294 | 0.546 | 0.301 | 0.239 |
| commons|cleveland (primary) | 3 | 1.1 | 1.23 | 0.842 | 1.08 | 0.853 | 0.661 | 0.7 | 0.627 |
| commons vs museum (primary) | 135 | 1.14 | 0.812 | 0.388 | 0.327 | 0.365 | 0.549 | 0.426 | 0.295 |
| commons vs museum, no flag | 102 | 1.23 | 0.868 | 0.414 | 0.373 | 0.373 | 0.567 | 0.451 | 0.314 |
| commons vs commons, no flag | 112 | 1.55 | 0.981 | 0.505 | 0.407 | 0.379 | 0.639 | 0.442 | 0.326 |
| lab_diff 1-3 (primary) | 67 | 0.682 | 0.483 | 0.19 | 0.185 | 0.244 | 0.366 | 0.282 | 0.19 |
| lab_diff 3-6 (primary) | 82 | 1.25 | 0.859 | 0.356 | 0.322 | 0.364 | 0.575 | 0.398 | 0.329 |
| lab_diff 6-9 (primary) | 56 | 1.71 | 1.23 | 0.631 | 0.495 | 0.444 | 0.701 | 0.539 | 0.376 |
| lab_diff 9-12 (primary) | 38 | 2.05 | 1.36 | 0.705 | 0.632 | 0.456 | 0.784 | 0.55 | 0.407 |
| lab_diff 12-99 (primary) | 31 | 2.05 | 1.49 | 1.3 | 1.27 | 1.05 | 1.02 | 0.966 | 0.795 |

#### N. Noise floor: share of a top-10 pilot neighbour list that changes with the photograph

| variant | no flag: mean share lost | no flag: median lost | no flag: pairs losing 5+ of 10 | all primary: mean share lost | all primary: median lost | all primary: pairs losing 5+ of 10 | commons vs museum, no flag: mean share lost | flag high_diff_check_frame_or_crop (all rows): mean share lost | flag bw_reproduction (all rows): mean share lost |
|---|---|---|---|---|---|---|---|---|---|
| subject: DINOv2-L cls, tile, centred cosine | 0.176 | 0.1 | 0.0561 | 0.196 | 0.15 | 0.0949 | 0.168 | 0.436 | 0.3 |
| subject (text-trained): SigLIP 2 embed, tile, centred | 0.232 | 0.2 | 0.0841 | 0.255 | 0.2 | 0.124 | 0.218 | 0.513 | 0.5 |
| manner: CSD style, tile, PCA-64 whitened | 0.399 | 0.3 | 0.393 | 0.412 | 0.4 | 0.405 | 0.353 | 0.706 | 0.912 |
| manner (alt.): DINOv2-L gram_late, tile, cosine | 0.27 | 0.2 | 0.15 | 0.307 | 0.2 | 0.204 | 0.276 | 0.659 | 0.418 |
| colour: std hist+sw, PCA-64 whitened | 0.68 | 0.7 | 0.794 | 0.677 | 0.7 | 0.766 | 0.654 | 0.911 | 0.976 |
| colour (as built): raw palette_hist, Hellinger | 0.786 | 0.9 | 0.874 | 0.759 | 0.9 | 0.828 | 0.721 | 0.951 | 1 |
| composition: grid8_an, PCA-128 whitened | 0.291 | 0.3 | 0.21 | 0.314 | 0.3 | 0.255 | 0.305 | 0.591 | 0.529 |
| composition (as built): ALL parts, Euclidean | 0.431 | 0.4 | 0.421 | 0.457 | 0.4 | 0.456 | 0.437 | 0.849 | 0.794 |

Images whose features changed under auto-crop: border 125, frame 137 of 689.

#### A. Auto-crop none / border / frame

The pilot gallery is not auto-cropped (no such store exists); both photographs of the pair and the other museums' reproductions are.

| feature | group | n | R@1 none | R@1 border | R@1 frame | d/NN med none | d/NN med border | d/NN med frame | ov10 none | ov10 border | ov10 frame |
|---|---|---|---|---|---|---|---|---|---|---|---|
| colour std hist+sw pca64w | all primary | 274 | 0.529 | 0.553 | 0.564 | 0.966 | 0.951 | 0.925 | 0.323 | 0.341 | 0.35 |
| colour std hist+sw pca64w | no flag | 214 | 0.547 | 0.577 | 0.582 | 0.955 | 0.934 | 0.924 | 0.32 | 0.338 | 0.344 |
| colour std hist+sw pca64w | high_diff flag (primary) | 30 | 0.0667 | 0.0667 | 0.133 | 1.48 | 1.54 | 1.48 | 0.0767 | 0.0767 | 0.11 |
| colour std hist+sw pca64w | high_diff flag (all rows) | 70 | 0.0429 | 0.05 | 0.0786 | 1.44 | 1.46 | 1.45 | 0.0886 | 0.0886 | 0.0986 |
| colour std hist+sw pca64w | commons vs commons (primary) | 139 | 0.453 | 0.453 | 0.46 | 1.09 | 1.08 | 1.07 | 0.274 | 0.28 | 0.286 |
| colour std hist+sw pca64w | commons vs met | 66 | 0.379 | 0.477 | 0.508 | 1.17 | 1.01 | 0.983 | 0.255 | 0.312 | 0.326 |
| colour std hist+sw pca64w | commons vs nga | 36 | 0.806 | 0.806 | 0.806 | 0.589 | 0.599 | 0.599 | 0.442 | 0.439 | 0.439 |
| colour std hist+sw pca64w | commons vs rijksmuseum | 21 | 0.857 | 0.857 | 0.857 | 0.603 | 0.603 | 0.567 | 0.562 | 0.557 | 0.581 |
| colour std hist+sw pca64w | commons vs aic/cleveland | 12 | 0.833 | 0.833 | 0.833 | 0.567 | 0.555 | 0.555 | 0.5 | 0.533 | 0.542 |
| colour std hist+sw pca64w | frame mode cropped either image (all rows) | 155 | 0.29 | 0.352 | 0.381 | 1.24 | 1.18 | 1.16 | 0.217 | 0.26 | 0.278 |
| colour std hist+sw pca64w | frame mode cropped neither (all rows) | 408 | 0.512 | 0.511 | 0.511 | 0.986 | 0.986 | 0.986 | 0.308 | 0.308 | 0.308 |
| colour std hist+sw euc | all primary | 274 | 0.482 | 0.502 | 0.515 | 1.03 | 0.982 | 0.951 | 0.33 | 0.339 | 0.346 |
| colour std hist+sw euc | no flag | 214 | 0.486 | 0.512 | 0.523 | 1.02 | 0.951 | 0.942 | 0.322 | 0.329 | 0.334 |
| colour std hist+sw euc | high_diff flag (primary) | 30 | 0.0833 | 0.0833 | 0.117 | 1.94 | 1.94 | 1.88 | 0.06 | 0.06 | 0.0867 |
| colour std hist+sw euc | high_diff flag (all rows) | 70 | 0.0714 | 0.0786 | 0.0929 | 1.74 | 1.73 | 1.73 | 0.0729 | 0.0757 | 0.0871 |
| colour std hist+sw euc | commons vs commons (primary) | 139 | 0.392 | 0.392 | 0.392 | 1.16 | 1.15 | 1.14 | 0.267 | 0.268 | 0.268 |
| colour std hist+sw euc | commons vs met | 66 | 0.364 | 0.447 | 0.492 | 1.21 | 1.1 | 1.02 | 0.291 | 0.327 | 0.342 |
| colour std hist+sw euc | commons vs nga | 36 | 0.722 | 0.722 | 0.722 | 0.622 | 0.633 | 0.633 | 0.456 | 0.456 | 0.456 |
| colour std hist+sw euc | commons vs rijksmuseum | 21 | 0.833 | 0.833 | 0.857 | 0.549 | 0.545 | 0.536 | 0.529 | 0.533 | 0.567 |
| colour std hist+sw euc | commons vs aic/cleveland | 12 | 0.833 | 0.833 | 0.833 | 0.529 | 0.529 | 0.529 | 0.558 | 0.542 | 0.542 |
| colour std hist+sw euc | frame mode cropped either image (all rows) | 155 | 0.281 | 0.329 | 0.361 | 1.34 | 1.25 | 1.22 | 0.223 | 0.246 | 0.261 |
| colour std hist+sw euc | frame mode cropped neither (all rows) | 408 | 0.46 | 0.458 | 0.458 | 1.05 | 1.05 | 1.05 | 0.296 | 0.296 | 0.296 |
| colour raw palette_hist euc | all primary | 274 | 0.325 | 0.334 | 0.336 | 1.39 | 1.4 | 1.41 | 0.241 | 0.245 | 0.243 |
| colour raw palette_hist euc | no flag | 214 | 0.292 | 0.301 | 0.304 | 1.41 | 1.41 | 1.42 | 0.214 | 0.218 | 0.217 |
| colour raw palette_hist euc | high_diff flag (primary) | 30 | 0.0833 | 0.0833 | 0.0833 | 2.05 | 2.05 | 2.16 | 0.0833 | 0.0833 | 0.0767 |
| colour raw palette_hist euc | high_diff flag (all rows) | 70 | 0.05 | 0.05 | 0.05 | 2.12 | 2.09 | 2.17 | 0.0486 | 0.0457 | 0.0429 |
| colour raw palette_hist euc | commons vs commons (primary) | 139 | 0.227 | 0.227 | 0.227 | 1.63 | 1.62 | 1.63 | 0.16 | 0.158 | 0.158 |
| colour raw palette_hist euc | commons vs met | 66 | 0.25 | 0.28 | 0.288 | 1.56 | 1.62 | 1.64 | 0.229 | 0.244 | 0.241 |
| colour raw palette_hist euc | commons vs nga | 36 | 0.667 | 0.667 | 0.667 | 0.799 | 0.799 | 0.799 | 0.428 | 0.428 | 0.428 |
| colour raw palette_hist euc | commons vs rijksmuseum | 21 | 0.595 | 0.595 | 0.595 | 0.855 | 0.855 | 0.855 | 0.448 | 0.448 | 0.448 |
| colour raw palette_hist euc | commons vs aic/cleveland | 12 | 0.375 | 0.417 | 0.417 | 1.11 | 1.15 | 1.27 | 0.325 | 0.35 | 0.333 |
| colour raw palette_hist euc | frame mode cropped either image (all rows) | 155 | 0.194 | 0.219 | 0.229 | 1.68 | 1.7 | 1.71 | 0.188 | 0.198 | 0.197 |
| colour raw palette_hist euc | frame mode cropped neither (all rows) | 408 | 0.272 | 0.272 | 0.272 | 1.54 | 1.54 | 1.54 | 0.191 | 0.191 | 0.191 |
| colour std palette_hist euc | all primary | 274 | 0.467 | 0.491 | 0.504 | 1.05 | 1.02 | 0.993 | 0.312 | 0.323 | 0.328 |
| colour std palette_hist euc | no flag | 214 | 0.47 | 0.5 | 0.512 | 1.04 | 1 | 0.989 | 0.304 | 0.314 | 0.319 |
| colour std palette_hist euc | high_diff flag (primary) | 30 | 0.0833 | 0.0833 | 0.117 | 1.78 | 1.8 | 1.76 | 0.0667 | 0.0733 | 0.0733 |
| colour std palette_hist euc | high_diff flag (all rows) | 70 | 0.0786 | 0.0714 | 0.0857 | 1.62 | 1.62 | 1.62 | 0.0771 | 0.08 | 0.08 |
| colour std palette_hist euc | commons vs commons (primary) | 139 | 0.381 | 0.385 | 0.385 | 1.15 | 1.15 | 1.14 | 0.253 | 0.254 | 0.254 |
| colour std palette_hist euc | commons vs met | 66 | 0.371 | 0.455 | 0.5 | 1.13 | 1.08 | 1 | 0.273 | 0.309 | 0.32 |
| colour std palette_hist euc | commons vs nga | 36 | 0.694 | 0.694 | 0.694 | 0.615 | 0.63 | 0.63 | 0.406 | 0.406 | 0.406 |
| colour std palette_hist euc | commons vs rijksmuseum | 21 | 0.786 | 0.786 | 0.81 | 0.654 | 0.654 | 0.645 | 0.529 | 0.533 | 0.557 |
| colour std palette_hist euc | commons vs aic/cleveland | 12 | 0.75 | 0.792 | 0.792 | 0.522 | 0.522 | 0.525 | 0.558 | 0.592 | 0.592 |
| colour std palette_hist euc | frame mode cropped either image (all rows) | 155 | 0.281 | 0.326 | 0.358 | 1.3 | 1.24 | 1.21 | 0.224 | 0.25 | 0.261 |
| colour std palette_hist euc | frame mode cropped neither (all rows) | 408 | 0.456 | 0.456 | 0.455 | 1.06 | 1.06 | 1.06 | 0.28 | 0.28 | 0.28 |
| composition grid8_an euc | all primary | 274 | 0.841 | 0.858 | 0.874 | 0.442 | 0.414 | 0.398 | 0.538 | 0.558 | 0.568 |
| composition grid8_an euc | no flag | 214 | 0.928 | 0.951 | 0.946 | 0.426 | 0.406 | 0.392 | 0.569 | 0.593 | 0.597 |
| composition grid8_an euc | high_diff flag (primary) | 30 | 0.1 | 0.0833 | 0.267 | 1.43 | 1.41 | 1.35 | 0.107 | 0.09 | 0.15 |
| composition grid8_an euc | high_diff flag (all rows) | 70 | 0.25 | 0.243 | 0.336 | 1.34 | 1.34 | 1.27 | 0.146 | 0.139 | 0.17 |
| composition grid8_an euc | commons vs commons (primary) | 139 | 0.827 | 0.831 | 0.86 | 0.518 | 0.52 | 0.508 | 0.486 | 0.491 | 0.501 |
| composition grid8_an euc | commons vs met | 66 | 0.742 | 0.803 | 0.818 | 0.622 | 0.538 | 0.473 | 0.432 | 0.503 | 0.518 |
| composition grid8_an euc | commons vs nga | 36 | 0.972 | 0.972 | 0.972 | 0.213 | 0.213 | 0.213 | 0.756 | 0.758 | 0.758 |
| composition grid8_an euc | commons vs rijksmuseum | 21 | 1 | 1 | 1 | 0.211 | 0.211 | 0.202 | 0.724 | 0.733 | 0.757 |
| composition grid8_an euc | commons vs aic/cleveland | 12 | 0.875 | 0.875 | 0.833 | 0.301 | 0.299 | 0.299 | 0.742 | 0.742 | 0.708 |
| composition grid8_an euc | frame mode cropped either image (all rows) | 155 | 0.69 | 0.729 | 0.771 | 0.736 | 0.656 | 0.607 | 0.367 | 0.426 | 0.451 |
| composition grid8_an euc | frame mode cropped neither (all rows) | 408 | 0.873 | 0.873 | 0.873 | 0.464 | 0.465 | 0.465 | 0.55 | 0.55 | 0.55 |
| composition grid8_an pca64w | all primary | 274 | 0.852 | 0.863 | 0.876 | 0.424 | 0.407 | 0.391 | 0.576 | 0.593 | 0.603 |
| composition grid8_an pca64w | no flag | 214 | 0.932 | 0.949 | 0.942 | 0.421 | 0.4 | 0.384 | 0.607 | 0.628 | 0.634 |
| composition grid8_an pca64w | high_diff flag (primary) | 30 | 0.167 | 0.15 | 0.317 | 1.34 | 1.31 | 1.25 | 0.15 | 0.137 | 0.19 |
| composition grid8_an pca64w | high_diff flag (all rows) | 70 | 0.293 | 0.286 | 0.371 | 1.28 | 1.25 | 1.21 | 0.194 | 0.187 | 0.217 |
| composition grid8_an pca64w | commons vs commons (primary) | 139 | 0.853 | 0.849 | 0.871 | 0.476 | 0.467 | 0.452 | 0.547 | 0.556 | 0.568 |
| composition grid8_an pca64w | commons vs met | 66 | 0.742 | 0.788 | 0.803 | 0.582 | 0.548 | 0.465 | 0.461 | 0.506 | 0.52 |
| composition grid8_an pca64w | commons vs nga | 36 | 0.972 | 0.972 | 0.972 | 0.209 | 0.209 | 0.209 | 0.744 | 0.744 | 0.744 |
| composition grid8_an pca64w | commons vs rijksmuseum | 21 | 1 | 1 | 1 | 0.207 | 0.207 | 0.196 | 0.752 | 0.743 | 0.762 |
| composition grid8_an pca64w | commons vs aic/cleveland | 12 | 0.833 | 0.875 | 0.833 | 0.231 | 0.229 | 0.229 | 0.717 | 0.783 | 0.775 |
| composition grid8_an pca64w | frame mode cropped either image (all rows) | 155 | 0.697 | 0.719 | 0.755 | 0.65 | 0.594 | 0.541 | 0.415 | 0.464 | 0.495 |
| composition grid8_an pca64w | frame mode cropped neither (all rows) | 408 | 0.903 | 0.903 | 0.903 | 0.43 | 0.43 | 0.43 | 0.589 | 0.589 | 0.589 |
| composition grid8_ap euc | all primary | 274 | 0.838 | 0.858 | 0.874 | 0.451 | 0.415 | 0.404 | 0.578 | 0.595 | 0.6 |
| composition grid8_ap euc | no flag | 214 | 0.925 | 0.946 | 0.944 | 0.435 | 0.409 | 0.396 | 0.61 | 0.63 | 0.634 |
| composition grid8_ap euc | high_diff flag (primary) | 30 | 0.1 | 0.117 | 0.283 | 1.43 | 1.41 | 1.36 | 0.17 | 0.18 | 0.193 |
| composition grid8_ap euc | high_diff flag (all rows) | 70 | 0.236 | 0.243 | 0.329 | 1.36 | 1.34 | 1.28 | 0.179 | 0.183 | 0.2 |
| composition grid8_ap euc | commons vs commons (primary) | 139 | 0.82 | 0.824 | 0.856 | 0.533 | 0.533 | 0.522 | 0.526 | 0.528 | 0.541 |
| composition grid8_ap euc | commons vs met | 66 | 0.742 | 0.818 | 0.826 | 0.617 | 0.568 | 0.491 | 0.514 | 0.585 | 0.576 |
| composition grid8_ap euc | commons vs nga | 36 | 0.972 | 0.972 | 0.972 | 0.214 | 0.214 | 0.214 | 0.764 | 0.767 | 0.767 |
| composition grid8_ap euc | commons vs rijksmuseum | 21 | 1 | 1 | 1 | 0.204 | 0.204 | 0.198 | 0.743 | 0.724 | 0.752 |
| composition grid8_ap euc | commons vs aic/cleveland | 12 | 0.875 | 0.875 | 0.833 | 0.305 | 0.305 | 0.304 | 0.692 | 0.692 | 0.65 |
| composition grid8_ap euc | frame mode cropped either image (all rows) | 155 | 0.674 | 0.719 | 0.765 | 0.761 | 0.666 | 0.612 | 0.45 | 0.494 | 0.515 |
| composition grid8_ap euc | frame mode cropped neither (all rows) | 408 | 0.866 | 0.866 | 0.866 | 0.476 | 0.477 | 0.477 | 0.57 | 0.57 | 0.57 |
| composition ALL euc | all primary | 274 | 0.849 | 0.861 | 0.881 | 0.491 | 0.445 | 0.42 | 0.543 | 0.57 | 0.583 |
| composition ALL euc | no flag | 214 | 0.925 | 0.946 | 0.946 | 0.475 | 0.42 | 0.409 | 0.569 | 0.602 | 0.61 |
| composition ALL euc | high_diff flag (primary) | 30 | 0.167 | 0.15 | 0.333 | 1.32 | 1.26 | 1.2 | 0.137 | 0.133 | 0.19 |
| composition ALL euc | high_diff flag (all rows) | 70 | 0.286 | 0.279 | 0.371 | 1.22 | 1.2 | 1.13 | 0.151 | 0.151 | 0.187 |
| composition ALL euc | commons vs commons (primary) | 139 | 0.842 | 0.838 | 0.874 | 0.557 | 0.548 | 0.536 | 0.515 | 0.521 | 0.535 |
| composition ALL euc | commons vs met | 66 | 0.75 | 0.811 | 0.833 | 0.649 | 0.567 | 0.535 | 0.417 | 0.512 | 0.532 |
| composition ALL euc | commons vs nga | 36 | 0.972 | 0.972 | 0.972 | 0.201 | 0.201 | 0.201 | 0.747 | 0.747 | 0.747 |
| composition ALL euc | commons vs rijksmuseum | 21 | 0.952 | 0.952 | 0.952 | 0.228 | 0.258 | 0.228 | 0.7 | 0.71 | 0.738 |
| composition ALL euc | commons vs aic/cleveland | 12 | 0.917 | 0.917 | 0.833 | 0.33 | 0.33 | 0.33 | 0.675 | 0.692 | 0.658 |
| composition ALL euc | frame mode cropped either image (all rows) | 155 | 0.681 | 0.716 | 0.777 | 0.771 | 0.647 | 0.607 | 0.361 | 0.437 | 0.472 |
| composition ALL euc | frame mode cropped neither (all rows) | 408 | 0.895 | 0.895 | 0.895 | 0.472 | 0.472 | 0.472 | 0.556 | 0.556 | 0.556 |
| composition saliency euc | all primary | 274 | 0.861 | 0.852 | 0.869 | 0.439 | 0.414 | 0.399 | 0.562 | 0.554 | 0.568 |
| composition saliency euc | no flag | 214 | 0.944 | 0.93 | 0.937 | 0.41 | 0.4 | 0.386 | 0.598 | 0.589 | 0.6 |
| composition saliency euc | high_diff flag (primary) | 30 | 0.183 | 0.183 | 0.283 | 1.51 | 1.5 | 1.46 | 0.117 | 0.0967 | 0.14 |
| composition saliency euc | high_diff flag (all rows) | 70 | 0.307 | 0.314 | 0.379 | 1.41 | 1.4 | 1.34 | 0.166 | 0.161 | 0.181 |
| composition saliency euc | commons vs commons (primary) | 139 | 0.845 | 0.845 | 0.871 | 0.472 | 0.462 | 0.45 | 0.535 | 0.533 | 0.545 |
| composition saliency euc | commons vs met | 66 | 0.788 | 0.758 | 0.773 | 0.662 | 0.626 | 0.558 | 0.438 | 0.42 | 0.445 |
| composition saliency euc | commons vs nga | 36 | 0.972 | 0.972 | 0.972 | 0.234 | 0.234 | 0.234 | 0.781 | 0.781 | 0.781 |
| composition saliency euc | commons vs rijksmuseum | 21 | 1 | 1 | 1 | 0.294 | 0.285 | 0.262 | 0.719 | 0.714 | 0.733 |
| composition saliency euc | commons vs aic/cleveland | 12 | 0.875 | 0.833 | 0.833 | 0.325 | 0.401 | 0.401 | 0.633 | 0.583 | 0.575 |
| composition saliency euc | frame mode cropped either image (all rows) | 155 | 0.719 | 0.713 | 0.768 | 0.724 | 0.644 | 0.547 | 0.431 | 0.425 | 0.453 |
| composition saliency euc | frame mode cropped neither (all rows) | 408 | 0.891 | 0.891 | 0.891 | 0.426 | 0.426 | 0.426 | 0.576 | 0.576 | 0.576 |
| composition aspect euc | all primary | 274 | 0.246 | 0.243 | 0.243 | 7.95e+09 | 7.89e+09 | 7.89e+09 | 0.335 | 0.353 | 0.351 |
| composition aspect euc | no flag | 214 | 0.236 | 0.231 | 0.231 | 7.94e+09 | 7.89e+09 | 7.89e+09 | 0.331 | 0.346 | 0.345 |
| composition aspect euc | high_diff flag (primary) | 30 | 0.0667 | 0.0667 | 0.0667 | 2.53e+10 | 2.29e+10 | 2.24e+10 | 0.127 | 0.173 | 0.167 |
| composition aspect euc | high_diff flag (all rows) | 70 | 0.0857 | 0.05 | 0.05 | 2.54e+10 | 2.35e+10 | 2.34e+10 | 0.15 | 0.137 | 0.134 |
| composition aspect euc | commons vs commons (primary) | 139 | 0.273 | 0.266 | 0.259 | 8.07e+09 | 7.93e+09 | 7.92e+09 | 0.358 | 0.362 | 0.355 |
| composition aspect euc | commons vs met | 66 | 0.167 | 0.167 | 0.167 | 8.1e+09 | 7.9e+09 | 7.92e+09 | 0.262 | 0.333 | 0.326 |
| composition aspect euc | commons vs nga | 36 | 0.375 | 0.375 | 0.375 | 4.47e+09 | 4.47e+09 | 4.47e+09 | 0.456 | 0.456 | 0.456 |
| composition aspect euc | commons vs rijksmuseum | 21 | 0.0952 | 0.143 | 0.19 | 7.92e+09 | 7.96e+09 | 7.88e+09 | 0.152 | 0.2 | 0.248 |
| composition aspect euc | commons vs aic/cleveland | 12 | 0.25 | 0.167 | 0.167 | 8.05e+09 | 9.54e+09 | 7.96e+09 | 0.417 | 0.317 | 0.317 |
| composition aspect euc | frame mode cropped either image (all rows) | 155 | 0.168 | 0.158 | 0.158 | 1.14e+10 | 1.12e+10 | 1.11e+10 | 0.217 | 0.262 | 0.269 |
| composition aspect euc | frame mode cropped neither (all rows) | 408 | 0.292 | 0.292 | 0.292 | 7.85e+09 | 7.85e+09 | 7.85e+09 | 0.397 | 0.397 | 0.397 |
| dinov2_b__pad cls cen | all primary | 274 | 0.951 |  | 0.953 | 0.395 |  | 0.386 | 0.741 |  | 0.753 |
| dinov2_b__pad cls cen | no flag | 214 | 0.988 |  | 0.986 | 0.392 |  | 0.38 | 0.773 |  | 0.782 |
| dinov2_b__pad cls cen | high_diff flag (primary) | 30 | 0.65 |  | 0.7 | 0.877 |  | 0.849 | 0.39 |  | 0.433 |
| dinov2_b__pad cls cen | high_diff flag (all rows) | 70 | 0.671 |  | 0.693 | 0.851 |  | 0.844 | 0.437 |  | 0.456 |
| dinov2_b__pad cls cen | commons vs commons (primary) | 139 | 0.942 |  | 0.953 | 0.439 |  | 0.431 | 0.704 |  | 0.714 |
| dinov2_b__pad cls cen | commons vs met | 66 | 0.932 |  | 0.917 | 0.455 |  | 0.401 | 0.727 |  | 0.748 |
| dinov2_b__pad cls cen | commons vs nga | 36 | 1 |  | 1 | 0.288 |  | 0.288 | 0.869 |  | 0.869 |
| dinov2_b__pad cls cen | commons vs rijksmuseum | 21 | 1 |  | 1 | 0.351 |  | 0.351 | 0.781 |  | 0.8 |
| dinov2_b__pad cls cen | commons vs aic/cleveland | 12 | 0.917 |  | 0.917 | 0.259 |  | 0.259 | 0.8 |  | 0.792 |
| dinov2_b__pad cls cen | frame mode cropped either image (all rows) | 155 | 0.913 |  | 0.926 | 0.49 |  | 0.465 | 0.68 |  | 0.699 |
| dinov2_b__pad cls cen | frame mode cropped neither (all rows) | 408 | 0.952 |  | 0.952 | 0.411 |  | 0.411 | 0.731 |  | 0.731 |
| dinov2_b__pad patch_mean cen | all primary | 274 | 0.931 |  | 0.938 | 0.395 |  | 0.377 | 0.738 |  | 0.758 |
| dinov2_b__pad patch_mean cen | no flag | 214 | 0.986 |  | 0.981 | 0.392 |  | 0.373 | 0.775 |  | 0.786 |
| dinov2_b__pad patch_mean cen | high_diff flag (primary) | 30 | 0.483 |  | 0.583 | 1 |  | 0.903 | 0.307 |  | 0.413 |
| dinov2_b__pad patch_mean cen | high_diff flag (all rows) | 70 | 0.571 |  | 0.629 | 0.942 |  | 0.83 | 0.387 |  | 0.44 |
| dinov2_b__pad patch_mean cen | commons vs commons (primary) | 139 | 0.91 |  | 0.924 | 0.425 |  | 0.427 | 0.711 |  | 0.731 |
| dinov2_b__pad patch_mean cen | commons vs met | 66 | 0.917 |  | 0.932 | 0.472 |  | 0.393 | 0.683 |  | 0.724 |
| dinov2_b__pad patch_mean cen | commons vs nga | 36 | 1 |  | 1 | 0.271 |  | 0.271 | 0.869 |  | 0.872 |
| dinov2_b__pad patch_mean cen | commons vs rijksmuseum | 21 | 1 |  | 1 | 0.345 |  | 0.345 | 0.857 |  | 0.862 |
| dinov2_b__pad patch_mean cen | commons vs aic/cleveland | 12 | 0.917 |  | 0.833 | 0.244 |  | 0.244 | 0.75 |  | 0.742 |
| dinov2_b__pad patch_mean cen | frame mode cropped either image (all rows) | 155 | 0.868 |  | 0.897 | 0.533 |  | 0.46 | 0.634 |  | 0.68 |
| dinov2_b__pad patch_mean cen | frame mode cropped neither (all rows) | 408 | 0.949 |  | 0.949 | 0.39 |  | 0.39 | 0.76 |  | 0.76 |
| dinov2_b__pad gram_late cen | all primary | 274 | 0.911 |  | 0.92 | 0.481 |  | 0.468 | 0.577 |  | 0.6 |
| dinov2_b__pad gram_late cen | no flag | 214 | 0.974 |  | 0.979 | 0.48 |  | 0.465 | 0.611 |  | 0.633 |
| dinov2_b__pad gram_late cen | high_diff flag (primary) | 30 | 0.417 |  | 0.467 | 1.01 |  | 1.01 | 0.2 |  | 0.237 |
| dinov2_b__pad gram_late cen | high_diff flag (all rows) | 70 | 0.507 |  | 0.55 | 0.994 |  | 0.957 | 0.236 |  | 0.271 |
| dinov2_b__pad gram_late cen | commons vs commons (primary) | 139 | 0.881 |  | 0.906 | 0.529 |  | 0.524 | 0.555 |  | 0.569 |
| dinov2_b__pad gram_late cen | commons vs met | 66 | 0.894 |  | 0.894 | 0.574 |  | 0.489 | 0.492 |  | 0.558 |
| dinov2_b__pad gram_late cen | commons vs nga | 36 | 1 |  | 1 | 0.349 |  | 0.349 | 0.761 |  | 0.761 |
| dinov2_b__pad gram_late cen | commons vs rijksmuseum | 21 | 1 |  | 1 | 0.426 |  | 0.417 | 0.629 |  | 0.633 |
| dinov2_b__pad gram_late cen | commons vs aic/cleveland | 12 | 0.917 |  | 0.833 | 0.4 |  | 0.423 | 0.658 |  | 0.642 |
| dinov2_b__pad gram_late cen | frame mode cropped either image (all rows) | 155 | 0.806 |  | 0.865 | 0.68 |  | 0.565 | 0.436 |  | 0.499 |
| dinov2_b__pad gram_late cen | frame mode cropped neither (all rows) | 408 | 0.936 |  | 0.936 | 0.481 |  | 0.481 | 0.6 |  | 0.6 |
| dinov2_b__pad meanstd_early cen | all primary | 274 | 0.735 |  | 0.776 | 0.733 |  | 0.702 | 0.445 |  | 0.459 |
| dinov2_b__pad meanstd_early cen | no flag | 214 | 0.799 |  | 0.836 | 0.726 |  | 0.694 | 0.455 |  | 0.464 |
| dinov2_b__pad meanstd_early cen | high_diff flag (primary) | 30 | 0.117 |  | 0.2 | 1.35 |  | 1.27 | 0.12 |  | 0.167 |
| dinov2_b__pad meanstd_early cen | high_diff flag (all rows) | 70 | 0.157 |  | 0.221 | 1.27 |  | 1.25 | 0.13 |  | 0.157 |
| dinov2_b__pad meanstd_early cen | commons vs commons (primary) | 139 | 0.691 |  | 0.709 | 0.785 |  | 0.782 | 0.386 |  | 0.394 |
| dinov2_b__pad meanstd_early cen | commons vs met | 66 | 0.606 |  | 0.735 | 0.921 |  | 0.772 | 0.37 |  | 0.412 |
| dinov2_b__pad meanstd_early cen | commons vs nga | 36 | 0.972 |  | 0.972 | 0.413 |  | 0.413 | 0.661 |  | 0.658 |
| dinov2_b__pad meanstd_early cen | commons vs rijksmuseum | 21 | 0.976 |  | 0.976 | 0.539 |  | 0.534 | 0.59 |  | 0.624 |
| dinov2_b__pad meanstd_early cen | commons vs aic/cleveland | 12 | 0.833 |  | 0.833 | 0.571 |  | 0.571 | 0.642 |  | 0.583 |
| dinov2_b__pad meanstd_early cen | frame mode cropped either image (all rows) | 155 | 0.513 |  | 0.639 | 0.984 |  | 0.848 | 0.331 |  | 0.38 |
| dinov2_b__pad meanstd_early cen | frame mode cropped neither (all rows) | 408 | 0.754 |  | 0.751 | 0.746 |  | 0.747 | 0.417 |  | 0.417 |

#### A. Change in d(A,B) under auto-crop, pairs where frame mode cropped either image (log2 of cropped / uncropped distance)

| measure | pairs with a crop | closer by >10 % | within 10 % | further by >10 % | median log2 change | p10 | p90 |
|---|---|---|---|---|---|---|---|
| comp_border | 155 | 0.303 | 0.619 | 0.0839 | -0.00575 | -0.568 | 0.109 |
| comp_frame | 155 | 0.439 | 0.465 | 0.103 | -0.0605 | -0.841 | 0.145 |
| col_border | 155 | 0.323 | 0.665 | 0.0129 | -0.0243 | -0.509 | 0.0171 |
| col_frame | 155 | 0.394 | 0.594 | 0.0194 | -0.0541 | -0.686 | 0.0337 |
| dino_frame | 155 | 0.265 | 0.568 | 0.174 | -0.0214 | -0.354 | 0.213 |
