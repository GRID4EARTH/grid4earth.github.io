# Extracted from scripts/figures/make_dggs_figures.py
# Shared helpers (geodetic_to_unit_ecef, orthographic, cell_edges,
# _sphere_cell_segments, _arrow) live in that file.

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
