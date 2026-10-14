"""Strip everything the author or translator did not write, and write data/clean/<key>.txt.

Removed where detectable: Gutenberg / Standard Ebooks boilerplate and licence text, title pages,
tables of contents, lists of illustrations, illustration captions, transcriber's notes,
footnotes and their markers, and introductions / prefaces written by someone other than the
author (a front section is treated as someone else's when its heading says so, e.g.
"TRANSLATOR'S PREFACE", or when a bare PREFACE / INTRODUCTION / FOREWORD names the author in the
third person). Chapter headings, epigraphs inside the body and the author's own prefaces stay.

The step is conservative and reports what it did per book in data/clean_report.csv so the result
can be eyeballed. A wrong cut is fixed by a row in clean_overrides.csv (key,start_at,end_at):
start_at / end_at are the opening words of the first paragraph to keep / the first to drop.

Output: paragraphs separated by one blank line, in reading order. "--" is normalised to an em
dash and _italic_ markers are removed; quotation marks are left as the source has them.
"""

from __future__ import annotations

import argparse
import csv
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from common import (
    CLEAN,
    DATA,
    DEFAULT_TESTBED,
    ROOT,
    VOLUME_BREAK,
    is_stale,
    n_words,
    raw_path,
    read_testbed,
    select,
    write_paragraphs,
)

REPORT = DATA / "clean_report.csv"
OVERRIDES = ROOT / "clean_overrides.csv"
REPORT_COLUMNS = [
    "key",
    "source",
    "words_raw",
    "words_clean",
    "n_paragraphs",
    "n_headings",
    "front_cut_words",
    "back_cut_words",
    "sections_cut",
    "sections_kept",
    "n_footnotes_cut",
    "n_illustrations_cut",
    "flags",
    "first_300",
    "last_300",
    "notes",
]

ROMAN = r"[IVXLCDM]+"
NUM_WORD = (
    r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen"
    r"|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|first|second"
    r"|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|last)"
)
CHAPTER_RE = re.compile(
    rf"^(?:(?:chapter|chap\.?|book|part|volume|vol\.?|letter|stave|canto|section|phase|act|scene"
    rf"|episode)\s+(?:{ROMAN}|\d+|{NUM_WORD}(?:[\s-]{NUM_WORD})?)\b"
    rf"|(?:prologue|epilogue|prelude|finale|conclusion|postscript|interlude)\b"
    rf"|(?:the\s+)?(?:{NUM_WORD})\s+(?:book|part|chapter|phase|volume)\b"
    rf"|{ROMAN}\.?$|\d{{1,3}}\.?$"
    rf"|(?:{ROMAN}|\d{{1,3}})\.?\s*[—:\-.]?\s+\S.*)",
    re.I,
)
ROMAN_LEAD_RE = re.compile(rf"^(?:{ROMAN}|\d{{1,3}})\.?\s*[—:\-.]?\s+(.*)$")
FRONT_CUT_RE = re.compile(
    r"^(?:(?:table\s+of\s+)?contents|(?:list\s+of\s+)?illustrations|list\s+of\s+plates"
    r"|.*\btranslat(?:or|ors|ion)\b.*|.*\beditor(?:s|ial)?\b.*|.*\btranscriber.*"
    r"|.*\bbiograph.*|.*\bbibliograph.*|.*\bpublishers?\b.*|.*\bnote\s+on\s+the\s+text.*"
    r"|.*\babout\s+the\s+author.*|.*\bchronology.*|.*\backnowledge?ments?.*|.*\berrata.*"
    r"|.*\bcritical\s+introduction.*|.*\bintroductory\s+note.*|.*\bprefatory\s+note.*)\W*$",
    re.I,
)
FRONT_MAYBE_RE = re.compile(
    r"^(?:(?:the\s+)?(?:author[’']?s?\s+)?(?:general\s+)?"
    r"(?:preface|introduction|foreword|prefatory|advertisement|to\s+the\s+reader|note"
    r"|dedication|apology)\b.{0,60})$",
    re.I,
)
BACK_CUT_RE = re.compile(
    r"^(?:the\s+end\b.{0,30}|finis\W*|end\s+of\s+(?:the\s+)?(?:project|vol|book|part|novel|story"
    r"|second|third|fourth|last|final)\b.*|foot-?notes?\W*|end-?notes?\W*|notes\W*"
    r"|.*\btranscriber.*|.*\btranslator[’']?s?\s+notes?.*|glossary\W*|index\W*"
    r"|by\s+the\s+same\s+author.*|works\s+by\b.*|other\s+(?:books|works)\s+by\b.*"
    r"|advertisements?\W*|.*\bbibliograph.*|.*\babout\s+the\s+author.*|colophon\W*)$",
    re.I,
)
PRINTER_RE = re.compile(r"(?i)\b(press|print(?:ed|ers?)|publish(?:ed|ers?)|limited|ltd)\b")
CITY_RE = re.compile(r"(?i)(london|edinburgh|glasgow|new york|boston|philadelphia|paris)")
END_MARK_RE = re.compile(r"^(?:the\s+end|finis)\W*$", re.I)
PG_START_RE = re.compile(r"^\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.M)
PG_END_RE = re.compile(r"^\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.M)
FOOTNOTE_PARA_RE = re.compile(r"^\s*\[(?:\*+|\d{1,3}|[A-Za-z]|†|‡)\]\s+\S")
FOOTNOTE_MARK_RE = re.compile(r"\s?\[(?:\*+|\d{1,3}|[A-Z]|†|‡)\]")
PAGE_MARK_RE = re.compile(r"\s?(?:\[(?:Pg|Page|p\.)\s*[\divxlc]+\]|\{\d{1,4}\})", re.I)
BRACKET_OPEN_RE = re.compile(
    r"\[\s*(Illustration|Footnote|Transcriber[’']?s?\s+Note|Sidenote|Blank Page|Decoration"
    r"|Frontispiece|Music|Greek)\b",
    re.I,
)
SE_DROP_FILES = re.compile(
    r"^(titlepage|imprint|colophon|uncopyright|halftitle(page)?|endnotes|loi|toc|copyright-page"
    r"|dramatis-personae|frontispiece|glossary|bibliography)"
)
SE_FRONT_TYPES = ("introduction", "foreword", "preface", "afterword", "preamble")
SE_BLOCKS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "dt", "dd", "figcaption"}
SE_SKIP = {"head", "figure", "img", "nav", "style", "script"}
XHTML = "{http://www.w3.org/1999/xhtml}"
EPUB_TYPE = "{http://www.idpf.org/2007/ops}type"


@dataclass
class Para:
    text: str
    heading: bool = False
    toc: bool = False
    section: str = ""  # SE only: the section-level epub:type of the file it came from


@dataclass
class Report:
    key: str
    source: str
    words_raw: int = 0
    front_cut_words: int = 0
    back_cut_words: int = 0
    sections_cut: list[str] = field(default_factory=list)
    sections_kept: list[str] = field(default_factory=list)
    n_footnotes: int = 0
    n_illustrations: int = 0
    flags: list[str] = field(default_factory=list)


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words_of(paras: list[Para]) -> int:
    return sum(n_words(p.text) for p in paras)


def heading_label(text: str) -> str:
    return squash(text).strip(" .:—-_*[]").strip()


def is_chapter_heading(text: str) -> bool:
    """A short paragraph that names a chapter, book, part or similar division."""
    label = heading_label(text)
    if not label or "\n" in text.strip() and len(text.strip().split("\n")) > 3:
        return False
    if len(label.split()) > 14 or len(label) > 90:
        return False
    if not CHAPTER_RE.match(label):
        return False
    m = ROMAN_LEAD_RE.match(label)
    keyword = re.match(r"(?i)(chapter|chap|book|part|volume|vol|letter|stave|canto|act)\b", label)
    if m and not keyword and not re.fullmatch(rf"(?:{ROMAN}|\d{{1,3}})\.?", label):
        rest = m.group(1)
        lead = label.split()[0].rstrip(".:—-")
        # "I had ..." is a sentence, "I. THE PRISON-DOOR" is a heading
        if not re.fullmatch(rf"{ROMAN}|\d{{1,3}}", lead) or lead != lead.upper():
            return False
        punctuated = label[len(lead) : len(lead) + 1] in ".:—"
        titled = rest == rest.upper() or (punctuated and rest[:1].isupper() and len(rest) < 70)
        if not titled or rest.rstrip().endswith((",", ";")):
            return False
        if not punctuated and lead in {"I", "A"} and rest != rest.upper():
            return False
    return True


def is_toc_block(raw_block: str) -> bool:
    """A multi-line block made mostly of chapter names or page-numbered entries."""
    lines = [ln.strip() for ln in raw_block.split("\n") if ln.strip()]
    if len(lines) < 3:
        return False
    hits = sum(
        bool(is_chapter_heading(ln) or re.search(r"(\.{3,}|\s{2,})\s*[\divxlc]+\.?$", ln, re.I))
        for ln in lines
    )
    return hits / len(lines) >= 0.6


def strip_brackets(text: str, rep: Report) -> str:
    """Drop [Illustration: ...], [Footnote ...] and similar blocks, keeping chapter names
    that some editions print inside an illustration caption."""
    out: list[str] = []
    pos = 0
    while True:
        m = BRACKET_OPEN_RE.search(text, pos)
        if not m:
            out.append(text[pos:])
            break
        out.append(text[pos : m.start()])
        depth, i = 0, m.start()
        while i < len(text):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        inner = text[m.end() : i]
        kind = m.group(1).lower()
        if kind.startswith("footnote"):
            rep.n_footnotes += 1
        elif kind.startswith(("illustration", "frontispiece", "decoration")):
            rep.n_illustrations += 1
            kept = [
                ln.strip(" :.·_")
                for ln in inner.split("\n")
                if re.match(
                    r"(?i)^\W*(chapter|book|part|volume)\s+([ivxlcdm]+|\d+)\W*$|^\W*preface\W*$",
                    ln.strip(),
                )
            ]
            if kept:
                out.append("\n\n" + "\n\n".join(kept) + "\n\n")
        pos = min(i + 1, len(text))
    return "".join(out)


def tidy_inline(text: str) -> str:
    text = re.sub("[\u2060\ufeff\u00ad\u200a\u200b]", "", text)  # joiners, hair spaces
    text = re.sub("[\u00a0\u202f\u2009\u2002\u2003]", " ", text)
    text = PAGE_MARK_RE.sub("", text)
    text = FOOTNOTE_MARK_RE.sub("", text)
    text = re.sub(r"\^\{([^}]*)\}", r"\1", text)
    text = re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", "", text)
    text = re.sub(r"(?<!-)--(?!-)", "—", text)
    return text


def pg_paragraphs(raw: str, rep: Report) -> list[Para]:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").lstrip("﻿")
    start, end = PG_START_RE.search(raw), PG_END_RE.search(raw)
    if not start or not end:
        rep.flags.append("NO_PG_MARKERS")
    body = raw[start.end() if start else 0 : end.start() if end else len(raw)]
    rep.words_raw += n_words(body)
    body = strip_brackets(body, rep)
    paras: list[Para] = []
    for block in re.split(r"\n[ \t]*\n", body):
        if not block.strip():
            continue
        if FOOTNOTE_PARA_RE.match(block):
            rep.n_footnotes += 1
            continue
        if re.fullmatch(r"[\s*_\-=—.·+~]+", block):
            continue
        lines = [ln for ln in block.split("\n") if ln.strip()]
        toc = is_toc_block(block)
        verse = (
            len(lines) > 1
            and all(ln.startswith(("  ", "\t")) for ln in lines)
            and max(len(ln.strip()) for ln in lines) < 62
        )
        joiner = "\n" if verse or toc else " "
        text = tidy_inline(joiner.join(squash(ln) for ln in lines)).strip()
        if text:
            paras.append(Para(text, heading=not toc and is_chapter_heading(text), toc=toc))
    mark_contents_runs(paras)
    return paras


def mark_contents_runs(paras: list[Para]) -> None:
    """A contents list set one entry per paragraph: five or more headings in a row, or a
    heading that ends in a page number. If a label repeats inside the run, the list has ended
    and the book has begun (PART I / CHAPTER I straight after the contents)."""
    i, n = 0, len(paras)
    while i < n:
        if not paras[i].heading:
            i += 1
            continue
        j = i
        seen: set[str] = set()
        while j < n and paras[j].heading:
            label = " ".join(re.sub(r"\W+", " ", paras[j].text).lower().split()[:2])
            if label in seen:
                break
            seen.add(label)
            j += 1
        repeated = j < n and paras[j].heading
        if j - i >= 5 or (repeated and j - i >= 3):
            for p in paras[i:j]:
                p.heading, p.toc = False, True
        i = max(j, i + 1) if not repeated else j
    for p in paras:
        paged = re.search(r"(?:\.\s*){2,}\d+$|[a-z,;]\s+\d{1,4}$", p.text)
        if p.heading and paged and len(p.text.split()) >= 4:
            p.heading, p.toc = False, True


def se_text(el: ET.Element) -> str:
    """Text of a block element: <br/> becomes a newline, note references are dropped."""
    parts: list[str] = [re.sub(r"\s+", " ", el.text or "")]
    for child in el:
        tag = child.tag.replace(XHTML, "")
        if tag == "br":
            parts.append("\n")
        elif tag == "a" and "noteref" in child.get(EPUB_TYPE, ""):
            pass
        elif tag not in SE_SKIP:
            parts.append(se_text(child))
        parts.append(re.sub(r"\s+", " ", child.tail or ""))
    return "".join(parts)


def se_walk(el: ET.Element, section: str, out: list[Para]) -> None:
    tag = el.tag.replace(XHTML, "")
    if tag in SE_SKIP:
        return
    if tag == "hgroup":
        bits = [squash(se_text(c)) for c in el if squash(se_text(c))]
        if bits:
            out.append(Para(". ".join(b.rstrip(".") for b in bits), heading=True, section=section))
        return
    if tag in SE_BLOCKS:
        if tag == "tr":
            text = " — ".join(squash(se_text(c)) for c in el if squash(se_text(c)))
        else:
            text = "\n".join(squash(ln) for ln in se_text(el).split("\n") if squash(ln))
        if text:
            out.append(Para(text, heading=tag[0] == "h" and len(tag) == 2, section=section))
        return
    for child in el:
        se_walk(child, section, out)


def se_paragraphs(path: Path, rep: Report, surname: str) -> list[Para]:
    paras: list[Para] = []
    with zipfile.ZipFile(path) as zf:
        opf = ET.fromstring(zf.read("src/epub/content.opf"))
        ns = {"opf": "http://www.idpf.org/2007/opf"}
        hrefs = {i.get("id"): i.get("href") for i in opf.findall(".//opf:manifest/opf:item", ns)}
        spine = [hrefs.get(i.get("idref"), "") for i in opf.findall(".//opf:spine/opf:itemref", ns)]
        for href in spine:
            name = Path(href or "").name
            if not name or f"src/epub/{href}" not in zf.namelist():
                continue
            root = ET.fromstring(zf.read(f"src/epub/{href}"))
            body = root.find(f"{XHTML}body")
            if body is None:
                continue
            sections = body.iter(f"{XHTML}section")
            types = " ".join([body.get(EPUB_TYPE, "")] + [s.get(EPUB_TYPE, "") for s in sections])
            file_paras: list[Para] = []
            se_walk(body, name, file_paras)
            n = words_of(file_paras)
            rep.words_raw += n
            rep.n_footnotes += sum(
                "noteref" in a.get(EPUB_TYPE, "") for a in body.iter(f"{XHTML}a")
            )
            if SE_DROP_FILES.match(name):
                if name.startswith("endnotes"):
                    rep.sections_cut.append(f"endnotes({n}w)")
                continue
            if any(t in types for t in SE_FRONT_TYPES) and "bodymatter" not in types:
                text = " ".join(p.text for p in file_paras)
                label = f"{name.removesuffix('.xhtml')}({n}w)"
                first = file_paras[0].text if file_paras else ""
                if other_hand(f"{name.removesuffix('.xhtml')} {first}"[:80], text, surname):
                    rep.sections_cut.append(label)
                    rep.front_cut_words += n
                    continue
                rep.sections_kept.append(label)
            paras.extend(file_paras)
    return paras


def other_hand(heading: str, text: str, surname: str) -> bool:
    """Was this front section written by someone other than the author? True when the heading
    says so, or when the text names the author in the third person at least twice."""
    if FRONT_CUT_RE.match(heading_label(heading)):
        return True
    if re.search(r"(?i)\bauthor[’']?s\b", heading):
        return False
    if len(re.findall(r"(?i)\btranslat\w*|\bthe editor\b", text)) >= 2:
        return True
    stem = re.escape(surname[:5]) if len(surname) >= 4 else None
    return bool(stem) and len(re.findall(rf"\b{stem}", text, flags=re.I)) >= 2


def front_kind(p: Para) -> str:
    """'cut', 'maybe' or '' for a short paragraph that could head a front-matter section."""
    label = heading_label(p.text)
    if p.toc or not label or len(label.split()) > 9 or len(label) > 70 or "\n" in p.text:
        return ""
    if label.endswith((",", ";")) or (label != label.upper() and label != label.title()):
        return ""
    if FRONT_CUT_RE.match(label):
        return "cut"
    return "maybe" if FRONT_MAYBE_RE.match(label) else ""


def starts_body(paras: list[Para], i: int) -> bool:
    """A chapter heading starts the book when prose follows it (a contents entry is followed
    by more entries, or by a front-matter heading)."""
    following: list[Para] = []
    for p in paras[i + 1 : i + 12]:
        if p.toc or front_kind(p):
            break
        if p.heading:
            if words_of(following) >= 40:
                break
            if len(following) > 1:
                return False
            continue
        following.append(p)
    return words_of(following) >= 40


def cut_front(paras: list[Para], rep: Report, surname: str) -> list[Para]:
    """Drop the title page, contents and other people's introductions (Gutenberg texts)."""
    body = next((i for i, p in enumerate(paras) if p.heading and starts_body(paras, i)), None)
    if body is None:
        rep.flags.append("NO_CHAPTER_HEADINGS_FOUND")
        body = next((i for i, p in enumerate(paras) if n_words(p.text) >= 60), 0)
    else:
        while body > 0 and paras[body - 1].heading and not paras[body - 1].toc:
            body -= 1
    marks = [i for i in range(body) if front_kind(paras[i])] + [body]
    kept: list[Para] = []
    loose = paras[: marks[0]]
    for a, b in zip(marks, marks[1:], strict=False):
        head, section = paras[a], paras[a + 1 : b]
        n = words_of(section)
        label = f"{heading_label(head.text)[:40]}({n}w)"
        text = " ".join(p.text for p in section)
        if front_kind(head) == "cut" or other_hand(head.text, text, surname) or n < 20:
            rep.sections_cut.append(label)
            rep.front_cut_words += n + n_words(head.text)
        else:
            rep.sections_kept.append(label)
            kept.append(Para(head.text, heading=True))
            kept.extend(p for p in section if not p.toc)
    loose_words = words_of(loose)
    rep.front_cut_words += loose_words
    if loose_words > 1500:
        rep.flags.append(f"BIG_UNNAMED_FRONT_CUT({loose_words}w)")
    return kept + paras[body:]


def cut_back(paras: list[Para], rep: Report) -> list[Para]:
    """Drop what follows THE END, and trailing notes / advertisements (Gutenberg texts)."""
    n = len(paras)
    total = words_of(paras)
    tail_start = max(0, n - max(40, n // 5))
    cut_at: int | None = None
    seen = 0
    for i in range(n - 1, tail_start - 1, -1):
        p = paras[i]
        seen += n_words(p.text)
        label = heading_label(p.text)
        if len(label.split()) > 14 or "\n" in p.text:
            continue
        end_mark = bool(END_MARK_RE.match(label)) or bool(
            re.match(r"(?i)end of (the )?project gutenberg", label)
            or (i >= n - 3 and re.fullmatch(r"(?i)end of the \w+(?: \w+){0,3}", label))
            or (CITY_RE.fullmatch(label) and i + 1 < n and PRINTER_RE.search(paras[i + 1].text))
        )
        if (end_mark or BACK_CUT_RE.match(label)) and seen <= max(3000, total * 0.1):
            if not end_mark and label != label.upper() and label != label.title():
                continue
            cut_at = i
            rep.sections_cut.append(f"back:{label[:40]}({seen}w)")
    if cut_at is None:
        cut_at = n
    while cut_at > 1 and PRINTER_RE.search(paras[cut_at - 1].text):
        last = paras[cut_at - 1].text
        if last != last.upper() or n_words(last) > 30:
            break
        cut_at -= 1
        rep.sections_cut.append(f"back:printer({n_words(last)}w)")
    rep.back_cut_words += words_of(paras[cut_at:])
    return paras[:cut_at]


def apply_override(paras: list[Para], rule: dict[str, str], rep: Report) -> list[Para]:
    def find(prefix: str) -> int:
        want = squash(prefix).lower()
        for i, p in enumerate(paras):
            if squash(p.text).lower().startswith(want):
                return i
        rep.flags.append(f"OVERRIDE_NOT_FOUND({prefix[:30]})")
        return -1

    a = find(rule["start_at"]) if rule.get("start_at") else 0
    b = find(rule["end_at"]) if rule.get("end_at") else len(paras)
    a, b = max(a, 0), (b if b >= 0 else len(paras))
    rep.front_cut_words, rep.back_cut_words = words_of(paras[:a]), words_of(paras[b:])
    rep.flags.append("OVERRIDE")
    return paras[a:b]


def read_overrides() -> dict[str, dict[str, str]]:
    if not OVERRIDES.exists():
        return {}
    with OVERRIDES.open(newline="", encoding="utf-8") as fh:
        return {r["key"]: r for r in csv.DictReader(fh) if r.get("key")}


def clean_book(row: dict[str, str], src: Path, rule: dict[str, str] | None) -> dict[str, str]:
    key = row["key"]
    surname = re.sub(r"[^\w\s\-']", "", row["author"]).split()[-1] if row["author"] else ""
    source = "se" if src.name.endswith(".se.zip") else "pg"
    rep = Report(key=key, source=source)
    if source == "se":
        paras = se_paragraphs(src, rep, surname)
        for p in paras:
            p.text = tidy_inline(p.text)
        if rule:
            paras = apply_override(paras, rule, rep)
    else:
        # a multi-volume work is cleaned volume by volume, then joined in order
        volumes = src.read_text(encoding="utf-8", errors="replace").split(VOLUME_BREAK.strip())
        paras = []
        for volume in volumes:
            vol = pg_paragraphs(volume, rep)
            if rule and len(volumes) == 1:
                vol = apply_override(vol, rule, rep)
            else:
                vol = cut_back(cut_front(vol, rep, surname), rep)
            paras.extend(vol)
        if len(volumes) > 1:
            rep.flags.append(f"{len(volumes)}_VOLUMES_JOINED")
    paras = [p for p in paras if not p.toc and p.text.strip()]
    for p in paras:
        p.heading = p.heading or is_chapter_heading(p.text)
    words = words_of(paras)
    if words < 15000:
        rep.flags.append("SHORT(<15k words)")
    if rep.words_raw and words / rep.words_raw < 0.8:
        rep.flags.append(f"CUT_OVER_20%({1 - words / rep.words_raw:.0%})")
    if row["title"] and re.search(re.escape(row["title"]), paras[0].text if paras else "", re.I):
        rep.flags.append("TITLE_IN_FIRST_PARAGRAPH")
    write_paragraphs(CLEAN / f"{key}.txt", [p.text for p in paras])
    text = "\n\n".join(p.text for p in paras)
    return {
        "key": key,
        "source": source,
        "words_raw": str(rep.words_raw),
        "words_clean": str(words),
        "n_paragraphs": str(len(paras)),
        "n_headings": str(sum(p.heading for p in paras)),
        "front_cut_words": str(rep.front_cut_words),
        "back_cut_words": str(rep.back_cut_words),
        "sections_cut": "; ".join(rep.sections_cut),
        "sections_kept": "; ".join(rep.sections_kept),
        "n_footnotes_cut": str(rep.n_footnotes),
        "n_illustrations_cut": str(rep.n_illustrations),
        "flags": "; ".join(rep.flags),
        "first_300": text[:300].replace("\n", " ⏎ "),
        "last_300": text[-300:].replace("\n", " ⏎ "),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--testbed", type=Path, default=DEFAULT_TESTBED)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    rows = select(read_testbed(args.testbed), args.only)
    overrides = read_overrides()
    report: dict[str, dict[str, str]] = {}
    if REPORT.exists():
        with REPORT.open(newline="", encoding="utf-8") as fh:
            report = {r["key"]: r for r in csv.DictReader(fh)}
    done = missing = 0
    for row in rows:
        key = row["key"]
        src = raw_path(key)
        if src is None:
            missing += 1
            print(f"{key}: no raw file, skipped")
            continue
        out = CLEAN / f"{key}.txt"
        deps = [src, Path(__file__)] + ([OVERRIDES] if OVERRIDES.exists() else [])
        if not args.force and key in report and not is_stale(out, *deps):
            continue
        report[key] = clean_book(row, src, overrides.get(key)) | {"notes": row["notes"]}
        done += 1
        r = report[key]
        print(
            f"{key}: {r['words_clean']} words, front -{r['front_cut_words']}, "
            f"back -{r['back_cut_words']} {r['flags']}"
        )
    with REPORT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(report[k] for k in sorted(report))
    print(f"clean: {done} cleaned, {missing} missing raw, report at {REPORT}")


if __name__ == "__main__":
    main()
