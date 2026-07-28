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


@dataclass(frozen=True)
class CaptionConfig:
    follow_cta: bool = True
    share_cta: bool = True
    comment_cta: bool = True
    comment_keyword: str = "🔥"


def _tags(script: dict) -> str:
    seen, out = set(), []
    for t in list(script.get("hashtags", []) or []) + ["#Shorts"]:
        tag = t if t.startswith("#") else f"#{t}"
        if tag.lower() not in seen:
            seen.add(tag.lower())
            out.append(tag)
    return " ".join(out)


def build_caption(script: dict, config: CaptionConfig | None = None,
                  part_number: int = 0, total_parts: int = 0,
                  youtube_url: str = "") -> str:
    cfg = config or CaptionConfig()
    tags = _tags(script)

    body = []
    hook = (script.get("hook") or script.get("title") or "").strip()
    if hook:
        body.append(f"😱 {hook}")

    ctas = []
    # Point at the part that is ALREADY posted (the previous one). On Part 1 there is nothing
    # to point at yet, so promise the next one instead of sending people to a dead end.
    if part_number > 1:
        ctas.append(f"👉 Part {part_number - 1} प्रोफाइल पर है — पहले वो देखो!")
    if total_parts and part_number < total_parts:
        ctas.append("👉 अगला पार्ट कल रात")
    if cfg.follow_cta:
        ctas.append("❤️ Follow करो ताकि अगला पार्ट मिस ना हो")
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
