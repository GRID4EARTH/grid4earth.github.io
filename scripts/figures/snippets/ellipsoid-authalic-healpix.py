# Extracted from scripts/figures/make_dggs_figures.py
# Shared helpers (geodetic_to_unit_ecef, orthographic, cell_edges,
# _sphere_cell_segments, _arrow) live in that file.

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
