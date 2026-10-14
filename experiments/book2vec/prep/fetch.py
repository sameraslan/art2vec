"""Download each testbed text once into data/raw/.

Project Gutenberg (source=pg): the plain-text UTF-8 file, saved as data/raw/<key>.pg.txt.
Standard Ebooks (source=se): the book's public GitHub repository as one zip request; only the
spine (content.opf) and the text XHTML files are kept, as data/raw/<key>.se.zip. Standard
Ebooks' robots.txt asks bots to stay off /ebooks/*/text* and /downloads/*, so the site itself is
never scraped. If the SE repository cannot be fetched and the row names a Gutenberg id (in the
notes or url column, e.g. "pg:1342"), the Gutenberg transcription is used instead.

One request per second, cached, resumable. What was used is recorded in data/fetch_log.csv.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import requests
from common import DATA, DEFAULT_TESTBED, RAW, VOLUME_BREAK, raw_path, read_testbed, select

USER_AGENT = (
    "art2vec-book2vec-prep/0.1 (one-off research download of ~80 public-domain texts; "
    "https://github.com/sameraslan/art2vec)"
)
DELAY_S = 1.0
LOG = DATA / "fetch_log.csv"
LOG_COLUMNS = ["key", "source_wanted", "source_used", "url", "bytes", "sha1", "status", "when"]
PG_URLS = [
    "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt",
    "https://www.gutenberg.org/ebooks/{id}.txt.utf-8",
]
SE_KEEP = re.compile(r"src/epub/(content\.opf|toc\.xhtml|text/[^/]+\.xhtml)$")

_last_request = 0.0


def get(session: requests.Session, url: str) -> requests.Response:
    """A polite GET: at most one request per second, a few retries on server errors."""
    global _last_request
    resp: requests.Response | None = None
    for attempt in range(3):
        wait = DELAY_S - (time.monotonic() - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.monotonic()
        try:
            resp = session.get(url, timeout=60)
        except requests.RequestException:
            time.sleep(5 * (attempt + 1))
            continue
        if resp.status_code in (429, 500, 502, 503, 504):
            time.sleep(10 * (attempt + 1))
            continue
        return resp
    if resp is None:
        raise requests.ConnectionError(f"no response from {url}")
    return resp


def pg_id(text: str) -> str | None:
    """A Gutenberg id from '1342', 'pg:1342', 'pg1342' or a gutenberg.org URL."""
    text = text.strip()
    if text.isdigit():
        return text
    m = re.search(r"gutenberg\.org/(?:ebooks|cache/epub|files)/(\d+)", text) or re.search(
        r"\bpg\s*[:=#]?\s*(\d+)\b", text, flags=re.I
    )
    return m.group(1) if m else None


def se_repo(row: dict[str, str]) -> str | None:
    """The GitHub repository name for a Standard Ebooks book: author_title[_translator]."""
    for field in (row["source_id"], row["url"]):
        m = re.search(r"github\.com/standardebooks/([\w.\-]+)", field)
        if m:
            return m.group(1).removesuffix(".git")
        m = re.search(r"standardebooks\.org/ebooks/([\w\-/]+)", field)
        slug = m.group(1) if m else field
        slug = re.sub(r"/(text|downloads)(/.*)?$", "", slug.strip().strip("/"))
        if re.fullmatch(r"[\w\-]+(/[\w\-]+){1,3}", slug):
            return slug.replace("/", "_")
        if re.fullmatch(r"[a-z0-9\-]+(_[a-z0-9\-]+)+", slug):
            return slug
    return None


def fetch_pg(session: requests.Session, book_ids: str, out: Path) -> tuple[str, bytes]:
    """One Gutenberg id, or several joined by ';' (volumes, concatenated in the order given)."""
    urls: list[str] = []
    parts: list[bytes] = []
    for book_id in book_ids.split(";"):
        for pattern in PG_URLS:
            url = pattern.format(id=book_id)
            resp = get(session, url)
            if resp.status_code == 200 and len(resp.content) > 2000:
                urls.append(url)
                parts.append(resp.content)
                break
        else:
            raise RuntimeError(f"Gutenberg id {book_id}: no plain-text file ({resp.status_code})")
    body = VOLUME_BREAK.encode().join(parts)
    out.write_bytes(body)
    return " ".join(urls), body


def fetch_se(session: requests.Session, repo: str, out: Path) -> tuple[str, bytes]:
    url = f"https://codeload.github.com/standardebooks/{repo}/zip/refs/heads/master"
    resp = get(session, url)
    if resp.status_code != 200:
        raise RuntimeError(f"Standard Ebooks repo {repo}: HTTP {resp.status_code}")
    slim = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(resp.content)) as src,
        zipfile.ZipFile(slim, "w", zipfile.ZIP_DEFLATED) as dst,
    ):
        for info in src.infolist():
            m = SE_KEEP.search(info.filename)
            if m:
                dst.writestr(m.group(0), src.read(info))
        if "src/epub/content.opf" not in dst.namelist():
            raise RuntimeError(f"Standard Ebooks repo {repo}: no src/epub/content.opf")
    out.write_bytes(slim.getvalue())
    return url, slim.getvalue()


def fetch_one(session: requests.Session, row: dict[str, str]) -> dict[str, str]:
    key, source = row["key"], row["source"].lower()
    entry = {"key": key, "source_wanted": source, "source_used": "", "url": "", "bytes": "0"}
    entry |= {"sha1": "", "status": "", "when": datetime.now(UTC).isoformat(timespec="seconds")}
    errors: list[str] = []
    attempts: list[tuple[str, str]] = []
    if source == "se":
        repo = se_repo(row)
        if repo:
            attempts.append(("se", repo))
        else:
            errors.append("no SE repo derivable from source_id/url")
        fallback = pg_id(row["notes"]) or pg_id(row["url"])
        if fallback:
            attempts.append(("pg", fallback))
    elif source == "pg":
        ids = [pg_id(x) for x in row["source_id"].split(";") if x.strip()]
        book_id = ";".join(i for i in ids if i) if ids and all(ids) else pg_id(row["url"])
        if book_id:
            attempts.append(("pg", book_id))
        else:
            errors.append("no Gutenberg id in source_id/url")
    else:
        errors.append(f"unknown source {source!r}")
    for used, ident in attempts:
        out = RAW / f"{key}.{used}.{'zip' if used == 'se' else 'txt'}"
        tmp = out.with_suffix(out.suffix + ".part")
        try:
            fetcher = fetch_se if used == "se" else fetch_pg
            url, body = fetcher(session, ident, tmp)
        except (RuntimeError, requests.RequestException, zipfile.BadZipFile) as exc:
            tmp.unlink(missing_ok=True)
            errors.append(str(exc))
            continue
        tmp.replace(out)
        entry |= {"source_used": used, "url": url, "bytes": str(len(body))}
        entry["sha1"] = hashlib.sha1(body).hexdigest()
        entry["status"] = "ok" if not errors else "ok (fallback: " + "; ".join(errors) + ")"
        return entry
    entry["status"] = "FAILED: " + "; ".join(errors)
    return entry


def read_log() -> dict[str, dict[str, str]]:
    if not LOG.exists():
        return {}
    with LOG.open(newline="", encoding="utf-8") as fh:
        return {r["key"]: r for r in csv.DictReader(fh)}


def write_log(log: dict[str, dict[str, str]]) -> None:
    with LOG.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOG_COLUMNS)
        writer.writeheader()
        writer.writerows(log[k] for k in sorted(log))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--testbed", type=Path, default=DEFAULT_TESTBED)
    ap.add_argument("--only", nargs="*", help="keys to fetch (default: all)")
    ap.add_argument("--force", action="store_true", help="download again even if cached")
    args = ap.parse_args()

    rows = select(read_testbed(args.testbed), args.only)
    RAW.mkdir(parents=True, exist_ok=True)
    log = read_log()
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    done = failed = 0
    for row in rows:
        key = row["key"]
        if args.force:
            for stale in RAW.glob(f"{key}.*"):
                stale.unlink()
        if raw_path(key) is not None:
            continue
        entry = fetch_one(session, row)
        log[key] = entry
        write_log(log)
        ok = entry["status"].startswith("ok")
        done += ok
        failed += not ok
        print(f"{key}: {entry['status']} [{entry['source_used']}] {entry['bytes']} bytes")
    have = sum(raw_path(r["key"]) is not None for r in rows)
    print(f"fetch: {done} downloaded, {failed} failed, {have}/{len(rows)} present in {RAW}")


if __name__ == "__main__":
    main()
