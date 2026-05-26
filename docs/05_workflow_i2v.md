# Workflow: image-to-video (short clips)

Input: a hero still from [`docs/04_workflow_hero_still.md`](04_workflow_hero_still.md) + a motion prompt.
Output: 2–10 second video at 16fps, 720p.

Why I2V (not T2V): starting from a strong still with your face already nailed is *dramatically* more identity-stable than letting the video model invent the face from text. T2V drifts. I2V anchors.

## Model

**Wan 2.2 14B I2V** (FP8 quantization fits 24 GB VRAM) + **LightX2V** acceleration LoRA.

LightX2V is the difference between a 5-second clip rendering in 60–120 seconds (with LightX2V, ~4–8 sampler steps) vs ~5 minutes (without, 30+ steps). Quality drop is small. Use it.

## ComfyUI graph

See [`workflows/comfyui/README.md`](../workflows/comfyui/README.md). Summary:

```
Load Wan 2.2 I2V (FP8) → LoRA(LightX2V, w=1.0) → Sampler → Decode → VHS_VideoCombine
                                  ↑
        Hero still + motion prompt
```

## Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Steps | 4–8 | LightX2V regime. Without LightX2V: 28–32. |
| CFG | 1.0 | LightX2V trained with CFG=1. Without: 5–7. |
| FPS (output) | 16 | Wan's native. Interpolate to 24/30 in post if needed. |
| Frames | 81 | ~5 seconds @ 16 fps. Wan supports up to 121 frames. |
| Resolution | 720×1280 (portrait for Reels) or 1280×720 | Going past 720p costs VRAM linearly. |

## Motion prompt patterns

Wan 2.2 listens to camera and subject motion cues. Patterns that work:

| Intent | Phrasing |
|--------|----------|
| Subject walks | "the person walks slowly toward the camera, looking around" |
| Subject talks | "the person speaks calmly, slight head movement, occasional smile" |
| Subject reacts | "the person turns their head to the right, surprised expression" |
| Camera moves | "the camera slowly dollies back revealing the full scene" |
| Camera moves on subject | "the camera slowly orbits around the person, cinematic" |
| Hold still | "the person stands still, gentle wind in their hair, slight blink" |

Combine subject motion + camera motion + atmosphere ("rain drizzles", "neon flickers in background"). Avoid contradictory motion ("walks forward but stays still").

## Tuning when identity drifts in the clip

- **Shorten clip length.** 5 seconds is usually safe. At 8+ seconds Wan starts to drift.
- **Make motion subtle.** Big head turns ask the model to invent angles the still doesn't show — that's where face drift happens. Subtle expression changes preserve identity best.
- **Use a more frontal hero still.** A 3/4 profile still as I2V input gives the model less to anchor to.
- **Train a Wan-native character LoRA** (advanced — see [Diffusion-Pipe](https://github.com/tdrussell/diffusion-pipe) or [musubi-tuner](https://github.com/kohya-ss/musubi-tuner)) if you find yourself doing many video clips of yourself and the identity drift in Wan vanilla is too much.

## Save outputs to repo

Save under `outputs/<era>/clip_<NNN>.mp4`.

## Next

For lip-synced talking-head content (you "speaking" lines in different eras), continue to [`docs/06_workflow_talking_head.md`](06_workflow_talking_head.md).
