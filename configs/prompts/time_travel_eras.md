# Time-travel era prompt library

Reusable prompts for the hero-still stage. Replace `[trigger]` with your LoRA's
trigger token (e.g., `dkm_person`) when prompting.

Each prompt below targets one still image. For an Instagram set, generate
3–5 stills per era (varied poses / framings), pick the best one per era,
then animate the chosen still via Wan 2.2 I2V (see `docs/05_workflow_i2v.md`).

Structure of a good prompt for Flux.2 + LoRA + PuLID:
- Subject + trigger token first
- Era / setting
- Wardrobe / props
- Lighting + lens / film stock
- Mood / composition

---

## Ancient & classical

**Ancient Egypt — scribe**
> [trigger], an ancient Egyptian scribe seated cross-legged, holding a reed brush over papyrus, linen kilt, kohl-lined eyes, warm afternoon light through a temple colonnade, low camera angle, painterly

**Roman senator**
> [trigger] as a Roman senator in a white toga with purple trim, standing on marble steps of the Forum, dramatic side light, shallow depth of field, 85mm portrait

**Edo-period samurai**
> [trigger] as an Edo-period samurai in dark indigo kimono and hakama, hand resting on katana, bamboo forest in soft mist, overcast light, traditional Japanese painting composition

## Pre-modern

**Renaissance painter**
> [trigger] as a Renaissance painter in dark wool tunic, paint-stained hands, candlelit studio with half-finished canvas, Caravaggio-style chiaroscuro

**Wild West gunslinger (1880s)**
> [trigger] as a gunslinger on a dusty frontier town main street at golden hour, weathered duster coat and Stetson, tin star on chest, 35mm grain, lens flare

## 20th century

**1920s jazz speakeasy**
> [trigger] in a 1920s pinstripe three-piece suit and fedora, leaning on a brass-railed bar in a smoky speakeasy, jazz band blurred in background, warm tungsten light, sepia tones

**1940s noir detective**
> [trigger] as a 1940s film-noir detective in trench coat and fedora, standing under a streetlamp in rain, hard shadows, black-and-white, deep contrast

**1970s disco**
> [trigger] in a satin shirt unbuttoned at collar, gold chain, wide lapels, on a mirrored dance floor under a disco ball, colored stage lights, soft film grain, 35mm

**1980s arcade**
> [trigger] in a denim jacket and graphic tee, leaning on an arcade cabinet, CRT glow on face, fluorescent ceiling tubes, hazy smoke, retro Kodak color

**1990s grunge**
> [trigger] in a flannel shirt and ripped jeans, sitting on a curb outside a Seattle record store, overcast light, slight motion blur, hand-held film camera feel

## Future

**2099 cyberpunk Tokyo**
> [trigger] in a high-collared techwear jacket with subtle LED trim, standing on a neon-lit Tokyo street in rain, holographic billboards reflected on wet asphalt, blade-runner lighting

**Interstellar colonist (2150s)**
> [trigger] in a fitted exploration suit with visible life-support seams, helmet held under one arm, looking out from a colony dome over an alien red-rock landscape, two moons in sky

**Far-future monk (year 3000)**
> [trigger] in flowing white robes with subtle geometric circuitry patterns, seated cross-legged on a polished obsidian floor of a vast empty hall, single beam of warm light from above

## Fantasy adjacent (optional)

**Steampunk inventor**
> [trigger] in a brass-buttoned waistcoat and leather apron, brass goggles pushed up onto forehead, surrounded by gears and steam-pipes in a cluttered workshop, warm gas-lamp light

**Astronaut on Mars**
> [trigger] in an exploration spacesuit, helmet visor reflecting a Martian sunset, standing beside a planted flag on red dust, photoreal NASA-style cinematography

---

## Prompting tips for identity lock

1. Lead with `[trigger], a portrait of a person, ...` for the strongest LoRA signal — `[trigger]` alone sometimes drifts.
2. Keep era keywords concrete (clothing, props, lens) rather than abstract ("vibes", "feel") — Flux.2 follows specifics better.
3. If face drifts, raise LoRA weight from 0.6 to 0.7–0.8 and lower PuLID weight from 0.8 to 0.6. (Stacking both too hot causes plasticky skin.)
4. For full-body shots, add `full body, standing, head visible` — otherwise Flux.2 tends to over-zoom on faces with strong LoRAs.
