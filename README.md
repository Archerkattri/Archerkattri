<p align="center">
  <img src="assets/banner.svg" alt="Krishi Attri — robotics, perception, verifiable AI tools" width="100%">
</p>

<p align="center">
  <a href="https://archerkattri.github.io"><img src="https://img.shields.io/badge/portfolio-archerkattri.github.io-3ebfc6?style=flat-square&labelColor=0C0D10" alt="Portfolio"></a>
  <a href="https://www.linkedin.com/in/krishi-attri15/"><img src="https://img.shields.io/badge/LinkedIn-Krishi%20Attri-3ebfc6?style=flat-square&labelColor=0C0D10&logo=linkedin&logoColor=3ebfc6" alt="LinkedIn"></a>
  <a href="mailto:krishiattriwork@gmail.com"><img src="https://img.shields.io/badge/email-krishiattriwork-E9E4D6?style=flat-square&labelColor=0C0D10" alt="Email"></a>
  <img src="https://img.shields.io/badge/SNU%20SRBL-%E2%86%92%20UCF%20Ph.D.-8a93a0?style=flat-square&labelColor=0C0D10" alt="SNU to UCF">
  <img src="https://komarev.com/ghpvc/?username=Archerkattri&style=flat-square&color=3ebfc6&label=views" alt="profile views">
</p>

<p align="center">
  <a href="https://github.com/Archerkattri">
    <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=21&pause=1100&color=3EBFC6&center=true&vCenter=true&width=660&height=40&lines=I+give+robots+a+sense+of+touch.;Visuo-tactile+SLAM+%2B+3D+Gaussian+splatting;Research+systems+that+ship+as+real+libraries;Making+AI+verifiable%2C+not+just+plausible." alt="what I work on">
  </a>
</p>

<p align="center">
  <sub>Robotics and AI. I build research systems that ship as real, installable libraries: visuo-tactile perception, 3D Gaussian splatting, and tooling that makes AI <b>verifiable</b> instead of plausible.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/-4_libraries_launched-3ebfc6?style=flat-square&labelColor=0C0D10" alt="">
  <img src="https://img.shields.io/badge/-20%2B_open--source_repos-8a93a0?style=flat-square&labelColor=0C0D10" alt="">
  <img src="https://img.shields.io/badge/-DOI--archived_%2B_on_PyPI-8a93a0?style=flat-square&labelColor=0C0D10" alt="">
</p>

---

<table align="center" border="0" cellspacing="0" cellpadding="0"><tr>
<td valign="top" width="50%">

<img src="https://github-readme-stats.vercel.app/api?username=Archerkattri&show_icons=true&include_all_commits=true&rank_icon=percentile&hide_border=true&title_color=3ebfc6&icon_color=3ebfc6&text_color=c9d1d9&bg_color=0C0D10" alt="GitHub stats">

</td>
<td valign="top" width="50%">

<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=Archerkattri&layout=compact&langs_count=8&hide_border=true&title_color=3ebfc6&text_color=c9d1d9&bg_color=0C0D10" alt="Top languages">

</td>
</tr></table>

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=Archerkattri&bg_color=0C0D10&color=c9d1d9&line=3ebfc6&point=ffffff&area=true&area_color=3ebfc6&hide_border=true&custom_title=Build%20activity" alt="Contribution activity" width="98%">
</p>

## ▌ Shipped

> Research that ends as something you can `pip install`, cite by DOI, and reproduce.

| | what it does | the number that matters |
|---|---|---|
| 🧩 [**splatreg**](https://github.com/Archerkattri/splatreg) <br> <a href="https://pypi.org/project/splatreg/"><img src="https://img.shields.io/pypi/v/splatreg?style=flat-square&color=3ebfc6&labelColor=0C0D10" alt="PyPI"></a> <a href="https://doi.org/10.5281/zenodo.20618389"><img src="https://img.shields.io/badge/DOI-zenodo-8a93a0?style=flat-square&labelColor=0C0D10" alt="DOI"></a> | Register Gaussian splats: align and merge two 3DGS scans into one SE(3)/Sim(3) frame, recover scale, dedupe the overlap. CLI plus a pure-PyTorch API. [Docs.](https://archerkattri.github.io/splatreg/) | **91.5%** official 3DMatch recall · splat-merge Chamfer **10.3 → 2.0 mm** vs naive concat · photometric refine **5° → 0.36°** where geometry under-constrains |
| 📐 [**mathlas**](https://github.com/Archerkattri/mathlas) <br> <a href="https://pypi.org/project/mathlas-mcp/"><img src="https://img.shields.io/pypi/v/mathlas-mcp?style=flat-square&color=3ebfc6&labelColor=0C0D10" alt="PyPI"></a> <a href="https://glama.ai/mcp/servers/Archerkattri/mathlas"><img src="https://glama.ai/mcp/servers/Archerkattri/mathlas/badges/score.svg" alt="Glama score" height="20"></a> <a href="https://doi.org/10.5281/zenodo.20618603"><img src="https://img.shields.io/badge/DOI-zenodo-8a93a0?style=flat-square&labelColor=0C0D10" alt="DOI"></a> | Airtight math an AI *uses* over MCP: 3.7M-theorem search, PSLQ constant ID, OEIS, **real Lean kernel checks**, applicability checklists. No LLM inside, no API key. `claude mcp add mathlas -- uvx mathlas-mcp` | Beats TheoremSearch on its own 110 human queries (**59.1 vs 45.0** Hit@20) · mathlib formal search **Hit@5 0.96** · zero false positives across every verification tier |
| ⚡ [**HiCache++**](https://github.com/Archerkattri/hicache-plus-plus) <br> <a href="https://pypi.org/project/hicache-pp/"><img src="https://img.shields.io/pypi/v/hicache-pp?style=flat-square&color=3ebfc6&labelColor=0C0D10" alt="PyPI"></a> <a href="https://doi.org/10.5281/zenodo.20618824"><img src="https://img.shields.io/badge/DOI-zenodo-8a93a0?style=flat-square&labelColor=0C0D10" alt="DOI"></a> | Training-free diffusion acceleration by **exponential** (Dynamic-Mode-Decomposition / Prony) feature forecasting: a drop-in basis upgrade to TaylorSeer/HiCache, plus a holdout `auto` mode that cannot make things worse. | Exact on the feature-ODE class: error stays **flat** across the skip horizon where polynomial bases diverge (4.7e-9 vs 6.5 at H=8) · `auto` detects basis misfit **120/120** |
| 🛣️ [**CERT-FLOW**](https://github.com/Archerkattri/CERT-FLOW) <br> <a href="https://pypi.org/project/certflow/"><img src="https://img.shields.io/pypi/v/certflow?style=flat-square&color=3ebfc6&labelColor=0C0D10" alt="PyPI"></a> <a href="https://doi.org/10.5281/zenodo.20631475"><img src="https://img.shields.io/badge/DOI-zenodo-8a93a0?style=flat-square&labelColor=0C0D10" alt="DOI"></a> | Certified route planning under drifting costs: every replanning round emits a conformal certificate **LB ≤ OPT ≤ UB** on the optimal route, directs paid sensing at the edges that shrink the certified gap fastest, and proof-gates the fast preprocessing. | Coverage at or above the claimed level on **every** reported condition including replayed METR-LA / PEMS-BAY traffic · 223 tests · 16 reproduction pipelines · 7 theorems including an impossibility result |

<details>
<summary>⚙️ <b>The 13-adapter acceleration family</b> : HiCache / HiCache++ on real 3D generators</summary>
<br>

| model | Hermite (HiCache) | DMD (HiCache++) | headline |
|---|---|---|---|
| TRELLIS v1 | [faster-trellis](https://github.com/Archerkattri/faster-trellis) | [faster-trellis-plus-plus](https://github.com/Archerkattri/faster-trellis-plus-plus) | 2.85× at equal-or-better F-score vs Fast-TRELLIS |
| TRELLIS.2-4B | [hermit-trellis2](https://github.com/Archerkattri/hermit-trellis2) · [fast-trellis2](https://github.com/Archerkattri/fast-trellis2) | [hermit-trellis2-plus-plus](https://github.com/Archerkattri/hermit-trellis2-plus-plus) | carved-hybrid sampler |
| Hunyuan3D-2 mini | [hunyuan2-plus](https://github.com/Archerkattri/hunyuan2-plus) | [hunyuan2-plus-plus](https://github.com/Archerkattri/hunyuan2-plus-plus) | exactly lossless at interval-5 (F 0.794 = 0.794) |
| Hunyuan3D-2.1 | [hunyuan2.1-plus](https://github.com/Archerkattri/hunyuan2.1-plus) | [hunyuan2.1-plus-plus](https://github.com/Archerkattri/hunyuan2.1-plus-plus) | DMD leads +0.13 F at i5, +0.24 at i6 |
| SAM 3D Objects | [sam3d-plus](https://github.com/Archerkattri/sam3d-plus) | [sam3d-plus-plus](https://github.com/Archerkattri/sam3d-plus-plus) | geometry-lossless (F1 = 1.000) to interval-6 at 1.56× |
| Fast-SAM3D | [fastsam3d-plus](https://github.com/Archerkattri/fastsam3d-plus) | [fastsam3d-plus-plus](https://github.com/Archerkattri/fastsam3d-plus-plus) | stacked accelerations |

ComfyUI nodes: [ComfyUI-HiCache](https://github.com/Archerkattri/ComfyUI-HiCache) · [ComfyUI-TRELLIS-HiCache](https://github.com/Archerkattri/ComfyUI-TRELLIS-HiCache) · [ComfyUI-TRELLIS2-HiCache](https://github.com/Archerkattri/ComfyUI-TRELLIS2-HiCache)

</details>

## ▌ In the lab

🫳 **GaussianFeels** : real-time visuo-tactile 3D-Gaussian SLAM for in-hand manipulation. One object-centric Gaussian map serves tracking, reconstruction, rendering, and manipulation-facing geometry at once. **0.83 mm** ADD-S in simulation, **3.37 mm** on real hardware, about **7.6×** faster than the neural-field baseline, **94%** sim-to-real reconstruction retention. M.S. thesis at the SNU Soft Robotics and Bionics Lab, release upcoming.

## ▌ Stack

<p>
  <img src="https://img.shields.io/badge/Python-161922?style=flat-square&logo=python&logoColor=3ebfc6" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-161922?style=flat-square&logo=pytorch&logoColor=3ebfc6" alt="PyTorch">
  <img src="https://img.shields.io/badge/CUDA-161922?style=flat-square&logo=nvidia&logoColor=3ebfc6" alt="CUDA">
  <img src="https://img.shields.io/badge/NumPy-161922?style=flat-square&logo=numpy&logoColor=3ebfc6" alt="NumPy">
  <img src="https://img.shields.io/badge/C%2B%2B-161922?style=flat-square&logo=cplusplus&logoColor=3ebfc6" alt="C++">
  <img src="https://img.shields.io/badge/Lean_4-161922?style=flat-square&logo=lean&logoColor=3ebfc6" alt="Lean">
  <img src="https://img.shields.io/badge/MCP-161922?style=flat-square&logo=anthropic&logoColor=3ebfc6" alt="MCP">
  <img src="https://img.shields.io/badge/Docker-161922?style=flat-square&logo=docker&logoColor=3ebfc6" alt="Docker">
  <img src="https://img.shields.io/badge/Linux-161922?style=flat-square&logo=linux&logoColor=3ebfc6" alt="Linux">
</p>

---

<p align="center">
  <sub>
    <a href="https://archerkattri.github.io">portfolio</a> ·
    <a href="https://archerkattri.github.io/splatreg/">splatreg docs</a> ·
    <a href="https://glama.ai/mcp/servers/Archerkattri/mathlas">mathlas on Glama</a> ·
    <a href="https://www.linkedin.com/in/krishi-attri15/">linkedin</a>
  </sub>
</p>
<p align="center"><sub><i>I build the system, then I make it prove it works.</i></sub></p>
