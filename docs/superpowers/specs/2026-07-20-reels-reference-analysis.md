# Instagram Reels Reference Analysis — 2026-07-20

Analysis of 8 reference reels supplied by Manan, viewed live on Instagram. Purpose: extract **topic buckets** and **format rules** that are actually working right now, to feed `prompts/script_prompts.py` and `prompts/idea_prompts.py`.

## Raw data

| # | Account | Topic | Format | Likes | Comments |
|---|---------|-------|--------|-------|----------|
| 1 | `aihealthstudio764` | AI talking stomach — "momos/chowmein khaate ho?" | Single | **317K** | 4.5K |
| 2 | `realistic_crime` | Crime story — Monty, ₹100 Cr | "Part 2 ke liye 100 like" | 98K | 2.1K |
| 3 | `krjha176` | "Dinner at a five star hotel" (ironic — village meal) | Single, real-life | **900K** | 1.8K |
| 4 | `ai_reels_hub01` | Nostalgia — barish + mummy ke bread pakode | Single | 9.9K | 46 |
| 5 | `amitghosh5395` | Jagannath Rath Yatra ke 9 Rahasya | Part 1 | 6 | 1 |
| 6 | `shadow_files0` | "DELIVERY" animated story | PART 1 | 18.8K | 64 |
| 7 | `shadow_files0` | same story | PART 2 | 17.6K | 161 |
| 8 | `shadow_files0` | same story | PART 4 | **25.3K** | **552** |

## The single biggest finding: multi-part engagement compounds

`shadow_files0`'s series shows **later parts outperform Part 1** — likes 18.8K → 25.3K, comments **64 → 552 (8.6x)**. The comment sections are dominated by *"Next part"*, *"Next episode"*, *"Continue"*. The cliffhanger genuinely converts viewers into a returning audience that comments to demand more.

`realistic_crime` gates it explicitly: **"Part 2 ke liye 100 like kar dijiye"** — engagement is the unlock. Caption ends on stacked cliffhanger questions ("Ab monty kya karega? Kaise wapas dega 100 Cr?").

**Implication for our pipeline:** one story → 5-6 parts × 20-25s, each ending on a cliffhanger, is a higher-leverage format than one standalone video. This is the top build priority.

## Topic buckets that are working

1. **Anthropomorphic health/body** — organs that talk and argue ("agar aapke शरीर के अंग बोल पाते, to kya kehte?"). Reel 1 = 317K. Everyday Indian food as the villain (momos, chowmein). Extremely shareable — comment section is *people tagging friends*, which is the actual viral engine.
2. **Crime / mystery serial** — a named protagonist, money stakes, betrayal. Runs as a multi-part serial.
3. **Nostalgia** — barish, mummy ke haath ka khana, bachpan, cartoons. Triggers long emotional comments (people writing paragraphs about missing their mother's cooking). Low ban risk, high emotional payload.
4. **Ironic everyday humour** — "Dinner at a five star hotel" over a simple village meal. 900K likes, the biggest performer of the set, and it's *real footage*, not AI. The joke is the contrast between caption and visual.
5. **Bhakti / mythology mysteries** — "Jagannath Rath Yatra ke 9 Rahasya | Part 1". Note: this one **flopped (6 likes)** despite correct format — proof that format alone doesn't save weak execution/distribution. The category is viable (huge Indian audience, ad-friendly) but needs genuinely strong hooks and visuals, not just keyword-stuffed captions.
6. **Slice-of-life fiction serial** — ordinary setup (a delivery, a knock at the door) escalating into drama. *Caveat: the reference account leans on suggestive setups for bait; the transferable learning is the serial structure and everyday-premise hook, not the titillation angle.*

## Format rules observed

**Caption structure** (consistent across the winners):
- Opens with an emoji hook — 😱 is the dominant one
- States a relatable premise as a question ("agar aap bhi roz momos khaate hain...")
- Ends with an **explicit engagement ask** — a question to answer in comments, or "Part 2 ke liye like karo", or "dosto ke saath share karna mat bhoolna"
- Hindi in **Devanagari script**, not roman Hinglish — worth noting, our current output is roman
- Hashtags: `#viralreels #trendingreels #explorepage #foryou` + 1-2 topic-specific

**On-screen text:** large Hindi text overlay at the **top** of frame (Reel 4), or bold overlay mid-frame (Reel 2). Emoji embedded in the overlay text itself.

**Fiction disclaimer:** `shadow_files0` labels every part *"This is Fictional story"* — cheap protection against misinformation complaints. We should copy this habit.

**Branding:** `aihealthstudio764` puts a logo watermark bottom-right on every frame — builds channel recall as the reel gets reshared.

**Visual quality** (the thing Manan specifically flagged): the AI art is genuinely high-grade —
- Reel 1: photoreal 3D render, dramatic warm rim-lighting, expressive anthropomorphic character, heavy detail in the environment
- Reels 6-8: a *consistent* illustrated/comic art style held across all parts — same palette, same line weight, cinematic night lighting, in-frame dialogue bubbles
- Reel 4: warm, cozy, near-photoreal domestic scene — lighting does the emotional work

The consistency *within a series* is the hard part and the differentiator. That's exactly what a character reference image + fixed style prompt is for.

## What to apply to our pipeline

1. **Build multi-part series generation** — 1 story → N parts, each with its own hook + cliffhanger + "Part N+1" CTA. Highest priority.
2. **Caption/description generator** — emoji hook, relatable question, explicit engagement ask, Devanagari Hindi, standard hashtag block.
3. **Fixed art-style prompt per series** so all parts look like one show (not N unrelated videos).
4. **On-screen Hindi text overlay** at top of frame, not just bottom captions.
5. **Watermark/logo** baked into every frame.
6. **"Fictional story" disclaimer** on story content (pairs with the AI-disclosure label we already render).
7. Prioritise topic buckets 1, 3, 4, 5 (anthropomorphic health, nostalgia, ironic humour, bhakti) — all high-performing and zero ban risk.

## Honest caveats

- Reel 3 (900K, the biggest) is **real footage**, not AI — a reminder that AI-generated content isn't automatically the winning format; the *idea* carried it.
- Reel 5 (bhakti) flopped at 6 likes with correct multi-part structure — format is necessary, not sufficient.
- `realistic_crime` and `shadow_files0` use sexual bait (`#sexygirl` hashtags, suggestive scenario framing). Their *structural* lessons transfer; that bait angle carries real platform-ban risk and is not part of what we build.
