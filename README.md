# fires-landuse-climate-interactions

Reproducible methods and Google Earth Engine scripts behind:

> Lartey, D., N'Dri, A. B., Amoako, E. E., Lawer, E. A., Issifu, H., Tsendbazar, N.,
> Ametsitsi, G., Janssen, T., Sylvie, K. A., & Veenendaal, E. (in production).
> *Fire, Land Use and Climate Interactions: Understanding the drivers of fire regimes
> in conservation landscapes of West Africa.* Manuscript ID TRC-26-0053.

A 20-year (2004–2024), 15-park, buffer-based analysis of fire regimes across four
West African ecological zones, integrating MODIS MCD64A1 burned area, harmonized
GLAD/ESRI land cover, and ERA5-Land climate reanalysis.

**Documentation site:** https://desmond-lartey.github.io/fires-landuse-climate-interactions/
(built from the plain static HTML/CSS/JS in `docs/` — no Jekyll, no build step, no
GitHub Actions required. GitHub Pages just needs to be pointed at the `docs/` folder
on the default branch.)

## What's in this repository

```
fires-landuse-climate-interactions/
├── DATA_DIR/              # raw CSV/SHP exports pulled from Google Drive <- GEE
├── gee-full-script/         # canonical, unabridged Earth Engine scripts
├── pipeline/                 # Python: cleaning, joins, regressions, figures
├── notebooks/                 # exploratory notebooks (not part of the reproducible path)
├── outputs/                   # cleaned/joined CSVs consumed by pipeline scripts
├── figures/                   # rendered figures referenced in the manuscript
├── docs/                      # this documentation site (GitHub Pages source)
├── archive/                    # superseded scripts, kept for provenance
└── ecological_zones_5class/   # earlier 5-class zoning attempt, retained for reference
```

## Quick start

1. Read the [Methodology](docs/methodology.html) page for the five-step workflow.
2. Read the [GEE scripts](docs/gee-scripts.html) page, or open the scripts directly
   from `gee-full-script/`, and paste them into the
   [Earth Engine Code Editor](https://code.earthengine.google.com/) — updating the
   `projects/ee-desmond/assets/...` paths to your own project.
3. Follow [Reproduce](docs/reproduce.html) for the exact run order, export
   destinations, and the Python steps that turn raw exports into the figures and
   regression tables reported in the manuscript.
4. See the [API reference](docs/api-reference.html) for parameter-level
   documentation of every custom function used across the scripts.

## Data sources

| Layer | Source | Resolution |
|---|---|---|
| Burned area | MODIS MCD64A1 Collection 6.1 (Giglio et al., 2018) | 500 m |
| Land cover | GLAD GLCLU2020 v2 (2000–2020) + ESRI Global LULC 10 m (2017–2024) | 30 m / 10 m |
| Climate | ERA5-Land Monthly Aggregates (ECMWF/C3S, 2018) | ~11 km native / ~25 km nominal |
| Park boundaries | WDPA-derived, merged authors' shapefile | vector |

## Status

This manuscript is in production. Figure numbers, exact statistics, and wording in
this repository's documentation follow the submitted draft and may be revised before
final publication.

## License

MIT — see `LICENSE`.
