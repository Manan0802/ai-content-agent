"""Caption builder — the engagement machinery, not just a description.

Measured from the reference set (`docs/superpowers/specs/2026-07-21-reels-batch2-analysis.md`):

- `creatortechnoyash`: 59K likes but **72.7K comments** — more comments than likes — because the
  caption stacked three asks: follow me + share with 3 friends + comment any emoji and I'll DM it.
- `nighttales169`: 148K likes, **17.4K comments** — "Comment 'LINK' and I'll send the YouTube video",
  repeated twice.
- `realistic_crime`: "Part 2 ke liye 100 like kar dijiye" — the next part is the reward.

Comments are the heaviest engagement signal Instagram ranks on, and these asks also push traffic
to YouTube, where the money actually is (Shorts RPM is ~10% of long-form).
"""
from dataclasses import dataclass

IG_CAPTION_LIMIT = 2200
# Instagram caps hashtags at 5 (was 30). Mosseri: "hashtags are not a way to get more reach" —
# they categorise the post so it reaches the right viewers. Extras are wasted, so keep the most
# specific ones and drop the rest.
IG_MAX_HASHTAGS = 5


@dataclass(frozen=True)
class CaptionConfig:
    follow_cta: bool = True
    share_cta: bool = True
    comment_cta: bool = True
    comment_keyword: str = "🔥"
    # The hook emoji has to match the domain. 😱 sells a horror short and undercuts a drama —
    # the first thing a reader sees shouldn't promise the wrong feeling.
    hook_emoji: str = "😱"


def _tags(script: dict, platform: str = "instagram") -> str:
    # `#Shorts` tells YouTube to treat the upload as a Short. It does nothing on Instagram, where
    # hashtags are capped at 5 — so it would only burn one of five slots.
    raw = list(script.get("hashtags", []) or [])
    limit = IG_MAX_HASHTAGS if platform == "instagram" else None
    if platform == "youtube":
        raw = raw + ["#Shorts"]

    seen, out = set(), []
    for t in raw:
        tag = t if t.startswith("#") else f"#{t}"
        if tag.lower() in seen:
            continue
        seen.add(tag.lower())
        out.append(tag)
        if limit and len(out) == limit:
            break
    return " ".join(out)


def build_caption(script: dict, config: CaptionConfig | None = None,
                  part_number: int = 0, total_parts: int = 0,
                  youtube_url: str = "", platform: str = "instagram") -> str:
    cfg = config or CaptionConfig()
    tags = _tags(script, platform)

    body = []
    hook = (script.get("hook") or script.get("title") or "").strip()
    if hook:
        body.append(f"{cfg.hook_emoji} {hook}")

    ctas = []
    # Point at the part that is ALREADY posted (the previous one). On Part 1 there is nothing
    # to point at yet, so promise the next one instead of sending people to a dead end.
    if part_number > 1:
        ctas.append(f"👉 Part {part_number - 1} प्रोफाइल पर है — पहले वो देखो!")
    if total_parts and part_number < total_parts:
        ctas.append("👉 अगला पार्ट कल रात")
    if cfg.follow_cta:
        # A standalone has no next part, so promising one reads as a mistake to anyone who
        # checks the profile — and there is nothing there to keep them.
        ctas.append("❤️ Follow करो ताकि अगला पार्ट मिस ना हो" if total_parts
                    else "❤️ Follow करो — रोज़ नई कहानी")
    if cfg.share_cta:
        ctas.append("📲 3 दोस्तों को share करो")
    if cfg.comment_cta:
        ctas.append(f"💬 Comment में {cfg.comment_keyword} भेजो")
    if youtube_url:
        ctas.append(f"▶️ Full video: {youtube_url}")

    parts = [p for p in ["\n".join(body), "\n".join(ctas)] if p]
    caption = "\n\n".join(parts)

    # keep the hashtags — truncate the body if we're over Instagram's cap
    tail = f"\n\n{tags}"
    room = IG_CAPTION_LIMIT - len(tail)
    if len(caption) > room:
        caption = caption[:max(room - 1, 0)].rstrip() + "…"
    return caption + tail
