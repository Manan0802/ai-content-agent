"""Script prompts — format-aware and language-aware.

Rules encoded here come from analysing 17 real reels (see
`docs/superpowers/specs/2026-07-21-audio-analysis.md` and the two reels-reference specs):

- the hook must be a question, a bold claim, or dropping mid-action — never scene-setting
- dialogue lines get burned on screen, so they must be short punchy clauses
- Hindi/Haryanvi/Punjabi are written in Devanagari/Gurmukhi *in dialect*, not roman Hinglish
- music-mode formats have NO voiceover at all — the dialogue is on-screen text only
- every part of a serial ends on a cliffhanger spoken *inside the dialogue*
  (`r1_sheru` ends on "अब असली कहाणी शुरू होगी", not just a caption CTA)
"""
from modules.formats import FormatProfile, get_format

_SCRIPT_STYLE = {
    "hindi": "Write all dialogue in Hindi using Devanagari script. Conversational, everyday Hindi.",
    "hinglish": "Write dialogue in Hinglish (Hindi-English mix) using Devanagari for the Hindi words.",
    "haryanvi": (
        "Write all dialogue in HARYANVI dialect using Devanagari script — real Haryanvi, not Hindi. "
        "Use forms like 'मन्ने', 'से', 'घणी', 'तेरे गैल', 'ठीक से'."
    ),
    "punjabi": (
        "Write all dialogue in PUNJABI using Gurmukhi script — real spoken Punjabi, not Hindi."
    ),
}


def script_system_prompt(niche: str, language: str,
                         profile: FormatProfile | None = None,
                         fmt: str | None = None) -> str:
    """Build the script system prompt.

    `profile` is the format profile (preferred). `fmt` is the legacy "short"/"long" arg kept
    so existing Phase-1 callers keep working.
    """
    if profile is None:
        profile = get_format("drama_50s") if fmt != "long" else get_format("serial_75s")

    lo, hi = profile.segment_range
    lang_rule = _SCRIPT_STYLE.get(language, _SCRIPT_STYLE["hindi"])

    if profile.audio_mode == "music":
        audio_rule = (
            "AUDIO MODE: music. There is NO voiceover — a background music track plays and the "
            "dialogue is burned on screen as text. So every 'dialogue' line must be SHORT enough "
            "to read comfortably on a phone screen (max ~10 words). Do NOT write narration. "
            "Set characters to an empty list."
        )
        char_rule = "Use an empty characters list."
    else:
        audio_rule = (
            f"AUDIO MODE: narrated. Each line is spoken aloud by a distinct character voice. "
            f"Use at most {profile.max_characters} characters, each with a clear personality."
        )
        char_rule = (
            f"Define {min(2, profile.max_characters)}-{profile.max_characters} characters. "
            "Each needs id (lowercase ascii), name (in the script language), and voice_hint "
            "(e.g. 'gruff male', 'young female', 'tired old male'). Every segment's 'speaker' "
            "must be one of those character ids."
        )

    return (
        f"You are an expert short-form video scriptwriter for a '{niche}' channel aimed at an "
        f"Indian audience.\n\n"
        f"FORMAT: {profile.name} — total video length about {profile.target_duration_sec:.0f} "
        f"seconds, split into {lo}-{hi} segments. {profile.description}\n\n"
        f"{audio_rule}\n\n"
        f"LANGUAGE: {language}. {lang_rule}\n\n"
        "HOOK RULE: the first segment must open with a direct question to the viewer, a bold "
        "shocking claim, or drop straight into the middle of the action. Never open with "
        "scene-setting or introductions.\n"
        "DIALOGUE RULE: short punchy clauses, roughly 8-12 words per line — this text is burned "
        "on screen verbatim.\n"
        "CLIFFHANGER RULE: the final segment's dialogue must end on an unresolved hook that makes "
        "the viewer want the next part.\n"
        f"CHARACTERS: {char_rule}\n"
        "VISUALS: every segment needs a specific, vivid visual_direction usable directly as an "
        "image-generation prompt. Mark character_visible=true only for 1-2 key hero scenes.\n\n"
        "Respond ONLY as a JSON object with keys: title, hook, characters (list of "
        "{id, name, voice_hint}), segments (list of {scene_number, duration_sec, speaker, "
        "dialogue, visual_direction, character_visible, emotion}), cliffhanger, outro_cta, "
        "total_duration_estimate, hashtags (list), thumbnail_concept."
    )
