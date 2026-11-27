"""Award medals in the style of GitHub achievements: bevelled metallic coins
with an illustration in the middle. Finishes are gradients of the profile
palette: gold rim on emerald for 1st place, violet for 3rd place, and a mint
hexagon for special mentions.

`medal(slug)` returns SVG drawn around (0, 0) with radius 100, so callers can
place and scale it with a transform (full medals and the mini versions on the
project cards share this code).
"""
import math

FINISHES = {
    # rim gradient stops, face (center, edge), chip text color, icon accent
    "gold": (["#fff6c2", "#FFD700", "#a77b06", "#f5c518", "#fff6c2"], ("#10b981", "#022c22"), "#3d2c00", "#FFD700"),
    "violet": (["#f1edff", "#c4b5fd", "#6d28d9", "#a78bfa", "#f1edff"], ("#7c3aed", "#2d0057"), "#2d0057", "#c4b5fd"),
    "mint": (["#e8fff5", "#6ee7b7", "#047857", "#34d399", "#e8fff5"], ("#059669", "#022c22"), "#022c22", "#6ee7b7"),
}

INK = "#ecfdf5"


def _shape(kind: str, r: float) -> str:
    if kind == "hex":
        pts = " ".join(f"{r * math.cos(math.radians(a)):.1f},{r * math.sin(math.radians(a)):.1f}" for a in range(-90, 270, 60))
        return f'<polygon points="{pts}" {{attrs}}/>'
    return f'<circle r="{r}" {{attrs}}/>'


def _icon(name: str, accent: str) -> str:
    def sw(w=6):
        return f'fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'
    s = sw()
    if name == "hexmap":  # H3 map of street commerce
        out = []
        for i, (cx, cy) in enumerate([(-18, -12), (18, -12), (0, 19), (-36, 19), (36, 19)]):
            pts = " ".join(f"{cx + 17 * math.cos(math.radians(a)):.1f},{cy + 17 * math.sin(math.radians(a)):.1f}" for a in range(30, 390, 60))
            fill = f'fill="{accent}" fill-opacity=".9"' if i == 2 else 'fill="none"'
            out.append(f'<polygon points="{pts}" {fill} stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
        return "".join(out)
    if name == "pin":  # map pin over a market-stall awning
        return (f'<path d="M0,44 C-8,30 -34,12 -34,-12 A34,34 0 1 1 34,-12 C34,12 8,30 0,44 Z" {s}/>'
                f'<path d="M-17,-14 L-13,-26 H13 L17,-14 Z" fill="{accent}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
                f'<path d="M-14,-14 V2 H14 V-14" {sw(4)}/>')
    if name == "gov":  # government building
        return (f'<path d="M-44,-14 L0,-42 L44,-14 Z" {s}/>'
                + "".join(f'<path d="M{x},-6 V26" {s}/>' for x in (-30, -10, 10, 30))
                + f'<path d="M-46,36 H46" {s}/><path d="M-40,-14 H40" {sw(4)}/>'
                f'<circle cx="0" cy="-24" r="4" fill="{accent}"/>')
    if name == "city":  # skyline with a monitoring signal
        return (f'<path d="M-44,40 V2 H-22 V40 M-22,40 V-18 H4 V40 M4,40 V-4 H28 V40 M28,40 V14 H44 V40 M-48,40 H48" {s}/>'
                f'<path d="M-15,-30 A20,20 0 0 1 -3,-48 M-3,-30 A8,8 0 0 1 -9,-38" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>'
                f'<circle cx="-9" cy="-28" r="4" fill="{accent}"/>')
    if name == "voice":  # speech bubble with a waveform
        bars = "".join(f'<path d="M{x},{-h / 2:.0f} V{h / 2:.0f}" stroke="{accent if i in (2, 3) else INK}" stroke-width="6" stroke-linecap="round"/>'
                       for i, (x, h) in enumerate([(-24, 12), (-12, 26), (0, 40), (12, 26), (24, 14)]))
        return f'<path d="M-44,-34 H44 A10,10 0 0 1 54,-24 V20 A10,10 0 0 1 44,30 H-10 L-28,46 L-26,30 H-44 A10,10 0 0 1 -54,20 V-24 A10,10 0 0 1 -44,-34 Z" {sw(5)}/>{bars}'
    if name == "train":  # metro train front on rails
        return (f'<rect x="-32" y="-44" width="64" height="72" rx="16" {s}/>'
                f'<path d="M-22,-30 H22 V-6 H-22 Z" fill="{accent}" fill-opacity=".85" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
                f'<circle cx="-16" cy="12" r="5" fill="{INK}"/><circle cx="16" cy="12" r="5" fill="{INK}"/>'
                f'<path d="M-20,30 L-32,46 M20,30 L32,46 M-38,46 H38" {s}/>')
    raise ValueError(name)


def medal(slug: str, finish: str, shape: str, icon: str, chip: str, shine_delay: float = 0.0, shine: bool = True) -> str:
    rim, (face_in, face_out), chip_ink, accent = FINISHES[finish]
    p = f"m-{slug}"
    stops = "".join(f'<stop offset="{i / (len(rim) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(rim))
    rstops = "".join(f'<stop offset="{i / (len(rim) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(reversed(rim)))
    shp = _shape(shape, 1)

    def at(r: float, attrs: str) -> str:
        return shp.replace('r="1"', f'r="{r}"').replace("{attrs}", attrs) if shape != "hex" else _shape(shape, r).replace("{attrs}", attrs)

    ticks = "".join(
        f'<line x1="{91 * math.cos(math.radians(a)):.1f}" y1="{91 * math.sin(math.radians(a)):.1f}" '
        f'x2="{97 * math.cos(math.radians(a)):.1f}" y2="{97 * math.sin(math.radians(a)):.1f}"/>'
        for a in range(0, 360, 8)
    ) if shape != "hex" else ""
    shine_svg = (
        f'<g clip-path="url(#{p}-clip)"><g transform="rotate(25)"><rect x="-220" y="-140" width="36" height="280" fill="#fff" '
        f'opacity=".38" class="shine" style="animation-delay:{shine_delay:.1f}s"/></g></g>'
    ) if shine else ""
    return f"""
  <defs>
    <linearGradient id="{p}-rim" x1="0" y1="0" x2="1" y2="1">{stops}</linearGradient>
    <linearGradient id="{p}-bevel" x1="0" y1="0" x2="1" y2="1">{rstops}</linearGradient>
    <radialGradient id="{p}-face" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="{face_in}"/><stop offset="1" stop-color="{face_out}"/></radialGradient>
    <clipPath id="{p}-clip">{at(100, '')}</clipPath>
  </defs>
  {at(100, f'fill="url(#{p}-rim)"')}
  <g stroke="#000" stroke-opacity=".18" stroke-width="2">{ticks}</g>
  {at(87, f'fill="url(#{p}-bevel)"')}
  {at(79, f'fill="url(#{p}-face)"')}
  {at(76, 'fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="2"')}
  <path d="M-62,-30 A68,68 0 0 1 30,-66" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="5" stroke-linecap="round"/>
  <g transform="translate(0,-4)">{_icon(icon, accent)}</g>
  {shine_svg}
  <rect x="-34" y="78" width="68" height="32" rx="16" fill="url(#{p}-rim)" stroke="#000" stroke-opacity=".2"/>
  <text x="0" y="101" text-anchor="middle" font-family="'Segoe UI', system-ui, sans-serif" font-weight="800" font-size="20" fill="{chip_ink}">{chip}</text>
"""


SHINE_CSS = """
    .shine { animation: shine 7s ease-in-out infinite; }
    @keyframes shine { 0% { transform: translateX(0) } 14%,100% { transform: translateX(420px) } }
"""
