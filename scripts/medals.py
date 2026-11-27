"""Award station badges. The awards section is drawn as a metro line: each
award is a station whose sign is a pictogram badge (a rounded square with a
metallic frame, in the spirit of the CDMX Metro station icons, with original
drawings). Finishes are gradients of the profile palette: gold frame on an
emerald face for 1st place, violet for 3rd place and mint for special
mentions.

`badge(slug, ...)` returns SVG drawn around (0, 0) with a half size of 64, so
callers place and scale it with a transform (the station tiles and the mini
badges on the project cards share this code).
"""
import math

FINISHES = {
    # rim gradient stops, face (center, edge), chip text color, ribbon (band, stripe)
    "gold": (["#fff6c2", "#FFD700", "#a77b06", "#f5c518", "#fff6c2"], ("#0f9f74", "#022c22"), "#3d2c00", ("#047857", "#FFD700")),
    "violet": (["#f1edff", "#c4b5fd", "#6d28d9", "#a78bfa", "#f1edff"], ("#7c3aed", "#1e0040"), "#2d0057", ("#5b21b6", "#c4b5fd")),
    "mint": (["#e8fff5", "#6ee7b7", "#047857", "#34d399", "#e8fff5"], ("#047857", "#011a14"), "#022c22", ("#065f46", "#6ee7b7")),
}


def _shape(kind: str, r: float, attrs: str) -> str:
    if kind == "hex":
        pts = " ".join(f"{r * math.cos(math.radians(a)):.1f},{r * math.sin(math.radians(a)):.1f}" for a in range(-90, 270, 60))
        return f'<polygon points="{pts}" {attrs}/>'
    return f'<circle r="{r}" {attrs}/>'


def _icon(name: str, ink: str, hi: str) -> str:
    """Line icon engraved in metal. `ink` is the metallic stroke, `hi` the highlight fill."""
    def sw(w=5.5):
        return f'fill="none" stroke="{ink}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'
    s = sw()
    if name == "hexmap":  # H3 map of street commerce
        out = []
        for i, (cx, cy) in enumerate([(-17, -14), (17, -14), (0, 16), (-34, 16), (34, 16)]):
            pts = " ".join(f"{cx + 16 * math.cos(math.radians(a)):.1f},{cy + 16 * math.sin(math.radians(a)):.1f}" for a in range(30, 390, 60))
            fill = f'fill="{hi}"' if i == 2 else 'fill="none"'
            out.append(f'<polygon points="{pts}" {fill} stroke="{ink}" stroke-width="4.5" stroke-linejoin="round"/>')
        return "".join(out)
    if name == "pin":  # map pin over a market-stall awning
        return (f'<path d="M0,42 C-8,29 -32,12 -32,-12 A32,32 0 1 1 32,-12 C32,12 8,29 0,42 Z" {s}/>'
                f'<path d="M-16,-12 L-12,-24 H12 L16,-12 Z" fill="{hi}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>'
                f'<path d="M-13,-12 V3 H13 V-12" {sw(4)}/>')
    if name == "gov":  # government building
        return (f'<path d="M-42,-14 L0,-40 L42,-14 Z" fill="{hi}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
                + "".join(f'<path d="M{x},-4 V24" {s}/>' for x in (-28, -9, 9, 28))
                + f'<path d="M-44,34 H44" {s}/>')
    if name == "city":  # skyline with a monitoring signal
        return (f'<path d="M-42,38 V4 H-21 V38 M-21,38 V-16 H4 V38 M4,38 V-2 H27 V38 M27,38 V16 H42 V38 M-46,38 H46" {s}/>'
                f'<path d="M-12,-30 A20,20 0 0 1 2,-46" fill="none" stroke="{ink}" stroke-width="4.5" stroke-linecap="round"/>'
                f'<circle cx="-8" cy="-27" r="5" fill="{hi}" stroke="{ink}" stroke-width="3"/>')
    if name == "voice":  # speech bubble with a waveform
        bars = "".join(f'<path d="M{x},{-h / 2 - 2:.0f} V{h / 2 - 2:.0f}" {sw(5.5)}/>'
                       for x, h in [(-22, 10), (-11, 22), (0, 34), (11, 22), (22, 12)])
        return (f'<path d="M-42,-32 H42 A10,10 0 0 1 52,-22 V18 A10,10 0 0 1 42,28 H-8 L-26,44 L-24,28 H-42 A10,10 0 0 1 -52,18 V-22 A10,10 0 0 1 -42,-32 Z" '
                f'fill="{hi}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>{bars}')
    if name == "train":  # metro train front on rails
        return (f'<rect x="-30" y="-42" width="60" height="68" rx="15" {s}/>'
                f'<path d="M-20,-28 H20 V-6 H-20 Z" fill="{hi}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>'
                f'<circle cx="-14" cy="11" r="4.5" fill="{ink}"/><circle cx="14" cy="11" r="4.5" fill="{ink}"/>'
                f'<path d="M-18,28 L-30,44 M18,28 L30,44 M-36,44 H36" {s}/>')
    raise ValueError(name)


def badge(slug: str, finish: str, icon: str, rank: str = "", shine_delay: float = 0.0, shine: bool = True) -> str:
    rim, (face_in, face_out), rank_ink, _ = FINISHES[finish]
    p = f"b-{slug}"

    def stops(colors):
        return "".join(f'<stop offset="{i / (len(colors) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(colors))

    # User-space gradients: a bounding-box gradient on a straight line has a
    # zero-height box and would not paint at all.
    shine_svg = (
        f'<g clip-path="url(#{p}-clip)"><g transform="rotate(25)"><rect x="-160" y="-110" width="26" height="220" fill="#fff" '
        f'opacity=".3" class="shine" style="animation-delay:{shine_delay:.1f}s"/></g></g>'
    ) if shine else ""
    rank_svg = (
        f'<g transform="translate(50,-50)"><circle r="21" fill="url(#{p}-rim)" stroke="#000" stroke-opacity=".25"/>'
        f'<circle r="15.5" fill="none" stroke="#000" stroke-opacity=".18"/>'
        f'<text y="6.5" text-anchor="middle" font-family="\'Segoe UI\', system-ui, sans-serif" font-weight="800" '
        f'font-size="{18 if len(rank) < 3 else 14}" fill="{rank_ink}">{rank}</text></g>'
    ) if rank else ""
    return f"""
  <defs>
    <linearGradient id="{p}-rim" gradientUnits="userSpaceOnUse" x1="-64" y1="-64" x2="64" y2="64">{stops(rim)}</linearGradient>
    <linearGradient id="{p}-ink" gradientUnits="userSpaceOnUse" x1="-40" y1="-40" x2="40" y2="40">{stops(["#ffffff", rim[0], rim[1]])}</linearGradient>
    <radialGradient id="{p}-face" cx=".32" cy=".25" r=".95"><stop offset="0" stop-color="{face_in}"/><stop offset="1" stop-color="{face_out}"/></radialGradient>
    <clipPath id="{p}-clip"><rect x="-64" y="-64" width="128" height="128" rx="30"/></clipPath>
  </defs>
  <rect x="-64" y="-64" width="128" height="128" rx="30" fill="url(#{p}-rim)"/>
  <rect x="-56" y="-56" width="112" height="112" rx="24" fill="url(#{p}-face)"/>
  <rect x="-56" y="-56" width="112" height="112" rx="24" fill="none" stroke="#000" stroke-opacity=".3" stroke-width="2"/>
  <path d="M-46,-30 Q-46,-46 -30,-46 H30" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="4" stroke-linecap="round"/>
  <g transform="translate(0,2) scale(.82)">
    <g transform="translate(0,3)" opacity=".4">{_icon(icon, "#000", "#000")}</g>
    {_icon(icon, f"url(#{p}-ink)", rim[1])}
  </g>
  {shine_svg}
  {rank_svg}
"""


SHINE_CSS = """
    .shine { animation: shine 8s ease-in-out infinite; }
    @keyframes shine { 0% { transform: translateX(0) } 12%,100% { transform: translateX(340px) } }
"""
