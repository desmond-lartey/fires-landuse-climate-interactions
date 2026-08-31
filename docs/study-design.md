# Study Design

## Objective

Assess fine-scale interactions of climatic, ecological, and landscape
controls on burning across West African protected areas, controls that
remain poorly understood despite advances in remote sensing and climate
modelling at larger scales, using a unified spatial and ecological
framework that allows direct comparison across parks, rather than the
single-site studies that have dominated the literature to date.

## Study region and period

| Item | Detail |
|---|---|
| Study period | 2004–2024 (20-year MODIS burned-area climatology, 22-year normalisation window) |
| Spatial domain | Upper Guinea, approximately 5°N–10°N, 10°W–5°E |
| Countries | Côte d'Ivoire, Ghana, Togo, Burkina Faso, Benin, Nigeria |
| Rainfall gradient | Peaks near 4,000 mm/yr, declining to ~1,200 mm/yr at the forest–savanna boundary and further in the driest segments |
| Spatial framework | Five concentric analysis units per park: interior (0 km) and buffers at 5, 10, 15, 20 km |

## Research questions

1. Why do protected areas differ in frequency of burning?
2. How is overall annual burning related to rainfall and temperature
   variability, particularly during dry years?
3. What is the relationship between fire activity, location, climate, and
   land cover types?
4. Do different land cover types burn at different frequencies, extents, and
   seasonal timings?
5. How does the timing of fires vary between inside and outside of protected
   areas?

## Ecological zones

Zones are a region-specific classification, not a global biome scheme,
combining three criteria:

- **Mean annual rainfall**, following Tano et al. (2023)
- **Dry-season length**, following Eva & Lambin (2000) and Ouattara et al. (2024)
- **Vegetation structure**, following Ametsitsi et al. (2020), Janssen et al. (2018), Liu et al. (2016)

| Zone | Character | Expected fire regime |
|---|---|---|
| **Northern Savanna** | Open canopy, continuous grass cover, long dry season | Frequent, extensive, low-intensity fire |
| **Northern Forest** | More humid woodland–forest mosaic | Less frequent, more spatially patchy |
| **Southern Transition** | Forest–savanna mosaic, moderate rainfall | Intermediate, interannually variable |
| **Southern Forest** | Closed canopy, high rainfall | Rare fire, but locally severe under drought |

!!! note "Zone assignment is a hypothesis, not an assumption"
    These zone–fire associations are treated as testable expectations
    against the 15 study parks, not foregone conclusions, see
    [Findings → zone-by-zone guidance](findings.md#zone-by-zone-guidance)
    for how each zone actually behaved.

## Protected areas evaluated

| # | Protected area | Country | Rainfall (mm/yr) | Dry season | Zone |
|---|---|---|---|---|---|
| 7 | W (Benin) | Benin | ~700 | 6–7 mo | Northern Savanna |
| 6 | Forêt Classée de Tiogo | Burkina Faso | ~1,200 | 5–6 mo | Northern Savanna |
| 1 | Bontioli (Partial Reserve) | Burkina Faso | ~1,200 | 5–6 mo | Northern Savanna |
| 9 | Bontioli (Total Reserve) | Burkina Faso | ~1,200 | 5–6 mo | Northern Forest |
| 3 | Kaboré Tambi | Burkina Faso | 600–700 | 6–7 mo | Northern Savanna |
| 8 | W (Burkina Faso) | Burkina Faso | ~700 | 6–7 mo | Northern Savanna |
| 2 | Comoé | Côte d'Ivoire | 900–1,100 | 5–6 mo | Northern Savanna |
| 13 | Marahoué | Côte d'Ivoire | ~1,100 | 5–6 mo | Southern Transition |
| 15 | Bia | Ghana | 1,500–1,800 | 4–5 mo | Southern Forest |
| 11 | Kogyae | Ghana | 1,200–1,300 | 5–6 mo | Southern Transition |
| 12 | Kyabobo | Ghana | 922–1,874 | 5–6 mo | Southern Transition |
| 5 | Mole | Ghana | ~1,100 | 5–6 mo | Northern Savanna |
| 10 | Gashaka-Gumti | Nigeria | 1,350–1,720 | 4–5 mo | Southern Transition |
| 4 | Kainji Lake | Nigeria | 1,100–1,200 | 5–6 mo | Northern Savanna |
| 14 | Old Oyo | Nigeria | 900–1,500 | 5–6 mo | Southern Transition |

Numbers match Figure 1 of the manuscript. IUCN category, designation year,
area, and human-occupancy detail are in the manuscript; boundary attributes
are exported from the authors' merged WDPA-derived shapefile.

## Data sources

| Layer | Source | Resolution | Coverage |
|---|---|---|---|
| Burned area | MODIS MCD64A1 Collection 6.1 (Giglio et al., 2018) | 500 m | 2004–2024 |
| Land cover | GLAD GLCLU2020 v2 (Potapov et al., 2022) + ESRI Global LULC 10 m (Karra et al., 2021) | 30 m / 10 m | 2000–2020 / 2017–2024 |
| Climate | ERA5-Land Monthly Aggregates (ECMWF/C3S, 2018) | ~11–25 km | 2004–2024 |
| Park boundaries | WDPA-derived, merged authors' shapefile | vector | static |

!!! note "Reconciling resolutions"
    Burned area (500 m), land cover (30 m), and climate (~11–25 km) are never
    resampled onto a common pixel grid. Each layer is reduced independently
    to zonal statistics *within* the same park/buffer geometry, and the
    resulting scalars are joined by `(park, buffer, year)`. See
    [Data & Outputs](data-outputs.md#output-csv-schema) for the joined
    schema.
