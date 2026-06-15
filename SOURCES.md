# Sources for the curated numbers in `data.json`

Every figure stamped into `README.md` by `gen_readme.py` is listed here with its
origin, so future updates are auditable. Live-API badges (PyPI version, PyPI
downloads/month, GitHub stars) are not listed: they refresh on page view and have
no manual value to source.

To update any number: edit `data.json`, then run `python gen_readme.py`.

## counts

| key | value | source |
|---|---|---|
| `counts.libraries_launched` | 4 | Curated subset: splatreg, mathlas, HiCache++, CERT-FLOW (the four launched + DOI-archived libraries shown in the Shipped table). No public API. |
| `counts.open_source_repos` | 20+ | Curated, conservative. GitHub API (`users/Archerkattri.public_repos`) reports 36 public repos, but 13 are forks, leaving 23 original. "20+" is the honest floor for original work. A live `public_repos` badge would display 36 (forks included), so this is intentionally generator-driven, not live. |

## libraries (Shipped table, "the number that matters" column)

| key | source |
|---|---|
| `libraries.splatreg.headline` | splatreg README / engrXiv paper (DOI 10.31224/7313). 3DMatch recall 91.5% on the official benchmark; splat-merge Chamfer 10.3 to 2.0 mm vs naive concat; photometric refinement 5 deg to 0.36 deg on geometry-underconstrained scenes. |
| `libraries.mathlas.headline` | mathlas README + retrieval eval. Hit@20 59.1 vs TheoremSearch 45.0 on TheoremSearch's own 110 human queries; mathlib formal search Hit@5 0.96; zero false positives across all verification tiers. |
| `libraries.hicache_pp.headline` | HiCache++ README / engrXiv paper (DOI 10.31224/7309). Feature-ODE class error 4.7e-9 (DMD) vs 6.5 (polynomial) at skip horizon H=8; `auto` basis-misfit detection 120/120. |
| `libraries.certflow.headline` | CERT-FLOW README / engrXiv paper (DOI 10.31224/7306). Conformal coverage at or above target on every reported condition incl. replayed METR-LA / PEMS-BAY; 223 tests; 16 reproduction pipelines; 7 theorems incl. an impossibility result. |

## adapters (13-adapter acceleration family table, "headline" column)

| key | source |
|---|---|
| `adapters.trellis_v1.headline` | faster-trellis benchmark: 2.85x at equal-or-better F-score vs Fast-TRELLIS. |
| `adapters.trellis2_4b.headline` | hermit-trellis2 / fast-trellis2: carved-hybrid sampler (descriptive, no single metric). |
| `adapters.hunyuan2_mini.headline` | hunyuan2-plus: exactly lossless at interval-5 (F 0.794 == 0.794). |
| `adapters.hunyuan2_1.headline` | hunyuan2.1-plus(-plus): DMD leads +0.13 F at interval-5, +0.24 at interval-6. |
| `adapters.sam3d.headline` | sam3d-plus(-plus): geometry-lossless (F1 = 1.000) to interval-6 at 1.56x. |
| `adapters.fastsam3d.headline` | fastsam3d-plus(-plus): stacked accelerations (descriptive, no single metric). |

## gaussianfeels (In the lab)

| key | value | source |
|---|---|---|
| `gaussianfeels.add_s_sim_mm` | 0.83 mm | GaussianFeels M.S. thesis, ADD-S in simulation. |
| `gaussianfeels.add_s_real_mm` | 3.37 mm | GaussianFeels M.S. thesis, ADD-S on real hardware. |
| `gaussianfeels.speedup_vs_neural_field` | 7.6x | GaussianFeels M.S. thesis, speedup vs neural-field baseline. |
| `gaussianfeels.sim2real_retention` | 94% | GaussianFeels M.S. thesis, sim-to-real reconstruction retention. |

## Live (not in this file, no manual maintenance)

- PyPI version: `img.shields.io/pypi/v/<pkg>` (splatreg, mathlas-mcp, hicache-pp, certflow)
- PyPI downloads/month: `img.shields.io/pypi/dm/<pkg>`
- GitHub stars: `img.shields.io/github/stars/Archerkattri/<repo>` (splatreg, mathlas, hicache-plus-plus, CERT-FLOW)
- github-readme-stats card, top-langs, activity graph, typing-svg header, Glama score badge.
