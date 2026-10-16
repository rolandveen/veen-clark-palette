# Contributing

Edit palette values only in `palettes/veen-clark.yaml`. Discuss changes to colour
values, grouping, interpretation and authorship with the maintainers before
including them in a versioned palette.

Use Python 3.12 and install `requirements-dev.txt` in a virtual environment.
Run `python tools/rebuild_all.py`, inspect the generated PDF and examples, then
run `python tools/rebuild_all.py --check`. Commit the source and its generated
outputs together. Do not manually change generated exports, report data or figures.
See [reproducibility](docs/reproducibility.md) for the file contract and commands.

Keep benefits and regressions condition-specific. Do not equate simulation with
human validation. Retain the Okabe–Ito provenance and the named human authors.

Before archival publication, ensure the Git tag, YAML, JSON, citation metadata,
report and release notes all identify the same version. Add the actual archival
DOI after allocation; do not insert placeholder identifiers. Zenodo setup and
release publication are separate maintainer actions.
