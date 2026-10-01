# Veen–Clark palette

An experimental, Okabe–Ito-derived categorical colour palette for scientific
figures by Roland J. Veen and Charlie Clark. The palette preserves the six
non-blue Okabe–Ito colours and separates two related subgroups by making sky
blue lighter and blue darker.

> **Candidate v0.1:** the replacement blues are first-attempt values. They are
> being evaluated reproducibly with PaletteBench and should not yet be
> described as perceptually optimal or universally accessible.

## Colours

| Name | Hex | RGB (8-bit) | RGB triplet (0–1) |
|---|---:|---:|---:|
| Orange | `#E69F00` | `(230, 159, 0)` | `(0.901961, 0.623529, 0.000000)` |
| Sky blue | `#7CC7F2` | `(124, 199, 242)` | `(0.486275, 0.780392, 0.949020)` |
| Bluish green | `#009E73` | `(0, 158, 115)` | `(0.000000, 0.619608, 0.450980)` |
| Yellow | `#F0E442` | `(240, 228, 66)` | `(0.941176, 0.894118, 0.258824)` |
| Blue | `#005A8D` | `(0, 90, 141)` | `(0.000000, 0.352941, 0.552941)` |
| Vermillion | `#D55E00` | `(213, 94, 0)` | `(0.835294, 0.368627, 0.000000)` |
| Reddish purple | `#CC79A7` | `(204, 121, 167)` | `(0.800000, 0.474510, 0.654902)` |
| Black | `#000000` | `(0, 0, 0)` | `(0.000000, 0.000000, 0.000000)` |

The order follows the commonly reproduced Okabe–Ito palette. The two blues
form a declared `blue_family` for related subgroups in scatter and bar charts.
When category identification is critical, also use marker shape, line style,
direct labels, hatching, or another redundant cue.

## Use

Ready-to-copy definitions are generated in [`exports/`](exports/) for:

- Python (Matplotlib and seaborn)
- R (ggplot2)
- MATLAB
- Julia (Makie and Plots)
- JavaScript (including D3)
- CSS custom properties

[`palettes/veen-clark-candidate.yaml`](palettes/veen-clark-candidate.yaml) is
the sole authoritative definition and the direct PaletteBench input.
[`palette.json`](palette.json) and every file in `exports/` are generated from
that YAML. Install the small validation environment, regenerate derived files,
and run consistency tests with:

```bash
python3 -m pip install -r requirements-dev.txt
python3 tools/generate_exports.py
python3 -m unittest discover -s tests
```

GitHub Actions repeats these checks, rejects stale generated files, and
smoke-tests the example renderer on every push and pull request.

## PaletteBench evaluation

The candidate is compared directly with the bundled Okabe–Ito baseline using
[PaletteBench v0.1.0](https://github.com/rolandveen/palettebench/tree/v0.1.0).
PaletteBench reports condition-specific CIEDE2000 separation under normal
vision, simulated protan/deutan/tritan colour-vision deficiencies, and
grayscale. It does not produce an opaque accessibility score.

The committed evaluation artifacts are generated with:

```bash
palettebench compare --okabe-ito-baseline \
  palettes/veen-clark-candidate.yaml \
  --output reports/palettebench-v0.1.0
```

The report, exact input copies, hashes, configuration, dependency versions,
figures, and full-precision data live together under `reports/`. Simulation and
colour-difference metrics support an assessment; they do not replace testing
with people who have colour-vision deficiencies or testing the actual figure
at its intended mark size and reproduction medium.

A single paginated report containing the baseline comparison, CVD overview,
grayscale, severity progressions, heatmaps, all four diagonal split pair
matrices, grouped-blue analysis, and limitations is available as
[`output/pdf/veen-clark-palette-report.pdf`](output/pdf/veen-clark-palette-report.pdf).
Rebuild it with `python3 tools/build_pdf_report.py`.

### First computational result

For the intended blue subgroup pair, PaletteBench reports an increase in
modelled separation from ΔE00 22.31 to 37.92 under normal vision. The increase
persists under the standard simulations: 20.75 to 36.03 (protan 100%), 22.45
to 38.57 (deutan 100%), 19.95 to 35.08 (tritan 100%), and 21.62 to 37.43 in
grayscale. These are encouraging pair-specific results, not proof that the
whole palette or every plotted use is superior.

The full-palette result is deliberately mixed and reported as such. Relative
to Okabe–Ito, the candidate raises the 10th-percentile separation under normal
vision by 2.73 and the minimum under protan 100% by 2.92, while some individual
pairs lose separation—most notably blue/vermillion under tritan 100% (−12.20)
and blue/black under the reported conditions. See the
[`PaletteBench comparison report`](reports/palettebench-v0.1.0/report.md) rather
than treating the blue-pair improvement as a universal ranking.

## Plot examples

![The candidate blues used for related subgroups in scatter and bar charts](examples/blue-subgroups.svg)

The two subgroups deliberately use identical marker shapes and solid bar fills,
so the example does not inflate their separation with a second visual channel.
The reproducible source is [`examples/blue_subgroups.py`](examples/blue_subgroups.py).

## Provenance and citation

This palette is derived from the colour-universal-design palette developed by
Masataka Okabe and Kei Ito. Bang Wong brought the palette to a broad scientific
audience in a 2011 *Nature Methods* column; a 2023 author correction added the
missing link to the Okabe–Ito presentation. See [`REFERENCES.bib`](REFERENCES.bib).

If you use this candidate palette, cite this repository using
[`CITATION.cff`](CITATION.cff), cite PaletteBench for the exact release used,
and retain the Okabe–Ito and Wong provenance.

## License

BSD 3-Clause. Copyright © 2026 Roland J. Veen and Charlie Clark.
