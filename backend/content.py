"""Game content generation: Gemini when a key is present, local fallback otherwise."""
import os
import json
import base64
import random

import httpx

from .artwork import fetch_image_bytes

GEMINI_PROMPT = """You are writing content for a browser party game about art interpretation.

Look at the artwork and return ONLY valid JSON.

Generate:
1. curator_notes: 4 short private notes for the Real Curator. These must be useful but not copy-pasteable.
2. ai_statement: one polished AI-style art interpretation. It should sound slightly too smooth but still believable.
3. mood_words: 5 simple mood words.
4. visual_anchors: 5 visible details that players may notice.
5. exhibition_title: a short fictional exhibition title.
6. critic_review: a short funny review for the reveal screen.

Rules:
- Do not mention the artist name.
- Do not mention the real artwork title.
- Do not use overly academic language.
- Keep language human and understandable.
- Avoid unsafe or explicit content.
- Keep all outputs short.
- Return valid JSON only.

JSON schema:
{
  "curator_notes": ["...", "...", "...", "..."],
  "ai_statement": "...",
  "mood_words": ["...", "...", "...", "...", "..."],
  "visual_anchors": ["...", "...", "...", "...", "..."],
  "exhibition_title": "...",
  "critic_review": "..."
}"""


def _gemini_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def generate_artwork_game_content(artwork: dict) -> dict:
    """Return structured game content for an artwork. Uses Gemini if available, else fallback."""
    key = _gemini_key()
    if key:
        try:
            content = _gemini_generate(artwork, key)
            if content:
                return _validate(content, artwork)
        except Exception:
            pass
    return _fallback_content(artwork)


def _gemini_generate(artwork: dict, key: str) -> dict:
    parts = [{"text": GEMINI_PROMPT}]

    img = fetch_image_bytes(artwork.get("image_url", ""))
    if img:
        mime, raw = img
        parts.append({
            "inline_data": {
                "mime_type": mime,
                "data": base64.b64encode(raw).decode("ascii"),
            }
        })
    else:
        parts.append({"text": (
            "No image is available. Invent plausible generic content for an "
            "abstract painting with muted tones."
        )})

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash:generateContent"
    )
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"},
    }
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, params={"key": key}, json=body)
        resp.raise_for_status()
        data = resp.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


def _validate(content: dict, artwork: dict) -> dict:
    """Ensure the content has every field with sane lengths; backfill from fallback if not."""
    fb = _fallback_content(artwork)

    def as_list(v, n, default):
        if isinstance(v, list) and len(v) >= n:
            return [str(x).strip()[:140] for x in v[:n]]
        return default

    return {
        "curator_notes": as_list(content.get("curator_notes"), 4, fb["curator_notes"]),
        "ai_statement": (str(content.get("ai_statement") or "").strip()[:240]
                         or fb["ai_statement"]),
        "mood_words": as_list(content.get("mood_words"), 5, fb["mood_words"]),
        "visual_anchors": as_list(content.get("visual_anchors"), 5, fb["visual_anchors"]),
        "exhibition_title": (str(content.get("exhibition_title") or "").strip()[:80]
                             or fb["exhibition_title"]),
        "critic_review": (str(content.get("critic_review") or "").strip()[:240]
                          or fb["critic_review"]),
        "source": "gemini",
    }


# --- Local fallback generator -------------------------------------------------

THEMES = ["memory", "loneliness", "silence", "movement", "conflict",
          "childhood", "distance", "light", "ritual", "waiting"]
MOODS = ["quiet", "tense", "warm", "cold", "dreamlike", "fragile",
         "mysterious", "nostalgic"]
SYMBOLS = ["light", "shadow", "space", "color", "gesture", "stillness",
           "rhythm", "contrast"]

_ANCHORS = ["a soft edge", "a pale shape", "a darker corner", "a single line",
            "a warm patch", "an empty space", "a leaning form", "a faint horizon",
            "a small bright spot", "a heavy shadow"]

_TITLES = ["Echoes of {t}", "Notes on {t}", "The Weight of {t}", "After the {t}",
           "{t}, Held Still", "Studies in {t}"]

_REVIEWS = [
    "Bold, brave, and possibly painted during a nap. Four stars.",
    "I felt seen. Then I felt judged. Mostly judged.",
    "A triumph of vibes over evidence. The gallery wept softly.",
    "Confusing in the way only true art and bad WiFi can be.",
    "It whispered to me. It said 'good luck'.",
]


def _fallback_content(artwork: dict) -> dict:
    rng = random.Random(hash(str(artwork.get("id", ""))) & 0xFFFFFFFF)
    theme = rng.choice(THEMES)
    theme2 = rng.choice([t for t in THEMES if t != theme])
    moods = rng.sample(MOODS, 5)
    syms = rng.sample(SYMBOLS, 3)
    anchors = rng.sample(_ANCHORS, 5)

    notes = [
        f"The work circles the idea of {theme}.",
        f"Pay attention to how {syms[0]} carries the eye across the frame.",
        f"There is a tension between {syms[1]} and {syms[2]}.",
        f"The intended feeling is something close to {moods[0]} {theme2}.",
    ]
    ai_statement = (
        f"This piece masterfully interrogates {theme} through a delicate dialogue "
        f"of {syms[0]} and {syms[1]}, inviting the viewer into a {moods[1]} space "
        f"where meaning gently dissolves."
    )
    title = rng.choice(_TITLES).format(t=theme.capitalize())
    review = rng.choice(_REVIEWS)

    return {
        "curator_notes": notes,
        "ai_statement": ai_statement,
        "mood_words": moods,
        "visual_anchors": anchors,
        "exhibition_title": title,
        "critic_review": review,
        "source": "fallback",
    }
