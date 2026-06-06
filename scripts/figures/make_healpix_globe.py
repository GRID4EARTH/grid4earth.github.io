"""Interactive HEALPix globe (Plotly) for the GRID4EARTH homepage.

Reproduces the GRID4EARTH BIDS25_demo / dggs_intro globe: a rotatable dark 3D
globe with the HEALPix grid (NESTED), the cell-ID numbers at each cell centre,
coastlines, and hover that reports lon/lat. Writes a standalone HTML embed to
static/embeds/healpix-globe.html (Plotly.js from CDN).

Deps: plotly, healpy, numpy.  Coastlines come from a Natural Earth 110m GeoJSON
fetched at build time — no cartopy needed.

Usage:
    pip install plotly healpy numpy
    python scripts/figures/make_healpix_globe.py
"""

import json
import urllib.request
from pathlib import Path

import healpy as hp
import numpy as np
import plotly.graph_objects as go

OUT = Path(__file__).resolve().parents[2] / "static" / "embeds"
COAST_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    "master/geojson/ne_110m_coastline.geojson"
)

NSIDE = 2            # refinement level 1 -> 48 cells (matches the demo)
RED = "#e8392a"     # HEALPix grid + cell-id labels
CYAN = "#00b5e2"    # coastlines


def sph2cart(lon, lat, r=1.0):
    lon, lat = np.radians(lon), np.radians(lat)
    return (
        r * np.cos(lat) * np.cos(lon),
        r * np.cos(lat) * np.sin(lon),
        r * np.sin(lat),
    )


def healpix_grid_trace(r=1.005):
    """All NESTED cell boundaries at NSIDE as one red Scatter3d (NaN-separated)."""
    xs, ys, zs = [], [], []
    for pix in range(hp.nside2npix(NSIDE)):
        x, y, z = hp.boundaries(NSIDE, pix, step=24, nest=True)
        xs += [*(r * x), r * x[0], np.nan]
        ys += [*(r * y), r * y[0], np.nan]
        zs += [*(r * z), r * z[0], np.nan]
    return go.Scatter3d(x=xs, y=ys, z=zs, mode="lines",
                        line=dict(color=RED, width=2), hoverinfo="skip", showlegend=False)


def cell_label_trace(r=1.01):
    """Cell-id numbers at each cell centre; hover shows the cell id + lon/lat.
    Centres sit on the globe so the opaque surface hides the back-facing labels."""
    ipix = np.arange(hp.nside2npix(NSIDE))
    lon, lat = hp.pix2ang(NSIDE, ipix, nest=True, lonlat=True)
    x, y, z = sph2cart(lon, lat, r=r)
    lon = ((lon + 180) % 360) - 180
    return go.Scatter3d(
        x=x, y=y, z=z, mode="text", text=[str(p) for p in ipix],
        textfont=dict(color=RED, size=12), showlegend=False,
        customdata=np.column_stack([ipix, lon, lat]),
        hovertemplate="cell %{customdata[0]}<br>lon %{customdata[1]:.1f}°, lat %{customdata[2]:.1f}°<extra></extra>",
    )


def coastline_trace(r=1.004):
    try:
        with urllib.request.urlopen(COAST_URL, timeout=60) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        print("WARNING: could not fetch coastlines:", exc)
        return None
    xs, ys, zs = [], [], []

    def add(coords):
        coords = np.asarray(coords)
        if coords.ndim != 2 or coords.shape[0] < 2:
            return
        x, y, z = sph2cart(coords[:, 0], coords[:, 1], r=r)
        xs.extend([*x, np.nan]); ys.extend([*y, np.nan]); zs.extend([*z, np.nan])

    for feat in data["features"]:
        geom = feat["geometry"]
        if geom["type"] == "LineString":
            add(geom["coordinates"])
        elif geom["type"] == "MultiLineString":
            for line in geom["coordinates"]:
                add(line)
    return go.Scatter3d(x=xs, y=ys, z=zs, mode="lines",
                        line=dict(color=CYAN, width=2), hoverinfo="skip", showlegend=False)


def build():
    fig = go.Figure()

    # dark globe surface; hover anywhere reports lon/lat
    u = np.linspace(0, 2 * np.pi, 120)
    v = np.linspace(0, np.pi, 120)
    R = 0.99
    xs = R * np.outer(np.cos(u), np.sin(v))
    ys = R * np.outer(np.sin(u), np.sin(v))
    zs = R * np.outer(np.ones_like(u), np.cos(v))
    lon2d = (np.degrees(u)[:, None] + 180) % 360 - 180
    lat2d = 90 - np.degrees(v)[None, :]
    custom = np.dstack([np.broadcast_to(lon2d, xs.shape), np.broadcast_to(lat2d, xs.shape)])
    fig.add_trace(go.Surface(
        x=xs, y=ys, z=zs, showscale=False,
        colorscale=[[0, "rgb(64,64,64)"], [1, "rgb(22,22,22)"]],
        lighting=dict(ambient=1, diffuse=0, specular=0),
        customdata=custom,
        hovertemplate="lon %{customdata[0]:.1f}°, lat %{customdata[1]:.1f}°<extra></extra>",
    ))

    fig.add_trace(healpix_grid_trace())
    coast = coastline_trace()
    if coast is not None:
        fig.add_trace(coast)
    fig.add_trace(cell_label_trace())

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode="data", bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.25, y=1.25, z=0.85)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "healpix-globe.html"
    build().write_html(
        out, include_plotlyjs="cdn", full_html=True,
        config={"displayModeBar": False, "responsive": True},
    )
    print("wrote", out)
