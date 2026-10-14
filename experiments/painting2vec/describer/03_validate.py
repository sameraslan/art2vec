"""Check one describer output against the instrument and its batch manifest.

  uv run --no-project python experiments/painting2vec/describer/03_validate.py <batch number>
Exit 0 and copy the file to raw/ if valid, else print every problem and exit 1.
"""
import json
import shutil
import sys

DATA = "data/painting2vec/describer"
HERE = "experiments/painting2vec/describer"
FELT = "calm tense tender eerie festive desolate joyful melancholy awed uneasy intimate playful solemn alarming sensual lonely hopeful oppressive dreamlike energetic still warm cold mysterious".split()
THINGS = "sky clouds sun_or_moon water trees mountains_or_hills rocks field_or_grass flowers fruit_or_food snow_or_ice fire_or_smoke buildings window_or_door furniture bridge road_or_path boat_or_ship cart_or_carriage horse dog cattle_or_sheep bird fish other_animal man woman child old_person nude crowd dead_or_wounded_body soldier_or_armour weapon book_or_paper musical_instrument vessel_or_tableware curtain_or_drapery hat_or_headdress jewellery_or_crown flag_or_banner halo wings cross skull_or_skeleton written_text".split()
MANNER = "abstraction contour finish detail depth palette_breadth saturation colour_temperature darkness contrast crowding symmetry closeness".split()
COUNTS = ["0", "1", "2", "3-5", "6+"]
SETTINGS = ["interior", "landscape", "townscape", "seascape", "garden", "sky_or_heaven", "plain_background", "mixed", "none"]


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
            if set(f) != set(FELT) or any(type(f[k]) is not int or not 0 <= f[k] <= 3 for k in f):
                errs.append(f"{c}: felt")
            if set(m) != set(MANNER) or any(type(m[k]) is not int or not 0 <= m[k] <= 4 for k in m):
                errs.append(f"{c}: manner")
            t = s["things"]
            if set(t) != set(THINGS) or any(t[k] not in (0, 1) for k in t):
                errs.append(f"{c}: things {set(t) ^ set(THINGS)}")
            if s["people"] not in COUNTS or s["animals"] not in COUNTS or s["setting"] not in SETTINGS:
                errs.append(f"{c}: counts/setting")
            if not isinstance(s["main_action"], str) or not isinstance(s["tags"], list) or len(s["tags"]) > 8:
                errs.append(f"{c}: action/tags")
            if type(g["recognised"]) is not bool or type(g["confidence"]) is not int or not 0 <= g["confidence"] <= 3:
                errs.append(f"{c}: recognition")
            if not isinstance(g["title"], str) or not isinstance(g["painter"], str) or not isinstance(g["guess_school"], str) or type(g["guess_century"]) is not int:
                errs.append(f"{c}: recognition fields")
        except (KeyError, TypeError) as e:
            errs.append(f"{c}: {type(e).__name__} {e}")
    return errs


if __name__ == "__main__":
    b = int(sys.argv[1])
    errs = check(b)
    if errs:
        print(f"batch {b:02d} INVALID"); print("\n".join(errs)); sys.exit(1)
    shutil.copy(f"{DATA}/out/batch_{b:02d}.json", f"{HERE}/raw/batch_{b:02d}.json")
    print(f"batch {b:02d} ok")
