"""Generate the data-driven SVGs: Pac-Man contribution graph and the 3D city + stats card.

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
      totalIssueContributions
      contributionYears
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


def graphql(query: str, variables: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN (e.g. GITHUB_TOKEN=$(gh auth token)).")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    return payload["data"]


def fetch() -> dict:
    return graphql(QUERY, {"login": USER})["user"]


def fetch_all_days(years: list[int]) -> list[dict]:
    """Every contribution day since the account's first active year (for all-time totals and streaks)."""
    parts = [
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
        "{ contributionCalendar { weeks { contributionDays { date contributionCount } } } }"
        for y in years
    ]
    data = graphql("query($login: String!) { user(login: $login) { " + " ".join(parts) + " } }", {"login": USER})["user"]
    today = date.today().isoformat()
    days = {}
    for y in years:
        for w in data[f"y{y}"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                if d["date"] <= today:
                    days[d["date"]] = d
    return [days[k] for k in sorted(days)]


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
    {ghost(t['alt'], 1.9)}
    <g class="motion glow">
      <animateMotion dur="{dur:.2f}s" repeatCount="indefinite" rotate="auto" path="{path_d}"/>
      <path d="{mouth_open}" fill="{t['gold'] if t is THEMES['dark'] else t['accent']}">
        <animate attributeName="d" dur="0.28s" repeatCount="indefinite" values="{mouth_open};{mouth_shut};{mouth_open}"/>
      </path>
    </g>
  </g>
"""
    return svg_doc(W, H, body, style, f"Pac-Man recorriendo {total} contribuciones de {USER} en el último año")


# --------------------------------------------------------------------------- city + stats

def mix(c1: str, c2: str, k: float) -> str:
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(a, b))


def human_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


STAT_ICONS = {
    "star": '<path d="M9 1.5 L11.2 6.3 L16.4 6.8 L12.5 10.3 L13.6 15.5 L9 12.9 L4.4 15.5 L5.5 10.3 L1.6 6.8 L6.8 6.3 Z" {s}/>',
    "commit": '<circle cx="9" cy="9" r="3.6" {s}/><path d="M0.5 9 H5.4 M12.6 9 H17.5" {s}/>',
    "pr": '<circle cx="4" cy="3.5" r="2.3" {s}/><circle cx="4" cy="14.5" r="2.3" {s}/><circle cx="14" cy="14.5" r="2.3" {s}/>'
          '<path d="M4 5.8 V12.2 M14 12.2 V7 Q14 3.5 10.5 3.5 H8 M10 1.5 L8 3.5 L10 5.5" {s}/>',
    "issue": '<circle cx="9" cy="9" r="7.2" {s}/><circle cx="9" cy="9" r="1.6" fill="{c}"/>',
    "calendar": '<rect x="1.5" y="3" width="15" height="13.5" rx="2.5" {s}/><path d="M1.5 7.5 H16.5 M5.5 1 V4.5 M12.5 1 V4.5" {s}/>',
}


def stats_city(t: dict, data: dict, weeks: list[list[dict]], all_days: list[dict]) -> str:
    W, H = 1280, 748
    cc = data["contributionsCollection"]
    cal = cc["contributionCalendar"]
    dark = t is THEMES["dark"]

    # ---- isometric city: one building per day, height = contributions
    ux, vx, vy = 21, 9, 9
    fw, depth = 16, 0.7
    X0, Y0, HMAX = 50, 236, 150
    days = [d for w in weeks for d in w]
    peak = max((d["contributionCount"] for d in days), default=1) or 1
    peak_day = max(days, key=lambda d: d["contributionCount"]) if days else None
    ncol = len(weeks)
    g0 = (X0 - 8, Y0 - 5)
    g1 = (X0 + ncol * ux + 2, Y0 - 5)
    g2 = (g1[0] + 7 * vx + 2, Y0 + 7 * vy + 1)
    g3 = (g0[0] + 7 * vx + 2, Y0 + 7 * vy + 1)
    ground = " ".join(f"{x:.1f},{y:.1f}" for x, y in (g0, g1, g2, g3))
    buildings = []
    for row in range(7):
        for col, week in enumerate(weeks):
            day = next((d for d in week if d["weekday"] == row), None)
            if day is None:
                continue
            n = day["contributionCount"]
            lvl = LEVELS[day["contributionLevel"]]
            ax, ay = X0 + col * ux + row * vx, Y0 + row * vy
            dx, dy = vx * depth, vy * depth
            h = 2.5 if not n else 8 + (HMAX - 8) * (n / peak) ** 0.6
            base = t["levels"][lvl - 1] if lvl else t["grid"]
            top = t["gold"] if day is peak_day and n else mix(base, "#ffffff", 0.28 if dark else 0.45)
            right = mix(base, "#000000", 0.35 if dark else 0.18)
            A, B = (ax, ay - h), (ax + fw, ay - h)
            C, D = (ax + fw + dx, ay + dy - h), (ax + dx, ay + dy - h)

            def poly(pts, fill):
                return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}"/>'

            front = poly([(D[0], D[1] + h), (C[0], C[1] + h), C, D], base)
            side = poly([(B[0], B[1] + h), (C[0], C[1] + h), C, B], right)
            roof = poly([A, B, C, D], top)
            cls = f' class="b" style="animation-delay:{0.02 * col + 0.04 * row:.2f}s"' if n else ""
            buildings.append(f"<g{cls}>{front}{side}{roof}</g>")
            if day is peak_day and n:
                buildings.append(f'<circle cx="{(A[0] + C[0]) / 2:.1f}" cy="{(A[1] + C[1]) / 2 - 10:.1f}" r="4" fill="{t["gold"]}" class="beacon"/>')

    # ---- stats list (left) and languages (right)
    repos = data["repositories"]
    stars = sum(n["stargazerCount"] for n in repos["nodes"])
    items = [
        ("star", "Estrellas", stars),
        ("commit", "Commits · 12 meses", cc["totalCommitContributions"]),
        ("pr", "Pull requests · 12 meses", cc["totalPullRequestContributions"]),
        ("issue", "Issues · 12 meses", cc["totalIssueContributions"]),
        ("calendar", "Contribuciones · 12 meses", cal["totalContributions"]),
    ]
    y0 = 414
    rows = []
    for i, (ic, label, value) in enumerate(items):
        y = y0 + i * 38
        svg_icon = STAT_ICONS[ic].format(s=f'fill="none" stroke="{t["accent"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"', c=t["accent"])
        rows.append(f'<g transform="translate(48,{y - 14})">{svg_icon}</g>'
                    f'<text x="80" y="{y}" class="sans" font-size="17" fill="{t["muted"]}">{esc(label)}</text>'
                    f'<text x="590" y="{y}" text-anchor="end" class="sans" font-weight="700" font-size="17" fill="{t["text"]}">{value:,}</text>')

    sizes: dict = {}
    for node in repos["nodes"]:
        for edge in node["languages"]["edges"]:
            sizes[edge["node"]["name"]] = sizes.get(edge["node"]["name"], 0) + edge["size"]
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:5]
    total = sum(v for _, v in sizes.items()) or 1
    ramp = [t["accent"], t["accent2"], t["soft"], t["levels"][1], t["alt"]]
    langs = [f'<text x="690" y="{y0 - 34}" class="mono" font-size="13" letter-spacing="1" fill="{t["muted"]}">LENGUAJES</text>']
    for i, (lang, size) in enumerate(top):
        y = y0 + i * 38
        pct = 100 * size / total
        langs.append(f'<text x="690" y="{y - 6}" class="sans" font-size="16" fill="{t["text"]}">{esc(lang)}</text>'
                     f'<text x="1232" y="{y - 6}" text-anchor="end" class="mono" font-size="14" fill="{t["muted"]}">{pct:.1f}%</text>'
                     f'<rect x="690" y="{y + 2}" width="542" height="6" rx="3" fill="{t["empty"]}"/>'
                     f'<rect x="690" y="{y + 2}" width="{max(542 * pct / 100, 6):.1f}" height="6" rx="3" fill="{ramp[i]}" class="grow" style="animation-delay:{0.6 + 0.1 * i:.1f}s"/>')

    # ---- big numbers
    cur, longest = streaks(all_days)
    all_total = sum(d["contributionCount"] for d in all_days)
    since = all_days[0]["date"][:4] if all_days else ""
    def days_label(n: int) -> str:
        return f"{n} día" if n == 1 else f"{n} días"

    bigs = [(f"{all_total:,}", f"contribuciones desde {since}"), (days_label(cur), "racha actual"), (days_label(longest), "racha más larga")]
    big_svg = []
    for i, (value, label) in enumerate(bigs):
        cx = 48 + (W - 96) * (i + 0.5) / 3
        big_svg.append(f'<text x="{cx:.0f}" y="676" text-anchor="middle" class="sans" font-weight="800" font-size="44" fill="{t["accent"]}">{esc(value)}</text>'
                       f'<text x="{cx:.0f}" y="706" text-anchor="middle" class="sans" font-size="16" fill="{t["muted"]}">{esc(label)}</text>')
        if i:
            x = 48 + (W - 96) * i / 3
            big_svg.append(f'<line x1="{x:.0f}" y1="628" x2="{x:.0f}" y2="716" stroke="{t["border"]}" stroke-width="1.5"/>')

    last_active = next((d["date"] for d in reversed(all_days) if d["contributionCount"]), None)
    stamp = f"última actividad · {human_date(last_active)}" if last_active else ""
    style = BASE_STYLE + f"""
    .b {{ transform-box: fill-box; transform-origin: 50% 100%; animation: rise 1s cubic-bezier(.2,.8,.2,1) both; }}
    @keyframes rise {{ from {{ transform: scaleY(0) }} to {{ transform: scaleY(1) }} }}
    .beacon {{ animation: beacon 2s ease-in-out infinite; }}
    @keyframes beacon {{ 0%,100% {{ opacity: .35 }} 50% {{ opacity: 1 }} }}
    .grow {{ transform-box: fill-box; transform-origin: 0 50%; animation: grow 1s ease-out both; }}
    @keyframes grow {{ from {{ transform: scaleX(0) }} to {{ transform: scaleX(1) }} }}
    """
    body = f"""
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="{t['surface']}" stroke="{t['border']}" stroke-width="2"/>
  <text x="48" y="50" class="sans" font-weight="700" font-size="20" fill="{t['text']}">Mi año como ciudad</text>
  <text x="{W - 48}" y="50" text-anchor="end" class="mono" font-size="12" fill="{t['muted']}">{esc(stamp)}</text>
  <polygon points="{ground}" fill="{t['bg2']}" stroke="{t['border']}"/>
  {''.join(buildings)}
  <text x="48" y="336" class="mono" font-size="12" fill="{t['muted']}">cada edificio es un día · la altura son las contribuciones · el más alto lleva luz dorada</text>
  <line x1="48" y1="356" x2="{W - 48}" y2="356" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="48" y="{y0 - 34}" class="mono" font-size="13" letter-spacing="1" fill="{t['muted']}">ACTIVIDAD</text>
  {''.join(rows)}
  {''.join(langs)}
  <line x1="48" y1="604" x2="{W - 48}" y2="604" stroke="{t['border']}" stroke-width="1.5"/>
  {''.join(big_svg)}
"""
    alt = (f"Mis contribuciones del último año como una ciudad 3D. {cal['totalContributions']} contribuciones en 12 meses, "
           f"{all_total} desde {since}, racha más larga de {longest} días.")
    return svg_doc(W, H, body, style, alt)


def main() -> None:
    data = fetch()
    cal = data["contributionsCollection"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]]
    all_days = fetch_all_days(sorted(data["contributionsCollection"]["contributionYears"]))
    os.makedirs(OUT, exist_ok=True)
    for mode, t in THEMES.items():
        write(os.path.join(OUT, f"pacman-{mode}.svg"), pacman(t, weeks, cal["totalContributions"]))
        write(os.path.join(OUT, f"stats-{mode}.svg"), stats_city(t, data, weeks, all_days))


if __name__ == "__main__":
    main()
