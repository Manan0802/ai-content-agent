# Background music library

Music-mode formats (`montage_35s`, `serial_75s`) play a background track instead of a voiceover.
This is what the reference thriller accounts actually do — `shadow_files0`, `realistic_crime` and
`nighttales169` all transcribe to a song with no narration at all
(see `docs/superpowers/specs/2026-07-21-audio-analysis.md`).

## Default is SILENT — you probably don't need this folder

`BGM_MODE=silent` is the default. Music-mode videos render **with no audio track**, and you add
the song inside the Instagram / YouTube app when posting. That's deliberate: trending audio is a
real ranking signal and it **cannot be attached through the API** — only in the app. So the
pipeline hands you a silent video and you pick the trending sound yourself.

Set `BGM_MODE=baked` in `.env` only if you want music mixed in automatically (fully hands-off
posting, but no trending-audio boost). Everything below applies to that mode.

## How to fill this

Drop audio files (`.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`) into the mood folder that fits:

| Folder | Used for | Vibe |
|---|---|---|
| `dark/` | horror, crime, thriller | tense, moody, suspenseful |
| `emotional/` | nostalgia, motivation, family | warm, wistful, hopeful |
| `comedy/` | funny, light | playful, upbeat |
| `devotional/` | bhakti, mythology | sacred, uplifting |

One track per mood is enough to start; more tracks means more variety across series.

Every part of a single series gets the **same** track (selection is seeded by series id), which
is what makes a serial feel like one show.

## Where to get tracks

Use music you have the right to use — royalty-free libraries (Pixabay Music, Free Music Archive,
YouTube Audio Library) or tracks you own. Don't drop in copyrighted film/label music: YouTube will
issue a Content ID claim and Instagram will mute or block the video, which defeats the point.

## Note on Instagram trending audio

Instagram's *trending* audio can only be attached inside the Instagram app at upload time — the
Graph API cannot set it. So there are two paths, and both are supported:

1. **Bake music in** (default) — fully automated, works for YouTube Shorts too, but no trending-audio boost.
2. **Render silent** — set the series to skip BGM, upload manually in the IG app and pick a
   trending sound there. More reach on IG, but a manual step per video.

## Optional: generated music

`hyperframes-media` can generate BGM with Lyria, but it needs `google-genai` plus a Gemini API
key. If you add one later we can wire that in as an alternative to this folder — it isn't needed
for the folder approach to work.
