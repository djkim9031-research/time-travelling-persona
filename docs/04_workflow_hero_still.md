# Workflow: hero still

Input: an era prompt + one reference photo of you.
Output: 1024×1024 image of you in that era. This is the still you'll later animate.

## ComfyUI graph

See [`workflows/comfyui/README.md`](../workflows/comfyui/README.md) for the node-by-node layout. Summary:

```
Flux.2-dev → LoRA(your, w=0.6) → PuLID-Flux2(ref photo, w=0.8) → KSampler → Save
                                                      ↑
                       (optional)  ControlNet OpenPose ┘
```

## Inputs you need ready

- `time_travel_persona_v1.safetensors` in `ComfyUI/models/loras/`
- One **best** reference photo of yourself, saved somewhere ComfyUI can load (well-lit, sharp focus, near-frontal, neutral expression). This goes into the PuLID Image Load node.
- An era prompt from [`configs/prompts/time_travel_eras.md`](../configs/prompts/time_travel_eras.md).

## Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Sampler | flowmatch (Flux native) | |
| Steps | 20 | 24–28 if you want slightly cleaner detail |
| CFG | 4.0 | Flux works best in 3.5–5.0 range |
| Resolution | 1024×1024 | Square — easiest for I2V follow-up |
| LoRA weight | 0.6 | First try; raise if face drifts |
| PuLID weight | 0.8 | First try; lower if skin looks plasticky |
| Seed | random | Vary across batch of 10–20 |

## Batch & cull

For each era you want to publish, generate **10–20 stills** (vary seed only), then pick 1–2 hero images.

It's faster to over-generate and cull than to try to nail it in one shot — Flux still occasionally produces a great image with a slightly-off face, or vice versa.

Cull criteria:
1. **Identity** — does it look like you, not "someone who could be your cousin"? Hold up next to a real photo.
2. **Era authenticity** — does the wardrobe / setting / lighting actually evoke the era? (1970s disco shouldn't look like 2020 fashion.)
3. **Compositional cleanliness** — no extra limbs, no melted hands, no weird text on signs.

## Tuning when identity drifts

Order of operations, try one change at a time:

1. **Use a closer / sharper reference photo for PuLID.** This is the #1 fix.
2. **Raise LoRA weight 0.6 → 0.7 → 0.8.** Past 0.8 the LoRA starts dominating the style cues from your prompt.
3. **Lower PuLID weight 0.8 → 0.6.** Helps if skin looks artificial.
4. **Add `photorealistic, sharp focus on face, 50mm lens` to the prompt.** Pushes the model toward portrait priors.
5. **Add a face ControlNet** if you have a specific angle you want — but only if (1–4) didn't fix it. Adds graph complexity.

## Tuning when the era looks generic

If the face is right but the era reads bland:

1. Make prompt era-specific: instead of "1970s clothes", use "1973 polyester wide-collar shirt, bell-bottom trousers".
2. Add a single lens/lighting cue from the era: "soft 35mm film grain", "tungsten interior light", "VHS color palette".
3. Drop ControlNet pose constraint — it can fight the era's natural body language.

## Save outputs to repo

Save final picks under `outputs/<era>/hero_<NNN>.png`. The `outputs/` tree is gitignored so it's safe to keep large files there without bloating the repo.

## Next

Pick your best 1–2 hero stills per era, then move to [`docs/05_workflow_i2v.md`](05_workflow_i2v.md) to animate them.
