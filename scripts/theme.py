"""Shared palette and SVG helpers for the profile assets.

Palette: emerald green, #022c22 (deep), #059669 (main), #34d399 (accent),
with #FFD700 for first places and violet (#a78bfa / #7c3aed) as the contrast accent.
"""
from html import escape

THEMES = {
    "dark": {
        "bg": "#02140f",
        "bg2": "#053b2c",
        "surface": "#04221a",
        "border": "#0d4a37",
        "text": "#ecfdf5",
        "muted": "#8fc2ae",
        "accent": "#34d399",
        "accent2": "#059669",
        "soft": "#6ee7b7",
        "grid": "#0b3d2e",
        "empty": "#062e22",
        "levels": ["#065f46", "#047857", "#059669", "#34d399"],
        "gold": "#FFD700",
        "alt": "#a78bfa",
        "icon": "#34d399",
    },
    "light": {
        "bg": "#f5fdf9",
        "bg2": "#e1f7ec",
        "surface": "#ffffff",
        "border": "#cdeedd",
        "text": "#022c22",
        "muted": "#4b7a68",
        "accent": "#059669",
        "accent2": "#34d399",
        "soft": "#10b981",
        "grid": "#d3f0e2",
        "empty": "#eaf8f1",
        "levels": ["#c8f2df", "#6ee7b7", "#34d399", "#059669"],
        "gold": "#b8860b",
        "alt": "#7c3aed",
        "icon": "#059669",
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
