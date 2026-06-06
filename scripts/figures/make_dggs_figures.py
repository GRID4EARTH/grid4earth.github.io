"""Generate GRID4EARTH DGGS figures with healpix-geo (on the WGS84 ellipsoid).

Produces the matplotlib figures used in the "How healpix-geo keeps equal area"
section and emits one .py snippet per figure (for the website's "show the code"
boxes). The interactive globe is built separately by make_healpix_globe.py, and
the ellipsoid→authalic schematic by make_authalic_schematic.py.

Usage:
    python -m venv .venv && . .venv/bin/activate
    pip install -r scripts/figures/requirements.txt
    python scripts/figures/make_dggs_figures.py
"""

import inspect
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import healpix_geo.nested as hpx

OUT = Path(__file__).resolve().parents[2] / "static" / "img"

NAVY = "#0a2540"
TEAL = "#2a9d8f"

# Larger default fonts so labels stay legible at display size.
plt.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
})


def make_sphere_vs_ellipsoid(out="healpix-sphere-vs-ellipsoid.png", depth=10):
    """How often the reference surface (sphere vs WGS84) changes a point's HEALPix
    cell, as a function of latitude. A clean curve — no per-pixel map (which would
    alias into moiré near the poles where HEALPix cells fan out)."""
    lons = np.linspace(-180, 180, 1440)
    lats = np.linspace(-89.5, 89.5, 720)
    lon_g, lat_g = np.meshgrid(lons, lats)
    s = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="sphere")
    e = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="WGS84")
    frac = 100.0 * (s != e).reshape(lat_g.shape).mean(axis=1)

    fig, ax = plt.subplots(figsize=(11.0, 4.6), dpi=200)
    ax.fill_between(lats, 0, frac, color=TEAL, alpha=0.22)
    ax.plot(lats, frac, color=NAVY, lw=2.5)
    ax.set_title(f"Spherical vs WGS84 HEALPix: cell reassignment by latitude (depth {depth})")
    ax.set_xlabel("latitude (°)")
    ax.set_ylabel("% of points moved to a different cell")
    ax.set_xlim(-90, 90); ax.set_ylim(0, max(5, frac.max() * 1.08))
    ax.set_xticks([-90, -60, -30, 0, 30, 60, 90])
    ax.grid(alpha=0.3)
    ax.margins(x=0)
    fig.tight_layout()
    fig.savefig(OUT / out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out, f"(max {frac.max():.1f}% reassigned)")


def make_data_demo(out="healpix-resample-demo.png", depth=4):
    """A continuous field aggregated onto equal-area HEALPix cells (WGS84)."""
    lons = np.linspace(-180, 180, 720)
    lats = np.linspace(-90, 90, 360)
    lon_g, lat_g = np.meshgrid(lons, lats)
    field = (
        np.sin(np.radians(3 * lon_g)) * np.cos(np.radians(2 * lat_g))
        + 1.8 * np.exp(-(((lon_g - 25) / 28) ** 2 + ((lat_g - 12) / 18) ** 2))
        + 1.4 * np.exp(-(((lon_g + 95) / 38) ** 2 + ((lat_g + 28) / 22) ** 2))
    )
    cells = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="WGS84")
    _, inv = np.unique(cells, return_inverse=True)
    means = np.bincount(inv, weights=field.ravel()) / np.bincount(inv)
    aggregated = means[inv].reshape(lat_g.shape)

    fig, (a0, a1) = plt.subplots(1, 2, figsize=(12.0, 4.4), dpi=200)
    kw = dict(extent=[-180, 180, -90, 90], origin="lower", cmap="viridis", aspect="auto")
    for ax, img, title in ((a0, field, "Original field (lon/lat grid)"),
                           (a1, aggregated, f"Aggregated onto HEALPix cells\n(equal-area, depth {depth}, WGS84)")):
        ax.imshow(img, **kw)
        ax.set_title(title)
        ax.set_xticks([-180, -90, 0, 90, 180]); ax.set_yticks([-90, -45, 0, 45, 90])
        ax.set_xlabel("longitude")
    a0.set_ylabel("latitude")
    fig.tight_layout()
    fig.savefig(OUT / out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out)


# Map each output figure to the function that produces it, so the website can
# show the exact code under each image.
FIGURE_FUNCS = {
    "healpix-sphere-vs-ellipsoid": make_sphere_vs_ellipsoid,
    "healpix-resample-demo": make_data_demo,
}


def write_snippets():
    """Emit one .py snippet per figure (the generating function) for the website."""
    snip = Path(__file__).resolve().parent / "snippets"
    snip.mkdir(exist_ok=True)
    header = (
        "# Extracted from scripts/figures/make_dggs_figures.py\n\n"
    )
    for name, fn in FIGURE_FUNCS.items():
        (snip / f"{name}.py").write_text(header + inspect.getsource(fn))
        print("wrote snippet", name)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in FIGURE_FUNCS.values():
        fn()
    write_snippets()
