"""Turn the gathered text and facts about each film into proxy blocks for analyse.py.

Reads proxy_text/*.jsonl in the cache home and writes proxies/<name>.npz (ids, vectors).
Text is embedded with the same small text embedder the words block uses, on CPU, in
chunks of about 200 words averaged per film. Facts and labels become one-hot vectors.
"""

from __future__ import annotations

import json

import numpy as np

from extract import MODELS, exp_dir, hf_load

SRC = exp_dir() / "proxy_text"
OUT = exp_dir() / "proxies"
CHUNK = 200


def rows(name: str) -> list[dict]:
    path = SRC / f"{name}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def save(name: str, ids: list[str], vectors: np.ndarray) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez(OUT / f"{name}.npz", ids=np.array(ids), vectors=vectors.astype(np.float32))
    print(f"{name}: {len(ids)} films, dim {vectors.shape[1]}")


def embedder():  # noqa: ANN201
    import torch
    from transformers import AutoModel, AutoTokenizer

    tok = hf_load(AutoTokenizer.from_pretrained, MODELS["words_text"]["id"])
    model = hf_load(AutoModel.from_pretrained, MODELS["words_text"]["id"]).eval()

    def embed(text: str) -> np.ndarray:
        words = text.split()
        chunks = [" ".join(words[i : i + CHUNK]) for i in range(0, len(words), CHUNK)] or [""]
        out = []
        for i in range(0, len(chunks), 8):
            enc = tok(["query: " + c for c in chunks[i : i + 8]], padding=True, truncation=True,
                      max_length=512, return_tensors="pt")  # fmt: skip
            with torch.no_grad():
                hidden = model(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1).float()
            out.append(((hidden * mask).sum(1) / mask.sum(1)).numpy())
        return np.concatenate(out).mean(0)

    return embed


def one_hot(values: list[list[str]], min_count: int = 2) -> np.ndarray:
    vocab = sorted({v for vs in values for v in vs if sum(v in w for w in values) >= min_count})
    return np.array([[float(v in vs) for v in vocab] for vs in values])


def as_list(x: object) -> list[str]:
    if x is None:
        return []
    return [str(v) for v in x] if isinstance(x, list) else [str(x)]


def main() -> None:
    embed = embedder()
    for src, name in [("wikipedia_full", "wiki_full"), ("wikipedia_plot", "wiki_plot"),
                      ("wikipedia_lead", "wiki_lead"), ("wikipedia_style", "wiki_style")]:  # fmt: skip
        rs = [r for r in rows(src) if r.get("text", "").strip()]
        if rs:
            save(name, [r["id"] for r in rs], np.stack([embed(r["text"]) for r in rs]))

    llm = rows("llm_title_only")
    if llm:
        style = np.stack([embed(r["style"]) for r in llm])
        felt = np.stack([embed(", ".join(r["felt"])) for r in llm])
        ids = [r["id"] for r in llm]
        save("llm_style", ids, style)
        save("llm_felt", ids, felt)
        for level in ("high", "medium", "low"):
            keep = [i for i, r in enumerate(llm) if r["confidence"] == level]
            if len(keep) >= 5:
                save(f"llm_style_{level}", [ids[i] for i in keep], style[keep])

    facts = rows("wikidata_facts")
    if facts:
        ids = [r["id"] for r in facts]
        save("label_genre", ids, one_hot([as_list(r.get("genres")) for r in facts]))
        save("label_director", ids, one_hot([as_list(r.get("director")) for r in facts]))
        save("label_cast", ids, one_hot([as_list(r.get("cast")) for r in facts]))
        decade = [[str(int(str(r.get("year"))[:4]) // 10)] if r.get("year") else [] for r in facts]
        save("label_decade_country", ids, np.hstack([one_hot(decade), one_hot([as_list(r.get("country")) for r in facts])]))
        dur = np.array([float(r.get("duration_min") or np.nan) for r in facts])
        dur = np.nan_to_num((dur - np.nanmean(dur)) / np.nanstd(dur))[:, None]
        save("facts", ids, np.hstack([one_hot([as_list(r.get("colour")) for r in facts], 1), dur,
                                      one_hot([as_list(r.get("original_language")) for r in facts], 1)]))  # fmt: skip


if __name__ == "__main__":
    main()
