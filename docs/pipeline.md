# Pipeline

The analysis runs in a fixed order. The first steps require Google Earth
Engine access, they submit extraction/export tasks and download the
results from Google Drive. The remaining steps run entirely locally.

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

earthengine authenticate
```

Python 3.10+ recommended for the local pipeline steps. A Google Earth
Engine account with a cloud project is required for every step run in the
Code Editor.

!!! tip "Adapting this to a different region"
    Every asset path in the scripts is namespaced under
    `projects/ee-desmond/assets/...`. To run this on a different park set or
    region, replace that prefix with your own Earth Engine cloud project,
    upload your own boundary shapefile as an EE `FeatureCollection`, and
    update the `NewParkMerged` reference used throughout.

## Run order

All scripts live in the `gee-full-script/` folder and are pasted directly
into the [Earth Engine Code Editor](https://code.earthengine.google.com/).

### Earth Engine steps (submit tasks, download from Drive)

```
Step 1   gee-full-script/01_burned_area_composites.js
         Sum MCD64A1 monthly burn detections into a 20-year (2004-2024)
         climatology, one composite per calendar month.
         → SummedBurnedArea_Month{1..12}, SummedBurnedArea_AllMonths

Step 2   gee-full-script/02_buffer_disaggregation.js
         Build five buffers per park (0, 5, 10, 15, 20 km) and compute
         monthly burn frequency + burned area for each.
         → BurnedAreaAndFrequencyResults.csv

Step 3   gee-full-script/03_landcover_harmonisation_full.js
         Harmonise GLAD (2000-2020) and ESRI (2021-2024) land cover into
         one 9-class scheme; resolve the correct source per year.

Step 4/5 gee-full-script/05_combined_pipeline_full.js
         For every park × buffer × benchmark year: burn stats, land-cover
         histogram, and 8 ERA5-Land climate variables in one export.
         → BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2.csv

Step 6   gee-full-script/05b_seasonal_fire_rainfall_full.js
         Dry- vs wet-season burned area and rainfall totals per park/year,
         used for the fire-rainfall regressions.
         → BurnedArea_ERA5Seasonal_2004_2024.csv
```

!!! warning "Export quotas"
    Earth Engine limits concurrent per-user tasks. Queue the 12 monthly
    exports in Step 1 in smaller batches if you hit a limit, and expect the
    combined pipeline (Steps 4/5) to be the slowest single export, it
    re-runs the climate zonal mean for every park × buffer × year.

### Local steps (no Earth Engine required)

```bash
# 1. Clean + join the raw exports (parses the LandUseDistribution
#    JSON column, joins benchmark-year land cover onto the per-buffer
#    burn table, derives dry/wet season totals)
python pipeline/01_clean_join.py --in DATA_DIR --out outputs/

# 2. Fit the fire-rainfall OLS regressions (within-year, multi-year, pooled)
python pipeline/02_fit_regressions.py --in outputs/BurnedArea_LC_Climate_joined.csv

# 3. Render the figures referenced on the Findings page
python pipeline/03_make_figures.py --in outputs/ --out figures/
```

## Pulling exports into the repository

All `Export.table.toDrive` calls write to a `GEE` folder in Google Drive.
Download the resulting CSVs into `DATA_DIR/`, keeping the export
`description` as the filename so the local scripts can find them without
edits:

```
DATA_DIR/
├── BurnedAreaAndFrequencyResults.csv
├── BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2.csv
└── BurnedArea_ERA5Seasonal_2004_2024.csv
```

## Key data products

| File | Contents |
|---|---|
| `BurnedAreaAndFrequencyResults.csv` | Park × buffer burn frequency/area, no land cover or climate |
| `BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2.csv` | Park × buffer × benchmark-year, burn + land-cover histogram + 8 climate variables |
| `BurnedArea_ERA5Seasonal_2004_2024.csv` | Park × year × season (dry/wet), burned area and rainfall totals |

Full column-by-column schema is on the [Data & Outputs](data-outputs.md)
page.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `User memory limit exceeded` in `reduceRegion` | Buffer geometry too large at 500 m/30 m scale for the default reducer memory | Raise `maxPixels` (already `1e13` in the provided scripts) and/or reduce at a coarser scale temporarily to debug |
| Land-cover histogram keys don't match expected 1–9 | A GLAD or ESRI code wasn't included in the remap dictionary | Check the unabridged `gladToEsri` dictionary in `gee-full-script/03_landcover_harmonisation_full.js`; add any missing native codes |
| Seasonal script times out client-side | The nested loop calls `.getInfo()` for list lengths on every iteration | Cache list sizes once before the loop, or refactor to server-side `.map()` |
| Precipitation values look 1000× too small | ERA5-Land precipitation is natively in metres, not millimetres | Confirm the `.multiply(1000)` conversion is present before export |
