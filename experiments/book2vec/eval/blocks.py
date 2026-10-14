"""Block files and the testbed table.

A block is one candidate measurement of the 87 test books, stored as
``data/blocks/<name>.npz``:

    keys    (n,) str    book keys, in row order
    X       (n, d)      one vector per book                      } one of the two
    D       (n, n)      symmetric distances, zero diagonal       }
    X_a, X_b            optional: vectors from the odd / even ~1,000-word chunks of each book
    X_h1, X_h2          optional: vectors from the first / second half of each book
    D_ab, D_h12         optional, for D blocks: D_ab[i, j] = distance from half a of book i to
                        half b of book j (same for h1 / h2)
    meta    str         JSON: {"what": ..., "input_level": "ordered text" | "page bag" |
                        "book bag", "metric": "cosine" | "euclidean" | "precomputed",
                        "flagged": [keys whose input is known to be unreliable], ...params}

Vectors in ``X`` are final (already z-scored if the method z-scores); the harness only applies
``metric``. Run things from ``experiments/book2vec`` as ``.venv/bin/python -m eval.score ...``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BLOCK_DIR = ROOT / "data" / "blocks"
RESULTS = ROOT / "results"
INPUT_LEVELS = ("ordered text", "page bag", "book bag")
METRICS = ("cosine", "euclidean", "precomputed")


@dataclass
class Block:
    name: str
    keys: np.ndarray
    meta: dict
    X: np.ndarray | None = None
    D: np.ndarray | None = None
    extra: dict[str, np.ndarray] = field(default_factory=dict)

    @property
    def metric(self) -> str:
        return self.meta.get("metric", "cosine" if self.D is None else "precomputed")

    def distances(self) -> np.ndarray:
        """Full n x n distance matrix."""
        if self.D is not None:
            return np.asarray(self.D, dtype=float)
        return cross_distance(self.X, self.X, self.metric)

    def split_distances(self, kind: str) -> np.ndarray | None:
        """Distances between the two halves; kind is "ab" or "h12". None if not stored."""
        a, b = ("X_a", "X_b") if kind == "ab" else ("X_h1", "X_h2")
        if a in self.extra and b in self.extra:
            return cross_distance(self.extra[a], self.extra[b], self.metric)
        return self.extra.get(f"D_{kind}")

    def subset(self, keep: np.ndarray) -> Block:
        """The block restricted to the rows where ``keep`` is true."""
        extra = {}
        for k, v in self.extra.items():
            extra[k] = v[np.ix_(keep, keep)] if k.startswith("D_") else v[keep]
        return Block(
            self.name,
            self.keys[keep],
            self.meta,
            None if self.X is None else self.X[keep],
            None if self.D is None else self.D[np.ix_(keep, keep)],
            extra,
        )


def cross_distance(A: np.ndarray, B: np.ndarray, metric: str) -> np.ndarray:
    """Distances between the rows of A and the rows of B."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    if metric == "cosine":
        An = A / np.maximum(np.linalg.norm(A, axis=1, keepdims=True), 1e-12)
        Bn = B / np.maximum(np.linalg.norm(B, axis=1, keepdims=True), 1e-12)
        return 1.0 - An @ Bn.T
    if metric == "euclidean":
        sq = (A**2).sum(1)[:, None] + (B**2).sum(1)[None, :] - 2 * A @ B.T
        return np.sqrt(np.maximum(sq, 0.0))
    raise ValueError(f"cannot compute distances for metric {metric!r}")


def save_block(
    name: str,
    keys: list[str] | np.ndarray,
    meta: dict,
    *,
    X: np.ndarray | None = None,
    D: np.ndarray | None = None,
    block_dir: Path = BLOCK_DIR,
    **extra: np.ndarray,
) -> Path:
    """Write a block file after checking its shape and meta."""
    if (X is None) == (D is None):
        raise ValueError("give exactly one of X or D")
    if meta.get("input_level") not in INPUT_LEVELS:
        raise ValueError(f"meta['input_level'] must be one of {INPUT_LEVELS}")
    meta = {"metric": "precomputed" if X is None else "cosine", **meta}
    if meta["metric"] not in METRICS:
        raise ValueError(f"meta['metric'] must be one of {METRICS}")
    n = len(keys)
    arrays: dict[str, np.ndarray] = {"keys": np.asarray(keys, dtype=str)}
    main = np.asarray(X if X is not None else D, dtype=np.float32)
    if main.shape[0] != n or (D is not None and main.shape != (n, n)):
        raise ValueError(f"{name}: bad shape {main.shape} for {n} keys")
    arrays["X" if X is not None else "D"] = main
    for k, v in extra.items():
        v = np.asarray(v, dtype=np.float32)
        if v.shape[0] != n:
            raise ValueError(f"{name}: {k} has {v.shape[0]} rows, expected {n}")
        arrays[k] = v
    for k, v in arrays.items():
        if k != "keys" and not np.isfinite(v).all():
            raise ValueError(f"{name}: {k} has non-finite values")
    block_dir.mkdir(parents=True, exist_ok=True)
    path = block_dir / f"{name}.npz"
    np.savez_compressed(path, meta=json.dumps(meta), **arrays)
    return path


def load_block(path: str | Path) -> Block:
    """Read a block file; a bare name is looked up in data/blocks/."""
    p = Path(path)
    if not p.exists():
        p = BLOCK_DIR / f"{p.name.removesuffix('.npz')}.npz"
    with np.load(p, allow_pickle=False) as z:
        extra = {k: z[k] for k in z.files if k not in ("keys", "X", "D", "meta")}
        return Block(
            name=p.stem,
            keys=z["keys"].astype(str),
            meta=json.loads(str(z["meta"])),
            X=z["X"] if "X" in z.files else None,
            D=z["D"] if "D" in z.files else None,
            extra=extra,
        )


def load_testbed(path: Path | None = None) -> pd.DataFrame:
    """The testbed, indexed by key, with parsed tags, word counts and dialogue flags.

    Adds: ``tags`` (dict tag type -> set of values; bare tags map to {""}), ``n_words``,
    ``dialogue_share``, ``quote_flag`` (from data/annotate_report.csv, when it exists).
    """
    tb = pd.read_csv(path or ROOT / "testbed.csv", dtype=str, keep_default_na=False)
    tb["year"] = tb["year"].astype(int)
    tb["tags"] = tb["group_tags"].map(parse_tags)
    rep = ROOT / "data" / "annotate_report.csv"
    if path is None and rep.exists():
        r = pd.read_csv(rep).set_index("key")
        tb["n_words"] = tb["key"].map(r["n_word_tokens"])
        tb["dialogue_share"] = tb["key"].map(r["dialogue_share"])
        tb["quote_flag"] = tb["key"].map(r["flags"]).fillna("")
    return tb.set_index("key", drop=False)


def parse_tags(s: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for part in filter(None, (p.strip() for p in s.split(";"))):
        k, _, v = part.partition(":")
        out.setdefault(k, set()).add(v)
    return out
