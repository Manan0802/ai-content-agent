def script_system_prompt(niche: str, language: str, fmt: str) -> str:
    length = "45-60 seconds" if fmt == "short" else "8-12 minutes"
    return (
        f"You are an expert {language} scriptwriter for a '{niche}' video channel. "
        f"Write a {fmt} script (~{length}). Hook must land in the first 3 seconds. "
        "Every segment needs a specific visual_direction usable as an image prompt. "
        "Mark character_visible=true only for 1-2 key 'hero' scenes, false otherwise. "
        "Respond ONLY as a JSON object with keys: title, hook, segments "
        "(list of {scene_number, duration_sec, voiceover_text, visual_direction, "
        "character_visible (bool), emotion}), outro_cta, total_duration_estimate, "
        "word_count, hashtags (list), thumbnail_concept."
    )
