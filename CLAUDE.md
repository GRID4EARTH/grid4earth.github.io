# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The GRID4EARTH project website — a **MyST Markdown** static site deployed to GitHub Pages.
GRID4EARTH is an ESA Digital Twin Earth (DTE) project building a unified Earth Observation
data infrastructure on **Discrete Global Grid Systems (DGGS)**, specifically the **HEALPix**
equal-area grid combined with **Zarr V3** cloud-optimized storage. It targets interoperability
across Copernicus Sentinel and Destination Earth (DestinE) datasets.

This is a documentation/landing site, not application code. Content lives in Markdown and
Jupyter notebooks; there is no test suite.

## Commands

```bash
# Create the conda env (named eopf-dggs) — also used by CI
micromamba env create -f environment.yml   # or: conda env create -f environment.yml

# Local preview with live reload
myst start

# Build the site (executes notebooks, emits ./_build/html)
myst build --html --execute

# Lint / format everything (must pass before commit; CI enforces it)
pre-commit run --all-files

# Install the git hooks so formatting runs automatically on commit
pip install pre-commit && pre-commit install --install-hooks
```

To run a single notebook non-interactively: `jupyter execute --inplace notebooks/<name>.ipynb`.

## Architecture

- **`myst.yml`** — the source of truth for site structure. The `project.toc` defines navigation
  (index.md → notebooks/index.md → the three notebooks). Site theme is `book-theme`. Adding a
  page means adding it to the TOC here.
- **`index.md`** — the landing page. Uses MyST `+++` block syntax with custom CSS classes
  (`hero-block`, `content-block`, `tool-badge`) that are styled/transformed by the plugin.
- **`landing-page.mjs`** — a MyST plugin (registered under `project.plugins` in myst.yml) that
  defines custom directives (`hero`, `block-title`), color roles, and a `block-transform` that
  rewrites blocks/badges at document stage. Edit this to change landing-page layout behavior.
- **`notebooks/`** — Jupyter notebooks (HEALPix numbering, Plotly demos, logo generation),
  executed at build time so their outputs render in the site.
- **`static/`** — logos and consortium-member badge images referenced by index.md.
- **`_config.yml`** — legacy Jekyll config (`jekyll-theme-cayman`); the live site is MyST, not
  Jekyll. Treat MyST as authoritative.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml` (MyST GitHub Pages Deploy):
it sets up the `eopf-dggs` micromamba env, runs `myst build --html --execute`, and publishes
`./_build/html`. The workflow sets `BASE_URL: /${{ github.event.repository.name }}` — required
for CSS/JS asset paths on GitHub Pages. Do **not** set `base_url` in `myst.yml` (MyST ignores it).

## Linting

Two CI workflows gate PRs: `pre-commit.yaml` (the full `.pre-commit-config.yaml` suite — ruff,
prettier, black, black-jupyter, nbqa) and `black.yml` (a standalone black check). Run
`pre-commit run --all-files` and commit the result before pushing; most failures are
auto-formatting fixes.

## Gotchas

- **Repo / naming mismatch:** the conda env and `myst.yml` `github:` field reference
  `eopf-dggs` / `EOPF-DGGS`, but the repo and project are GRID4EARTH (`grid4earth.github.io`).
  This is intentional carryover — keep the env named `eopf-dggs` so it matches CI.
- Notebooks must stay listed in `myst.yml` TOC as `.ipynb` to be built.
- `todo.txt` tracks planned content (linking the -geo / -resample / -plot / -analyse tool docs,
  a 5th tool, and the GRID4EARTH_talk.pdf) — not yet implemented.
