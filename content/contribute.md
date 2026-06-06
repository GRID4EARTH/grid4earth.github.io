+++
title = "Add to the community page"
description = "How to add your tool, example, replication study or dataset to the GRID4EARTH community page."
template = "page.html"
+++

The [community page](/community/) lists examples, replication studies and datasets
built with the GRID4EARTH HEALPix DGGS tools. Anyone can add an entry — the page
is generated from a simple list in the site's `config.toml`, so adding a card is a
few lines of text.

There are two ways to contribute: open a **pull request** (preferred), or open an
**issue** and a maintainer will add it for you.

## Option A — Open a pull request

1. **Fork and clone** the website repository:
   [`GRID4EARTH/grid4earth.github.io`](https://github.com/GRID4EARTH/grid4earth.github.io).

2. Open **`config.toml`** and find the `[extra.community]` section.

3. Choose the group your contribution belongs to:

   | Your contribution | Add it under |
   |---|---|
   | A notebook / application using the tools | `[[extra.community.examples]]` |
   | A replication study or benchmark | `[[extra.community.replications]]` |
   | A dataset published on the HEALPix grid | `[[extra.community.datasets]]` |

4. **Copy this block** to the end of that group and fill it in:

   ```toml
   [[extra.community.examples]]   # or .replications / .datasets
   name = "my-project"
   description = "One or two sentences: what it does and which tools it uses."
   url = "https://my-org.github.io/my-project/"   # the "Open" button
   repo_url = "https://github.com/my-org/my-project"   # optional
   doi_url = "https://doi.org/10.5281/zenodo.0000000"  # optional
   note = "Developed by …"                             # optional
   ```

5. *(Optional)* **Preview locally** — install [Zola](https://www.getzola.org/),
   then from the repo run `zola serve` and open
   `http://127.0.0.1:1111/community/`.

6. **Commit and open a pull request.** That's it — once merged, your card appears
   on the community page automatically.

### Field reference

| Field | Required | What it does |
|---|---|---|
| `name` | ✅ | Card title |
| `description` | ✅ | Short summary shown on the card |
| `url` | ✅ | The **Open** button — link to the docs site (preferred) or the repo |
| `repo_url` | optional | Adds a **GitHub** icon linking to the source |
| `doi_url` | optional | Adds a **DOI** link (e.g. a Zenodo archive) |
| `note` | optional | A small attribution / info line under the description |

## Option B — Open an issue

Not comfortable editing TOML? [Open an issue](https://github.com/GRID4EARTH/grid4earth.github.io/issues/new)
with:

- the **name** and a **one-line description**,
- the **link(s)** (docs site and/or repository),
- a **DOI** if the work is archived (e.g. on Zenodo),
- which **group** it belongs to (example, replication, or dataset).

A maintainer will add it for you.

## What makes a good contribution

- **Self-contained & reproducible** — the notebook or code downloads its own input
  data, and the environment is pinned (`environment.yml`, `pixi.toml`, or a
  `Dockerfile`), so others can clone and run it.
- **Uses the HEALPix tools** ([`healpix-geo`](/tools/) and friends) on the WGS84
  ellipsoid where relevant.
- **Documented** — a docs site or a clear README explaining how to run it.
- **Archived** — a Zenodo DOI (via the GitHub–Zenodo integration) so the work is
  citable.
