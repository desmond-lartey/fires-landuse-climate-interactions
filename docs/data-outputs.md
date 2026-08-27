# Data & Outputs

Everything downstream of Earth Engine is built from a single wide CSV keyed
by park, buffer distance, and year. This page documents the intermediate
assets and the resulting schema.

## Intermediate Earth Engine assets

| Asset ID pattern | Produced by | Contents |
|---|---|---|
| `assets/SummedBurnedArea_Month{1..12}` | Script 01 | 21-year summed monthly burn-frequency image, 500 m |
| `assets/SummedBurnedArea_AllMonths` | Script 01 | All-months summed burn-frequency image |
| `assets/NewParkMerged` | manual GIS step | Merged 15-park boundary FeatureCollection (`ORIG_NAME`) |
| `assets/GLAD_harmonised_30m_2000` | Script 03 | GLAD 2000 remapped to the 9-class scheme, 30 m |
| `assets/BurnedAreaAndFrequencyResultsAsset` | Script 02 | Park × buffer burn-frequency/area table, no land cover/climate |
| `assets/BurnedArea_LC_Climate_ESRI_GLAD_2000_2024` | Script 05 | Park × buffer × year, burn + land cover + 8 climate variables |

## Output CSV schema

One row per `(park, buffer distance, year)` in the land-cover-linked table
— 15 parks × 5 buffers × 9 benchmark years = 675 rows. The seasonal table
has one row per `(park, year, season)` — 15 × 21 × 2 = 630 rows.

| Column | Type | Description |
|---|---|---|
| `ORIG_NAME` | string | Park name |
| `Year` | int | Benchmark year or calendar year |
| `Buffer_km` | float | 0, 5, 10, 15, or 20 |
| `BufferArea_sqkm` | float | Geodesic area of the buffer polygon |
| `{Mon}_BurnFrequency` | int | Summed pixel-years burned for that month, Oct–Mar |
| `{Mon}_BurnedArea_sqkm` | float | Burn frequency converted to km² at 500 m/pixel |
| `TotalPixels` | float | Buffer area ÷ pixel area at the relevant resolution |
| `AvgBurnPerPixel` | float | Summed monthly frequencies ÷ TotalPixels |
| `AvgBurnPerYear` | float | AvgBurnPerPixel ÷ 22 |
| `LandUseDistribution` | dict/JSON | Class → pixel-count histogram, 30 m |
| `ERA5_Tmean_C`, `_Tmin_C`, `_Tmax_C`, `_Tdew_C` | float | Zonal mean temperature variables, °C |
| `ERA5_Precip_mm` | float | Zonal mean total precipitation, mm |
| `ERA5_SurfacePressure_hPa` | float | Zonal mean surface pressure, hPa |
| `ERA5_WindU`, `ERA5_WindV` | float | Zonal mean 10 m wind components, m/s |
| `Season` | string | Dry (Oct–Mar) or Wet (Apr–Sep) — seasonal table only |
| `BurnedArea_km2`, `Rainfall_mm` | float | Seasonal totals — seasonal table only |

!!! note "frequencyHistogram output"
    `LandUseDistribution` is a nested dictionary keyed by class code
    (`"1"`…`"9"`) with pixel counts as values. Divide each value by the
    row's `TotalPixels` for a class fraction, or multiply by 0.0009 km²
    (30 m pixel area) for class area.

## Repository layout

```
fires-landuse-climate-interactions/
├── DATA_DIR/          # raw CSV/SHP exports pulled from Google Drive <- GEE
├── gee-full-script/    # canonical, unabridged Earth Engine scripts
├── pipeline/            # Python: cleaning, joins, regressions, figures
├── notebooks/            # exploratory notebooks, not part of the reproducible path
├── outputs/               # cleaned/joined CSVs consumed by pipeline scripts
├── figures/                # rendered figures referenced in the manuscript
├── docs/                    # this documentation site (mkdocs source)
├── archive/                  # superseded scripts, kept for provenance
└── mkdocs.yml                 # site configuration
```
