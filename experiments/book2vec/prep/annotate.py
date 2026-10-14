"""spaCy annotation: data/clean/<key>.txt -> data/tok/<key>.parquet, one row per token.

Columns: para_id (index of the paragraph in the clean file), sent_id (running through the book),
idx (character offset inside the paragraph), text, lower, pos, tag, dep, ent_type, ent_iob,
ws (is the token followed by whitespace), is_quote (inside quotation marks). Line breaks inside
a paragraph (verse) are kept as tokens with pos == "SPACE" so the paragraph can be rebuilt
exactly; filter them out for counts.

Quotation marks: the book's dialogue style is decided first (double or single marks, whichever
opens more quotations). Curly doubles open and close by shape, straight doubles toggle, and
every paragraph starts outside a quotation (a speech carried over a paragraph break reopens
its mark). For single-mark books the closing mark is the same character as the apostrophe, so
the close is chosen heuristically: the first candidate that follows punctuation, else the last
candidate before the next opening mark. data/annotate_report.csv gives the dialogue share per
book as a sanity check.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from common import (
    CLEAN,
    DATA,
    DEFAULT_TESTBED,
    TOK,
    is_stale,
    read_paragraphs,
    read_testbed,
    select,
)

REPORT = DATA / "annotate_report.csv"
REPORT_COLUMNS = [
    "key",
    "n_paragraphs",
    "n_sentences",
    "n_tokens",
    "n_word_tokens",
    "quote_style",
    "dialogue_share",
    "paragraphs_with_dialogue",
    "flags",
    "notes",
]
SINGLE_OPEN_RE = re.compile(r"(?:^|(?<=[\s—(\[“\"]))[‘'](?=[^\s\d])")
SINGLE_OPEN_COUNT_RE = re.compile(r"(?:^|(?<=[\s—(]))[‘'](?=[A-Z])", re.M)
DOUBLE_OPEN_COUNT_RE = re.compile(r"“|(?:^|(?<=[\s—(]))\"(?=\S)", re.M)
CLOSE_PUNCT = ",.!?;:—–-…"
ELISIONS = ("tis", "twas", "twere", "twill", "em ", "em,", "em.", "cause ", "bout ", "im ", "un ")

BATCH = 16  # paragraphs per spaCy batch; small on purpose, the machine is shared

MIN_FREE_BYTES = 1_200_000_000

_nlp = None


def quote_style(paras: list[str]) -> str:
    """'double' or 'single': which mark opens more quotations in this book."""
    text = "\n".join(paras)
    double = len(DOUBLE_OPEN_COUNT_RE.findall(text))
    single = len(SINGLE_OPEN_COUNT_RE.findall(text))
    return "single" if single > 1.5 * double else "double"


def quote_mask_double(para: str) -> list[bool]:
    mask = [False] * len(para)
    inside = False
    for i, ch in enumerate(para):
        if ch == "“":
            inside = True
            mask[i] = True
        elif ch == "”":
            mask[i] = True
            inside = False
        elif ch == '"':
            mask[i] = True
            inside = not inside
        else:
            mask[i] = inside
    return mask


def quote_mask_single(para: str) -> list[bool]:
    mask = [False] * len(para)
    n = len(para)
    opens = [
        m.start()
        for m in SINGLE_OPEN_RE.finditer(para)
        if not para[m.start() + 1 :].lower().startswith(ELISIONS)
    ]
    pos = 0
    for k, start in enumerate(opens):
        if start < pos:
            continue  # an opening mark inside a quotation already taken (nested)
        limit = n
        candidates: list[int] = []
        for j in range(start + 1, n):
            if para[j] not in "’'":
                continue
            before = para[j - 1]
            after = para[j + 1] if j + 1 < n else " "
            if before.isalpha() and after.isalpha():
                continue  # apostrophe inside a word
            if before.isspace():
                continue  # a later opening mark or a leading elision
            candidates.append(j)
        nxt = [o for o in opens[k + 1 :] if o > start]
        sure = [j for j in candidates if para[j - 1] in CLOSE_PUNCT]
        if sure:
            # nested openers before the first sure close stay inside this quotation
            end = sure[0]
        else:
            limit = nxt[0] if nxt else n
            soft = [j for j in candidates if j < limit]
            end = soft[-1] if soft else limit - 1
        for i in range(start, min(end, n - 1) + 1):
            mask[i] = True
        pos = end + 1
    return mask


def load_nlp():  # noqa: ANN201
    global _nlp
    if _nlp is None:
        import spacy

        _nlp = spacy.load("en_core_web_sm", disable=["lemmatizer"])
        _nlp.max_length = 3_000_000
    return _nlp


def annotate_book(key: str) -> dict[str, str]:
    nlp = load_nlp()
    paras = read_paragraphs(CLEAN / f"{key}.txt")
    style = quote_style(paras)
    mask_fn = quote_mask_single if style == "single" else quote_mask_double
    cols: dict[str, list] = {
        c: []
        for c in (
            "para_id",
            "sent_id",
            "idx",
            "text",
            "lower",
            "pos",
            "tag",
            "dep",
            "ent_type",
            "ent_iob",
            "ws",
            "is_quote",
        )
    }
    sent_id = -1
    words = quoted = paras_with_quote = 0
    for para_id, doc in enumerate(nlp.pipe(paras, batch_size=BATCH)):
        mask = mask_fn(paras[para_id])
        any_quote = False
        for tok in doc:
            if tok.is_sent_start or sent_id < 0:
                sent_id += 1
            q = mask[tok.idx] if tok.idx < len(mask) else False
            cols["para_id"].append(para_id)
            cols["sent_id"].append(sent_id)
            cols["idx"].append(tok.idx)
            cols["text"].append(tok.text)
            cols["lower"].append(tok.lower_)
            cols["pos"].append(tok.pos_)
            cols["tag"].append(tok.tag_)
            cols["dep"].append(tok.dep_)
            cols["ent_type"].append(tok.ent_type_)
            cols["ent_iob"].append(tok.ent_iob_)
            cols["ws"].append(bool(tok.whitespace_))
            cols["is_quote"].append(q)
            if tok.is_alpha:
                words += 1
                quoted += q
                any_quote = any_quote or q
        paras_with_quote += any_quote
    cat = pa.dictionary(pa.int32(), pa.string())
    schema = pa.schema(
        [
            ("para_id", pa.int32()),
            ("sent_id", pa.int32()),
            ("idx", pa.int32()),
            ("text", pa.string()),
            ("lower", pa.string()),
            ("pos", cat),
            ("tag", cat),
            ("dep", cat),
            ("ent_type", cat),
            ("ent_iob", cat),
            ("ws", pa.bool_()),
            ("is_quote", pa.bool_()),
        ]
    )
    arrays = [pa.array(cols[f.name]).cast(f.type) for f in schema]
    out = TOK / f"{key}.parquet"
    tmp = out.with_suffix(".parquet.tmp")
    pq.write_table(pa.Table.from_arrays(arrays, schema=schema), tmp, compression="zstd")
    tmp.replace(out)
    share = quoted / words if words else 0.0
    flags = []
    if share < 0.03:
        flags.append("ALMOST_NO_QUOTED_SPEECH (dash dialogue or none?)")
    if share > 0.85:
        flags.append("ALMOST_ALL_QUOTED (unbalanced marks or framed narration?)")
    return {
        "key": key,
        "n_paragraphs": str(len(paras)),
        "n_sentences": str(sent_id + 1),
        "n_tokens": str(len(cols["text"])),
        "n_word_tokens": str(words),
        "quote_style": style,
        "dialogue_share": f"{share:.3f}",
        "paragraphs_with_dialogue": f"{paras_with_quote / max(len(paras), 1):.3f}",
        "flags": "; ".join(flags),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--testbed", type=Path, default=DEFAULT_TESTBED)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    rows = select(read_testbed(args.testbed), args.only)
    TOK.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict[str, str]] = {}
    if REPORT.exists():
        with REPORT.open(newline="", encoding="utf-8") as fh:
            report = {r["key"]: r for r in csv.DictReader(fh)}
    todo = []
    notes = {r["key"]: r["notes"] for r in rows}
    for row in rows:
        key = row["key"]
        src = CLEAN / f"{key}.txt"
        if not src.exists():
            print(f"{key}: no clean text, skipped")
        elif args.force or key not in report or is_stale(TOK / f"{key}.parquet", src):
            todo.append(key)

    def save() -> None:
        with REPORT.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=REPORT_COLUMNS)
            writer.writeheader()
            writer.writerows(report[k] for k in sorted(report))

    def record(r: dict[str, str]) -> None:
        report[r["key"]] = r
        save()
        print(
            f"{r['key']}: {r['n_tokens']} tokens, {r['quote_style']} quotes, "
            f"dialogue share {r['dialogue_share']} {r['flags']}",
            flush=True,
        )

    for key in todo:  # strictly one book at a time, one process
        if shutil.disk_usage(DATA).free < MIN_FREE_BYTES:
            save()
            raise SystemExit("annotate: under 1.2 GB of disk free, stopping (re-run to resume)")
        record(annotate_book(key) | {"notes": notes[key]})
    save()
    print(f"annotate: {len(todo)} annotated, report at {REPORT}")


if __name__ == "__main__":
    main()
