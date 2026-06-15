#!/usr/bin/env python3
"""Inject curated numbers from data.json into AUTOGEN-marked regions of README.md.

Why this exists: the GitHub profile mixes two kinds of dynamic content.
  1. Live shields.io badges (PyPI version + downloads, GitHub stars). Those
     refresh on every page view and need no script. They are NOT touched here.
  2. Curated benchmark numbers that have no public API (ADD-S, F-scores, Hit@k,
     test counts, ...). Those live in data.json as the single source of truth and
     are stamped into README.md by this script.

Contract:
  * Only bytes BETWEEN matching markers change. Everything else (prose, banner,
    layout, live widgets, taglines) is left byte-for-byte identical.
  * Idempotent: running twice yields zero diff.
  * Each region is `<!-- AUTOGEN:key -->VALUE<!-- /AUTOGEN:key -->` where `key` is
    a dotted path into data.json (e.g. `libraries.splatreg.headline`).

Usage:
    python gen_readme.py            # rewrite README.md in place
    python gen_readme.py --check    # exit 1 if README.md is out of date (no write)

No em-dashes anywhere in output: use commas, parentheses, colons, or &rarr;.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data.json"
README_PATH = HERE / "README.md"

# Marker pair. The body is captured non-greedily so adjacent regions never merge.
# re.DOTALL lets a region span multiple lines (used by the adapter table block).
MARKER_RE = re.compile(
    r"(?P<open><!-- AUTOGEN:(?P<key>[A-Za-z0-9_.]+) -->)"
    r"(?P<body>.*?)"
    r"(?P<close><!-- /AUTOGEN:(?P=key) -->)",
    re.DOTALL,
)

# A few values are embedded inside a shields.io URL, so the raw number cannot be
# wrapped by a marker without breaking the link. For those keys the marker wraps
# the whole <img> tag and we rebuild the tag from a template, keeping the number
# itself in data.json as the single source of truth. The badge style is the
# existing teal/carbon theme (style=flat-square, labelColor=0C0D10); do not edit
# the colors here without matching the rest of the README.
def _count_badge(label_text: str, color: str) -> str:
    # shields.io label encoding: '-' -> '--', ' ' -> '_', '+' -> '%2B'.
    # Order matters: escape '-' before inserting '--', and encode '+' last.
    enc = label_text.replace("-", "--").replace(" ", "_").replace("+", "%2B")
    return (
        f'<img src="https://img.shields.io/badge/-{enc}-{color}'
        f'?style=flat-square&labelColor=0C0D10" alt="">'
    )


# NOTE: counts.open_source_repos used to live here but was retired on 2026-06-15.
# The public-repo count is now a LIVE shields dynamic/json badge in README.md
# (reads users/Archerkattri.public_repos from the GitHub API on each page view),
# so it is no longer generator-driven. Only genuinely API-less curated counts stay.
TEMPLATED = {
    "counts.libraries_launched": lambda v: _count_badge(f"{v} libraries launched", "3ebfc6"),
}


def resolve(data: dict, dotted_key: str):
    """Walk a dotted path into nested dicts. Keys starting with '_' are metadata."""
    node = data
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(
                f"data.json has no value for AUTOGEN key '{dotted_key}' "
                f"(failed at segment '{part}')"
            )
        node = node[part]
    if isinstance(node, (dict, list)):
        raise TypeError(
            f"AUTOGEN key '{dotted_key}' resolves to a {type(node).__name__}, "
            f"not a scalar. Point the marker at a leaf value."
        )
    return str(node)


def render(text: str, data: dict) -> str:
    """Replace each AUTOGEN region body with its data.json value."""
    seen: set[str] = set()

    def _sub(m: re.Match) -> str:
        key = m.group("key")
        if key in seen:
            raise ValueError(
                f"Duplicate AUTOGEN marker for key '{key}'. Each key must appear once."
            )
        seen.add(key)
        raw = resolve(data, key)
        value = TEMPLATED[key](raw) if key in TEMPLATED else raw
        return f"{m.group('open')}{value}{m.group('close')}"

    return MARKER_RE.sub(_sub, text)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if README.md is stale (for a pre-commit hook or CI)",
    )
    args = ap.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    original = README_PATH.read_text(encoding="utf-8")
    updated = render(original, data)

    n_regions = len(seen_keys(original))
    if n_regions == 0:
        print(
            "warning: no <!-- AUTOGEN:key --> markers found in README.md; nothing to do.",
            file=sys.stderr,
        )

    if args.check:
        if updated != original:
            print(
                "README.md is out of date. Run `python gen_readme.py` to regenerate.",
                file=sys.stderr,
            )
            return 1
        print(f"README.md is up to date ({n_regions} AUTOGEN regions).")
        return 0

    if updated == original:
        print(f"README.md already current ({n_regions} AUTOGEN regions); no change.")
        return 0

    README_PATH.write_text(updated, encoding="utf-8")
    print(f"README.md regenerated ({n_regions} AUTOGEN regions stamped).")
    return 0


def seen_keys(text: str) -> list[str]:
    return [m.group("key") for m in MARKER_RE.finditer(text)]


if __name__ == "__main__":
    raise SystemExit(main())
