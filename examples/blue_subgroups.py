"""Render scatter and bar examples for the related blue subgroups."""

import argparse
import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load_colors() -> dict[str, str]:
    """Import the generated Python export without requiring package installation."""
    export = ROOT / "exports" / "veen_clark.py"
    spec = importlib.util.spec_from_file_location("veen_clark", export)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return dict(zip(module.NAMES, module.HEX))


def render(output: Path) -> None:
    """Write deterministic example plots to ``output`` in SVG and PNG formats."""
    colors = load_colors()
    sky_blue, blue = colors["sky_blue"], colors["blue"]
    rng = np.random.default_rng(20261001)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), constrained_layout=True)

    # Keep geometry identical so the example shows the contribution of colour
    # itself rather than gaining extra separation from marker shape or texture.
    for center, color, label in (
        ((0.0, 0.0), sky_blue, "Subgroup A"),
        ((1.15, 0.8), blue, "Subgroup B"),
    ):
        points = rng.normal(center, (0.42, 0.34), size=(45, 2))
        axes[0].scatter(
            points[:, 0],
            points[:, 1],
            s=38,
            color=color,
            marker="o",
            edgecolor="white",
            linewidth=0.45,
            label=label,
        )
    axes[0].set(title="Related subgroups: scatter", xlabel="Measure 1", ylabel="Measure 2")
    axes[0].legend(frameon=False)

    x = np.arange(4)
    width = 0.36
    axes[1].bar(
        x - width / 2, [6.2, 7.8, 6.9, 8.7], width, color=sky_blue, label="Subgroup A"
    )
    axes[1].bar(
        x + width / 2,
        [5.1, 6.4, 8.1, 7.5],
        width,
        color=blue,
        label="Subgroup B",
    )
    axes[1].set(
        title="Related subgroups: bars",
        xlabel="Condition",
        ylabel="Value",
        xticks=x,
        xticklabels=["I", "II", "III", "IV"],
    )
    axes[1].legend(frameon=False)

    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)

    output.mkdir(parents=True, exist_ok=True)
    for suffix in ("svg", "png"):
        fig.savefig(output / f"blue-subgroups.{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    render(args.output)


if __name__ == "__main__":
    main()
