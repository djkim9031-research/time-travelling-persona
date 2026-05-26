# What to do on Jetson Thor

This box (aarch64, Blackwell, 128GB unified memory) is the wrong machine for the heavy stack (ComfyUI custom nodes, PuLID, Sonic) but it's the right machine for everything *before* generation.

## What you can do here, today

1. **Clone the repo and set up the lightweight Python env.**
2. **Collect and pre-process your training photos.** Output is a directory of 1024×1024 JPEGs + caption stubs.
3. **Author / refine prompts** in [`configs/prompts/time_travel_eras.md`](../configs/prompts/time_travel_eras.md).
4. **Write / edit the ai-toolkit config** in [`configs/ai_toolkit/flux2_lora_train.yaml`](../configs/ai_toolkit/flux2_lora_train.yaml).
5. **Transfer the curated dataset** to the x86 workstation when it's ready.

## Setup

```bash
cd ~/repos/time-travelling-persona

# Minimal install — Pillow only. Works on aarch64 with no compiler grief.
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Optional: face-aware cropping (recommended)
pip install -e ".[face]"
```

`mediapipe` ships aarch64 wheels and installs cleanly on Thor. If it fails, fall back to plain center-crop (don't pass `--face-crop`).

## Step 1 — collect photos

Drop 25–40+ photos into `data/source_photos/`. See [`data/README.md`](../data/README.md) for the collection guidelines.

```bash
# From wherever your photos live:
cp -r /path/to/your/photos/* ~/repos/time-travelling-persona/data/source_photos/
ls data/source_photos/ | wc -l
```

## Step 2 — prep the dataset

```bash
# Face-aware crop (recommended)
python scripts/prepare_dataset.py \
    --in data/source_photos \
    --out data/training_dataset \
    --face-crop \
    --reject-multi-face

# Or basic center crop if mediapipe isn't installed
python scripts/prepare_dataset.py --in data/source_photos --out data/training_dataset
```

Output: `data/training_dataset/<stem>_<hash>.jpg` (1024×1024) + matching `.txt` caption stub.

## Step 3 — caption the dataset

The script writes stub captions. Edit each `.txt` to replace the `[DESCRIBE: ...]` placeholder with a real description.

```bash
# Open all stubs in your editor of choice:
ls data/training_dataset/*.txt | xargs -n1 echo  # list them
nano data/training_dataset/<one>.txt              # edit one
```

This is the most tedious step. Budget 30–45 minutes for ~30 images. See [`data/README.md`](../data/README.md) for caption format and examples.

## Step 4 — sanity check

```bash
python scripts/verify_environment.py
```

You should see:
- `Dataset prep` → READY
- `LoRA training` → NOT READY (no CUDA stack on this box — that's expected and fine)

## Step 5 — transfer to x86

When the dataset is captioned and you're ready to train:

```bash
# To another machine on the LAN:
rsync -av --progress data/training_dataset/ user@x86-workstation:/path/to/clone/data/training_dataset/

# Or to a cloud bucket / RunPod volume:
tar czf training_dataset.tar.gz data/training_dataset/
# then upload tarball via scp / aws s3 cp / rsync / runpod cli
```

**Do not commit `data/training_dataset/` to git** — it's gitignored for a reason. Your face is private.

## Things you CANNOT do on Thor (don't try)

- Install full ComfyUI with PuLID-Flux2 / Sonic / InfiniteYou custom nodes — these have brittle aarch64 wheels and you'll burn a day debugging.
- Run ai-toolkit Flux.2 LoRA training — even though Thor has lots of unified memory, ai-toolkit's CUDA path expects x86 wheels (bitsandbytes, xformers).
- Run Wan 2.2 video generation at a reasonable speed.

The exception: NVIDIA's Jetson AI Lab has tutorials for vanilla Flux + ComfyUI on Jetson (no custom nodes). Useful as a future experiment but not on the critical path right now.

## Next

Once `data/training_dataset/` is captioned and copied to the x86 box, move to [`docs/02_setup_x86.md`](02_setup_x86.md).
