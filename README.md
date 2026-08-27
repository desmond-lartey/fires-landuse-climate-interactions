# fires-landuse-climate-interactions

Reproducible methods and Google Earth Engine scripts behind:

> Lartey, D., N'Dri, A., Amoako, E. E., Lawer, E., Issifu, H., Tsendbazar, N.,
> Ametsitsi, G., Janssen, T., Konan, A., & Veenendaal, E.
> *Fire, Land Use and Climate Interactions: Understanding the drivers of fire regimes
> in conservation landscapes of West Africa.* Tropical Conservation Science.
> https://doi.org/10.1177/19400829261486748

A 20-year (2004–2024), 15-park, buffer-based analysis of fire regimes across four
West African ecological zones, integrating MODIS MCD64A1 burned area, harmonized
GLAD/ESRI land cover, and ERA5-Land climate reanalysis.

**Documentation site:** https://desmond-lartey.github.io/fires-landuse-climate-interactions/
(plain static HTML/CSS/JS in `docs/`, generated once by `tools/build_site.py` — no
Jekyll, no mkdocs, no GitHub Actions. GitHub Pages just needs to be pointed at the
`docs/` folder on the default branch and serves the files as-is.)

## Site map

| Page | Contents |
|---|---|
| [Home](docs/index.html) | Overview, headline findings, fire-season calendar, quick links |
| [Study Design](docs/study-design.html) | Objective, study region, research questions, ecological-zone criteria, the 15 protected areas, data sources |
| [Pipeline](docs/pipeline.html) | Environment setup and the exact run order of every script |
| [Script Reference](docs/script-reference.html) | Every Earth Engine script, function by function, with parameter/return documentation |
| [Data & Outputs](docs/data-outputs.html) | Intermediate asset names, output CSV schema, repository layout |
| [Findings](docs/findings.html) | Headline results and zone-by-zone operational guidance |

## What's in this repository

```
fires-landuse-climate-interactions/
├── DATA_DIR/              # raw CSV/SHP exports pulled from Google Drive <- GEE
├── gee-full-script/         # canonical, unabridged Earth Engine scripts
├── pipeline/                 # Python: cleaning, joins, regressions, figures
├── notebooks/                 # exploratory notebooks (not part of the reproducible path)
├── outputs/                   # cleaned/joined CSVs consumed by pipeline scripts
├── figures/                    # rendered figures referenced in the manuscript
├── docs/                        # documentation site (GitHub Pages source)
├── tools/build_site.py           # regenerates docs/ — plain Python, no framework
└── archive/                       # superseded scripts, kept for provenance
```

## Quick start

1. Read [Study Design](docs/study-design.html) for the objective, region, and the
   15 protected areas.
2. Read [Pipeline](docs/pipeline.html) for environment setup and run order, then open
   the scripts directly from `gee-full-script/` and paste them into the
   [Earth Engine Code Editor](https://code.earthengine.google.com/) — updating the
   `projects/ee-desmond/assets/...` paths to your own project.
3. See [Script Reference](docs/script-reference.html) for parameter-level
   documentation of every custom function used across the scripts.
4. See [Data & Outputs](docs/data-outputs.html) for the exact CSV schema produced
   at the end of the pipeline.

### Editing the documentation site

The site in `docs/` is generated, not hand-edited. To change content, edit the
page-content functions in `tools/build_site.py` and re-run:

```bash
python tools/build_site.py
```

This rewrites every file in `docs/` deterministically — commit the regenerated
output along with your source change.

## Data sources

| Layer | Source | Resolution |
|---|---|---|
| Burned area | MODIS MCD64A1 Collection 6.1 (Giglio et al., 2018) | 500 m |
| Land cover | GLAD GLCLU2020 v2 (2000–2020) + ESRI Global LULC 10 m (2017–2024) | 30 m / 10 m |
| Climate | ERA5-Land Monthly Aggregates (ECMWF/C3S, 2018) | ~11 km native / ~25 km nominal |
| Park boundaries | WDPA-derived, merged authors' shapefile | vector |

## Citation

```
Lartey, D., N'Dri, A., Amoako, E. E., Lawer, E., Issifu, H., Tsendbazar, N.,
Ametsitsi, G., Janssen, T., Konan, A., & Veenendaal, E. Fire, Land Use and
Climate Interactions: Understanding the drivers of fire regimes in
conservation landscapes of West Africa. Tropical Conservation Science.
https://doi.org/10.1177/19400829261486748
```

## License

MIT — see `LICENSE`.
