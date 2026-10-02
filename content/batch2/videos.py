# -*- coding: utf-8 -*-
"""The five videos of batch 2, as data — one place the generator and the assembler both read.

Prompt shape is the one that survived the earlier batch, plus one addition:

  "Vertical 9:16 portrait video, tall vertical frame."

The Sept 2026 Flow rebuild ignores the Agent-settings 9:16 default — a clip generated with the
default set to 9:16 still came back 1280x720 — so the orientation has to be stated in the prompt.

Everything else is the rules from `aica-format-rules` and `aica-handoff`:
one speaker per clip, English scaffolding with the dialogue in dialect, the character lock pasted
verbatim, static camera, and the no-subtitles line that stops Veo burning its own captions.
"""

TAIL = "Do not include closed captioning or auto-generated speech subtitles."
HEAD = "Vertical 9:16 portrait video, tall vertical frame. Static camera, medium shot."


def build(shot: dict, video: dict) -> str:
    lock = video["cast"][shot["lock"]]
    who = shot.get("pronoun", "He")
    return (
        f"{HEAD} {video['set']}. {lock}, {shot['action']}. "
        f"{who} is the only person in frame. "
        f"{who} says in {video['lang']}: \"{shot['line']}\" {TAIL}"
    )


VIDEOS = {
    "v1": {
        "title": "दोस्ती का हिसाब",
        "emoji": "💔", "hook": "जिस दोस्त की गाड्डी बिक गी थी… आज वा गाड्डी ढाबे पै आ खड़ी होई।",
        "hashtags": ["हरियाणवी", "दोस्ती", "EmotionalStory", "DesiKahani", "Haryanvi"], "niche": "drama", "slug": "dosti-ka-hisaab",
        "part": 2, "total_parts": 3, "lang": "Haryanvi",
        "set": "Inside a roadside Indian dhaba with wooden benches and Hindi signboards, "
               "warm golden afternoon light, 50mm lens",
        "cast": {
            # verbatim from Part 1 — a reworded lock is how a cast starts drifting
            "sheru": "A male lion head with a full golden mane on a human body, wearing a black "
                     "kurta and a thick gold chain",
            "kaalu": "A brown and white street dog head on a lean human body, wearing a faded "
                     "blue shirt and a dhaba apron",
        },
        "outro": ("के शेरू वा चाबी लेगा?", "PART 3 — कल रात"),
        "shots": [
            {"lock": "sheru", "line": "यो हॉर्न... मेरी गाड्डी का सै।",
             "action": "wiping down a wooden table with a cloth, he stops moving and raises his "
                       "head toward the road, his face tightening, NOT smiling"},
            {"lock": "kaalu", "line": "तू अंदर चाल जा। मैं देख लूँ सूं।",
             "action": "wiping his hands on a cloth and looking away, avoiding eye contact, "
                       "uneasy, NOT smiling"},
            {"lock": "sheru", "line": "यो तो मेरी ए गाड्डी सै।",
             "action": "standing at the dhaba entrance staring at a white sedan parked outside, "
                       "stunned, mouth slightly open, NOT smiling"},
            {"lock": "kaalu", "line": "मन्नै खरीदी। अपणी जमीन बेच के।",
             "action": "holding a single car key in his open palm, looking down at it, quiet and "
                       "ashamed, NOT smiling"},
            {"lock": "sheru", "line": "क्यूँ काळू? क्यूँ?",
             "action": "his eyes wet, voice breaking, hands hanging at his sides, NOT smiling"},
            {"lock": "kaalu", "line": "तेरी गाड्डी किसे और कै हाथ मैं ना जाणी चाहिए थी।",
             "action": "holding the car key out toward the camera, steady and calm, NOT smiling"},
        ],
    },

    "v2": {
        "title": "खून का सौदा",
        "emoji": "🔪", "hook": "दो लाख रुपये। एक रात का काम। अर एक नाम।",
        "hashtags": ["हरियाणवी", "crimestory", "suspense", "DesiKahani", "Haryanvi"], "niche": "crime", "slug": "khoon-ka-sauda",
        "part": 1, "total_parts": 4, "lang": "Haryanvi",
        "set": "Inside a dim village room at night, a single bare bulb hanging overhead, cracked "
               "plaster walls, cold hard shadows, 35mm lens",
        "cast": {
            "kaalia": "A black buffalo head with thick curved horns on a heavy human body, "
                      "wearing a white kurta and dark sunglasses",
            "birju": "A grey goat head with a short beard on a lean human body, wearing a torn "
                     "brown shirt",
        },
        "outro": ("कालिया नै कौण सा नाम लिया?", "PART 2 — कल रात"),
        "shots": [
            {"lock": "birju", "line": "मेरी छोरी की जान का सवाल सै।",
             "action": "sitting hunched on a low stool with his hands clasped, pleading, "
                       "desperate, NOT smiling"},
            {"lock": "kaalia", "line": "पैसा मिलैगा। पूरा।",
             "action": "leaning back in a wooden chair, utterly calm, unreadable behind the dark "
                       "sunglasses, NOT smiling"},
            {"lock": "birju", "line": "कितना?",
             "action": "leaning forward into the bulb light, hopeful and afraid at once, "
                       "NOT smiling"},
            {"lock": "kaalia", "line": "दो लाख। आज रात।",
             "action": "sliding a thick bundle of banknotes across a wooden table, deliberate and "
                       "slow, NOT smiling"},
            {"lock": "birju", "line": "बदले मैं के?",
             "action": "staring at the money without touching it, suspicion crossing his face, "
                       "NOT smiling"},
            {"lock": "kaalia", "line": "एक नाम। अर एक रात का काम।",
             "action": "leaning in close to the camera, lowering his voice, menacing, "
                       "NOT smiling"},
        ],
    },

    "v3": {
        "title": "सासु का WiFi",
        "emoji": "😂", "hook": "सासु नै WiFi का पासवर्ड बदल दिया… फेर बहू नै हिंट पढ़ लिया।",
        "hashtags": ["हरियाणवी", "HaryanviComedy", "SaasBahu", "DesiComedy", "Haryanvi"], "niche": "comedy", "slug": "sasu-ka-wifi",
        "part": 0, "total_parts": 0, "lang": "Haryanvi",
        "set": "Inside a Haryanvi village courtyard with a charpai and a hand pump, bright "
               "morning sunlight, 50mm lens",
        "cast": {
            "sasu": "An elderly grey cat head with sharp green eyes on a stout human body, "
                    "wearing a maroon saree and large gold earrings",
            "bahu": "A young brown rabbit head with long upright ears on a slim human body, "
                    "wearing a bright yellow salwar kameez",
        },
        "outro": ("थारी सासु का पासवर्ड के सै?", ""),
        "shots": [
            {"lock": "bahu", "pronoun": "She", "line": "मम्मी जी, WiFi का पासवर्ड बदल दिया के?",
             "action": "holding up a smartphone and frowning at it, annoyed"},
            {"lock": "sasu", "pronoun": "She", "line": "हाँ। अब घणा चलावै सै तू।",
             "action": "stirring a steel pot with a ladle, smug and unbothered, one eyebrow up"},
            {"lock": "bahu", "pronoun": "She", "line": "तो नया पासवर्ड बता दो ना।",
             "action": "putting both hands together in mock pleading, exasperated"},
            {"lock": "sasu", "pronoun": "She", "line": "ना बतावूँ। खुद सोच।",
             "action": "turning her face away with her chin lifted, deeply pleased with herself"},
            {"lock": "bahu", "pronoun": "She", "line": "हिंट मैं आपका ए नाम लिख्या सै, मम्मी जी।",
             "action": "reading her phone screen with a flat deadpan expression, one eyebrow "
                       "raised"},
        ],
    },

    "v4": {
        "title": "तेरा हिसाब",
        "emoji": "🔥", "hook": "तूने इस जन्म में चार हज़ार रोटियाँ फेंकी हैं। हिसाब तैयार है।",
        "hashtags": ["गरुड़पुराण", "यमराज", "BhaktiStory", "hindikahani", "DharmikKahani"], "niche": "mythology", "slug": "tera-hisaab",
        "part": 0, "total_parts": 0, "lang": "Hindi",
        "set": "Inside a vast dark stone court with tall pillars, floating embers in the air, "
               "cold blue light falling from above, heavy shadows, 35mm lens",
        "cast": {
            "chitragupt": "An owl head with large amber eyes on a human body, wearing deep blue "
                          "robes and holding a thick open ledger",
            "yamraj": "A black water buffalo head with enormous curved horns on a towering human "
                      "body, wearing dark red robes and a heavy gold crown",
        },
        "outro": ("आज थाली में कुछ छोड़ा था?", ""),
        "shots": [
            {"lock": "chitragupt", "line": "तेरा नाम आ गया है। बैठ।",
             "action": "opening a heavy ledger and looking directly into the camera, severe, "
                       "NOT smiling"},
            {"lock": "chitragupt", "line": "तूने इस जन्म में चार हज़ार रोटियाँ फेंकी हैं।",
             "action": "running one finger down a page of the ledger, reading aloud, flat and "
                       "certain, NOT smiling"},
            {"lock": "yamraj", "line": "गिनती सही है, चित्रगुप्त?",
             "action": "seated on a huge stone throne, turning his head slowly, immense and calm, "
                       "NOT smiling"},
            {"lock": "chitragupt", "line": "एक भी कम नहीं, महाराज।",
             "action": "closing the ledger with both hands, bowing his head slightly, "
                       "NOT smiling"},
            {"lock": "yamraj", "line": "अगले जन्म में तुझे भूख मिलेगी। रोटी नहीं।",
             "action": "leaning forward toward the camera, his amber eyes fixed on the viewer, "
                       "final and merciless, NOT smiling"},
        ],
    },

    "v5": {
        "title": "घर का वो कोना",
        "emoji": "😱", "hook": "नए घर का साउथ-वेस्ट कोना। जो पहले रहते थे, वो भी उधर ही सोते थे।",
        "hashtags": ["वास्तु", "VastuTips", "hindikahani", "DarawaniKahani", "HorrorStory"], "niche": "horror", "slug": "ghar-ka-wo-kona",
        "part": 0, "total_parts": 0, "lang": "Hindi",
        "set": "Inside a modern almost-empty apartment at night, one floor lamp, bare white "
               "walls, a tall dark window, cold shadows, 35mm lens",
        "cast": {
            # night + a single lamp on purpose: human faces drift between generations and darkness
            # hides the drift, which is the same reason तीसरा हाथ works
            "meera": "A young Indian woman with long straight black hair, wearing a fitted cream "
                     "crop top and high-waisted jeans, confident upright posture",
            "aunty": "An older Indian woman with grey hair tied in a bun, wearing a plain green "
                     "cotton saree and thin gold-rimmed glasses",
        },
        "outro": ("आप किस कोने में सोते हो?", ""),
        "shots": [
            {"lock": "meera", "pronoun": "She", "line": "आंटी, नया घर कैसा लगा आपको?",
             "action": "lifting a cardboard carton onto a table, relaxed and pleased, "
                       "warm expression"},
            {"lock": "aunty", "pronoun": "She", "line": "बाकी सब ठीक है। वो कोना कौन सा है?",
             "action": "staring past the camera at one dark corner of the room, not blinking, "
                       "NOT smiling"},
            {"lock": "meera", "pronoun": "She", "line": "साउथ-वेस्ट। वहीं मेरा बेडरूम है।",
             "action": "glancing over her shoulder toward the dark corner, still casual, "
                       "half-smiling"},
            {"lock": "aunty", "pronoun": "She", "line": "उधर मत सोना। जो पहले रहते थे, वो भी उधर ही सोते थे।",
             "action": "turning her head very slowly back toward the camera, flat and serious, "
                       "NOT smiling"},
            {"lock": "meera", "pronoun": "She", "line": "वो... वो कहाँ गए?",
             "action": "her smile gone, face pale in the lamp light, dread rising, NOT smiling"},
        ],
    },
}


if __name__ == "__main__":
    import sys
    key = sys.argv[1] if len(sys.argv) > 1 else None
    for k, v in VIDEOS.items():
        if key and k != key:
            continue
        print(f"\n===== {k}: {v['title']} ({v['niche']}, {v['lang']}, {len(v['shots'])} clips) =====")
        for i, s in enumerate(v["shots"], 1):
            print(f"\n--- {k} clip {i} ---")
            print(build(s, v))
