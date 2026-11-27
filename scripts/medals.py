"""Award medals in the style of GitHub achievements: bevelled metallic coins
with an engraved illustration in the middle. Finishes are gradients of the
profile palette: gold on emerald for 1st place, violet for 3rd place and mint
for special mentions.

`medal(slug, ...)` returns SVG drawn around (0, 0) with radius 100, so callers
can place and scale it with a transform (the full medals and the mini versions
on the project cards share this code). `ribbon(finish)` draws the hanging
ribbon; its bottom edge (where the clasp goes) sits at y=0.
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


def medal(slug: str, finish: str, shape: str, icon: str, chip: str, shine_delay: float = 0.0, shine: bool = True) -> str:
    rim, (face_in, face_out), chip_ink, _ = FINISHES[finish]
    p = f"m-{slug}"

    def stops(colors):
        return "".join(f'<stop offset="{i / (len(colors) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(colors))

    # Metal gradients use user space: an objectBoundingBox gradient on a
    # straight line has a zero-height box and would not paint at all.
    ticks = "".join(
        f'<line x1="{90 * math.cos(math.radians(a)):.1f}" y1="{90 * math.sin(math.radians(a)):.1f}" '
        f'x2="{97 * math.cos(math.radians(a)):.1f}" y2="{97 * math.sin(math.radians(a)):.1f}"/>'
        for a in range(0, 360, 6)
    ) if shape != "hex" else ""
    shine_svg = (
        f'<g clip-path="url(#{p}-clip)"><g transform="rotate(25)"><rect x="-220" y="-140" width="30" height="280" fill="#fff" '
        f'opacity=".35" class="shine" style="animation-delay:{shine_delay:.1f}s"/></g></g>'
    ) if shine else ""
    chip_svg = (
        f'<rect x="-30" y="80" width="60" height="28" rx="14" fill="url(#{p}-rim)" stroke="#000" stroke-opacity=".25"/>'
        f'<text x="0" y="100" text-anchor="middle" font-family="\'Segoe UI\', system-ui, sans-serif" font-weight="800" font-size="18" fill="{chip_ink}">{chip}</text>'
    ) if chip else ""
    return f"""
  <defs>
    <linearGradient id="{p}-rim" gradientUnits="userSpaceOnUse" x1="-100" y1="-100" x2="100" y2="100">{stops(rim)}</linearGradient>
    <linearGradient id="{p}-bevel" gradientUnits="userSpaceOnUse" x1="-100" y1="-100" x2="100" y2="100">{stops(list(reversed(rim)))}</linearGradient>
    <linearGradient id="{p}-ink" gradientUnits="userSpaceOnUse" x1="-50" y1="-50" x2="50" y2="50">{stops(rim[:4])}</linearGradient>
    <radialGradient id="{p}-face" cx=".38" cy=".3" r=".85"><stop offset="0" stop-color="{face_in}"/><stop offset="1" stop-color="{face_out}"/></radialGradient>
    <clipPath id="{p}-clip">{_shape(shape, 100, '')}</clipPath>
  </defs>
  {_shape(shape, 100, f'fill="url(#{p}-rim)"')}
  <g stroke="#000" stroke-opacity=".16" stroke-width="2">{ticks}</g>
  {_shape(shape, 86, f'fill="url(#{p}-bevel)"')}
  {_shape(shape, 78, f'fill="url(#{p}-face)"')}
  {_shape(shape, 78, 'fill="none" stroke="#000" stroke-opacity=".35" stroke-width="3"')}
  {_shape(shape, 70, 'fill="none" stroke="#fff" stroke-opacity=".14" stroke-width="1.5" stroke-dasharray="2 5"')}
  <g transform="translate(0,-2)">
    <g transform="translate(0,2.5)" opacity=".45">{_icon(icon, "#000", "#000")}</g>
    {_icon(icon, f"url(#{p}-ink)", face_in)}
  </g>
  <path d="M-60,-34 A68,68 0 0 1 26,-66" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="5" stroke-linecap="round"/>
  {shine_svg}
  {chip_svg}
"""


def ribbon(slug: str, finish: str, w: float = 96, h: float = 108) -> str:
    """V-shaped ribbon hanging from y=-h down to a clasp at y=0, centered on x=0."""
    band, stripe = FINISHES[finish][3]
    p = f"r-{slug}"
    top, bot = w / 2, w * 0.32
    poly = f"{-top},{-h} {top},{-h} {bot},0 {-bot},0"
    return f"""
  <defs>
    <clipPath id="{p}"><polygon points="{poly}"/></clipPath>
    <linearGradient id="{p}-fold" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000" stop-opacity=".35"/><stop offset=".22" stop-color="#000" stop-opacity="0"/>
      <stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset=".78" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".35"/>
    </linearGradient>
  </defs>
  <g clip-path="url(#{p})">
    <rect x="{-top}" y="{-h}" width="{w}" height="{h}" fill="{band}"/>
    <rect x="{-w * 0.12:.1f}" y="{-h}" width="{w * 0.24:.1f}" height="{h}" fill="{stripe}"/>
    <rect x="{-w * 0.31:.1f}" y="{-h}" width="{w * 0.05:.1f}" height="{h}" fill="{stripe}" opacity=".8"/>
    <rect x="{w * 0.26:.1f}" y="{-h}" width="{w * 0.05:.1f}" height="{h}" fill="{stripe}" opacity=".8"/>
    <rect x="{-top}" y="{-h}" width="{w}" height="{h}" fill="url(#{p}-fold)"/>
  </g>
"""


SHINE_CSS = """
    .shine { animation: shine 7s ease-in-out infinite; }
    @keyframes shine { 0% { transform: translateX(0) } 14%,100% { transform: translateX(420px) } }
"""
