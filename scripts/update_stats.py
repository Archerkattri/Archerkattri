#!/usr/bin/env python3
"""Render a self-contained live GitHub stats card to assets/stats.svg.

Runs ON GitHub's servers (.github/workflows/live-stats.yml), every ~5 minutes and
the instant someone stars the profile repo. It fetches the numbers straight from
the GitHub API and draws them into an SVG that is committed to the repo. Because a
committed file busts GitHub's page/image cache, the numbers actually change when
they change, unlike third-party widget images which sit behind GitHub's camo proxy
and look frozen.

There is a single source of truth (this script's fetch), so no two numbers can ever
disagree. Nothing runs on a personal machine; the only dependency is Python stdlib.

Why not "real time to the second"? You cannot: GitHub caches the rendered README and
proxies images. Every 5 minutes (GitHub Actions' minimum cron) plus on-star is the
fastest a GitHub profile can honestly refresh.

Env:
  GH_USER        GitHub login to render (default: Archerkattri)
  GITHUB_TOKEN   required for the GraphQL call (provided automatically in Actions)
  STATS_MOCK     if set to a JSON object, skip the API and render those numbers
                 (used to seed the first card and for local preview/tests)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SVG_PATH = ASSETS / "stats.svg"
JSON_PATH = ASSETS / "stats.json"

USER = os.environ.get("GH_USER", "Archerkattri")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
API = "https://api.github.com"

# Theme: teal #3ebfc6 / carbon #0C0D10 / grey #8a93a0, matching assets/banner.svg.
BG, GRID, TEAL, CREAM, TEXT, GREY = (
    "#0C0D10", "#1b1e24", "#3ebfc6", "#E9E4D6", "#c9d1d9", "#8a93a0",
)
# Fallback colours for common languages when the API doesn't supply one.
LANG_COLORS = {
    "Python": "#3572A5", "Jupyter Notebook": "#DA5B0B", "C++": "#f34b7d",
    "Cuda": "#3A4E3A", "JavaScript": "#f1e05a", "CSS": "#663399",
    "HTML": "#e34c26", "Shell": "#89e051", "C": "#555555", "TypeScript": "#3178c6",
}

# Published packages, for the aggregate download/install count.
PYPI_PKGS = ("splatreg", "certflow", "mathlas-mcp", "hicache-pp", "aura-splat", "toothprint")
COMFY_NODES = ("comfyui-hicache", "comfyui-trellis-hicache", "comfyui-trellis2-hicache")


def _get_public(url: str):
    """Unauthenticated JSON GET; None on any failure (kept out of the GitHub path)."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": f"{USER}-live-stats", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def fetch_downloads(prior: int = 0) -> int:
    """Aggregate reach = PyPI all-time (pepy) + Comfy registry installs.

    Monotonic: downloads only ever grow, so we return max(fetched, prior). A
    transient API miss (pepy rate-limits) therefore keeps the last good number
    instead of dropping the card to a smaller value.
    """
    total = 0
    for pkg in PYPI_PKGS:
        d = _get_public(f"https://api.pepy.tech/api/v2/projects/{pkg}")
        if d and isinstance(d.get("total_downloads"), int):
            total += d["total_downloads"]
    for nid in COMFY_NODES:
        d = _get_public(f"https://api.comfy.org/nodes/{nid}")
        if d and isinstance(d.get("downloads"), int):
            total += d["downloads"]
    return max(total, prior)


# --------------------------------------------------------------------------- API

def _req(url: str, data: bytes | None = None, accept: str = "application/vnd.github+json"):
    headers = {
        "Accept": accept,
        "User-Agent": f"{USER}-live-stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _graphql(query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    out = _req(f"{API}/graphql", data=body)
    if "errors" in out:
        raise RuntimeError(f"GraphQL errors: {out['errors']}")
    return out["data"]


_QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def _search_count(qualifier: str) -> int | None:
    """All-time count via the search API; None if it is unavailable/rate-limited."""
    from urllib.parse import quote
    try:
        which = "commits" if qualifier.startswith("commits") else "issues"
        q = quote(f"author:{USER}" + ("" if which == "commits" else " type:pr"))
        out = _req(f"{API}/search/{which}?q={q}&per_page=1")
        return int(out.get("total_count", 0))
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError):
        return None


def fetch_stats() -> dict:
    if not TOKEN:
        raise SystemExit("update_stats: GITHUB_TOKEN is required (run in GitHub Actions).")
    data = _graphql(_QUERY, {"login": USER})
    user = data["user"]
    repos = user["repositories"]["nodes"]

    stars = sum(r["stargazerCount"] for r in repos)
    # Aggregate language bytes across all owned repos.
    bytes_by_lang: dict[str, int] = {}
    color_by_lang: dict[str, str] = {}
    for r in repos:
        for edge in r["languages"]["edges"]:
            name = edge["node"]["name"]
            bytes_by_lang[name] = bytes_by_lang.get(name, 0) + edge["size"]
            if edge["node"].get("color"):
                color_by_lang[name] = edge["node"]["color"]
    total_bytes = sum(bytes_by_lang.values()) or 1
    languages = [
        {"name": n, "pct": round(100 * b / total_bytes, 1),
         "color": color_by_lang.get(n) or LANG_COLORS.get(n, GREY)}
        for n, b in sorted(bytes_by_lang.items(), key=lambda kv: kv[1], reverse=True)
    ][:6]

    # All-time counts via search; if search is unavailable, fall back to the
    # GraphQL contribution totals (last 12 months) so the card never shows 0.
    cc = user["contributionsCollection"]
    commits = _search_count("commits")
    if commits is None:
        commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    prs = _search_count("prs")
    if prs is None:
        prs = cc["totalPullRequestContributions"]
    prior_dl = 0
    try:
        prior_dl = int(json.loads(JSON_PATH.read_text(encoding="utf-8")).get("downloads", 0))
    except Exception:
        prior_dl = 0
    return {
        "name": user.get("name") or USER,
        "stars": stars,
        "downloads": fetch_downloads(prior_dl),
        "commits": commits,
        "prs": prs,
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "languages": languages,
    }


# ----------------------------------------------------------------------- render

def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(n: int) -> str:
    return f"{n:,}"


def build_svg(stats: dict) -> str:
    W, H, PAD = 854, 232, 28
    cells = [
        ("stars", "Stars"), ("downloads", "Downloads"),
        ("commits", "Commits"), ("prs", "Pull requests"),
        ("repos", "Repos"), ("followers", "Followers"),
    ]
    cell_w = (W - 2 * PAD) / len(cells)
    num_y, lab_y = 122, 145

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Live GitHub stats for {_esc(USER)}">'
    )
    parts.append(
        '<defs><pattern id="g" width="34" height="34" patternUnits="userSpaceOnUse">'
        f'<path d="M 34 0 L 0 0 0 34" fill="none" stroke="{GRID}" stroke-width="1"/>'
        '</pattern></defs>'
    )
    parts.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')
    parts.append(f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)"/>')
    parts.append(
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" '
        f'fill="none" stroke="{GRID}" stroke-width="1"/>'
    )
    # Title + animated LIVE indicator (proves it self-updates).
    parts.append(
        f'<text x="{PAD}" y="46" font-family="Georgia,serif" font-size="23" '
        f'font-weight="600" fill="{CREAM}">{_esc(str(stats.get("name") or USER))}</text>'
        f'<text x="{PAD}" y="67" font-family="ui-monospace,Menlo,monospace" '
        f'font-size="11.5" fill="{GREY}">LIVE GITHUB STATS &#183; SELF-SYNCED ON GITHUB ACTIONS</text>'
    )
    dot_x = W - PAD - 52
    parts.append(
        f'<circle cx="{dot_x}" cy="42" r="4.5" fill="{TEAL}">'
        '<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/>'
        '</circle>'
        f'<circle cx="{dot_x}" cy="42" r="4.5" fill="none" stroke="{TEAL}" stroke-width="1.4">'
        '<animate attributeName="r" values="4.5;11" dur="1.6s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0.6;0" dur="1.6s" repeatCount="indefinite"/>'
        '</circle>'
        f'<text x="{W-PAD}" y="46" text-anchor="end" font-family="ui-monospace,Menlo,monospace" '
        f'font-size="12" font-weight="600" fill="{TEAL}">LIVE</text>'
    )
    # Stat cells.
    for i, (key, label) in enumerate(cells):
        cx = PAD + cell_w * (i + 0.5)
        parts.append(
            f'<text x="{cx:.1f}" y="{num_y}" text-anchor="middle" '
            f'font-family="Georgia,serif" font-size="32" font-weight="700" '
            f'fill="{TEAL}">{_fmt(int(stats.get(key, 0)))}</text>'
            f'<text x="{cx:.1f}" y="{lab_y}" text-anchor="middle" '
            f'font-family="ui-monospace,Menlo,monospace" font-size="11.5" '
            f'fill="{GREY}">{_esc(label)}</text>'
        )
        if i:
            sep_x = PAD + cell_w * i
            parts.append(
                f'<line x1="{sep_x:.1f}" y1="100" x2="{sep_x:.1f}" y2="150" '
                f'stroke="{GRID}" stroke-width="1"/>'
            )
    # Language bar.
    langs = stats.get("languages") or []
    bar_x, bar_y, bar_w, bar_h = PAD, 172, W - 2 * PAD, 9
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="4.5" fill="{GRID}"/>')
    x = float(bar_x)
    total_pct = sum(l["pct"] for l in langs) or 100
    for j, lang in enumerate(langs):
        seg = bar_w * lang["pct"] / total_pct
        rx_l = 4.5 if j == 0 else 0
        rx_r = 4.5 if j == len(langs) - 1 else 0
        # simple rect; rounded ends approximated by the underlying rounded track
        parts.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{max(seg,0):.1f}" height="{bar_h}" '
            f'fill="{lang["color"]}"/>'
        )
        x += seg
    # Legend.
    lx, ly = PAD, 200
    for lang in langs[:5]:
        parts.append(
            f'<circle cx="{lx+4:.1f}" cy="{ly-4}" r="4" fill="{lang["color"]}"/>'
            f'<text x="{lx+13:.1f}" y="{ly}" font-family="ui-monospace,Menlo,monospace" '
            f'font-size="11" fill="{TEXT}">{_esc(lang["name"])} {lang["pct"]}%</text>'
        )
        lx += 18 + (len(lang["name"]) + len(str(lang["pct"])) + 2) * 6.6
    # Footer cadence note.
    parts.append(
        f'<text x="{W-PAD}" y="{H-12}" text-anchor="end" '
        f'font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{GREY}">'
        f'auto-synced every ~5 min &#183; GitHub Actions</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ------------------------------------------------------------------------- main

def main() -> int:
    mock = os.environ.get("STATS_MOCK")
    stats = json.loads(mock) if mock else fetch_stats()

    ASSETS.mkdir(exist_ok=True)
    # stats.json is the diff anchor: the workflow commits only when it changes,
    # so an unchanged 5-minute run produces no commit (no history spam). It holds
    # no timestamp for exactly that reason.
    JSON_PATH.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SVG_PATH.write_text(build_svg(stats), encoding="utf-8")
    print(
        f"stats: {stats['stars']} stars, {stats.get('downloads', 0):,} downloads, "
        f"{stats['commits']} commits, {stats['prs']} PRs, {stats['repos']} repos, "
        f"{stats['followers']} followers, {len(stats.get('languages', []))} languages "
        f"(rendered {datetime.now(timezone.utc):%Y-%m-%d %H:%M}Z)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
