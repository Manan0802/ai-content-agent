"""Series prompts — one story split into N cliffhanger-linked parts.

Why this exists: across both reference batches, serialisation was the most repeatedly
confirmed win. `shadow_files0`'s DELIVERY series went 18.8K likes / 64 comments on Part 1 to
25.3K / 552 on Part 4 — later parts outperform the first because the audience becomes invested.
Their comment sections are literally "Next", "Part 2", "This need to be continue till eternity".

Two things make it work, and both are generated ONCE here and reused by every part:

1. `style_prompt` — a single locked art direction, so all parts look like one show.
2. `characters[].appearance` — a fixed physical description per character, so the same people
   recur. (Text-only consistency still drifts; reference-image conditioning would fix that
   properly — see the Phase 4 plan's caveat.)

And the cliffhanger goes INSIDE the dialogue, not just the caption: `r1_sheru` ends its part on
"अब असली कहाणी शुरू होगी".
"""
from modules.formats import get_format

_LANG_RULE = {
    "hindi": "Hindi in Devanagari script.",
    "hinglish": "Hinglish (Hindi-English mix), Hindi words in Devanagari.",
    "haryanvi": "HARYANVI dialect in Devanagari — real Haryanvi ('मन्ने', 'से', 'घणी'), not Hindi.",
    "punjabi": "PUNJABI in Gurmukhi script — real spoken Punjabi, not Hindi.",
}


def series_system_prompt(niche: str, language: str, format_name: str, parts: int) -> str:
    profile = get_format(format_name)
    lang_rule = _LANG_RULE.get(language, _LANG_RULE["hindi"])

    return (
        f"You are a show-runner for a '{niche}' short-form video series aimed at an Indian audience.\n\n"
        f"Break ONE story into exactly {parts} parts. Each part becomes a separate "
        f"~{profile.target_duration_sec:.0f} second vertical video ({profile.name}).\n\n"
        f"LANGUAGE: {language}. {lang_rule}\n\n"
        "SERIALISATION RULES:\n"
        f"- Part 1 must work standalone as a hook — assume most viewers see it first.\n"
        "- EVERY part must end on a cliffhanger: an unanswered question, a reveal cut short, or "
        "sudden danger. Write it as a line a character would actually say, not a caption.\n"
        "- Each following part must open by paying off the previous part's cliffhanger.\n"
        f"- The final part ({parts}) still ends on a hook — leave room for a sequel.\n\n"
        "CONSISTENCY (this is what makes it look like a real show):\n"
        "- style_prompt: ONE art-direction sentence reused for every image in every part "
        "(medium, lighting, mood, colour). Keep it specific and repeatable.\n"
        "- characters[].appearance: a fixed physical description per character (age, build, hair, "
        "clothing, distinguishing features) that will be pasted into every image prompt so the "
        "same person recurs across all parts. Give each character a signature visual detail.\n\n"
        "Respond ONLY as a JSON object with keys: series_title, logline, style_prompt, "
        "characters (list of {id, name, voice_hint, appearance}), parts (list of "
        "{part_number, beat_summary, cliffhanger})."
    )
