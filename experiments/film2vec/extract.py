"""film2vec experiments: extract content features from one film at a time.

Throwaway experiment code, not library code. See PLAN.md.

    extract.py --id QID --url URL|--file PATH [--silent] [--stages cuts,look,time,sound,words,motion]
               [--keep-video] [--force]
    extract.py --catalog catalog.csv [--only id1,id2,...] [--limit N] [--stages ...]

Every stage runs in its own child process, one after the other, so only one model is ever in memory,
a crashed stage cannot take the loop down, and the peak memory recorded for a stage is that stage's own.

Cache home: $ART2VEC_HOME, else ~/Library/Caches/art2vec.
    <home>/artefacts/film/<id>/                    the downloaded video; deleted when the film is done
    <home>/experiments/film2vec/features/<id>/     <stage>.npz, <stage>.json, transcript.json, meta.json
    <home>/experiments/film2vec/extract.log        one line per stage
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import ctypes
import datetime as dt
import gc
import io
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import time
import traceback
import urllib.parse
from fractions import Fraction
from pathlib import Path

# hf-xet stalled for over an hour on the first model download here; plain HTTPS took 30 s.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np  # noqa: E402

FFMPEG = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/usr/local/bin/ffprobe"

ALL_STAGES = ["cuts", "look", "time", "sound", "words", "motion"]
DEFAULT_STAGES = ["cuts", "look", "time", "sound", "words"]
AUDIO_STAGES = {"sound", "words"}

HEAD_MARGIN_S = 60.0  # credits: skipped at the start for look/sound/motion sampling
TAIL_MARGIN_S = 90.0  # and at the end
SHORT_FILM_S = 300.0  # at or below this running time the margins are dropped

CUT_THRESHOLD = 0.5
MAX_SHOT_FRAMES = 1500
GRID_STEP_S = 20.0
LOOK_HEIGHT = 224
PATCH = 14
STATS_WIDTH = 160
COS_OK = 0.999

AUDIO_SR = 16000
WINDOW_S = 10.0
WINDOW_STEP_S = 20.0
CHUNK_WORDS = 200

MODELS = {
    "cuts": {
        "id": "transnetv2-pytorch==1.0.5 (PyPI; weights bundled in the wheel)",
        "licence": "MIT (Tomas Soucek 2020; port github.com/allenday/transnetv2_pytorch)",
        "weights_mb": 30.5,
    },
    "look": {"id": "facebook/dinov2-with-registers-base", "licence": "Apache-2.0", "weights_mb": 346},
    "sound": {
        "id": "worstchan/EAT-base_epoch30_pretrain",
        "revision": "6eb95936bf1061cacee1c0b89404a1aca9a3c62a",
        "licence": "MIT",
        "trained_on": "AudioSet-2M audio, self-supervised (masked latent prediction); no labels, no text",
        "weights_mb": 360,
    },
    "words_asr": {
        "id": "mlx-community/whisper-large-v3-turbo",
        "licence": "MIT (OpenAI Whisper)",
        "weights_mb": 1614,
    },
    "words_text": {"id": "intfloat/multilingual-e5-small", "licence": "MIT", "weights_mb": 471},
    "motion": {"id": "facebook/vjepa2-vitl-fpc64-256", "licence": "MIT", "weights_mb": 1304},
}
NO_SPACE_LANGS = {"ja", "zh", "yue", "th", "lo", "km", "my"}


# ----------------------------------------------------------------------------------------------- paths


def cache_home() -> Path:
    env = os.environ.get("ART2VEC_HOME")
    return Path(env).expanduser() if env else Path.home() / "Library" / "Caches" / "art2vec"


def video_dir(film_id: str) -> Path:
    return cache_home() / "artefacts" / "film" / film_id


def exp_dir() -> Path:
    return cache_home() / "experiments" / "film2vec"


def feat_dir(film_id: str) -> Path:
    return exp_dir() / "features" / film_id


def log_line(*fields: object) -> None:
    exp_dir().mkdir(parents=True, exist_ok=True)
    line = "\t".join([dt.datetime.now().isoformat(timespec="seconds"), *[str(f) for f in fields]])
    with open(exp_dir() / "extract.log", "a") as fh:
        fh.write(line + "\n")
    print(line, flush=True)


def write_json(path: Path, obj: object) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=_json_default))
    os.replace(tmp, path)


def _json_default(o: object) -> object:
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path | Fraction):
        return str(o)
    raise TypeError(type(o))


def save_npz(path: Path, **arrays: np.ndarray) -> None:
    tmp = path.with_name(path.stem + ".tmp.npz")
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)


def f16(a: object) -> np.ndarray:
    return np.asarray(a, dtype=np.float32).astype(np.float16)


def free_disk_gb(path: Path) -> float:
    p = path
    while not p.exists():
        p = p.parent
    return shutil.disk_usage(p).free / 1e9


def hf_load(loader, model_id: str, **kwargs):  # noqa: ANN001
    """from_pretrained from the local cache without touching the network; download only if it is not there."""
    try:
        return loader(model_id, local_files_only=True, **kwargs)
    except Exception:
        return loader(model_id, **kwargs)


# ---------------------------------------------------------------------------------------------- memory


def peak_memory() -> dict:
    """Peak memory of this process. On macOS `footprint` is what Activity Monitor shows and, unlike
    RSS, includes Metal (MPS / MLX) allocations."""
    out = {"peak_rss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 3)}
    try:
        buf = (ctypes.c_uint64 * 64)()  # rusage_info_v4: 16-byte uuid, then uint64 fields
        lib = ctypes.CDLL("/usr/lib/libproc.dylib")
        if lib.proc_pid_rusage(os.getpid(), 4, ctypes.byref(buf)) == 0:
            out["peak_footprint_gb"] = round(buf[2 + 28] / 1e9, 3)  # ri_lifetime_max_phys_footprint
    except Exception:
        pass
    return out


def free_torch() -> None:
    gc.collect()
    try:
        import torch

        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:
        pass


# -------------------------------------------------------------------------------------------- probing


def probe(path: Path) -> dict:
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    info = json.loads(out)
    vs = [s for s in info["streams"] if s.get("codec_type") == "video" and not _attached_pic(s)]
    aus = [s for s in info["streams"] if s.get("codec_type") == "audio"]
    if not vs:
        raise RuntimeError("no video stream")
    v = vs[0]

    def frac(s: str | None) -> Fraction | None:
        try:
            f = Fraction(s)
            return f if f > 0 else None
        except (ValueError, ZeroDivisionError, TypeError):
            return None

    fps = frac(v.get("avg_frame_rate")) or frac(v.get("r_frame_rate"))
    fps_note = ""
    if fps is None or not 5 <= fps <= 61:
        alt = frac(v.get("r_frame_rate"))
        fps_note = f"implausible avg_frame_rate {v.get('avg_frame_rate')}"
        fps = alt if alt is not None and 5 <= alt <= 61 else Fraction(24)
    fps = fps.limit_denominator(1001)
    sar = frac((v.get("sample_aspect_ratio") or "1:1").replace(":", "/")) or Fraction(1)
    duration = float(info["format"].get("duration") or v.get("duration") or 0)
    return {
        "source_file": path.name,
        "file_bytes": path.stat().st_size,
        "duration_s": duration,
        "fps": float(fps),
        "fps_fraction": f"{fps.numerator}/{fps.denominator}",
        "fps_note": fps_note,
        "width": int(v["width"]),
        "height": int(v["height"]),
        "sample_aspect_ratio": float(sar),
        "video_codec": v.get("codec_name"),
        "has_audio": bool(aus),
        "audio_codec": aus[0].get("codec_name") if aus else None,
        "format": info["format"].get("format_name"),
    }


def _attached_pic(stream: dict) -> bool:
    return bool(stream.get("disposition", {}).get("attached_pic"))


def margins(duration: float) -> tuple[float, float]:
    """The window of running time that look, sound and motion sample from."""
    if duration <= SHORT_FILM_S:
        return 0.0, duration
    return HEAD_MARGIN_S, duration - TAIL_MARGIN_S


# ------------------------------------------------------------------------------------------- stage: cuts


def conv2plus1d_forward(self, x):  # noqa: ANN001
    """TransNetV2's separable block as a 2D then a 1D convolution: the same weights and the same sums as
    its two Conv3d layers. PyTorch's dilated Conv3d is wrong on MPS and slow on an ARM CPU; these are neither."""
    import torch.nn.functional as F

    conv1, conv2 = self.layers
    b, c, t, h, w = x.shape
    y = x.permute(0, 2, 1, 3, 4).reshape(b * t, c, h, w)
    y = F.conv2d(y, conv1.weight[:, :, 0], None, padding=1)
    c2 = y.shape[1]
    y = y.reshape(b, t, c2, h, w).permute(0, 3, 4, 2, 1).reshape(b * h * w, c2, t)
    d = conv2.dilation[0]
    y = F.conv1d(y, conv2.weight[:, :, :, 0, 0], conv2.bias, padding=d, dilation=d)
    return y.reshape(b, h, w, y.shape[1], t).permute(0, 3, 4, 1, 2)


def stage_cuts(ctx: dict) -> dict:
    import torch
    from transnetv2_pytorch import TransNetV2
    from transnetv2_pytorch.transnetv2_pytorch import Conv3DConfigurable

    t0 = time.time()
    fps = ctx["probe"]["fps"]
    with contextlib.redirect_stdout(io.StringIO()):
        model = TransNetV2(device="cpu")
    torch.use_deterministic_algorithms(False)  # the port switches this on globally
    conv3d_forward = Conv3DConfigurable.forward
    device = "cpu"
    validation: dict = {"threshold_max_abs_diff": 1e-3}
    h, w = 27, 48
    frame_bytes = h * w * 3
    cmd = [FFMPEG, "-v", "error", "-nostdin", "-i", str(ctx["video"]), "-map", "0:v:0", "-an",
           "-vf", f"fps={ctx['probe']['fps_fraction']},scale={w}:{h}", "-pix_fmt", "rgb24",
           "-f", "rawvideo", "pipe:1"]  # fmt: skip
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    batch_windows = 4
    preds: list[np.ndarray] = []
    pending: list[np.ndarray] = []
    motion: list[np.ndarray] = []
    buf: np.ndarray | None = None
    prev: np.ndarray | None = None
    n = 0

    def predict(x: torch.Tensor, dev: str) -> np.ndarray:
        with torch.no_grad():
            one, _ = model.predict_raw(x.to(dev))
        return one[:, :, 0].float().cpu().numpy()

    def choose_device(x: torch.Tensor) -> str:
        """Unpatched Conv3d on the CPU is the reference; use MPS only if the patched model reproduces it."""
        if not torch.backends.mps.is_available():
            return "cpu"
        ref = predict(x, "cpu")
        try:
            Conv3DConfigurable.forward = conv2plus1d_forward
            model.to("mps")
            diff = float(np.abs(predict(x, "mps") - ref).max())
            validation.update(n_windows=int(len(x)), max_abs_diff=diff)
            if diff < validation["threshold_max_abs_diff"]:
                return "mps"
        except Exception as e:
            validation["error"] = repr(e)[:300]
        Conv3DConfigurable.forward = conv3d_forward
        model.to("cpu")
        return "cpu"

    def flush() -> None:
        nonlocal device
        if not pending:
            return
        x = torch.from_numpy(np.stack(pending))
        if not preds:
            device = choose_device(x[:2])
        preds.append(predict(x, device)[:, 25:75].reshape(-1))
        pending.clear()

    def drain() -> None:
        nonlocal buf
        while len(buf) >= 100:
            pending.append(buf[:100])
            buf = buf[50:]
            if len(pending) == batch_windows:
                flush()

    while True:
        raw = proc.stdout.read(frame_bytes * 2000)
        if not raw:
            break
        chunk = np.frombuffer(raw[: len(raw) // frame_bytes * frame_bytes], np.uint8).reshape(-1, h, w, 3)
        if len(chunk) == 0:
            break
        first = chunk[:1] if prev is None else prev[None]
        seq = np.concatenate([first, chunk]).astype(np.int16)
        motion.append(np.abs(seq[1:] - seq[:-1]).mean(axis=(1, 2, 3), dtype=np.float32))
        prev = chunk[-1].copy()
        buf = np.concatenate([np.repeat(chunk[:1], 25, 0), chunk]) if buf is None else np.concatenate([buf, chunk])
        n += len(chunk)
        drain()
    err = proc.stderr.read().decode(errors="replace")
    proc.wait()
    if n == 0:
        raise RuntimeError(f"ffmpeg decoded no frames: {err[-500:]}")
    pad_end = 25 + 50 - (n % 50 if n % 50 else 50)
    buf = np.concatenate([buf, np.repeat(prev[None], pad_end, 0)])
    drain()
    flush()
    pred = np.concatenate(preds)[:n]
    motion_frame = np.concatenate(motion)
    t_decode_predict = time.time() - t0

    scenes = TransNetV2.predictions_to_scenes(pred, CUT_THRESHOLD)  # [start, end] inclusive
    start, end = scenes[:, 0].astype(np.int64), scenes[:, 1].astype(np.int64)

    cut_mask = pred > CUT_THRESHOLD
    cut_mask[start] = True  # the first frame of a shot differs from the last frame of the one before
    cut_mask[0] = True
    sec = np.floor(np.arange(n) / fps).astype(np.int64)
    n_sec = int(sec[-1]) + 1
    valid = ~cut_mask
    sums = np.bincount(sec[valid], weights=motion_frame[valid], minlength=n_sec)
    counts = np.bincount(sec[valid], minlength=n_sec)
    motion_1hz = np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)

    save_npz(
        ctx["out"] / "cuts.npz",
        fps=np.float64(fps),
        n_frames=np.int64(n),
        shot_start_frame=start,
        shot_end_frame=end,
        shot_start_s=start / fps,
        shot_end_s=(end + 1) / fps,
        cut_prob=f16(pred),
        motion_frame=f16(motion_frame),
        motion_1hz=motion_1hz.astype(np.float32),
        motion_1hz_valid_frames=counts.astype(np.int16),
    )
    model = None  # drop the weights before anything else loads
    free_torch()
    return {
        "model": MODELS["cuts"],
        "device": device,
        "mps_vs_cpu": validation,
        "note": "on MPS the separable Conv3d pairs run as Conv2d + Conv1d with the same weights",
        "threshold": CUT_THRESHOLD,
        "n_frames": n,
        "n_shots": int(len(start)),
        "decoded_duration_s": n / fps,
        "median_shot_s": float(np.median((end + 1 - start) / fps)),
        "ffmpeg_stderr": err[-300:],
        "timings_s": {"decode_and_predict": round(t_decode_predict, 2)},
    }


# ------------------------------------------------------------------------------------------- stage: time


def stage_time(ctx: dict) -> dict:
    cuts = np.load(ctx["out"] / "cuts.npz")
    fps = float(cuts["fps"])
    length_frames = cuts["shot_end_frame"] - cuts["shot_start_frame"] + 1
    save_npz(
        ctx["out"] / "time.npz",
        fps=np.float64(fps),
        shot_len_frames=length_frames.astype(np.int32),
        shot_len_s=(length_frames / fps).astype(np.float32),
        shot_start_s=cuts["shot_start_s"],
        cut_times_s=cuts["shot_start_s"][1:],
        motion_1hz=cuts["motion_1hz"],
    )
    return {"n_shots": int(len(length_frames)), "mean_shot_s": float(length_frames.mean() / fps)}


# ------------------------------------------------------------------------------------------- stage: look


def detect_crop(video: Path, p: dict) -> dict:
    """Black bars: ffmpeg cropdetect on nine two-second samples; the union of the boxes is kept."""
    w0, h0 = p["width"], p["height"]
    boxes = []
    for frac in np.linspace(0.1, 0.9, 9):
        r = subprocess.run(
            [FFMPEG, "-hide_banner", "-nostats", "-nostdin", "-ss", f"{frac * p['duration_s']:.2f}",
             "-i", str(video), "-t", "2", "-map", "0:v:0", "-an",
             "-vf", "cropdetect=limit=24:round=2:reset=0", "-f", "null", "-"],
            capture_output=True, text=True,
        )  # fmt: skip
        found = re.findall(r"crop=(-?\d+):(-?\d+):(-?\d+):(-?\d+)", r.stderr)
        if found:
            cw, ch, cx, cy = map(int, found[-1])
            if cw > 0 and ch > 0:
                boxes.append((cx, cy, cx + cw, cy + ch))
    x1, y1, x2, y2 = 0, 0, w0, h0
    note = "no box detected; full frame"
    if boxes:
        b = np.array(boxes)
        x1, y1, x2, y2 = int(b[:, 0].min()), int(b[:, 1].min()), int(b[:, 2].max()), int(b[:, 3].max())
        note = f"union of {len(boxes)} samples"
        if (x2 - x1) < 0.5 * w0 or (y2 - y1) < 0.5 * h0:
            x1, y1, x2, y2, note = 0, 0, w0, h0, "detected box under half the frame; ignored"
        elif (x2 - x1) >= 0.98 * w0 and (y2 - y1) >= 0.98 * h0:
            x1, y1, x2, y2, note = 0, 0, w0, h0, "bars under 2%; full frame"
    cw, ch = x2 - x1, y2 - y1
    return {
        "crop": [cw, ch, x1, y1],
        "note": note,
        "active_aspect": cw * p["sample_aspect_ratio"] / ch,
        "stored_aspect": w0 * p["sample_aspect_ratio"] / h0,
    }


def select_expr(frames: np.ndarray) -> str:
    """An ffmpeg select expression true for exactly these frame numbers (grouped to keep it shallow)."""
    terms = [f"eq(n,{int(i)})" for i in frames]
    groups = ["(" + "+".join(terms[i : i + 40]) + ")" for i in range(0, len(terms), 40)]
    return "+".join(groups)


def stream_frames(ctx: dict, frames: np.ndarray, tail_filters: str, w: int, h: int, batch: int):
    """Yield uint8 [b, h, w, 3] batches of exactly the frames numbered `frames` (sorted, unique), in order.
    One decoding pass; frame numbers are those of the fps-normalised stream the cuts stage saw."""
    script = ctx["out"] / f".select_{os.getpid()}.txt"
    script.write_text(f"fps={ctx['probe']['fps_fraction']},select='{select_expr(frames)}',{tail_filters}")
    cmd = [FFMPEG, "-v", "error", "-nostdin", "-i", str(ctx["video"]), "-map", "0:v:0", "-an",
           "-/filter:v", str(script), "-fps_mode", "passthrough",
           "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"]  # fmt: skip
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    size = h * w * 3
    try:
        while True:
            raw = proc.stdout.read(size * batch)
            k = len(raw) // size
            if k == 0:
                break
            yield np.frombuffer(raw[: k * size], np.uint8).reshape(k, h, w, 3)
    finally:
        proc.stdout.close()
        proc.wait()
        script.unlink(missing_ok=True)


def colour_stats(batch: np.ndarray) -> dict[str, np.ndarray]:
    """Light and colour statistics per frame, on a copy STATS_WIDTH pixels wide. batch: uint8 [b,h,w,3]."""
    import torch
    import torch.nn.functional as F

    b, h, w, _ = batch.shape
    sh = max(1, round(h * STATS_WIDTH / w))
    x = torch.from_numpy(batch).permute(0, 3, 1, 2).float()
    x = F.interpolate(x, size=(sh, STATS_WIDTH), mode="area").permute(0, 2, 3, 1).numpy()
    rgb = x.reshape(b, -1, 3) / 255.0
    r, g, bl = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * bl
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    sat = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0.0)
    safe = np.maximum(d, 1e-6)
    hue = np.where(mx == r, ((g - bl) / safe) % 6, np.where(mx == g, (bl - r) / safe + 2, (r - g) / safe + 4))
    hue = np.where(d > 0, hue / 6.0, 0.0)
    hbin = np.clip((hue * 12).astype(np.int64), 0, 11) + 12 * np.arange(b)[:, None]

    def hue_hist(weight: np.ndarray) -> np.ndarray:
        hist = np.bincount(hbin.ravel(), weights=weight.ravel(), minlength=12 * b).reshape(b, 12)
        return hist / np.maximum(hist.sum(1, keepdims=True), 1e-9)

    rg = (r - g) * 255.0
    yb = (0.5 * (r + g) - bl) * 255.0
    colourfulness = np.sqrt(rg.std(1) ** 2 + yb.std(1) ** 2) + 0.3 * np.sqrt(rg.mean(1) ** 2 + yb.mean(1) ** 2)
    lbin = np.clip((lum * 8).astype(np.int64), 0, 7) + 8 * np.arange(b)[:, None]
    lum_hist = np.bincount(lbin.ravel(), minlength=8 * b).reshape(b, 8) / lum.shape[1]
    return {
        "lum_mean": lum.mean(1),
        "lum_std": lum.std(1),
        "lum_p10": np.percentile(lum, 10, axis=1),
        "lum_p90": np.percentile(lum, 90, axis=1),
        "sat_mean": sat.mean(1),
        "colourfulness": colourfulness,
        "hue_hist": hue_hist(sat),  # weighted by HSV saturation, as specified
        "hue_hist_chroma": hue_hist(d),  # weighted by max-min, which ignores near-black pixels
        "lum_hist": lum_hist,
    }


def cosine_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a, b = a.astype(np.float64), b.astype(np.float64)
    return (a * b).sum(-1) / (np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1) + 1e-12)


def stage_look(ctx: dict) -> dict:
    import torch
    from transformers import AutoModel

    timings: dict[str, float] = {}
    p = ctx["probe"]
    cuts = np.load(ctx["out"] / "cuts.npz")
    fps, n_frames = float(cuts["fps"]), int(cuts["n_frames"])
    duration = n_frames / fps
    lo, hi = margins(duration)

    t0 = time.time()
    crop = detect_crop(ctx["video"], p)
    timings["cropdetect"] = round(time.time() - t0, 2)
    out_w = int(min(46, max(8, round(LOOK_HEIGHT * crop["active_aspect"] / PATCH))) * PATCH)

    mid = (cuts["shot_start_frame"] + cuts["shot_end_frame"]) // 2
    in_window = np.flatnonzero((mid / fps >= lo) & (mid / fps <= hi))
    n_eligible = len(in_window)
    if n_eligible > MAX_SHOT_FRAMES:
        in_window = in_window[np.round(np.linspace(0, n_eligible - 1, MAX_SHOT_FRAMES)).astype(int)]
    shot_frames = mid[in_window]
    grid_t = np.arange(lo, max(lo, hi) + 1e-6, GRID_STEP_S)
    grid_frames = np.clip(np.round(grid_t * fps).astype(np.int64), 0, n_frames - 1)
    wanted, inverse = np.unique(np.concatenate([shot_frames, grid_frames]), return_inverse=True)
    if len(wanted) == 0:
        raise RuntimeError("no frames to sample")

    t0 = time.time()
    model = hf_load(AutoModel.from_pretrained, MODELS["look"]["id"]).eval()
    n_reg = int(getattr(model.config, "num_register_tokens", 4))
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    timings["load_model"] = round(time.time() - t0, 2)

    def embed(batch: np.ndarray, device: str) -> tuple[np.ndarray, np.ndarray]:
        x = torch.from_numpy(batch).permute(0, 3, 1, 2).float().div(255.0)
        x = ((x - mean) / std).to(device)
        with torch.no_grad():
            hidden = model(pixel_values=x).last_hidden_state
        return hidden[:, 0].float().cpu().numpy(), hidden[:, 1 + n_reg :].mean(1).float().cpu().numpy()

    cw, ch, cx, cy = crop["crop"]
    tail = f"crop={cw}:{ch}:{cx}:{cy},scale={out_w}:{LOOK_HEIGHT}:flags=bicubic,setsar=1"
    device = "cpu"
    validation: dict = {"threshold": COS_OK}
    cls_all, patch_all, stats_all = [], [], []
    t0 = time.time()
    t_embed = t_stats = 0.0
    for i, batch in enumerate(stream_frames(ctx, wanted, tail, out_w, LOOK_HEIGHT, batch=16)):
        batch = np.ascontiguousarray(batch)
        if i == 0 and torch.backends.mps.is_available():
            ref = embed(batch[:8], "cpu")
            try:
                model.to("mps")
                got = embed(batch[:8], "mps")
                cos = [float(cosine_rows(r, g).min()) for r, g in zip(ref, got, strict=True)]
                validation.update(n_frames=int(len(batch[:8])), min_cos_cls=cos[0], min_cos_patch_mean=cos[1])
                device = "mps" if min(cos) > COS_OK else "cpu"
            except Exception as e:  # an operator MPS lacks, for instance
                validation["error"] = repr(e)[:300]
            if device == "cpu":
                model.to("cpu")
                free_torch()
        t1 = time.time()
        c, pm = embed(batch, device)
        t_embed += time.time() - t1
        cls_all.append(c)
        patch_all.append(pm)
        t1 = time.time()
        stats_all.append(colour_stats(batch))
        t_stats += time.time() - t1
    timings["decode_embed_stats_total"] = round(time.time() - t0, 2)
    timings["embed"] = round(t_embed, 2)
    timings["stats"] = round(t_stats, 2)

    cls, patch = np.concatenate(cls_all), np.concatenate(patch_all)
    stats = {k: np.concatenate([s[k] for s in stats_all]) for k in stats_all[0]}
    got_n = len(cls)
    warning = ""
    if got_n != len(wanted):
        # the decoder returned fewer frames than asked for; keep the sets whose frames all arrived
        warning = f"asked for {len(wanted)} frames, got {got_n}"
        if got_n == 0:
            raise RuntimeError(warning)
    inv_shot, inv_grid = inverse[: len(shot_frames)], inverse[len(shot_frames) :]
    keep_shot, keep_grid = inv_shot < got_n, inv_grid < got_n
    arrays: dict[str, np.ndarray] = {}
    for name, inv, keep, frames in (
        ("shot", inv_shot, keep_shot, shot_frames),
        ("grid", inv_grid, keep_grid, grid_frames),
    ):
        idx = inv[keep]
        arrays[f"{name}_frame"] = frames[keep].astype(np.int64)
        arrays[f"{name}_time_s"] = (frames[keep] + 0.5) / fps
        arrays[f"{name}_cls"] = f16(cls[idx])
        arrays[f"{name}_patch_mean"] = f16(patch[idx])
        for k, v in stats.items():
            arrays[f"{name}_{k}"] = v[idx].astype(np.float32)
    arrays["shot_index"] = in_window[keep_shot].astype(np.int64)
    save_npz(ctx["out"] / "look.npz", **arrays)

    model = None  # drop the weights before anything else loads
    free_torch()
    return {
        "model": MODELS["look"],
        "device": device,
        "dtype": "float32",
        "mps_vs_cpu": validation,
        "crop": crop,
        "input_size_hw": [LOOK_HEIGHT, out_w],
        "n_shot_frames": int(keep_shot.sum()),
        "n_shots_in_window": int(n_eligible),
        "shot_cap": MAX_SHOT_FRAMES,
        "n_grid_frames": int(keep_grid.sum()),
        "grid_step_s": GRID_STEP_S,
        "sampling_window_s": [lo, hi],
        "warning": warning,
        "timings_s": timings,
    }


# ------------------------------------------------------------------------------------------ stage: sound


def load_audio_int16(video: Path) -> np.ndarray:
    r = subprocess.run(
        [FFMPEG, "-v", "error", "-nostdin", "-i", str(video), "-map", "0:a:0", "-vn", "-ac", "1",
         "-ar", str(AUDIO_SR), "-f", "s16le", "pipe:1"],
        capture_output=True,
    )  # fmt: skip
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"audio decode failed: {r.stderr.decode(errors='replace')[-400:]}")
    return np.frombuffer(r.stdout, np.int16)


def load_eat(repo: str, revision: str):  # noqa: ANN201
    """EAT's hub code predates transformers 5 and AutoModel.from_pretrained fails on it, so build the class
    from the pinned revision of that code and load the checkpoint strictly."""
    from huggingface_hub import snapshot_download
    from safetensors.torch import load_file
    from transformers import AutoConfig
    from transformers.dynamic_module_utils import get_class_from_dynamic_module

    local = hf_load(snapshot_download, repo, revision=revision)
    config = AutoConfig.from_pretrained(local, trust_remote_code=True)
    cls = get_class_from_dynamic_module("modeling_eat.EATModel", local)
    model = cls(config)
    model.load_state_dict(load_file(os.path.join(local, "model.safetensors")), strict=True)
    return model.eval()


def stage_sound(ctx: dict) -> dict:
    import torch
    import torchaudio
    from scipy.signal import stft

    timings: dict[str, float] = {}
    t0 = time.time()
    audio = load_audio_int16(ctx["video"])
    duration = len(audio) / AUDIO_SR
    timings["decode_audio"] = round(time.time() - t0, 2)
    lo, hi = margins(duration)
    starts = np.arange(lo, hi - WINDOW_S + 1e-6, WINDOW_STEP_S)
    if len(starts) == 0:
        raise RuntimeError("audio too short for one window")
    n_win = int(WINDOW_S * AUDIO_SR)

    t0 = time.time()
    spec = MODELS["sound"]
    model = load_eat(spec["id"], spec["revision"])
    blocks = model.model.blocks
    mid_block = len(blocks) // 2 - 1  # output of the 6th of 12 blocks
    grabbed: dict[str, torch.Tensor] = {}
    hook = blocks[mid_block].register_forward_hook(lambda _m, _i, o: grabbed.__setitem__("mid", o[0]))
    timings["load_model"] = round(time.time() - t0, 2)

    target_len, n_real_tokens = 1024, (int(WINDOW_S * 100) - 2) // 16 * 8  # time patches of real audio x 8 mel patches

    def mel_of(wav: np.ndarray) -> torch.Tensor:
        x = torch.from_numpy(wav.astype(np.float32) / 32768.0)
        x = x - x.mean()
        m = torchaudio.compliance.kaldi.fbank(
            x.unsqueeze(0), htk_compat=True, sample_frequency=AUDIO_SR, use_energy=False,
            window_type="hanning", num_mel_bins=128, dither=0.0, frame_shift=10,
        )  # fmt: skip
        m = torch.nn.functional.pad(m, (0, 0, 0, target_len - m.shape[0]))[:target_len]
        return (m + 4.268) / (4.569 * 2)

    def embed(mels: torch.Tensor, device: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        with torch.no_grad():
            last = model.extract_features(mels.to(device))
        mid = grabbed["mid"]
        sl = slice(1, 1 + n_real_tokens)  # token 0 is the CLS-like extra token; the tail is zero padding
        return (
            last[:, sl].mean(1).float().cpu().numpy(),
            mid[:, sl].mean(1).float().cpu().numpy(),
            last[:, 0].float().cpu().numpy(),
        )

    device = "cpu"
    validation: dict = {"threshold": COS_OK}
    last_all, mid_all, cls_all, rms_db, centroid = [], [], [], [], []
    t0 = time.time()
    bs = 8
    for b0 in range(0, len(starts), bs):
        wavs = []
        for s in starts[b0 : b0 + bs]:
            a = int(round(s * AUDIO_SR))
            wavs.append(audio[a : a + n_win])
        mels = torch.stack([mel_of(w) for w in wavs]).unsqueeze(1)  # [b, 1, 1024, 128]
        if b0 == 0 and torch.backends.mps.is_available():
            ref = embed(mels, "cpu")
            try:
                model.to("mps")
                got = embed(mels, "mps")
                cos = [float(cosine_rows(r, g).min()) for r, g in zip(ref, got, strict=True)]
                validation.update(n_windows=len(wavs), min_cos_last=cos[0], min_cos_mid=cos[1], min_cos_cls=cos[2])
                device = "mps" if min(cos) > COS_OK else "cpu"
            except Exception as e:
                validation["error"] = repr(e)[:300]
            if device == "cpu":
                model.to("cpu")
                free_torch()
        la, mi, cl = embed(mels, device)
        last_all.append(la)
        mid_all.append(mi)
        cls_all.append(cl)
        for w in wavs:
            x = w.astype(np.float32) / 32768.0
            rms_db.append(20 * np.log10(np.sqrt(np.mean(x**2)) + 1e-9))
            f, _, z = stft(x, fs=AUDIO_SR, nperseg=1024, noverlap=512)
            mag = np.abs(z).mean(1)
            centroid.append(float((f * mag).sum() / (mag.sum() + 1e-12)))
    timings["embed_windows"] = round(time.time() - t0, 2)
    hook.remove()

    save_npz(
        ctx["out"] / "sound.npz",
        window_start_s=starts,
        window_len_s=np.float64(WINDOW_S),
        emb_last=f16(np.concatenate(last_all)),
        emb_mid=f16(np.concatenate(mid_all)),
        emb_cls_last=f16(np.concatenate(cls_all)),
        rms_db=np.asarray(rms_db, np.float32),
        spectral_centroid_hz=np.asarray(centroid, np.float32),
    )
    model = None  # drop the weights before anything else loads
    free_torch()
    return {
        "model": spec,
        "device": device,
        "mps_vs_cpu": validation,
        "layers": {"last": f"block {len(blocks)} of {len(blocks)}", "mid": f"block {mid_block + 1} of {len(blocks)}"},
        "pooling": "mean over the patch tokens that cover real audio; emb_cls_last is the extra token",
        "n_windows": int(len(starts)),
        "window_s": WINDOW_S,
        "step_s": WINDOW_STEP_S,
        "audio_duration_s": duration,
        "sampling_window_s": [lo, hi],
        "timings_s": timings,
    }


# ------------------------------------------------------------------------------------------ stage: words


def make_chunks(segments: list[dict], language: str) -> list[dict]:
    def units(text: str) -> int:
        return max(1, len(text) // 2) if language in NO_SPACE_LANGS else len(text.split())

    chunks, cur, count = [], [], 0
    for s in segments:
        text = s["text"].strip()
        if not text:
            continue
        cur.append({**s, "text": text})
        count += units(text)
        if count >= CHUNK_WORDS:
            chunks.append(cur)
            cur, count = [], 0
    if cur:
        if chunks and count < CHUNK_WORDS // 4:
            chunks[-1].extend(cur)  # a short tail joins the chunk before it
        else:
            chunks.append(cur)
    joiner = "" if language in NO_SPACE_LANGS else " "
    return [
        {"start": c[0]["start"], "end": c[-1]["end"], "n_segments": len(c), "text": joiner.join(s["text"] for s in c)}
        for c in chunks
    ]


def stage_words(ctx: dict) -> dict:
    timings: dict[str, float] = {}
    out: Path = ctx["out"]
    transcript_path = out / "transcript.json"
    asr = MODELS["words_asr"]

    if transcript_path.exists():
        transcript = json.loads(transcript_path.read_text())
        timings["asr"] = 0.0
    else:
        import mlx.core as mx
        import mlx_whisper
        from huggingface_hub import snapshot_download
        from mlx_whisper.audio import N_FRAMES, N_SAMPLES, log_mel_spectrogram, pad_or_trim
        from mlx_whisper.decoding import detect_language
        from mlx_whisper.transcribe import ModelHolder

        asr_path = hf_load(snapshot_download, asr["id"])  # a local directory, so transcribe() stays offline
        t0 = time.time()
        audio = load_audio_int16(ctx["video"]).astype(np.float32) / 32768.0
        duration = len(audio) / AUDIO_SR
        timings["decode_audio"] = round(time.time() - t0, 2)

        # Whisper picks the language from the first 30 s, which in a film is usually credits music.
        # Ask at seven points across the film instead and take the language with the most probability.
        t0 = time.time()
        language, lang_probs = None, {}
        try:
            model = ModelHolder.get_model(asr_path, mx.float16)
            totals: dict[str, float] = {}
            for frac in np.linspace(0.15, 0.85, 7):
                a = int(frac * max(0, len(audio) - N_SAMPLES))
                mel = log_mel_spectrogram(audio[a : a + N_SAMPLES], n_mels=model.dims.n_mels)
                mel = pad_or_trim(mel, N_FRAMES, axis=-2).astype(mx.float16)
                _, probs = detect_language(model, mel)
                for k, v in probs.items():
                    totals[k] = totals.get(k, 0.0) + float(v) / 7
            top = sorted(totals.items(), key=lambda kv: -kv[1])[:5]
            language, lang_probs = top[0][0], dict(top)
        except Exception as e:
            lang_probs = {"error": repr(e)[:300]}
        timings["detect_language"] = round(time.time() - t0, 2)

        t0 = time.time()
        # Whole-film transcription let MLX's buffer cache grow to 6-9 GB on the pilot. Cap the cache
        # and transcribe in ten-minute slices, clearing it between slices.
        with contextlib.suppress(Exception):
            mx.set_cache_limit(512 * 1024 * 1024)
        result: dict = {"segments": [], "language": language}
        step = 600 * AUDIO_SR
        for a in range(0, len(audio), step):
            part = mlx_whisper.transcribe(
                audio[a : a + step],
                path_or_hf_repo=asr_path,
                language=language,
                condition_on_previous_text=False,
                verbose=None,
            )
            for s in part["segments"]:
                s["start"], s["end"] = s["start"] + a / AUDIO_SR, s["end"] + a / AUDIO_SR
            result["segments"] += part["segments"]
            result["language"] = result["language"] or part.get("language")
            with contextlib.suppress(Exception):
                mx.clear_cache()
        timings["asr"] = round(time.time() - t0, 2)
        keys = ("start", "end", "text", "no_speech_prob", "avg_logprob", "compression_ratio")
        transcript = {
            "model": asr["id"],
            "language": result.get("language"),
            "language_probs": lang_probs,
            "audio_duration_s": duration,
            "segments": [{k: s.get(k) for k in keys} for s in result["segments"] if s.get("text", "").strip()],
            "n_empty_segments_dropped": sum(not s.get("text", "").strip() for s in result["segments"]),
        }
        write_json(transcript_path, transcript)
        del result, audio
        with contextlib.suppress(Exception):
            ModelHolder.model = None
            ModelHolder.model_path = None
        gc.collect()
        with contextlib.suppress(Exception):
            mx.clear_cache()

    language = transcript.get("language") or "en"
    duration = float(transcript["audio_duration_s"])
    segs = transcript["segments"]
    spoken = [s for s in segs if s["text"].strip() and (s.get("no_speech_prob") or 0.0) < 0.6]

    def share(cap_per_word: float | None) -> float:
        covered, edge = 0.0, 0.0
        for s in sorted(spoken, key=lambda s: s["start"]):
            end = s["end"]
            if cap_per_word is not None:  # Whisper stretches a few words over a long stretch of music
                end = min(end, s["start"] + 1.0 + cap_per_word * len(s["text"].split()))
            a, b = max(s["start"], edge), min(end, duration)
            if b > a:
                covered += b - a
                edge = b
        return covered / duration if duration else 0.0

    speech_share, speech_share_capped = share(None), share(0.6)

    chunks = make_chunks(segs, language)
    write_json(out / "words_chunks.json", {"language": language, "chunk_words": CHUNK_WORDS, "chunks": chunks})

    t0 = time.time()
    n_tokens: list[int] = []
    emb = np.zeros((0, 384), np.float32)
    prefix = "query: "  # E5's prefix for symmetric similarity
    if chunks:
        import torch
        from transformers import AutoModel, AutoTokenizer

        tok = hf_load(AutoTokenizer.from_pretrained, MODELS["words_text"]["id"])
        model = hf_load(AutoModel.from_pretrained, MODELS["words_text"]["id"]).eval()
        embs = []
        for i in range(0, len(chunks), 8):
            texts = [prefix + c["text"] for c in chunks[i : i + 8]]
            n_tokens += [len(t) for t in tok(texts, truncation=False)["input_ids"]]
            enc = tok(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
            with torch.no_grad():
                hidden = model(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1).float()
            embs.append(((hidden * mask).sum(1) / mask.sum(1)).numpy())
        emb = np.concatenate(embs)
        del model
        free_torch()
    timings["embed_text"] = round(time.time() - t0, 2)

    save_npz(
        out / "words.npz",
        chunk_emb=f16(emb),
        chunk_start_s=np.array([c["start"] for c in chunks], np.float32),
        chunk_end_s=np.array([c["end"] for c in chunks], np.float32),
        chunk_n_tokens=np.array(n_tokens, np.int32),
        speech_share=np.float32(speech_share),
        speech_share_capped=np.float32(speech_share_capped),
    )
    return {
        "asr_model": asr,
        "text_model": MODELS["words_text"],
        "text_device": "cpu",
        "text_prefix": prefix,
        "text_pooling": "attention-masked mean of the last layer, not normalised",
        "language": language,
        "language_probs": transcript.get("language_probs"),
        "n_segments": len(segs),
        "n_words": sum(len(s["text"].split()) for s in segs),
        "speech_share": speech_share,
        "speech_share_capped": speech_share_capped,
        "speech_share_note": "union of segments with no_speech_prob < 0.6; capped: a segment counts for at most "
        "1 s + 0.6 s a word",
        "n_empty_segments_dropped": transcript.get("n_empty_segments_dropped"),
        "n_chunks": len(chunks),
        "n_chunks_truncated_at_512_tokens": int(sum(n > 512 for n in n_tokens)),
        "timings_s": timings,
    }


# ----------------------------------------------------------------------------------------- stage: motion


def stage_motion(ctx: dict) -> dict:
    """V-JEPA 2 on a 16-frame clip from the middle of at most 200 shots. Optional, off by default."""
    import torch
    from huggingface_hub import try_to_load_from_cache
    from transformers import AutoModel

    spec = MODELS["motion"]
    cached = try_to_load_from_cache(spec["id"], "model.safetensors")
    if not isinstance(cached, str) and free_disk_gb(Path.home()) < 3.5:
        raise RuntimeError("motion: 1.3 GB of weights not cached and under 3.5 GB of disk free; not downloading")

    timings: dict[str, float] = {}
    cuts = np.load(ctx["out"] / "cuts.npz")
    fps, n_frames = float(cuts["fps"]), int(cuts["n_frames"])
    lo, hi = margins(n_frames / fps)
    n_clip, max_shots, side = 16, 200, 256
    step = max(1, round(fps * 2.5 / n_clip))
    start, end = cuts["shot_start_frame"], cuts["shot_end_frame"]
    mid = (start + end) // 2
    ok = np.flatnonzero((end - start + 1 >= n_clip * step) & (mid / fps >= lo) & (mid / fps <= hi))
    n_eligible = len(ok)
    if n_eligible == 0:
        raise RuntimeError("no shot is long enough for a clip")
    if n_eligible > max_shots:
        ok = ok[np.round(np.linspace(0, n_eligible - 1, max_shots)).astype(int)]
    first = mid[ok] - (n_clip * step) // 2
    frames = (first[:, None] + step * np.arange(n_clip)[None]).reshape(-1)

    t0 = time.time()
    model = hf_load(AutoModel.from_pretrained, spec["id"]).eval()
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model.to(device)
    timings["load_model"] = round(time.time() - t0, 2)
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 1, 3, 1, 1)

    p = ctx["probe"]
    crop = detect_crop(ctx["video"], p)
    cw, ch, cx, cy = crop["crop"]
    tail = f"crop={cw}:{ch}:{cx}:{cy},scale={side}:{side}:flags=bicubic,setsar=1"  # squashed, not cropped
    last_all, mid_all = [], []
    depth_layer = n_layers = None
    t0 = time.time()
    for clip in stream_frames(ctx, frames, tail, side, side, batch=n_clip):
        if len(clip) < n_clip:
            break
        x = torch.from_numpy(np.ascontiguousarray(clip)).permute(0, 3, 1, 2).float().div(255.0).unsqueeze(0)
        x = ((x - mean) / std).to(device)
        with torch.no_grad():
            o = model(pixel_values_videos=x, skip_predictor=True, output_hidden_states=True)
        hs = o.hidden_states
        n_layers = len(hs) - 1
        depth_layer = round(0.65 * n_layers)
        last_all.append(o.last_hidden_state.mean(1).float().cpu().numpy())
        mid_all.append(hs[depth_layer].mean(1).float().cpu().numpy())
        if time.time() - t0 > 600:
            raise RuntimeError(f"motion: over 10 minutes after {len(last_all)} clips; stopped")
        if peak_memory().get("peak_footprint_gb", 0) > 6.0:
            raise RuntimeError(f"motion: memory over 6 GB after {len(last_all)} clips; stopped")
    timings["decode_and_embed"] = round(time.time() - t0, 2)
    k = len(last_all)
    if k == 0:
        raise RuntimeError("no clip decoded")
    save_npz(
        ctx["out"] / "motion.npz",
        shot_index=ok[:k].astype(np.int64),
        clip_start_s=first[:k] / fps,
        clip_len_s=np.float64(n_clip * step / fps),
        emb_last=f16(np.concatenate(last_all)),
        emb_mid=f16(np.concatenate(mid_all)),
    )
    model = None  # drop the weights before anything else loads
    free_torch()
    return {
        "model": spec,
        "device": device,
        "n_clips": k,
        "n_shots_long_enough": int(n_eligible),
        "frames_per_clip": n_clip,
        "frame_step": int(step),
        "input": f"{side}x{side}, active picture squashed to square",
        "mid_layer": f"hidden state {depth_layer} of {n_layers} (about 65% depth)",
        "timings_s": timings,
    }


STAGE_FNS = {
    "cuts": stage_cuts,
    "look": stage_look,
    "time": stage_time,
    "sound": stage_sound,
    "words": stage_words,
    "motion": stage_motion,
}
NEEDS_CUTS = {"look", "time", "motion"}
NEEDS_VIDEO = {"cuts", "look", "sound", "words", "motion"}


# ---------------------------------------------------------------------------------------------- child


def run_stage_child(stage: str, film_id: str, video: str | None) -> int:
    out = feat_dir(film_id)
    ctx = {
        "id": film_id,
        "out": out,
        "video": Path(video) if video else None,
        "probe": json.loads((out / "probe.json").read_text()) if (out / "probe.json").exists() else None,
    }
    if stage in NEEDS_CUTS and not (out / "cuts.npz").exists():
        print("cuts.npz missing; run the cuts stage first", file=sys.stderr)
        return 2
    t0 = time.time()
    try:
        info = STAGE_FNS[stage](ctx)
    except Exception:
        traceback.print_exc()
        return 1
    info["wall_s"] = round(time.time() - t0, 2)
    info.update(peak_memory())
    info["finished"] = dt.datetime.now().isoformat(timespec="seconds")
    write_json(out / f"{stage}.json", info)  # written last: its presence marks the stage as done
    return 0


# --------------------------------------------------------------------------------------------- parent


def stage_done(film_id: str, stage: str) -> bool:
    return (feat_dir(film_id) / f"{stage}.json").exists()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    for other in dest.parent.iterdir():  # never more than one video on disk for a film
        if other.name != dest.name + ".part":
            other.unlink()
    head = subprocess.run(["curl", "-sIL", "--max-time", "60", url], capture_output=True, text=True).stdout
    sizes = re.findall(r"(?im)^content-length:\s*(\d+)", head)
    size_gb = int(sizes[-1]) / 1e9 if sizes else 0.0
    free = free_disk_gb(dest.parent)
    if free - size_gb < 1.0:
        raise RuntimeError(f"not enough disk: file {size_gb:.2f} GB, free {free:.2f} GB (1 GB must remain)")
    part = dest.with_name(dest.name + ".part")
    for attempt in range(4):  # curl retries transient errors itself; a dropped transfer is resumed here
        r = subprocess.run(
            ["curl", "-L", "--fail", "-sS", "-C", "-", "--retry", "5", "--retry-delay", "15",
             "--connect-timeout", "30", "-o", str(part), url],
            capture_output=True, text=True,
        )  # fmt: skip
        if r.returncode == 0:
            break
        if r.returncode == 22 or attempt == 3:  # 22: an HTTP error such as 404; trying again will not help
            raise RuntimeError(f"curl exit {r.returncode}: {r.stderr.strip()[-300:]}")
        time.sleep(20)
    os.replace(part, dest)


def process_film(
    film_id: str,
    *,
    url: str | None,
    file: str | None,
    silent: bool,
    stages: list[str],
    keep_video: bool,
    force: bool,
    extra_meta: dict | None = None,
) -> bool:
    out = feat_dir(film_id)
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    meta.update({"id": film_id, "silent": silent, **(extra_meta or {})})
    meta.setdefault("errors", {})
    meta["credit_margins_s"] = {"head": HEAD_MARGIN_S, "tail": TAIL_MARGIN_S, "dropped_at_or_below_s": SHORT_FILM_S}
    meta["cache_home"] = str(cache_home())

    todo = []
    for s in stages:
        if silent and s in AUDIO_STAGES:
            meta.setdefault("skipped", {})[s] = "silent film"
        elif force or not stage_done(film_id, s):
            todo.append(s)
    if not todo:
        log_line(film_id, "-", "skip", "all requested stages already done")
        write_json(meta_path, meta)
        return True

    downloaded: Path | None = None
    video: Path | None = None
    ok = True
    try:
        if any(s in NEEDS_VIDEO for s in todo):
            t0 = time.time()
            if file:
                video = Path(file).expanduser().resolve()
                if not video.exists():
                    raise FileNotFoundError(video)
                meta["source"] = {"file": str(video)}
            else:
                name = urllib.parse.unquote(url.rsplit("/", 1)[-1]) or "video"
                video = video_dir(film_id) / name
                download(url, video)
                downloaded = video
                meta["source"] = {"url": url, "download_s": round(time.time() - t0, 1)}
                log_line(film_id, "download", "ok", f"{time.time() - t0:.1f}s", f"{video.stat().st_size / 1e6:.0f}MB")
            pr = probe(video)
            write_json(out / "probe.json", pr)
            meta["probe"] = pr
            if not pr["has_audio"] and not silent:
                meta["errors"]["audio"] = "catalog says sound but the file has no audio stream"
        write_json(meta_path, meta)

        for s in todo:
            if s in AUDIO_STAGES and meta.get("probe") and not meta["probe"]["has_audio"]:
                log_line(film_id, s, "FAIL", "no audio stream")
                meta["errors"][s] = "no audio stream"
                ok = False
                continue
            (out / f"{s}.json").unlink(missing_ok=True)
            cmd = [sys.executable, str(Path(__file__).resolve()), "--run-stage", s, "--id", film_id]
            if video:
                cmd += ["--file", str(video)]
            t0 = time.time()
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=4 * 3600)
                code, err = r.returncode, r.stderr
            except subprocess.TimeoutExpired:
                code, err = -9, "timed out after 4 h"
            wall = time.time() - t0
            if code == 0 and stage_done(film_id, s):
                info = json.loads((out / f"{s}.json").read_text())
                meta.setdefault("stages", {})[s] = info
                meta["errors"].pop(s, None)
                mem = info.get("peak_footprint_gb", info.get("peak_rss_gb"))
                log_line(film_id, s, "ok", f"{wall:.1f}s", f"peak {mem}GB")
            else:
                ok = False
                meta["errors"][s] = err.strip()[-1500:]
                last = err.strip().splitlines()[-1] if err.strip() else ""
                log_line(film_id, s, "FAIL", f"{wall:.1f}s", f"exit {code}: {last}"[:300])
            write_json(meta_path, meta)
    except Exception as e:
        ok = False
        meta["errors"]["film"] = repr(e)[:1500]
        log_line(film_id, "film", "FAIL", repr(e)[:300])
    finally:
        if downloaded is not None and not keep_video:
            shutil.rmtree(video_dir(film_id), ignore_errors=True)  # only ever a video this script downloaded
        elif not keep_video and video_dir(film_id).exists() and not file:
            shutil.rmtree(video_dir(film_id), ignore_errors=True)  # a partial download
        meta["peak_footprint_gb"] = max(
            [v.get("peak_footprint_gb", v.get("peak_rss_gb", 0)) for v in meta.get("stages", {}).values()] or [0]
        )
        meta["updated"] = dt.datetime.now().isoformat(timespec="seconds")
        write_json(meta_path, meta)
    return ok


def run_catalog(args: argparse.Namespace, stages: list[str]) -> int:
    with open(args.catalog, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if args.only:
        only = [x.strip() for x in args.only.split(",") if x.strip()]
        by_id = {r["id"].strip(): r for r in rows}
        missing = [i for i in only if i not in by_id]
        if missing:
            log_line("-", "catalog", "WARN", f"ids not in catalog: {','.join(missing)}")
        rows = [by_id[i] for i in only if i in by_id]
    if args.limit:
        rows = rows[: args.limit]
    log_line("-", "catalog", "start", f"{len(rows)} films", f"stages {','.join(stages)}")
    n_ok = 0
    for row in rows:
        film_id = (row.get("id") or "").strip()
        try:
            ident, ia_file = (row.get("ia_identifier") or "").strip(), (row.get("ia_file") or "").strip()
            if not film_id or not ident or not ia_file:
                raise ValueError("row lacks id, ia_identifier or ia_file")
            kind = (row.get("silent_or_sound") or "").strip().lower()
            url = f"https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(ia_file)}"
            extra = {"title": row.get("title"), "year": row.get("year"), "silent_or_sound": kind,
                     "ia_identifier": ident, "ia_file": ia_file}  # fmt: skip
            n_ok += process_film(film_id, url=url, file=None, silent=(kind == "silent"), stages=stages,
                                 keep_video=args.keep_video, force=args.force, extra_meta=extra)  # fmt: skip
        except Exception as e:  # one bad film must not stop the run
            log_line(film_id or "?", "film", "FAIL", repr(e)[:300])
    log_line("-", "catalog", "end", f"{n_ok}/{len(rows)} films without errors")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", help="film id (Wikidata QID)")
    ap.add_argument("--url")
    ap.add_argument("--file", help="a local video; never deleted")
    ap.add_argument("--silent", action="store_true", help="skip sound and words")
    ap.add_argument("--stages", default=",".join(DEFAULT_STAGES), help=f"comma list from {','.join(ALL_STAGES)}")
    ap.add_argument("--keep-video", action="store_true")
    ap.add_argument("--force", action="store_true", help="redo stages whose output exists")
    ap.add_argument("--catalog")
    ap.add_argument("--only", help="comma list of ids, with --catalog")
    ap.add_argument("--limit", type=int, help="first N films, with --catalog")
    ap.add_argument("--run-stage", choices=ALL_STAGES, help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.run_stage:
        return run_stage_child(args.run_stage, args.id, args.file)

    stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    bad = [s for s in stages if s not in ALL_STAGES]
    if bad:
        ap.error(f"unknown stages: {bad}")
    stages = [s for s in ALL_STAGES if s in stages]  # dependency order

    if args.catalog:
        return run_catalog(args, stages)
    if not args.id or not (args.url or args.file):
        ap.error("give --catalog, or --id with --url or --file")
    ok = process_film(args.id, url=args.url, file=args.file, silent=args.silent, stages=stages,
                      keep_video=args.keep_video, force=args.force)  # fmt: skip
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
