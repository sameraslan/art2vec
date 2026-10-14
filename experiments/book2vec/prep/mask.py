"""Name masking: data/tok/<key>.parquet -> data/maskA/<key>.txt (persons) and data/maskB/<key>.txt
(persons + places). Paragraphs stay aligned one-to-one with data/clean/<key>.txt.

How a name is found. en_core_web_sm NER is noisy on old fiction, so it only votes. A word is a
name word when it is capitalised in the middle of a sentence, is tagged PROPN or sits in a
PERSON / place entity there, and never (or almost never) occurs lower-cased in the book. Each
name word is then typed person or place from all its occurrences: NER labels, a title before it
(Mr., Lady, Aunt), a verb or 's after it, a vocative; against a place preposition before it or a
place noun after it (Street, Park, Hall). Runs of name words form one mention.

How variants are merged. Multi-word names are the anchors ("Elizabeth Bennet"). A shorter form
joins a longer one when exactly one longer name contains it. A single word joins the one full
name that contains it; when several do (the Bennets), "Mr. X", "Mrs. X", "Miss X" stay separate
people and a bare surname goes with "Mr. X". Stand-ins are numbered in order of first
appearance: Person1, Place1. Titles and kinship words are kept ("Mr. Person3", "Aunt Person7").

data/mask_report.csv lists per book the counts and the 15 most replaced names.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import pyarrow.parquet as pq
from common import (
    CLEAN,
    DATA,
    DEFAULT_TESTBED,
    MASK_A,
    MASK_B,
    TOK,
    is_stale,
    read_paragraphs,
    read_testbed,
    select,
    write_paragraphs,
)

REPORT = DATA / "mask_report.csv"
REPORT_COLUMNS = [
    "key",
    "n_persons",
    "n_places",
    "person_mentions",
    "place_mentions",
    "masked_share_of_words",
    "top15_replaced",
    "top_unclassified_proper_nouns",
    "notes",
]

TITLE_CLASS = {
    "mr": "mr", "mister": "mr", "monsieur": "mr", "m": "mr", "herr": "mr", "signor": "mr",
    "don": "mr", "master": "mr", "messrs": "mr", "squire": "mr", "esq": "mr",
    "mrs": "mrs", "madame": "mrs", "mme": "mrs", "frau": "mrs", "signora": "mrs", "ms": "mrs",
    "madam": "mrs", "mistress": "mrs", "dame": "mrs", "widow": "mrs",
    "miss": "miss", "mademoiselle": "miss", "mlle": "miss", "fraulein": "miss",
    "sir": "sir", "lord": "lord", "lady": "lady",
}  # fmt: skip
RANKS = {
    "dr", "doctor", "captain", "capt", "colonel", "col", "major", "general", "gen", "lieutenant",
    "lieut", "sergeant", "admiral", "commodore", "professor", "prof", "rev", "reverend", "father",
    "brother", "sister", "mother", "saint", "st", "king", "queen", "prince", "princess", "duke",
    "duchess", "count", "countess", "baron", "baroness", "earl", "marquis", "marchioness",
    "viscount", "emperor", "empress", "tsar", "czar", "judge", "inspector", "constable",
    "president", "senator", "governor", "mayor", "bishop", "archbishop", "cardinal", "pope",
    "deacon", "elder", "parson", "abbe", "abbé", "dom", "fra", "friar", "chevalier", "comte",
    "comtesse", "marquise", "vicomte", "nurse", "farmer", "goodman", "goodwife", "old", "young",
    "little", "poor", "dear", "cousin", "aunt", "auntie", "uncle", "grandfather", "grandmother",
    "grandpa", "grandma", "granny", "mamma", "mama", "papa", "corporal", "private", "mate",
    "skipper", "chief", "pan", "pani",
}  # fmt: skip
SURNAME_RANKS = {
    "dr", "doctor", "captain", "capt", "colonel", "col", "major", "general", "gen", "lieutenant",
    "lieut", "sergeant", "admiral", "professor", "prof", "rev", "reverend", "inspector", "judge",
}  # fmt: skip
GENDERED = {"mr", "mrs", "miss", "sir", "lord", "lady"}
KEPT_BEFORE = set(TITLE_CLASS) | RANKS
NOT_NAMES = {
    "i", "god", "lord", "christ", "jesus", "heaven", "hell", "providence", "almighty", "devil",
    "satan", "bible", "gospel", "scripture", "christmas", "easter", "lent", "sabbath", "monday",
    "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "january", "february",
    "march", "april", "may", "june", "july", "august", "september", "october", "november",
    "december", "sir", "madam", "ma'am", "o", "oh", "ah", "yes", "no", "amen", "esq", "mr", "mrs",
    "english", "french", "german", "russian", "italian", "spanish", "american", "british",
    "irish", "scotch", "scottish", "greek", "latin", "roman", "jewish", "christian", "catholic",
    "protestant", "dutch", "polish", "chinese", "indian", "turkish", "european", "englishman",
    "frenchman", "th", "st", "chapter", "book", "part", "volume", "letter", "majesty", "highness",
    "excellency", "ladyship", "lordship", "honour", "honor", "grace", "reverence", "worship",
    "parliament", "church", "state", "government", "court", "king", "queen", "tsar", "emperor",
}  # fmt: skip
PLACE_NOUNS = {
    "street", "st", "road", "lane", "square", "place", "park", "house", "hall", "abbey", "castle",
    "court", "row", "bridge", "hill", "river", "island", "isle", "bay", "lake", "mountain",
    "mount", "valley", "wood", "forest", "common", "green", "heath", "farm", "manor", "lodge",
    "cottage", "inn", "hotel", "avenue", "terrace", "gardens", "garden", "prospect", "canal",
    "county", "city", "town", "village", "parish", "station", "harbour", "harbor", "sea", "ocean",
    "grange", "priory", "rectory", "parsonage", "vicarage", "chapel", "cathedral", "gate",
    "quay", "wharf", "market", "grove", "vale", "dale", "towers", "villa", "chase", "moor",
    "boulevard", "rue", "province", "district", "embankment",
}  # fmt: skip
PLACE_PREPS = {"in", "at", "from", "near", "through", "towards", "toward", "into", "leaving"}
PLACE_ENTS = {"GPE", "LOC", "FAC"}
CONNECTORS = {"de", "von", "van", "du", "la", "le", "di", "da", "del", "della", "des", "der", "y"}
OPENERS = {'"', "'", "“", "‘", "(", "[", "—", "--", "-", "–", "*", "_"}
BREAKS = {".", "!", "?", ":", "…", "..."}


@dataclass
class Mention:
    start: int  # token index, inclusive
    end: int  # token index, exclusive
    words: tuple[str, ...]
    kind: str  # "person" or "place"
    title: str  # normalised title before a person mention, or ""


def load_tokens(key: str) -> dict[str, list]:
    table = pq.read_table(TOK / f"{key}.parquet")
    return {name: table.column(name).to_pylist() for name in table.column_names}


def norm(word: str) -> str:
    return word.lower().replace("’", "'").rstrip(".")


def looks_capitalised(text: str) -> bool:
    """Capitalised word, not ALL CAPS (headings and shouting say nothing about names)."""
    return is_name_shaped(text) and not text.isupper()


def is_name_shaped(text: str) -> bool:
    return len(text) > 1 and text[0].isupper() and text.replace("-", "").replace("'", "").isalpha()


def find_mid_sentence(t: dict[str, list]) -> list[bool]:
    """True for tokens that are not at the start of a sentence, clause or quotation."""
    n = len(t["text"])
    mid = [False] * n
    for i in range(1, n):
        if t["sent_id"][i] != t["sent_id"][i - 1] or t["para_id"][i] != t["para_id"][i - 1]:
            continue
        prev = t["text"][i - 1]
        if prev in OPENERS or prev in BREAKS or prev in {"”", "’"} or prev.isspace():
            continue
        mid[i] = True
    return mid


def name_words(t: dict[str, list], mid: list[bool]) -> tuple[dict[str, str], Counter[str]]:
    """Decide which words are names and whether each is a person or a place."""
    text, pos, ent = t["text"], t["pos"], t["ent_type"]
    n = len(text)
    lower_n: Counter[str] = Counter()
    cap_n: Counter[str] = Counter()
    cap_mid: Counter[str] = Counter()
    evidence: Counter[str] = Counter()
    propn: Counter[str] = Counter()
    person: defaultdict[str, float] = defaultdict(float)
    place: defaultdict[str, float] = defaultdict(float)
    norp: Counter[str] = Counter()
    non_final: Counter[str] = Counter()
    heads: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for i in range(n):
        w = text[i]
        if w.islower() and w.isalpha():
            lower_n[w] += 1
            continue
        if not looks_capitalised(w):
            continue
        lw = norm(w)
        cap_n[lw] += 1
        propn[lw] += pos[i] == "PROPN"
        prev = norm(text[i - 1]) if i > 0 and t["para_id"][i - 1] == t["para_id"][i] else ""
        nxt = text[i + 1] if i + 1 < n and t["para_id"][i + 1] == t["para_id"][i] else ""
        nxt_pos = pos[i + 1] if nxt else ""
        if mid[i]:
            cap_mid[lw] += 1
            evidence[lw] += pos[i] == "PROPN" or ent[i] == "PERSON" or ent[i] in PLACE_ENTS
        norp[lw] += ent[i] in {"NORP", "LANGUAGE"}
        person[lw] += 0.5 * (ent[i] == "PERSON") + (t["dep"][i] == "nsubj")
        place[lw] += 0.5 * (ent[i] in PLACE_ENTS)
        if prev in KEPT_BEFORE and prev not in {"old", "young", "little", "poor", "dear", "st"}:
            person[lw] += 3
        if nxt_pos in {"VERB", "AUX"}:
            person[lw] += 1
        if nxt in {"'s", "’s"}:
            person[lw] += 0.5
        if (prev == "," or not mid[i]) and nxt in {",", "!", "?"} and t["is_quote"][i]:
            person[lw] += 1
        if prev in PLACE_PREPS:
            place[lw] += 1.5
        if norm(nxt) in PLACE_NOUNS and nxt[:1].isupper():
            place[lw] += 3
        if looks_capitalised(nxt):
            non_final[lw] += 1
            heads[lw][norm(nxt)] += 1
    kinds: dict[str, str] = {}
    unclassified: Counter[str] = Counter()
    for lw, caps in cap_n.items():
        if lw in NOT_NAMES or lw in KEPT_BEFORE or lw in CONNECTORS or len(lw) < 2:
            continue
        low = lower_n[lw]
        never_lower = low == 0 or (cap_mid[lw] >= 3 and cap_mid[lw] >= 4 * low)
        seen = evidence[lw] >= 1 or (propn[lw] >= 2 and person[lw] >= 2)
        if not never_lower or not seen:
            continue
        if norp[lw] > 0.5 * caps:
            continue
        p, q = person[lw], place[lw]
        if max(p, q) <= 0:
            unclassified[lw] = caps
        else:
            kinds[lw] = "person" if p >= q else "place"
    # a word mostly used as the first part of a longer name ("Brigid O'Shaughnessy") gets few
    # cues of its own, so it takes the kind of the names it leads
    inherited: dict[str, str] = {}
    for lw in list(kinds) + list(unclassified):
        if non_final[lw] < 0.5 * cap_n[lw]:
            continue
        votes: Counter[str] = Counter()
        for head, count in heads[lw].items():
            if head in kinds:
                votes[kinds[head]] += count
        if votes:
            inherited[lw] = votes.most_common(1)[0][0]
    for lw, kind in inherited.items():
        kinds[lw] = kind
        unclassified.pop(lw, None)
    return kinds, unclassified


def find_mentions(t: dict[str, list], kinds: dict[str, str]) -> list[Mention]:
    text, para, sent = t["text"], t["para_id"], t["sent_id"]
    n = len(text)
    mentions: list[Mention] = []
    i = 0
    while i < n:
        if not is_name_shaped(text[i]):
            i += 1
            continue
        lw = norm(text[i])
        prev = norm(text[i - 1]) if i > 0 and para[i - 1] == para[i] else ""
        if lw not in kinds and prev in TITLE_CLASS and text[i - 1][:1].isupper():
            # "Mrs. Long": a capitalised word after Mr./Mrs./Miss is a name even if the word
            # is an ordinary one elsewhere in the book
            if lw not in NOT_NAMES and lw not in KEPT_BEFORE and not text[i].isupper():
                mentions.append(Mention(i, i + 1, (lw,), "person", TITLE_CLASS[prev]))
            i += 1
            continue
        if lw not in kinds:
            i += 1
            continue
        j = i + 1
        while j < n and sent[j] == sent[i] and para[j] == para[i]:
            if is_name_shaped(text[j]) and norm(text[j]) in kinds:
                j += 1
            elif (
                text[j] in CONNECTORS | {"-"}
                and j + 1 < n
                and sent[j + 1] == sent[i]
                and is_name_shaped(text[j + 1])
                and norm(text[j + 1]) in kinds
            ):
                j += 2
            else:
                break
        words = tuple(norm(text[k]) for k in range(i, j) if text[k] != "-")
        kind = kinds.get(words[-1], "person")  # the last word of a name is its head
        end = j
        nxt = text[j] if j < n and para[j] == para[i] else ""
        if norm(nxt) in PLACE_NOUNS and nxt[:1].isupper() and len(nxt) > 2:
            kind, end = "place", j + 1
        elif len(words) > 1 and words[-1] in PLACE_NOUNS:
            kind = "place"
        title = ""
        if kind == "person" and i > 0 and para[i - 1] == para[i]:
            prev = norm(text[i - 1])
            if prev in TITLE_CLASS:
                title = TITLE_CLASS[prev]
            elif prev in SURNAME_RANKS and text[i - 1][:1].isupper():
                title = "rank:surname"
            elif prev in RANKS and text[i - 1][:1].isupper():
                title = "rank"
        mentions.append(Mention(i, end, words, kind, title))
        i = end
    return mentions


def contains(longer: tuple[str, ...], shorter: tuple[str, ...]) -> bool:
    k = len(shorter)
    return any(longer[a : a + k] == shorter for a in range(len(longer) - k + 1))


def resolve_persons(mentions: list[Mention]) -> dict[tuple[str, tuple[str, ...]], tuple]:
    """Map each (title, words) form to an entity key, merging obvious variants."""
    forms = Counter((m.title, m.words) for m in mentions if m.kind == "person")
    multi = sorted({w for _, w in forms if len(w) > 1}, key=len, reverse=True)
    canon: dict[tuple[str, ...], tuple[str, ...]] = {}
    for words in multi:
        longer = [c for c in set(canon.values()) if len(c) > len(words) and contains(c, words)]
        canon[words] = longer[0] if len(longer) == 1 else words
    full = set(canon.values())
    gendered: defaultdict[str, set[str]] = defaultdict(set)
    ranked: defaultdict[str, bool] = defaultdict(bool)
    for title, words in forms:
        if len(words) == 1 and title in GENDERED:
            gendered[words[0]].add(title)
        if len(words) == 1 and title == "rank:surname":
            ranked[words[0]] = True
    out: dict[tuple[str, tuple[str, ...]], tuple] = {}
    for title, words in forms:
        if len(words) > 1:
            out[(title, words)] = ("full", canon[words])
            continue
        w = words[0]
        holders = [c for c in full if w in c]
        male = bool(gendered[w] & {"mr", "sir", "lord"})
        female = bool(gendered[w] & {"mrs", "miss", "lady"})
        if ranked[w] and all(c[-1] != w for c in holders):
            # "Colonel Fitzwilliam" is a surname even if someone's given name is Fitzwilliam
            out[(title, words)] = ("rank", w)
        elif len(holders) == 1 and not (male and female):
            out[(title, words)] = ("full", holders[0])
        elif title in GENDERED:
            out[(title, words)] = (title, w)
        else:
            surname = any(c[-1] == w for c in full) and not any(c[0] == w for c in full)
            if (surname or not holders) and "mr" in gendered[w] and len(gendered[w]) > 1:
                out[(title, words)] = ("mr", w)
            elif not holders and len(gendered[w]) == 1:
                out[(title, words)] = (next(iter(gendered[w])), w)
            else:
                out[(title, words)] = ("bare", w)
    return out


def place_key(words: tuple[str, ...]) -> tuple[str, ...]:
    core = tuple(w for w in words if w not in PLACE_NOUNS and w != "the")
    return core or words


def mask_book(key: str) -> tuple[dict[str, str], list[str], list[str], list[str]]:
    t = load_tokens(key)
    text, ws, para = t["text"], t["ws"], t["para_id"]
    mid = find_mid_sentence(t)
    kinds, unclassified = name_words(t, mid)
    mentions = find_mentions(t, kinds)
    entity_of = resolve_persons(mentions)
    person_no: dict[tuple, int] = {}
    place_no: dict[tuple[str, ...], int] = {}
    replaced: Counter[tuple[str, str]] = Counter()
    stand_in: dict[int, tuple[Mention, str]] = {}
    for m in mentions:
        surface = " ".join(text[m.start : m.end])
        if m.kind == "person":
            ent = entity_of[(m.title, m.words)]
            label = f"Person{person_no.setdefault(ent, len(person_no) + 1)}"
        else:
            label = f"Place{place_no.setdefault(place_key(m.words), len(place_no) + 1)}"
        stand_in[m.start] = (m, label)
        replaced[(surface, label)] += 1

    n_paras = para[-1] + 1 if para else 0
    out_a: list[list[str]] = [[] for _ in range(n_paras)]
    out_b: list[list[str]] = [[] for _ in range(n_paras)]
    i, n = 0, len(text)
    while i < n:
        p = para[i]
        if i in stand_in:
            m, label = stand_in[i]
            tail = " " if ws[m.end - 1] else ""
            original = "".join(text[k] + (" " if ws[k] else "") for k in range(m.start, m.end))
            original = original.rstrip(" ") + tail
            out_a[p].append(label + tail if m.kind == "person" else original)
            out_b[p].append(label + tail)
            i = m.end
        else:
            piece = text[i] + (" " if ws[i] else "")
            out_a[p].append(piece)
            out_b[p].append(piece)
            i += 1
    paras_a = ["".join(x).strip() for x in out_a]
    paras_b = ["".join(x).strip() for x in out_b]
    clean = read_paragraphs(CLEAN / f"{key}.txt")
    if len(clean) != n_paras or any(not p for p in paras_a):
        raise RuntimeError(f"{key}: masked paragraphs do not line up with the clean text")
    write_paragraphs(MASK_A / f"{key}.txt", paras_a)
    write_paragraphs(MASK_B / f"{key}.txt", paras_b)

    persons = sum(m.kind == "person" for m in mentions)
    words = sum(1 for w in text if w[:1].isalpha())
    masked_tokens = sum(m.end - m.start for m in mentions)
    top = "; ".join(f"{s}→{lab} ({c})" for (s, lab), c in replaced.most_common(15))
    row = {
        "key": key,
        "n_persons": str(len(person_no)),
        "n_places": str(len(place_no)),
        "person_mentions": str(persons),
        "place_mentions": str(len(mentions) - persons),
        "masked_share_of_words": f"{masked_tokens / max(words, 1):.4f}",
        "top15_replaced": top,
        "top_unclassified_proper_nouns": "; ".join(
            f"{w} ({c})" for w, c in unclassified.most_common(10)
        ),
    }
    return row, clean, paras_a, paras_b


def spot_check(key: str, clean: list[str], a: list[str], b: list[str]) -> None:
    """Print one mid-length paragraph with several replacements, before and after."""
    best, best_score = None, -1
    for i, (c, masked) in enumerate(zip(clean, b, strict=True)):
        hits = len(re.findall(r"\b(?:Person|Place)\d+\b", masked))
        places = len(re.findall(r"\bPlace\d+\b", masked))
        if 40 <= len(c.split()) <= 110 and hits + 2 * min(places, 2) > best_score:
            best, best_score = i, hits + 2 * min(places, 2)
    if best is None:
        return
    print(f"\n--- spot check {key}, paragraph {best}")
    print(f"clean : {clean[best]}")
    print(f"maskA : {a[best]}")
    print(f"maskB : {b[best]}\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--testbed", type=Path, default=DEFAULT_TESTBED)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--spot", type=int, default=3, help="how many books to spot-check in print")
    args = ap.parse_args()

    rows = select(read_testbed(args.testbed), args.only)
    report: dict[str, dict[str, str]] = {}
    if REPORT.exists():
        with REPORT.open(newline="", encoding="utf-8") as fh:
            report = {r["key"]: r for r in csv.DictReader(fh)}
    done = spots = 0
    for row in rows:
        key = row["key"]
        tok = TOK / f"{key}.parquet"
        if not tok.exists():
            print(f"{key}: no token file, skipped")
            continue
        stale = is_stale(MASK_A / f"{key}.txt", tok, Path(__file__)) or is_stale(
            MASK_B / f"{key}.txt", tok, Path(__file__)
        )
        if not args.force and key in report and not stale:
            continue
        try:
            report[key], clean, a, b = mask_book(key)
            report[key]["notes"] = row["notes"]
        except RuntimeError as exc:
            print(f"FAILED {exc}")
            continue
        done += 1
        r = report[key]
        print(f"{key}: {r['n_persons']} persons, {r['n_places']} places", flush=True)
        if spots < args.spot:
            spot_check(key, clean, a, b)
            spots += 1
    with REPORT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(report[k] for k in sorted(report))
    print(f"mask: {done} masked, report at {REPORT}")


if __name__ == "__main__":
    main()
