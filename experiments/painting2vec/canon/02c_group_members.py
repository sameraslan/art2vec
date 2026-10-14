"""Members of every series / cycle / group item among the candidates: the group's own P527 (has part) plus
every item that points at the group with P361 (part of) or P179 (part of the series).
Out: data/group_members.csv (group, member); data/member_ids.txt for 02_entities.py."""
import csv, json
from wd import sparql, qid
from common import AGG

groups, pairs = [], set()
for l in open("data/items.jsonl"):
    d = json.loads(l)
    if set(d.get("P31", [])) & AGG:
        groups.append(d["id"])
        for m in d.get("P527", []): pairs.add((d["id"], m))
for i in range(0, len(groups), 150):
    vals = " ".join("wd:" + g for g in groups[i:i + 150])
    for x in sparql(f"SELECT ?g ?m WHERE {{ VALUES ?g {{ {vals} }} ?m wdt:P361|wdt:P179 ?g }}"):
        pairs.add((qid(x["g"]), qid(x["m"])))
with open("data/group_members.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["group", "member"]); w.writerows(sorted(pairs))
open("data/member_ids.txt", "w").write("\n".join(sorted({m for _, m in pairs})))
print(len(groups), "groups;", len(pairs), "pairs;", len({g for g, _ in pairs}), "groups with members")
