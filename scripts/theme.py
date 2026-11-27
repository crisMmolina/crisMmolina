"""Shared palette and SVG helpers for the profile assets.

Palette: #2d0057 (deep), #7c3aed (violet), #a78bfa (lavender),
with #FFD700 / #34d399 kept as award accents.
"""
from html import escape

THEMES = {
    "dark": {
        "bg": "#0d0221",
        "bg2": "#1f0745",
        "surface": "#14052b",
        "border": "#2e1460",
        "text": "#f5f3ff",
        "muted": "#a99bd1",
        "accent": "#a78bfa",
        "accent2": "#7c3aed",
        "soft": "#c4b5fd",
        "grid": "#2a1356",
        "empty": "#1c0b3a",
        "levels": ["#3b1a78", "#5b21b6", "#7c3aed", "#a78bfa"],
        "gold": "#FFD700",
        "green": "#34d399",
        "icon": "#a78bfa",
    },
    "light": {
        "bg": "#faf7ff",
        "bg2": "#efe6ff",
        "surface": "#ffffff",
        "border": "#e4dafc",
        "text": "#2d0057",
        "muted": "#6b5b95",
        "accent": "#7c3aed",
        "accent2": "#a78bfa",
        "soft": "#8b5cf6",
        "grid": "#e6dcfb",
        "empty": "#efe9fb",
        "levels": ["#ddd0fb", "#c4b5fd", "#a78bfa", "#7c3aed"],
        "gold": "#b8860b",
        "green": "#059669",
        "icon": "#7c3aed",
    },
}

SANS = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

REDUCED_MOTION = (
    "@media (prefers-reduced-motion: reduce) {"
    " *, *::before, *::after { animation: none !important; } .motion { display: none; } }"
)


def esc(text: str) -> str:
    return escape(text, quote=True)


def text_width(text: str, size: float, mono: bool = False, bold: bool = False) -> float:
    """Rough width estimate; good enough to size chips and pills."""
    factor = 0.61 if mono else (0.58 if bold else 0.54)
    return len(text) * size * factor


def svg_doc(width: int, height: int, body: str, style: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title><style>{style}{REDUCED_MOTION}</style>{body}</svg>\n"
    )


def chip(x: float, y: float, label: str, t: dict, size: int = 15, fill=None, stroke=None, color=None) -> tuple[str, float]:
    """A rounded pill with mono text. Returns (svg, width)."""
    w = text_width(label, size, mono=True) + 28
    h = size + 16
    svg = (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h / 2}" '
        f'fill="{fill or t["surface"]}" stroke="{stroke or t["border"]}"/>'
        f'<text x="{x + 14:.1f}" y="{y + h / 2 + size * 0.36:.1f}" class="mono" '
        f'font-size="{size}" fill="{color or t["muted"]}">{esc(label)}</text>'
    )
    return svg, w


def write(path, content: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"wrote {path} ({len(content.encode()) / 1024:.1f} KB)")
