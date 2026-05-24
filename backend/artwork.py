"""Artwork fetching from the Art Institute of Chicago API with local SVG fallbacks."""
import random
import base64
import html

import httpx

ARTIC_API = "https://api.artic.edu/api/v1/artworks"
IIIF_PATTERN = "https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
FIELDS = "id,title,artist_title,date_display,image_id,is_public_domain"


def _build_image_url(image_id: str) -> str:
    return IIIF_PATTERN.format(image_id=image_id)


def get_random_artwork() -> dict:
    """Return a single public-domain artwork. Falls back to a local SVG piece on any failure."""
    try:
        page = random.randint(1, 60)
        with httpx.Client(timeout=6.0) as client:
            resp = client.get(
                ARTIC_API,
                params={"fields": FIELDS, "limit": 100, "page": page},
                headers={"AIC-User-Agent": "PromptGallery (hackathon demo)"},
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])

        candidates = [
            a for a in data
            if a.get("image_id") and a.get("is_public_domain")
        ]
        if not candidates:
            raise ValueError("no public-domain artworks with images on this page")

        art = random.choice(candidates)
        return {
            "id": str(art["id"]),
            "title": art.get("title") or "Untitled",
            "artist": art.get("artist_title") or "Unknown artist",
            "date": art.get("date_display") or "",
            "image_url": _build_image_url(art["image_id"]),
            "source": "Art Institute of Chicago",
            "is_public_domain": True,
        }
    except Exception:
        return _fallback_artwork()


# --- Local fallback: generated SVG artworks so the game always works offline ---

_PALETTES = [
    ["#1b2a4a", "#c9a227", "#e8e1d1", "#6b3f2b"],
    ["#0f1419", "#d4a017", "#7a8b8b", "#2c3e50"],
    ["#2b1a3d", "#e0c060", "#a05050", "#1a2530"],
    ["#10242b", "#cfa84e", "#8aa39b", "#3a2417"],
    ["#1a1a2e", "#d9b44a", "#b85c38", "#16213e"],
    ["#22223b", "#c9ada7", "#9a8c98", "#4a4e69"],
    ["#241b2f", "#e6b800", "#5d8aa8", "#2e1a47"],
    ["#0b132b", "#d4af37", "#5bc0be", "#3a506b"],
]

_FALLBACK_TITLES = [
    "Study in Quiet Light",
    "The Long Afternoon",
    "Figures Near Water",
    "Composition in Gold",
    "Interior with Window",
    "The Distant Shore",
    "Still Life, Late Hour",
    "Movement and Rest",
]

_FALLBACK_ARTISTS = [
    "Attributed to a 19th-century master",
    "Unknown hand",
    "From a private collection",
    "Anonymous, European school",
]


def _svg_artwork(seed: int) -> str:
    rng = random.Random(seed)
    palette = _PALETTES[seed % len(_PALETTES)]
    bg, accent, mid, deep = palette
    w, h = 843, 1000

    shapes = []
    shapes.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')
    # soft horizon / wash
    shapes.append(
        f'<rect x="0" y="{rng.randint(400,650)}" width="{w}" height="{h}" '
        f'fill="{deep}" opacity="0.55"/>'
    )
    # large organic forms
    for _ in range(rng.randint(4, 7)):
        cx, cy = rng.randint(0, w), rng.randint(0, h)
        r = rng.randint(60, 260)
        color = rng.choice([accent, mid, deep])
        shapes.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" '
            f'opacity="{rng.uniform(0.15, 0.5):.2f}"/>'
        )
    # gestural strokes
    for _ in range(rng.randint(5, 9)):
        x1, y1 = rng.randint(0, w), rng.randint(0, h)
        x2, y2 = rng.randint(0, w), rng.randint(0, h)
        shapes.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{accent}" stroke-width="{rng.randint(2,8)}" '
            f'opacity="{rng.uniform(0.2, 0.6):.2f}"/>'
        )
    # focal accent
    shapes.append(
        f'<circle cx="{rng.randint(250,600)}" cy="{rng.randint(300,600)}" '
        f'r="{rng.randint(30,80)}" fill="{accent}" opacity="0.85"/>'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">{"".join(shapes)}</svg>'
    )
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def _fallback_artwork() -> dict:
    seed = random.randint(0, len(_FALLBACK_TITLES) - 1)
    return {
        "id": f"fallback-{seed}",
        "title": _FALLBACK_TITLES[seed],
        "artist": random.choice(_FALLBACK_ARTISTS),
        "date": "date unknown",
        "image_url": _svg_artwork(seed + random.randint(0, 9999)),
        "source": "Prompt Gallery archive",
        "is_public_domain": True,
    }


def fetch_image_bytes(image_url: str):
    """Best-effort fetch of artwork bytes for vision models. Returns (mime, bytes) or None."""
    if not image_url or image_url.startswith("data:"):
        return None
    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.get(image_url)
            resp.raise_for_status()
            mime = resp.headers.get("content-type", "image/jpeg").split(";")[0]
            return mime, resp.content
    except Exception:
        return None
