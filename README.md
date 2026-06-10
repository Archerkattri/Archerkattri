<p align="center">
  <img src="assets/banner.svg" alt="Krishi Attri — I give robots a sense of touch. Visuo-tactile SLAM, 3D Gaussian splatting, verifiable AI tooling." width="100%">
</p>

<p align="center">
  <a href="https://archerkattri.github.io"><img src="https://img.shields.io/badge/portfolio-archerkattri.github.io-3ebfc6?style=flat-square" alt="Portfolio"></a>
  <a href="mailto:krishiattriwork@gmail.com"><img src="https://img.shields.io/badge/email-krishiattriwork%40gmail.com-E9E4D6?style=flat-square&labelColor=0C0D10" alt="Email"></a>
  <img src="https://img.shields.io/badge/SNU%20SRBL-%E2%86%92%20UCF%20Ph.D.-8a93a0?style=flat-square&labelColor=0C0D10" alt="SNU to UCF">
</p>

Robotics & AI — I build research systems that ship as real libraries: visuo-tactile perception, 3D Gaussian splatting, and tools that make AI **verifiable** instead of plausible.

## Shipped

| | what it does | the number that matters |
|---|---|---|
| 🧩 [**splatreg**](https://github.com/Archerkattri/splatreg) <br> <a href="https://pypi.org/project/splatreg/"><img src="https://img.shields.io/pypi/v/splatreg?style=flat-square&color=3ebfc6" alt="PyPI"></a> <a href="https://doi.org/10.5281/zenodo.20618389"><img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20618389-8a93a0?style=flat-square" alt="DOI"></a> | Register Gaussian splats — align & merge two 3DGS scans into one SE(3)/Sim(3) frame, recover scale, dedupe the overlap. CLI + pure-PyTorch API. [Docs.](https://archerkattri.github.io/splatreg/) | **91.5%** official 3DMatch recall · splat-merge Chamfer **10.3 → 2.0 mm** vs naive concat · photometric refine **5° → 0.36°** where geometry under-constrains |
| 📐 [**mathlas**](https://github.com/Archerkattri/mathlas) <br> <a href="https://pypi.org/project/mathlas-mcp/"><img src="https://img.shields.io/pypi/v/mathlas-mcp?style=flat-square&color=3ebfc6" alt="PyPI"></a> <a href="https://glama.ai/mcp/servers/Archerkattri/mathlas"><img src="https://glama.ai/mcp/servers/Archerkattri/mathlas/badges/score.svg" alt="Glama score" height="20"></a> <a href="https://doi.org/10.5281/zenodo.20618603"><img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20618603-8a93a0?style=flat-square" alt="DOI"></a> | Airtight math an AI *uses* over MCP — 3.7M-theorem search, PSLQ constant ID, OEIS, **real Lean kernel checks**, applicability checklists. No LLM inside, no API key. `claude mcp add mathlas -- uvx mathlas-mcp` | Beats TheoremSearch on its own 110 human queries (**59.1 vs 45.0** Hit@20) · mathlib formal search **Hit@5 0.96** · zero false positives across every verification tier |
| ⚡ [**HiCache++**](https://github.com/Archerkattri/hicache-plus-plus) <br> <a href="https://pypi.org/project/hicache-pp/"><img src="https://img.shields.io/pypi/v/hicache-pp?style=flat-square&color=3ebfc6" alt="PyPI"></a> <a href="https://doi.org/10.5281/zenodo.20618824"><img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20618824-8a93a0?style=flat-square" alt="DOI"></a> | Training-free diffusion acceleration by **exponential** (Dynamic-Mode-Decomposition / Prony) feature forecasting — a drop-in basis upgrade to TaylorSeer/HiCache, plus a holdout `auto` mode that can't make things worse. | Exact on the feature-ODE class — error stays **flat** in skip horizon where polynomial bases diverge (4.7e-9 vs 6.5 at H=8) · `auto` detects basis misfit **120/120** |

<details>
<summary>⚙️ <b>The 13-adapter acceleration family</b> — HiCache/HiCache++ deployed on real 3D generators</summary>
<br>

| model | Hermite (HiCache) | DMD (HiCache++) | headline |
|---|---|---|---|
| TRELLIS v1 | [faster-trellis](https://github.com/Archerkattri/faster-trellis) | [faster-trellis-plus-plus](https://github.com/Archerkattri/faster-trellis-plus-plus) | 2.85× at equal-or-better F-score vs Fast-TRELLIS |
| TRELLIS.2-4B | [hermit-trellis2](https://github.com/Archerkattri/hermit-trellis2) · [fast-trellis2](https://github.com/Archerkattri/fast-trellis2) | [hermit-trellis2-plus-plus](https://github.com/Archerkattri/hermit-trellis2-plus-plus) | carved-hybrid sampler |
| Hunyuan3D-2 mini | [hunyuan2-plus](https://github.com/Archerkattri/hunyuan2-plus) | [hunyuan2-plus-plus](https://github.com/Archerkattri/hunyuan2-plus-plus) | exactly lossless at interval-5 (F 0.794 = 0.794) |
| Hunyuan3D-2.1 | [hunyuan2.1-plus](https://github.com/Archerkattri/hunyuan2.1-plus) | [hunyuan2.1-plus-plus](https://github.com/Archerkattri/hunyuan2.1-plus-plus) | DMD leads +0.13 F at i5, +0.24 at i6 |
| SAM 3D Objects | [sam3d-plus](https://github.com/Archerkattri/sam3d-plus) | [sam3d-plus-plus](https://github.com/Archerkattri/sam3d-plus-plus) | geometry-lossless (F1 = 1.000) to interval-6 at 1.56× |
| Fast-SAM3D | [fastsam3d-plus](https://github.com/Archerkattri/fastsam3d-plus) | [fastsam3d-plus-plus](https://github.com/Archerkattri/fastsam3d-plus-plus) | stacked accelerations |

</details>

## In the lab

🫳 **GaussianFeels** — real-time visuo-tactile 3D-Gaussian SLAM for in-hand manipulation. One object-centric Gaussian map serves tracking, reconstruction, rendering, and manipulation-facing geometry: **0.83 mm** ADD-S in simulation / **3.37 mm** on real hardware, ~**7.6×** faster than the neural-field baseline, **94%** sim-to-real reconstruction retention. M.S. thesis (SNU Soft Robotics & Bionics Lab) — *release upcoming.*

<p align="center">
  <sub>
    <a href="https://archerkattri.github.io">portfolio</a> ·
    <a href="https://archerkattri.github.io/splatreg/">splatreg docs</a> ·
    <a href="https://glama.ai/mcp/servers/Archerkattri/mathlas">mathlas on Glama</a> ·
    Seoul <code>37.46°N</code> → Orlando <code>28.60°N</code> · est. arrival Aug 2026
  </sub>
</p>
