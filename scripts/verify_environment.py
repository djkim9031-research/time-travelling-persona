#!/usr/bin/env python3
"""Quick environment audit — tells you which phases of this project are runnable here.

Run on whatever box you're on (Thor, x86 workstation, RunPod):

    python scripts/verify_environment.py

Prints a per-phase verdict (dataset-prep / LoRA-training / ComfyUI inference) so
you don't waste time trying to train on the wrong machine.
"""

from __future__ import annotations

import importlib
import platform
import shutil
import subprocess
import sys
from typing import Optional


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def check_import(modname: str) -> Optional[str]:
    try:
        m = importlib.import_module(modname)
        return getattr(m, "__version__", "(no __version__)")
    except ImportError:
        return None


def nvidia_smi_query() -> Optional[dict]:
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,compute_cap",
             "--format=csv,noheader,nounits"],
            text=True, timeout=5,
        ).strip()
    except Exception as e:
        return {"error": str(e)}
    rows = [r.strip() for r in out.splitlines() if r.strip()]
    if not rows:
        return {"error": "no rows"}
    parts = [p.strip() for p in rows[0].split(",")]
    return {"name": parts[0], "vram_mib": parts[1], "driver": parts[2], "cc": parts[3]}


def main() -> int:
    section("Host")
    print(f"  Python      : {sys.version.split()[0]}")
    print(f"  Platform    : {platform.system()} {platform.release()} ({platform.machine()})")
    is_aarch64 = platform.machine() == "aarch64"
    if is_aarch64:
        print("  [note] aarch64 — ComfyUI custom nodes (PuLID-Flux2, Sonic, InfiniteYou)")
        print("         have brittle ARM packaging. Prefer x86_64 for the heavy stack.")

    section("GPU")
    gpu = nvidia_smi_query()
    if gpu is None:
        print("  nvidia-smi not on PATH — no NVIDIA GPU visible.")
    elif "error" in gpu:
        print(f"  nvidia-smi error: {gpu['error']}")
    else:
        vram = gpu["vram_mib"]
        try:
            vram_gb = int(vram) / 1024 if vram != "[N/A]" else None
            vram_str = f"{vram_gb:.1f} GiB" if vram_gb is not None else "unified / unknown"
        except ValueError:
            vram_str = vram
        print(f"  Device      : {gpu['name']}")
        print(f"  VRAM        : {vram_str}")
        print(f"  Driver      : {gpu['driver']}  | Compute cap: {gpu['cc']}")

    section("Python packages")
    versions = {name: check_import(name) for name in [
        "PIL", "numpy", "torch", "torchvision", "diffusers", "transformers",
        "accelerate", "safetensors", "mediapipe", "cv2",
    ]}
    for name, v in versions.items():
        mark = "✓" if v else "·"
        print(f"  {mark} {name:<14} {v or 'not installed'}")

    section("Phase readiness")
    have_pil = versions["PIL"] is not None
    have_torch = versions["torch"] is not None
    have_diffusers = versions["diffusers"] is not None
    have_mp = versions["mediapipe"] is not None

    has_cuda = False
    cuda_msg = "unknown"
    if have_torch:
        try:
            import torch
            has_cuda = torch.cuda.is_available()
            cuda_msg = f"torch.cuda.is_available() = {has_cuda}"
            if has_cuda:
                cuda_msg += f" (device 0: {torch.cuda.get_device_name(0)})"
        except Exception as e:
            cuda_msg = f"torch import error: {e}"

    def verdict(ok: bool, msg: str) -> str:
        return ("READY" if ok else "NOT READY") + " — " + msg

    print(f"  Dataset prep (resize/crop)       : {verdict(have_pil, 'Pillow present.')}")
    print(f"  Dataset prep (face-aware crop)   : {verdict(have_mp, 'mediapipe present.' if have_mp else 'install with: pip install \".[face]\"')}")
    print(f"  LoRA training (ai-toolkit/Flux.2): {verdict(has_cuda, cuda_msg)}")
    print(f"  Inference (diffusers/ComfyUI)    : {verdict(has_cuda and have_diffusers, cuda_msg + ('; diffusers ' + str(versions['diffusers']) if have_diffusers else '; diffusers missing'))}")

    section("Recommendation")
    if is_aarch64:
        print("  This is the Jetson Thor box. Use it for: photo collection, dataset prep,")
        print("  prompt authoring, doc writing. Do LoRA training + ComfyUI heavy stack on x86.")
    elif has_cuda:
        print("  CUDA GPU detected. This box is a candidate for LoRA training and ComfyUI.")
        print("  See docs/02_setup_x86.md to install the full stack.")
    else:
        print("  No CUDA GPU. Use for dataset prep only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
