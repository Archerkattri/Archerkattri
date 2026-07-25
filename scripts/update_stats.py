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
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SVG_PATH = ASSETS / "stats.svg"
REACH_PATH = ASSETS / "reach.svg"
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
PYPI_PKGS = (
    "splatreg", "certflow", "mathlas-mcp", "hicache-pp",
    "aura-splat", "toothprint", "actionshift", "stepback",
)
ZENODO_RECORDS = (20618389, 20618603, 20618824, 20631475, 21500723, 21500733, 21536385)


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


def _get_text(url: str) -> str | None:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": f"{USER}-live-stats", "Accept": "text/html"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        return None


def parse_pypi_last_month(page: str) -> int:
    match = re.search(r"Downloads last month:\s*([\d,]+)", page, re.IGNORECASE)
    if not match:
        raise ValueError("PyPI last-month count missing")
    return int(match.group(1).replace(",", ""))


def parse_pepy_lifetime_total(page: str) -> int:
    match = re.search(r'"name":"Total downloads","value":(\d+)', page)
    if not match:
        raise ValueError("Pepy lifetime count missing")
    return int(match.group(1))


def _new_pypi_package_lifetime(package: str) -> int | None:
    """Use the rolling count as lifetime only when the package is under 30 days old."""
    metadata = _get_public(f"https://pypi.org/pypi/{package}/json")
    page = _get_text(f"https://pypistats.org/packages/{package}")
    if not isinstance(metadata, dict) or not page:
        return None
    uploads = [
        file.get("upload_time_iso_8601")
        for files in metadata.get("releases", {}).values()
        for file in files
        if file.get("upload_time_iso_8601")
    ]
    if not uploads:
        return None
    first_upload = datetime.fromisoformat(min(uploads).replace("Z", "+00:00"))
    if datetime.now(timezone.utc) - first_upload > timedelta(days=30):
        return None
    try:
        return parse_pypi_last_month(page)
    except ValueError:
        return None


def personal_hugging_face_items(items: list[dict]) -> list[dict]:
    return [item for item in items if "gaussianfeels" not in item.get("id", "").lower()]


def is_mcp_so_listing(page: str, repository_url: str) -> bool:
    return "Project not found" not in page and f'href="{repository_url}"' in page


def _prior(prior: dict, key: str) -> int:
    return int(prior.get(key, 0))


def fetch_reach(prior: dict, release_downloads: int, release_stale: bool = False) -> dict:
    """Fetch each distribution counter independently without mixing time windows."""
    stale_sources = {"GitHub releases"} if release_stale else set()
    out = {
        "pypi_all": _prior(prior, "pypi_all"),
        "pypi_packages": len(PYPI_PKGS),
        "huggingface_all": _prior(prior, "huggingface_all"),
        "huggingface_30d": _prior(prior, "huggingface_30d"),
        "huggingface_assets": _prior(prior, "huggingface_assets"),
        "comfy_downloads": _prior(prior, "comfy_downloads"),
        "comfy_nodes": _prior(prior, "comfy_nodes"),
        "release_downloads": release_downloads,
        "zenodo_downloads": _prior(prior, "zenodo_downloads"),
        "zenodo_views": _prior(prior, "zenodo_views"),
        "mcp_listings": _prior(prior, "mcp_listings"),
    }

    pypi_counts = []
    for package in PYPI_PKGS:
        page = _get_text(f"https://pepy.tech/projects/{package}")
        if page:
            try:
                pypi_counts.append(parse_pepy_lifetime_total(page))
                continue
            except ValueError:
                pass
        new_package_total = _new_pypi_package_lifetime(package)
        if new_package_total is not None:
            pypi_counts.append(new_package_total)
    if len(pypi_counts) == len(PYPI_PKGS):
        out["pypi_all"] = sum(pypi_counts)
    else:
        stale_sources.add("PyPI")

    models = _get_public(
        "https://huggingface.co/api/models?author=kattri15&limit=100"
        "&expand=downloads&expand=downloadsAllTime"
    )
    datasets = _get_public(
        "https://huggingface.co/api/datasets?author=kattri15&limit=100"
        "&expand=downloads&expand=downloadsAllTime"
    )
    if isinstance(models, list) and isinstance(datasets, list):
        hf_items = personal_hugging_face_items(models + datasets)
        out["huggingface_all"] = sum(int(item.get("downloadsAllTime", 0)) for item in hf_items)
        out["huggingface_30d"] = sum(int(item.get("downloads", 0)) for item in hf_items)
        out["huggingface_assets"] = len(hf_items)
    else:
        stale_sources.add("Hugging Face")

    comfy = _get_public("https://api.comfy.org/publishers/archerkattri/nodes")
    if isinstance(comfy, list):
        out["comfy_downloads"] = sum(int(node.get("downloads", 0)) for node in comfy)
        out["comfy_nodes"] = len(comfy)
    else:
        stale_sources.add("Comfy")

    records = [_get_public(f"https://zenodo.org/api/records/{record}") for record in ZENODO_RECORDS]
    if all(isinstance(record, dict) for record in records):
        out["zenodo_downloads"] = sum(int(record.get("stats", {}).get("downloads", 0)) for record in records)
        out["zenodo_views"] = sum(int(record.get("stats", {}).get("views", 0)) for record in records)
    else:
        stale_sources.add("Zenodo")

    official = _get_public(
        "https://registry.modelcontextprotocol.io/v0.1/servers"
        "?search=io.github.Archerkattri/mathlas"
    )
    glama = _get_public("https://glama.ai/api/mcp/v1/servers/Archerkattri/mathlas")
    mcp_so = _get_text("https://chat.mcp.so/en/server/mathlas/Archerkattri")
    checks = [
        isinstance(official, dict) and any(
            item.get("server", {}).get("name") == "io.github.Archerkattri/mathlas"
            for item in official.get("servers", [])
        ),
        isinstance(glama, dict)
        and glama.get("repository", {}).get("url") == "https://github.com/Archerkattri/mathlas",
        bool(mcp_so) and is_mcp_so_listing(mcp_so, "https://github.com/Archerkattri/mathlas"),
    ]
    if official is not None and glama is not None and mcp_so is not None:
        out["mcp_listings"] = sum(bool(value) for value in checks)
    else:
        stale_sources.add("MCP")
    out["stale_sources"] = sorted(stale_sources)
    return out


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
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        nameWithOwner
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


def owner_contributions(contributors: list[dict], owner: str) -> int:
    owner_key = owner.lower()
    return sum(
        int(item.get("contributions", 0))
        for item in contributors
        if item.get("login", "").lower() == owner_key
    )


def _owned_repo_commits(repositories: list[dict], prior: int = 0) -> tuple[int, bool]:
    total = 0
    try:
        for repository in repositories:
            page = 1
            while True:
                try:
                    contributors = _req(
                        f"{API}/repos/{repository['nameWithOwner']}/contributors"
                        f"?anon=false&per_page=100&page={page}"
                    )
                except urllib.error.HTTPError as error:
                    if error.code == 409:
                        break
                    raise
                total += owner_contributions(contributors, USER)
                if len(contributors) < 100:
                    break
                page += 1
        return total, False
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError, TypeError):
        return prior, True


def _release_downloads(repositories: list[dict], prior: int = 0) -> tuple[int, bool]:
    total = 0
    try:
        for repository in repositories:
            page = 1
            while True:
                releases = _req(
                    f"{API}/repos/{repository['nameWithOwner']}/releases?per_page=100&page={page}"
                )
                total += sum(
                    int(asset.get("download_count", 0))
                    for release in releases
                    for asset in release.get("assets", [])
                )
                if len(releases) < 100:
                    break
                page += 1
        return total, False
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError, TypeError):
        return prior, True


def fetch_stats() -> dict:
    if not TOKEN:
        raise SystemExit("update_stats: GITHUB_TOKEN is required (run in GitHub Actions).")
    data = _graphql(_QUERY, {"login": USER})
    user = data["user"]
    repos = user["repositories"]["nodes"]
    try:
        prior = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception:
        prior = {}

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
    commits, commits_stale = _owned_repo_commits(repos, int(prior.get("commits", 0)))
    if not repos and commits == 0:
        commits = cc["totalCommitContributions"]
    prs = _search_count("prs")
    if prs is None:
        prs = cc["totalPullRequestContributions"]
    release_downloads, releases_stale = _release_downloads(
        repos, int(prior.get("release_downloads", 0))
    )
    stats = {
        "name": user.get("name") or USER,
        "stars": stars,
        "commits": commits,
        "prs": prs,
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "release_downloads": release_downloads,
        "languages": languages,
    }
    stats.update(fetch_reach(prior, release_downloads, releases_stale))
    if commits_stale:
        stats["stale_sources"] = sorted(set(stats["stale_sources"]) | {"GitHub commits"})
    return stats


# ----------------------------------------------------------------------- render

def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(n: int) -> str:
    return f"{n:,}"


def build_svg(stats: dict) -> str:
    W, H, PAD = 854, 232, 28
    cells = [
        ("stars", "Stars"), ("commits", "Authored commits"),
        ("prs", "Pull requests"), ("repos", "Owned repos"),
        ("followers", "Followers"), ("release_downloads", "Release downloads"),
    ]
    cell_w = (W - 2 * PAD) / len(cells)
    num_y, lab_y = 122, 145
    github_stale = [
        source for source in stats.get("stale_sources", [])
        if source.startswith("GitHub")
    ]
    sync_label = (
        f"CACHED FALLBACK · {', '.join(github_stale)}"
        if github_stale
        else "LIVE GITHUB STATS · SELF-SYNCED ON GITHUB ACTIONS"
    )

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
        f'font-size="11.5" fill="{GREY}">{_esc(sync_label)}</text>'
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


def build_reach_svg(stats: dict) -> str:
    """Render distribution counters without combining incompatible windows."""
    width, height, pad = 854, 224, 28
    cells = [
        ("pypi_all", "PyPI &#183; all time", f"{stats.get('pypi_packages', 0)} packages"),
        (
            "huggingface_all",
            "Hugging Face &#183; all time",
            f"{_fmt(int(stats.get('huggingface_30d', 0)))} in 30d",
        ),
        ("comfy_downloads", "Comfy &#183; all time", f"{stats.get('comfy_nodes', 0)} nodes"),
        ("release_downloads", "Release assets", "GitHub · all time"),
        ("zenodo_downloads", "Zenodo &#183; all time", f"{_fmt(int(stats.get('zenodo_views', 0)))} views"),
        ("mcp_listings", "MCP directories", "Official · Glama · mcp.so"),
    ]
    cell_w = (width - 2 * pad) / len(cells)
    stale_sources = stats.get("stale_sources", [])
    status_line = (
        f"CACHED FALLBACK · {', '.join(stale_sources)}"
        if stale_sources
        else "LIVE COUNTERS · EACH WINDOW LABELLED · NO MIXED TOTAL"
    )
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" '
            'aria-label="Live downloads and distribution reach for Krishi Attri">'
        ),
        (
            '<defs><pattern id="g" width="34" height="34" patternUnits="userSpaceOnUse">'
            f'<path d="M 34 0 L 0 0 0 34" fill="none" stroke="{GRID}" stroke-width="1"/>'
            '</pattern></defs>'
        ),
        f'<rect width="{width}" height="{height}" rx="14" fill="{BG}"/>',
        f'<rect width="{width}" height="{height}" rx="14" fill="url(#g)"/>',
        (
            f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="14" '
            f'fill="none" stroke="{GRID}" stroke-width="1"/>'
        ),
        (
            f'<text x="{pad}" y="43" font-family="Georgia,serif" font-size="22" '
            f'font-weight="600" fill="{CREAM}">Distribution reach</text>'
        ),
        (
            f'<text x="{pad}" y="64" font-family="ui-monospace,Menlo,monospace" '
            f'font-size="11" fill="{GREY}">{_esc(status_line)}</text>'
        ),
    ]
    for index, (key, label, note) in enumerate(cells):
        center = pad + cell_w * (index + 0.5)
        parts.extend([
            (
                f'<text x="{center:.1f}" y="119" text-anchor="middle" '
                f'font-family="Georgia,serif" font-size="29" font-weight="700" '
                f'fill="{TEAL}">{_fmt(int(stats.get(key, 0)))}</text>'
            ),
            (
                f'<text x="{center:.1f}" y="143" text-anchor="middle" '
                f'font-family="ui-monospace,Menlo,monospace" font-size="10.5" '
                f'fill="{TEXT}">{label}</text>'
            ),
            (
                f'<text x="{center:.1f}" y="161" text-anchor="middle" '
                f'font-family="ui-monospace,Menlo,monospace" font-size="9.5" '
                f'fill="{GREY}">{_esc(note)}</text>'
            ),
        ])
        if index:
            separator = pad + cell_w * index
            parts.append(
                f'<line x1="{separator:.1f}" y1="92" x2="{separator:.1f}" y2="166" '
                f'stroke="{GRID}" stroke-width="1"/>'
            )
    parts.append(
        f'<text x="{width-pad}" y="{height-16}" text-anchor="end" '
        f'font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{GREY}">'
        'PyPI/HF/Comfy/GitHub/Zenodo cumulative &#183; HF 30d shown separately &#183; MCP listing status</text>'
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
    REACH_PATH.write_text(build_reach_svg(stats), encoding="utf-8")
    print(
        f"stats: {stats['stars']} stars, {stats.get('pypi_all', 0):,} PyPI all-time, "
        f"{stats.get('huggingface_all', 0):,} HF all-time, "
        f"{stats.get('comfy_downloads', 0):,} Comfy downloads, "
        f"{stats['commits']} commits, {stats['prs']} PRs, {stats['repos']} repos, "
        f"{stats['followers']} followers, {len(stats.get('languages', []))} languages "
        f"(rendered {datetime.now(timezone.utc):%Y-%m-%d %H:%M}Z)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
