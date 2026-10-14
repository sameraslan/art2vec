"""Step 4: download the pilot images (Commons thumbnails, one at a time, resumable) and write meta.csv."""
from common import CACHE, DATA, HERE, free_bytes, load_json
from meta import build

if __name__ == "__main__":
    sel = load_json(CACHE / "selected.json")
    print("free GB before:", round(free_bytes() / 1e9, 2))
    build(sel, DATA / "pilot" / "images", [DATA / "pilot" / "meta.csv", HERE / "pilot_meta.csv"])
    print("free GB after:", round(free_bytes() / 1e9, 2))
