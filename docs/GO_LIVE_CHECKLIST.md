# Go-Live Checklist — everything needed to start posting

Status as of 2026-07-22. Split by what's **already working**, what **only you can do**, and what's
**optional**. Nothing here is a guess — each item says why it's needed and what breaks without it.

---

## ✅ Already working — nothing needed from you

| Piece | Status |
|---|---|
| Script + ideas (Groq, free tier) | ✅ key set, live-tested |
| Images (Pollinations, free, no key) | ✅ live-tested |
| Voice (Kokoro, local, free) | ✅ live-tested, 12 voices |
| Render (HyperFrames, local, free) | ✅ real MP4s produced |
| Series engine (N parts, cliffhangers, locked style) | ✅ live-tested |
| Captions + engagement CTAs | ✅ |
| Dashboard | ✅ `uvicorn dashboard.app:create_app --factory --port 8000` |
| AI-content disclosure | ✅ baked into every render |

**Current cost per video: ₹0.**

---

## 🔴 REQUIRED to start posting — only you can do these

### 1. Create the accounts (30 min)
- **YouTube channel** — decide the channel name/handle first, it's a pain to change later.
- **Instagram account** — must be a **Business** account (not Creator, not Personal) if you ever
  want API publishing; also needs to be linked to a Facebook Page. Even for manual posting,
  start it as Business so you don't have to migrate later.

Pick the name to match the content: the reference accounts that work are literal —
`aihealthstudio764`, `realistic_crime`, `shadow_files0`, `desii_toons`.

### 2. YouTube API access (~20 min, then a wait)
Needed for automatic uploads. Without it the pipeline still renders videos — you'd just upload
them by hand.

1. [Google Cloud Console](https://console.cloud.google.com) → new project → enable **YouTube Data API v3**
2. Create **OAuth 2.0 Client ID**, type **Desktop app**
3. Put them in `.env`:
   ```
   YOUTUBE_CLIENT_ID=...
   YOUTUBE_CLIENT_SECRET=...
   ```
4. Run once — it opens a browser, you approve, it writes the refresh token itself:
   ```
   python -m scripts.youtube_auth
   ```
5. **Apply for the quota audit the same day.** Default quota = ~6 uploads/day and Google's review
   takes weeks. Fine for testing, blocking once you scale.

### 3. Decide the channel identity (creative — only you)
- **Niche to start with.** Recommendation: pick **one** and go deep for 30 days. Based on the
  measured research, `drama_50s` health/"body on trial" has the best proven ceiling (8.6M views on
  a single reel) and zero ban risk. Thriller serials (`serial_75s`) are the other strong option.
- **Character look** — the recurring lead. Reference images and locked prompts are already in
  `assets/reference/` from our earlier session; pick the one you want as canon.
- **Channel handle + profile picture.**

---

## 🟡 Strongly recommended (not blocking, but a real quality jump)

### fal.ai key — the character-consistency fix (~₹50 per 3-part series)
This is the **single biggest remaining quality gap**. Right now character consistency is
text-prompt only, so faces drift between scenes. fal.ai FLUX.2 accepts a reference image and locks
the face — which is exactly what makes `shadow_files0` look like a real show.

- Sign up at [fal.ai](https://fal.ai), put `FAL_KEY=...` in `.env`, set `IMAGE_PROVIDER=fal`
- ~₹1-3 per image, so a 3-part series ≈ ₹30-90
- Keep `IMAGE_PROVIDER=pollinations` for testing and switch to fal for videos you'll actually post

**My honest recommendation:** get this before posting seriously. Free images are fine for testing
the machine; they are the weak point of the finished product.

---

## ⚪ Optional / later

| Item | When you'd want it |
|---|---|
| **Music tracks** in `assets/music/<mood>/` | Only if you set `BGM_MODE=baked`. Default is `silent` so you add trending audio in the app — which is better for reach anyway. |
| **Instagram Graph API** | Automatic IG posting. Needs Business account + Facebook Page + Meta app review (**2-4 weeks**). Manual posting works fine until then. |
| **Sarvam AI** (`₹1000` free credits) | Better Hinglish TTS than Kokoro. Only matters for narrated formats. |
| **Local GPU image gen** | Free unlimited images on the Mac, but a real setup project and quality likely *below* fal.ai. Only if volume gets large. |
| **Dashboard hosting** | To view it away from the laptop. Tunnel = free/instant, cloud = always-on but needs storage work. |

---

## 📅 Suggested first week

**Day 1** — accounts + YouTube API + pick niche/character.
**Day 2** — generate 5-10 videos, watch them yourself, tune prompts. Post nothing.
**Day 3** — post the 3 best manually, see what the platform does with them.
**Day 4-7** — one video/day, same niche, same character. Watch which topic shape lands.

Then decide: scale the winner, or change the niche.

### Reality check on money (from the earlier research, not optimism)
- YouTube ad revenue needs 1,000 subs + 4,000 watch-hours **or** 10M Shorts views/90 days — that's
  months away, and early videos earn ₹0 regardless of views.
- Shorts RPM in India is ₹5-30 per 1,000 views. Long-form is 10-30x higher.
- The reference accounts hit 80K-107K followers on **26-40 posts** — so volume isn't the barrier,
  consistency and topic choice are.

Treat the first month as learning what lands, not as income.

---

## What I still owe on the build

- Character-consistency wiring for fal.ai reference images (needs your key first)
- Async human-in-the-loop so approvals can happen from the dashboard/WhatsApp instead of the terminal
- Scheduler (Phase 5) for hands-off daily posting
- Instagram publishing once Meta approves the app
