# Reproducibility

## Sources and generated files

`palettes/veen-clark.yaml` defines palette identity, version, colour order,
values and groups. `tools/`, the Python example source, README, citation and
reference files are maintained sources.

Generated outputs are `palette.json`, `CITATION.ris`, `REFERENCES.ris`, `exports/`,
the example PNG/SVG, `reports/v0.1.0/`, and `output/pdf/veen-clark-palette-0.1.0-report.pdf`.
Reports contain exact YAML input copies, hashes, configuration, dependency
versions, full-precision data, tables and figures. Generated data are not edited
by hand. `CITATION.ris` contains only the palette citation from `CITATION.cff`.
`REFERENCES.ris` contains all supporting references from `REFERENCES.bib`.
Users are asked to cite Veen–Clark and acknowledge its Okabe–Ito origins;
citing the original work is encouraged where relevant, rather than required.
The PDF reads metrics from the generated CSV files and imports the responsible
AI use statement and linked references directly from their README sections.

## Environment

Use Python 3.12 and Git. Create a virtual environment and install
`requirements-dev.txt`; it pins the complete validation and rendering dependency
set. PaletteBench is pinned to release 0.1.0 commit
`759f06f25cafa1ae80355b7a064122c27f879f8a`.
The first install needs network access. No neighbouring checkout is required.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python tools/rebuild_all.py --check
```

Windows uses `.venv\Scripts\python.exe`. Environment activation is optional.
The scripts select the noninteractive Matplotlib backend. A writable temporary
Matplotlib configuration directory is supplied by the rebuild script.

## Full rebuild

```bash
.venv/bin/python tools/rebuild_all.py
```

The script builds in `tmp/`, runs export generation, example rendering,
PaletteBench audit and comparison, PDF assembly and tests, then replaces only
the explicit generated targets. Backups are restored if replacement raises an
ordinary error. This is not a transaction against power loss or process termination;
Git retains the preceding committed artifacts.

Both analyses use severity values 20, 40, 60, 80 and 100, SVG/PDF/PNG output,
and 300 dpi. Normal, protan/deutan 100%, tritan 100% and grayscale are included;
partial tritan simulation is omitted. Equivalent manual analysis commands are:

```bash
.venv/bin/python -m palettebench audit palettes/veen-clark.yaml --output tmp/audit
.venv/bin/python -m palettebench compare --okabe-ito-baseline palettes/veen-clark.yaml --output tmp/comparison
```

Choose new or empty output directories; PaletteBench refuses existing nonempty
outputs. Run `tools/build_pdf_report.py` only to reassemble the PDF from the
existing reports and example image. It does not rerun the analyses.

## Validation boundaries

`--check` runs consistency tests without replacing tracked artifacts. It checks
exact source hashes and generated exports, every matched pair against the audit,
summary statistics, citation/README values, local README links, PDF sections and
colours, and two byte-identical PDF assemblies in the current environment.
The rebuilt PDF's extracted text must also match the committed PDF.

CI additionally performs the full staged rebuild and compares its numerical CSV
and JSON data against the committed results with floating-point tolerance.
Generated timestamps and platform metadata record each actual run. Rendering
bytes can differ across operating systems, fonts and plotting libraries; the
workflow does not require identical figure pixels across platforms. Review the
PDF visually after a deliberate rebuild before committing generated artifacts.

## Scientific limits

PaletteBench models ideal sRGB, CVD simulations with gamut clipping, and
gray-scale luminance. CIEDE2000 distances are condition-specific computational
evidence. They do not establish universal accessibility, projector performance,
or participant-level discriminability. Use redundant cues when category identity
is critical, and inspect figures at their intended size and viewing conditions.
