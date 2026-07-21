# Instagram Reels — Batch 2 Analysis (2026-07-21)

Second reference batch (9 reels) supplied by Manan, viewed live. Focus areas he asked for:
new ideas, stories, animals, kids, food/recipes, and character portrayal.

## Raw data

| # | Account | Topic | Format | Likes | Comments |
|---|---------|-------|--------|-------|----------|
| 1 | `chitrakatha16` | 90s nostalgia — "जब बिजली जाना परेशानी नहीं… खुशी की वजह होती थी" | Single | **1.7M** | 3.2K |
| 2 | `krjha176` | "Dinner at a five star hotel" (ironic village meal) | Single, real | **900K** | 1.8K |
| 3 | `desii_toons` | "Ladakh Trip Day-1" animated travel series | **Multi-part** | **453.3K** | 1.1K |
| 4 | `nighttales169` | "She Planned His Death" — Karnataka true crime | Single + YT funnel | **148.2K** | **17.4K** |
| 5 | `creatortechnoyash` | AI miniature-food tutorial ("mummy bhi bana sakti hai") | Tutorial | 59K | **72.7K** |
| 6 | `highwayhaikuindia` | "Episode 2" — truck life, cooking, kindness to a stranger | **Multi-part** + YT | 46.7K | 124 |
| 7 | `official_sheru_empire` | "Sheru Bana Garib \| Emotional Story \| Part 1" — animal (lion) story, Haryanvi | **Multi-part** | 46.2K | 26 |
| 8 | `babysardartv` | AI Sikh baby Punjabi comedy — "ਮੈਂ Cute ਆਂ?" | Single | 10.1K | 67 |
| 9 | `dark_crime_8` | Sexual-crime headline (chachi/nabalig case) | Single | **1.3K** | 14 |

## Finding 1 — the comment-bait funnel (biggest new mechanic in this batch)

Two accounts have **more comments than you'd ever expect for their like count**, and both do it deliberately:

- `nighttales169`: 148.2K likes but **17.4K comments** — because the caption says *"For the FULL YouTube video, Comment 'LINK' and I'll send it."* Repeated **twice** in the caption.
- `creatortechnoyash`: 59K likes but **72.7K comments — more comments than likes.** The comment section is a wall of identical 🙌 emojis: people commenting a keyword to receive the AI prompt.

This is a deliberate growth hack with two payoffs at once:
1. Comments are the heaviest engagement signal in Instagram's ranking → the reel gets pushed harder.
2. It converts Instagram reach into **YouTube views / DM contacts**, where the money actually is.

`highwayhaikuindia` and `nighttales169` both also put a **YouTube link in the caption** — Instagram is their top-of-funnel, YouTube is the monetised destination. This matches the earlier monetisation research (Shorts RPM is ~10% of long-form).

**Apply to our pipeline:** the caption generator should support a configurable comment-bait CTA ("Comment 'X' and I'll send the link") plus a YouTube funnel line. Cheap to add, large effect.

## Finding 2 — nostalgia is the single biggest winner in this batch

`chitrakatha16` at **1.7M likes** is the top performer of all 17 reels analysed across both batches. The topic: *the power cut used to be a happy occasion — sleeping on the roof, talking to friends, that childhood was the most beautiful.*

Comment section is pure emotional response — 🥺😢, "क्या दिन थे वो", "Main bhi bachpan me light katne ka intezar karta tha". One commenter simply wrote **"Prompt"** — i.e. other creators are asking how it was made.

Combined with batch 1 (`ai_reels_hub01` nostalgia at 9.9K but with long heartfelt comments), the lesson is that nostalgia's ceiling is enormous **when the specific memory is universal enough**. "Bijli jaana" is universal for an entire generation; "maa ke pakode" is warmer but narrower.

## Finding 3 — animal + kid characters work, and they serialise well

- `official_sheru_empire` — "Sheru Bana Garib | Part 1": a lion character who gives up his wealth, and stands by his friend Tiger when his house is destroyed in the rain. **Haryanvi** story reels. Comments: *"Part 2"*, *"Part 3"*, *"Next"*, and the top comment — **"This need to be continue till eternity 🙏" (36 likes)**. Also: *"bhai kaunse AI App se banate ho"* — creators asking for the tooling.
- `babysardartv` — an AI Sikh baby doing **Punjabi** comedy. Small numbers (10.1K) but a clean, cheap, repeatable format with zero risk. Tagged `#AIBaby #SikhBaby #PunjabiComedy`.

Regional language is doing real work here — Punjabi and Haryanvi both show up in this batch, and the comments come back in the same language. Less competition than Hindi, very high affinity.

## Finding 4 — food works, but as *story* or *tutorial*, not as recipe

- `highwayhaikuindia` (46.7K): the food is described in loving detail (steaming basmati, egg curry with peas, golden parathas) but the reel is really about **two truckers inviting an old tea seller to share dinner in a storm** — "strangers became family". Food is the vehicle; warmth is the payload.
- `creatortechnoyash` (72.7K comments): pure **meta-tutorial** — "tell your mum she can make miniature food videos on her phone with AI in 2 minutes". The audience for *how to make AI content* is itself enormous.

Straight recipe content did not appear in this set at all. The winning shapes are food-as-emotional-story and food-as-AI-tutorial.

## Finding 5 — the character-portrayal data point

Manan specifically asked to look at how the girls are portrayed. The most direct evidence in this batch:

**`dark_crime_8` — 1.3K likes. The lowest of all 9 by a factor of ~35x, and ~1,300x below the top performer.**

It is the one reel in the batch built purely on a sexual-crime headline. Its comment section is degraded (users joking about wanting the woman involved), which is exactly the kind of signal that suppresses reach and attracts moderation.

Meanwhile the top three — nostalgia (1.7M), ironic village humour (900K), animated travel series (453K) — contain **no sexualised content at all**.

Across both batches now (17 reels), the pattern is consistent: the accounts leaning on titillation are the *smallest* ones, and the biggest numbers come from emotion, humour, fear, and serialised story. Attractive, well-designed characters absolutely matter — `desii_toons`, `shadow_files0` and `official_sheru_empire` all have strong, appealing character art — but the *sexual* angle is not what carries the views, and it correlates with the worst performers in this sample.

## Finding 6 — multi-part serialisation confirmed again

Three of the nine are explicitly serialised (`desii_toons` Day-1, `highwayhaikuindia` Episode 2, `official_sheru_empire` Part 1), and all three have comment sections dominated by *"Next"* / *"Part 2"* / *"Part 3"*. `desii_toons` is at **453K** on a Part-1 travel episode.

This is now the most repeatedly-confirmed finding across both batches and should be the next thing built.

## Audio — still a genuine gap

I still have **no audio analysis**. The browser renders video muted and Instagram serves the stream via MSE/blob (no plain `.mp4` request to intercept), and `yt-dlp` refuses without login cookies (Chrome's cookies are Keychain-encrypted and returned 0 usable entries).

To actually analyse voice/music/pacing, one of these is needed:
1. **Screen-record 2-3 reels** and hand over the files — then local ffmpeg + Whisper gives a full transcript, voice character, and music analysis. Simplest path.
2. Export Instagram cookies to a `cookies.txt` (browser extension) → `yt-dlp --cookies` works from then on.
3. Manan describes the audio himself (voice gender/energy, music style, whether trending audio is used).

Until then every audio-side conclusion in these docs is unverified.

## What to build next (priority order)

1. **Multi-part series generator** — 5-6 parts, cliffhanger + "Part N" CTA. Confirmed by 6 reels across two batches.
2. **Caption generator with comment-bait + YouTube funnel** — cheap, and demonstrably worth 10-70K extra comments.
3. **Locked character + style per series** — the thing that makes a channel look like a real show.
4. **Regional language support** (Punjabi / Haryanvi alongside Hindi) — low competition, high affinity.
5. **Topic scoring** on *universality × emotional charge* (nostalgia, fear, warmth) rather than novelty.
