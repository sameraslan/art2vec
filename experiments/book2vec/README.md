# book2vec experiments: shared data prep

Everything the book2vec experiments read comes out of this prep. Texts and derived data live
under `data/` and are never committed (`.gitignore`); the scripts, the testbed and the override
file are.

## Setup

    cd experiments/book2vec
    uv venv --python cpython-3.11-macos-aarch64 --python-preference only-managed .venv
    uv pip install --python .venv/bin/python -r requirements.txt

The venv is arm64 Python 3.11 with numpy, scipy, pandas, scikit-learn, pyarrow, requests,
spaCy + `en_core_web_sm`, torch (CPU/MPS) and sentence-transformers. No embedding model is
downloaded by the prep.

## Run

    prep/run_all.sh                         # testbed.csv, every book
    prep/run_all.sh testbed.csv key1 key2   # only these keys
    prep/run_all.sh testbed.dev.csv         # the two development books

Every step skips work already done, so the script is safe to re-run. Steps run one after the
other and one book at a time, in one process (the machine is shared). Single steps:

    .venv/bin/python prep/fetch.py    [--testbed F] [--only KEY ...] [--force]
    .venv/bin/python prep/clean.py    ...
    .venv/bin/python prep/annotate.py ...
    .venv/bin/python prep/mask.py     ... [--spot N]
    .venv/bin/python prep/chunk.py    ...

## Steps

| Step | Reads | Writes | What it does |
|---|---|---|---|
| `fetch.py` | `testbed.csv` | `data/raw/<key>.se.zip` or `<key>.pg.txt`, `data/fetch_log.csv` | Downloads each text once, one request per second. Standard Ebooks books come from their public GitHub repositories (spine + text XHTML only), never from standardebooks.org, whose robots.txt asks bots to stay off the text pages. Gutenberg books are the plain-text UTF-8 file; several ids joined by `;` are concatenated as volumes. |
| `clean.py` | `data/raw/` | `data/clean/<key>.txt`, `data/clean_report.csv` | Removes boilerplate, licence text, title pages, contents, illustration captions, transcriber's notes, footnotes and endnotes, and front matter by another hand. Paragraphs are separated by one blank line; chapter headings are kept as their own paragraphs. |
| `annotate.py` | `data/clean/` | `data/tok/<key>.parquet`, `data/annotate_report.csv` | spaCy `en_core_web_sm` (lemmatizer off). One row per token: `para_id, sent_id, idx, text, lower, pos, tag, dep, ent_type, ent_iob, ws, is_quote`. |
| `mask.py` | `data/tok/` | `data/maskA/<key>.txt`, `data/maskB/<key>.txt`, `data/mask_report.csv` | Replaces names with stand-ins that are consistent within a book. A = persons, B = persons + places. |
| `chunk.py` | `data/clean`, `maskA`, `maskB` | `data/chunks/<variant>/<key>.jsonl` | Chunks of about 1,000 words on paragraph boundaries: `key, idx, n_words, start_para, end_para, text`. |

## Things to know before using the data

- **Check `data/clean_report.csv` by eye.** It gives, per book, what was cut and kept, the
  first and last 300 characters, word counts and flags. A front section headed PREFACE /
  INTRODUCTION / FOREWORD is cut when its heading names a translator or editor, or when its text
  speaks of translating or names the author in the third person twice; otherwise it is kept as
  the author's and listed under `sections_kept`. Fix a wrong call with a row in
  `clean_overrides.csv` (`key,start_at,end_at`: the opening words of the first paragraph to
  keep and of the first paragraph to drop; single-volume Gutenberg texts and SE texts).
- **Typography differs by source.** Standard Ebooks texts have curly quotes and em dashes;
  Gutenberg texts often have straight quotes. `--` is turned into an em dash and `_italics_`
  markers are dropped, nothing else is normalised. Prose features that count punctuation should
  fold quote styles first.
- **Paragraph ids line up across variants.** `para_id` in the parquet, the paragraph order in
  `clean`, `maskA` and `maskB`, and `start_para` / `end_para` in the chunks all index the same
  paragraphs, and chunk `idx` is the same passage in all three variants.
- **`pos == "SPACE"` rows** are line breaks inside verse paragraphs; drop them for counts.
- **`is_quote`** marks tokens inside quotation marks. The book's style (double or single marks)
  is decided first; single-mark closing is heuristic because it shares a character with the
  apostrophe. Books with dash dialogue or none (Joyce) show a dialogue share near zero and are
  flagged in `data/annotate_report.csv`.
- **Masking is a heuristic** (see the docstring of `mask.py`). Known weaknesses: nicknames and
  diminutives are separate people (Lizzy / Elizabeth, Rodya / Raskolnikov); a bare surname
  shared by a family goes to one stand-in; names that are also common words (Grace, Rose) are
  missed unless clearly capitalised mid-sentence; a name seen only at sentence starts is
  missed; real and invented places are both masked in B; a few people are typed as places and
  the reverse; adjectives from names (Napoleonic) and titles of nobility by place ("the Duke of
  Omnium") leak. `data/mask_report.csv` lists the 15 most replaced names per book.
- The `notes` column of the testbed (abridged translations and the like) is carried into every
  report.
