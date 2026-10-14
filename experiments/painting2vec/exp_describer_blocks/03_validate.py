"""Check one describer output against instrument v2 and its batch manifest.

  uv run --no-project python experiments/painting2vec/exp_describer_blocks/03_validate.py <batch number>
Exit 0 and copy the file to raw/ if valid, else print every problem and exit 1.
"""
import json
import shutil
import sys

DATA = "data/painting2vec/exp_describer_blocks"
HERE = "experiments/painting2vec/exp_describer_blocks"
FELT = "calm tense tender eerie festive desolate joyful melancholy awed uneasy intimate playful solemn alarming sensual lonely hopeful oppressive dreamlike energetic still warm cold mysterious".split()
THINGS = "sky clouds sun_or_moon water trees mountains_or_hills rocks field_or_grass flowers fruit_or_food snow_or_ice fire_or_smoke buildings window_or_door furniture bridge road_or_path boat_or_ship cart_or_carriage horse dog cattle_or_sheep bird fish other_animal man woman child old_person nude crowd dead_or_wounded_body soldier_or_armour weapon book_or_paper musical_instrument vessel_or_tableware curtain_or_drapery hat_or_headdress jewellery_or_crown flag_or_banner halo wings cross skull_or_skeleton written_text".split()
MANNER_V1 = "abstraction contour finish detail depth palette_breadth saturation colour_temperature darkness contrast crowding symmetry closeness".split()
MANNER_V2 = "edge_hardness outline stroke_direction flat_colour modelling ornament idealisation distortion".split()
MANNER = MANNER_V1 + MANNER_V2
CUES = "linear_perspective atmospheric_perspective overlap size_diminution cast_shadows foreshortening stacked_space".split()
HUES = "red orange yellow green blue purple pink brown gold black white grey".split()
COUNTS = ["0", "1", "2", "3-5", "6+"]
SETTINGS = ["interior", "landscape", "townscape", "seascape", "garden", "sky_or_heaven", "plain_background", "mixed", "none"]
KEYS = ["high", "mid", "low"]


def check(b):
    errs = []
    man = json.load(open(f"{DATA}/batches/batch_{b:02d}.json"))
    try:
        out = json.load(open(f"{DATA}/out/batch_{b:02d}.json"))
    except Exception as e:  # missing or not JSON
        return [f"cannot load: {e}"]
    recs = out.get("records") if isinstance(out, dict) else None
    if not isinstance(recs, list):
        return ["no records list"]
    want = [i["code"] for i in man["images"]]
    got = [r.get("code") for r in recs]
    if sorted(want) != sorted(got):
        errs.append(f"codes differ: missing {set(want) - set(got)}, extra {set(got) - set(want)}")
    for r in recs:
        c = r.get("code")
        try:
            f, s, m, g = r["felt"], r["subject"], r["manner"], r["recognition"]
            for k in ("people", "animals"):  # an exact count inside a bin is mapped to the bin and logged
                v = str(s[k])
                fixed = {"3": "3-5", "4": "3-5", "5": "3-5"}.get(v, "6+" if v.isdigit() and int(v) >= 6 else v)
                if fixed != s[k]:
                    FIXES.append(f"{b},{c},{k},{s[k]},{fixed}")
                    s[k] = fixed
            if set(f) != set(FELT) or any(type(f[k]) is not int or not 0 <= f[k] <= 3 for k in f):
                errs.append(f"{c}: felt")
            if set(m) != set(MANNER) or any(type(m[k]) is not int or not 0 <= m[k] <= 4 for k in m):
                errs.append(f"{c}: manner {set(m) ^ set(MANNER)}")
            t = s["things"]
            if set(t) != set(THINGS) or any(t[k] not in (0, 1) for k in t):
                errs.append(f"{c}: things {set(t) ^ set(THINGS)}")
            if s["people"] not in COUNTS or s["animals"] not in COUNTS or s["setting"] not in SETTINGS:
                errs.append(f"{c}: counts/setting")
            if not isinstance(s["main_action"], str) or not isinstance(s["tags"], list) or len(s["tags"]) > 8:
                errs.append(f"{c}: action/tags")
            d = r["space"]["depth_cues"]
            if set(d) != set(CUES) or any(d[k] not in (0, 1) for k in d):
                errs.append(f"{c}: depth_cues {set(d) ^ set(CUES)}")
            col = r["colour"]
            h = col["hues"]
            if set(h) != set(HUES) or any(h[k] not in (0, 1) for k in h):
                errs.append(f"{c}: hues {set(h) ^ set(HUES)}")
            if col["main_hue"] not in HUES or col["accent_hue"] not in HUES + ["none"] or col["value_key"] not in KEYS:
                errs.append(f"{c}: main_hue/accent_hue/value_key")
            if type(g["recognised"]) is not bool or type(g["confidence"]) is not int or not 0 <= g["confidence"] <= 3:
                errs.append(f"{c}: recognition")
            if not isinstance(g["title"], str) or not isinstance(g["painter"], str) or not isinstance(g["guess_school"], str) or type(g["guess_century"]) is not int:
                errs.append(f"{c}: recognition fields")
        except (KeyError, TypeError) as e:
            errs.append(f"{c}: {type(e).__name__} {e}")
    if not errs:
        json.dump(out, open(f"{HERE}/raw/batch_{b:02d}.json", "w"), ensure_ascii=False)
    return errs


FIXES = []

if __name__ == "__main__":
    ok = True
    for b in map(int, sys.argv[1:]):
        errs = check(b)
        if errs:
            ok = False
            print(f"batch {b:02d} INVALID"); print("\n".join(errs))
        else:
            print(f"batch {b:02d} ok")
    if FIXES:
        open(f"{HERE}/normalised.csv", "a").write("\n".join(FIXES) + "\n")
        print("normalised:", FIXES)
    sys.exit(0 if ok else 1)
