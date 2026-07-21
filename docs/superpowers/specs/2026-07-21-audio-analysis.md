# Audio Analysis — 15 Reels (2026-07-21)

**This is the first analysis in the project with actual audio.** All 15 reels downloaded via
`yt-dlp --cookies-from-browser "chrome:Profile 1"` (Manan logged in; the extension's Chrome
profile was `Default`, the logged-in one was `Profile 1` — that mismatch was the earlier blocker),
audio extracted with ffmpeg, transcribed with Groq `whisper-large-v3`.

Everything below is new information that captions and screenshots could not reveal.

## Measured durations (the real ones)

| Reel | Duration |
|---|---|
| `babysardar_punjabi` | **10.0s** |
| `krjha_fivestar` (900K likes) | **10.8s** |
| `aireels_barish` | 32.6s |
| `shadow_p1` | 33.5s |
| `chitrakatha_nostalgia` (1.7M likes) | **34.0s** |
| `shadow_p2` | 36.2s |
| `darkcrime` (1.3K likes) | 37.1s |
| `technoyash_food` | 49.9s |
| `aihealth_momos` (8.6M views) | **50.5s** |
| `r1_sheru` | 52.1s |
| `jagannath` | 63.0s |
| `nighttales_crime` | 63.0s |
| `highway_truck` | 66.4s |
| `realisticcrime_monty` | 90.0s |
| `desiitoons_ladakh` (453K likes) | **91.0s** |

**Correction to an earlier assumption.** The Phase-2 plan and the earlier research assumed
20–25s parts. The real range is **10s to 91s**, and the two biggest performers sit at opposite
ends: 10.8s (900K) and 91s (453K). There is no single winning length — length follows format:
- **Punchline/irony → 10s** (one joke, one reveal)
- **Emotional montage → ~34s**
- **Anthropomorphic drama / tutorial → ~50s**
- **Story serial → 60–91s**

Our `script_writer` should take target duration as an input driven by format, not hardcode one.

## Finding 1 — most of these are NOT narrated. They are *songs*.

Four reels transcribed to the **same devotional/karmic song lyrics**:

- `realisticcrime_monty`, `shadow_p1`, `shadow_p2` → *"कर्म की कोख ही जनम का द्वार है, यही संसार का सार है… नैन को मूंद के पाप करे"*
- `nighttales_crime` and `jagannath` → *"ये गुमराहों का रास्ता… जो एक राज है… ऐ रात इतना बता"*

So `shadow_files0` (the account Manan most wants to emulate) has **no voiceover at all** — it is
a **music track + on-screen text dialogue**. Same for `realistic_crime` and `nighttales169`.
`darkcrime` is also just a song fragment.

**This changes the build significantly.** For thriller/crime serials the model is:

> moody licensed/trending audio track + silent visuals + burned-in Hindi dialogue text

That is *cheaper and easier* than what we built — no TTS needed at all, and it sidesteps the
Kokoro Hinglish quality problem entirely for this genre. It also explains a comment on
`shadow_p2`: *"itna ghatiya sound na lagaya karo reel pr, sara maza kharab hojata hai"* — the
audio choice is doing heavy lifting and viewers notice when it's wrong.

**Implication:** `composition_writer` needs a **text-dialogue-over-music mode** (no per-scene
voiceover), alongside the existing narrated mode.

## Finding 2 — the 8.6M reel is a full multi-character voice drama

`aihealth_momos` is the single best-performing piece analysed (8.6M views), and the audio is
nothing like our current pipeline's single-narrator output. It is a **conversation between organs**:

> **Stomach:** "अरे यार, ये मोटी कितनी चौमिन और मोमोस खाती है रे…"
> **Small intestine:** "पेटू भाई, मैं अभी बहुत छोटी हूँ, इतना सारा खाना अकेले कैसे संभालू?"
> **Liver:** "अरे रुक जा, अब मत खा पागल लड़की… मेरे सारे फिल्टर भर चुके हैं, ये पाइप भी फटने लगा है"
> **Heart:** "मेरा काम तो धड़कने का है ना… जब ये गोलगप्पे खाती है… मेरी तो धड़कनें और बढ़ जाती हैं"
> **Closing (calm, direct address):** "सुनो लड़की, अगर ऐसे ही रोज़ बाहर का खाना खाती रही, तो पेट थक जाएगा, छोटी आंत परेशान हो जाएगी, लिवर पर ज़्यादा बोझ पड़ेगा… कभी-कभी खा लो, लेकिन रोज़-रोज़ नहीं। अपने शरीर की भी सुनो।"

Structure: **complaint → escalation → multiple characters piling on → calm moral payoff.**
Each organ has a distinct personality and speaks *about* the girl in third person, which is what
makes it funny rather than preachy. Colloquial, rude, affectionate register ("मोटी भैंस", "पागल लड़की").

**Implication:** we need **multi-voice dialogue**, not single narration. Kokoro has 12 voices —
assigning a different voice per organ/character is directly buildable and is the difference
between our current output and an 8.6M-view format.

## Finding 3 — the 900K reel is a 10-second two-line joke

`krjha_fivestar`, 10.8 seconds, entire script:

> **Daughter (on phone):** "मॉम, डेट के साथ डिनर कर रही हूँ, फाइव स्टार होटल में। घर पहुँच के बात करती हूँ।"
> **Mother:** "अरे ओ पापा की परी, जिस भंडारे में तुम खड़ी हो, उसी में पीछे वाली लाइन में मैं हूँ।"

Two lines. One setup, one reveal. 900K likes. This is the highest views-per-second of anything
analysed, and it needs no AI visuals at all — just the joke.

**Implication:** add a **"one-joke 10s" format** to the generator. Very cheap, very high ceiling.

## Finding 4 — regional language is real dialogue, not decoration

- `r1_sheru` is **Haryanvi throughout**: "कालू, मन्ने कुछ दिन गरीब बनके जीणा से", "जैसा तु कहे शेरू भाई",
  "तेरे गैल बैठके मन्ने घणी खुशी मिले से", ending on **"अब असली कहाणी शुरू होगी"** — an explicit
  hook into the next part.
- `desiitoons_ladakh` is Haryanvi road-trip banter: "गाड़ी साइड में रोक लो, एक कड़क चाय पीवेंगे",
  "फेर तो असली रोड ट्रिप का मज़ा आवेगा".
- `babysardar_punjabi` is a 10-second Punjabi two-liner: "मैं क्यूट आं?" / "बिल भर दे, होर क्यूट लगेंगी।"

These aren't Hindi with a regional word sprinkled in — they're written in the dialect. That's
part of why the comment sections come back in the same language.

**Implication:** language should be a first-class series parameter (`hindi | haryanvi | punjabi`),
affecting the script prompt, not just a label.

## Finding 5 — the tutorial reel states the business model out loud

`technoyash_food` (72.7K comments) literally explains the whole economy in its own script:

> "Instagram पर ऐसी miniature cooking वीडियोस पर **millions में views** आते हैं, और लोग इनसे
> **लाखों में कमाई** करते हैं… ये सब फोन से AI की help से **2 minute** में बना सकते हो।"

Then the exact funnel: Google Gemini → paste prompt → run → for other dishes, take the prompt to
ChatGPT → "make this prompt for making samosa" → regenerate → repeat. And the CTA:

> "अगर आपको भी ये prompt चाहिए तो **जल्दी से मुझे फॉलो करो**, इस वीडियो को **तीन दोस्तों को शेयर** कर दो,
> **कमेंट में कोई भी emoji** send कर देना, मैं आपकी DM में directly send कर दूँगा।"

Three asks stacked: **follow + share to 3 friends + comment an emoji**. That's engineered
engagement, and it produced more comments than likes.

## Finding 6 — the nostalgia 1.7M reel is a *song*, one line of speech

`chitrakatha_nostalgia` (1.7M likes, 34s) transcribes to essentially one line over music:

> "ये जीवन… तब बिजली कम आती थी, लेकिन खुशियाँ भरपूर होती थीं"

No narration, no dialogue. Music + visuals + one nostalgic line. The emotional weight is carried
entirely by the imagery and the track.

## Consolidated build implications

1. **Two audio modes, not one.**
   - *Narrated mode* (health/explainer): multi-voice TTS dialogue.
   - *Music mode* (thriller/nostalgia/crime): background track + burned-in text dialogue, **no TTS**.
   Music mode is what `shadow_files0` uses — the account Manan most wants to match.
2. **Multi-voice dialogue** — assign distinct Kokoro voices per character. This is the core of the
   8.6M format and is buildable today.
3. **Duration by format** — 10s joke / 34s montage / 50s drama / 60–91s serial. Not one fixed length.
4. **Language as a series parameter** — Hindi, Haryanvi, Punjabi.
5. **Engagement CTA block** in captions — follow + share-to-3 + comment-an-emoji, plus a YouTube line.
6. **Explicit next-part hook in the script itself** — `r1_sheru` ends on "अब असली कहाणी शुरू होगी",
   not just a caption CTA. The cliffhanger belongs in the dialogue.

## Method note (so this is repeatable)

```bash
yt-dlp --cookies-from-browser "chrome:Profile 1" -o "name.%(ext)s" "<reel-url>"
ffmpeg -i name.mp4 -vn -ac 1 -ar 16000 -b:a 64k name.mp3
curl -X POST https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F file=@name.mp3 -F model=whisper-large-v3 -F response_format=text
```
Whisper's Devanagari transcription of Haryanvi/Punjabi is imperfect (some words garbled) but
easily good enough to read structure, register and dialogue count.
