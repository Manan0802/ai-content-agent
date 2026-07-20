# Reference assets — 2026-07-20

Style and character exploration done while studying the reference Instagram accounts
(see `docs/superpowers/specs/2026-07-20-reels-reference-analysis.md`).

All images generated **free** via Pollinations (`IMAGE_PROVIDER=pollinations`) at 576×1024
(free-tier cap — production needs 1080×1920 via fal.ai FLUX.2 or a local GPU).

**The prompts below are the real asset** — they are what gets reused to lock a style and a
character across an entire series. Keep them in sync with whatever the pipeline uses.

---

## `style/` — art-direction tests per niche

### Health / "body on trial" (matches `aihealthstudio764`, the 8.6M-view account)
```
Pixar style 3D animated render, highly detailed, expressive cartoon characters with big eyes,
dramatic cinematic warm red and orange rim lighting, shallow depth of field,
vertical 9:16 composition, <SCENE>
```
Scenes that worked: angry stomach in an industrial kitchen; brain judge in a courtroom;
kidney-stone villain on a throne with kidney soldiers; brain+eyeball vs glowing phone at night.

### Devotional / bhakti
```
ultra detailed cinematic 3D render, divine golden glowing light, dramatic volumetric rays,
rich saturated colors, epic devotional atmosphere, vertical 9:16, highly detailed, <SCENE>
```
Scenes that worked: Shiva on Kailash under stars; Hanuman flying with the mountain;
Krishna at the Yamuna at sunset; Jagannath Rath Yatra chariot.

### Thriller / suspense (matches `shadow_files0`)
```
semi realistic digital illustration, Indian comic book art style, clean line art,
cinematic dramatic lighting, moody night atmosphere, detailed rendering, vertical 9:16, <SCENE>
```

---

## `character/` — the recurring lead

The point of a locked character description is that **every part of a series reuses the exact
same string**, so the lead stays recognisable across 30+ images. This is the single hardest
thing to get right and the main reason the reference accounts look like real "shows".

### Style block (graphic-novel — the version that felt right)
```
stunning graphic novel illustration, semi realistic Indian comic art, bold confident linework,
rich cinematic color grading, dramatic chiaroscuro lighting, Bollywood movie poster energy,
highly detailed expressive face, glamorous cinematic framing, vertical 9:16,
```

### Lead character — traditional/signature look (`heroine_graphicnovel_*`)
```
a breathtakingly beautiful Indian heroine, mid 20s, thick lustrous black hair falling in waves,
large deeply expressive kohl-lined eyes, sharp elegant jawline, a signature deep red dupatta,
delicate gold jhumka earrings, magnetic screen presence,
```
The **red dupatta + gold jhumkas** are deliberate signature props — they make her instantly
recognisable in a thumbnail even before you see her face.

### Lead character — modern/western look (`heroine_modern_*`)
```
a breathtakingly beautiful modern Indian woman, mid 20s, long glossy black hair with soft waves,
large expressive kohl-lined eyes, sharp elegant features, subtle glossy makeup, small gold hoop
earrings, wearing a chic fitted burgundy midi dress with a tailored black blazer, elegant heels,
bold confident magnetic presence,
```

### Couple — romance (`couple_*`)
```
a beautiful young Indian couple on their honeymoon, she has long wavy black hair and large
expressive eyes in a flowing summer dress, he is handsome with short black hair in a linen shirt,
both genuinely happy and deeply in love,
```

---

## Known limitation (fix this next)

Character consistency here is **text-description only** — the face still drifts between images.
Real locking needs either:
- **fal.ai FLUX.2** with a reference image (`image_urls`) — ~₹1–3/image, no setup, works today; or
- **local GPU** (M3 Pro, 14-core, Metal) with IP-Adapter/LoRA — free and unlimited, but a real
  setup project and per-image quality is likely *below* FLUX.

Pick one before building the series generator, because the series feature depends on it.
