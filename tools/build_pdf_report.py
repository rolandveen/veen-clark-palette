"""Build the complete, paginated Veen-Clark palette report as a PDF."""

from __future__ import annotations

import argparse
import csv
import json
import re
from html import escape
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "reports" / "v0.1.0" / "audit"
COMPARISON = ROOT / "reports" / "v0.1.0" / "comparison"
DEFAULT_OUTPUT = ROOT / "output" / "pdf" / "veen-clark-palette-0.1.0-report.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 17 * mm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN
CONTENT_HEIGHT = PAGE_HEIGHT - 2 * MARGIN

RELEASE = json.loads((ROOT / "palette.json").read_text(encoding="utf-8"))
HEX = {colour["name"]: colour["hex"] for colour in RELEASE["colors"]}
PALETTE = [colors.HexColor(HEX[name]) for name in ("blue", "sky_blue", "orange")]


class InvariantCanvas(canvas.Canvas):
    """Remove clock-dependent PDF metadata so rebuilds are reproducible."""

    def __init__(self, *args, **kwargs):
        kwargs["invariant"] = 1
        super().__init__(*args, **kwargs)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def figure(path: Path, caption: str, max_height: float = 205 * mm) -> KeepTogether:
    """Scale a raster figure without distortion and attach a stable caption."""
    with PILImage.open(path) as source:
        width, height = source.size
    scale = min(CONTENT_WIDTH / width, max_height / height)
    image = Image(str(path), width=width * scale, height=height * scale)
    image.hAlign = "CENTER"
    caption_style = ParagraphStyle(
        "Figure caption",
        parent=STYLES["BodyText"],
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#333333"),
        spaceBefore=3 * mm,
    )
    return KeepTogether([image, Paragraph(caption, caption_style)])


def styled_table(data: list[list[str]], widths: list[float], font_size: float = 7.5) -> Table:
    """Apply one compact, legible table treatment throughout the report."""
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PALETTE[0]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("LEADING", (0, 0), (-1, -1), font_size + 2),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B9C3CA")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6F8")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def page_chrome(pdf: canvas.Canvas, document: SimpleDocTemplate) -> None:
    """Draw a quiet running header, divider, and page number."""
    pdf.saveState()
    pdf.setStrokeColor(colors.HexColor(HEX["sky_blue"]))
    pdf.setLineWidth(0.8)
    pdf.line(MARGIN, PAGE_HEIGHT - 12 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 12 * mm)
    pdf.setFont("Helvetica", 7.5)
    pdf.setFillColor(colors.HexColor("#4A5962"))
    pdf.drawString(MARGIN, PAGE_HEIGHT - 9 * mm, f"Veen-Clark {RELEASE['version']} - PaletteBench evaluation")
    pdf.drawRightString(PAGE_WIDTH - MARGIN, 9 * mm, f"Page {document.page}")
    pdf.restoreState()


def heading(text: str, level: int = 1) -> Paragraph:
    return Paragraph(text, STYLES[f"Heading{level}"])


def body(text: str) -> Paragraph:
    return Paragraph(text, STYLES["BodyText"])


def readme_section(title: str) -> list[str]:
    """Read shared disclosure/reference paragraphs from their maintained source."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    marker = f"## {title}\n"
    if readme.count(marker) != 1:
        raise ValueError(f"Expected one README section: {title}")
    section = readme.split(marker, 1)[1].split("\n## ", 1)[0].strip()
    if not section:
        raise ValueError(f"Empty README section: {title}")
    return [" ".join(paragraph.splitlines()) for paragraph in section.split("\n\n")]


def markdown_paragraph(text: str) -> Paragraph:
    """Render the small Markdown subset used by the shared README sections."""
    text = escape(text, quote=True)
    text = re.sub(r"\[([^\]]+)\]\((https://[^\s)]+)\)",
                  r'<a href="\2" color="#005A8D"><u>\1</u></a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return body(text)


def build_story() -> list:
    summary = read_csv(AUDIT / "data" / "summary.csv")
    colours_data = read_csv(AUDIT / "data" / "colours.csv")
    groups = read_csv(AUDIT / "data" / "group_summary.csv")
    metadata = json.loads((AUDIT / "metadata.json").read_text(encoding="utf-8"))

    pair_changes = read_csv(COMPARISON / "data" / "pairwise_changes.csv")
    comparison = {row["condition"]: row for row in read_csv(COMPARISON / "data" / "comparison.csv")
                  if row["palette_index"] == "1"}
    conditions = (("normal", "Normal"), ("protan100", "Protan 100%"),
                  ("deutan100", "Deutan 100%"), ("tritan100", "Tritan 100%"),
                  ("grayscale", "Grayscale"))

    def pair(condition: str, first: str, second: str) -> dict:
        matches = [row for row in pair_changes if row["condition"] == condition
                   and {row["colour1"], row["colour2"]} == {first, second}]
        if len(matches) != 1:
            raise ValueError(f"Expected one pair for {condition}: {first}/{second}")
        return matches[0]

    blue_table = [["Condition", "Okabe-Ito", "Veen-Clark", "Change"]]
    yellow_table = [["Condition", "Pair", "Okabe-Ito", "Veen-Clark", "Change"]]
    for condition, label in conditions:
        row = pair(condition, "sky_blue", "blue")
        blue_table.append([label, f"{float(row['baseline_delta_e_00']):.2f}",
                           f"{float(row['palette_delta_e_00']):.2f}",
                           f"{float(row['change_from_baseline']):+.2f}"])
        for other in ("orange", "bluish_green"):
            row = pair(condition, "yellow", other)
            yellow_table.append([label, "Yellow / " + other.replace("_", " "),
                                 f"{float(row['baseline_delta_e_00']):.2f}",
                                 f"{float(row['palette_delta_e_00']):.2f}",
                                 f"{float(row['change_from_baseline']):+.2f}"])
    yellow = next(row for row in colours_data if row["id"] == "yellow")

    story: list = [
        Spacer(1, 21 * mm),
        Paragraph("Veen-Clark palette", STYLES["Title"]),
        Paragraph(f"Version {RELEASE['version']} evaluation", STYLES["Subtitle"]),
        Spacer(1, 8 * mm),
        figure(AUDIT / "figures" / "palette_normal.png", "Veen-Clark palette in normal sRGB.", 65 * mm),
        Spacer(1, 8 * mm),
        body(
            "An Okabe-Ito derivative by Roland J. Veen and Charlie Clark. "
            "Sky blue is lightened and blue is darkened so the pair can represent related "
            "subgroups in scientific scatter and bar charts. "
            f"The palette uses yellow {HEX['yellow']}."
        ),
        Spacer(1, 3 * mm),
        body(
            "This report compares colour-difference metrics for the Veen-Clark "
            "and Okabe-Ito palettes."
        ),
        Spacer(1, 8 * mm),
        body(
            f"Generated with PaletteBench {metadata['palettebench_version']} using Python "
            f"{metadata['python_version']}. Exact inputs, hashes, dependencies, full-precision "
            "CSV/JSON data, and individual vector figures accompany this PDF in the repository."
        ),
        PageBreak(),
        heading("Results"),
        body(
            "The intended sky-blue/blue subgroup pair has greater modelled separation "
            "relative to Okabe-Ito under every standard reported condition: normal, protan "
            "100%, deutan 100%, tritan 100%, and grayscale."
        ),
        Spacer(1, 4 * mm),
        styled_table(
            blue_table,
            [55 * mm, 35 * mm, 35 * mm, 30 * mm],
            8.5,
        ),
        Spacer(1, 5 * mm),
        body(
            "The whole-palette result is mixed. The normal-vision 10th percentile rises by "
            f"{float(comparison['normal']['q10_change_from_baseline']):.2f} Delta E00 "
            f"and the protan-100% minimum rises by {float(comparison['protan100']['minimum_change_from_baseline']):.2f}, but darkening blue "
            "reduces separation from black and produces the largest loss against vermillion "
            f"under tritan 100% ({float(pair('tritan100', 'blue', 'vermillion')['change_from_baseline']):.2f} Delta E00)."
        ),
        Spacer(1, 6 * mm),
        figure(
            ROOT / "examples" / "blue-subgroups.png",
            "Figure 1. Synthetic data illustrating the two blues with circular markers and solid bar fills.",
            100 * mm,
        ),
        PageBreak(),
        heading("Yellow in context"),
        body(
            "Informal feedback from people with regular colour vision suggested that the "
            "original yellow could appear greenish and insufficiently distinct in presentations. "
            "This motivated the yellow choice; it was not a controlled participant study. "
            "The table reports modelled separation from orange and bluish green."
        ),
        Spacer(1, 5 * mm),
        styled_table(yellow_table, [29 * mm, 55 * mm, 28 * mm, 28 * mm, 28 * mm]),
        Spacer(1, 5 * mm),
        body(
            f"Yellow's normal-sRGB contrast ratio against white is {float(yellow['contrast_white']):.2f}:1. "
            "Pairwise colour separation does not establish visibility on a white slide. "
            "PaletteBench does not model projector colour errors or audience perception. "
            "Check the actual figure under its intended viewing conditions."
        ),
        PageBreak(),
        heading("Baseline-relative comparison"),
        figure(COMPARISON / "figures" / "palette_comparison.png", "Figure 2. Okabe-Ito baseline and Veen-Clark under the standard reported conditions.", 90 * mm),
        Spacer(1, 5 * mm),
        figure(COMPARISON / "figures" / "minimum_distance_comparison.png", "Figure 3. Whole-palette minimum Delta E00 by condition.", 95 * mm),
        PageBreak(),
        heading("Baseline-relative comparison", 1),
        figure(COMPARISON / "figures" / "minimum_change_comparison.png", "Figure 4. Change in minimum separation relative to Okabe-Ito.", 105 * mm),
        Spacer(1, 5 * mm),
        body(
            "Positive changes indicate greater modelled separation; negative changes indicate "
            "reduced modelled separation. Zero change means the minimum separation is unchanged."
        ),
        PageBreak(),
        heading("Methods and assumptions"),
        body(
            "Six-digit values are interpreted as gamma-encoded sRGB. PaletteBench applies "
            "Colorspacious sRGB1+CVD simulations based on Machado, Oliveira and Fernandes, "
            "clips results to displayable sRGB, converts through CIE XYZ to CIE Lab under the "
            "sRGB D65 white point, and calculates CIEDE2000 colour differences with Colour "
            "Science for Python. Grayscale preserves WCAG relative luminance."
        ),
        Spacer(1, 4 * mm),
        body(
            "Severity percentages are simulation parameters, not clinical measurements. "
            "Partial tritan severity is omitted from the standard report. Clipping provenance "
            "and raw values are retained in the machine-readable audit directory."
        ),
        Spacer(1, 7 * mm),
        figure(AUDIT / "figures" / "cvd_overview.png", "Figure 5. Normal, simulated CVD, and grayscale overview.", 145 * mm),
        PageBreak(),
        heading("Palette characteristics"),
    ]

    colour_table = [["Colour", "Hex", "RGB", "L*", "Chroma", "Luminance", "Group"]]
    for row in colours_data:
        colour_table.append(
            [
                row["name"],
                row["hex"],
                " ".join(
                    str(round(float(row[channel]) * 255))
                    for channel in ("srgb_r", "srgb_g", "srgb_b")
                ),
                f"{float(row['lab_l']):.2f}",
                f"{float(row['chroma']):.2f}",
                f"{float(row['relative_luminance']):.4f}",
                row["group"] or "-",
            ]
        )
    story += [
        styled_table(colour_table, [32 * mm, 22 * mm, 28 * mm, 18 * mm, 23 * mm, 27 * mm, 31 * mm]),
        Spacer(1, 7 * mm),
        heading("Condition-level summary", 2),
    ]
    summary_table = [["Condition", "Min", "Weakest pair", "Mean", "Median", "10th pct."]]
    for row in summary:
        summary_table.append(
            [
                row["condition"],
                f"{float(row['minimum']):.2f}",
                row["minimum_pair"].replace("/", " / "),
                f"{float(row['mean']):.2f}",
                f"{float(row['median']):.2f}",
                f"{float(row['q10']):.2f}",
            ]
        )
    story += [
        styled_table(summary_table, [29 * mm, 18 * mm, 55 * mm, 21 * mm, 21 * mm, 24 * mm], 7),
        PageBreak(),
        heading("Palette strips"),
    ]
    for filename, caption in (
        ("palette_normal.png", "Normal sRGB"),
        ("palette_protan100.png", "Simulated protan 100%"),
        ("palette_deutan100.png", "Simulated deutan 100%"),
        ("palette_tritan100.png", "Simulated tritan 100%"),
        ("palette_grayscale.png", "WCAG-luminance grayscale"),
    ):
        story += [figure(AUDIT / "figures" / filename, caption, 29 * mm), Spacer(1, 2.5 * mm)]

    story += [PageBreak(), heading("Severity progressions")]
    for filename, caption in (
        ("severity_protan.png", "Figure 6. Protan simulation progression from 20% to 100%."),
        ("severity_deutan.png", "Figure 7. Deutan simulation progression from 20% to 100%."),
        ("minimum_distance_severity.png", "Figure 8. Minimum pairwise distance across simulated severity."),
    ):
        story += [figure(AUDIT / "figures" / filename, caption, 72 * mm), Spacer(1, 4 * mm)]

    for title, filename in (
        ("Normal pairwise heatmap", "heatmap_normal.png"),
        ("Protan 100% pairwise heatmap", "heatmap_protan100.png"),
        ("Deutan 100% pairwise heatmap", "heatmap_deutan100.png"),
        ("Tritan 100% pairwise heatmap", "heatmap_tritan100.png"),
    ):
        story += [PageBreak(), heading(title), figure(AUDIT / "figures" / filename, title + ".", 220 * mm)]

    for title, filename in (
        ("Normal diagonal split pair matrix", "pairs_normal.png"),
        ("Protan 100% diagonal split pair matrix", "pairs_protan100.png"),
        ("Deutan 100% diagonal split pair matrix", "pairs_deutan100.png"),
        ("Tritan 100% diagonal split pair matrix", "pairs_tritan100.png"),
    ):
        story += [
            PageBreak(),
            heading(title),
            body(
                "The lower triangle places each colour pair in direct diagonal contact; the "
                "upper triangle reports its Delta E00 value."
            ),
            Spacer(1, 3 * mm),
            figure(AUDIT / "figures" / filename, title + ".", 220 * mm),
        ]

    group_table = [["Condition", "Severity", "Pairs", "Minimum", "Mean", "Maximum"]]
    for row in groups:
        if row["relationship"] != "within":
            continue
        group_table.append(
            [
                row["condition"],
                row["severity"],
                row["count"],
                f"{float(row['minimum']):.2f}",
                f"{float(row['mean']):.2f}",
                f"{float(row['maximum']):.2f}",
            ]
        )
    story += [
        PageBreak(),
        heading("Grouped blue-family analysis"),
        body(
            "The YAML declares sky blue and blue as one visual family. With two members, the "
            "group contains one colour pair: sky blue and blue."
        ),
        Spacer(1, 5 * mm),
        styled_table(group_table, [42 * mm, 24 * mm, 20 * mm, 27 * mm, 27 * mm, 27 * mm]),
        PageBreak(),
        heading("Weakest-pair diagnostic"),
        figure(AUDIT / "figures" / "weakest_pairs.png", "Figure 9. Weakest pairs under each standard condition.", 205 * mm),
        PageBreak(),
        heading("Interpretation and limitations"),
        body(
            "The palette improves its intended blue-family separation in all standard "
            "PaletteBench conditions. It does not improve every pair. In particular, the darker "
            "blue approaches black, and its tritan-simulated relationship with vermillion loses "
            "separation relative to Okabe-Ito. Redundant encodings remain appropriate whenever "
            "category identity is critical."
        ),
        Spacer(1, 4 * mm),
        body(
            "CVD simulations and perceptual-distance models do not reproduce a particular "
            "person's perception. Monitor calibration, viewing environment, acuity, ageing, "
            "print reproduction, surrounding colours, spatial context, and mark size can all "
            "change discriminability. Human evaluation is outside this computational audit."
        ),
        Spacer(1, 7 * mm),
        heading("Reproducibility", 2),
        body(
            f"Palette input SHA-256: {metadata['input_sha256']}. PaletteBench version: "
            f"{metadata['palettebench_version']}. Metric: {metadata['configuration']['metric']}. "
            f"Simulation: {metadata['configuration']['simulation']}."
        ),
        Spacer(1, 7 * mm),
        PageBreak(),
        heading("Responsible use of AI"),
        *[markdown_paragraph(text) for text in readme_section("Responsible use of AI")],
        Spacer(1, 7 * mm),
        heading("References", 2),
        *[markdown_paragraph(text) for text in readme_section("References")],
    ]
    return story


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"Veen-Clark palette: version {RELEASE['version']} evaluation",
        author="Roland J. Veen and Charlie Clark",
        subject="PaletteBench audit and Okabe-Ito comparison",
    )
    document.build(
        build_story(),
        onFirstPage=page_chrome,
        onLaterPages=page_chrome,
        canvasmaker=InvariantCanvas,
    )


STYLES = getSampleStyleSheet()
STYLES["Title"].fontName = "Helvetica-Bold"
STYLES["Title"].fontSize = 27
STYLES["Title"].leading = 31
STYLES["Title"].textColor = PALETTE[0]
STYLES.add(
    ParagraphStyle(
        "Subtitle",
        parent=STYLES["BodyText"],
        fontName="Helvetica",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#496674"),
        spaceAfter=3 * mm,
    )
)
for level, size in ((1, 18), (2, 12)):
    style = STYLES[f"Heading{level}"]
    style.fontName = "Helvetica-Bold"
    style.fontSize = size
    style.leading = size + 4
    style.textColor = PALETTE[0]
    style.spaceAfter = 4 * mm
STYLES["BodyText"].fontName = "Helvetica"
STYLES["BodyText"].fontSize = 9.5
STYLES["BodyText"].leading = 13
STYLES["BodyText"].spaceAfter = 2.5 * mm


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
