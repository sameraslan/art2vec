"""Shared loaders for the round-two experiments (World, Story, Felt, neural Prose)."""

from __future__ import annotations

import json
import re

import numpy as np
from eval.blocks import ROOT, load_testbed

CHUNKS = ROOT / "data" / "chunks"
EMB = ROOT / "data" / "emb"
STANDIN = re.compile(r"\b(?:Person|Place)\d+\b")


def book_keys() -> list[str]:
    """The 87 keys in testbed order."""
    return list(load_testbed().index)


def load_chunks(variant: str, key: str) -> list[dict]:
    with (CHUNKS / variant / f"{key}.jsonl").open() as f:
        return [json.loads(line) for line in f]


def even_sample(n: int, k: int) -> np.ndarray:
    """k indices spread evenly over range(n) (all of them when n <= k)."""
    if n <= k:
        return np.arange(n)
    return np.unique(np.round(np.linspace(0, n - 1, k)).astype(int))


def first_words(text: str, n: int) -> str:
    return " ".join(text.split()[:n])


def unit(X: np.ndarray) -> np.ndarray:
    return X / np.maximum(np.linalg.norm(X, axis=-1, keepdims=True), 1e-12)


def centre_unit(X: np.ndarray, mean: np.ndarray | None = None) -> np.ndarray:
    """Subtract the corpus mean (or the one given) and L2-normalise the rows."""
    return unit(X - (X.mean(0) if mean is None else mean))


def remove_pcs(X: np.ndarray, k: int, *others: np.ndarray) -> list[np.ndarray]:
    """Centre on X's mean, project out X's top-k principal directions, normalise.

    The same mean and directions are applied to ``others`` (split-half matrices).
    """
    mu = X.mean(0)
    Xc = X - mu
    out = []
    V = np.linalg.svd(Xc, full_matrices=False)[2][:k] if k else np.zeros((0, X.shape[1]))
    for M in (X, *others):
        Mc = M - mu
        out.append(unit(Mc - Mc @ V.T @ V))
    return out
