import csv
import hashlib
import importlib.util
import re
import subprocess
import sys
import tempfile
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PaletteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = yaml.safe_load(
            (ROOT / "palettes" / "veen-clark.yaml").read_text(encoding="utf-8")
        )
        cls.generated = json.loads((ROOT / "palette.json").read_text(encoding="utf-8"))

    def test_hex_matches_rgb(self):
        for color in self.generated["colors"]:
            expected = "#" + "".join(f"{channel:02X}" for channel in color["rgb"])
            self.assertEqual(color["hex"], expected)

    def test_names_and_values_are_unique(self):
        colors = self.generated["colors"]
        self.assertEqual(len({color["name"] for color in colors}), len(colors))
        self.assertEqual(len({color["hex"] for color in colors}), len(colors))

    def test_json_matches_authoritative_yaml(self):
        """Prevent the language-neutral export from becoming a second authority."""
        self.assertEqual(self.generated["name"], self.source["name"])
        self.assertEqual(self.generated["slug"], self.source["slug"])
        self.assertEqual(self.generated["version"], self.source["version"])
        self.assertEqual(self.generated["status"], self.source["status"])
        self.assertEqual(len(self.generated["colors"]), len(self.source["colors"]))
        for generated, source in zip(self.generated["colors"], self.source["colors"]):
            self.assertEqual(generated["name"], source["id"])
            self.assertEqual(generated["display_name"], source["name"])
            self.assertEqual(generated["hex"], source["hex"])
            self.assertEqual(generated.get("group"), source.get("group"))

    def test_python_export_matches_source(self):
        export = ROOT / "exports" / "veen_clark.py"
        spec = importlib.util.spec_from_file_location("veen_clark", export)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.HEX, [color["hex"] for color in self.source["colors"]])
        self.assertEqual(module.NAMES, [color["id"] for color in self.source["colors"]])
        self.assertEqual(len(module.RGB), len(self.generated["colors"]))
        for actual, color in zip(module.RGB, self.generated["colors"]):
            self.assertEqual(len(actual), len(color["rgb"]))
            for channel, integer in zip(actual, color["rgb"]):
                self.assertAlmostEqual(channel, integer / 255, places=6)

    def test_text_exports_contain_every_colour(self):
        """Catch omissions without requiring R, MATLAB, Julia, or Node in CI."""
        paths = [
            ROOT / "exports" / "veen_clark.R",
            ROOT / "exports" / "veen_clark.m",
            ROOT / "exports" / "veen_clark.jl",
            ROOT / "exports" / "veen-clark.js",
            ROOT / "exports" / "veen-clark.css",
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8").upper()
            for color in self.source["colors"]:
                # MATLAB stores normalized triplets rather than hexadecimal,
                # so it is validated numerically by its generated row count.
                if path.suffix == ".m":
                    matrix = text.split("COLORS = [", 1)[1].split("];", 1)[0]
                    self.assertEqual(len(matrix.strip().splitlines()), len(self.source["colors"]))
                    break
                self.assertIn(color["hex"], text, path.name)

    def test_committed_report_uses_current_authoritative_input(self):
        """Require exact current inputs and honest archive provenance."""
        source = ROOT / "palettes" / "veen-clark.yaml"
        for folder in ("audit", "comparison"):
            report = ROOT / "reports" / "v0.1.0" / folder
            metadata = json.loads((report / "metadata.json").read_text())
            matched = []
            for item in metadata["inputs"]:
                archived = report / item["copied_file"]
                self.assertEqual(hashlib.sha256(archived.read_bytes()).hexdigest(), item["sha256"])
                if archived.name.endswith("-veen-clark.yaml"):
                    self.assertEqual(source.read_bytes(), archived.read_bytes())
                    matched.append(item)
            self.assertEqual(len(matched), 1)
            self.assertEqual(metadata["palettebench_version"], "0.1.0")
            self.assertEqual(metadata["configuration"]["severities"], [20, 40, 60, 80, 100])
            if folder == "audit":
                self.assertEqual(metadata["input_sha256"], matched[0]["sha256"])

    def test_report_metrics_agree(self):
        """Cross-check full audit, comparison, pair coverage and summary minima."""
        def rows(path):
            with path.open(encoding="utf-8", newline="") as stream:
                return list(csv.DictReader(stream))
        reports = ROOT / "reports" / "v0.1.0"
        audit = rows(reports / "audit/data/pairwise.csv")
        indexed = {(r["condition"], r["colour1"], r["colour2"]): r for r in audit}
        self.assertEqual(len(indexed), 13 * 28)
        changes = rows(reports / "comparison/data/pairwise_changes.csv")
        self.assertEqual(len(changes), len(indexed))
        self.assertEqual({(r["condition"], r["colour1"], r["colour2"]) for r in changes}, set(indexed))
        for row in changes:
            expected = float(indexed[row["condition"], row["colour1"], row["colour2"]]["delta_e_00"])
            self.assertAlmostEqual(float(row["palette_delta_e_00"]), expected, places=10)
            self.assertAlmostEqual(float(row["change_from_baseline"]),
                                   expected - float(row["baseline_delta_e_00"]), places=10)
        summary = rows(reports / "audit/data/summary.csv")
        self.assertEqual({r["condition"] for r in summary}, {r["condition"] for r in audit})
        for row in summary:
            values = [float(r["delta_e_00"]) for r in audit if r["condition"] == row["condition"]]
            self.assertEqual(len(values), 28)
            self.assertAlmostEqual(float(row["minimum"]), min(values), places=10)
            self.assertAlmostEqual(float(row["mean"]), sum(values) / len(values), places=10)
        for row in rows(reports / "comparison/data/comparison.csv"):
            if row["palette_index"] == "1":
                matching = next(r for r in summary if r["condition"] == row["condition"])
                for field in ("minimum", "mean", "median", "q10"):
                    self.assertAlmostEqual(float(row[field]), float(matching[field]), places=10)

    def test_readme_metrics_match_reports(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        path = ROOT / "reports/v0.1.0/comparison/data/pairwise_changes.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            pairs = list(csv.DictReader(stream))
        for row in pairs:
            if row["condition"] in ("normal", "protan100", "deutan100", "tritan100", "grayscale"):
                if {row["colour1"], row["colour2"]} == {"sky_blue", "blue"}:
                    for key in ("baseline_delta_e_00", "palette_delta_e_00"):
                        self.assertIn(f"{float(row[key]):.2f}", readme)
                if row["condition"] == "tritan100" and {row["colour1"], row["colour2"]} == {"blue", "vermillion"}:
                    self.assertIn(f"{float(row['change_from_baseline']):.2f}".replace("-", "−"), readme)
        with (ROOT / "reports/v0.1.0/comparison/data/comparison.csv").open(newline="", encoding="utf-8") as stream:
            summaries = list(csv.DictReader(stream))
        for condition, field in (("normal", "q10_change_from_baseline"),
                                 ("protan100", "minimum_change_from_baseline")):
            row = next(r for r in summaries if r["palette_index"] == "1" and r["condition"] == condition)
            self.assertIn(f"{float(row[field]):.2f}", readme)

    def test_all_exports_are_fresh(self):
        spec = importlib.util.spec_from_file_location("generator", ROOT / "tools/generate_exports.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            module.ROOT = Path(temporary)
            module.EXPORTS = module.ROOT / "exports"
            module.main()
            for path in [module.ROOT / "palette.json", module.ROOT / "CITATION.ris",
                         *module.EXPORTS.iterdir()]:
                self.assertEqual(path.read_bytes(), (ROOT / path.relative_to(module.ROOT)).read_bytes())

    def test_readme_links_resolve(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", readme):
            if "://" not in target and not target.startswith("#"):
                self.assertTrue((ROOT / target.split("#")[0]).exists(), target)

    def test_report_structure_and_rebuild(self):
        from pypdf import PdfReader
        committed = ROOT / "output/pdf/veen-clark-palette-0.1.0-report.pdf"
        reader = PdfReader(committed)
        self.assertFalse(reader.is_encrypted)
        self.assertEqual(len(reader.pages), 22)
        text = "\n".join(page.extract_text() for page in reader.pages)
        for title in ("Version 0.1.0 evaluation", "Yellow in context", "Grouped blue-family analysis", "References"):
            self.assertIn(title, text)
        for colour in self.source["colors"]:
            self.assertIn(colour["hex"], text)
        normalized = " ".join(text.split())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertLess(text.index("Responsible use of AI"), text.rindex("References"))
        links = set()
        for page in reader.pages:
            for annotation in page.get("/Annots", []):
                action = annotation.get_object().get("/A", {})
                if action.get("/S") == "/URI":
                    links.add(str(action["/URI"]))
        for section in ("Responsible use of AI", "References"):
            content = readme.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0].strip()
            for url in re.findall(r"\]\((https://[^)]+)\)", content):
                self.assertIn(url, links)
            for paragraph in content.split("\n\n"):
                plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", paragraph)
                plain = plain.replace("**", "").replace("*", "")
                self.assertIn(" ".join(plain.split()), normalized)
        digest = hashlib.sha256((ROOT / "palettes/veen-clark.yaml").read_bytes()).hexdigest()
        self.assertIn(digest, text)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.pdf"
            command = [sys.executable, str(ROOT / "tools/build_pdf_report.py"), "--output", str(output)]
            subprocess.run(command, check=True, capture_output=True)
            first = output.read_bytes()
            regenerated = "\n".join(page.extract_text() for page in PdfReader(output).pages)
            self.assertEqual(regenerated, text)
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(output.read_bytes(), first)

    def test_documented_values_and_citation_version_are_current(self):
        """Keep the human-facing table and citation metadata synchronized."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        self.assertEqual(citation["version"], self.source["version"])
        for color in self.generated["colors"]:
            integer = f"({', '.join(str(value) for value in color['rgb'])})"
            normalized = "(" + ", ".join(
                f"{value / 255:.6f}" for value in color["rgb"]
            ) + ")"
            self.assertIn(color["hex"], readme)
            self.assertIn(integer, readme)
            self.assertIn(normalized, readme)


if __name__ == "__main__":
    unittest.main()
