"""Check the hand-written CLIP ViT-L/14 visual tower that carries the CSD weights.

    uv run python -m features.checks --images ../../data/painting2vec/sample [--fp16]

CSD's checkpoint uses openai/CLIP parameter names, so embed._ClipVisual re-implements that tower.
This loads OpenAI's own ViT-L/14 weights (openai/clip-vit-large-patch14, safetensors) into it,
renamed, and compares its output with the transformers implementation on a few images. Agreement
means the architecture CSD's weights will be loaded into is right. Needs the clip_l weights.
"""

from __future__ import annotations

import argparse
import gc

import numpy as np

from . import embed
from .preprocess import list_images, load_image, model_views


def openai_names(sd: dict) -> dict:
    """transformers CLIPVisionModelWithProjection state dict -> embed._CSD names."""
    import torch

    v = "vision_model."
    out = {
        "backbone.class_embedding": sd[v + "embeddings.class_embedding"],
        "backbone.conv1.weight": sd[v + "embeddings.patch_embedding.weight"],
        "backbone.positional_embedding": sd[v + "embeddings.position_embedding.weight"],
        "last_layer_style": sd["visual_projection.weight"].T,
        "last_layer_content": sd["visual_projection.weight"].T,
    }
    for a, b in (("pre_layrnorm", "ln_pre"), ("post_layernorm", "ln_post")):
        for w in ("weight", "bias"):
            out[f"backbone.{b}.{w}"] = sd[f"{v}{a}.{w}"]
    n = 1 + max(int(k.split(".")[3]) for k in sd if k.startswith(v + "encoder.layers."))
    for i in range(n):
        s, d = f"{v}encoder.layers.{i}.", f"backbone.transformer.resblocks.{i}."
        for w in ("weight", "bias"):
            out[d + f"attn.in_proj_{w}"] = torch.cat([sd[s + f"self_attn.{p}_proj.{w}"] for p in "qkv"])
            out[d + f"attn.out_proj.{w}"] = sd[s + f"self_attn.out_proj.{w}"]
            out[d + f"ln_1.{w}"] = sd[s + f"layer_norm1.{w}"]
            out[d + f"ln_2.{w}"] = sd[s + f"layer_norm2.{w}"]
            out[d + f"mlp.c_fc.{w}"] = sd[s + f"mlp.fc1.{w}"]
            out[d + f"mlp.c_proj.{w}"] = sd[s + f"mlp.fc2.{w}"]
    return out


def main() -> None:
    import torch
    from safetensors.torch import load_file

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True)
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--fp16", action="store_true")
    ap.add_argument("--device", default="auto")
    a = ap.parse_args()
    spec = embed.MODELS["clip_l"]
    mean, std = spec.mean_std
    views = [model_views(load_image(p), 224, "pad", mean, std, 14) for p in list_images(a.images)[: a.n]]

    em = embed.Embedder("clip_l", a.device, fp16=a.fp16)
    ref = np.stack([em.embed(px, m)["embed"] for px, m in views])
    dev, dtype = em.device, em.dtype
    em.close()
    del em
    gc.collect()

    sd = load_file(embed.fetch_weights(spec) / "model.safetensors")
    sd = {k: t for k, t in sd.items() if k.startswith("vision_model.") or k == "visual_projection.weight"}
    mine = embed._CSD()
    mine.load_state_dict(openai_names(sd), strict=True)
    del sd
    gc.collect()
    mine = mine.eval().to(dev, dtype)
    with torch.inference_mode():
        got = []
        for px, _ in views:
            f, _, _ = mine(torch.from_numpy(px).to(dev, dtype))
            got.append((f @ mine.last_layer_style).float().cpu().numpy().mean(axis=0))
    got = np.stack(got)
    cos = (got * ref).sum(1) / np.linalg.norm(got, axis=1) / np.linalg.norm(ref, axis=1)
    print(f"device {dev}, dtype {dtype}; {len(views)} images")
    print(f"cosine(our tower, transformers CLIP image_embeds): min {cos.min():.6f}  max abs diff {np.abs(got - ref).max():.4f}  (norm {np.linalg.norm(ref, axis=1).mean():.2f})")
    print("OK" if cos.min() > 0.999 else "MISMATCH")


if __name__ == "__main__":
    main()
