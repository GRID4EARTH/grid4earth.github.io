# Extracted from scripts/figures/make_dggs_figures.py
# Shared helpers (geodetic_to_unit_ecef, orthographic, cell_edges,
# _sphere_cell_segments, _arrow) live in that file.

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
