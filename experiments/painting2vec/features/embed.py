"""Learned embeddings: DINOv2 (with registers), SigLIP 2, CLIP ViT-L/14, CSD ViT-L.

Weights come only from the original authors' Hugging Face repos, into data/painting2vec/models.
One model in memory at a time; `Embedder.close()` frees it and `remove_weights()` deletes the files.
"""

from __future__ import annotations

import gc
import resource
import shutil
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .store import MODELS_DIR, point_caches_at_models_dir, require_disk

point_caches_at_models_dir()

import torch  # noqa: E402
from torch import nn  # noqa: E402

IMAGENET = ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
HALF = ((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
CLIP = ((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
GRAM_K = 24  # tokens are projected to this many dimensions before the second-order statistic


@dataclass(frozen=True)
class Spec:
    kind: str
    repo: str
    files: tuple[str, ...]
    download_mb: float
    licence: str
    size: int
    patch: int
    mean_std: tuple
    views: tuple[str, ...]
    default_view: str


MODELS: dict[str, Spec] = {
    "dinov2_b": Spec("dinov2", "facebook/dinov2-with-registers-base", ("config.json", "model.safetensors"),
                     346, "Apache-2.0", 224, 14, IMAGENET, ("center", "squash", "pad", "tile", "native"), "pad"),
    "dinov2_l": Spec("dinov2", "facebook/dinov2-with-registers-large", ("config.json", "model.safetensors"),
                     1218, "Apache-2.0", 224, 14, IMAGENET, ("center", "squash", "pad", "tile", "native"), "pad"),
    "siglip2_b": Spec("siglip", "google/siglip2-base-patch16-224", ("config.json", "model.safetensors"),
                      1501, "Apache-2.0", 224, 16, HALF, ("center", "squash", "pad", "tile"), "squash"),
    "clip_l": Spec("clip", "openai/clip-vit-large-patch14", ("config.json", "model.safetensors"),
                   1711, "MIT", 224, 14, CLIP, ("center", "squash", "pad", "tile"), "pad"),
    "csd_l": Spec("csd", "tomg-group-umd/CSD-ViT-L", ("config.json", "pytorch_model.bin"),
                  2438, "CC-BY-4.0 (weights); MIT (code)", 224, 14, CLIP, ("center", "squash", "pad", "tile"), "pad"),
}


def pick_device(want: str = "auto") -> str:
    if want != "auto":
        return want
    return "mps" if torch.backends.mps.is_available() else "cpu"


def repo_dir(spec: Spec) -> Path:
    return MODELS_DIR / "hf" / "hub" / ("models--" + spec.repo.replace("/", "--"))


def fetch_weights(spec: Spec) -> Path:
    """Download just the files in spec.files (never the Flax/TF/duplicate copies). Returns the
    snapshot directory. Refuses if the download would leave under 1.5 GB of free disk."""
    from huggingface_hub import snapshot_download

    try:
        return Path(snapshot_download(spec.repo, allow_patterns=list(spec.files),
                                      cache_dir=MODELS_DIR / "hf" / "hub", local_files_only=True))
    except Exception:  # noqa: BLE001 - not cached yet
        pass
    require_disk(spec.download_mb, spec.repo)
    p = Path(snapshot_download(spec.repo, allow_patterns=list(spec.files), cache_dir=MODELS_DIR / "hf" / "hub"))
    missing = [f for f in spec.files if not (p / f).exists()]
    if missing:
        raise SystemExit(f"{spec.repo}: expected files missing after download: {missing}")
    return p


def remove_weights(spec: Spec) -> None:
    """Delete this model's files, and only under data/painting2vec/models.

    huggingface_hub keeps the bytes in a blob store and puts symlinks in the snapshot directory
    (since 1.x the store can sit beside the repo directories, in hub/blobs), so the link targets
    are deleted first, then the repo directory.
    """
    root = MODELS_DIR.resolve()
    d = repo_dir(spec)
    if root not in d.resolve().parents:
        raise SystemExit(f"refusing to delete {d}: not under {root}")
    if d.exists():
        for f in d.rglob("*"):
            if f.is_symlink():
                target = f.resolve()
                if root in target.parents and target.is_file():
                    target.unlink()
    shutil.rmtree(d, ignore_errors=True)
    for extra in ("xet", "hub/.locks"):
        shutil.rmtree(root / "hf" / extra, ignore_errors=True)
    blobs = root / "hf" / "hub" / "blobs"
    if blobs.is_dir() and not any((root / "hf" / "hub").glob("models--*")):
        shutil.rmtree(blobs, ignore_errors=True)  # no model left: whatever remains is orphaned


# ---------------------------------------------------------------- patch statistics

_PROJ: dict[int, np.ndarray] = {}


def _projection(c: int) -> np.ndarray:
    """Fixed Gaussian projection C -> GRAM_K (legacy RandomState: the stream is frozen by NumPy)."""
    if c not in _PROJ:
        _PROJ[c] = (np.random.RandomState(1000 + c).randn(c, GRAM_K) / np.sqrt(GRAM_K)).astype(np.float32)
    return _PROJ[c]


_IU = np.triu_indices(GRAM_K)
_IU_SCALE = np.where(_IU[0] == _IU[1], 1.0, np.sqrt(2.0)).astype(np.float32)


def patch_stats(tokens: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """tokens [P, C] (all real patches of all views) -> (mean and sd per channel [2C], gram [300]).

    gram: tokens centred, projected to 24 dimensions with a fixed random matrix, then the 24x24
    covariance; upper triangle with off-diagonals times sqrt 2, so Euclidean distance between two
    of these equals the Frobenius distance between the projected covariance matrices.
    """
    mu = tokens.mean(axis=0)
    z = (tokens - mu) @ _projection(tokens.shape[1])
    cov = (z.T @ z) / max(1, len(z))
    return np.concatenate([mu, tokens.std(axis=0)]).astype(np.float32), (cov[_IU] * _IU_SCALE).astype(np.float32)


# ---------------------------------------------------------------- CSD (OpenAI CLIP visual tower)


class _QuickGELU(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.sigmoid(1.702 * x)


class _Block(nn.Module):
    def __init__(self, d: int, heads: int):
        super().__init__()
        self.attn = nn.MultiheadAttention(d, heads, batch_first=True)
        self.ln_1 = nn.LayerNorm(d)
        self.mlp = nn.Sequential(OrderedDict(c_fc=nn.Linear(d, 4 * d), gelu=_QuickGELU(), c_proj=nn.Linear(4 * d, d)))
        self.ln_2 = nn.LayerNorm(d)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.ln_1(x)
        x = x + self.attn(y, y, y, need_weights=False)[0]
        return x + self.mlp(self.ln_2(x))


class _Transformer(nn.Module):
    def __init__(self, d: int, layers: int, heads: int):
        super().__init__()
        self.resblocks = nn.Sequential(*[_Block(d, heads) for _ in range(layers)])


class _ClipVisual(nn.Module):
    """Same parameter names as openai/CLIP's VisionTransformer, so the CSD state dict loads strictly."""

    def __init__(self, size: int = 224, patch: int = 14, d: int = 1024, layers: int = 24, heads: int = 16):
        super().__init__()
        self.conv1 = nn.Conv2d(3, d, patch, patch, bias=False)
        self.class_embedding = nn.Parameter(torch.zeros(d))
        self.positional_embedding = nn.Parameter(torch.zeros((size // patch) ** 2 + 1, d))
        self.ln_pre = nn.LayerNorm(d)
        self.transformer = _Transformer(d, layers, heads)
        self.ln_post = nn.LayerNorm(d)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x).flatten(2).transpose(1, 2)
        cls = self.class_embedding.expand(x.shape[0], 1, -1)
        x = torch.cat([cls, x], dim=1) + self.positional_embedding
        x = self.transformer.resblocks(self.ln_pre(x))
        return self.ln_post(x[:, 0])


class _CSD(nn.Module):
    """CSD_CLIP from github.com/learn2phoenix/CSD (model.py), inference path only."""

    def __init__(self) -> None:
        super().__init__()
        self.backbone = _ClipVisual()
        self.last_layer_style = nn.Parameter(torch.zeros(1024, 768))
        self.last_layer_content = nn.Parameter(torch.zeros(1024, 768))

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        f = self.backbone(x)
        style = nn.functional.normalize(f @ self.last_layer_style, dim=1)
        content = nn.functional.normalize(f @ self.last_layer_content, dim=1)
        return f, content, style


class _InertPickled:
    """Stand-in for a non-tensor object in the CSD pickle: accepts anything, keeps nothing."""

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __setstate__(self, state) -> None:
        pass


def _inert_pickled_call(*args, **kwargs) -> None:
    return None


CSD_PICKLE_GLOBALS = ("argparse.Namespace", "numpy.core.multiarray.scalar", "numpy.dtype", "_codecs.encode")


def _load_csd(snapshot: Path, allow_listed_globals: bool = False) -> nn.Module:
    """The CSD repo ships only a pickle: a training checkpoint {"model_state_dict", "args", ...}.

    It is read with torch.load(weights_only=True), memory-mapped. That refuses the file as
    published, because besides tensors it holds an argparse.Namespace and NumPy scalars (found by
    listing the pickle's opcodes without running them). By default we stop there. With
    allow_listed_globals=True the load is still weights_only=True, with exactly the four names in
    CSD_PICKLE_GLOBALS added to torch's allow-list; anything else in the file still aborts the load.
    The file is never unpickled with weights_only=False.
    """
    path = snapshot / "pytorch_model.bin"
    try:
        ckpt = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
    except Exception as e:  # noqa: BLE001
        if not allow_listed_globals:
            raise SystemExit(
                "CSD checkpoint did not load with weights_only=True, so it was not unpickled.\n"
                f"  torch said: {str(e).splitlines()[0][:300]}\n"
                "  It needs these non-tensor globals: " + ", ".join(CSD_PICKLE_GLOBALS) + ".\n"
                "  To allow exactly those (still weights_only=True), rerun with --csd-allow-listed-globals."
            ) from e
        import argparse

        # Exactly the four names in CSD_PICKLE_GLOBALS, and nothing else. argparse.Namespace is the
        # real class (a plain attribute bag). The other three are resolved to do-nothing stand-ins
        # under the pickle's own names, for two reasons: NumPy 2 moved numpy.core to numpy._core,
        # and torch would otherwise also need each concrete dtype class (numpy.dtypes.Float64DType
        # ...) allow-listed before it will restore a dtype's state, which would widen the list.
        # Only the tensors are wanted; the NumPy scalars in the training record are dropped.
        allow = [argparse.Namespace, (_InertPickled, "numpy.dtype"),
                 (_inert_pickled_call, "numpy.core.multiarray.scalar"), (_inert_pickled_call, "_codecs.encode")]
        names = ["argparse.Namespace", *(n for _, n in allow[1:])]
        if len(allow) != 4 or sorted(names) != sorted(CSD_PICKLE_GLOBALS):
            raise SystemExit("CSD allow-list does not match CSD_PICKLE_GLOBALS; not loading")
        try:
            with torch.serialization.safe_globals(allow):
                ckpt = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
        except Exception as e2:  # noqa: BLE001
            raise SystemExit(f"CSD checkpoint still refused under the allow-list; not unpickling it. ({e2})") from e2
    if isinstance(ckpt, dict):
        print(f"csd checkpoint top-level keys: {sorted(map(str, ckpt))[:12]}", flush=True)
    for key in ("model_state_dict", "state_dict", "model"):
        if isinstance(ckpt, dict) and key in ckpt and isinstance(ckpt[key], dict):
            ckpt = ckpt[key]
    sd = {k.removeprefix("module.").removeprefix("model."): v for k, v in ckpt.items()}
    model = _CSD()
    wanted = set(model.state_dict())
    extra = sorted(set(sd) - wanted)
    missing = sorted(wanted - set(sd))
    if missing:
        raise SystemExit(f"CSD checkpoint lacks {len(missing)} expected tensors, e.g. {missing[:5]}; extra: {extra[:5]}")
    model.load_state_dict({k: sd[k].float() for k in wanted}, strict=True)
    model.ignored_keys = extra  # type: ignore[attr-defined]
    print(f"csd: loaded {len(wanted)} tensors strictly; {len(extra)} checkpoint tensors not used, e.g. {extra[:4]}", flush=True)
    del ckpt, sd
    return model


# ---------------------------------------------------------------- the embedder


class Embedder:
    """Loads one model. embed(pixels, mask) -> dict of named float32 vectors for one painting."""

    def __init__(self, name: str, device: str = "auto", fp16: bool = False, csd_allow_listed_globals: bool = False):
        self.name, self.spec = name, MODELS[name]
        self.device = pick_device(device)
        snap = fetch_weights(self.spec)
        kind = self.spec.kind
        self.dtype = torch.float16 if (fp16 and self.device != "cpu") else torch.float32
        kw = {"dtype": self.dtype, "low_cpu_mem_usage": True}  # never hold a float32 copy we do not need
        if kind == "dinov2":
            from transformers import AutoModel

            self.model = AutoModel.from_pretrained(snap, use_safetensors=True, **kw)
            self.registers = int(getattr(self.model.config, "num_register_tokens", 0))
            n = self.model.config.num_hidden_layers
            self.layers = {"early": n // 4, "mid": n // 2, "late": n}
        elif kind == "siglip":
            from transformers import SiglipVisionModel

            self.model = SiglipVisionModel.from_pretrained(snap, use_safetensors=True, **kw)
        elif kind == "clip":
            from transformers import CLIPVisionModelWithProjection

            self.model = CLIPVisionModelWithProjection.from_pretrained(snap, use_safetensors=True, **kw)
        elif kind == "csd":
            self.model = _load_csd(snap, csd_allow_listed_globals)
        else:
            raise ValueError(kind)
        self.model = self.model.eval().to(self.device, self.dtype)

    @torch.inference_mode()
    def embed(self, pixels: np.ndarray, mask: np.ndarray) -> dict[str, np.ndarray]:
        x = torch.from_numpy(pixels).to(self.device, self.dtype)
        kind = self.spec.kind
        out: dict[str, np.ndarray] = {}
        if kind == "dinov2":
            r = self.model(pixel_values=x, output_hidden_states=True)
            skip = 1 + self.registers
            m = mask.reshape(len(mask), -1)
            last = r.last_hidden_state.float().cpu().numpy()
            out["cls"] = last[:, 0].mean(axis=0)
            out["patch_mean"] = last[:, skip:][m].mean(axis=0)
            for tag, i in self.layers.items():
                tok = r.hidden_states[i][:, skip:].float().cpu().numpy()[m]
                out[f"meanstd_{tag}"], out[f"gram_{tag}"] = patch_stats(tok)
        elif kind == "siglip":
            r = self.model(pixel_values=x)
            out["embed"] = r.pooler_output.float().cpu().numpy().mean(axis=0)
            out["patch_mean"] = r.last_hidden_state.float().cpu().numpy()[mask.reshape(len(mask), -1)].mean(axis=0)
        elif kind == "clip":
            r = self.model(pixel_values=x)
            out["embed"] = r.image_embeds.float().cpu().numpy().mean(axis=0)
            # The tower output before the 1024 -> 768 projection: the same quantity as CSD's
            # `backbone`, so the two can be compared directly (CSD is a fine-tune of this tower).
            pooled = self.model.vision_model.post_layernorm(r.last_hidden_state[:, 0])
            if not getattr(self, "_clip_checked", False):
                again = self.model.visual_projection(pooled).float()
                cos = nn.functional.cosine_similarity(again, r.image_embeds.float(), dim=1).min().item()
                if cos < 0.999:
                    raise SystemExit(f"clip: projecting the pooled output does not reproduce image_embeds (cos {cos:.4f})")
                self._clip_checked = True
            out["backbone"] = pooled.float().cpu().numpy().mean(axis=0)
        elif kind == "csd":
            f, content, style = self.model(x)
            out["style"] = style.float().cpu().numpy().mean(axis=0)
            out["content"] = content.float().cpu().numpy().mean(axis=0)
            out["backbone"] = f.float().cpu().numpy().mean(axis=0)
        return {k: np.asarray(v, np.float32) for k, v in out.items()}

    def memory_mb(self) -> dict[str, float]:
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6  # bytes on macOS
        mps = torch.mps.driver_allocated_memory() / 1e6 if self.device == "mps" else 0.0
        return {"peak_rss_mb": round(rss, 1), "mps_driver_mb": round(mps, 1)}

    def close(self) -> None:
        self.model = None
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
