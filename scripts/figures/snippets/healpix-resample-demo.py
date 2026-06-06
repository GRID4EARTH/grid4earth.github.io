# Extracted from scripts/figures/make_dggs_figures.py
# Shared helpers (geodetic_to_unit_ecef, orthographic, cell_edges,
# _sphere_cell_segments, _arrow) live in that file.

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
