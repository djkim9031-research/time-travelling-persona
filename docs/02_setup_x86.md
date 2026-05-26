# x86 workstation setup

Target hardware: x86_64 Linux with an NVIDIA GPU, **24 GB VRAM minimum** (RTX 3090 / 4090 / 5090 / A6000 / H100 / etc.), driver supporting CUDA 12.x, Python 3.10–3.12.

If you don't have such a box: **RunPod** rents H100 / A6000 / 4090 instances by the hour. A community-cloud 4090 is ~$0.40/hr; an H100 is ~$2/hr. The full pipeline (train LoRA + generate dozens of stills + clips) fits comfortably in <$10 of rental.

## 1. Clone

```bash
git clone https://github.com/djkim9031-research/time-travelling-persona.git
cd time-travelling-persona
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## 2. Copy in your curated dataset from Thor

```bash
rsync -av thor:/home/dkim4/repos/time-travelling-persona/data/training_dataset/ data/training_dataset/
ls data/training_dataset/*.jpg | wc -l    # should be 25–40
```

## 3. Verify GPU is visible

```bash
python scripts/verify_environment.py
```

Expect `LoRA training` → READY after step 4.

## 4. Install PyTorch matching your CUDA

```bash
# CUDA 12.4 — adjust the index URL if your driver is different
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## 5. Install ai-toolkit (for LoRA training)

ai-toolkit is a separate repo. Clone it next to this one:

```bash
cd ..
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
pip install -r requirements.txt
```

Confirm Flux.2 support is in your checkout:

```bash
ls config/examples/ | grep -i flux2
```

If you don't see a Flux.2 example, `git pull` ai-toolkit — Flux.2 support landed at Flux.2 launch in late 2025.

## 6. Install ComfyUI (for inference)

```bash
cd ..
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# Add the Manager (essential for the custom nodes below)
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
cd ..

# Launch:
python main.py --listen 0.0.0.0
```

Open `http://localhost:8188` (or the workstation's IP if remote).

## 7. Install custom nodes via Manager

Inside ComfyUI's Manager UI, install:

- **ComfyUI-PuLID-Flux2** (iFayens) — face adapter for Flux.2
- **ComfyUI-WanVideoWrapper** (kijai) — Wan 2.2 I2V
- **ComfyUI-Sonic** — talking head
- **ComfyUI-VideoHelperSuite** (kijai) — `VHS_VideoCombine` save node
- **ComfyUI-Advanced-ControlNet** — optional pose conditioning

Restart ComfyUI after install.

## 8. Download model weights

Use `huggingface-cli` (login first with a token that has accepted each model's license):

```bash
huggingface-cli login

# Flux.2 base + VAE + text encoders
huggingface-cli download black-forest-labs/FLUX.2-dev \
    --local-dir ComfyUI/models/diffusion_models/flux2-dev

# Wan 2.2 I2V (FP8 — fits 24GB)
huggingface-cli download Wan-AI/Wan2.2-I2V-A14B \
    --local-dir ComfyUI/models/diffusion_models/wan2.2-i2v-a14b

# LightX2V acceleration LoRA for Wan 2.2 (search Manager for current canonical repo)

# PuLID-Flux2 weights — see the iFayens repo README for exact HF path

# Sonic weights — see the ComfyUI-Sonic repo README
```

Verify the files end up in the paths listed in [`workflows/comfyui/README.md`](../workflows/comfyui/README.md).

## 9. Confirm the stack runs

Quick smoke test — generate a Flux.2 still with no LoRA / no PuLID first:

1. In ComfyUI, load the default Flux example workflow (`Workflow → Open Default → flux_dev`).
2. Point the checkpoint loader at `flux2-dev`.
3. Render a generic prompt ("a red bicycle"). If you get an image, the base stack works.

Then add LoRA loader + PuLID-Flux2 nodes per [`workflows/comfyui/README.md`](../workflows/comfyui/README.md).

## Next

Move to [`docs/03_lora_training.md`](03_lora_training.md) to train your personal LoRA.
