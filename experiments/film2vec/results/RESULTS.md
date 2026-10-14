# film2vec experiments: results

Films with features: 128 (128 in the catalog). k = 10. Seed 0. Distance: cosine after L2, centring on the films present, L2. Tables only; every number sits next to its chance level.

## Blocks

| block | films | dimension | what |
|---|---|---|---|
| look:mean | 128 | 768 | mean of per-shot DINOv2 CLS vectors |
| look:mean+std | 128 | 1536 | per-shot CLS: mean and per-dimension std, concatenated |
| look:profile8 | 128 | 6144 | per-shot CLS: mean within each of 8 equal slices of the sampled running time, concatenated |
| look:patchmean | 128 | 768 | mean over shots of the mean patch token |
| look_grid | 128 | 768 | mean of DINOv2 CLS over the every-20-s frame set |
| colour | 128 | 32 | every-20-s frames: mean and std over frames of 6 light/colour statistics (12), mean 8-bin luminance histogram (8), mean 12-bin chroma-weighted hue histogram gated off when mean saturation < 0.08 (12); z-scored across films |
| time | 128 | 32 | hand-built shot-length, cutting-rate and motion-energy terms, z-scored across films |
| time_sl | 128 | 13 | the shot-length terms of `time` only |
| motion:mid:mean | 128 | 1024 | mean over clips of the V-JEPA 2 ViT-L embedding at about 65% depth, 16 frames from the middle of up to 200 shots |
| motion:mid:mean+std | 128 | 2048 | mean and per-dimension std over clips of the same embedding |
| motion:last:mean | 128 | 1024 | mean over clips of the V-JEPA 2 final-layer embedding |
| sound:mid:mean | 72 | 768 | mean over windows of the EAT middle-layer (block 6 of 12) embedding |
| sound:mid:mean+std | 72 | 1536 | EAT middle layer: mean and per-dimension std over windows |
| sound:last_c:mean | 72 | 768 | EAT last layer; each window minus the corpus mean (mean of film means), L2-normalised, then averaged |
| sound:last_c:mean+std | 72 | 1536 | as sound:last_c:mean, with the per-dimension std over windows appended |
| sound:stats | 72 | 8 | loudness (RMS dB, clipped at -80) and log spectral centroid over windows: mean, std, p10, p90 of each; z-scored across films |
| sound:mid:mean+stats | 72 | 776 | sound:mid:mean and sound:stats concatenated, each scaled to the same total variance |
| words | 72 | 384 | mean of multilingual-e5-small transcript chunk embeddings; films with capped speech share under 0.05 left out |
| fused | 72 | 1568 | look:mean + time + sound:mid:mean, each normalised on the shared films and scaled to equal total variance, concatenated |
| fused:look+time | 128 | 800 | look:mean + time, each normalised on the shared films and scaled to equal total variance, concatenated |
| proxy:facts | 129 | 10 | proxy vectors from facts.npz |
| proxy:label_cast | 129 | 223 | proxy vectors from label_cast.npz |
| proxy:label_decade_country | 129 | 15 | proxy vectors from label_decade_country.npz |
| proxy:label_director | 129 | 28 | proxy vectors from label_director.npz |
| proxy:label_genre | 129 | 41 | proxy vectors from label_genre.npz |
| proxy:llm_felt | 129 | 384 | proxy vectors from llm_felt.npz |
| proxy:llm_style | 129 | 384 | proxy vectors from llm_style.npz |
| proxy:llm_style_high | 37 | 384 | proxy vectors from llm_style_high.npz |
| proxy:llm_style_low | 19 | 384 | proxy vectors from llm_style_low.npz |
| proxy:llm_style_medium | 73 | 384 | proxy vectors from llm_style_medium.npz |
| proxy:wiki_full | 129 | 384 | proxy vectors from wiki_full.npz |
| proxy:wiki_lead | 129 | 384 | proxy vectors from wiki_lead.npz |
| proxy:wiki_plot | 128 | 384 | proxy vectors from wiki_plot.npz |
| proxy:wiki_style | 61 | 384 | proxy vectors from wiki_style.npz |

## Films

| id | title | stages | min | shots | median shot s | shot frames | grid frames | sound windows | speech share | capped | word chunks | height | kbps | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1041834 | Suddenly | time,look,motion,sound,words | 76.700 | 577 | 3.879 | 564 | 223 | 223 | 0.703 | 0.658 | 49 | 1080 | 2384 |  |
| Q1056727 | Kansas City Confidential | time,look,motion,sound,words | 99.300 | 637 | 5.547 | 628 | 291 | 290 | 0.638 | 0.472 | 43 | 720 | 1092 |  |
| Q1058095 | Master of the House | time,look,motion | 106.6 | 1261 | 3.570 | 1245 | 313 |  |  |  |  | 432 | 1338 |  |
| Q1066714 | His Girl Friday | time,look,motion,sound,words | 91.700 | 357 | 7.241 | 355 | 268 | 268 | 0.883 | 0.867 | 96 | 480 | 836.1 |  |
| Q1068328 | Hell's Angels | time,look,motion,sound,words | 131.0 | 1113 | 4.045 | 1108 | 386 | 385 | 0.634 | 0.429 | 57 | 480 | 780.2 | 2 word chunks truncated at 512 tokens |
| Q1144659 | Prelude to War | time,look,motion,sound,words | 52.300 | 561 | 3.136 | 545 | 150 | 150 | 0.794 | 0.611 | 22 | 540 | 3031 |  |
| Q1152044 | Murder! | time,look,motion,sound,words | 102.3 | 424 | 4.817 | 420 | 300 | 299 | 0.729 | 0.632 | 52 | 480 | 770.7 |  |
| Q1156836 | October: Ten Days That Shook the World | time,look,motion | 100.3 | 2320 | 2.080 | 1500 | 294 |  |  |  |  | 480 | 831.9 |  |
| Q1158191 | The Last Time I Saw Paris | time,look,motion,sound,words | 114.4 | 518 | 4.640 | 497 | 336 | 336 | 0.635 | 0.538 | 52 | 720 | 1344 |  |
| Q1164789 | Of Human Bondage | time,look,motion,sound,words | 83.100 | 643 | 4.046 | 634 | 242 | 242 | 0.648 | 0.481 | 34 | 1072 | 2383 |  |
| Q1165285 | A Page of Madness | time,look,motion | 71.200 | 650 | 4.004 | 644 | 207 |  |  |  |  | 1072 | 2296 |  |
| Q1167592 | Jungle Book | time,look,motion,sound,words | 104.9 | 1038 | 4.071 | 1027 | 308 | 307 | 0.656 | 0.531 | 34 | 480 | 833.2 |  |
| Q1187189 | Way Down East | time,look,motion | 147.9 | 1708 | 4.104 | 1500 | 437 |  |  |  |  | 480 | 1211 |  |
| Q1192927 | The Thief of Bagdad | time,look,motion | 151.2 | 1434 | 4.588 | 1419 | 447 |  |  |  |  | 480 | 735.7 |  |
| Q1193655 | The Phantom Carriage | time,look,motion | 106.4 | 913 | 4.667 | 902 | 312 |  |  |  |  | 720 | 1194 |  |
| Q1194608 | King of Jazz | time,look,motion,sound,words | 100.4 | 512 | 8.215 | 508 | 294 | 294 | 0.793 | 0.405 | 23 | 480 | 755.3 |  |
| Q1195531 | The Southerner | time,look,motion,sound,words | 91.900 | 491 | 5.458 | 489 | 269 | 268 | 0.682 | 0.473 | 39 | 1080 | 1335 |  |
| Q1195631 | The Man with the Golden Arm | time,look,motion,sound,words | 119.1 | 198 | 11.979 | 196 | 350 | 350 | 0.663 | 0.561 | 59 | 742 | 1283 |  |
| Q1197672 | The Unknown | time,look,motion | 68.100 | 738 | 4.188 | 721 | 197 |  |  |  |  | 1080 | 2386 |  |
| Q1198850 | The Big Trail | time,look,motion,sound,words | 121.7 | 695 | 6.964 | 693 | 358 | 358 | 0.670 | 0.562 | 54 | 480 | 776.4 | 1 word chunks truncated at 512 tokens |
| Q1199039 | Our Hospitality | time,look,motion | 75.400 | 658 | 5.048 | 653 | 219 |  |  |  |  | 1072 | 2640 |  |
| Q1214957 | Mother | time,look,motion | 87.300 | 1558 | 2.452 | 1500 | 255 |  |  |  |  | 480 | 804.2 |  |
| Q1218520 | The Big Parade | time,look,motion | 151.3 | 1554 | 3.607 | 1500 | 447 |  |  |  |  | 480 | 696.9 |  |
| Q1242772 | The Last Man on Earth | time,look,motion,sound,words | 86.800 | 740 | 3.837 | 718 | 253 | 253 | 0.527 | 0.391 | 29 | 720 | 1149 |  |
| Q128930 | Scarlet Street | time,look,motion,sound,words | 101.7 | 535 | 5.714 | 527 | 298 | 298 | 0.686 | 0.531 | 50 | 720 | 941.0 |  |
| Q1304986 | The Crowd | time,look,motion | 93.200 | 1154 | 3.086 | 1139 | 273 |  |  |  |  | 480 | 922.1 |  |
| Q1305557 | Made for Each Other | time,look,motion,sound,words | 90.500 | 727 | 4.771 | 698 | 264 | 264 | 0.702 | 0.651 | 52 | 480 | 834.7 |  |
| Q1365572 | Steamboat Bill Jr. | time,look,motion | 71.300 | 562 | 4.880 | 552 | 207 |  |  |  |  | 1072 | 2641 |  |
| Q1394119 | The Emperor Jones | time,look,motion,sound,words | 76.300 | 266 | 8.425 | 258 | 222 | 221 | 0.678 | 0.634 | 41 | 1072 | 2383 |  |
| Q1438966 | Häxan | time,look,motion | 105.0 | 1089 | 4.755 | 1073 | 308 |  |  |  |  | 720 | 902.4 |  |
| Q1470370 | Beat the Devil | time,look,motion,sound,words | 89.300 | 478 | 5.590 | 471 | 261 | 260 | 0.809 | 0.762 | 61 | 720 | 1035 |  |
| Q151177 | Strike | time,look,motion | 88.900 | 1708 | 2.252 | 1500 | 260 |  |  |  |  | 720 | 1617 |  |
| Q151599 | Metropolis | time,look,motion | 149.0 | 1749 | 3.712 | 1500 | 440 |  |  |  |  | 1080 | 1352 |  |
| Q151895 | Nosferatu | time,look,motion | 94.300 | 697 | 5.839 | 692 | 276 |  |  |  |  | 720 | 1038 |  |
| Q151913 | The Blood of Jesus | time,look,motion,sound,words | 56.500 | 366 | 5.860 | 348 | 162 | 162 | 0.759 | 0.556 | 20 | 1072 | 2384 |  |
| Q1520732 | Meet John Doe | time,look,motion,sound,words | 122.6 | 1041 | 4.042 | 1032 | 361 | 360 | 0.734 | 0.656 | 79 | 720 | 749.4 |  |
| Q152163 | Last Woman on Earth | time,look,motion,sound,words | 71.000 | 523 | 4.463 | 505 | 206 | 206 | 0.636 | 0.485 | 27 | 720 | 2422 |  |
| Q152350 | Battleship Potemkin | time,look,motion | 71.600 | 1455 | 2.442 | 1419 | 208 |  |  |  |  | 1072 | 2300 |  |
| Q153886 | The Cabinet of Dr. Caligari | time,look,motion | 77.300 | 422 | 7.146 | 405 | 225 |  |  |  |  | 1072 | 2538 |  |
| Q1541422 | The Most Dangerous Game | time,look,motion,sound,words | 62.400 | 486 | 4.421 | 472 | 180 | 180 | 0.798 | 0.464 | 23 | 720 | 897.0 | 26% of sound windows below -60 dB |
| Q1569918 | Sherlock, Jr. | time,look,motion | 44.600 | 357 | 4.922 | 348 | 127 |  |  |  |  | 1072 | 2296 |  |
| Q1571464 | Hallelujah! | time,look,motion,sound,words | 99.900 | 637 | 6.048 | 624 | 293 | 292 | 0.794 | 0.611 | 40 | 1072 | 2384 |  |
| Q1575490 | A Farewell to Arms | time,look,motion,sound,words | 89.100 | 467 | 6.465 | 460 | 260 | 260 | 0.657 | 0.468 | 35 | 1072 | 2093 |  |
| Q158047 | The Blue Angel | time,look,motion,sound,words | 107.3 | 482 | 7.521 | 477 | 315 | 315 | 0.679 | 0.354 | 25 | 720 | 1084 |  |
| Q1586983 | The Docks of New York | time,look,motion | 75.600 | 714 | 4.588 | 702 | 220 |  |  |  |  | 1072 | 2384 |  |
| Q1620069 | Love Affair | time,look,motion,sound,words | 86.800 | 412 | 6.123 | 404 | 254 | 253 | 0.669 | 0.488 | 34 | 480 | 834.8 |  |
| Q166089 | Abraham Lincoln | time,look,motion,sound,words | 93.700 | 391 | 8.383 | 389 | 274 | 273 | 0.690 | 0.434 | 30 | 720 | 1537 |  |
| Q1713697 | Juno and the Paycock | time,look,motion,sound,words | 92.500 | 235 | 10.944 | 228 | 270 | 270 | 0.752 | 0.695 | 54 | 480 | 783.8 |  |
| Q174513 | One-Eyed Jacks | time,look,motion,sound,words | 141.4 | 1106 | 4.796 | 1093 | 417 | 417 | 0.579 | 0.446 | 45 | 480 | 767.8 |  |
| Q1751461 | White Zombie | time,look,motion,sound,words | 66.800 | 473 | 4.671 | 454 | 193 | 193 | 0.637 | 0.387 | 16 | 480 | 832.5 |  |
| Q1799948 | Ladies of Leisure | time,look,motion,sound,words | 99.800 | 579 | 6.216 | 577 | 292 | 292 | 0.683 | 0.582 | 46 | 720 | 1274 | 1 word chunks truncated at 512 tokens |
| Q1811134 | My Man Godfrey | time,look,motion,sound,words | 94.800 | 594 | 4.900 | 583 | 277 | 277 | 0.761 | 0.702 | 74 | 480 | 830.8 |  |
| Q18341272 | Die Nibelungen: Siegfried | time,look,motion | 149.9 | 1096 | 5.708 | 1093 | 443 |  |  |  |  | 720 | 1290 |  |
| Q1852671 | Carnival of Souls | time,look,motion,sound,words | 77.700 | 426 | 8.000 | 405 | 226 | 226 | 0.685 | 0.370 | 24 | 720 | 1200 |  |
| Q190575 | Un Chien Andalou | time,look,motion | 16.400 | 298 | 2.336 | 282 | 42 |  |  |  |  | 1080 | 2386 |  |
| Q192206 | Intolerance | time,look,motion | 167.5 | 1995 | 3.586 | 1500 | 495 |  |  |  |  | 480 | 805.0 |  |
| Q1968139 | The Terror | time,look,motion,sound,words | 79.300 | 701 | 4.338 | 682 | 231 | 230 | 0.705 | 0.362 | 22 | 720 | 1284 |  |
| Q2032599 | Life with Father | time,look,motion,sound,words | 117.7 | 629 | 7.012 | 621 | 346 | 346 | 0.790 | 0.725 | 77 | 1072 | 1634 |  |
| Q2046050 | He Who Gets Slapped | time,look,motion | 71.700 | 1044 | 2.769 | 1025 | 208 |  |  |  |  | 480 | 1260 |  |
| Q2061614 | Mr. Bug Goes to Town | time,look,motion,sound,words | 77.500 | 555 | 5.320 | 543 | 226 | 225 | 0.666 | 0.445 | 24 | 720 | 1338 |  |
| Q2062566 | Detour | time,look,motion,sound,words | 69.100 | 217 | 10.969 | 213 | 200 | 200 | 0.725 | 0.648 | 46 | 1072 | 2245 |  |
| Q2138984 | The Cameraman | time,look,motion | 70.500 | 775 | 3.712 | 753 | 204 |  |  |  |  | 1072 | 2384 |  |
| Q214723 | The Gold Rush | time,look,motion | 89.200 | 868 | 3.670 | 844 | 261 |  |  |  |  | 480 | 812.6 |  |
| Q2162104 | Under the Roofs of Paris | time,look,motion,sound,words | 92.800 | 658 | 5.500 | 643 | 271 | 271 | 0.675 | 0.256 | 13 | 480 | 766.0 |  |
| Q2264826 | The Strange Woman | time,look,motion,sound,words | 100.1 | 557 | 6.073 | 549 | 293 | 293 | 0.660 | 0.573 | 51 | 720 | 893.6 |  |
| Q2377258 | The Black Pirate | time,look,motion | 95.400 | 957 | 3.921 | 950 | 279 |  |  |  |  | 720 | 1283 |  |
| Q2379666 | The Memphis Belle: A Story of a Flying Fortress | time,look,motion,sound,words | 41.500 | 450 | 4.154 | 442 | 118 | 117 | 0.728 | 0.541 | 18 | 480 | 834.0 |  |
| Q2399580 | Let There Be Light | time,look,motion,sound,words | 57.900 | 288 | 6.131 | 270 | 167 | 166 | 0.833 | 0.779 | 36 | 720 | 1394 |  |
| Q2411291 | The Toll of the Sea | time,look,motion | 53.100 | 437 | 4.204 | 429 | 152 |  |  |  |  | 720 | 1811 |  |
| Q2426434 | The Wind | time,look,motion | 75.800 | 835 | 3.467 | 830 | 220 |  |  |  |  | 720 | 810.8 |  |
| Q246418 | Gulliver's Travels | time,look,motion,sound,words | 76.400 | 553 | 5.589 | 548 | 222 | 222 | 0.691 | 0.336 | 15 | 1080 | 2306 |  |
| Q2482628 | The Freshman | time,look,motion | 76.200 | 944 | 3.420 | 932 | 221 |  |  |  |  | 720 | 1383 |  |
| Q2515935 | The Strong Man | time,look,motion | 75.400 | 859 | 3.240 | 846 | 219 |  |  |  |  | 480 | 621.5 |  |
| Q2517806 | Within Our Gates | time,look,motion | 73.700 | 839 | 3.625 | 829 | 214 |  |  |  |  | 1072 | 2381 |  |
| Q2567687 | A Bucket of Blood | time,look,motion,sound,words | 66.000 | 303 | 7.040 | 300 | 191 | 190 | 0.690 | 0.578 | 32 | 720 | 1781 |  |
| Q258830 | The Last Laugh | time,look,motion | 90.200 | 485 | 6.667 | 481 | 264 |  |  |  |  | 480 | 807.7 |  |
| Q2625053 | The Hitch-Hiker | time,look,motion,sound,words | 70.700 | 519 | 4.171 | 505 | 205 | 205 | 0.555 | 0.381 | 21 | 720 | 1460 |  |
| Q263583 | House on Haunted Hill | time,look,motion,sound,words | 74.900 | 472 | 4.671 | 466 | 218 | 217 | 0.645 | 0.491 | 28 | 720 | 1297 |  |
| Q272036 | Wings | time,look,motion | 144.3 | 1969 | 3.086 | 1500 | 426 |  |  |  |  | 720 | 950.8 |  |
| Q272599 | All Quiet on the Western Front | time,look,motion,sound,words | 133.4 | 779 | 3.879 | 771 | 393 | 393 | 0.648 | 0.449 | 46 | 720 | 971.2 |  |
| Q2884134 | Bluebeard | time,look,motion,sound,words | 70.600 | 449 | 4.938 | 429 | 205 | 204 | 0.692 | 0.568 | 34 | 480 | 834.1 |  |
| Q315896 | People on Sunday | time,look,motion | 73.700 | 854 | 3.560 | 834 | 214 |  |  |  |  | 480 | 829.7 |  |
| Q3321119 | Strange Illusion | time,look,motion,sound,words | 85.300 | 385 | 6.240 | 372 | 249 | 248 | 0.707 | 0.592 | 49 | 480 | 832.9 |  |
| Q419838 | Penny Serenade | time,look,motion,sound,words | 119.1 | 701 | 6.206 | 697 | 350 | 350 | 0.628 | 0.456 | 49 | 480 | 833.7 |  |
| Q4290514 | Ménilmontant | time,look,motion | 37.900 | 455 | 3.036 | 392 | 107 |  |  |  |  | 480 | 832.7 |  |
| Q430852 | Till the Clouds Roll By | time,look,motion,sound,words | 135.1 | 303 | 15.224 | 297 | 398 | 398 | 0.776 | 0.564 | 63 | 768 | 940.9 |  |
| Q431093 | Sunrise: A Song of Two Humans | time,look,motion | 94.300 | 562 | 6.131 | 556 | 276 |  |  |  |  | 720 | 1010 |  |
| Q466816 | The Last Command | time,look,motion | 88.700 | 826 | 4.354 | 817 | 259 |  |  |  |  | 480 | 809.0 |  |
| Q496266 | Charade | time,look,motion,sound,words | 113.4 | 1203 | 3.420 | 1189 | 333 | 333 | 0.651 | 0.510 | 54 | 1080 | 1502 |  |
| Q500296 | The Little Shop of Horrors | time,look,motion,sound,words | 71.800 | 582 | 5.422 | 565 | 208 | 208 | 0.756 | 0.695 | 41 | 720 | 1193 |  |
| Q504961 | The Lodger: A Story of the London Fog | time,look,motion | 90.700 | 969 | 3.750 | 961 | 265 |  |  |  |  | 720 | 481.9 |  |
| Q512618 | Salt of the Earth | time,look,motion,sound,words | 93.900 | 965 | 3.440 | 935 | 275 | 274 | 0.686 | 0.602 | 44 | 480 | 831.6 |  |
| Q51520 | The Passion of Joan of Arc | time,look,motion | 81.500 | 1495 | 2.461 | 1490 | 238 |  |  |  |  | 1072 | 2305 |  |
| Q522754 | The Golem: How He Came into the World | time,look,motion | 76.200 | 590 | 5.480 | 579 | 222 |  |  |  |  | 1072 | 2245 |  |
| Q530507 | McLintock! | time,look,motion,sound,words | 126.7 | 1183 | 4.292 | 1163 | 373 | 373 | 0.676 | 0.617 | 63 | 480 | 766.5 |  |
| Q538600 | Royal Wedding | time,look,motion,sound,words | 93.100 | 188 | 14.620 | 176 | 272 | 272 | 0.772 | 0.528 | 45 | 720 | 697.0 |  |
| Q547279 | Animal Crackers | time,look,motion,sound,words | 98.700 | 293 | 12.354 | 285 | 289 | 289 | 0.827 | 0.754 | 71 | 1072 | 1247 |  |
| Q55188 | Earth | time,look,motion | 78.000 | 965 | 3.520 | 957 | 227 |  |  |  |  | 480 | 833.1 |  |
| Q562096 | Westfront 1918 | time,look,motion,sound,words | 96.200 | 368 | 9.739 | 361 | 282 | 281 | 0.537 | 0.342 | 20 | 720 | 1282 |  |
| Q567591 | The Adventures of Prince Achmed | time,look,motion | 66.100 | 582 | 4.583 | 571 | 191 |  |  |  |  | 1080 | 2384 |  |
| Q569699 | Diary of a Lost Girl | time,look,motion | 113.1 | 1405 | 3.370 | 1397 | 332 |  |  |  |  | 480 | 807.1 |  |
| Q570143 | Spies | time,look,motion | 150.5 | 1307 | 5.213 | 1286 | 444 |  |  |  |  | 480 | 812.8 |  |
| Q577754 | Morocco | time,look,motion,sound,words | 91.700 | 457 | 6.922 | 456 | 268 | 268 | 0.686 | 0.339 | 20 | 480 | 763.1 |  |
| Q581117 | The Cocoanuts | time,look,motion,sound,words | 93.400 | 299 | 10.300 | 296 | 273 | 273 | 0.804 | 0.594 | 53 | 480 | 769.8 |  |
| Q585983 | D.O.A. | time,look,motion,sound,words | 83.400 | 338 | 7.741 | 332 | 243 | 243 | 0.679 | 0.545 | 46 | 720 | 1486 |  |
| Q594498 | The Bigamist | time,look,motion,sound,words | 79.400 | 351 | 7.241 | 336 | 231 | 231 | 0.687 | 0.607 | 43 | 480 | 1476 |  |
| Q621159 | Applause | time,look,motion,sound,words | 78.600 | 276 | 6.456 | 272 | 229 | 228 | 0.822 | 0.628 | 44 | 720 | 1235 |  |
| Q623051 | Night of the Living Dead | time,look,motion,sound,words | 95.900 | 1011 | 3.294 | 994 | 281 | 280 | 0.696 | 0.473 | 39 | 480 | 831.3 |  |
| Q632362 | Berlin: Symphony of a Metropolis | time,look,motion | 62.200 | 1001 | 2.753 | 967 | 180 |  |  |  |  | 1072 | 2311 |  |
| Q645771 | Angel and the Badman | time,look,motion,sound,words | 100.1 | 567 | 6.673 | 560 | 293 | 293 | 0.647 | 0.543 | 44 | 720 | 1973 |  |
| Q659669 | Michael | time,look,motion | 94.300 | 1005 | 4.067 | 987 | 276 |  |  |  |  | 1056 | 2299 |  |
| Q669068 | The Front Page | time,look,motion,sound,words | 101.1 | 452 | 3.629 | 452 | 296 | 296 | 0.803 | 0.772 | 80 | 720 | 840.6 |  |
| Q672480 | Faust | time,look,motion | 107.3 | 862 | 4.880 | 849 | 315 |  |  |  |  | 720 | 1212 |  |
| Q690583 | Greed | time,look,motion | 136.0 | 1596 | 2.967 | 1500 | 401 |  |  |  |  | 480 | 826.7 |  |
| Q700736 | Pandora's Box | time,look,motion | 131.2 | 1191 | 4.705 | 1176 | 387 |  |  |  |  | 478 | 813.0 |  |
| Q778755 | Safety Last! | time,look,motion | 73.900 | 883 | 3.462 | 865 | 215 |  |  |  |  | 1072 | 2384 |  |
| Q829250 | Man with a Movie Camera | time,look,motion | 67.100 | 1184 | 2.708 | 1139 | 194 |  |  |  |  | 1080 | 2382 |  |
| Q850159 | The General | time,look,motion | 78.900 | 630 | 5.568 | 610 | 230 |  |  |  |  | 720 | 1696 |  |
| Q873186 | A Star Is Born | time,look,motion,sound,words | 111.0 | 712 | 5.818 | 700 | 326 | 325 | 0.692 | 0.589 | 59 | 720 | 910.3 |  |
| Q905932 | Broken Blossoms | time,look,motion | 88.400 | 665 | 5.806 | 657 | 258 |  |  |  |  | 480 | 1195 |  |
| Q916078 | Blackmail | time,look,motion,sound,words | 85.600 | 427 | 5.631 | 410 | 250 | 249 | 0.669 | 0.398 | 21 | 1072 | 2182 |  |
| Q918401 | Nanook of the North | time,look,motion | 78.500 | 420 | 7.820 | 405 | 229 |  |  |  |  | 720 | 1284 |  |
| Q927919 | The Phantom of the Opera | time,look,motion | 106.9 | 1086 | 4.204 | 1073 | 314 |  |  |  |  | 480 | 21700 | decoded duration 6416 s vs container 403 s |
| Q946849 | L’Age d’Or | time,look,motion,sound,words | 62.600 | 603 | 3.921 | 595 | 181 | 180 | 0.863 | 0.162 | 5 | 720 | 1282 |  |
| Q961965 | Never Fear | time,look,motion,sound,words | 80.800 | 295 | 8.308 | 282 | 235 | 235 | 0.698 | 0.500 | 38 | 480 | 833.5 |  |
| Q964771 | Nothing Sacred | time,look,motion,sound,words | 73.800 | 577 | 5.000 | 557 | 214 | 214 | 0.732 | 0.602 | 42 | 1080 | 1454 |  |
| Q971265 | The Strange Love of Martha Ivers | time,look,motion,sound,words | 115.8 | 646 | 4.922 | 633 | 340 | 340 | 0.648 | 0.561 | 60 | 480 | 834.7 |  |
| Q978770 | The Stranger | time,look,motion,sound,words | 95.000 | 524 | 4.962 | 494 | 278 | 277 | 0.658 | 0.540 | 47 | 480 | 817.2 |  |

## 1. Block agreement

Spearman: correlation of the two pairwise-distance vectors over the shared films; chance 0, and the 95th percentile over 200 shuffles of the films of block B. Overlap: mean share of the top-k lists in common.

| block A | block B | films | k | Spearman | chance | shuffled p95 | top-k overlap | chance k/(n-1) | shuffled p95 |
|---|---|---|---|---|---|---|---|---|---|
| look:mean | look_grid | 128 | 10 | 0.963 | 0.000 | 0.018 | 0.795 | 0.079 | 0.096 |
| look:mean | colour | 128 | 10 | 0.228 | 0.000 | 0.014 | 0.177 | 0.079 | 0.092 |
| look:mean | time | 128 | 10 | 0.191 | 0.000 | 0.021 | 0.164 | 0.079 | 0.092 |
| look:mean | motion:mid:mean | 128 | 10 | 0.331 | 0.000 | 0.021 | 0.314 | 0.079 | 0.093 |
| look:mean | sound:mid:mean | 72 | 10 | 0.203 | 0.000 | 0.027 | 0.261 | 0.141 | 0.165 |
| look:mean | words | 72 | 10 | 0.454 | 0.000 | 0.036 | 0.350 | 0.141 | 0.164 |
| look:mean | fused | 72 | 10 | 0.525 | 0.000 | 0.026 | 0.496 | 0.141 | 0.168 |
| look:mean | fused:look+time | 128 | 10 | 0.634 | 0.000 | 0.020 | 0.465 | 0.079 | 0.095 |
| look:mean | proxy:facts | 128 | 10 | 0.134 | 0.000 | 0.017 | 0.151 | 0.079 | 0.093 |
| look:mean | proxy:label_cast | 128 | 10 | 0.100 | 0.000 | 0.018 | 0.171 | 0.079 | 0.095 |
| look:mean | proxy:label_decade_country | 128 | 10 | 0.268 | 0.000 | 0.020 | 0.188 | 0.079 | 0.095 |
| look:mean | proxy:label_director | 128 | 10 | 0.006 | 0.000 | 0.020 | 0.127 | 0.079 | 0.096 |
| look:mean | proxy:label_genre | 128 | 10 | 0.276 | 0.000 | 0.020 | 0.208 | 0.079 | 0.093 |
| look:mean | proxy:llm_felt | 128 | 10 | 0.119 | 0.000 | 0.017 | 0.161 | 0.079 | 0.094 |
| look:mean | proxy:llm_style | 128 | 10 | 0.310 | 0.000 | 0.019 | 0.229 | 0.079 | 0.089 |
| look:mean | proxy:llm_style_high | 37 | 10 | 0.282 | 0.000 | 0.057 | 0.446 | 0.278 | 0.314 |
| look:mean | proxy:llm_style_low | 18 | 10 | 0.248 | 0.000 | 0.135 | 0.628 | 0.588 | 0.644 |
| look:mean | proxy:llm_style_medium | 73 | 10 | 0.306 | 0.000 | 0.031 | 0.301 | 0.139 | 0.160 |
| look:mean | proxy:wiki_full | 128 | 10 | 0.346 | 0.000 | 0.019 | 0.315 | 0.079 | 0.092 |
| look:mean | proxy:wiki_lead | 128 | 10 | 0.254 | 0.000 | 0.017 | 0.239 | 0.079 | 0.092 |
| look:mean | proxy:wiki_plot | 127 | 10 | 0.254 | 0.000 | 0.019 | 0.222 | 0.079 | 0.093 |
| look:mean | proxy:wiki_style | 60 | 10 | 0.108 | 0.000 | 0.057 | 0.240 | 0.169 | 0.200 |
| look_grid | colour | 128 | 10 | 0.243 | 0.000 | 0.015 | 0.181 | 0.079 | 0.091 |
| look_grid | time | 128 | 10 | 0.214 | 0.000 | 0.018 | 0.169 | 0.079 | 0.093 |
| look_grid | motion:mid:mean | 128 | 10 | 0.336 | 0.000 | 0.021 | 0.321 | 0.079 | 0.093 |
| look_grid | sound:mid:mean | 72 | 10 | 0.202 | 0.000 | 0.024 | 0.256 | 0.141 | 0.165 |
| look_grid | words | 72 | 10 | 0.456 | 0.000 | 0.037 | 0.347 | 0.141 | 0.167 |
| look_grid | fused | 72 | 10 | 0.488 | 0.000 | 0.027 | 0.467 | 0.141 | 0.167 |
| look_grid | fused:look+time | 128 | 10 | 0.636 | 0.000 | 0.018 | 0.448 | 0.079 | 0.094 |
| look_grid | proxy:facts | 128 | 10 | 0.148 | 0.000 | 0.017 | 0.159 | 0.079 | 0.091 |
| look_grid | proxy:label_cast | 128 | 10 | 0.100 | 0.000 | 0.017 | 0.170 | 0.079 | 0.096 |
| look_grid | proxy:label_decade_country | 128 | 10 | 0.294 | 0.000 | 0.020 | 0.192 | 0.079 | 0.098 |
| look_grid | proxy:label_director | 128 | 10 | 0.009 | 0.000 | 0.018 | 0.125 | 0.079 | 0.103 |
| look_grid | proxy:label_genre | 128 | 10 | 0.311 | 0.000 | 0.020 | 0.206 | 0.079 | 0.094 |
| look_grid | proxy:llm_felt | 128 | 10 | 0.119 | 0.000 | 0.018 | 0.162 | 0.079 | 0.095 |
| look_grid | proxy:llm_style | 128 | 10 | 0.310 | 0.000 | 0.020 | 0.221 | 0.079 | 0.088 |
| look_grid | proxy:llm_style_high | 37 | 10 | 0.273 | 0.000 | 0.054 | 0.424 | 0.278 | 0.311 |
| look_grid | proxy:llm_style_low | 18 | 10 | 0.214 | 0.000 | 0.146 | 0.628 | 0.588 | 0.639 |
| look_grid | proxy:llm_style_medium | 73 | 10 | 0.303 | 0.000 | 0.032 | 0.290 | 0.139 | 0.163 |
| look_grid | proxy:wiki_full | 128 | 10 | 0.341 | 0.000 | 0.018 | 0.284 | 0.079 | 0.093 |
| look_grid | proxy:wiki_lead | 128 | 10 | 0.254 | 0.000 | 0.017 | 0.225 | 0.079 | 0.094 |
| look_grid | proxy:wiki_plot | 127 | 10 | 0.253 | 0.000 | 0.019 | 0.217 | 0.079 | 0.094 |
| look_grid | proxy:wiki_style | 60 | 10 | 0.102 | 0.000 | 0.053 | 0.243 | 0.169 | 0.200 |
| colour | time | 128 | 10 | 0.097 | 0.000 | 0.019 | 0.127 | 0.079 | 0.093 |
| colour | motion:mid:mean | 128 | 10 | 0.554 | 0.000 | 0.019 | 0.363 | 0.079 | 0.097 |
| colour | sound:mid:mean | 72 | 10 | 0.076 | 0.000 | 0.032 | 0.188 | 0.141 | 0.165 |
| colour | words | 72 | 10 | 0.095 | 0.000 | 0.029 | 0.188 | 0.141 | 0.167 |
| colour | fused | 72 | 10 | 0.160 | 0.000 | 0.030 | 0.229 | 0.141 | 0.162 |
| colour | fused:look+time | 128 | 10 | 0.188 | 0.000 | 0.017 | 0.159 | 0.079 | 0.093 |
| colour | proxy:facts | 128 | 10 | 0.134 | 0.000 | 0.016 | 0.111 | 0.079 | 0.092 |
| colour | proxy:label_cast | 128 | 10 | 0.046 | 0.000 | 0.012 | 0.105 | 0.079 | 0.093 |
| colour | proxy:label_decade_country | 128 | 10 | 0.046 | 0.000 | 0.018 | 0.114 | 0.079 | 0.091 |
| colour | proxy:label_director | 128 | 10 | 0.038 | 0.000 | 0.019 | 0.080 | 0.079 | 0.088 |
| colour | proxy:label_genre | 128 | 10 | 0.086 | 0.000 | 0.020 | 0.120 | 0.079 | 0.094 |
| colour | proxy:llm_felt | 128 | 10 | 0.048 | 0.000 | 0.014 | 0.109 | 0.079 | 0.095 |
| colour | proxy:llm_style | 128 | 10 | 0.118 | 0.000 | 0.017 | 0.129 | 0.079 | 0.091 |
| colour | proxy:llm_style_high | 37 | 10 | 0.115 | 0.000 | 0.067 | 0.359 | 0.278 | 0.322 |
| colour | proxy:llm_style_low | 18 | 10 | 0.073 | 0.000 | 0.149 | 0.572 | 0.588 | 0.650 |
| colour | proxy:llm_style_medium | 73 | 10 | 0.115 | 0.000 | 0.034 | 0.166 | 0.139 | 0.162 |
| colour | proxy:wiki_full | 128 | 10 | 0.078 | 0.000 | 0.017 | 0.123 | 0.079 | 0.092 |
| colour | proxy:wiki_lead | 128 | 10 | 0.062 | 0.000 | 0.018 | 0.109 | 0.079 | 0.091 |
| colour | proxy:wiki_plot | 127 | 10 | 0.060 | 0.000 | 0.020 | 0.107 | 0.079 | 0.096 |
| colour | proxy:wiki_style | 60 | 10 | -0.017 | 0.000 | 0.052 | 0.162 | 0.169 | 0.195 |
| time | motion:mid:mean | 128 | 10 | 0.101 | 0.000 | 0.021 | 0.141 | 0.079 | 0.092 |
| time | sound:mid:mean | 72 | 10 | 0.016 | 0.000 | 0.031 | 0.156 | 0.141 | 0.164 |
| time | words | 72 | 10 | 0.138 | 0.000 | 0.035 | 0.185 | 0.141 | 0.165 |
| time | fused | 72 | 10 | 0.554 | 0.000 | 0.026 | 0.436 | 0.141 | 0.165 |
| time | fused:look+time | 128 | 10 | 0.863 | 0.000 | 0.017 | 0.516 | 0.079 | 0.093 |
| time | proxy:facts | 128 | 10 | 0.054 | 0.000 | 0.025 | 0.116 | 0.079 | 0.091 |
| time | proxy:label_cast | 128 | 10 | 0.032 | 0.000 | 0.014 | 0.107 | 0.079 | 0.094 |
| time | proxy:label_decade_country | 128 | 10 | 0.172 | 0.000 | 0.018 | 0.109 | 0.079 | 0.091 |
| time | proxy:label_director | 128 | 10 | 0.006 | 0.000 | 0.014 | 0.083 | 0.079 | 0.093 |
| time | proxy:label_genre | 128 | 10 | 0.183 | 0.000 | 0.022 | 0.135 | 0.079 | 0.094 |
| time | proxy:llm_felt | 128 | 10 | 0.041 | 0.000 | 0.021 | 0.107 | 0.079 | 0.094 |
| time | proxy:llm_style | 128 | 10 | 0.120 | 0.000 | 0.018 | 0.130 | 0.079 | 0.093 |
| time | proxy:llm_style_high | 37 | 10 | 0.016 | 0.000 | 0.060 | 0.327 | 0.278 | 0.322 |
| time | proxy:llm_style_low | 18 | 10 | 0.067 | 0.000 | 0.136 | 0.567 | 0.588 | 0.644 |
| time | proxy:llm_style_medium | 73 | 10 | 0.128 | 0.000 | 0.043 | 0.147 | 0.139 | 0.166 |
| time | proxy:wiki_full | 128 | 10 | 0.088 | 0.000 | 0.021 | 0.122 | 0.079 | 0.093 |
| time | proxy:wiki_lead | 128 | 10 | 0.095 | 0.000 | 0.017 | 0.130 | 0.079 | 0.093 |
| time | proxy:wiki_plot | 127 | 10 | 0.061 | 0.000 | 0.018 | 0.115 | 0.079 | 0.094 |
| time | proxy:wiki_style | 60 | 10 | 0.028 | 0.000 | 0.045 | 0.198 | 0.169 | 0.198 |
| motion:mid:mean | sound:mid:mean | 72 | 10 | 0.128 | 0.000 | 0.031 | 0.203 | 0.141 | 0.165 |
| motion:mid:mean | words | 72 | 10 | 0.074 | 0.000 | 0.033 | 0.168 | 0.141 | 0.164 |
| motion:mid:mean | fused | 72 | 10 | 0.201 | 0.000 | 0.033 | 0.244 | 0.141 | 0.170 |
| motion:mid:mean | fused:look+time | 128 | 10 | 0.240 | 0.000 | 0.018 | 0.248 | 0.079 | 0.095 |
| motion:mid:mean | proxy:facts | 128 | 10 | 0.160 | 0.000 | 0.023 | 0.180 | 0.079 | 0.094 |
| motion:mid:mean | proxy:label_cast | 128 | 10 | 0.044 | 0.000 | 0.036 | 0.123 | 0.079 | 0.094 |
| motion:mid:mean | proxy:label_decade_country | 128 | 10 | 0.110 | 0.000 | 0.017 | 0.141 | 0.079 | 0.091 |
| motion:mid:mean | proxy:label_director | 128 | 10 | -0.002 | 0.000 | 0.028 | 0.098 | 0.079 | 0.084 |
| motion:mid:mean | proxy:label_genre | 128 | 10 | 0.168 | 0.000 | 0.019 | 0.150 | 0.079 | 0.093 |
| motion:mid:mean | proxy:llm_felt | 128 | 10 | 0.071 | 0.000 | 0.016 | 0.141 | 0.079 | 0.094 |
| motion:mid:mean | proxy:llm_style | 128 | 10 | 0.156 | 0.000 | 0.018 | 0.198 | 0.079 | 0.093 |
| motion:mid:mean | proxy:llm_style_high | 37 | 10 | 0.113 | 0.000 | 0.051 | 0.351 | 0.278 | 0.316 |
| motion:mid:mean | proxy:llm_style_low | 18 | 10 | 0.033 | 0.000 | 0.150 | 0.550 | 0.588 | 0.639 |
| motion:mid:mean | proxy:llm_style_medium | 73 | 10 | 0.178 | 0.000 | 0.031 | 0.225 | 0.139 | 0.163 |
| motion:mid:mean | proxy:wiki_full | 128 | 10 | 0.113 | 0.000 | 0.019 | 0.180 | 0.079 | 0.092 |
| motion:mid:mean | proxy:wiki_lead | 128 | 10 | 0.110 | 0.000 | 0.020 | 0.158 | 0.079 | 0.092 |
| motion:mid:mean | proxy:wiki_plot | 127 | 10 | 0.078 | 0.000 | 0.018 | 0.151 | 0.079 | 0.094 |
| motion:mid:mean | proxy:wiki_style | 60 | 10 | 0.035 | 0.000 | 0.044 | 0.172 | 0.169 | 0.202 |
| sound:mid:mean | words | 72 | 10 | 0.228 | 0.000 | 0.030 | 0.250 | 0.141 | 0.167 |
| sound:mid:mean | fused | 72 | 10 | 0.566 | 0.000 | 0.038 | 0.472 | 0.141 | 0.168 |
| sound:mid:mean | fused:look+time | 72 | 10 | 0.130 | 0.000 | 0.031 | 0.217 | 0.141 | 0.164 |
| sound:mid:mean | proxy:facts | 72 | 10 | 0.049 | 0.000 | 0.035 | 0.174 | 0.141 | 0.170 |
| sound:mid:mean | proxy:label_cast | 72 | 10 | 0.040 | 0.000 | 0.026 | 0.165 | 0.141 | 0.168 |
| sound:mid:mean | proxy:label_decade_country | 72 | 10 | 0.148 | 0.000 | 0.026 | 0.225 | 0.141 | 0.168 |
| sound:mid:mean | proxy:label_director | 72 | 10 | -0.011 | 0.000 | 0.037 | 0.151 | 0.141 | 0.161 |
| sound:mid:mean | proxy:label_genre | 72 | 10 | 0.118 | 0.000 | 0.037 | 0.214 | 0.141 | 0.165 |
| sound:mid:mean | proxy:llm_felt | 72 | 10 | 0.104 | 0.000 | 0.032 | 0.213 | 0.141 | 0.164 |
| sound:mid:mean | proxy:llm_style | 72 | 10 | 0.136 | 0.000 | 0.032 | 0.219 | 0.141 | 0.165 |
| sound:mid:mean | proxy:llm_style_high | 8 | 6 | -0.070 | 0.000 | 0.308 | 0.896 | 0.857 | 0.896 |
| sound:mid:mean | proxy:llm_style_low | 14 | 10 | 0.139 | 0.000 | 0.176 | 0.786 | 0.769 | 0.807 |
| sound:mid:mean | proxy:llm_style_medium | 50 | 10 | 0.165 | 0.000 | 0.044 | 0.298 | 0.204 | 0.238 |
| sound:mid:mean | proxy:wiki_full | 72 | 10 | 0.172 | 0.000 | 0.028 | 0.236 | 0.141 | 0.167 |
| sound:mid:mean | proxy:wiki_lead | 72 | 10 | 0.152 | 0.000 | 0.027 | 0.215 | 0.141 | 0.165 |
| sound:mid:mean | proxy:wiki_plot | 71 | 10 | 0.108 | 0.000 | 0.030 | 0.197 | 0.143 | 0.172 |
| sound:mid:mean | proxy:wiki_style | 28 | 10 | 0.139 | 0.000 | 0.073 | 0.454 | 0.370 | 0.411 |
| words | fused | 72 | 10 | 0.377 | 0.000 | 0.038 | 0.328 | 0.141 | 0.162 |
| words | fused:look+time | 72 | 10 | 0.358 | 0.000 | 0.043 | 0.272 | 0.141 | 0.164 |
| words | proxy:facts | 72 | 10 | 0.082 | 0.000 | 0.044 | 0.169 | 0.141 | 0.167 |
| words | proxy:label_cast | 72 | 10 | 0.067 | 0.000 | 0.036 | 0.210 | 0.141 | 0.161 |
| words | proxy:label_decade_country | 72 | 10 | 0.082 | 0.000 | 0.034 | 0.163 | 0.141 | 0.163 |
| words | proxy:label_director | 72 | 10 | -0.001 | 0.000 | 0.034 | 0.151 | 0.141 | 0.165 |
| words | proxy:label_genre | 72 | 10 | 0.146 | 0.000 | 0.039 | 0.274 | 0.141 | 0.165 |
| words | proxy:llm_felt | 72 | 10 | 0.148 | 0.000 | 0.038 | 0.246 | 0.141 | 0.167 |
| words | proxy:llm_style | 72 | 10 | 0.230 | 0.000 | 0.033 | 0.262 | 0.141 | 0.164 |
| words | proxy:llm_style_high | 8 | 6 | -0.010 | 0.000 | 0.349 | 0.875 | 0.857 | 0.896 |
| words | proxy:llm_style_low | 14 | 10 | 0.371 | 0.000 | 0.152 | 0.800 | 0.769 | 0.800 |
| words | proxy:llm_style_medium | 50 | 10 | 0.217 | 0.000 | 0.048 | 0.316 | 0.204 | 0.240 |
| words | proxy:wiki_full | 72 | 10 | 0.432 | 0.000 | 0.041 | 0.372 | 0.141 | 0.168 |
| words | proxy:wiki_lead | 72 | 10 | 0.209 | 0.000 | 0.039 | 0.243 | 0.141 | 0.168 |
| words | proxy:wiki_plot | 71 | 10 | 0.482 | 0.000 | 0.034 | 0.413 | 0.143 | 0.168 |
| words | proxy:wiki_style | 28 | 10 | 0.126 | 0.000 | 0.079 | 0.418 | 0.370 | 0.414 |
| fused | fused:look+time | 72 | 10 | 0.724 | 0.000 | 0.025 | 0.632 | 0.141 | 0.161 |
| fused | proxy:facts | 72 | 10 | 0.074 | 0.000 | 0.034 | 0.176 | 0.141 | 0.164 |
| fused | proxy:label_cast | 72 | 10 | 0.094 | 0.000 | 0.028 | 0.207 | 0.141 | 0.165 |
| fused | proxy:label_decade_country | 72 | 10 | 0.112 | 0.000 | 0.029 | 0.228 | 0.141 | 0.164 |
| fused | proxy:label_director | 72 | 10 | 0.002 | 0.000 | 0.030 | 0.160 | 0.141 | 0.160 |
| fused | proxy:label_genre | 72 | 10 | 0.130 | 0.000 | 0.030 | 0.235 | 0.141 | 0.165 |
| fused | proxy:llm_felt | 72 | 10 | 0.111 | 0.000 | 0.038 | 0.242 | 0.141 | 0.164 |
| fused | proxy:llm_style | 72 | 10 | 0.235 | 0.000 | 0.035 | 0.262 | 0.141 | 0.165 |
| fused | proxy:llm_style_high | 8 | 6 | 0.205 | 0.000 | 0.367 | 0.833 | 0.857 | 0.897 |
| fused | proxy:llm_style_low | 14 | 10 | 0.230 | 0.000 | 0.211 | 0.736 | 0.769 | 0.807 |
| fused | proxy:llm_style_medium | 50 | 10 | 0.265 | 0.000 | 0.054 | 0.330 | 0.204 | 0.236 |
| fused | proxy:wiki_full | 72 | 10 | 0.286 | 0.000 | 0.029 | 0.307 | 0.141 | 0.168 |
| fused | proxy:wiki_lead | 72 | 10 | 0.203 | 0.000 | 0.029 | 0.274 | 0.141 | 0.162 |
| fused | proxy:wiki_plot | 71 | 10 | 0.213 | 0.000 | 0.036 | 0.255 | 0.143 | 0.166 |
| fused | proxy:wiki_style | 28 | 10 | 0.065 | 0.000 | 0.083 | 0.404 | 0.370 | 0.414 |
| fused:look+time | proxy:facts | 128 | 10 | 0.105 | 0.000 | 0.024 | 0.141 | 0.079 | 0.092 |
| fused:look+time | proxy:label_cast | 128 | 10 | 0.077 | 0.000 | 0.014 | 0.152 | 0.079 | 0.097 |
| fused:look+time | proxy:label_decade_country | 128 | 10 | 0.273 | 0.000 | 0.019 | 0.180 | 0.079 | 0.097 |
| fused:look+time | proxy:label_director | 128 | 10 | 0.016 | 0.000 | 0.015 | 0.106 | 0.079 | 0.100 |
| fused:look+time | proxy:label_genre | 128 | 10 | 0.286 | 0.000 | 0.021 | 0.174 | 0.079 | 0.095 |
| fused:look+time | proxy:llm_felt | 128 | 10 | 0.093 | 0.000 | 0.021 | 0.138 | 0.079 | 0.095 |
| fused:look+time | proxy:llm_style | 128 | 10 | 0.251 | 0.000 | 0.018 | 0.191 | 0.079 | 0.092 |
| fused:look+time | proxy:llm_style_high | 37 | 10 | 0.146 | 0.000 | 0.056 | 0.389 | 0.278 | 0.316 |
| fused:look+time | proxy:llm_style_low | 18 | 10 | 0.176 | 0.000 | 0.153 | 0.622 | 0.588 | 0.645 |
| fused:look+time | proxy:llm_style_medium | 73 | 10 | 0.261 | 0.000 | 0.039 | 0.238 | 0.139 | 0.168 |
| fused:look+time | proxy:wiki_full | 128 | 10 | 0.241 | 0.000 | 0.016 | 0.223 | 0.079 | 0.095 |
| fused:look+time | proxy:wiki_lead | 128 | 10 | 0.207 | 0.000 | 0.017 | 0.200 | 0.079 | 0.094 |
| fused:look+time | proxy:wiki_plot | 127 | 10 | 0.172 | 0.000 | 0.017 | 0.180 | 0.079 | 0.093 |
| fused:look+time | proxy:wiki_style | 60 | 10 | 0.063 | 0.000 | 0.044 | 0.220 | 0.169 | 0.207 |
| proxy:facts | proxy:label_cast | 129 | 10 | 0.085 | 0.000 | 0.030 | 0.144 | 0.078 | 0.094 |
| proxy:facts | proxy:label_decade_country | 129 | 10 | 0.143 | 0.000 | 0.017 | 0.171 | 0.078 | 0.095 |
| proxy:facts | proxy:label_director | 129 | 10 | 0.016 | 0.000 | 0.023 | 0.102 | 0.078 | 0.093 |
| proxy:facts | proxy:label_genre | 129 | 10 | 0.099 | 0.000 | 0.022 | 0.113 | 0.078 | 0.096 |
| proxy:facts | proxy:llm_felt | 129 | 10 | 0.043 | 0.000 | 0.018 | 0.114 | 0.078 | 0.093 |
| proxy:facts | proxy:llm_style | 129 | 10 | 0.069 | 0.000 | 0.017 | 0.139 | 0.078 | 0.092 |
| proxy:facts | proxy:llm_style_high | 37 | 10 | 0.079 | 0.000 | 0.063 | 0.330 | 0.278 | 0.316 |
| proxy:facts | proxy:llm_style_low | 19 | 10 | 0.118 | 0.000 | 0.126 | 0.568 | 0.556 | 0.605 |
| proxy:facts | proxy:llm_style_medium | 73 | 10 | 0.027 | 0.000 | 0.032 | 0.195 | 0.139 | 0.163 |
| proxy:facts | proxy:wiki_full | 129 | 10 | 0.152 | 0.000 | 0.013 | 0.165 | 0.078 | 0.093 |
| proxy:facts | proxy:wiki_lead | 129 | 10 | 0.116 | 0.000 | 0.018 | 0.160 | 0.078 | 0.093 |
| proxy:facts | proxy:wiki_plot | 128 | 10 | 0.074 | 0.000 | 0.019 | 0.129 | 0.079 | 0.096 |
| proxy:facts | proxy:wiki_style | 61 | 10 | 0.037 | 0.000 | 0.037 | 0.215 | 0.167 | 0.192 |
| proxy:label_cast | proxy:label_decade_country | 129 | 10 | 0.066 | 0.000 | 0.019 | 0.194 | 0.078 | 0.116 |
| proxy:label_cast | proxy:label_director | 129 | 10 | 0.104 | 0.000 | 0.059 | 0.225 | 0.078 | 0.150 |
| proxy:label_cast | proxy:label_genre | 129 | 10 | 0.038 | 0.000 | 0.017 | 0.157 | 0.078 | 0.100 |
| proxy:label_cast | proxy:llm_felt | 129 | 10 | 0.027 | 0.000 | 0.015 | 0.125 | 0.078 | 0.093 |
| proxy:label_cast | proxy:llm_style | 129 | 10 | 0.055 | 0.000 | 0.012 | 0.135 | 0.078 | 0.092 |
| proxy:label_cast | proxy:llm_style_high | 37 | 10 | 0.090 | 0.000 | 0.049 | 0.305 | 0.278 | 0.314 |
| proxy:label_cast | proxy:llm_style_low | 19 | 10 | 0.103 | 0.000 | 0.094 | 0.563 | 0.556 | 0.595 |
| proxy:label_cast | proxy:llm_style_medium | 73 | 10 | 0.042 | 0.000 | 0.024 | 0.186 | 0.139 | 0.159 |
| proxy:label_cast | proxy:wiki_full | 129 | 10 | 0.083 | 0.000 | 0.014 | 0.197 | 0.078 | 0.092 |
| proxy:label_cast | proxy:wiki_lead | 129 | 10 | 0.071 | 0.000 | 0.015 | 0.176 | 0.078 | 0.091 |
| proxy:label_cast | proxy:wiki_plot | 128 | 10 | 0.040 | 0.000 | 0.014 | 0.121 | 0.079 | 0.091 |
| proxy:label_cast | proxy:wiki_style | 61 | 10 | 0.050 | 0.000 | 0.034 | 0.179 | 0.167 | 0.195 |
| proxy:label_decade_country | proxy:label_director | 129 | 10 | 0.019 | 0.000 | 0.023 | 0.140 | 0.078 | 0.129 |
| proxy:label_decade_country | proxy:label_genre | 129 | 10 | 0.360 | 0.000 | 0.020 | 0.191 | 0.078 | 0.095 |
| proxy:label_decade_country | proxy:llm_felt | 129 | 10 | 0.029 | 0.000 | 0.018 | 0.112 | 0.078 | 0.092 |
| proxy:label_decade_country | proxy:llm_style | 129 | 10 | 0.149 | 0.000 | 0.016 | 0.145 | 0.078 | 0.091 |
| proxy:label_decade_country | proxy:llm_style_high | 37 | 10 | 0.095 | 0.000 | 0.051 | 0.373 | 0.278 | 0.322 |
| proxy:label_decade_country | proxy:llm_style_low | 19 | 10 | 0.082 | 0.000 | 0.089 | 0.568 | 0.556 | 0.600 |
| proxy:label_decade_country | proxy:llm_style_medium | 73 | 10 | 0.103 | 0.000 | 0.027 | 0.203 | 0.139 | 0.162 |
| proxy:label_decade_country | proxy:wiki_full | 129 | 10 | 0.239 | 0.000 | 0.019 | 0.210 | 0.078 | 0.091 |
| proxy:label_decade_country | proxy:wiki_lead | 129 | 10 | 0.249 | 0.000 | 0.020 | 0.212 | 0.078 | 0.095 |
| proxy:label_decade_country | proxy:wiki_plot | 128 | 10 | 0.081 | 0.000 | 0.021 | 0.136 | 0.079 | 0.093 |
| proxy:label_decade_country | proxy:wiki_style | 61 | 10 | 0.103 | 0.000 | 0.039 | 0.241 | 0.167 | 0.194 |
| proxy:label_director | proxy:label_genre | 129 | 10 | 0.030 | 0.000 | 0.021 | 0.105 | 0.078 | 0.107 |
| proxy:label_director | proxy:llm_felt | 129 | 10 | 0.029 | 0.000 | 0.018 | 0.099 | 0.078 | 0.091 |
| proxy:label_director | proxy:llm_style | 129 | 10 | 0.013 | 0.000 | 0.014 | 0.109 | 0.078 | 0.090 |
| proxy:label_director | proxy:llm_style_high | 37 | 10 | 0.030 | 0.000 | 0.054 | 0.322 | 0.278 | 0.311 |
| proxy:label_director | proxy:llm_style_low | 19 | 10 | -0.029 | 0.000 | 0.110 | 0.521 | 0.556 | 0.595 |
| proxy:label_director | proxy:llm_style_medium | 73 | 10 | 0.012 | 0.000 | 0.029 | 0.125 | 0.139 | 0.156 |
| proxy:label_director | proxy:wiki_full | 129 | 10 | 0.033 | 0.000 | 0.016 | 0.137 | 0.078 | 0.092 |
| proxy:label_director | proxy:wiki_lead | 129 | 10 | 0.048 | 0.000 | 0.017 | 0.152 | 0.078 | 0.094 |
| proxy:label_director | proxy:wiki_plot | 128 | 10 | 0.001 | 0.000 | 0.016 | 0.088 | 0.079 | 0.091 |
| proxy:label_director | proxy:wiki_style | 61 | 10 | -0.009 | 0.000 | 0.045 | 0.172 | 0.167 | 0.197 |
| proxy:label_genre | proxy:llm_felt | 129 | 10 | 0.202 | 0.000 | 0.017 | 0.199 | 0.078 | 0.092 |
| proxy:label_genre | proxy:llm_style | 129 | 10 | 0.189 | 0.000 | 0.018 | 0.178 | 0.078 | 0.092 |
| proxy:label_genre | proxy:llm_style_high | 37 | 10 | 0.085 | 0.000 | 0.053 | 0.300 | 0.278 | 0.314 |
| proxy:label_genre | proxy:llm_style_low | 19 | 10 | 0.074 | 0.000 | 0.108 | 0.574 | 0.556 | 0.595 |
| proxy:label_genre | proxy:llm_style_medium | 73 | 10 | 0.172 | 0.000 | 0.028 | 0.225 | 0.139 | 0.163 |
| proxy:label_genre | proxy:wiki_full | 129 | 10 | 0.238 | 0.000 | 0.020 | 0.229 | 0.078 | 0.092 |
| proxy:label_genre | proxy:wiki_lead | 129 | 10 | 0.246 | 0.000 | 0.021 | 0.209 | 0.078 | 0.095 |
| proxy:label_genre | proxy:wiki_plot | 128 | 10 | 0.127 | 0.000 | 0.016 | 0.144 | 0.079 | 0.094 |
| proxy:label_genre | proxy:wiki_style | 61 | 10 | 0.107 | 0.000 | 0.036 | 0.262 | 0.167 | 0.193 |
| proxy:llm_felt | proxy:llm_style | 129 | 10 | 0.133 | 0.000 | 0.017 | 0.185 | 0.078 | 0.093 |
| proxy:llm_felt | proxy:llm_style_high | 37 | 10 | 0.170 | 0.000 | 0.056 | 0.362 | 0.278 | 0.314 |
| proxy:llm_felt | proxy:llm_style_low | 19 | 10 | 0.203 | 0.000 | 0.133 | 0.626 | 0.556 | 0.611 |
| proxy:llm_felt | proxy:llm_style_medium | 73 | 10 | 0.113 | 0.000 | 0.035 | 0.197 | 0.139 | 0.163 |
| proxy:llm_felt | proxy:wiki_full | 129 | 10 | 0.169 | 0.000 | 0.019 | 0.189 | 0.078 | 0.092 |
| proxy:llm_felt | proxy:wiki_lead | 129 | 10 | 0.148 | 0.000 | 0.020 | 0.195 | 0.078 | 0.092 |
| proxy:llm_felt | proxy:wiki_plot | 128 | 10 | 0.122 | 0.000 | 0.017 | 0.147 | 0.079 | 0.094 |
| proxy:llm_felt | proxy:wiki_style | 61 | 10 | 0.136 | 0.000 | 0.039 | 0.220 | 0.167 | 0.195 |
| proxy:llm_style | proxy:llm_style_high | 37 | 10 | 0.964 | 0.000 | 0.067 | 0.897 | 0.278 | 0.322 |
| proxy:llm_style | proxy:llm_style_low | 19 | 10 | 0.899 | 0.000 | 0.128 | 0.926 | 0.556 | 0.611 |
| proxy:llm_style | proxy:llm_style_medium | 73 | 10 | 0.991 | 0.000 | 0.034 | 0.930 | 0.139 | 0.166 |
| proxy:llm_style | proxy:wiki_full | 129 | 10 | 0.260 | 0.000 | 0.019 | 0.225 | 0.078 | 0.092 |
| proxy:llm_style | proxy:wiki_lead | 129 | 10 | 0.173 | 0.000 | 0.017 | 0.188 | 0.078 | 0.095 |
| proxy:llm_style | proxy:wiki_plot | 128 | 10 | 0.204 | 0.000 | 0.015 | 0.169 | 0.079 | 0.091 |
| proxy:llm_style | proxy:wiki_style | 61 | 10 | 0.092 | 0.000 | 0.043 | 0.238 | 0.167 | 0.197 |
| proxy:llm_style_high | proxy:wiki_full | 37 | 10 | 0.281 | 0.000 | 0.060 | 0.403 | 0.278 | 0.324 |
| proxy:llm_style_high | proxy:wiki_lead | 37 | 10 | 0.143 | 0.000 | 0.048 | 0.357 | 0.278 | 0.319 |
| proxy:llm_style_high | proxy:wiki_plot | 37 | 10 | 0.227 | 0.000 | 0.068 | 0.368 | 0.278 | 0.322 |
| proxy:llm_style_high | proxy:wiki_style | 28 | 10 | 0.090 | 0.000 | 0.087 | 0.364 | 0.370 | 0.422 |
| proxy:llm_style_low | proxy:wiki_full | 19 | 10 | 0.218 | 0.000 | 0.123 | 0.605 | 0.556 | 0.616 |
| proxy:llm_style_low | proxy:wiki_lead | 19 | 10 | 0.134 | 0.000 | 0.102 | 0.584 | 0.556 | 0.605 |
| proxy:llm_style_low | proxy:wiki_plot | 19 | 10 | 0.208 | 0.000 | 0.136 | 0.605 | 0.556 | 0.611 |
| proxy:llm_style_medium | proxy:wiki_full | 73 | 10 | 0.257 | 0.000 | 0.030 | 0.288 | 0.139 | 0.160 |
| proxy:llm_style_medium | proxy:wiki_lead | 73 | 10 | 0.157 | 0.000 | 0.028 | 0.234 | 0.139 | 0.160 |
| proxy:llm_style_medium | proxy:wiki_plot | 72 | 10 | 0.191 | 0.000 | 0.030 | 0.242 | 0.141 | 0.165 |
| proxy:llm_style_medium | proxy:wiki_style | 30 | 10 | 0.125 | 0.000 | 0.119 | 0.427 | 0.345 | 0.403 |
| proxy:wiki_full | proxy:wiki_lead | 129 | 10 | 0.498 | 0.000 | 0.016 | 0.388 | 0.078 | 0.094 |
| proxy:wiki_full | proxy:wiki_plot | 128 | 10 | 0.469 | 0.000 | 0.019 | 0.297 | 0.079 | 0.094 |
| proxy:wiki_full | proxy:wiki_style | 61 | 10 | 0.278 | 0.000 | 0.034 | 0.330 | 0.167 | 0.192 |
| proxy:wiki_lead | proxy:wiki_plot | 128 | 10 | 0.171 | 0.000 | 0.020 | 0.157 | 0.079 | 0.094 |
| proxy:wiki_lead | proxy:wiki_style | 61 | 10 | 0.142 | 0.000 | 0.033 | 0.277 | 0.167 | 0.194 |
| proxy:wiki_plot | proxy:wiki_style | 61 | 10 | 0.100 | 0.000 | 0.043 | 0.257 | 0.167 | 0.197 |

## 2. Pooling

### look

| block A | block B | films | k | Spearman | chance | shuffled p95 | top-k overlap | chance k/(n-1) | shuffled p95 |
|---|---|---|---|---|---|---|---|---|---|
| look:mean | look:mean+std | 128 | 10 | 0.957 | 0.000 | 0.019 | 0.861 | 0.079 | 0.096 |
| look:mean | look:profile8 | 128 | 10 | 0.974 | 0.000 | 0.019 | 0.802 | 0.079 | 0.093 |
| look:mean | look:patchmean | 128 | 10 | 0.888 | 0.000 | 0.018 | 0.684 | 0.079 | 0.097 |
| look:mean | look_grid | 128 | 10 | 0.963 | 0.000 | 0.018 | 0.795 | 0.079 | 0.096 |
| look:mean+std | look:profile8 | 128 | 10 | 0.942 | 0.000 | 0.019 | 0.761 | 0.079 | 0.095 |
| look:mean+std | look:patchmean | 128 | 10 | 0.876 | 0.000 | 0.018 | 0.682 | 0.079 | 0.097 |
| look:mean+std | look_grid | 128 | 10 | 0.918 | 0.000 | 0.021 | 0.754 | 0.079 | 0.094 |
| look:profile8 | look:patchmean | 128 | 10 | 0.872 | 0.000 | 0.018 | 0.664 | 0.079 | 0.097 |
| look:profile8 | look_grid | 128 | 10 | 0.949 | 0.000 | 0.019 | 0.745 | 0.079 | 0.095 |
| look:patchmean | look_grid | 128 | 10 | 0.879 | 0.000 | 0.019 | 0.666 | 0.079 | 0.093 |

### time

| block A | block B | films | k | Spearman | chance | shuffled p95 | top-k overlap | chance k/(n-1) | shuffled p95 |
|---|---|---|---|---|---|---|---|---|---|
| time | time_sl | 128 | 10 | 0.769 | 0.000 | 0.018 | 0.304 | 0.079 | 0.089 |

### motion

| block A | block B | films | k | Spearman | chance | shuffled p95 | top-k overlap | chance k/(n-1) | shuffled p95 |
|---|---|---|---|---|---|---|---|---|---|
| motion:mid:mean | motion:mid:mean+std | 128 | 10 | 0.977 | 0.000 | 0.021 | 0.848 | 0.079 | 0.094 |
| motion:mid:mean | motion:last:mean | 128 | 10 | 0.836 | 0.000 | 0.024 | 0.591 | 0.079 | 0.094 |
| motion:mid:mean+std | motion:last:mean | 128 | 10 | 0.822 | 0.000 | 0.024 | 0.586 | 0.079 | 0.095 |

### sound

| block A | block B | films | k | Spearman | chance | shuffled p95 | top-k overlap | chance k/(n-1) | shuffled p95 |
|---|---|---|---|---|---|---|---|---|---|
| sound:mid:mean | sound:mid:mean+std | 72 | 10 | 0.988 | 0.000 | 0.035 | 0.910 | 0.141 | 0.165 |
| sound:mid:mean | sound:last_c:mean | 72 | 10 | 0.721 | 0.000 | 0.033 | 0.617 | 0.141 | 0.164 |
| sound:mid:mean | sound:last_c:mean+std | 72 | 10 | 0.735 | 0.000 | 0.034 | 0.625 | 0.141 | 0.165 |
| sound:mid:mean | sound:mid:mean+stats | 72 | 10 | 0.556 | 0.000 | 0.037 | 0.475 | 0.141 | 0.168 |
| sound:mid:mean | sound:stats | 72 | 10 | 0.285 | 0.000 | 0.041 | 0.297 | 0.141 | 0.165 |
| sound:mid:mean+std | sound:last_c:mean | 72 | 10 | 0.714 | 0.000 | 0.032 | 0.619 | 0.141 | 0.167 |
| sound:mid:mean+std | sound:last_c:mean+std | 72 | 10 | 0.734 | 0.000 | 0.032 | 0.633 | 0.141 | 0.168 |
| sound:mid:mean+std | sound:mid:mean+stats | 72 | 10 | 0.554 | 0.000 | 0.037 | 0.475 | 0.141 | 0.167 |
| sound:mid:mean+std | sound:stats | 72 | 10 | 0.286 | 0.000 | 0.038 | 0.292 | 0.141 | 0.167 |
| sound:last_c:mean | sound:last_c:mean+std | 72 | 10 | 0.992 | 0.000 | 0.031 | 0.924 | 0.141 | 0.165 |
| sound:last_c:mean | sound:mid:mean+stats | 72 | 10 | 0.406 | 0.000 | 0.036 | 0.392 | 0.141 | 0.160 |
| sound:last_c:mean | sound:stats | 72 | 10 | 0.205 | 0.000 | 0.032 | 0.249 | 0.141 | 0.163 |
| sound:last_c:mean+std | sound:mid:mean+stats | 72 | 10 | 0.414 | 0.000 | 0.033 | 0.404 | 0.141 | 0.161 |
| sound:last_c:mean+std | sound:stats | 72 | 10 | 0.209 | 0.000 | 0.032 | 0.260 | 0.141 | 0.161 |
| sound:mid:mean+stats | sound:stats | 72 | 10 | 0.950 | 0.000 | 0.035 | 0.740 | 0.141 | 0.163 |

## 3. Subsampling

### look:mean from n shot frames per film

Against the full version. Available per film: min 176, median 622, max 1500. 5 seeds; sd over seeds.

| n | mean n used | films capped | top-k overlap | sd | chance | Spearman | sd | chance |
|---|---|---|---|---|---|---|---|---|
| 3 | 3.000 | 0 | 0.283 | 0.015 | 0.079 | 0.494 | 0.040 | 0.000 |
| 5 | 5.000 | 0 | 0.375 | 0.026 | 0.079 | 0.622 | 0.016 | 0.000 |
| 10 | 10.000 | 0 | 0.512 | 0.013 | 0.079 | 0.765 | 0.003 | 0.000 |
| 20 | 20.000 | 0 | 0.641 | 0.012 | 0.079 | 0.878 | 0.005 | 0.000 |
| 40 | 40.000 | 0 | 0.724 | 0.014 | 0.079 | 0.936 | 0.009 | 0.000 |
| 80 | 80.000 | 0 | 0.805 | 0.012 | 0.079 | 0.968 | 0.003 | 0.000 |
| 160 | 160.0 | 0 | 0.872 | 0.006 | 0.079 | 0.987 | 0.001 | 0.000 |
| 320 | 313.7 | 13 | 0.923 | 0.004 | 0.079 | 0.996 | 0.000 | 0.000 |

### sound:mid:mean from n 10-s windows per film

Against the full version. Available per film: min 117, median 269, max 417. 5 seeds; sd over seeds.

| n | mean n used | films capped | top-k overlap | sd | chance | Spearman | sd | chance |
|---|---|---|---|---|---|---|---|---|
| 3 | 3.000 | 0 | 0.422 | 0.023 | 0.141 | 0.505 | 0.043 | 0.000 |
| 5 | 5.000 | 0 | 0.496 | 0.014 | 0.141 | 0.634 | 0.021 | 0.000 |
| 10 | 10.000 | 0 | 0.625 | 0.038 | 0.141 | 0.785 | 0.038 | 0.000 |
| 20 | 20.000 | 0 | 0.719 | 0.021 | 0.141 | 0.873 | 0.011 | 0.000 |
| 40 | 40.000 | 0 | 0.811 | 0.016 | 0.141 | 0.941 | 0.009 | 0.000 |
| 80 | 80.000 | 0 | 0.864 | 0.007 | 0.141 | 0.972 | 0.002 | 0.000 |
| 160 | 159.3 | 2 | 0.932 | 0.006 | 0.141 | 0.993 | 0.001 | 0.000 |
| 320 | 259.7 | 58 | 0.993 | 0.005 | 0.141 | 1.000 | 0.000 | 0.000 |

## 4. Cross-prediction

A = look:mean from 10 random shot frames per film. A reduced to PCs fitted on the training films, ridge (alpha by efficient leave-one-out inside each fold) to each standardised PC of B, leave-one-film-out. R^2 is against the training-fold mean, so 0 = no skill. Chance: the films of B shuffled, 20 times, first seed. Mean and sd over 5 draws of the stills. For the overlap the shuffled figure is the baseline to use: a leave-one-out prediction with no skill is the training mean, which mirrors the held-out film's own value and so keeps some of its neighbours, lifting the overlap above k/(n-1).

| B | films | k | A PCs | B PCs | B variance kept | mean R^2 | sd | shuffled mean | shuffled p95 | overlap pred vs true B | sd | chance k/(n-1) | shuffled mean | shuffled p95 | overlap pred vs B PCs | overlap B PCs vs true B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| time | 128 | 10 | 16 | 8 | 0.720 | 0.050 | 0.008 | -0.004 | 0.001 | 0.126 | 0.007 | 0.079 | 0.127 | 0.232 | 0.124 | 0.571 |
| sound:mid:mean | 72 | 10 | 16 | 8 | 0.613 | 0.081 | 0.019 | -0.006 | 0.012 | 0.229 | 0.025 | 0.141 | 0.203 | 0.290 | 0.221 | 0.718 |
| colour | 128 | 10 | 16 | 8 | 0.871 | 0.120 | 0.009 | -0.007 | -0.000 | 0.149 | 0.014 | 0.079 | 0.141 | 0.266 | 0.145 | 0.685 |
| words | 72 | 10 | 16 | 8 | 0.403 | 0.142 | 0.008 | -0.007 | 0.005 | 0.278 | 0.023 | 0.141 | 0.168 | 0.216 | 0.259 | 0.653 |

R^2 per component of B (mean over draws):

| B | R^2 of PC1..PCq |
|---|---|
| time | 0.197; 0.057; 0.053; 0.114; -0.002; -0.010; -0.006; -0.006 |
| sound:mid:mean | 0.191; 0.173; 0.091; 0.129; 0.009; 0.047; 0.005; 0.004 |
| colour | 0.304; 0.268; 0.207; 0.046; 0.107; 0.037; 0.002; -0.010 |
| words | 0.503; 0.211; 0.038; 0.144; 0.054; 0.135; -0.013; 0.062 |

The measures of experiment 1 for look from 10 stills against each block (shuffled p95 from the first draw):

| block B | films | k | Spearman | sd | chance | shuffled p95 | top-k overlap | sd | chance k/(n-1) | shuffled p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| time | 128 | 10 | 0.144 | 0.018 | 0.000 | 0.018 | 0.132 | 0.010 | 0.079 | 0.094 |
| sound:mid:mean | 72 | 10 | 0.174 | 0.008 | 0.000 | 0.034 | 0.226 | 0.009 | 0.141 | 0.165 |
| colour | 128 | 10 | 0.185 | 0.020 | 0.000 | 0.020 | 0.157 | 0.005 | 0.079 | 0.092 |
| words | 72 | 10 | 0.340 | 0.030 | 0.000 | 0.027 | 0.291 | 0.008 | 0.141 | 0.170 |
| look:mean | 128 | 10 | 0.760 | 0.004 | 0.000 | 0.017 | 0.513 | 0.013 | 0.079 | 0.093 |
| look:mean+std | 128 | 10 | 0.748 | 0.007 | 0.000 | 0.017 | 0.500 | 0.013 | 0.079 | 0.094 |
| look:profile8 | 128 | 10 | 0.747 | 0.005 | 0.000 | 0.018 | 0.500 | 0.013 | 0.079 | 0.093 |
| look:patchmean | 128 | 10 | 0.685 | 0.012 | 0.000 | 0.017 | 0.460 | 0.014 | 0.079 | 0.095 |
| look_grid | 128 | 10 | 0.727 | 0.008 | 0.000 | 0.018 | 0.485 | 0.008 | 0.079 | 0.095 |
| time_sl | 128 | 10 | 0.122 | 0.020 | 0.000 | 0.020 | 0.125 | 0.010 | 0.079 | 0.095 |
| motion:mid:mean | 128 | 10 | 0.249 | 0.008 | 0.000 | 0.016 | 0.244 | 0.006 | 0.079 | 0.095 |
| motion:mid:mean+std | 128 | 10 | 0.291 | 0.009 | 0.000 | 0.017 | 0.245 | 0.005 | 0.079 | 0.094 |
| motion:last:mean | 128 | 10 | 0.237 | 0.006 | 0.000 | 0.018 | 0.252 | 0.010 | 0.079 | 0.094 |
| sound:mid:mean+std | 72 | 10 | 0.182 | 0.011 | 0.000 | 0.033 | 0.232 | 0.006 | 0.141 | 0.163 |
| sound:last_c:mean | 72 | 10 | 0.099 | 0.011 | 0.000 | 0.038 | 0.196 | 0.008 | 0.141 | 0.167 |
| sound:last_c:mean+std | 72 | 10 | 0.106 | 0.012 | 0.000 | 0.039 | 0.195 | 0.012 | 0.141 | 0.165 |
| sound:stats | 72 | 10 | 0.034 | 0.011 | 0.000 | 0.038 | 0.146 | 0.004 | 0.141 | 0.169 |
| sound:mid:mean+stats | 72 | 10 | 0.084 | 0.009 | 0.000 | 0.040 | 0.177 | 0.005 | 0.141 | 0.172 |
| proxy:facts | 128 | 10 | 0.099 | 0.015 | 0.000 | 0.020 | 0.127 | 0.005 | 0.079 | 0.094 |
| proxy:label_cast | 128 | 10 | 0.085 | 0.010 | 0.000 | 0.014 | 0.143 | 0.009 | 0.079 | 0.091 |
| proxy:label_decade_country | 128 | 10 | 0.196 | 0.021 | 0.000 | 0.017 | 0.145 | 0.007 | 0.079 | 0.090 |
| proxy:label_director | 128 | 10 | 0.004 | 0.008 | 0.000 | 0.018 | 0.108 | 0.009 | 0.079 | 0.088 |
| proxy:label_genre | 128 | 10 | 0.204 | 0.015 | 0.000 | 0.022 | 0.169 | 0.005 | 0.079 | 0.092 |
| proxy:llm_felt | 128 | 10 | 0.090 | 0.005 | 0.000 | 0.017 | 0.137 | 0.009 | 0.079 | 0.091 |
| proxy:llm_style | 128 | 10 | 0.247 | 0.004 | 0.000 | 0.020 | 0.188 | 0.005 | 0.079 | 0.091 |
| proxy:llm_style_high | 37 | 10 | 0.254 | 0.038 | 0.000 | 0.056 | 0.397 | 0.021 | 0.278 | 0.322 |
| proxy:llm_style_low | 18 | 10 | 0.154 | 0.050 | 0.000 | 0.157 | 0.622 | 0.027 | 0.588 | 0.644 |
| proxy:llm_style_medium | 73 | 10 | 0.251 | 0.004 | 0.000 | 0.034 | 0.250 | 0.012 | 0.139 | 0.166 |
| proxy:wiki_full | 128 | 10 | 0.281 | 0.007 | 0.000 | 0.018 | 0.237 | 0.014 | 0.079 | 0.095 |
| proxy:wiki_lead | 128 | 10 | 0.208 | 0.015 | 0.000 | 0.018 | 0.188 | 0.015 | 0.079 | 0.095 |
| proxy:wiki_plot | 127 | 10 | 0.214 | 0.007 | 0.000 | 0.017 | 0.172 | 0.008 | 0.079 | 0.095 |
| proxy:wiki_style | 60 | 10 | 0.086 | 0.006 | 0.000 | 0.045 | 0.210 | 0.015 | 0.169 | 0.200 |

## 5. Leaks

Catalog films only. Each cell: value / chance.

### Share of top-k neighbours with the same attribute / share of all other films with it

| block | films | k | director | lead_actor | decade | country | silent_or_sound | colour_class | kind |
|---|---|---|---|---|---|---|---|---|---|
| look:mean | 128 | 10 | 0.048 / 0.011 | 0.054 / 0.009 | 0.478 / 0.274 | 0.652 / 0.549 | 0.816 / 0.504 | 0.702 / 0.601 | 0.836 / 0.796 |
| look:mean+std | 128 | 10 | 0.051 / 0.011 | 0.055 / 0.009 | 0.495 / 0.274 | 0.636 / 0.549 | 0.833 / 0.504 | 0.707 / 0.601 | 0.828 / 0.796 |
| look:profile8 | 128 | 10 | 0.045 / 0.011 | 0.055 / 0.009 | 0.464 / 0.274 | 0.654 / 0.549 | 0.820 / 0.504 | 0.693 / 0.601 | 0.836 / 0.796 |
| look:patchmean | 128 | 10 | 0.045 / 0.011 | 0.058 / 0.009 | 0.493 / 0.274 | 0.661 / 0.549 | 0.859 / 0.504 | 0.695 / 0.601 | 0.848 / 0.796 |
| look_grid | 128 | 10 | 0.044 / 0.011 | 0.054 / 0.009 | 0.484 / 0.274 | 0.644 / 0.549 | 0.835 / 0.504 | 0.695 / 0.601 | 0.848 / 0.796 |
| colour | 128 | 10 | 0.026 / 0.011 | 0.019 / 0.009 | 0.313 / 0.274 | 0.552 / 0.549 | 0.591 / 0.504 | 0.770 / 0.601 | 0.798 / 0.796 |
| time | 128 | 10 | 0.026 / 0.011 | 0.020 / 0.009 | 0.395 / 0.274 | 0.559 / 0.549 | 0.709 / 0.504 | 0.650 / 0.601 | 0.810 / 0.796 |
| time_sl | 128 | 10 | 0.025 / 0.011 | 0.022 / 0.009 | 0.371 / 0.274 | 0.603 / 0.549 | 0.721 / 0.504 | 0.645 / 0.601 | 0.813 / 0.796 |
| motion:mid:mean | 128 | 10 | 0.032 / 0.011 | 0.036 / 0.009 | 0.455 / 0.274 | 0.613 / 0.549 | 0.778 / 0.504 | 0.874 / 0.601 | 0.816 / 0.796 |
| motion:mid:mean+std | 128 | 10 | 0.034 / 0.011 | 0.037 / 0.009 | 0.476 / 0.274 | 0.617 / 0.549 | 0.837 / 0.504 | 0.885 / 0.601 | 0.827 / 0.796 |
| motion:last:mean | 128 | 10 | 0.023 / 0.011 | 0.024 / 0.009 | 0.460 / 0.274 | 0.623 / 0.549 | 0.816 / 0.504 | 0.880 / 0.601 | 0.826 / 0.796 |
| sound:mid:mean | 72 | 10 | 0.022 / 0.012 | 0.025 / 0.014 | 0.390 / 0.252 | 0.833 / 0.819 | 1.000 / 1.000 | 0.700 / 0.649 | 0.864 / 0.841 |
| sound:mid:mean+std | 72 | 10 | 0.024 / 0.012 | 0.024 / 0.014 | 0.400 / 0.252 | 0.833 / 0.819 | 1.000 / 1.000 | 0.694 / 0.649 | 0.858 / 0.841 |
| sound:last_c:mean | 72 | 10 | 0.017 / 0.012 | 0.018 / 0.014 | 0.319 / 0.252 | 0.835 / 0.819 | 1.000 / 1.000 | 0.656 / 0.649 | 0.862 / 0.841 |
| sound:last_c:mean+std | 72 | 10 | 0.018 / 0.012 | 0.019 / 0.014 | 0.318 / 0.252 | 0.833 / 0.819 | 1.000 / 1.000 | 0.651 / 0.649 | 0.860 / 0.841 |
| sound:stats | 72 | 10 | 0.014 / 0.012 | 0.004 / 0.014 | 0.292 / 0.252 | 0.840 / 0.819 | 1.000 / 1.000 | 0.681 / 0.649 | 0.837 / 0.841 |
| sound:mid:mean+stats | 72 | 10 | 0.019 / 0.012 | 0.014 / 0.014 | 0.353 / 0.252 | 0.839 / 0.819 | 1.000 / 1.000 | 0.686 / 0.649 | 0.846 / 0.841 |
| words | 72 | 10 | 0.021 / 0.012 | 0.035 / 0.014 | 0.282 / 0.252 | 0.851 / 0.819 | 1.000 / 1.000 | 0.654 / 0.649 | 0.860 / 0.841 |
| fused | 72 | 10 | 0.029 / 0.012 | 0.039 / 0.014 | 0.360 / 0.252 | 0.850 / 0.819 | 1.000 / 1.000 | 0.704 / 0.649 | 0.865 / 0.841 |
| fused:look+time | 128 | 10 | 0.037 / 0.011 | 0.047 / 0.009 | 0.484 / 0.274 | 0.630 / 0.549 | 0.816 / 0.504 | 0.697 / 0.601 | 0.822 / 0.796 |
| proxy:facts | 129 | 10 | 0.037 / 0.011 | 0.022 / 0.009 | 0.359 / 0.273 | 0.767 / 0.551 | 0.647 / 0.505 | 0.771 / 0.604 | 0.829 / 0.798 |
| proxy:label_cast | 129 | 10 | 0.057 / 0.011 | 0.107 / 0.009 | 0.449 / 0.273 | 0.609 / 0.551 | 0.604 / 0.505 | 0.629 / 0.604 | 0.718 / 0.798 |
| proxy:label_decade_country | 129 | 10 | 0.054 / 0.011 | 0.036 / 0.009 | 0.914 / 0.273 | 0.891 / 0.551 | 0.895 / 0.505 | 0.607 / 0.604 | 0.814 / 0.798 |
| proxy:label_director | 129 | 10 | 0.138 / 0.011 | 0.029 / 0.009 | 0.403 / 0.273 | 0.492 / 0.551 | 0.446 / 0.505 | 0.561 / 0.604 | 0.676 / 0.798 |
| proxy:label_genre | 129 | 10 | 0.035 / 0.011 | 0.037 / 0.009 | 0.499 / 0.273 | 0.631 / 0.551 | 0.848 / 0.505 | 0.694 / 0.604 | 0.848 / 0.798 |
| proxy:llm_felt | 129 | 10 | 0.043 / 0.011 | 0.040 / 0.009 | 0.314 / 0.273 | 0.587 / 0.551 | 0.545 / 0.505 | 0.652 / 0.604 | 0.828 / 0.798 |
| proxy:llm_style | 129 | 10 | 0.043 / 0.011 | 0.043 / 0.009 | 0.406 / 0.273 | 0.602 / 0.551 | 0.748 / 0.505 | 0.722 / 0.604 | 0.824 / 0.798 |
| proxy:llm_style_high | 37 | 10 | 0.043 / 0.017 | 0.041 / 0.020 | 0.554 / 0.505 | 0.386 / 0.380 | 0.708 / 0.652 | 0.722 / 0.610 | 0.727 / 0.707 |
| proxy:llm_style_low | 19 | 10 | 0.053 / 0.029 | 0.000 / 0.000 | 0.279 / 0.246 | 0.626 / 0.620 | 0.689 / 0.649 | 0.747 / 0.719 | 0.895 / 0.895 |
| proxy:llm_style_medium | 73 | 10 | 0.014 / 0.008 | 0.029 / 0.010 | 0.311 / 0.235 | 0.664 / 0.641 | 0.714 / 0.562 | 0.690 / 0.583 | 0.844 / 0.818 |
| proxy:wiki_full | 129 | 10 | 0.074 / 0.011 | 0.066 / 0.009 | 0.410 / 0.273 | 0.776 / 0.551 | 0.726 / 0.505 | 0.647 / 0.604 | 0.822 / 0.798 |
| proxy:wiki_lead | 129 | 10 | 0.088 / 0.011 | 0.066 / 0.009 | 0.450 / 0.273 | 0.740 / 0.551 | 0.740 / 0.505 | 0.654 / 0.604 | 0.822 / 0.798 |
| proxy:wiki_plot | 128 | 10 | 0.016 / 0.011 | 0.023 / 0.009 | 0.320 / 0.274 | 0.635 / 0.549 | 0.586 / 0.504 | 0.652 / 0.611 | 0.840 / 0.809 |
| proxy:wiki_style | 61 | 10 | 0.015 / 0.009 | 0.018 / 0.009 | 0.407 / 0.310 | 0.556 / 0.473 | 0.644 / 0.493 | 0.523 / 0.515 | 0.772 / 0.785 |
| look:10stills (seed 0) | 128 | 10 | 0.029 / 0.011 | 0.043 / 0.009 | 0.410 / 0.274 | 0.636 / 0.549 | 0.752 / 0.504 | 0.674 / 0.601 | 0.819 / 0.796 |

### Leave-one-out kNN accuracy / majority-class rate (films with the label)

| block | decade | silent_or_sound | colour_class | height_bucket | bitrate_tercile |
|---|---|---|---|---|---|
| look:mean | 0.570 / 0.438 (n=128) | 0.906 / 0.562 (n=128) | 0.797 / 0.758 (n=128) | 0.484 / 0.375 (n=128) | 0.406 / 0.336 (n=128) |
| look:mean+std | 0.570 / 0.438 (n=128) | 0.906 / 0.562 (n=128) | 0.797 / 0.758 (n=128) | 0.477 / 0.375 (n=128) | 0.375 / 0.336 (n=128) |
| look:profile8 | 0.523 / 0.438 (n=128) | 0.914 / 0.562 (n=128) | 0.820 / 0.758 (n=128) | 0.461 / 0.375 (n=128) | 0.445 / 0.336 (n=128) |
| look:patchmean | 0.562 / 0.438 (n=128) | 0.914 / 0.562 (n=128) | 0.789 / 0.758 (n=128) | 0.414 / 0.375 (n=128) | 0.320 / 0.336 (n=128) |
| look_grid | 0.555 / 0.438 (n=128) | 0.906 / 0.562 (n=128) | 0.789 / 0.758 (n=128) | 0.422 / 0.375 (n=128) | 0.391 / 0.336 (n=128) |
| colour | 0.469 / 0.438 (n=128) | 0.680 / 0.562 (n=128) | 0.828 / 0.758 (n=128) | 0.320 / 0.375 (n=128) | 0.352 / 0.336 (n=128) |
| time | 0.484 / 0.438 (n=128) | 0.773 / 0.562 (n=128) | 0.758 / 0.758 (n=128) | 0.367 / 0.375 (n=128) | 0.297 / 0.336 (n=128) |
| time_sl | 0.453 / 0.438 (n=128) | 0.766 / 0.562 (n=128) | 0.766 / 0.758 (n=128) | 0.344 / 0.375 (n=128) | 0.297 / 0.336 (n=128) |
| motion:mid:mean | 0.617 / 0.438 (n=128) | 0.914 / 0.562 (n=128) | 0.938 / 0.758 (n=128) | 0.562 / 0.375 (n=128) | 0.500 / 0.336 (n=128) |
| motion:mid:mean+std | 0.602 / 0.438 (n=128) | 0.938 / 0.562 (n=128) | 0.938 / 0.758 (n=128) | 0.609 / 0.375 (n=128) | 0.523 / 0.336 (n=128) |
| motion:last:mean | 0.562 / 0.438 (n=128) | 0.898 / 0.562 (n=128) | 0.922 / 0.758 (n=128) | 0.562 / 0.375 (n=128) | 0.461 / 0.336 (n=128) |
| sound:mid:mean | 0.528 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.819 / 0.778 (n=72) | 0.375 / 0.417 (n=72) | 0.292 / 0.361 (n=72) |
| sound:mid:mean+std | 0.556 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.764 / 0.778 (n=72) | 0.375 / 0.417 (n=72) | 0.333 / 0.361 (n=72) |
| sound:last_c:mean | 0.444 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.736 / 0.778 (n=72) | 0.361 / 0.417 (n=72) | 0.264 / 0.361 (n=72) |
| sound:last_c:mean+std | 0.389 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.736 / 0.778 (n=72) | 0.361 / 0.417 (n=72) | 0.306 / 0.361 (n=72) |
| sound:stats | 0.403 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.750 / 0.778 (n=72) | 0.333 / 0.417 (n=72) | 0.278 / 0.361 (n=72) |
| sound:mid:mean+stats | 0.458 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.778 / 0.778 (n=72) | 0.417 / 0.417 (n=72) | 0.264 / 0.361 (n=72) |
| words | 0.347 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.764 / 0.778 (n=72) | 0.250 / 0.417 (n=72) | 0.208 / 0.361 (n=72) |
| fused | 0.514 / 0.361 (n=72) | 1.000 / 1.000 (n=72) | 0.792 / 0.778 (n=72) | 0.306 / 0.417 (n=72) | 0.236 / 0.361 (n=72) |
| fused:look+time | 0.617 / 0.438 (n=128) | 0.906 / 0.562 (n=128) | 0.781 / 0.758 (n=128) | 0.469 / 0.375 (n=128) | 0.398 / 0.336 (n=128) |
| proxy:facts | 0.403 / 0.434 (n=129) | 0.775 / 0.566 (n=129) | 0.860 / 0.760 (n=129) | 0.438 / 0.375 (n=128) | 0.492 / 0.336 (n=128) |
| proxy:label_cast | 0.527 / 0.434 (n=129) | 0.705 / 0.566 (n=129) | 0.760 / 0.760 (n=129) | 0.383 / 0.375 (n=128) | 0.359 / 0.336 (n=128) |
| proxy:label_decade_country | 0.969 / 0.434 (n=129) | 0.915 / 0.566 (n=129) | 0.760 / 0.760 (n=129) | 0.320 / 0.375 (n=128) | 0.359 / 0.336 (n=128) |
| proxy:label_director | 0.426 / 0.434 (n=129) | 0.481 / 0.566 (n=129) | 0.752 / 0.760 (n=129) | 0.336 / 0.375 (n=128) | 0.352 / 0.336 (n=128) |
| proxy:label_genre | 0.620 / 0.434 (n=129) | 0.953 / 0.566 (n=129) | 0.760 / 0.760 (n=129) | 0.289 / 0.375 (n=128) | 0.266 / 0.336 (n=128) |
| proxy:llm_felt | 0.434 / 0.434 (n=129) | 0.612 / 0.566 (n=129) | 0.791 / 0.760 (n=129) | 0.359 / 0.375 (n=128) | 0.281 / 0.336 (n=128) |
| proxy:llm_style | 0.527 / 0.434 (n=129) | 0.946 / 0.566 (n=129) | 0.868 / 0.760 (n=129) | 0.266 / 0.375 (n=128) | 0.312 / 0.336 (n=128) |
| proxy:llm_style_high | 0.703 / 0.703 (n=37) | 0.784 / 0.784 (n=37) | 0.865 / 0.757 (n=37) | 0.297 / 0.378 (n=37) | 0.351 / 0.405 (n=37) |
| proxy:llm_style_low | 0.316 / 0.368 (n=19) | 0.789 / 0.789 (n=19) | 0.842 / 0.842 (n=19) | 0.389 / 0.389 (n=18) | 0.278 / 0.389 (n=18) |
| proxy:llm_style_medium | 0.425 / 0.356 (n=73) | 0.890 / 0.685 (n=73) | 0.849 / 0.740 (n=73) | 0.301 / 0.397 (n=73) | 0.356 / 0.384 (n=73) |
| proxy:wiki_full | 0.527 / 0.434 (n=129) | 0.860 / 0.566 (n=129) | 0.744 / 0.760 (n=129) | 0.430 / 0.375 (n=128) | 0.320 / 0.336 (n=128) |
| proxy:wiki_lead | 0.605 / 0.434 (n=129) | 0.899 / 0.566 (n=129) | 0.767 / 0.760 (n=129) | 0.352 / 0.375 (n=128) | 0.375 / 0.336 (n=128) |
| proxy:wiki_plot | 0.453 / 0.438 (n=128) | 0.711 / 0.562 (n=128) | 0.789 / 0.766 (n=128) | 0.323 / 0.370 (n=127) | 0.323 / 0.339 (n=127) |
| proxy:wiki_style | 0.459 / 0.508 (n=61) | 0.754 / 0.525 (n=61) | 0.639 / 0.689 (n=61) | 0.417 / 0.367 (n=60) | 0.350 / 0.350 (n=60) |
| look:10stills (seed 0) | 0.477 / 0.438 (n=128) | 0.805 / 0.562 (n=128) | 0.742 / 0.758 (n=128) | 0.469 / 0.375 (n=128) | 0.414 / 0.336 (n=128) |

### Hubness

Chance: neighbour lists drawn at random (binomial k-occurrence).

| block | films | k | k-occurrence skew | chance | share in nobody's list | chance | max k-occurrence |
|---|---|---|---|---|---|---|---|
| look:mean | 128 | 10 | 0.686 | 0.278 | 0.000 | 0.000 | 25 |
| look:mean+std | 128 | 10 | 0.739 | 0.278 | 0.000 | 0.000 | 27 |
| look:profile8 | 128 | 10 | 0.798 | 0.278 | 0.008 | 0.000 | 29 |
| look:patchmean | 128 | 10 | 0.833 | 0.278 | 0.000 | 0.000 | 28 |
| look_grid | 128 | 10 | 0.700 | 0.278 | 0.000 | 0.000 | 28 |
| colour | 128 | 10 | 0.287 | 0.278 | 0.000 | 0.000 | 22 |
| time | 128 | 10 | 1.137 | 0.278 | 0.000 | 0.000 | 28 |
| time_sl | 128 | 10 | -0.055 | 0.278 | 0.016 | 0.000 | 20 |
| motion:mid:mean | 128 | 10 | 0.241 | 0.278 | 0.008 | 0.000 | 23 |
| motion:mid:mean+std | 128 | 10 | -0.021 | 0.278 | 0.008 | 0.000 | 19 |
| motion:last:mean | 128 | 10 | 0.425 | 0.278 | 0.023 | 0.000 | 25 |
| sound:mid:mean | 72 | 10 | 0.412 | 0.245 | 0.000 | 0.000 | 19 |
| sound:mid:mean+std | 72 | 10 | 0.126 | 0.245 | 0.000 | 0.000 | 17 |
| sound:last_c:mean | 72 | 10 | 0.170 | 0.245 | 0.000 | 0.000 | 21 |
| sound:last_c:mean+std | 72 | 10 | 0.417 | 0.245 | 0.000 | 0.000 | 22 |
| sound:stats | 72 | 10 | -0.821 | 0.245 | 0.000 | 0.000 | 15 |
| sound:mid:mean+stats | 72 | 10 | -0.485 | 0.245 | 0.000 | 0.000 | 16 |
| words | 72 | 10 | 0.277 | 0.245 | 0.000 | 0.000 | 20 |
| fused | 72 | 10 | -0.126 | 0.245 | 0.000 | 0.000 | 16 |
| fused:look+time | 128 | 10 | 0.797 | 0.278 | 0.000 | 0.000 | 27 |
| proxy:facts | 129 | 10 | -0.058 | 0.278 | 0.008 | 0.000 | 19 |
| proxy:label_cast | 129 | 10 | 2.497 | 0.278 | 0.054 | 0.000 | 61 |
| proxy:label_decade_country | 129 | 10 | 0.438 | 0.278 | 0.287 | 0.000 | 28 |
| proxy:label_director | 129 | 10 | 2.146 | 0.278 | 0.326 | 0.000 | 67 |
| proxy:label_genre | 129 | 10 | 1.304 | 0.278 | 0.023 | 0.000 | 29 |
| proxy:llm_felt | 129 | 10 | 0.368 | 0.278 | 0.000 | 0.000 | 22 |
| proxy:llm_style | 129 | 10 | 0.104 | 0.278 | 0.000 | 0.000 | 19 |
| proxy:llm_style_high | 37 | 10 | 0.036 | 0.165 | 0.000 | 0.000 | 15 |
| proxy:llm_style_low | 19 | 10 | 0.592 | -0.053 | 0.000 | 0.000 | 13 |
| proxy:llm_style_medium | 73 | 10 | 0.244 | 0.246 | 0.000 | 0.000 | 16 |
| proxy:wiki_full | 129 | 10 | 0.024 | 0.278 | 0.000 | 0.000 | 18 |
| proxy:wiki_lead | 129 | 10 | 0.832 | 0.278 | 0.000 | 0.000 | 21 |
| proxy:wiki_plot | 128 | 10 | 0.167 | 0.278 | 0.000 | 0.000 | 18 |
| proxy:wiki_style | 61 | 10 | 0.469 | 0.231 | 0.000 | 0.000 | 23 |
| look:10stills (seed 0) | 128 | 10 | 0.902 | 0.278 | 0.000 | 0.000 | 28 |

### Pairs sharing a lead actor but no director

Mean percentile of their distance among all pairs (0 = nearest). Chance 0.5; sd of that mean if the pairs were independent.

| block | pairs | mean percentile | chance | chance sd |
|---|---|---|---|---|
| look:mean | 53 | 0.165 | 0.500 | 0.040 |
| look:mean+std | 53 | 0.167 | 0.500 | 0.040 |
| look:profile8 | 53 | 0.171 | 0.500 | 0.040 |
| look:patchmean | 53 | 0.153 | 0.500 | 0.040 |
| look_grid | 53 | 0.163 | 0.500 | 0.040 |
| colour | 53 | 0.322 | 0.500 | 0.040 |
| time | 53 | 0.348 | 0.500 | 0.040 |
| time_sl | 53 | 0.379 | 0.500 | 0.040 |
| motion:mid:mean | 53 | 0.350 | 0.500 | 0.040 |
| motion:mid:mean+std | 53 | 0.320 | 0.500 | 0.040 |
| motion:last:mean | 53 | 0.398 | 0.500 | 0.040 |
| sound:mid:mean | 31 | 0.416 | 0.500 | 0.052 |
| sound:mid:mean+std | 31 | 0.425 | 0.500 | 0.052 |
| sound:last_c:mean | 31 | 0.502 | 0.500 | 0.052 |
| sound:last_c:mean+std | 31 | 0.505 | 0.500 | 0.052 |
| sound:stats | 31 | 0.523 | 0.500 | 0.052 |
| sound:mid:mean+stats | 31 | 0.493 | 0.500 | 0.052 |
| words | 31 | 0.348 | 0.500 | 0.052 |
| fused | 31 | 0.328 | 0.500 | 0.052 |
| fused:look+time | 53 | 0.213 | 0.500 | 0.040 |
| proxy:facts | 54 | 0.377 | 0.500 | 0.039 |
| proxy:label_cast | 54 | 0.045 | 0.500 | 0.039 |
| proxy:label_decade_country | 54 | 0.238 | 0.500 | 0.039 |
| proxy:label_director | 54 | 0.455 | 0.500 | 0.039 |
| proxy:label_genre | 54 | 0.250 | 0.500 | 0.039 |
| proxy:llm_felt | 54 | 0.379 | 0.500 | 0.039 |
| proxy:llm_style | 54 | 0.303 | 0.500 | 0.039 |
| proxy:llm_style_high | 8 | 0.306 | 0.500 | 0.102 |
| proxy:llm_style_low | 0 |  | 0.500 |  |
| proxy:llm_style_medium | 25 | 0.339 | 0.500 | 0.058 |
| proxy:wiki_full | 54 | 0.190 | 0.500 | 0.039 |
| proxy:wiki_lead | 54 | 0.182 | 0.500 | 0.039 |
| proxy:wiki_plot | 54 | 0.331 | 0.500 | 0.039 |
| proxy:wiki_style | 15 | 0.437 | 0.500 | 0.075 |
| look:10stills (seed 0) | 53 | 0.207 | 0.500 | 0.040 |

## 6. Neighbour lists

`neighbours.json`: look (128 films), colour (128 films), time (128 films), motion (128 films), sound (72 films), words (72 films), fused (72 films), fused:look+time (128 films).
