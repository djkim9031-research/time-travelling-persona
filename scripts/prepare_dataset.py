#!/usr/bin/env python3
"""Prepare a folder of raw photos for personal-LoRA training (ai-toolkit / Flux.2).

Outputs square N x N images plus a same-named .txt caption stub for each, in the
target directory (default `data/training_dataset/`). ai-toolkit picks these up
when `caption_ext: "txt"` is set in the training config.

Required: Pillow.
Optional: mediapipe (face-aware cropping). Transformers + a VLM (auto-captioning)
— see --help for the optional flags.

Examples:
    # Basic resize + center-crop, empty caption stubs you fill in manually
    python scripts/prepare_dataset.py --in data/source_photos --out data/training_dataset

    # Face-aware crop (needs `pip install -e ".[face]"`)
    python scripts/prepare_dataset.py --in data/source_photos --out data/training_dataset --face-crop

    # Use a different trigger token in the stub captions
    python scripts/prepare_dataset.py --trigger my_subject

This script runs fine on aarch64 (Jetson Thor) with stock Pillow.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageOps

VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--in", dest="src", default="data/source_photos", help="Input directory of raw photos")
    p.add_argument("--out", dest="dst", default="data/training_dataset", help="Output directory")
    p.add_argument("--size", type=int, default=1024, help="Output square size in pixels (default: 1024)")
    p.add_argument("--trigger", default="dkm_person", help="Trigger token written into caption stubs")
    p.add_argument("--face-crop", action="store_true", help="Crop around detected face (needs mediapipe)")
    p.add_argument("--min-face-area", type=float, default=0.04,
                   help="Reject if largest face occupies less than this fraction of image area (default: 0.04)")
    p.add_argument("--reject-multi-face", action="store_true",
                   help="Skip images with more than one detected face (recommended)")
    p.add_argument("--dry-run", action="store_true", help="List actions without writing files")
    p.add_argument("--overwrite", action="store_true", help="Re-process files that already exist in --out")
    return p.parse_args()


def load_mediapipe():
    try:
        import mediapipe as mp  # type: ignore
        return mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    except ImportError:
        print("[!] mediapipe not installed — install with: pip install '.[face]'", file=sys.stderr)
        sys.exit(2)


def detect_faces(detector, pil_img: Image.Image):
    """Return list of (x, y, w, h) face boxes in pixel coords, sorted by area desc."""
    import numpy as np  # local import — only needed when mediapipe is used

    rgb = np.array(pil_img.convert("RGB"))
    h, w = rgb.shape[:2]
    res = detector.process(rgb)
    boxes = []
    if res.detections:
        for det in res.detections:
            bb = det.location_data.relative_bounding_box
            x = max(0, int(bb.xmin * w))
            y = max(0, int(bb.ymin * h))
            bw = min(w - x, int(bb.width * w))
            bh = min(h - y, int(bb.height * h))
            if bw > 0 and bh > 0:
                boxes.append((x, y, bw, bh))
    boxes.sort(key=lambda b: b[2] * b[3], reverse=True)
    return boxes


def square_crop_around_box(img: Image.Image, box: tuple[int, int, int, int], pad_ratio: float = 1.6) -> Image.Image:
    """Crop a square centered on `box`, padded by pad_ratio * max(face_dim).
    If the padded crop would exceed image edges, slide it in.
    """
    W, H = img.size
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    side = int(max(w, h) * pad_ratio)
    side = min(side, min(W, H))  # cap at smaller image dim
    left = int(cx - side / 2)
    top = int(cy - side / 2)
    left = max(0, min(left, W - side))
    top = max(0, min(top, H - side))
    return img.crop((left, top, left + side, top + side))


def center_square_crop(img: Image.Image) -> Image.Image:
    W, H = img.size
    side = min(W, H)
    left = (W - side) // 2
    top = (H - side) // 2
    return img.crop((left, top, left + side, top + side))


def safe_stem(src: Path) -> str:
    """Output filename = original stem + short hash for uniqueness across subdirs."""
    h = hashlib.sha1(str(src.resolve()).encode()).hexdigest()[:6]
    return f"{src.stem}_{h}"


def caption_stub(trigger: str) -> str:
    return f"{trigger}, photo of a person, [DESCRIBE: lighting, pose, framing, expression, attire, setting]\n"


def main() -> int:
    args = parse_args()
    src = Path(args.src)
    dst = Path(args.dst)
    if not src.is_dir():
        print(f"[!] Source dir not found: {src}", file=sys.stderr)
        return 1
    dst.mkdir(parents=True, exist_ok=True)

    detector = load_mediapipe() if args.face_crop else None

    kept = skipped = 0
    files = [p for p in sorted(src.rglob("*")) if p.is_file() and p.suffix.lower() in VALID_EXT]
    if not files:
        print(f"[!] No images found under {src}")
        return 1

    print(f"Found {len(files)} candidate images in {src}")
    for src_path in files:
        out_stem = safe_stem(src_path)
        out_img = dst / f"{out_stem}.jpg"
        out_txt = dst / f"{out_stem}.txt"

        if out_img.exists() and not args.overwrite:
            print(f"  skip (exists): {out_img.name}")
            skipped += 1
            continue

        try:
            img = Image.open(src_path)
            img = ImageOps.exif_transpose(img).convert("RGB")
        except Exception as e:
            print(f"  skip (open failed): {src_path.name} — {e}")
            skipped += 1
            continue

        if detector is not None:
            boxes = detect_faces(detector, img)
            if not boxes:
                print(f"  skip (no face): {src_path.name}")
                skipped += 1
                continue
            if args.reject_multi_face and len(boxes) > 1:
                print(f"  skip (multi-face: {len(boxes)}): {src_path.name}")
                skipped += 1
                continue
            x, y, w, h = boxes[0]
            face_frac = (w * h) / (img.size[0] * img.size[1])
            if face_frac < args.min_face_area:
                print(f"  skip (face too small: {face_frac:.3f}): {src_path.name}")
                skipped += 1
                continue
            cropped = square_crop_around_box(img, boxes[0])
        else:
            cropped = center_square_crop(img)

        resized = cropped.resize((args.size, args.size), Image.LANCZOS)

        if args.dry_run:
            print(f"  would write: {out_img.name}")
        else:
            resized.save(out_img, "JPEG", quality=95)
            if not out_txt.exists() or args.overwrite:
                out_txt.write_text(caption_stub(args.trigger))
            print(f"  wrote: {out_img.name}")
        kept += 1

    print(f"\nDone. Kept {kept}, skipped {skipped}. Output: {dst}")
    if kept < 20:
        print("[!] Fewer than 20 training images. LoRA quality scales with data — aim for 25–40.")
    print("\nNext: open each .txt and replace the [DESCRIBE: ...] stub with a short caption,")
    print("      keeping the trigger token at the start. ai-toolkit will use these at training time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
