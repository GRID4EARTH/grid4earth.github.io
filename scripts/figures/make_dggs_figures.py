"""Generate GRID4EARTH DGGS illustrations — on the WGS84 ellipsoid.

The grid is evaluated with ``healpix-geo`` using ``ellipsoid="WGS84"`` (not a
sphere), so the figures show HEALPix as GRID4EARTH actually uses it.

Usage:
    python -m venv .venv && . .venv/bin/activate
    pip install healpix-geo matplotlib numpy
    python scripts/figures/make_dggs_figures.py

Outputs PNGs into ``static/img/``.
"""

import inspect
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch

import healpix_geo.nested as hpx

# ── WGS84 reference ellipsoid ────────────────────────────────────────────────
A = 6378137.0                      # semi-major axis (m)
F = 1.0 / 298.257223563            # flattening
B = A * (1.0 - F)                  # semi-minor axis (m)
E2 = 1.0 - (B / A) ** 2            # first eccentricity squared

OUT = Path(__file__).resolve().parents[2] / "static" / "img"

NAVY = "#0a2540"
TEAL = "#2a9d8f"
RED = "#c0392b"
GRID = "#5b6b7b"
OCEAN = "#dbe6f3"

# Larger default fonts so labels stay legible at display size.
plt.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
})


def geodetic_to_unit_ecef(lon_deg, lat_deg):
    """Geodetic (lon, lat) on WGS84 -> ECEF XYZ, normalised by A."""
    lon = np.radians(lon_deg)
    lat = np.radians(lat_deg)
    n = A / np.sqrt(1.0 - E2 * np.sin(lat) ** 2)
    x = n * np.cos(lat) * np.cos(lon)
    y = n * np.cos(lat) * np.sin(lon)
    z = n * (1.0 - E2) * np.sin(lat)
    return np.stack([x, y, z]) / A


def orthographic(xyz, lon0, lat0):
    """Rotate so (lon0, lat0) faces the viewer (+X); return (Y, Z, frontmask)."""
    lon0, lat0 = np.radians(lon0), np.radians(lat0)
    x, y, z = xyz
    # rotate about Z by -lon0
    x1 = x * np.cos(lon0) + y * np.sin(lon0)
    y1 = -x * np.sin(lon0) + y * np.cos(lon0)
    z1 = z
    # rotate about Y by lat0
    x2 = x1 * np.cos(lat0) + z1 * np.sin(lat0)
    z2 = -x1 * np.sin(lat0) + z1 * np.cos(lat0)
    return y1, z2, x2 > 0.0


def cell_edges(ipix, depth, view, step=12):
    """LineCollection segments for front-facing HEALPix cell boundaries on WGS84."""
    lon, lat = hpx.vertices(ipix, depth, "WGS84", step=step)
    lon, lat = np.asarray(lon), np.asarray(lat)
    segs = []
    for cl, ca in zip(lon, lat):
        cl = np.append(cl, cl[0])
        ca = np.append(ca, ca[0])
        yy, zz, front = orthographic(geodetic_to_unit_ecef(cl, ca), *view)
        if front.mean() < 0.5:           # mostly back hemisphere -> skip
            continue
        pts = np.column_stack([yy, zz])
        pts[~front] = np.nan             # break edges crossing the limb
        segs.append(pts)
    return segs


def make_globe(out="healpix-ellipsoid-globe.png", depth=2, view=(15.0, 25.0)):
    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=200)
    # ocean disk
    ax.add_patch(plt.Circle((0, 0), 1.0, color=OCEAN, zorder=0))
    # graticule (every 30°)
    for lat in range(-60, 61, 30):
        lon = np.linspace(-180, 180, 200)
        yy, zz, fr = orthographic(geodetic_to_unit_ecef(lon, np.full_like(lon, lat)), *view)
        yy[~fr] = np.nan
        ax.plot(yy, zz, color="#ffffff", lw=0.8, zorder=1)
    for lon in range(-180, 180, 30):
        lat = np.linspace(-89.5, 89.5, 200)
        yy, zz, fr = orthographic(geodetic_to_unit_ecef(np.full_like(lat, lon), lat), *view)
        yy[~fr] = np.nan
        ax.plot(yy, zz, color="#ffffff", lw=0.8, zorder=1)
    # HEALPix: deeper cells (thin) then the 12 base cells (thick red)
    fine = np.arange(12 * 4 ** depth, dtype="uint64")
    ax.add_collection(LineCollection(cell_edges(fine, depth, view), colors=GRID, linewidths=0.6, zorder=2))
    base = np.arange(12, dtype="uint64")
    ax.add_collection(LineCollection(cell_edges(base, 0, view), colors=RED, linewidths=1.8, zorder=3))
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=0.1)
    fig.savefig(OUT / out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def make_sphere_vs_ellipsoid(out="healpix-sphere-vs-ellipsoid.png", depth=10):
    """Where does the reference surface change a point's HEALPix cell?"""
    lons = np.linspace(-180, 180, 1440)
    lats = np.linspace(-89.5, 89.5, 720)
    lon_g, lat_g = np.meshgrid(lons, lats)
    s = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="sphere")
    e = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="WGS84")
    diff = (s != e).reshape(lat_g.shape)
    frac = 100.0 * diff.mean(axis=1)

    fig, (axm, axc) = plt.subplots(
        1, 2, figsize=(12.5, 5.2), dpi=200, gridspec_kw={"width_ratios": [2.0, 1.0]}
    )
    axm.imshow(
        diff, extent=[-180, 180, -90, 90], origin="lower",
        cmap=plt.matplotlib.colors.ListedColormap(["#eef3f9", TEAL]), aspect="auto",
    )
    axm.set_title(f"Points assigned a different cell\n(sphere vs WGS84, depth {depth})")
    axm.set_xlabel("longitude"); axm.set_ylabel("latitude")
    axm.set_xticks([-180, -90, 0, 90, 180]); axm.set_yticks([-90, -45, 0, 45, 90])

    axc.plot(frac, lats, color=NAVY, lw=2)
    axc.fill_betweenx(lats, 0, frac, color=TEAL, alpha=0.25)
    axc.set_title("% reassigned vs latitude")
    axc.set_xlabel("% of points"); axc.set_ylim(-90, 90)
    axc.set_yticks([-90, -45, 0, 45, 90]); axc.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out, f"(max {frac.max():.1f}% reassigned)")


def _sphere_cell_segments(centre, r, squash=1.0, depth=1, view=(28.0, 18.0)):
    """Front-facing HEALPix cell boundaries on a unit sphere, placed/scaled in axes coords."""
    cells = np.arange(12 * 4 ** depth, dtype="uint64")
    lon, lat = hpx.vertices(cells, depth, "sphere", step=8)
    segs = []
    for cl, ca in zip(np.asarray(lon), np.asarray(lat)):
        cl, ca = np.append(cl, cl[0]), np.append(ca, ca[0])
        lo, la = np.radians(cl), np.radians(ca)
        xyz = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
        yy, zz, front = orthographic(xyz, *view)
        if front.mean() < 0.5:
            continue
        px = centre[0] + yy * r
        py = centre[1] + zz * r * squash
        px[~front] = np.nan
        py[~front] = np.nan
        segs.append(np.column_stack([px, py]))
    return segs


def _arrow(ax, p0, p1, text):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=16,
                                 lw=1.6, color=NAVY, shrinkA=6, shrinkB=6))
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    ax.text(mx, my + 0.18, text, ha="center", va="bottom", fontsize=10.5,
            style="italic", color=NAVY)


def make_authalic_schematic(out="ellipsoid-authalic-healpix.png"):
    """How healpix-geo works: ellipsoid -> authalic sphere -> HEALPix -> ellipsoid pixelization."""
    fig, ax = plt.subplots(figsize=(10.8, 7.8), dpi=200)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.4)
    ax.set_aspect("equal")
    ax.axis("off")
    TL, TR, BR, BL = (2.3, 5.4), (7.7, 5.4), (7.7, 1.7), (2.3, 1.7)
    aw, ah = 3.0, 2.0  # ellipse axes (flattening exaggerated for clarity)

    # 1. ELLIPSOID with geodetic (phi) and geocentric (theta) latitude
    ax.add_patch(Ellipse(TL, aw, ah, fill=False, lw=2, ec=NAVY))
    t = np.radians(48)
    a, b = aw / 2, ah / 2
    pt = (TL[0] + a * np.cos(t), TL[1] + b * np.sin(t))
    ax.plot([TL[0], pt[0]], [TL[1], pt[1]], color=GRID, lw=1)               # radius (theta)
    nrm = np.array([np.cos(t) / a, np.sin(t) / b])
    nrm = nrm / np.hypot(*nrm)
    ax.plot([pt[0] - nrm[0] * 1.0, pt[0]], [pt[1] - nrm[1] * 1.0, pt[1]], color=RED, lw=1)  # normal (phi)
    ax.plot([TL[0], TL[0] + a + 0.5], [TL[1], TL[1]], color="#aab4c0", lw=0.8, ls=":")
    ax.text(pt[0] + 0.08, pt[1] + 0.05, r"$P_0$", fontsize=11)
    ax.text(TL[0] + 0.55, TL[1] + 0.12, r"$\theta$", fontsize=11, color=GRID)
    ax.text(pt[0] - 0.55, pt[1] - 0.02, r"$\varphi$", fontsize=11, color=RED)
    ax.text(TL[0], TL[1] - b - 0.45, "ELLIPSOID", ha="center", fontsize=12, weight="bold", color=NAVY)

    # 2. AUTHALIC SPHERE with authalic latitude (xi)
    ax.add_patch(Circle(TR, b, fill=False, lw=2, ec=NAVY))
    tx = np.radians(48)
    px = (TR[0] + b * np.cos(tx), TR[1] + b * np.sin(tx))
    ax.plot([TR[0], px[0]], [TR[1], px[1]], color=TEAL, lw=1)
    ax.plot([TR[0], TR[0] + b + 0.5], [TR[1], TR[1]], color="#aab4c0", lw=0.8, ls=":")
    ax.text(px[0] + 0.08, px[1] + 0.05, r"$P_\xi$", fontsize=11)
    ax.text(TR[0] + 0.45, TR[1] + 0.12, r"$\xi$", fontsize=11, color=TEAL)
    ax.text(TR[0], TR[1] - b - 0.45, "AUTHALIC SPHERE", ha="center", fontsize=12, weight="bold", color=NAVY)

    # 3. HEALPix on the sphere
    ax.add_patch(Circle(BR, b, fill=False, lw=1.5, ec=NAVY))
    ax.add_collection(LineCollection(_sphere_cell_segments(BR, b), colors=TEAL, lw=0.7))
    ax.text(BR[0], BR[1] - b - 0.45, "HEALPix", ha="center", fontsize=12, weight="bold", color=NAVY)

    # 4. ELLIPSOID PIXELIZATION
    ax.add_patch(Ellipse(BL, aw, ah, fill=False, lw=1.5, ec=NAVY))
    ax.add_collection(LineCollection(_sphere_cell_segments(BL, a, squash=b / a), colors=TEAL, lw=0.7))
    ax.text(BL[0], BL[1] - b - 0.45, "ELLIPSOID PIXELIZATION", ha="center", fontsize=12, weight="bold", color=NAVY)

    # arrows
    _arrow(ax, (TL[0] + a + 0.4, TL[1]), (TR[0] - b - 0.4, TR[1]), "authalic mapping\n(same surface area)")
    _arrow(ax, (TR[0], TR[1] - b - 0.95), (BR[0], BR[1] + b + 0.55), "HEALPix\npixelisation")
    _arrow(ax, (BR[0] - b - 0.4, BR[1]), (BL[0] + a + 0.4, BL[1]), "reverse mapping\n(area preserving)")

    # properties (BR list on the right, BL list on the left to avoid the arrow label)
    props = "✓ hierarchical\n✓ iso-latitude\n✓ equal area"
    ax.text(BR[0] + b + 0.35, BR[1], props, fontsize=11.5, color=TEAL, va="center", ha="left")
    ax.text(BL[0] - a - 0.35, BL[1], props, fontsize=11.5, color=TEAL, va="center", ha="right")
    ax.text(5.0, 3.55,
            r"$\varphi$  geodetic     $\theta$  geocentric     $\xi$  authalic",
            ha="center", fontsize=11.5, color=GRID,
            bbox=dict(boxstyle="round,pad=0.3", fc="#f4f7fb", ec="#d9e1ea"))
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


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
    uniq, inv = np.unique(cells, return_inverse=True)
    means = np.bincount(inv, weights=field.ravel()) / np.bincount(inv)
    hp = means[inv].reshape(lat_g.shape)

    fig, (a0, a1) = plt.subplots(1, 2, figsize=(12.0, 4.4), dpi=200)
    kw = dict(extent=[-180, 180, -90, 90], origin="lower", cmap="viridis", aspect="auto")
    for ax, img, title in ((a0, field, "Original field (lon/lat grid)"),
                           (a1, hp, f"Aggregated onto HEALPix cells\n(equal-area, depth {depth}, WGS84)")):
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
    "healpix-ellipsoid-globe": make_globe,
    "ellipsoid-authalic-healpix": make_authalic_schematic,
    "healpix-sphere-vs-ellipsoid": make_sphere_vs_ellipsoid,
    "healpix-resample-demo": make_data_demo,
}


def write_snippets():
    """Emit one .py snippet per figure (the generating function) for the website."""
    snip = Path(__file__).resolve().parent / "snippets"
    snip.mkdir(exist_ok=True)
    header = (
        "# Extracted from scripts/figures/make_dggs_figures.py\n"
        "# Shared helpers (geodetic_to_unit_ecef, orthographic, cell_edges,\n"
        "# _sphere_cell_segments, _arrow) live in that file.\n\n"
    )
    for name, fn in FIGURE_FUNCS.items():
        (snip / f"{name}.py").write_text(header + inspect.getsource(fn))
        print("wrote snippet", name)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in FIGURE_FUNCS.values():
        fn()
    write_snippets()
