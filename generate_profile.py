#!/usr/bin/env python3
"""
Generates an animated terminal-style GitHub profile card (dark.svg + light.svg).

Everything you'd normally want to tweak lives in CONFIG / ASCII_ART / INFO below.
Stats (repos, stars, followers) are pulled live from the GitHub API when the
script runs in Actions; if the API is unreachable it silently falls back.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
USERNAME = "ChetanSenta"

PORTRAIT_COLOR_FILE = "portrait_color.json"  # [[ [hexcolor, char], ... ], ...] one list per row

def load_portrait_color():
    """Load the true-color ASCII portrait and merge consecutive same-color
    characters in each row into single runs, to keep the SVG lean."""
    f = Path(__file__).parent / PORTRAIT_COLOR_FILE
    if not f.exists():
        return []
    rows = json.loads(f.read_text(encoding="utf-8"))
    merged_rows = []
    for row in rows:
        runs = []
        for color, char in row:
            if runs and runs[-1][0] == color:
                runs[-1] = (color, runs[-1][1] + char)
            else:
                runs.append((color, char))
        merged_rows.append(runs)
    return merged_rows


# (label, value, colour-key)  |  colour-key: key / val / accent / warn / muted
INFO = [
    ("__header__", "Chetan Senta", ""),
    ("__rule__", "", ""),
    ("Role", "B.Tech Computer Engineering Student", "val"),
    ("Edu", "Charotar University of Science & Technology · CGPA 7.38/10", "val"),
    ("Focus", "Competitive Programming · Full-Stack Development", "accent"),
    ("__blank__", "", ""),
    ("__section__", "~/stack", ""),
    ("Languages", "C/C++ · Java · SQL · Python", "val"),
    ("Frontend", "HTML · CSS · JavaScript · React.js", "val"),
    ("Backend", "Node.js · Express.js", "val"),
    ("Database", "PostgreSQL · MySQL", "val"),
    ("Tools", "VS Code · GitHub · GitHub Copilot", "val"),
    ("__blank__", "", ""),
    ("__section__", "~/experience", ""),
    ("Oasis Infobyte", "Web Dev & Design Intern · React/Node/Express/MongoDB", "warn"),
    ("__blank__", "", ""),
    ("__section__", "~/projects", ""),
    ("Cashen", "Full-Stack Budget Tracker · Node/Express/PostgreSQL", "warn"),
    ("__blank__", "", ""),
    ("__section__", "~/certifications", ""),
    ("McKinsey", "Forward Program Badge · 2025", "val"),
    ("OCI", "2025 AI Foundations Associate", "val"),
    ("__blank__", "", ""),
    ("__section__", "~/achievements", ""),
    ("Codeforces", "Newbie · Max Rating 1068", "val"),
    ("LeetCode", "Max Rating 1473", "val"),
    ("CodeChef", "1-Star · Max Rating 1088", "val"),
    ("__blank__", "", ""),
    ("__section__", "~/reach", ""),
    ("GitHub", "github.com/ChetanSenta", "accent"),
    ("LinkedIn", "linkedin.com/in/chetansenta", "accent"),
    ("Mail", "chetansenta11@gmail.com", "accent"),
]

THEMES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "border": "#30363d",
        "text": "#c9d1d9", "muted": "#8b949e", "key": "#3fb950",
        "accent": "#58a6ff", "warn": "#d29922", "art": "#bc8cff",
        "prompt": "#3fb950", "dot1": "#ff5f56", "dot2": "#ffbd2e", "dot3": "#27c93f",
    },
    "light": {
        "bg": "#0d1117", "panel": "#161b22", "border": "#30363d",
        "text": "#c9d1d9", "muted": "#8b949e", "key": "#3fb950",
        "accent": "#58a6ff", "warn": "#d29922", "art": "#bc8cff",
        "prompt": "#3fb950", "dot1": "#ff5f56", "dot2": "#ffbd2e", "dot3": "#27c93f",
    },
}

W, H = 1160, 660
ART_X, ART_Y = 30, 86
ART_CW = 2.6           # forced char width (textLength keeps this exact in any font)
ART_LH = ART_CW * 1.72
INFO_X, INFO_Y, INFO_LH = 490, 92, 17.5
VAL_X = INFO_X + 140


# ----------------------------------------------------------------------------
# STATS
# ----------------------------------------------------------------------------
def fetch_stats():
    stats = {"repos": "-", "stars": "-", "followers": "-"}
    try:
        headers = {"User-Agent": "profile-readme"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        req = urllib.request.Request(
            f"https://api.github.com/users/{USERNAME}", headers=headers)
        user = json.load(urllib.request.urlopen(req, timeout=15))
        stats["repos"] = str(user.get("public_repos", 0))
        stats["followers"] = str(user.get("followers", 0))

        stars, page = 0, 1
        while page <= 5:
            req = urllib.request.Request(
                f"https://api.github.com/users/{USERNAME}/repos"
                f"?per_page=100&page={page}", headers=headers)
            repos = json.load(urllib.request.urlopen(req, timeout=15))
            if not repos:
                break
            stars += sum(r.get("stargazers_count", 0) for r in repos)
            page += 1
        stats["stars"] = str(stars)
    except Exception as e:  # offline / rate-limited -> keep placeholders
        print(f"[warn] stats fetch failed: {e}")
    return stats


# ----------------------------------------------------------------------------
# RENDER
# ----------------------------------------------------------------------------
def render(theme_name, colors, stats, ist_now):
    art_rows = load_portrait_color()

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, '
        f'\'JetBrains Mono\', \'Cascadia Code\', Menlo, Consolas, monospace">'
    )

    # styles + animations
    parts.append(f"""<style>
    .art  {{ font-size:4.2px; white-space:pre; }}
    .key  {{ fill:{colors['key']}; font-size:13px; font-weight:700; }}
    .val  {{ fill:{colors['text']}; font-size:13px; }}
    .acc  {{ fill:{colors['accent']}; font-size:13px; }}
    .wrn  {{ fill:{colors['warn']}; font-size:13px; }}
    .mut  {{ fill:{colors['muted']}; font-size:12px; }}
    .hdr  {{ fill:{colors['accent']}; font-size:15px; font-weight:700; }}
    .sec  {{ fill:{colors['muted']}; font-size:12px; letter-spacing:1px; }}
    .ttl  {{ fill:{colors['muted']}; font-size:12px; }}
    .row  {{ opacity:1; animation: fade .35s ease backwards; }}
    @keyframes fade {{ from {{ opacity:0; transform:translateY(3px); }}
                       to   {{ opacity:1; transform:translateY(0); }} }}
    .cur  {{ fill:{colors['prompt']}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    .artline {{ opacity:1; animation: fade .3s ease backwards; }}
    </style>""")

    # window chrome
    parts.append(
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" '
        f'fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>'
    )
    parts.append(
        f'<path d="M1 13 a12 12 0 0 1 12 -12 h{W-26} a12 12 0 0 1 12 12 v25 h{-(W-2)} z" '
        f'fill="{colors["panel"]}"/>'
    )
    parts.append(f'<line x1="1" y1="38" x2="{W-1}" y2="38" stroke="{colors["border"]}"/>')
    for i, c in enumerate(["dot1", "dot2", "dot3"]):
        parts.append(f'<circle cx="{24 + i*20}" cy="20" r="6" fill="{colors[c]}"/>')
    parts.append(
        f'<text x="{W/2}" y="24" class="ttl" text-anchor="middle">'
        f'{escape(USERNAME)} — zsh — 90×26</text>'
    )

    # command line
    parts.append(
        f'<text x="{ART_X}" y="66" class="row" style="animation-delay:.05s">'
        f'<tspan class="key">➜</tspan>'
        f'<tspan class="acc" dx="8">~</tspan>'
        f'<tspan class="val" dx="8">neofetch --profile</tspan></text>'
    )

    # ascii art (true color, from portrait_color.json)
    for i, runs in enumerate(art_rows):
        row_len = sum(len(chars) for _, chars in runs)
        if row_len == 0:
            continue
        y = ART_Y + i * ART_LH
        delay = 0.15 + i * 0.012
        tl = row_len * ART_CW
        tspans = "".join(
            f'<tspan fill="{color}">{escape(chars)}</tspan>' for color, chars in runs
        )
        parts.append(
            f'<text x="{ART_X}" y="{y:.1f}" class="art artline" xml:space="preserve" '
            f'textLength="{tl:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'style="animation-delay:{delay:.2f}s">{tspans}</text>'
        )

    # info block
    y = INFO_Y
    delay = 0.35
    cls_map = {"val": "val", "accent": "acc", "warn": "wrn", "muted": "mut"}

    for label, value, ckey in INFO:
        d = f'style="animation-delay:{delay:.2f}s"'
        if label == "__header__":
            parts.append(f'<text x="{INFO_X}" y="{y:.1f}" class="hdr row" {d}>{escape(value)}</text>')
            y += INFO_LH
        elif label == "__rule__":
            parts.append(
                f'<line x1="{INFO_X}" y1="{y-8:.1f}" x2="{W-40}" y2="{y-8:.1f}" '
                f'stroke="{colors["border"]}" class="row" {d}/>'
            )
            y += 8
        elif label == "__blank__":
            y += 10
            continue
        elif label == "__section__":
            parts.append(f'<text x="{INFO_X}" y="{y:.1f}" class="sec row" {d}>{escape(value)}</text>')
            y += INFO_LH
        elif label == "__stats__":
            stat_txt = (f'repos {stats["repos"]}   ·   stars {stats["stars"]}'
                        f'   ·   followers {stats["followers"]}')
            parts.append(
                f'<text x="{INFO_X}" y="{y:.1f}" class="row" {d}>'
                f'<tspan class="key">⚡</tspan>'
                f'<tspan class="val" dx="8">{escape(stat_txt)}</tspan></text>'
            )
            y += INFO_LH
        else:
            cls = cls_map.get(ckey, "val")
            if label:
                parts.append(
                    f'<text x="{INFO_X}" y="{y:.1f}" class="key row" {d}>{escape(label)}</text>'
                )
            parts.append(
                f'<text x="{VAL_X}" y="{y:.1f}" class="{cls} row" {d}>{escape(value)}</text>'
            )
            y += INFO_LH
        delay += 0.07

    # footer prompt + blinking cursor
    fy = H - 24
    parts.append(
        f'<text x="{ART_X}" y="{fy}" class="row" style="animation-delay:{delay+0.1:.2f}s">'
        f'<tspan class="key">➜</tspan>'
        f'<tspan class="acc" dx="8">~</tspan>'
        f'<tspan class="val" dx="8"> Competitive Programmer </tspan>'
        f'<tspan class="cur" dx="8">█</tspan></text>'
    )
    parts.append(
        f'<text x="{W-34}" y="{fy}" class="mut" text-anchor="end">'
        f'last updated {ist_now}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    stats = fetch_stats()
    ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    stamp = ist.strftime("%d %b %Y, %H:%M IST")
    out = Path(__file__).parent
    for name, colors in THEMES.items():
        (out / f"{name}.svg").write_text(render(name, colors, stats, stamp), encoding="utf-8")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
