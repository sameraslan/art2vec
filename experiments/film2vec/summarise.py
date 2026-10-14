"""Print the handful of tables from results/results.json that the write-up uses."""

import json

r = json.load(open("results/results.json"))
core = ["look:mean", "colour", "time", "motion:mid:mean", "sound:mid:mean", "words"]
proxies = ["proxy:wiki_full", "proxy:wiki_plot", "proxy:wiki_lead", "proxy:wiki_style", "proxy:llm_style",
           "proxy:llm_style_high", "proxy:llm_style_medium", "proxy:llm_style_low", "proxy:llm_felt", "proxy:facts",
           "proxy:label_genre", "proxy:label_director", "proxy:label_cast", "proxy:label_decade_country"]  # fmt: skip
pair = {}
for row in r["exp1_block_agreement"] + [x for v in r["exp2_pooling"].values() for x in v]:
    pair[(row["a"], row["b"])] = pair[(row["b"], row["a"])] = row


def cell(a: str, b: str) -> str:
    p = pair.get((a, b))
    return "      -      " if p is None else f"{p['spearman']:+.2f} {p['overlap']:.2f}/{p['overlap_chance']:.2f}"


print(f"films {r['n_films']}  k {r['k']}   cell = spearman, top-k overlap / chance")
print("\nblock x block")
print(" " * 18 + "".join(f"{c[:14]:>16}" for c in core))
for a in core:
    print(f"{a[:17]:18}" + "".join(f"{cell(a, b) if a != b else '':>16}" for b in core))
print("\nproxy x block (n in brackets for first column)")
print(" " * 28 + "".join(f"{c[:14]:>16}" for c in core))
for a in proxies:
    n = pair.get((a, "look:mean"), {}).get("n", "")
    print(f"{a[6:] + ' [' + str(n) + ']':28}" + "".join(f"{cell(a, b):>16}" for b in core))
print("\npooling / variants")
for fam, rows in r["exp2_pooling"].items():
    for x in rows:
        print(f"  {x['a']:22} ~ {x['b']:24} sp {x['spearman']:+.2f} ov {x['overlap']:.2f}")
print("\nsubsampling: top-k overlap with the full block")
for b, v in r["exp3_subsampling"].items():
    print(f"  {b}: " + "  ".join(f"{x['n_requested']}:{x['overlap_mean']:.2f}" for x in v["rows"])
          + f"  (chance {v['rows'][0]['overlap_chance']:.2f})")  # fmt: skip
print("\n10 stills -> block: R2 (null p95), overlap of predicted vs true (shuffled mean)")
for b, v in r["exp4_cross_prediction"]["targets"].items():
    print(f"  {b:16} n={v['n']:3d} R2 {v['r2_mean']:+.3f} ({v['r2_chance_p95']:+.3f})  "
          f"ov {v['overlap_pred_vs_true_mean']:.2f} ({v['overlap_chance_shuffled_mean']:.2f})")  # fmt: skip
print("\nleaks: top-k share / chance")
attrs = ["director", "lead_actor", "decade", "country", "silent_or_sound", "colour_class", "kind"]
print(" " * 18 + "".join(f"{a[:11]:>12}" for a in attrs) + "   actor!dir pct (pairs)")
for b in core + ["fused", "fused:look+time"]:
    v = r["exp5_leaks"].get(b)
    if not v:
        continue
    s = "".join(f"{v['share'][a]['top_k']:.2f}/{v['share'][a]['chance']:.2f}".rjust(12) for a in attrs)
    ad = v.get("actor_not_director") or {}
    print(f"{b[:17]:18}{s}   {ad.get('mean_distance_percentile', float('nan')):.2f} ({ad.get('n_pairs')})")
print("\nkNN accuracy / majority rate, and hubness")
ks = ["decade", "silent_or_sound", "colour_class", "height_bucket", "bitrate_tercile"]
print(" " * 18 + "".join(f"{a[:13]:>14}" for a in ks) + "   skew  max  none")
for b in core + ["fused", "fused:look+time"]:
    v = r["exp5_leaks"].get(b)
    if not v:
        continue
    s = "".join(f"{v['knn'][a]['accuracy']:.2f}/{v['knn'][a]['majority_rate']:.2f}".rjust(14) for a in ks if a in v["knn"])
    h = v["hubness"]
    print(f"{b[:17]:18}{s}   {h['k_occurrence_skew']:.2f}  {h['max_k_occurrence']}  {h['share_in_no_list']:.2f}")
