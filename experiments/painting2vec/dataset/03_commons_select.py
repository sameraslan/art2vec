"""Step 3: read each candidate's Commons file record, keep only files Commons marks public domain / CC0,
and make the final pick: N_RANK by Wikipedia sitelink rank, then N_NONEUR by sitelink rank within
non-European traditions. Writes data/painting2vec/cache/selected.json.
"""
from collections import Counter

from common import CACHE, load_json, save_json
from commons import info, is_open
from wd import fetch_creators, fetch_paintings

N_RANK = 1600
N_NONEUR = 400
QUOTA = {"japanese": 100, "chinese": 100, "korean": 40, "south_asian": 60, "persian_ottoman": 50, "other_non_european": 50}
LOOKAHEAD = 2200       # how far down the global ranking to check licences
PER_TRADITION = 400    # how far down each tradition's ranking to check licences


def main():
    elig = load_json(CACHE / "eligible.json")
    P = fetch_paintings([e["qid"] for e in elig])
    C = fetch_creators([a for e in elig for a in P[e["qid"]]["P170"]])
    head = elig[:LOOKAHEAD]
    seen = Counter()
    tail = []
    for e in elig[LOOKAHEAD:]:
        if e["tradition"] in QUOTA and seen[e["tradition"]] < PER_TRADITION:
            seen[e["tradition"]] += 1
            tail.append(e)
    cand = head + tail
    recs = info([P[e["qid"]]["P18"][0] for e in cand])
    drop = Counter()

    def usable(e):
        rec = recs.get(P[e["qid"]]["P18"][0])
        if not rec or not rec.get("thumburl"):
            drop["commons_file_missing"] += 1
            return False
        if not is_open(rec):
            drop["licence_not_pd_or_cc0:" + (rec["licence"] or "none")] += 1
            return False
        if max(rec["w"], rec["h"]) < 600:
            drop["original_under_600px"] += 1
            return False
        return True

    good = [e for e in cand if usable(e)]
    print("checked", len(cand), "usable", len(good), "dropped", dict(drop))
    top = good[:N_RANK]
    sl = lambda e: P[e["qid"]]["wp_sitelinks"]
    print("rank stratum sitelinks: max", sl(top[0]), "min", sl(top[-1]), "| traditions", Counter(e["tradition"] for e in top))
    rest = [e for e in good[N_RANK:] if e["tradition"] in QUOTA]
    avail = Counter(e["tradition"] for e in rest)
    print("non-European usable beyond the rank stratum:", dict(avail))
    take = {t: min(QUOTA[t], avail[t]) for t in QUOTA}
    spare = N_NONEUR - sum(take.values())
    while spare > 0 and any(avail[t] > take[t] for t in QUOTA):  # unused quota goes round-robin to traditions with stock
        for t in QUOTA:
            if spare > 0 and avail[t] > take[t]:
                take[t] += 1
                spare -= 1
    sel = [{"qid": e["qid"], "stratum": "sitelink_rank", "tradition": e["tradition"]} for e in top]
    got = Counter()
    for e in rest:
        t = e["tradition"]
        if got[t] < take[t]:
            got[t] += 1
            sel.append({"qid": e["qid"], "stratum": "non_european:" + t, "tradition": t})
    for t in QUOTA:
        fl = [P[s["qid"]]["wp_sitelinks"] for s in sel if s["stratum"] == "non_european:" + t]
        print(f"  non_european:{t}: n={len(fl)} sitelinks max={max(fl, default=0)} min={min(fl, default=0)}")
    save_json(CACHE / "selected.json", sel)

    painters = Counter(a for s in sel for a in P[s["qid"]]["P170"] if a != "UNKNOWN")
    big = [(C[a]["label"] if C.get(a) else a, n) for a, n in painters.most_common() if n >= 8]
    print("selected", len(sel), "| painters with 8+ works:", len(big))
    print(big)
    cent = Counter((min(P[s["qid"]]["inception"]) // 100 + 1) if P[s["qid"]]["inception"] else None for s in sel)
    print("centuries:", sorted(cent.items(), key=lambda kv: (kv[0] is None, kv[0] or 0)))


if __name__ == "__main__":
    main()
