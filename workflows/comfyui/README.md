# ComfyUI workflows

This directory will hold the three ComfyUI workflow JSONs once you author them on the x86 box. The workflow files themselves are intentionally NOT committed as templates — ComfyUI workflow JSON depends on the exact custom-node versions and model paths on your machine, and a stale JSON does more harm than no JSON.

## How to author each workflow

Build the graph live in ComfyUI, then `File → Save (API Format)` and drop the JSON in this directory with the filename suggested below.

### `01_hero_still.json` — Flux.2 + personal LoRA + PuLID-Flux2

Nodes:

```
[Load Checkpoint: FLUX.2-dev]
        │
        ├──> [LoRA Loader: time_travel_persona_v1.safetensors  weight=0.6]
        │
        ├──> [PuLID Flux II Loader] ──> [PuLID Flux II Apply  weight=0.8]
        │                                       ↑
        │                              [Load Image: one good reference photo of you]
        │
        ├──> (optional) [ControlNet OpenPose] ──> [Apply ControlNet]
        │                                              ↑
        │                                     [Load Image: pose reference]
        │
        ├──> [CLIP Text Encode (Positive)] ── era prompt from configs/prompts/time_travel_eras.md
        ├──> [CLIP Text Encode (Negative)] ── usually empty for Flux
        │
        ├──> [Empty Latent: 1024×1024]
        │
        └──> [KSampler  steps=20 cfg=4 sampler=flowmatch] ──> [VAE Decode] ──> [Save Image]
```

Settings to remember:
- LoRA weight 0.6, PuLID weight 0.8 as starting point. If face drifts, push LoRA to 0.7–0.8 and PuLID down to 0.6.
- Use one reference photo for PuLID per generation — its highest-quality shot, well-lit, near-frontal.

### `02_animate_still.json` — Wan 2.2 I2V

Nodes:

```
[Load Diffusion Model: Wan2.2-I2V-A14B (FP8)]
        │
        ├──> [LoRA Loader: LightX2V LoRA  weight=1.0]
        │
        ├──> [Load Image: hero still from workflow 01]
        │       │
        │       └──> [WanImageEncode]
        │
        ├──> [CLIP Text Encode] ── motion prompt: e.g. "the person walks forward, camera dollies back slowly, cinematic"
        │
        └──> [Wan Sampler  steps=4-8 (LightX2V)  fps=16  frames=80] ──> [VAE Decode (Wan)] ──> [VHS Video Combine]
```

LightX2V cuts denoising steps from ~30 to 4–8 with only modest quality loss, so 5-second 720p clips render in 60–120s on a 4090.

### `03_talking_head_sonic.json` — Sonic

Nodes:

```
[Sonic Model Loader]
        │
        ├──> [Load Image: chosen portrait — usually a Bucket-1 hero still]
        ├──> [Load Audio: your recorded WAV/MP3]
        │
        └──> [Sonic Sampler  motion_scale=1.0  steps=25] ──> [VHS Video Combine  fps=25]
```

For full sentences (>5s), Sonic chunks audio internally — works out of the box. For long takes (>30s), split into multiple shorter clips and concat in a video editor.

## Custom nodes to install (via ComfyUI-Manager)

- `ComfyUI-PuLID-Flux2` (iFayens) — Bucket 1 face adapter
- `ComfyUI-WanVideoWrapper` (kijai) or the native Wan nodes — Bucket 2 I2V
- `ComfyUI-Sonic` — Bucket 3 talking head
- `ComfyUI-VideoHelperSuite` (kijai) — video save/combine
- `ComfyUI-Advanced-ControlNet` — for the optional pose conditioning in Workflow 01

## Where to put model weights in ComfyUI's tree

```
ComfyUI/models/
  diffusion_models/
    flux2-dev.safetensors                   # Flux.2 base
    wan2.2-i2v-a14b-fp8.safetensors         # Wan 2.2 I2V
  loras/
    time_travel_persona_v1.safetensors      # YOUR trained LoRA (output of ai-toolkit)
    lightx2v-wan22.safetensors              # Wan acceleration LoRA
  pulid/
    pulid_flux2_v1.safetensors              # PuLID-Flux2 weights
  clip/                                     # text encoder shards if Flux.2 needs split download
  vae/                                      # Flux.2 VAE (if split download)
  sonic/                                    # Sonic weights
```

Exact filenames depend on what HuggingFace publishes — keep the names the node expects.
