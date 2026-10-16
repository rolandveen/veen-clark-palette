"""Rebuild release artifacts in staging, validate, then replace explicit targets."""

from __future__ import annotations

import argparse
import importlib.metadata
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(root: Path, *arguments: str) -> None:
    environment = os.environ.copy()
    environment["MPLBACKEND"] = "Agg"
    environment.setdefault("MPLCONFIGDIR", str(root / "tmp" / "matplotlib"))
    subprocess.run([sys.executable, *arguments], cwd=root, env=environment, check=True)


def rebuild() -> None:
    if importlib.metadata.version("palettebench") != "0.1.0":
        raise RuntimeError("Install the pinned PaletteBench 0.1.0 dependency")
    (ROOT / "tmp").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rebuild-", dir=ROOT / "tmp") as temporary:
        stage = Path(temporary) / "release"
        stage.mkdir()
        for folder in ("palettes", "tools", "tests", "docs"):
            shutil.copytree(ROOT / folder, stage / folder, ignore=shutil.ignore_patterns("__pycache__"))
        (stage / "examples").mkdir()
        shutil.copy2(ROOT / "examples" / "blue_subgroups.py", stage / "examples")
        for name in ("README.md", "CITATION.cff", "REFERENCES.bib", "LICENSE", "CONTRIBUTING.md"):
            shutil.copy2(ROOT / name, stage / name)
        run(stage, "tools/generate_exports.py")
        run(stage, "examples/blue_subgroups.py")
        source = "palettes/veen-clark.yaml"
        for command, destination, extra in (
            ("audit", "audit", []),
            ("compare", "comparison", ["--okabe-ito-baseline"]),
        ):
            run(stage, "-m", "palettebench", command, *extra, source,
                "--output", f"reports/v0.1.0/{destination}",
                "--severity", "20,40,60,80,100", "--format", "svg,pdf,png", "--dpi", "300")
        run(stage, "tools/build_pdf_report.py")
        run(stage, "-m", "unittest", "discover", "-s", "tests", "-v")

        # Validation happens before any committed output is touched. Keep backups
        # until every replacement succeeds, and restore them on a normal failure.
        targets = ["palette.json", "CITATION.ris", "exports", "reports/v0.1.0",
                   "examples/blue-subgroups.svg", "examples/blue-subgroups.png",
                   "output/pdf/veen-clark-palette-0.1.0-report.pdf"]
        backup = Path(temporary) / "backup"
        installed: list[str] = []
        saved: list[str] = []
        try:
            for name in targets:
                destination = ROOT / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    (backup / name).parent.mkdir(parents=True, exist_ok=True)
                    destination.rename(backup / name)
                    saved.append(name)
                (stage / name).rename(destination)
                installed.append(name)
        except Exception:
            for name in reversed(installed):
                destination = ROOT / name
                if destination.is_dir():
                    shutil.rmtree(destination)
                else:
                    destination.unlink()
            for name in reversed(saved):
                (backup / name).rename(ROOT / name)
            raise
    print("Release artifacts rebuilt and validated.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Validate committed inputs, metrics, exports and PDF without regenerating reports")
    args = parser.parse_args()
    if args.check:
        run(ROOT, "-m", "unittest", "discover", "-s", "tests", "-v")
    else:
        rebuild()


if __name__ == "__main__":
    main()
