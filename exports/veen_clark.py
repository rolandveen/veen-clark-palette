"""Generated from palettes/veen-clark-candidate.yaml by tools/generate_exports.py; do not edit."""

NAMES = ['orange', 'sky_blue', 'bluish_green', 'yellow', 'blue', 'vermillion', 'reddish_purple', 'black']
HEX = ['#E69F00', '#7CC7F2', '#009E73', '#F0E442', '#005A8D', '#D55E00', '#CC79A7', '#000000']
RGB = [
    (0.901961, 0.623529, 0.000000),
    (0.486275, 0.780392, 0.949020),
    (0.000000, 0.619608, 0.450980),
    (0.941176, 0.894118, 0.258824),
    (0.000000, 0.352941, 0.552941),
    (0.835294, 0.368627, 0.000000),
    (0.800000, 0.474510, 0.654902),
    (0.000000, 0.000000, 0.000000),
]

def as_listed_colormap():
    from matplotlib.colors import ListedColormap
    return ListedColormap(HEX, name="veen_clark")
