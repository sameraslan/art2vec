"""Paths, guards (disk, memory) and the resumable on-disk feature store."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "painting2vec"
MODELS_DIR = Path(os.environ.get("P2V_MODELS_DIR", DATA_DIR / "models"))
DISK_FLOOR_GB = 1.5


def point_caches_at_models_dir() -> None:
    """Send every Hugging Face / torch hub download to data/painting2vec/models (gitignored).

    Forced, not defaulted: nothing this code downloads may land in ~/.cache/huggingface.
    Must run before huggingface_hub or transformers is imported.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(MODELS_DIR / "hf")
    os.environ["HF_HUB_CACHE"] = str(MODELS_DIR / "hf" / "hub")
    os.environ["HF_XET_CACHE"] = str(MODELS_DIR / "hf" / "xet")
    os.environ["TORCH_HOME"] = str(MODELS_DIR / "torch")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def free_disk_gb(path: Path = REPO_ROOT) -> float:
    return shutil.disk_usage(path).free / 1e9


def require_disk(need_mb: float, what: str) -> None:
    free = free_disk_gb()
    if free - need_mb / 1000 < DISK_FLOOR_GB:
        raise SystemExit(
            f"refusing to download {what} ({need_mb:.0f} MB): {free:.2f} GB free, and "
            f"{DISK_FLOOR_GB} GB must stay free afterwards"
        )


def memory_free_pct() -> int | None:
    """System-wide free memory percentage from macOS `memory_pressure`; None if unavailable."""
    try:
        out = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"free percentage:\s*(\d+)%", out)
    return int(m.group(1)) if m else None


def wait_for_memory(min_free_pct: int, max_wait_s: int = 900) -> int | None:
    """Block until system-wide free memory is at least min_free_pct; give up after max_wait_s."""
    t0 = time.time()
    while True:
        pct = memory_free_pct()
        if pct is None or pct >= min_free_pct:
            return pct
        if time.time() - t0 > max_wait_s:
            raise SystemExit(f"free memory {pct}% stayed under {min_free_pct}% for {max_wait_s}s; not loading a model")
        print(f"  free memory {pct}% < {min_free_pct}%; waiting", flush=True)
        time.sleep(30)


def swap_used_mb() -> float | None:
    try:
        out = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"used = ([\d.]+)M", out)
    return float(m.group(1)) if m else None


class Store:
    """<out>/<name>.npz (one array per part, rows aligned), <name>.ids.txt, <name>.json.

    Resumable: reopening a store loads what is there and `done` lists the ids already written.
    Writes are atomic (temp file then rename).
    """

    def __init__(self, out_dir: str | Path, name: str, dtype: str = "float32", flush_every: int = 50):
        self.dir = Path(out_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.name, self.dtype, self.flush_every = name, dtype, flush_every
        self.npz, self.ids_path, self.meta_path = (self.dir / f"{name}{s}" for s in (".npz", ".ids.txt", ".json"))
        self.ids: list[str] = []
        self.parts: dict[str, list[np.ndarray]] = {}
        self.meta: dict = {}
        self._dirty = 0
        if self.npz.exists() and self.ids_path.exists():
            self.ids = [x for x in self.ids_path.read_text().splitlines() if x]
            with np.load(self.npz) as z:
                self.parts = {k: list(z[k]) for k in z.files}
            if any(len(v) != len(self.ids) for v in self.parts.values()):
                raise SystemExit(f"{self.npz} and {self.ids_path} disagree; delete both and rerun")
            if self.meta_path.exists():
                self.meta = json.loads(self.meta_path.read_text())
        self.done = set(self.ids)

    def add(self, id_: str, parts: dict[str, np.ndarray]) -> None:
        if self.parts and set(parts) != set(self.parts):
            raise ValueError(f"{self.name}: parts changed ({sorted(parts)} vs {sorted(self.parts)}); use a new --out")
        for k, v in parts.items():
            self.parts.setdefault(k, []).append(np.asarray(v, self.dtype))
        self.ids.append(id_)
        self.done.add(id_)
        self._dirty += 1
        if self._dirty >= self.flush_every:
            self.flush()

    def flush(self) -> None:
        if not self.ids:
            return
        tmp = self.dir / f".{self.name}.tmp.npz"
        np.savez(tmp, **{k: np.stack(v) for k, v in self.parts.items()})
        os.replace(tmp, self.npz)
        tmp_ids = self.dir / f".{self.name}.ids.tmp"
        tmp_ids.write_text("\n".join(self.ids) + "\n")
        os.replace(tmp_ids, self.ids_path)
        self.meta["n"] = len(self.ids)
        self.meta["parts"] = {k: int(np.asarray(v[0]).size) for k, v in self.parts.items()}
        self.meta["dtype"] = self.dtype
        self.meta_path.write_text(json.dumps(self.meta, indent=1) + "\n")
        self._dirty = 0


def load_features(out_dir: str | Path, name: str, parts: list[str] | None = None) -> tuple[list[str], np.ndarray]:
    """Read a store back: (ids, [N, D] float32) with the chosen parts concatenated in the order given
    (default: every part, in the order recorded in <name>.json)."""
    d = Path(out_dir)
    ids = [x for x in (d / f"{name}.ids.txt").read_text().splitlines() if x]
    with np.load(d / f"{name}.npz") as z:
        keys = parts or list(json.loads((d / f"{name}.json").read_text())["parts"])
        x = np.concatenate([z[k].astype(np.float32).reshape(len(ids), -1) for k in keys], axis=1)
    return ids, x
