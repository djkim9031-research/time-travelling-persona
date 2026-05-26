# Data directory

This directory holds your face data. **Everything under `source_photos/` and `training_dataset/` is gitignored** — your face never goes to the remote.

## `source_photos/`

Drop your raw photos here. Subdirectories are fine — `prepare_dataset.py` recurses.

### Collection guidelines for a strong personal LoRA

Aim for **25–40 photos** with this distribution:

| Type | Count | Notes |
|------|-------|-------|
| Close-up face (head + shoulders) | 8–12 | Sharp focus on face. Varied expressions. |
| Mid-shot (waist up) | 8–12 | Different clothing, different backgrounds. |
| Full body | 6–10 | Standing, sitting, walking — varied posture. |
| Side / 3/4 profile | 4–6 | Critical for video — I2V needs angle coverage. |

### Hard rules

- One person per photo (not you + friends).
- Sharp focus on the face. Reject any blur / motion-blur on the face.
- No sunglasses, no heavy filters, no Snapchat-style face distortions.
- Mix lighting: indoor / outdoor / golden hour / overcast / studio if you have it.
- Mix outfits and backgrounds — the LoRA should learn *you*, not "you in your one favorite shirt".
- Resolution: 1024×1024 or higher native. Phone portrait shots are fine.
- Recent: photos from the last ~2 years. Old photos teach the model an outdated you.

### Common pitfalls

- All selfies from the same angle → LoRA only knows you from one camera height.
- All photos in similar lighting → LoRA bakes that lighting into your "look".
- Photos with strong filters → LoRA learns the filter as part of your face.
- Group photos cropped down → the model often picks up bystanders' features.

## `training_dataset/`

Auto-populated by `scripts/prepare_dataset.py`. For each photo it creates:

- `<stem>_<hash>.jpg` — 1024×1024 square crop (face-centered if `--face-crop` and mediapipe are available)
- `<stem>_<hash>.txt` — caption stub that you should edit before training

### Caption format (ai-toolkit)

The stub looks like:

```
dkm_person, photo of a person, [DESCRIBE: lighting, pose, framing, expression, attire, setting]
```

Replace `[DESCRIBE: ...]` with a short factual caption. Examples:

```
dkm_person, photo of a person, close-up portrait, soft window light, neutral expression, blue t-shirt, white wall background

dkm_person, photo of a person, full body, standing on a beach at golden hour, smiling, white linen shirt and khaki shorts

dkm_person, photo of a person, three-quarter profile, indoor cafe, looking off-camera, dark hoodie, soft bokeh background
```

Why this format:
- Trigger token at the start gives the strongest learning signal.
- "photo of a person" keeps the LoRA from baking in unrelated subject-class noise.
- Concrete descriptors (lighting, pose, attire) become *editable* at inference — the model learns "your face under variable conditions" instead of "your face under one fixed condition".

You don't need to caption every detail. Aim for ~10–20 words per image.
