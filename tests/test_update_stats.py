import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import update_stats


class LiveStatsTests(unittest.TestCase):
    def test_parse_pepy_lifetime_total(self):
        html = (
            '<meta content="splatreg has been downloaded 5,205 times in total.">'
            '"variableMeasured":{"@type":"PropertyValue",'
            '"name":"Total downloads","value":5205}'
        )
        self.assertEqual(update_stats.parse_pepy_lifetime_total(html), 5205)

    def test_parse_pypi_last_month(self):
        html = "<p>Downloads last month:\n2,097<br></p>"
        self.assertEqual(update_stats.parse_pypi_last_month(html), 2097)

    def test_pypi_lifetime_counts_keep_per_package_values_and_new_package_fallback(self):
        pepy_page = '"name":"Total downloads","value":5205'
        pages = {
            "https://pepy.tech/projects/splatreg": pepy_page,
            "https://pepy.tech/projects/stepback": None,
        }
        counts = update_stats.fetch_pypi_lifetime_counts(
            ("splatreg", "stepback"),
            get_text=pages.get,
            new_package_lifetime=lambda package: 106 if package == "stepback" else None,
        )
        self.assertEqual(counts, {"splatreg": 5205, "stepback": 106})

    def test_mcp_so_requires_exact_repository_and_real_page(self):
        repo = "https://github.com/Archerkattri/mathlas"
        self.assertTrue(update_stats.is_mcp_so_listing(f'<a href="{repo}">source</a>', repo))
        self.assertFalse(
            update_stats.is_mcp_so_listing(
                "<title>mathlas Archerkattri</title><p>Project not found</p>", repo
            )
        )

    def test_hugging_face_school_assets_are_excluded(self):
        items = [
            {"id": "kattri15/actionshift", "downloads": 51, "downloadsAllTime": 51},
            {"id": "kattri15/gaussianfeels-thesis-data", "downloads": 500, "downloadsAllTime": 900},
        ]
        self.assertEqual(
            update_stats.personal_hugging_face_items(items),
            [items[0]],
        )

    def test_owned_repo_commits_ignore_other_contributors(self):
        contributors = [
            {"login": "other", "contributions": 500},
            {"login": "ARCHERKATTRI", "contributions": 37},
        ]
        self.assertEqual(
            update_stats.owner_contributions(contributors, "Archerkattri"),
            37,
        )

    def test_reach_svg_keeps_each_download_window_separate(self):
        stats = {
            "pypi_all": 16280,
            "pypi_packages": 7,
            "huggingface_all": 168,
            "huggingface_30d": 129,
            "huggingface_assets": 4,
            "comfy_downloads": 2356,
            "comfy_nodes": 3,
            "release_downloads": 111,
            "zenodo_downloads": 53,
            "zenodo_views": 288,
            "mcp_listings": 3,
        }
        svg = update_stats.build_reach_svg(stats)
        for text in (
            "PyPI &#183; all time",
            "Hugging Face &#183; all time",
            "Comfy &#183; all time",
            "Release assets",
            "Zenodo &#183; all time",
            "MCP directories",
            "16,280",
            "2,356",
        ):
            self.assertIn(text, svg)

    def test_reach_svg_discloses_cached_sources(self):
        svg = update_stats.build_reach_svg({
            "stale_sources": ["PyPI", "MCP"],
        })
        self.assertIn("CACHED FALLBACK", svg)
        self.assertIn("PyPI, MCP", svg)


if __name__ == "__main__":
    unittest.main()
