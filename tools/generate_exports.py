"""Generate palette exports and an RIS citation from the canonical YAML sources."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "palettes" / "veen-clark.yaml"
CITATION_SOURCE = ROOT / "CITATION.cff"
EXPORTS = ROOT / "exports"
HEADER = (
    "Generated from palettes/veen-clark.yaml by "
    "tools/generate_exports.py; do not edit."
)
HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def normalized(rgb: list[int]) -> list[float]:
    return [channel / 255 for channel in rgb]


def rgb_from_hex(value: str) -> list[int]:
    """Convert the validated six-digit sRGB form used by PaletteBench."""
    return [int(value[index : index + 2], 16) for index in (1, 3, 5)]


def load_source() -> dict:
    """Load the hand-edited source and enforce fields needed by every export."""
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    required = ("name", "slug", "version", "status", "colors")
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(f"Canonical palette is missing: {', '.join(missing)}")
    validate_colors(data["colors"])
    return data


def validate_colors(colors: object) -> None:
    """Fail early when an edit would create invalid or ambiguous exports."""
    if not isinstance(colors, list) or len(colors) < 2:
        raise ValueError("Canonical palette must contain at least two colours")
    ids: list[str] = []
    values: list[str] = []
    for index, color in enumerate(colors, start=1):
        if not isinstance(color, dict):
            raise ValueError(f"Colour {index} must be a mapping")
        identifier, label, value = color.get("id"), color.get("name"), color.get("hex")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"Colour {index} has an invalid id")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"Colour {identifier!r} has an invalid display name")
        if not isinstance(value, str) or not HEX_PATTERN.fullmatch(value):
            raise ValueError(f"Colour {identifier!r} must use six-digit hexadecimal sRGB")
        ids.append(identifier)
        values.append(value.upper())
    if len(ids) != len(set(ids)):
        raise ValueError("Colour ids must be unique")
    if len(values) != len(set(values)):
        raise ValueError("Colour values must be unique")


def main() -> None:
    data = load_source()
    colors = data["colors"]
    names = [color["id"] for color in colors]
    hexes = [color["hex"].upper() for color in colors]
    rgb = [rgb_from_hex(value) for value in hexes]
    triplets = [normalized(value) for value in rgb]
    EXPORTS.mkdir(exist_ok=True)

    # JSON is deliberately derived rather than hand-maintained so downstream
    # tools that cannot read YAML still receive exactly the benchmarked values.
    json_colors = []
    for color, value, integer_rgb in zip(colors, hexes, rgb):
        row = {
            "name": color["id"],
            "display_name": color["name"],
            "hex": value,
            "rgb": integer_rgb,
        }
        if "group" in color:
            row["group"] = color["group"]
        json_colors.append(row)
    json_data = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "name": data["name"],
        "slug": data["slug"],
        "version": data["version"],
        "status": data["status"],
        "colors": json_colors,
    }
    (ROOT / "palette.json").write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    python = [
        f'"""{HEADER}"""',
        "",
        f"NAMES = {names!r}",
        f"HEX = {hexes!r}",
        "RGB = [",
    ]
    python += [
        f"    ({', '.join(f'{value:.6f}' for value in row)})," for row in triplets
    ]
    python += [
        "]",
        "",
        "def as_listed_colormap():",
        "    from matplotlib.colors import ListedColormap",
        '    return ListedColormap(HEX, name="veen_clark")',
        "",
    ]
    (EXPORTS / "veen_clark.py").write_text("\n".join(python), encoding="utf-8")

    r_values = ", ".join(f'"{value}"' for value in hexes)
    r_names = ", ".join(f'"{value}"' for value in names)
    (EXPORTS / "veen_clark.R").write_text(
        f"# {HEADER}\nveen_clark <- setNames(c({r_values}), c({r_names}))\n",
        encoding="utf-8",
    )

    matlab_rows = ["    " + " ".join(f"{value:.6f}" for value in row) for row in triplets]
    matlab = (
        f"% {HEADER}\nfunction colors = veen_clark()\ncolors = [\n"
        + ";\n".join(matlab_rows)
        + "\n];\nend\n"
    )
    (EXPORTS / "veen_clark.m").write_text(matlab, encoding="utf-8")

    julia_values = ", ".join(f'colorant"{value}"' for value in hexes)
    (EXPORTS / "veen_clark.jl").write_text(
        f"# {HEADER}\nusing Colors\nconst VEEN_CLARK = [{julia_values}]\n",
        encoding="utf-8",
    )

    js_values = ", ".join(f'"{value}"' for value in hexes)
    (EXPORTS / "veen-clark.js").write_text(
        f"// {HEADER}\nexport const veenClark = Object.freeze([{js_values}]);\n",
        encoding="utf-8",
    )

    css = [f"/* {HEADER} */", ":root {"]
    css += [
        f"  --vc-{color['id'].replace('_', '-')}: {value};"
        for color, value in zip(colors, hexes)
    ]
    css += ["}", ""]
    (EXPORTS / "veen-clark.css").write_text("\n".join(css), encoding="utf-8")

    citation = yaml.safe_load(CITATION_SOURCE.read_text(encoding="utf-8"))
    if citation["version"] != data["version"]:
        raise ValueError("Citation version must match the palette version")
    date = str(citation["date-released"])
    ris = ["TY  - COMP"]
    ris += [f"AU  - {author['family-names']}, {author['given-names']}"
            for author in citation["authors"]]
    ris += [f"TI  - {citation['title']}", f"PY  - {date[:4]}",
            f"DA  - {date.replace('-', '/')}", f"ET  - {citation['version']}",
            f"UR  - {citation['repository-code']}"]
    if citation.get("doi"):
        ris.append(f"DO  - {citation['doi']}")
    ris += ["ER  -", ""]
    (ROOT / "CITATION.ris").write_text("\n".join(ris), encoding="utf-8")


if __name__ == "__main__":
    main()
