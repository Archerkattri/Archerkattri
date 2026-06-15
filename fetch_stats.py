#!/usr/bin/env python3
"""Fetch account-wide GitHub stats and write them to live.json.

Companion to gen_readme.py. There are three kinds of dynamic content on this
profile, and this script owns the third:

  1. Live shields / github-readme-stats widgets that refresh on every page view
     (PyPI version + downloads, per-repo stars, followers, public-repo count,
     the stats card). Those need no script.
  2. Curated benchmark numbers that have no public API (ADD-S, F-scores, Hit@k).
     Those live in data.json and are stamped by gen_readme.py.
  3. Account-wide numbers that DO have an API but no honest single-URL shields
     path, the headline example being "total stars earned" summed across every
     repo. This script computes those from the GitHub REST API and writes them
     to live.json; gen_readme.py then stamps them into the AUTOGEN regions.

Why commit a number instead of using a live badge? GitHub proxies README images
through camo and caches them, so a "live on page view" badge can render stale for
a long time. A number computed on a cron and committed to the repo is never
mis-cached and never needs hand-editing. .github/workflows/refresh-stats.yml runs
this every 6 hours (and on demand) and commits the refreshed live.json + README.

No third-party dependencies (urllib only). Uses GITHUB_TOKEN when present to lift
the rate limit from 60/hr to 5000/hr; runs unauthenticated for local use.

Usage:
    python fetch_stats.py            # rewrite live.json from the live API
    GH_USER=someone python fetch_stats.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE_PATH = HERE / "live.json"

USER = os.environ.get("GH_USER", "Archerkattri")
API = "https://api.github.com"
TIMEOUT = 30


def _get(url: str):
    """GET a GitHub API URL as JSON. Sends a token if one is in the environment."""
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USER}-profile-stats",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_repos() -> list[dict]:
    """All repos owned by USER (paginated, 100/page, owner-only, includes forks)."""
    repos: list[dict] = []
    page = 1
    while True:
        batch = _get(f"{API}/users/{USER}/repos?per_page=100&type=owner&page={page}")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.2)  # be gentle on the API between pages
    return repos


def main() -> int:
    try:
        user = _get(f"{API}/users/{USER}")
        repos = fetch_repos()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:200]
        print(f"fetch_stats: HTTP {exc.code} from GitHub API: {body}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"fetch_stats: network error reaching GitHub API: {exc}", file=sys.stderr)
        return 1

    # "Total stars earned" counts stars on repos the account owns, not forks
    # (a fork's stars belong to its upstream). This matches how the
    # github-readme-stats card computes "Total Stars Earned".
    owned = [r for r in repos if not r.get("fork")]
    total_stars = sum(r.get("stargazers_count", 0) for r in owned)
    total_forks = sum(r.get("forks_count", 0) for r in owned)
    now = datetime.now(timezone.utc)

    live = {
        "_comment": (
            "MACHINE-WRITTEN by fetch_stats.py on a 6-hour cron "
            "(.github/workflows/refresh-stats.yml). Do not hand-edit: your change "
            "is overwritten on the next refresh. Curated, API-less numbers live in "
            "data.json instead. gen_readme.py stamps both into README.md."
        ),
        "user": USER,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "original_repos": len(owned),
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "updated": now.strftime("%Y-%m-%d"),
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    LIVE_PATH.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
    print(
        f"live.json: {total_stars} stars across {len(owned)} owned repos, "
        f"{user.get('followers', 0)} followers, {user.get('public_repos', 0)} "
        f"public repos, updated {live['updated']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
