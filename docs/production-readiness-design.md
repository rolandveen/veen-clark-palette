# Veen–Clark palette: production-readiness design

## Status update — 16 October 2026

Candidate 2 has been approved as Veen–Clark palette 0.1.0. Its only colour change
from candidate 1 is yellow `#F0E442` to `#F5E600`. The canonical source is now
`palettes/veen-clark.yaml`; both candidate sources and their reports remain
historical evidence. See [the release record](releases/0.1.0.md).

The sections below preserve the original candidate-1 design and handover context;
their candidate status, six unchanged colours, numerical summaries and approval
gates describe that earlier snapshot. Full regeneration and dependency locking
remain open engineering tasks. Approval does not establish human validation.

## Purpose

This document preserves the design intent, scientific context, current
implementation, known limitations, and remaining work for the Veen–Clark
palette repository. It is written so that a future maintainer—human or
automated—can resume the project without having to reconstruct decisions from
chat history.

The immediate objective is to turn the current candidate into a reproducible,
well-documented and citable scientific colour palette. The repository should
eventually support one-command regeneration from the authoritative palette
definition through all exports, analyses, examples and the final PDF report.

This is a design and handover document, not evidence that the candidate has
already been approved for release.

## People, credit and terminology

The palette is by Roland J. Veen and Charlie Clark. The current copyright line
is:

> Copyright © 2026 Roland J. Veen and Charlie Clark.

The working name is **Veen–Clark palette**. It is an experimental,
Okabe–Ito-derived categorical palette developed for scientific figures and
reproducibly evaluated with PaletteBench.

Use “colour” in narrative documentation unless a technical interface or title
requires another spelling. Do not imply that Bang Wong designed the underlying
palette. The palette originates with Masataka Okabe and Kei Ito. Wong brought
it to a broad scientific audience in a 2011 *Nature Methods* column. A later
author correction added the missing link to the Okabe–Ito presentation. The
repository retains this provenance in `REFERENCES.bib`.

## Scientific motivation

The palette begins with the commonly reproduced eight-colour Okabe–Ito
palette. Six colours remain unchanged. The two blue colours are deliberately
moved farther apart so that they can represent two related subgroups in plots,
especially scatter plots and grouped bar charts.

The first candidate values are:

| Role | Name | Hex | 8-bit RGB | Normalized RGB |
|---|---|---|---|---|
| Lighter subgroup | Sky blue | `#7CC7F2` | `(124, 199, 242)` | `(0.486275, 0.780392, 0.949020)` |
| Darker subgroup | Blue | `#005A8D` | `(0, 90, 141)` | `(0.000000, 0.352941, 0.552941)` |

These two colours belong to the declared `blue_family`. The word “family”
expresses semantic relatedness; it does not claim that all observers or output
media will perceive the colours equally well.

The remaining colours and their order match the commonly reproduced
Okabe–Ito palette:

1. Orange `#E69F00`
2. Sky blue `#7CC7F2`
3. Bluish green `#009E73`
4. Yellow `#F0E442`
5. Blue `#005A8D`
6. Vermillion `#D55E00`
7. Reddish purple `#CC79A7`
8. Black `#000000`

The two blue values are still candidates. Roland planned to confer with Charlie
before treating them as final. Do not remove candidate language, mint a release,
or claim that these values are optimal without explicit approval.

## Evidence and claim boundaries

PaletteBench v0.1.0 is the evaluation workbench. It reports colour-difference
metrics separately for each condition. The committed analysis includes normal
sRGB, simulated protan, deutan
and tritan conditions, WCAG-luminance grayscale, pairwise CIEDE2000 distances,
severity progressions, gamut-clipping provenance and group-level summaries.

For the intended sky-blue/blue pair, the current audit reports:

| Condition | Okabe–Ito | Candidate | Change |
|---|---:|---:|---:|
| Normal | 22.31 | 37.92 | +15.61 |
| Protan 100% | 20.75 | 36.03 | +15.28 |
| Deutan 100% | 22.45 | 38.57 | +16.12 |
| Tritan 100% | 19.95 | 35.08 | +15.13 |
| Grayscale | 21.62 | 37.43 | +15.81 |

The blue pair has greater modelled separation in each of these conditions.
For the whole palette, the normal 10th percentile and protan-100% minimum improve, while some individual pairs
lose separation. The most notable reported regressions are blue/vermillion
under tritan 100% and blue/black under several conditions.

Every publication and release should preserve these boundaries:

- Simulations are model outputs, not clinical measurements.
- CIEDE2000 values are evidence, not an accessibility certification.
- A palette cannot be declared universally colour-blind safe from these tests.
- Results depend on mark size, surrounding colours, display, print process and
  viewing conditions.
- Human evaluation, including participants with colour-vision deficiencies,
  would strengthen a final validation but is not replaced by PaletteBench.
- Do not create an opaque aggregate “accessibility score.” Report conditions
  and important pairs separately.

## Plot examples

The scatter-and-bar example originally used a fill pattern for one blue. That
added a distinguishing cue beyond colour. The corrected example uses
identical circular scatter markers and solid, unhatched bars. The data are
synthetic. Group positions and values also differ, so the
example illustrates palette use rather than testing colour discriminability.

This does not mean redundant encodings are bad practice. In actual figures,
marker shape, line style, direct labels or hatching can improve accessibility.
A test of colour discriminability would need to control these other cues.

The source is `examples/blue_subgroups.py`; committed PNG and SVG outputs live
beside it. The script imports the generated Python palette rather than repeating
hex values.

## Source-of-truth architecture

`palettes/veen-clark-candidate.yaml` is the sole authority for palette identity,
version, status, colour order, values and groups.

Derived palette files are:

- `palette.json`
- `exports/veen_clark.py`
- `exports/veen_clark.R`
- `exports/veen_clark.m`
- `exports/veen_clark.jl`
- `exports/veen-clark.js`
- `exports/veen-clark.css`

`tools/generate_exports.py` must generate all of them from YAML. Never edit a
derived export to change the palette. Modify the YAML and regenerate.

The exports currently cover Python/Matplotlib/seaborn, R/ggplot2, MATLAB,
Julia/Makie/Plots, JavaScript/D3 and CSS. If another ecosystem is added, its
export must be deterministic, generated from YAML and checked in tests.

## Current report architecture

The final report is `output/pdf/veen-clark-palette-report.pdf`. It is currently
a 20-page A4 document and contains:

- title, scope and limitations;
- results;
- the corrected scatter-and-bar example;
- comparison with the Okabe–Ito baseline;
- methods and assumptions;
- normal, protan, deutan, tritan and grayscale strips;
- severity progression diagrams;
- condition-level summary data;
- normal, protan, deutan and tritan heatmaps;
- all four diagonal split pair matrices;
- grouped blue-family analysis;
- weakest-pair diagnostics; and
- interpretation and limitations.

`tools/build_pdf_report.py` assembles this PDF with ReportLab. It uses an
invariant canvas so rebuilding identical inputs produces byte-identical output.
The document was rendered page-by-page and visually inspected; the corrected
example, matrices, tables and captions were legible and unclipped at that time.

### Important limitation

Running only `python3 tools/build_pdf_report.py` is sufficient to reassemble
the current PDF **only when all committed intermediate analysis figures, data
and example images already exist**. It is not an end-to-end regeneration from
the YAML.

The builder currently consumes:

- `reports/palettebench-v0.1.0/` for the baseline comparison;
- `reports/veen-clark-palettebench-v0.1.0/` for the full candidate audit;
- `examples/blue-subgroups.png`; and
- several narrative values that are presently hard-coded in the builder.

Thus the repository can rebuild the checked-in PDF from checked-in
intermediates, but a colour change would not automatically propagate through
every analysis and every sentence. This is the main production-readiness gap.

## Required production pipeline

Add one cross-platform orchestration entry point, preferably
`tools/rebuild_all.py`, with a thin `make rebuild` convenience target if desired.
The Python entry point should remain the authoritative implementation so that
Windows users and CI do not require Make.

The pipeline should perform these stages in order:

1. Validate `palettes/veen-clark-candidate.yaml`.
2. Generate JSON and all language exports.
3. Render the scatter-and-bar example in PNG and SVG.
4. Run the PaletteBench Okabe–Ito comparison into a clean staging directory.
5. Run the complete single-palette PaletteBench audit into a clean staging
   directory.
6. Validate that PaletteBench archived the exact authoritative YAML bytes.
7. Build the PDF using generated data and figures.
8. Run consistency and structural tests.
9. Atomically replace committed derived artifacts only after every stage
   succeeds.

Do not write directly into committed report directories during a partial run.
PaletteBench deliberately refuses non-empty output directories. Use temporary
staging directories, validate them, and then replace the explicit target
directories. Avoid broad deletion commands.

Recommended interfaces:

```bash
python3 tools/rebuild_all.py
python3 tools/rebuild_all.py --check
python3 tools/rebuild_all.py --output-root /path/to/staging
```

`--check` should rebuild in a temporary directory and compare every generated
artifact against the checkout without modifying it. CI should use this mode.

## Remove duplicated report facts

The PDF builder currently contains hard-coded palette accent colours, numerical
results and interpretive sentences. Before production release:

- Read all palette colours from the authoritative YAML or generated JSON.
- Read every displayed metric from PaletteBench CSV/JSON output.
- Calculate changes rather than copying them into source text.
- Generate pair names from identifiers rather than embedding them manually.
- Keep prose templates in code only where they express interpretation, not data.
- Add assertions for expected conditions and explicitly fail on missing fields.
- Include the source palette version and PaletteBench version in the output
  filename or report metadata where appropriate.

Generated prose must still be reviewed by a human. Automation prevents stale
numbers; it does not make scientific interpretation automatic.

## Dependency and environment design

The current development requirements are in `requirements-dev.txt`:

- PyYAML
- Matplotlib
- NumPy
- Pillow
- ReportLab

PaletteBench is not currently declared there, because the analysis was produced
from the separate `rolandveen/palettebench` repository/release. Production
reproducibility needs an explicit decision:

1. Depend on the published `palettebench==0.1.0` package, preferably with a
   locked environment; or
2. Provide a documented environment file that pins its exact install source and
   version.

Do not vendor PaletteBench’s implementation into this repository. Record the
PaletteBench version and dependency provenance in generated metadata. Consider
adding `pyproject.toml` with a reproducibility extra and a lock file appropriate
to the chosen package workflow.

A clean-checkout command should eventually be no more complicated than:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 tools/rebuild_all.py --check
```

Document the Windows activation equivalent without making shell activation a
requirement for CI.

## Tests and continuous integration

The current unit tests check:

- agreement between hex and integer RGB;
- unique colour names and values;
- JSON agreement with authoritative YAML;
- Python export agreement with YAML;
- presence of every colour in text exports;
- exact YAML copies in both committed PaletteBench report archives; and
- synchronization of README values and `CITATION.cff` version.

CI installs dependencies, regenerates exports, rejects a dirty diff, runs unit
tests, smoke-renders the example and smoke-builds the PDF.

Extend CI so it tests the actual production promise:

- Run the complete rebuild in `--check` mode.
- Verify that the PDF has the expected page count and required section titles.
- Build the PDF twice and confirm byte identity.
- Check PDF metadata, encryption state and extractable text.
- Check that both example formats are freshly generated.
- Check all report tables and figures against staged PaletteBench output.
- Run on all supported Python versions and at least Linux; add macOS only if it
  catches relevant font/rendering differences.
- Pin action versions and use least-privilege GitHub permissions.
- Add formatting or linting only with an explicit, documented configuration.

CI should prove that committed artifacts are current. It should not silently
rewrite them.

## Documentation still needed

The README correctly identifies YAML as authoritative and documents export
generation, tests, the baseline comparison and the PDF builder. It does not yet
document a full end-to-end regeneration because that workflow does not exist.

Once implemented, update the README with:

- the one-command rebuild and check commands;
- the exact full-audit PaletteBench command;
- environment creation from a clean checkout;
- which files are sources and which are generated;
- the policy for committing generated reports and PDFs;
- how to change a colour without leaving stale results;
- how a candidate becomes a release; and
- troubleshooting for fonts, headless Matplotlib and unsupported Python.

Add a short `CONTRIBUTING.md` that directs palette changes through YAML and
requires regeneration plus scientific review. A generated-file header should
say which command owns each export.

## Publication strategy and unresolved checks

The initial publication ambition was a short contribution akin in visibility
and practical usefulness to Wong’s *Nature Methods* column. That analogy is
about reaching scientific figure makers, not claiming the same authorship,
format or editorial route.

Possible routes discussed were *Nature Methods*, another methods or
visualization venue, and *Color Research & Application* (Wiley). A preprint on
arXiv was also considered. The fact that the GitHub repository is already
public is normally an advantage for transparency and priority, but journal
preprint and prior-publication policies must be checked immediately before
submission because policies can change.

The following matters remain unresolved and must be verified from current
first-party sources rather than remembered from conversation:

- Whether the intended article type is accepted by *Nature Methods* and whether
  the contribution has enough methodological novelty for that venue.
- Which alternative journal best matches a palette plus transparent evaluation
  workbench.
- Current submission, page, colour, open-access or other publication fees for
  *Color Research & Application*.
- Whether the University of Groningen has a current Wiley read-and-publish or
  open-access agreement covering the corresponding author, selected journal,
  article type and submission/acceptance date.
- The selected journal’s current arXiv/preprint policy and the correct timing of
  a preprint.
- Whether the palette paper and the PaletteBench software paper should be one
  article, companion outputs, or separate manuscripts.

When checking the University of Groningen–Wiley agreement, record the source
URL, access date, eligibility rules, journal coverage, article types, author
requirements, available caps and the person or library service that confirmed
the interpretation. Do not infer coverage merely because the publisher is
Wiley.

An arXiv deposit should include a stable manuscript source bundle, matching
figures, complete references, version identifier, repository URL and software
archive DOI. Check the target category and obtain both authors’ approval before
submission. A preprint is not a substitute for a versioned software/palette
release.

## Citation, licensing and archiving

The repository currently uses the BSD 3-Clause License and attributes Roland
J. Veen and Charlie Clark. `CITATION.cff` provides repository citation metadata,
and `REFERENCES.bib` records relevant provenance.

Before release:

- Confirm authorship order, affiliations, ORCIDs and corresponding author with
  Charlie.
- Confirm that both authors approve the final palette values, name, licence and
  public claims.
- Confirm that reuse of the unchanged Okabe–Ito values and attribution wording
  is appropriately documented.
- Assign a semantic version without the `candidate` suffix only after approval.
- Tag the exact commit used for the manuscript.
- Archive the release, ideally with Zenodo, and add concept/version DOI metadata.
- Cite the exact PaletteBench version or DOI used to generate the report.
- Keep the GitHub release, archive, PDF, YAML and manuscript version aligned.

Public availability before journal submission does not by itself damage the
work. It provides provenance and reproducibility. The risks are inconsistent
versions, claims that predate evidence, unclear authorship approval, or a
journal whose current policies conflict with the chosen preprint/publication
route.

## Release gates

The palette is production-ready only when all of the following are true:

### Scientific

- Charlie has approved the values and interpretation.
- Pair-specific benefits and whole-palette regressions are both reported.
- Human validation is completed or its absence is explicit.
- Claims have been reviewed against the final generated evidence.

### Reproducibility

- One command rebuilds every derived artifact from YAML.
- A clean checkout passes that command using documented dependencies.
- No report values are duplicated manually in source code.
- CI confirms that checked-in outputs are current and deterministic.
- The final PDF passes structural and visual QA.

### Repository quality

- README, contribution guide and generated-file policy are complete.
- Temporary renders, caches and local environments are ignored.
- No credentials, local absolute paths or machine-specific files are tracked.
- The working tree is reviewed before committing because the present work began
  from an almost empty repository and remains uncommitted pending discussion.

### Publication and governance

- Authorship, affiliations, ORCIDs, licence and corresponding author are agreed.
- Journal, article type, fees and institutional agreement have been verified.
- Preprint timing is compatible with current journal policy.
- Release tag, citations, DOI/archive and manuscript all identify the same
  palette and analysis versions.

## Recommended next work session

1. Review this document and the current PDF with Charlie.
2. Record approval or requested colour changes.
3. If colours change, edit only the YAML and treat all current outputs as stale.
4. Implement `tools/rebuild_all.py` with staged, atomic output replacement.
5. Refactor `tools/build_pdf_report.py` to read all values from generated data.
6. Add end-to-end and deterministic-report checks to CI.
7. Perform a clean-checkout rehearsal on a second machine or fresh environment.
8. Only then prepare a coherent commit, candidate release and manuscript plan.

## Current handover summary

At the time this document was written, the candidate palette, generated
language exports, PaletteBench comparison, complete candidate audit, honest
plot example, tests, CI configuration and 20-page PDF all existed in the
working tree. Seven unit tests passed. The PDF rebuilt byte-for-byte and its 20
pages and expected section headings were programmatically verified. It was also
visually inspected from rendered page images.

Those checks establish that the current snapshot is internally consistent.
They do **not** close the end-to-end regeneration gap described above, and they
do not constitute Charlie’s approval or a production release.

### Report wording

The comparison report introduction has been edited locally for clarity.
PaletteBench v0.1.0 regeneration restores its original boilerplate; preserve
this wording when adding the full rebuild pipeline. Numerical outputs are unchanged.
