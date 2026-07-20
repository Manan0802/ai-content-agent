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

## Account-level data (profiles checked live)

| Account | Posts | Followers | Bio / niche |
|---|---|---|---|
| `realistic_crime` | **40** | **107K** | "AI Creator \| Ghibli Visuals ✨" — crime serials |
| `aihealthstudio764` | **32** | **80K** | "AI Talking Foods & Organs · Funny Health Stories in Hindi" |
| `shadow_files0` | **26** | **11K** | "Thriller • Suspense • Horror · Dark Stories & Hidden Secrets · Animated Short Stories" (also runs YouTube @theshadowfiles001) |

**This is the headline finding.** All three are low-post-count accounts — 26 to 40 posts — sitting on 11K–107K followers. None of them has a back catalogue of hundreds of videos. A consistent daily output for one month puts you at their post count. The barrier is *quality and format discipline*, not volume or age.

Also note: all three follow **0 accounts** — pure content plays, no engagement-farming.

## The winning visual formula (aihealthstudio764 — the most replicable)

Their entire grid runs one repeatable template:

- **Premise:** an everyday Indian habit is put on trial — momos/chowmein, gas, beedi, hair gel, chai-pakode, phone addiction.
- **Cast:** anthropomorphic 3D characters — brain, stomach, heart, liver, plus the "villain" product (cigarette, hair-gel bottle, momo) — all with big expressive angry/scared faces, Pixar-grade render.
- **Recurring narrative device: a COURTROOM.** "बिड़ी VS पोटी — कौन दोषी?" and "रोज़-रोज़ जेल लगाते हो? बाल क्यों गिर रहे हैं?" both stage the brain as a judge in a wig, with the offending products as defendants. It's a template you can refill infinitely with new topics.
- **Text:** huge Devanagari Hindi at the **top** of frame — yellow/white/red, thick black stroke, always a **question**.
- **Lighting:** dramatic warm/red, high contrast, cinematic.
- **Branding:** "AI Health Studio" painted *inside the scene* (on the judge's bench) — native branding that survives resharing.

`shadow_files0` runs the same discipline for thriller: one consistent illustrated art style, the *same two protagonists* across every part, night/car/forest settings, Hindi dialogue in speech bubbles.

The common thread is **style consistency across the whole catalogue** — every post looks like it came from the same studio. That is exactly what a locked style prompt + character reference gives us.

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

## ⭐ The most important data: view counts per topic (aihealthstudio764, 12 reels)

Pulled from their Reels tab, which exposes per-reel view counts. Same account, same art style, same format — **only the topic changes**. So this isolates topic choice as the variable.

| Topic | Views |
|---|---|
| 😱 रोज़-रोज़ मोमोज़-चाउमीन? | **8.6M** |
| बिड़ी VS पोटी — कौन दोषी? | **7.1M** |
| पेशाब की नली में पथरी | **5.1M** |
| क्या आप भी GAS से परेशान हैं? | **4.8M** |
| क्या तुम भी रात में mobile चलाते हो? | **1M** |
| मालिक का BREAKUP हो गया | 162k |
| मिलावटी खाना — शरीर के अंदर क्या होता है? | 131k |
| (organ factory scene) | 86.2k |
| रोज-रोज TEEKHE MOMOS | 35.4k |
| बारिश में चाय पकोड़े | 30.9k |
| रोज़ जेल लगाते हो? बाल क्यों गिर रहे? | 25.7k |
| मुँह में बीड़ी की बंस? | **6,992** |

### What this actually tells us

**1. It is a hit-driven business, not a steady one.** Five reels did 1M–8.6M. The other seven did 7k–162k. Those 5 hits built the entire 80K following. Expect most videos to do modest numbers — the strategy has to be *volume of consistent-quality attempts*, because a small number of them carry everything. This is the single most important expectation to set.

**2. Topic beats execution.** Identical art style, identical format, identical account — and the spread is 6,992 vs 8,600,000. A **1,200x** difference driven purely by topic choice. Getting the graphics right is necessary but nowhere near sufficient.

**3. The mega-hits share one exact formula:**

> **A habit almost EVERY Indian has  +  a scary bodily consequence  +  anthropomorphic character drama**

- मोमोज़/चाउमीन — everyone eats it
- GAS — everyone gets it
- पथरी (kidney stone) — everyone fears it
- रात में मोबाइल — everyone does it
- बीड़ी vs पोटी — universal + shock/toilet humour

**4. The flops are all "narrow habit" topics:**
- बीड़ी की बंस (6,992) — only smokers care
- हेयर जेल (25.7k) — only gel users
- चाय पकोड़े (30.9k) — nostalgic but has **no fear hook**, nothing to be scared of

The winning emotional trigger is *"oh no, I do that"* — self-recognition plus a threat. Nostalgia alone (चाय पकोड़े) underperforms in this niche by ~200x compared to fear-based topics.

**Topic selection rule for our `idea_generator`:** score every candidate on (a) *what % of Indians do this daily?* and (b) *is there a visceral, scary consequence?* Only generate when both are high. This is directly encodable as a scoring prompt.

## Ready-to-use topic list (generated from the observed formula)

**Bucket A — "Body on trial" (aihealthstudio764 template, courtroom device):**
1. मोमोज़ vs चाउमीन — पेट का फैसला
2. बीड़ी vs पोटी — कौन दोषी?
3. रोज़ जेल लगाते हो? बाल क्यों गिर रहे हैं?
4. चाय खाली पेट — दिल की शिकायत
5. कोल्ड ड्रिंक vs दांत — 20 साल की सज़ा
6. रात 2 बजे मोबाइल — आँखों का मुकदमा
7. मैदा vs आटा — आंतों की अदालत
8. AC में सोना — गले की FIR
9. Protein powder — किडनी का बयान
10. Late night biryani — लिवर का गुस्सा

**Bucket B — Nostalgia (ai_reels_hub01 template):**
11. बारिश + कार्टून + मम्मी के पकोड़े
12. गर्मी की छुट्टी — नानी का घर
13. स्कूल की आखिरी बेंच
14. 90s का टीवी — रविवार सुबह
15. पापा की साइकिल पर पहली सवारी

**Bucket C — Thriller serial (shadow_files0 template, 5-6 parts):**
16. "डिलीवरी" — रात 9:22 की घंटी
17. "आखिरी बस" — सुनसान सड़क
18. "किरायेदार" — ऊपर वाला कमरा
19. "पुराना फोन" — जो खुद डायल करता है
20. "शादी का एल्बम" — एक चेहरा गायब

**Bucket D — Bhakti / mythology mystery (needs stronger execution than the reference):**
21. जगन्नाथ रथ यात्रा के 9 रहस्य
22. केदारनाथ — 2013 में मंदिर कैसे बचा
23. शनि देव — साढ़ेसाती का सच
24. हनुमान जी आज भी जीवित हैं?
25. सोमनाथ मंदिर — 17 बार लूटा गया

**Bucket E — Ironic everyday humour (krjha176 template — the 900K one):**
26. "Five star dinner" — गाँव की थाली
27. "Home gym" — खेत का काम
28. "Luxury AC" — पेड़ की छाँव

## Honest caveats

- Reel 3 (900K, the biggest) is **real footage**, not AI — a reminder that AI-generated content isn't automatically the winning format; the *idea* carried it.
- Reel 5 (bhakti) flopped at 6 likes with correct multi-part structure — format is necessary, not sufficient.
- `realistic_crime` and `shadow_files0` use sexual bait (`#sexygirl` hashtags, suggestive scenario framing). Their *structural* lessons transfer; that bait angle carries real platform-ban risk and is not part of what we build.
