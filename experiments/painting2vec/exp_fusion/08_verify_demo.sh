#!/bin/sh
# Serve the demo on a free port, fetch the page and every JSON file with curl, check that the JSON
# parses and is consistent, and that every referenced image exists. Stops the server afterwards.
# Pass KEEP=1 to leave the server running (prints the URL).
DEMO="$(cd "$(dirname "$0")/../../.." && pwd)/data/painting2vec/demo"
PORT=$(python3 -c "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1])")
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$DEMO" >/dev/null 2>&1 &
PID=$!
sleep 1
TMP=$(mktemp -d)
fail=0
for f in index.html atlas.jpg data/paintings.json data/lenses.json; do
  code=$(curl -s -o "$TMP/$(basename $f)" -w "%{http_code}" "http://127.0.0.1:$PORT/$f"); echo "$f $code $(wc -c < "$TMP/$(basename $f)") bytes"; [ "$code" = 200 ] || fail=1
done
for id in $(python3 -c "import json,sys; print(' '.join(l['id'] for l in json.load(open('$TMP/lenses.json'))['lenses']))"); do
  code=$(curl -s -o "$TMP/lens_$id.json" -w "%{http_code}" "http://127.0.0.1:$PORT/data/lens_$id.json"); echo "data/lens_$id.json $code"; [ "$code" = 200 ] || fail=1
done
python3 - "$TMP" "$DEMO" <<'PY' || fail=1
import json, os, sys
tmp, demo = sys.argv[1:]
P = json.load(open(f"{tmp}/paintings.json")); info = json.load(open(f"{tmp}/lenses.json"))
n = P["n"]; assert all(len(P[k]) == n for k in ("qid", "title", "painter", "year", "tw", "th", "palette")), "column lengths"
miss = [q for q in P["qid"] for d in ("thumbs", "large") if not os.path.exists(f"{demo}/{d}/{q}.jpg")]
assert not miss, f"{len(miss)} images missing"
for l in info["lenses"]:
    L = json.load(open(f"{tmp}/lens_{l['id']}.json"))
    assert len(L["xy"]) == 2 * n and len(L["nn"]) == n and len(L["far"]) == n
    assert all(len(r) == info["k"] and i not in r and all(0 <= j < n for j in r) for i, r in enumerate(L["nn"]))
    assert all(abs(v) <= 1 for v in L["xy"])
    gap = info["far_gap_years"]
    assert all(abs(P["year"][i] - P["year"][j]) >= gap for i, r in enumerate(L["far"]) for j in r)
html = open(f"{tmp}/index.html").read()
import re
ext = [u for u in re.findall(r"""(?:src|href)=["'](https?://[^"']+)""", html)]
assert not ext, ext
assert "fetch(\"http" not in html
print(f"ok: {n} paintings, {len(info['lenses'])} lenses, {2*n} images present, JSON consistent, no external requests in the page")
PY
if [ "$KEEP" = 1 ]; then echo "serving at http://127.0.0.1:$PORT/ (pid $PID)"; else kill $PID; echo "server stopped"; fi
rm -rf "$TMP"
exit $fail
