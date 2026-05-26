# Overview

Read this first. The other docs assume you've seen this one.

## What you're building

A repeatable pipeline that takes a text prompt and your own face, and produces a still / short clip / talking-head video that looks recognizably like you.

Three output types, three workflows:

| Workflow | Input | Output | Time per generation (RTX 4090) |
|----------|-------|--------|--------------------------------|
| Hero still | Era prompt + 1 reference photo | 1024×1024 image | 30–60 s |
| I2V clip | A hero still + motion prompt | 2–10 s video @ 16fps 720p | 60–120 s w/ LightX2V |
| Talking head | A hero still + audio file | Lip-synced video | ~real-time × 2 |

## Why two layers of identity preservation

A face adapter alone (PuLID, IP-Adapter, InstantID) steers the model toward your face but doesn't *teach* the model your identity — it averages your face against the base model's prior. A personal LoRA does teach the model — you become a token in vocabulary — but a LoRA trained on 30 photos doesn't cover every angle. Stacking them gives:

- **LoRA** = strong identity baseline across all generations
- **Face adapter** = per-generation correction from one reference photo

This is the empirically best open-source setup for one specific person as of late 2025 / early 2026.

## Phases of the project

1. **Collect** photos. Off the machine. (Phone, hard drive, whatever.)
2. **Prep** dataset on Jetson Thor (this box). → [`docs/01_setup_thor.md`](01_setup_thor.md)
3. **Set up** the x86 workstation. → [`docs/02_setup_x86.md`](02_setup_x86.md)
4. **Train** the personal LoRA (one-time, ~1–3 GPU-hours). → [`docs/03_lora_training.md`](03_lora_training.md)
5. **Generate** hero stills. → [`docs/04_workflow_hero_still.md`](04_workflow_hero_still.md)
6. **Animate** stills to short clips. → [`docs/05_workflow_i2v.md`](05_workflow_i2v.md)
7. **Lip-sync** for talking-head versions. → [`docs/06_workflow_talking_head.md`](06_workflow_talking_head.md)
8. **Verify** the output is good enough to post. → [`docs/07_verification.md`](07_verification.md)

