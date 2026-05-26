# Training the personal LoRA

One-time process. Output: a `.safetensors` file (~150–300 MB) that you load alongside Flux.2 in ComfyUI.

Prereqs:
- `data/training_dataset/` is populated and captioned (Thor steps done).
- ai-toolkit is cloned and `pip install`-ed.
- 24 GB+ VRAM, CUDA working (`python scripts/verify_environment.py` shows READY).

## 1. Edit the training config

Open [`configs/ai_toolkit/flux2_lora_train.yaml`](../configs/ai_toolkit/flux2_lora_train.yaml). Set:

- `folder_path:` → **absolute path** to `data/training_dataset/` on this machine.
- `trigger_word:` → your chosen rare token (default `dkm_person`). Whatever you pick, use the same one in your prompts later.
- `name:` → run name, written to ai-toolkit's `output/` directory.

If you have <24 GB VRAM, also set `quantize: true` (already the default) and lower `linear: 32` → `linear: 16`.

If you have ≥48 GB VRAM, set `quantize: false` for marginally better fidelity.

## 2. Run training

From the ai-toolkit checkout:

```bash
cd /path/to/ai-toolkit
source ../time-travelling-persona/.venv/bin/activate    # or your ai-toolkit venv
python run.py /path/to/time-travelling-persona/configs/ai_toolkit/flux2_lora_train.yaml
```

Expected runtimes for 2000 steps:

| GPU | Wall time |
|-----|-----------|
| H100 80GB | ~50–70 min |
| A6000 48GB | ~2 hr |
| RTX 4090 24GB | ~2.5–3 hr |
| RTX 3090 24GB | ~3.5 hr |

Sample images are saved to `output/<name>/samples/` every 250 steps. **Watch these — they're how you know if training is working.**

## 3. What to look for in the samples

- Steps 0–250: face is the base model's average — not you yet.
- Steps 500–1000: face starts converging on you. Compare to a real photo.
- Steps 1000–1500: identity should be solid. If samples look like you in the trigger-token prompts but generalize well to the era prompts, you're done.
- Steps 1500–2500: diminishing returns. Watch for **overfitting** — same pose / expression / lighting across all samples means the LoRA memorized your photos instead of learning your face.

Stop when sample quality stabilizes. The best checkpoint is usually NOT the last one — pick the one with the best identity + variety balance.

## 4. Install the LoRA into ComfyUI

```bash
# Copy the best checkpoint into ComfyUI's loras directory
cp /path/to/ai-toolkit/output/time_travel_persona_v1/time_travel_persona_v1_001500.safetensors \
   /path/to/ComfyUI/models/loras/time_travel_persona_v1.safetensors
```

In ComfyUI, refresh the Manager (or restart) and the LoRA name will appear in the `Load LoRA` node's dropdown.

## 5. Quick quality sanity check

Generate 5 portraits in ComfyUI with just `Flux.2 + your LoRA` (no PuLID yet):

```
Prompt: dkm_person, portrait, studio lighting, neutral expression
```

If those look like you, the LoRA is good. Add PuLID-Flux2 on top for the production workflow (see [`docs/04_workflow_hero_still.md`](04_workflow_hero_still.md)).

If they DON'T look like you:
- Captions might be wrong — verify trigger token is at the start of every `.txt` in `data/training_dataset/`.
- LoRA weight in the loader might be too low — try `1.0` for this sanity test.
- Try an earlier checkpoint (often the last checkpoint overfits).
- If still bad: dataset is the problem. Re-collect with more angle/lighting variety.

## 6. Versioning

When you re-train (more photos, different rank, different settings), bump the suffix:
`time_travel_persona_v2.safetensors`, etc. Keep older versions — sometimes v1 produces better results in a specific setting and you'll want to A/B test.
