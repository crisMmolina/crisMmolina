"""Generate the static profile SVGs (banner, awards, project cards, icons).

Run from the repo root:  python3 scripts/build_assets.py
Every asset is written twice, as <name>-dark.svg and <name>-light.svg.
"""
import math
import os
import random

from theme import MONO, SANS, THEMES, chip, esc, svg_doc, text_width, write

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
SQ3 = math.sqrt(3)

BASE_STYLE = f".sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}"


def hex_points(cx: float, cy: float, r: float) -> str:
    return " ".join(
        f"{cx + r * math.cos(math.radians(a)):.1f},{cy + r * math.sin(math.radians(a)):.1f}"
        for a in range(0, 360, 60)
    )


def wrap(text: str, limit: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + ([cur] if cur else [])


# --------------------------------------------------------------------------- banner

def banner(t: dict) -> str:
    W, H, R = 1280, 440, 30
    rng = random.Random(7)
    x0, y0 = 600, 14

    def center(col: int, row: int) -> tuple[float, float]:
        return x0 + col * 1.5 * R, y0 + row * SQ3 * R + (col % 2) * SQ3 * R / 2

    route_cells = [(3, 6), (4, 5), (5, 5), (6, 5), (7, 4), (8, 3), (9, 3), (10, 3), (11, 2), (12, 2)]
    route_set = set(route_cells)

    hexes = []
    for col in range(-1, 17):
        for row in range(-1, 9):
            cx, cy = center(col, row)
            pts = hex_points(cx, cy, R - 2)
            hexes.append(f'<polygon points="{pts}" class="cell"/>')
            if (col, row) in route_set:
                continue
            if rng.random() < 0.2:
                lvl = rng.randint(0, 3)
                delay = rng.uniform(0, 6)
                hexes.append(
                    f'<polygon points="{pts}" fill="{t["levels"][lvl]}" class="hot" '
                    f'style="animation-delay:{delay:.2f}s"/>'
                )

    route_pts = [center(c, r) for c, r in route_cells]
    route_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in route_pts)
    visited = []
    for i, (c, r) in enumerate(route_cells):
        cx, cy = center(c, r)
        delay = 1.2 + 1.6 * i / (len(route_cells) - 1)
        visited.append(
            f'<polygon points="{hex_points(cx, cy, R - 2)}" class="visit" style="animation-delay:{delay:.2f}s"/>'
        )
    px, py = route_pts[-1]

    chips_svg, cx_ = [], 72
    for label in ("frontend + datos geoespaciales", "4× 1er lugar en hackathons", "IA aplicada"):
        svg, w = chip(cx_, 370, label, t, size=15)
        chips_svg.append(svg)
        cx_ += w + 10

    style = BASE_STYLE + f"""
    .cell {{ fill: none; stroke: {t['grid']}; stroke-width: 1.2; }}
    .hot {{ opacity: .5; animation: pulse 6s ease-in-out infinite both; }}
    @keyframes pulse {{ 0%,100% {{ opacity: .12 }} 50% {{ opacity: .7 }} }}
    .visit {{ fill: {t['accent']}; fill-opacity: .28; animation: visit .5s ease-out both; }}
    @keyframes visit {{ from {{ fill-opacity: 0 }} to {{ fill-opacity: .28 }} }}
    .route {{ fill: none; stroke: {t['accent']}; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round;
              stroke-dasharray: 1; stroke-dashoffset: 0; animation: draw 1.6s 1.2s ease-in-out both; }}
    @keyframes draw {{ from {{ stroke-dashoffset: 1 }} to {{ stroke-dashoffset: 0 }} }}
    .pin {{ animation: drop .6s 2.8s cubic-bezier(.3,1.6,.5,1) both; transform-box: fill-box; transform-origin: 50% 100%; }}
    @keyframes drop {{ from {{ opacity: 0; transform: translateY(-40px) scale(.6) }} to {{ opacity: 1; transform: none }} }}
    .ring {{ fill: none; stroke: {t['accent']}; stroke-width: 2; transform-box: fill-box; transform-origin: center;
             animation: ring 2.4s 3.4s ease-out infinite both; }}
    @keyframes ring {{ from {{ opacity: .9; transform: scale(.3) }} to {{ opacity: 0; transform: scale(2.2) }} }}
    .name {{ font-weight: 800; font-size: 100px; letter-spacing: -2px; stroke-width: 1.6;
             stroke-dasharray: 1400; stroke-dashoffset: 0; fill-opacity: 1;
             animation: write 2.4s ease-in-out both; }}
    .n1 {{ fill: {t['text']}; stroke: {t['accent']}; }}
    .n2 {{ fill: url(#nameGrad); stroke: {t['accent']}; animation-delay: .35s; }}
    @keyframes write {{ 0% {{ stroke-dashoffset: 1400; fill-opacity: 0 }} 65% {{ stroke-dashoffset: 0; fill-opacity: 0 }}
                        100% {{ stroke-dashoffset: 0; fill-opacity: 1 }} }}
    .up {{ animation: up .7s ease-out both; }}
    @keyframes up {{ from {{ opacity: 0; transform: translateY(12px) }} to {{ opacity: 1; transform: none }} }}
    .cursor {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    """

    body = f"""
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['bg2']}"/>
    </linearGradient>
    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t['accent2']}"/><stop offset="1" stop-color="{t['accent']}"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0.38" stop-color="#fff" stop-opacity="0"/><stop offset="0.72" stop-color="#fff" stop-opacity="1"/>
    </linearGradient>
    <mask id="fadeMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <g mask="url(#fadeMask)">{''.join(hexes)}{''.join(visited)}</g>
    <path d="{route_d}" pathLength="1" class="route"/>
    <circle r="5" fill="{t['text']}" class="motion">
      <animateMotion dur="5s" begin="3.4s" repeatCount="indefinite" path="{route_d}"/>
    </circle>
    <circle cx="{px:.1f}" cy="{py:.1f}" r="16" class="ring"/>
    <g class="pin">
      <path d="M{px:.1f},{py:.1f} c-4,-10 -16,-18 -16,-32 a16,16 0 1 1 32,0 c0,14 -12,22 -16,32 z" fill="{t['accent2']}" stroke="{t['text']}" stroke-width="2"/>
      <circle cx="{px:.1f}" cy="{py - 32:.1f}" r="6" fill="{t['text']}"/>
    </g>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="27" fill="none" stroke="{t['border']}" stroke-width="2"/>

  <g class="up" style="animation-delay:.1s">
    <text x="72" y="92" class="mono" font-size="18" fill="{t['muted']}">~/cdmx · 19.43°N 99.13°W</text>
    <rect x="{72 + text_width('~/cdmx · 19.43°N 99.13°W', 18, mono=True) + 6:.0f}" y="76" width="10" height="20" fill="{t['accent']}" class="cursor"/>
  </g>
  <text x="68" y="196" class="sans name n1">Cristopher</text>
  <text x="68" y="296" class="sans name n2">Molina</text>
  <text x="72" y="346" class="sans up" font-size="23" fill="{t['muted']}" style="animation-delay:2.2s">Ingeniería en Informática · IPN UPIICSA</text>
  <g class="up" style="animation-delay:2.6s">{''.join(chips_svg)}</g>
"""
    return svg_doc(W, H, body, style, "Cristopher Molina — Ingeniería en Informática, IPN UPIICSA")


# --------------------------------------------------------------------------- awards

AWARDS = [
    ("1°", "gold", "SEDECO Chilangatón", "Mapa H3 del comercio popular", "OCT 2026"),
    ("1°", "gold", "Hackathon ADA", "Datos abiertos a escala CDMX", "OCT 2026"),
    ("1°", "gold", "SEDECO SecretarIA", "MercurIA · planeación de eventos", "JUN 2026"),
    ("1°", "gold", "IBM Talent Land", "LumivIA · Genius Arena", "ABR 2026"),
    ("3°", "accent", "ElevenLabs Hackathon", "Psyness · Mejor proyecto con Bolt", "DIC 2025"),
    ("OS", "green", "Made in Austria", "RailSense · Ganador Open Source", "NOV 2025"),
]


def awards(t: dict) -> str:
    W, H = 1280, 360
    tw, th, gap, pad = 400, 150, 20, 20
    tiles = []
    for i, (rank, tone, name, detail, date) in enumerate(AWARDS):
        x = pad + (i % 3) * (tw + gap)
        y = pad + (i // 3) * (th + gap)
        color = t[tone]
        tiles.append(f"""
  <g class="tile" style="animation-delay:{0.12 * i:.2f}s">
    <rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="22" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
    <rect x="{x + 24}" y="{y + 24}" width="64" height="64" rx="18" fill="{color}" fill-opacity=".14" stroke="{color}" stroke-opacity=".5"/>
    <text x="{x + 56}" y="{y + 66}" text-anchor="middle" class="sans" font-weight="800" font-size="{28 if rank != 'OS' else 22}" fill="{color}">{rank}</text>
    <text x="{x + tw - 24}" y="{y + 42}" text-anchor="end" class="mono" font-size="13" fill="{t['muted']}" letter-spacing="1">{date}</text>
    <text x="{x + 24}" y="{y + 118}" class="sans" font-weight="700" font-size="21" fill="{t['text']}">{esc(name)}</text>
    <text x="{x + 24}" y="{y + 138}" class="sans" font-size="15" fill="{t['muted']}">{esc(detail)}</text>
  </g>""")
    style = BASE_STYLE + """
    .tile { animation: up .6s ease-out both; }
    @keyframes up { from { opacity: 0; transform: translateY(14px) } to { opacity: 1; transform: none } }
    """
    return svg_doc(W, H, "".join(tiles), style, "Reconocimientos: 4 primeros lugares, un 3er lugar y ganador Open Source")


# --------------------------------------------------------------------------- project cards

def motif_mercuria(t, ox, oy, w, h):
    r, out = 17, []
    rng = random.Random(3)
    for col in range(7):
        for row in range(7):
            cx = ox + 14 + col * 1.5 * r
            cy = oy + 30 + row * SQ3 * r + (col % 2) * SQ3 * r / 2
            if cx > ox + w - 6 or cy > oy + h - 10:
                continue
            fill = t["levels"][rng.randint(0, 3)] if rng.random() < 0.45 else "none"
            out.append(f'<polygon points="{hex_points(cx, cy, r - 2)}" fill="{fill}" stroke="{t["grid"]}" stroke-width="1.2"/>')
    for i, (px, py) in enumerate([(ox + 52, oy + 120), (ox + 120, oy + 80), (ox + 100, oy + 200)]):
        out.append(
            f'<g class="pop" style="animation-delay:{0.5 * i:.1f}s"><path d="M{px},{py} c-3,-7 -11,-12 -11,-22 a11,11 0 1 1 22,0 '
            f'c0,10 -8,15 -11,22 z" fill="{t["accent2"]}" stroke="{t["text"]}" stroke-width="1.5"/>'
            f'<circle cx="{px}" cy="{py - 22}" r="4" fill="{t["text"]}"/></g>'
        )
    return "".join(out)


def motif_lumivia(t, ox, oy, w, h):
    cx, cy = ox + w / 2, oy + h / 2
    out = [f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{t["grid"]}" stroke-width="1.2"/>' for rr in (30, 55, 80)]
    out.append(f'<line x1="{cx - 80}" y1="{cy}" x2="{cx + 80}" y2="{cy}" stroke="{t["grid"]}"/>')
    out.append(f'<line x1="{cx}" y1="{cy - 80}" x2="{cx}" y2="{cy + 80}" stroke="{t["grid"]}"/>')
    out.append(
        f'<g><path d="M{cx},{cy} L{cx + 80},{cy} A80,80 0 0 0 {cx + 80 * math.cos(math.radians(-40)):.1f},'
        f'{cy + 80 * math.sin(math.radians(-40)):.1f} Z" fill="{t["accent"]}" fill-opacity=".28"/>'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="4s" repeatCount="indefinite"/></g>'
    )
    for i, (dx, dy) in enumerate([(30, -42), (-50, -20), (-24, 52), (58, 30)]):
        out.append(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="5" fill="{t["accent"]}" class="blink" style="animation-delay:{i * 0.9:.1f}s"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="10" class="ripple" fill="none" stroke="{t["accent"]}" stroke-width="2"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{t["text"]}"/>')
    return "".join(out)


def motif_railsense(t, ox, oy, w, h):
    l1 = f"M{ox + 14},{oy + 60} C{ox + 80},{oy + 60} {ox + 80},{oy + 210} {ox + w - 14},{oy + 210}"
    l2 = f"M{ox + 20},{oy + h - 30} C{ox + 70},{oy + 140} {ox + 120},{oy + 120} {ox + w - 20},{oy + 40}"
    out = [
        f'<path id="l1" d="{l1}" fill="none" stroke="{t["accent2"]}" stroke-width="7" stroke-linecap="round"/>',
        f'<path id="l2" d="{l2}" fill="none" stroke="{t["soft"]}" stroke-width="7" stroke-linecap="round" stroke-opacity=".8"/>',
    ]
    for i, (sx, sy, heat) in enumerate([(ox + 14, oy + 60, 1), (ox + 94, oy + 140, 3), (ox + w - 14, oy + 210, 2),
                                        (ox + 20, oy + h - 30, 1), (ox + w - 20, oy + 40, 2)]):
        out.append(f'<circle cx="{sx}" cy="{sy}" r="{10 + heat * 6}" fill="{t["accent"]}" class="heat" style="animation-delay:{i * 0.6:.1f}s"/>')
        out.append(f'<circle cx="{sx}" cy="{sy}" r="7" fill="{t["surface"]}" stroke="{t["text"]}" stroke-width="3"/>')
    for lid, dur in (("l1", "3.5s"), ("l2", "4.2s")):
        out.append(f'<circle r="5" fill="{t["text"]}" class="motion"><animateMotion dur="{dur}" repeatCount="indefinite"><mpath href="#{lid}"/></animateMotion></circle>')
    return "".join(out)


def motif_psyness(t, ox, oy, w, h):
    n, bw = 13, 8
    gap = (w - 24 - n * bw) / (n - 1)
    cy = oy + h / 2
    heights = [24, 46, 70, 52, 96, 130, 84, 118, 64, 92, 48, 30, 18]
    out = []
    for i, bh in enumerate(heights):
        x = ox + 12 + i * (bw + gap)
        out.append(f'<rect x="{x:.1f}" y="{cy - bh / 2:.1f}" width="{bw}" height="{bh}" rx="4" fill="{t["accent"] if i % 3 else t["accent2"]}" '
                   f'class="bar" style="animation-delay:{(i * 0.11) % 0.9:.2f}s"/>')
    out.append(f'<circle cx="{ox + 22}" cy="{oy + 28}" r="6" fill="#f43f5e" class="blink"/>')
    out.append(f'<text x="{ox + 34}" y="{oy + 33}" class="mono" font-size="13" fill="{t["muted"]}">voz en vivo</text>')
    return "".join(out)


PROJECTS = [
    ("mercuria", "MercurIA", "1er lugar · SEDECO SecretarIA",
     "Planeación de eventos en CDMX con IA, análisis geoespacial y datos económicos.",
     ["React", "Vite", "MapBox", "Node.js"], motif_mercuria),
    ("lumivia", "LumivIA", "1er lugar · IBM Talent Land",
     "Monitoreo urbano en tiempo real: movilidad, medio ambiente y riesgos en una sola vista.",
     ["React", "TypeScript", "MapBox", "IBM Cloud"], motif_lumivia),
    ("railsense", "RailSense", "Ganador · Open Source",
     "Mapas de calor de redes de metro a partir de reportes ciudadanos en tiempo real.",
     ["React", "Node.js", "Heatmaps"], motif_railsense),
    ("psyness", "Psyness", "3er lugar · ElevenLabs",
     "Interfaz conversacional por voz para un asistente de salud mental.",
     ["ElevenLabs", "Bolt", "Voz"], motif_psyness),
]


def project_card(t: dict, name, award, tagline, tags, motif) -> str:
    W, H = 640, 340
    mx, my, mw, mh = 412, 24, 204, 292
    pill, _ = chip(32, 32, award, t, size=13, fill=t["bg2"], stroke=t["border"], color=t["accent"])
    lines = "".join(
        f'<text x="32" y="{170 + i * 26}" class="sans" font-size="18" fill="{t["muted"]}">{esc(line)}</text>'
        for i, line in enumerate(wrap(tagline, 36))
    )
    tag_svg, x = [], 32
    for tag in tags:
        svg, w = chip(x, 270, tag, t, size=13)
        tag_svg.append(svg)
        x += w + 8
    style = BASE_STYLE + f"""
    .pop {{ animation: pop 3s ease-in-out infinite both; transform-box: fill-box; transform-origin: 50% 100%; }}
    @keyframes pop {{ 0% {{ opacity: 0; transform: translateY(-12px) }} 15%,80% {{ opacity: 1; transform: none }} 100% {{ opacity: 0 }} }}
    .blink {{ animation: blink 2.4s ease-in-out infinite both; }}
    @keyframes blink {{ 0%,100% {{ opacity: .25 }} 50% {{ opacity: 1 }} }}
    .ripple {{ transform-box: fill-box; transform-origin: center; animation: ripple 2.4s ease-out infinite; }}
    @keyframes ripple {{ from {{ opacity: .9; transform: scale(1) }} to {{ opacity: 0; transform: scale(8) }} }}
    .heat {{ opacity: .25; animation: heat 3s ease-in-out infinite both; }}
    @keyframes heat {{ 0%,100% {{ opacity: .12 }} 50% {{ opacity: .45 }} }}
    .bar {{ transform-box: fill-box; transform-origin: center; animation: talk 1.1s ease-in-out infinite alternate both; }}
    @keyframes talk {{ from {{ transform: scaleY(.25) }} to {{ transform: scaleY(1) }} }}
    """
    body = f"""
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="{t['surface']}" stroke="{t['border']}" stroke-width="2"/>
  <clipPath id="m"><rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="18"/></clipPath>
  <rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="18" fill="{t['bg2']}"/>
  <g clip-path="url(#m)">{motif(t, mx, my, mw, mh)}</g>
  {pill}
  <text x="30" y="128" class="sans" font-weight="800" font-size="44" letter-spacing="-1" fill="{t['text']}">{esc(name)}</text>
  {lines}
  {''.join(tag_svg)}
"""
    return svg_doc(W, H, body, style, f"{name}: {tagline}")


# --------------------------------------------------------------------------- icons

ICONS = {
    "mail": '<rect x="7" y="11" width="34" height="26" rx="5" fill="none" stroke="{c}" stroke-width="3"/>'
            '<path d="M9 14 L24 26 L39 14" fill="none" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>',
    "linkedin": '<rect x="6" y="6" width="36" height="36" rx="8" fill="{c}"/>'
                '<rect x="13" y="20" width="5" height="15" rx="1" fill="{bg}"/><circle cx="15.5" cy="14.5" r="3" fill="{bg}"/>'
                '<path d="M22 35 V20 h5 v2.2 c1.2-1.8 3-2.7 5.2-2.7 c3.8 0 5.8 2.5 5.8 6.6 V35 h-5 v-8.2 c0-2.2-.9-3.4-2.7-3.4 '
                'c-2 0-3.3 1.4-3.3 3.6 V35 z" fill="{bg}"/>',
    "web": '<circle cx="24" cy="24" r="17" fill="none" stroke="{c}" stroke-width="3"/>'
           '<ellipse cx="24" cy="24" rx="7" ry="17" fill="none" stroke="{c}" stroke-width="2.5"/>'
           '<path d="M7 24 H41 M10 15 H38 M10 33 H38" stroke="{c}" stroke-width="2.5"/>',
}


def icon(t: dict, name: str) -> str:
    inner = ICONS[name].format(c=t["icon"], bg="#ffffff" if t is THEMES["light"] else "#0d1117")
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">{inner}</svg>\n'


def main() -> None:
    for mode, t in THEMES.items():
        write(os.path.join(ASSETS, f"banner-{mode}.svg"), banner(t))
        write(os.path.join(ASSETS, f"awards-{mode}.svg"), awards(t))
        for slug, name, award, tagline, tags, motif in PROJECTS:
            write(os.path.join(ASSETS, f"project-{slug}-{mode}.svg"), project_card(t, name, award, tagline, tags, motif))
        for name in ICONS:
            write(os.path.join(ASSETS, "icons", f"{name}-{mode}.svg"), icon(t, name))


if __name__ == "__main__":
    main()
