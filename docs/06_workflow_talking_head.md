# Workflow: talking head (lip-synced)

Input: a hero portrait still + an audio file (your voice).
Output: a video of that portrait speaking your audio, with natural facial motion.

## When to use this vs Wan 2.2 I2V

| Want | Use |
|------|-----|
| You speaking a line | Sonic (this workflow) |
| You doing an action (walking, reacting, gesturing) | Wan 2.2 I2V |
| You speaking *while* doing an action | Wan 2.2 first, then LatentSync to overlay lip motion |

Sonic is purpose-built for portrait + audio. It nails lip sync and produces natural eyebrow / micro-expression motion that pure I2V doesn't.

## Model

**Sonic** — primary pick. Mature ComfyUI integration, best identity preservation among open lip-sync models as of late 2025.

Backups (don't bother unless Sonic fails):
- **HunyuanVideo Avatar (audio mode)** — for longer / more dynamic shots.
- **LatentSync** — pure lip-overlay onto an existing video (e.g., onto a Wan 2.2 clip).

## Input prep

### The portrait still

- Use a hero still from your Bucket-1 workflow — the same identity layer means the talking-head face matches your other generated images.
- Frontal or near-frontal. Sonic struggles with strong profiles.
- Face occupying ~30–50% of the frame.
- Resolution 512×512 or 768×768 typically — Sonic doesn't need 1024.

### The audio

- Record yourself reading the line. ~5–15 seconds for a single take.
- WAV preferred. 16 kHz mono is fine.
- Clean recording — no music, no background noise. Phone voice memos work if you record in a quiet room.
- Pace: natural conversational speed. Very fast speech causes lip sync to lag.

Tool tip: `ffmpeg` for cleanup:

```bash
# Convert any input to a 16 kHz mono WAV that Sonic likes:
ffmpeg -i input.m4a -ar 16000 -ac 1 voice_clean.wav
```

## ComfyUI graph

See [`workflows/comfyui/README.md`](../workflows/comfyui/README.md). Summary:

```
Sonic Model Loader → Sampler → VHS_VideoCombine (fps=25)
        ↑
  Portrait still + audio WAV
```

## Settings

| Setting | Value | Notes |
|---------|-------|-------|
| motion_scale | 1.0 | Higher = more expressive, but more identity drift |
| steps | 25 | Sonic default. 20 if you want faster iteration. |
| fps | 25 | Sonic native. Re-encode to 30 in post if needed. |

## Tuning

- **Lip sync drifts on certain syllables (`b/p/m`)**: input audio quality. Re-record cleaner.
- **Eyes look dead / blink rate wrong**: raise motion_scale to 1.2.
- **Identity drifts mid-clip**: take a sharper portrait, or use a slightly larger face crop in the input.
- **Clip ends abruptly**: trim audio to end on a complete word.

## Long-form takes (>30 s)

Sonic handles ~30 s comfortably. For longer:
- Split audio into 15–25 s chunks at sentence boundaries.
- Render each chunk.
- Stitch in a video editor (DaVinci Resolve, Premiere, or `ffmpeg -f concat`).
- Reuse the same portrait still across chunks for visual continuity.

## Save outputs to repo

Save under `outputs/<era>/talking_<NNN>.mp4`.

## Next

Quality-gate your outputs before posting — see [`docs/07_verification.md`](07_verification.md).
