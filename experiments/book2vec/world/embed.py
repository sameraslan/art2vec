"""Embed sampled ~1,000-word chunks of every book with a sentence-transformers model.

    caffeinate -i .venv/bin/python -m world.embed --variant maskB --per-book 40 --name qwen_maskB
        [--instruction world] [--only KEY ...] [--batch 8] [--max-tokens 512] [--device mps]

Writes data/emb/<name>/<key>.npy (one unit-length row per sampled chunk) and <key>.idx.npy
(the chunk idx of each row); books already done are skipped, so the run can be resumed. One
process, one model, one book at a time. ``--per-book 0`` embeds every chunk.
"""

from __future__ import annotations

import argparse
import gc
import subprocess
import time

import numpy as np

from world.common import EMB, book_keys, even_sample, load_chunks

MODEL = "Qwen/Qwen3-Embedding-0.6B"
INSTRUCTIONS = {
    "world": "Represent the setting, period and subject matter of this passage of fiction",
    "plot": "Represent the plot of this story: what happens and how it ends",
    "felt": "Represent the mood and atmosphere this passage creates in its reader",
}


def prompt_for(instruction: str | None) -> str | None:
    """Qwen3-Embedding's instruction format; None embeds the bare text."""
    if not instruction:
        return None
    return f"Instruct: {INSTRUCTIONS.get(instruction, instruction)}\nQuery:"


def free_memory_pct() -> int:
    out = subprocess.run(["memory_pressure"], capture_output=True, text=True).stdout
    return int(out.strip().splitlines()[-1].split(":")[1].strip().rstrip("%"))


def load_model(model_id: str = MODEL, device: str = "mps", max_tokens: int = 512):
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_id, device=device)
    model.max_seq_length = max_tokens
    return model


def unload(model) -> None:
    import torch

    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def encode(model, texts: list[str], prompt: str | None, batch: int) -> np.ndarray:
    kw = {"prompt": prompt} if prompt else {}
    return model.encode(
        texts, batch_size=batch, normalize_embeddings=True, show_progress_bar=False, **kw
    ).astype(np.float32)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variant", default="maskB")
    ap.add_argument("--per-book", type=int, default=40)
    ap.add_argument("--name", required=True)
    ap.add_argument("--instruction", default=None)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--limit", type=int, default=0, help="timing: stop after this many chunks")
    args = ap.parse_args()

    out = EMB / args.name
    out.mkdir(parents=True, exist_ok=True)
    model = load_model(MODEL, args.device, args.max_tokens)
    prompt = prompt_for(args.instruction)
    done = 0
    t0 = time.time()
    batch = args.batch
    for key in args.only or book_keys():
        path = out / f"{key}.npy"
        if path.exists():
            continue
        chunks = load_chunks(args.variant, key)
        idx = even_sample(len(chunks), args.per_book or len(chunks))
        if args.limit:
            idx = idx[: args.limit - done]
        while free_memory_pct() < 20:
            print("memory pressure: pausing 30 s, halving the batch", flush=True)
            batch = max(1, batch // 2)
            time.sleep(30)
        E = encode(model, [chunks[i]["text"] for i in idx], prompt, batch)
        done += len(idx)
        if args.limit:
            print(f"{done} chunks in {time.time() - t0:.1f} s", flush=True)
            if done >= args.limit:
                break
            continue
        np.save(out / f"{key}.idx.npy", idx)
        np.save(path, E)
        print(f"{key} {len(idx)} chunks, total {done}, {time.time() - t0:.0f} s", flush=True)
    unload(model)


if __name__ == "__main__":
    main()
