"""Generate the data-driven SVGs: Pac-Man contribution graph and stats card.

Needs a token with read access to public data:
    GITHUB_TOKEN=$(gh auth token) python3 scripts/build_profile.py
In CI the workflow passes secrets.GITHUB_TOKEN.
"""
import json
import os
import urllib.request
from datetime import date, timedelta

from theme import MONO, SANS, THEMES, esc, svg_doc, text_width, write

USER = os.environ.get("PROFILE_USER", "crisMmolina")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "generated")
BASE_STYLE = f".sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}
"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def fetch() -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN (e.g. GITHUB_TOKEN=$(gh auth token)).")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    return payload["data"]["user"]


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    seq = list(reversed(days))
    if seq and seq[0]["contributionCount"] == 0:  # today may still be empty
        seq = seq[1:]
    for d in seq:
        if not d["contributionCount"]:
            break
        current += 1
    return current, longest


# --------------------------------------------------------------------------- pac-man

def pacman(t: dict, weeks: list[list[dict]], total: int) -> str:
    cell, pitch = 15, 19
    gx, gy = 96, 78
    ncols = len(weeks)
    W = gx + ncols * pitch + 60
    H = gy + 7 * pitch + 58

    def cxy(col: int, row: int) -> tuple[float, float]:
        return gx + col * pitch + cell / 2, gy + row * pitch + cell / 2

    # Serpentine route: down even columns, up odd ones; enter from the left, leave to the right.
    route = [(gx - 46, cxy(0, 0)[1])]
    order = []
    for col in range(ncols):
        rows = range(7) if col % 2 == 0 else range(6, -1, -1)
        for row in rows:
            route.append(cxy(col, row))
            order.append((col, row, len(route) - 1))
    route.append((W + 30, route[-1][1]))

    dist = [0.0]
    for (x1, y1), (x2, y2) in zip(route, route[1:]):
        dist.append(dist[-1] + abs(x2 - x1) + abs(y2 - y1))
    total_len = dist[-1]
    speed = 160.0  # px per second
    dur = total_len / speed
    regrow = 0.42  # fraction of the loop a cell stays eaten

    path_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in route)

    peak = max((d for w in weeks for d in w), key=lambda d: d["contributionCount"], default=None)
    cells, food = [], []
    for col, row, idx in order:
        day = next((d for d in weeks[col] if d["weekday"] == row), None)
        x, y = gx + col * pitch, gy + row * pitch
        cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" class="e"/>')
        if day is None:
            continue
        delay = max(0.0, dist[idx] / speed - 0.05)
        lvl = LEVELS[day["contributionLevel"]]
        style = f'style="animation-delay:{delay:.2f}s"'
        if lvl:
            extra = " pk" if peak is not None and day is peak and day["contributionCount"] else ""
            food.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{t["levels"][lvl - 1]}" class="f{extra}" {style}/>')
        else:
            cx, cy = cxy(col, row)
            food.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.8" class="f dot" {style}/>')

    # Month labels from the first day of each week.
    labels, last = [], None
    for col, week in enumerate(weeks):
        if not week:
            continue
        m = int(week[0]["date"][5:7])
        if m != last and col < ncols - 2:
            labels.append(f'<text x="{gx + col * pitch}" y="{gy - 12}" class="mono lab">{MONTHS[m - 1]}</text>')
            last = m
    for row, name in ((1, "lun"), (3, "mié"), (5, "vie")):
        labels.append(f'<text x="{gx - 14}" y="{gy + row * pitch + 12}" text-anchor="end" class="mono lab">{name}</text>')

    legend_x = W - 60 - 5 * pitch - 90
    legend = [f'<text x="{legend_x}" y="{H - 22}" class="mono lab" text-anchor="end">menos</text>']
    for i, color in enumerate([t["empty"]] + t["levels"]):
        legend.append(f'<rect x="{legend_x + 10 + i * pitch}" y="{H - 34}" width="{cell}" height="{cell}" rx="4" fill="{color}"/>')
    legend.append(f'<text x="{legend_x + 18 + 5 * pitch}" y="{H - 22}" class="mono lab">más</text>')

    r = 8.5
    mouth_open = f"M0,0 L{r * 0.82:.2f},{-r * 0.57:.2f} A{r},{r} 0 1 0 {r * 0.82:.2f},{r * 0.57:.2f} Z"
    mouth_shut = f"M0,0 L{r:.2f},-0.4 A{r},{r} 0 1 0 {r:.2f},0.4 Z"

    def ghost(color: str, lag: float) -> str:
        return f"""
    <g class="motion" opacity="0">
      <set attributeName="opacity" to="1" begin="{lag:.2f}s"/>
      <animateMotion dur="{dur:.2f}s" begin="{lag:.2f}s" repeatCount="indefinite" path="{path_d}"/>
      <path d="M-8,8 V-1 A8,8 0 0 1 8,-1 V8 L5.3,5.5 L2.7,8 L0,5.5 L-2.7,8 L-5.3,5.5 Z" fill="{color}"/>
      <circle cx="-3" cy="-1.5" r="2.4" fill="#fff"/><circle cx="3" cy="-1.5" r="2.4" fill="#fff"/>
      <circle cx="-2.4" cy="-0.8" r="1.1" fill="{t['bg']}"/><circle cx="3.6" cy="-0.8" r="1.1" fill="{t['bg']}"/>
    </g>"""

    regrow_pct = regrow * 100
    style = BASE_STYLE + f"""
    .e {{ fill: {t['empty']}; }}
    .lab {{ font-size: 12px; fill: {t['muted']}; }}
    .dot {{ fill: {t['muted']}; opacity: .55; }}
    .f {{ transform-box: fill-box; transform-origin: center; animation: eat {dur:.2f}s linear infinite; }}
    @keyframes eat {{ 0% {{ transform: scale(0); opacity: 0 }} {regrow_pct:.1f}% {{ transform: scale(0); opacity: 0 }}
                      {regrow_pct + 6:.1f}% {{ transform: scale(1); opacity: 1 }} 100% {{ transform: scale(1); opacity: 1 }} }}
    .pk {{ stroke: {t['soft']}; stroke-width: 2; }}
    .glow {{ filter: drop-shadow(0 0 4px {t['accent']}); }}
    """

    body = f"""
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="{t['surface']}" stroke="{t['border']}" stroke-width="2"/>
  <text x="{gx}" y="40" class="sans" font-weight="700" font-size="20" fill="{t['text']}">{total} contribuciones en el último año</text>
  <text x="{W - 60}" y="40" text-anchor="end" class="mono lab">se actualiza a diario</text>
  {''.join(labels)}
  {''.join(cells)}
  {''.join(food)}
  {''.join(legend)}
  <clipPath id="arena"><rect x="{gx - 40}" y="{gy - 10}" width="{W - gx + 10}" height="{7 * pitch + 20}"/></clipPath>
  <g clip-path="url(#arena)">
    {ghost(t['accent2'], 1.1)}
    {ghost(t['green'], 1.9)}
    <g class="motion glow">
      <animateMotion dur="{dur:.2f}s" repeatCount="indefinite" rotate="auto" path="{path_d}"/>
      <path d="{mouth_open}" fill="{t['gold'] if t is THEMES['dark'] else t['accent']}">
        <animate attributeName="d" dur="0.28s" repeatCount="indefinite" values="{mouth_open};{mouth_shut};{mouth_open}"/>
      </path>
    </g>
  </g>
"""
    return svg_doc(W, H, body, style, f"Pac-Man recorriendo {total} contribuciones de {USER} en el último año")


# --------------------------------------------------------------------------- stats

def stats(t: dict, data: dict, days: list[dict]) -> str:
    W, H, pad, gap = 1280, 300, 20, 20
    cc = data["contributionsCollection"]
    _, longest = streaks(days)
    active = sum(1 for d in days if d["contributionCount"])
    repos = data["repositories"]
    numbers = [
        (f"{cc['contributionCalendar']['totalContributions']}", "contribuciones · último año"),
        (f"{active}", "días activos · último año"),
        (f"{longest} días", "racha más larga"),
        (f"{repos['totalCount']}", "repositorios públicos"),
    ]
    tw = (W - 2 * pad - 3 * gap) / 4
    tiles = []
    for i, (value, label) in enumerate(numbers):
        x = pad + i * (tw + gap)
        tiles.append(f"""
  <g class="tile" style="animation-delay:{i * 0.1:.1f}s">
    <rect x="{x:.1f}" y="{pad}" width="{tw:.1f}" height="120" rx="20" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
    <text x="{x + 24:.1f}" y="{pad + 64}" class="sans" font-weight="800" font-size="38" fill="{t['accent']}">{esc(value)}</text>
    <text x="{x + 24:.1f}" y="{pad + 94}" class="sans" font-size="15" fill="{t['muted']}">{esc(label)}</text>
  </g>""")

    sizes: dict[str, int] = {}
    for node in repos["nodes"]:
        for edge in node["languages"]["edges"]:
            sizes[edge["node"]["name"]] = sizes.get(edge["node"]["name"], 0) + edge["size"]
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    ramp = [t["accent2"], t["accent"], t["soft"], t["levels"][1], t["levels"][0], t["muted"]]
    y0 = pad + 120 + gap
    bar_x, bar_w = pad + 24, W - 2 * pad - 48
    segs, legend, x, lx = [], [], bar_x, bar_x
    for i, (lang, size) in enumerate(top):
        w = bar_w * size / total
        segs.append(f'<rect x="{x:.1f}" y="{y0 + 54}" width="{max(w - 3, 1):.1f}" height="14" rx="7" fill="{ramp[i]}"/>')
        x += w
        label = f"{lang} {100 * size / total:.0f}%"
        legend.append(f'<circle cx="{lx + 6}" cy="{y0 + 99}" r="6" fill="{ramp[i]}"/>'
                      f'<text x="{lx + 18}" y="{y0 + 104}" class="sans" font-size="15" fill="{t["text"]}">{esc(label)}</text>')
        lx += text_width(label, 15) + 46
    body = "".join(tiles) + f"""
  <g class="tile" style="animation-delay:.4s">
    <rect x="{pad}" y="{y0}" width="{W - 2 * pad}" height="{H - y0 - pad}" rx="20" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
    <text x="{pad + 24}" y="{y0 + 36}" class="sans" font-weight="700" font-size="17" fill="{t['text']}">Lenguajes en repos públicos</text>
    {''.join(segs)}{''.join(legend)}
  </g>"""
    style = BASE_STYLE + """
    .tile { animation: up .6s ease-out both; }
    @keyframes up { from { opacity: 0; transform: translateY(12px) } to { opacity: 1; transform: none } }
    """
    return svg_doc(W, H, body, style, f"Estadísticas de GitHub de {USER}")


def main() -> None:
    data = fetch()
    cal = data["contributionsCollection"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]]
    days = [d for w in weeks for d in w]
    os.makedirs(OUT, exist_ok=True)
    for mode, t in THEMES.items():
        write(os.path.join(OUT, f"pacman-{mode}.svg"), pacman(t, weeks, cal["totalContributions"]))
        write(os.path.join(OUT, f"stats-{mode}.svg"), stats(t, data, days))


if __name__ == "__main__":
    main()
