# time-travelling-persona

Generate identity-preserved "time travel" still images, short video clips, and talking-head videos of one specific person (me) using open-source local models. Used to publish stylized content (1970s disco, Edo-period samurai, 2099 cyberpunk, etc.) to social media while my face stays recognizably me.

## Approach

Two-layer identity preservation:

1. **Personal LoRA** trained on 25–40 of my own photos with [ai-toolkit](https://github.com/ostris/ai-toolkit) — teaches Flux.2 my face as a token (`dkm_person`).
2. **Zero-shot face adapter** ([PuLID-Flux2](https://github.com/iFayens/ComfyUI-PuLID-Flux2)) stacked on top at generation time — locks identity from angles the LoRA didn't cover.

Pipeline:

| Stage | Tool | Output |
|-------|------|--------|
| Hero still | ComfyUI: Flux.2 + my LoRA + PuLID-Flux2 (+ optional ControlNet pose) | 1024px image per era |
| Short clip | ComfyUI: Wan 2.2 14B I2V + LightX2V LoRA, fed from the hero still | 2–10 s video |
| Talking head | ComfyUI: Sonic (portrait + audio) | Lip-synced video |

See [docs/](docs/) for step-by-step setup and workflow guides.

## Repo layout

```
configs/
  ai_toolkit/flux2_lora_train.yaml   # LoRA training config
  prompts/time_travel_eras.md        # Era prompt library
data/
  source_photos/                     # Raw photos (gitignored)
  training_dataset/                  # Curated 1024px + captions (gitignored)
docs/                                # Setup + workflow guides
scripts/
  prepare_dataset.py                 # Resize, crop, caption-stub photos
  verify_environment.py              # Check GPU/CUDA/deps on whatever box you're on
workflows/comfyui/                   # ComfyUI workflow templates + how to load them
outputs/                             # Generated content (gitignored)
```

## Status

| Phase | Where | Status |
|-------|-------|--------|
| Repo scaffold | Jetson Thor (current) | ✅ |
| Collect 25–40 source photos | Anywhere | ⏳ |
| Run `prepare_dataset.py` | Thor (PIL only — works on aarch64) | ⏳ |
| Set up ComfyUI + ai-toolkit | x86 workstation w/ 24GB+ NVIDIA GPU | ⏳ |
| Train personal LoRA | x86 / RunPod H100 (~1–3 GPU-hours) | ⏳ |
| Run hero still / I2V / Sonic workflows | x86 | ⏳ |

Start with [docs/01_setup_thor.md](docs/01_setup_thor.md) for what to do on the current machine.

## License

Personal-use repository. Model weights have their own licenses (Flux.2 dev license, Wan 2.2 license, Sonic license) — review before any commercial use.
