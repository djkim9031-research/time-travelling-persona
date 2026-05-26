# Verification (quality gates)

Before you post anything generated to a public account, run these checks. The goal: when a friend looks at it, the only thing they should be uncertain about is *how you made it*, not *who that is*.

## Gate 1 — Identity sanity (stills)

Print or fullscreen 10 generated stills next to 5 real photos of yourself. Show to two friends who know you well, separately. Ask: "circle the real photos."

- **Pass**: friends sometimes pick AI ones thinking they're real, or vice versa, but never say "this isn't you."
- **Fail (and how to fix)**: friends consistently say "this doesn't look like you" → LoRA undertrained or dataset lacked angle coverage. Retrain with more photos. Don't ship.

## Gate 2 — Identity drift (video)

Take your best I2V clip. Scrub frame-by-frame in a video player (VLC: `E` for next frame, `Shift+E` for previous).

- **Pass**: identity holds through small head turns (≤15° yaw) and expression changes. Eyes, nose proportions, jawline stay yours.
- **Fail**: face morphs noticeably between adjacent frames → shorten clip length, use a more frontal hero still, or reduce motion in the prompt.

## Gate 3 — Lip-sync (talking head)

Watch a Sonic-generated clip at 0.5× speed with audio. Check phoneme matches:

| Sound | Mouth shape |
|-------|-------------|
| `b / p / m` | Lips fully closed |
| `f / v` | Lower lip touches upper teeth |
| `o / u` | Lips rounded forward |
| `ee` (as in "see") | Lips wide, teeth showing |

- **Pass**: 90%+ of those land. Hard-to-judge frames are okay.
- **Fail**: noticeable mouth flap that doesn't match audio → re-record audio cleaner, or switch to LatentSync for overlay-style lip sync.

## Gate 4 — Era authenticity

Show a still to someone (ideally a friend who knows the era — boomer for 70s, etc.) WITHOUT context. Ask: "what year is this?"

- **Pass**: their guess is within 5–10 years of your intended era.
- **Fail**: they say "looks like a costume" or "this is just a modern person in old clothes" → prompt needs era-specific props/lighting/film cues, not just clothing.

## Gate 5 — Compositional check (hands, text, background)

Zoom into the still at 100% in an image viewer. Inspect:
- Hands — 5 fingers, no extra knuckles, no merged fingers.
- Any text (signs, books, posters) — readable or convincingly blurred? AI text gibberish kills the realism.
- Background continuity — no objects that bleed into each other, no impossible perspective.

This is the most common reason a still that *looks* great at thumbnail size falls apart on Instagram (which displays full-resolution on tap).

If anything fails: inpaint the offending region in ComfyUI with a small Flux-fill node, or just generate a new seed.

## Gate 6 — License sanity

Before any commercial / sponsored use:
- Flux.2 [dev] — non-commercial dev license. Check current terms before monetizing.
- Wan 2.2 — Apache-style license, generally permissive.
- Sonic — research/non-commercial. Check before monetizing.
- Likeness — you're using your own face, so no third-party likeness concern.

For Instagram personal posts: all of these are fine. For paid promotion or merch: re-read the licenses.

## Tracking what worked

Keep a simple log:

```
outputs/<era>/notes.md

- LoRA version: v1
- LoRA weight: 0.6
- PuLID weight: 0.8
- Reference photo used: data/source_photos/best_studio_shot.jpg
- Prompt: <copy from configs/prompts/time_travel_eras.md>
- Seed: 4421
- Pass gates 1, 2, 5; Gate 4 weak (era reads too clean). Next time: add "soft 35mm film grain".
```

After a few eras you'll know your machine's sweet spot for weights / steps / which reference photo works best.
