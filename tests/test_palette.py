import importlib.util
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PaletteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = yaml.safe_load(
            (ROOT / "palettes" / "veen-clark-candidate.yaml").read_text(encoding="utf-8")
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
        """Force every palette edit to be accompanied by a fresh benchmark report."""
        source = ROOT / "palettes" / "veen-clark-candidate.yaml"
        archived_inputs = [
            ROOT
            / "reports"
            / "palettebench-v0.1.0"
            / "inputs"
            / "02-veen-clark-candidate.yaml",
            ROOT
            / "reports"
            / "veen-clark-palettebench-v0.1.0"
            / "inputs"
            / "01-veen-clark-candidate.yaml",
        ]
        for archived in archived_inputs:
            self.assertEqual(source.read_bytes(), archived.read_bytes(), archived)

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
