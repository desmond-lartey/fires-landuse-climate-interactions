# Script Reference

This page documents the functions in each Earth Engine script. These
scripts live in **`gee-full-script/`** and run in order (see
[Pipeline](pipeline.md)). They are a **run-in-order study pipeline**, pasted
directly into the [Earth Engine Code Editor](https://code.earthengine.google.com/),
not an installable package, so this is a reference for reading and
adapting the code.

!!! note "Full unabridged source"
    The excerpts below are trimmed for readability. Complete, unabridged
    scripts, including the full ~200-entry `gladToEsri` dictionary, are in
    `gee-full-script/` in the repository.

## 01_burned_area_composites.js

Builds the 20-year (2004–2024) monthly burn-frequency climatology from
MODIS MCD64A1, one image per calendar month.

- **`processBurnedArea(date, region)`**, filters MCD64A1 to a one-month
  window, mosaics over `region`, returns a binary "burned this month" mask.
- **`sumBurnedAreaForSpecificMonth(month, startYear, endYear, region)`**,
  sums that mask across a year range into a per-pixel year-count
  climatology.
- **`sumBurnedAreaForAllMonths(startYear, endYear, region)`**, sums all 12
  months into one all-months composite.

```javascript
function processBurnedArea(date, region) {
  var filtered = modisCollection.filterDate(date, ee.Date(date).advance(1, 'month'));
  var mosaicked = filtered.mosaic().clip(region);
  var burned = mosaicked.select('BurnDate').gt(0).selfMask();
  return burned.set('date', date);
}

function sumBurnedAreaForSpecificMonth(month, startYear, endYear, region) {
  var dateList = ee.List.sequence(startYear, endYear).map(function(year) {
    return ee.Date.fromYMD(year, month, 1);
  });
  var monthlyBurned = ee.ImageCollection.fromImages(
    dateList.map(function(date) { return processBurnedArea(date, region); })
  );
  return monthlyBurned.sum().set('month', month).toDouble();
}

function sumBurnedAreaForAllMonths(startYear, endYear, region) {
  var monthList = ee.List.sequence(1, 12);
  var allBurned = ee.ImageCollection.fromImages(
    monthList.map(function(month) {
      return sumBurnedAreaForSpecificMonth(month, startYear, endYear, region);
    })
  );
  return allBurned.sum().toDouble();
}

for (var month = 1; month <= 12; month++) {
  (function(month) {
    var summedBurned = sumBurnedAreaForSpecificMonth(month, 2004, 2024, area);
    Export.image.toDrive({
      image: summedBurned, description: 'SummedBurnedArea_Month' + month,
      scale: 500, region: area, fileFormat: 'GeoTIFF'
    });
  })(month);
}

var summedBurnedForAllMonths = sumBurnedAreaForAllMonths(2004, 2024, area);
Export.image.toDrive({
  image: summedBurnedForAllMonths, description: 'SummedBurnedArea_AllMonths',
  scale: 500, region: area, fileFormat: 'GeoTIFF'
});
```

## 02_buffer_disaggregation.js

Generates five concentric buffers per park (0, 5, 10, 15, 20 km) and
computes burn frequency, burned area, and normalised exposure rates for
each.

- **`calculateBurnedAreaAndFrequency(feature)`**, builds the five buffer
  geometries around one park and reduces each of the six dry-season monthly
  composites within them.

```javascript
var bufferDistances = ee.List.sequence(0, 20, 5).map(function(distance) {
  return ee.Number(distance).multiply(1000);
});

function calculateBurnedAreaAndFrequency(feature) {
  var results = bufferDistances.map(function(bufferDistance) {
    var bufferedGeometry = ee.Algorithms.If(
      ee.Number(bufferDistance).eq(0),
      feature.geometry(),
      feature.geometry().buffer(bufferDistance)
    );
    bufferedGeometry = ee.Geometry(bufferedGeometry);

    var burnFrequencyDict = ee.Dictionary({});
    var burnedAreaDict = ee.Dictionary({});

    months.forEach(function(month, index) {
      var burnedImage = ee.Image(burnedAreaImages[index]);
      var burnFrequency = burnedImage.reduceRegion({
        reducer: ee.Reducer.sum(), geometry: bufferedGeometry,
        scale: 500, maxPixels: 1e13
      }).get('BurnDate');
      var burnedAreaSqKm = ee.Number(burnFrequency).multiply(500 * 500).divide(1e6);
      burnFrequencyDict = burnFrequencyDict.set(month, burnFrequency);
      burnedAreaDict = burnedAreaDict.set(month, burnedAreaSqKm);
    });

    var bufferAreaSqKm = ee.Number(bufferedGeometry.area()).divide(1e6);
    var totalPixels = bufferAreaSqKm.divide(0.25); // 500 m pixel = 0.25 sqkm
    var avgBurnPerPixel = ee.Number(
      burnFrequencyDict.values().reduce(ee.Reducer.sum())
    ).divide(totalPixels);
    var avgBurnPerYear = avgBurnPerPixel.divide(22);

    return ee.Feature(bufferedGeometry, {
      'ORIG_NAME': feature.get('ORIG_NAME'),
      'Bufferdist': ee.Number(bufferDistance).divide(1000),
      'TotalPixels': totalPixels,
      'AvgBurnPerPixel': avgBurnPerPixel,
      'AvgBurnPerYear': avgBurnPerYear,
      'BufferArea_sqkm': bufferAreaSqKm
      // ...plus one {Month}_BurnFrequency / {Month}_BurnedArea_sqkm pair per month
    });
  });
  return ee.FeatureCollection(results);
}

var allResults = ee.FeatureCollection(parks.map(calculateBurnedAreaAndFrequency).flatten());
Export.table.toDrive({
  collection: allResults, description: 'BurnedAreaAndFrequencyResults',
  fileFormat: 'CSV', folder: 'GEE'
});
```

## 03_landcover_harmonisation_full.js

Remaps GLAD's native codes and ESRI's 11-class scheme onto one shared
9-class scheme, and resolves the correct dataset for any requested year.

- **`harmoniseGlad(img)`**, remaps GLAD codes via the `gladToEsri`
  dictionary.
- **`remapEsri(image)`**, remaps ESRI's 11 native codes onto the same
  9-class target.
- **`getLandCoverYear(year)`**, dispatches to GLAD (2000–2020) or ESRI
  (2021–2024) automatically.

```javascript
var gladToEsri = ee.Dictionary({
  // Water
  200:1, 201:1, 202:1, 203:1, 204:1, 207:1, 208:1, 209:1, 210:1, 211:1,
  // Trees: stable, disturbed, gains, and height-gain sub-codes all map to class 2
  25:2, 26:2, /* ... 27 through 195 follow the same pattern ... */ 196:2,
  // Flooded vegetation
  100:3, 101:3, /* ... */ 124:3,
  // Rangeland / short vegetation
  0:9, 1:9, /* ... */ 24:9,
  // Crops
  244:4, 245:4, 246:4, 247:4, 248:4, 249:4,
  // Built-up
  250:5, 251:5, 252:5, 253:5,
  // Snow/Ice
  241:7, 242:7, 243:7
  // Clouds (8) has no GLAD equivalent -- absent by design
});

function harmoniseGlad(img) {
  return img.remap(
    gladToEsri.keys().map(ee.Number.parse),
    gladToEsri.values().map(ee.Number.parse)
  ).rename('landcover');
}

function remapEsri(image) {
  return image.remap([1,2,4,5,7,8,9,10,11], [1,2,3,4,5,6,7,8,9]).rename('landcover');
}

function getLandCoverYear(year) {
  if (year >= 2021) {
    var esriImage = esri_lulc10.filterDate(year+'-01-01', year+'-12-31').mosaic().select(0);
    return remapEsri(esriImage);
  }
  if (year >= 2000 && year <= 2020) {
    return harmoniseGlad(ee.Image('projects/glad/GLCLU2020/v2/LCLUC_' + year).select(0));
  }
  return ee.Image(0).rename('landcover');
}
```

## 04_climate_integration.js

Builds an 8-band annual-mean ERA5-Land climate image with unit conversions
already applied.

- **`getClimateForYear(year)`**, K→°C, m→mm, Pa→hPa conversions, one image
  per year.

```javascript
function getClimateForYear(year) {
  var start = ee.Date.fromYMD(year, 1, 1);
  var end   = ee.Date.fromYMD(year, 12, 31);

  var era5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
      .filterDate(start, end)
      .select(['temperature_2m','temperature_2m_min','temperature_2m_max',
                'dewpoint_temperature_2m','total_precipitation_sum',
                'surface_pressure','u_component_of_wind_10m','v_component_of_wind_10m'])
      .mean();

  var Tmean_C = era5.select('temperature_2m').subtract(273.15).rename('Tmean_C');
  var Tmin_C  = era5.select('temperature_2m_min').subtract(273.15).rename('Tmin_C');
  var Tmax_C  = era5.select('temperature_2m_max').subtract(273.15).rename('Tmax_C');
  var Tdew_C  = era5.select('dewpoint_temperature_2m').subtract(273.15).rename('Tdew_C');
  var Precip_mm = era5.select('total_precipitation_sum').multiply(1000).rename('Precip_mm');
  var SurfaceP_hPa = era5.select('surface_pressure').divide(100).rename('SurfaceP_hPa');
  var WindU = era5.select('u_component_of_wind_10m').rename('WindU');
  var WindV = era5.select('v_component_of_wind_10m').rename('WindV');

  return ee.Image.cat([Tmean_C, Tmin_C, Tmax_C, Tdew_C, Precip_mm, SurfaceP_hPa, WindU, WindV]);
}
```

## 05_combined_pipeline_full.js

The production script: for every park × buffer × benchmark year, emits burn
frequency, burned area, the land-cover histogram, and all eight climate
variables in a single feature.

- **`calculateBurnedAreaAndLandUse(feature, landCover, year)`**, the main
  per-park-per-year driver, merging burn stats, land cover, and climate into
  one output row per buffer.

```javascript
function calculateBurnedAreaAndLandUse(feature, landCover, year) {
  var results = bufferDistances.map(function(bufferDistance) {
    var geom = ee.Algorithms.If(
      ee.Number(bufferDistance).eq(0), feature.geometry(), feature.geometry().buffer(bufferDistance)
    );
    geom = ee.Geometry(geom);

    var climate = getClimateForYear(year).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: geom, scale: 11132, maxPixels: 1e13
    });

    var burnFrequencyDict = ee.Dictionary({});
    var burnedAreaDict = ee.Dictionary({});
    months.forEach(function(month, index) {
      var burnFreq = burnedAreaImages[index].reduceRegion({
        reducer: ee.Reducer.sum(), geometry: geom, scale: 500, maxPixels: 1e13
      }).get('BurnDate');
      var areaSqKm = ee.Number(burnFreq).multiply(500 * 500).divide(1e6);
      burnFrequencyDict = burnFrequencyDict.set(month + '_BurnFrequency', burnFreq);
      burnedAreaDict = burnedAreaDict.set(month + '_BurnedArea_sqkm', areaSqKm);
    });

    var landCoverStats = landCover.reduceRegion({
      reducer: ee.Reducer.frequencyHistogram(), geometry: geom, scale: 30, maxPixels: 1e13
    }).get('landcover');

    var bufferAreaSqKm = ee.Number(geom.area()).divide(1e6);
    var totalBurns = ee.Number(burnFrequencyDict.values().reduce(ee.Reducer.sum()));
    var totalPixels = bufferAreaSqKm.divide(0.0009); // 30 m LC pixels
    var avgBurnPerPixel = totalBurns.divide(totalPixels);
    var avgBurnPerYear = avgBurnPerPixel.divide(22);

    var props = ee.Dictionary({
      'ORIG_NAME': feature.get('ORIG_NAME'), 'Year': year,
      'Buffer_km': ee.Number(bufferDistance).divide(1000),
      'BufferArea_sqkm': bufferAreaSqKm, 'TotalPixels': totalPixels,
      'AvgBurnPerPixel': avgBurnPerPixel, 'AvgBurnPerYear': avgBurnPerYear,
      'LandUseDistribution': landCoverStats,
      'ERA5_Tmean_C': climate.get('Tmean_C'), 'ERA5_Tmin_C': climate.get('Tmin_C'),
      'ERA5_Tmax_C': climate.get('Tmax_C'), 'ERA5_Tdew_C': climate.get('Tdew_C'),
      'ERA5_Precip_mm': climate.get('Precip_mm'),
      'ERA5_SurfacePressure_hPa': climate.get('SurfaceP_hPa'),
      'ERA5_WindU': climate.get('WindU'), 'ERA5_WindV': climate.get('WindV')
    }).combine(burnFrequencyDict).combine(burnedAreaDict);

    return ee.Feature(geom, props);
  });
  return ee.FeatureCollection(results);
}

var allResults = ee.FeatureCollection([]);
[2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023, 2024].forEach(function(y) {
  var lcImg = getLandCoverYear(y);
  var yearFC = ee.FeatureCollection(
    parks.map(function(f) { return calculateBurnedAreaAndLandUse(f, lcImg, y); }).flatten()
  );
  allResults = allResults.merge(yearFC);
});

Export.table.toDrive({
  collection: allResults,
  description: 'BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2',
  fileFormat: 'CSV', folder: 'GEE'
});
```

## 05b_seasonal_fire_rainfall_full.js

Computes dry- vs wet-season burned-area and rainfall totals per park/year,
the input to the fire–rainfall regressions.

- **`processParkYearSeason(park, year, season)`**, one seasonal
  burned-area/rainfall total for one park in one year.

```javascript
var seasons = [
  {label: 'Dry', startMonth: 10, endMonth: 3},  // Oct -> Mar (crosses year boundary)
  {label: 'Wet', startMonth: 4,  endMonth: 9}   // Apr -> Sep
];

var processParkYearSeason = function(park, year, season) {
  var geom = park.geometry();
  var start = ee.Date.fromYMD(year, season.startMonth, 1);
  var end = ee.Algorithms.If(
    ee.Number(season.startMonth).gt(season.endMonth),
    ee.Date.fromYMD(ee.Number(year).add(1), season.endMonth, 28),
    ee.Date.fromYMD(year, season.endMonth, 28)
  );
  end = ee.Date(end);

  var BA_season = MODIS_BA.filterDate(start, end).map(function(img) {
    return ee.Image.pixelArea().updateMask(img.select('BurnDate').gt(0)).divide(1e6);
  }).sum();
  var baDict = BA_season.reduceRegion({
    reducer: ee.Reducer.sum(), geometry: geom, scale: 500, maxPixels: 1e13
  });
  var burnedArea_km2 = ee.Number(ee.Algorithms.If(baDict.contains('area'), baDict.get('area'), 0));

  var rainImg = ERA5.filterDate(start, end).sum().multiply(1000).rename('rainfall_mm');
  var rainDict = rainImg.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: geom, scale: 27830, maxPixels: 1e13
  });
  var rainfall_mm = ee.Number(ee.Algorithms.If(rainDict.contains('rainfall_mm'), rainDict.get('rainfall_mm'), 0));

  return ee.Feature(null, {
    'Park': park.get('ORIG_NAME'), 'Year': year, 'Season': season.label,
    'BurnedArea_km2': burnedArea_km2, 'Rainfall_mm': rainfall_mm
  });
};

Export.table.toDrive({
  collection: outputFC, description: 'BurnedArea_ERA5Seasonal_2004_2024',
  folder: 'GEE', fileFormat: 'CSV',
  selectors: ['Park', 'Year', 'Season', 'BurnedArea_km2', 'Rainfall_mm']
});
```

!!! warning "Performance note"
    The triple loop over parks × years × seasons calls `.getInfo()` to get
    client-side list lengths. Fine for 15 parks × 21 years × 2 seasons (630
    features), but restructure as server-side `.map()` nesting for much
    larger park lists.

## Full function reference

Parameter and return-type documentation for every custom function above.

### `processBurnedArea(date, region)` → `ee.Image`

| Parameter | Type | Description |
|---|---|---|
| `date` | `ee.Date` | First day of the target month |
| `region` | `ee.Geometry` | Clipping extent (study area) |

Returns a single-band binary mask (`BurnDate > 0`, self-masked), tagged with
a `date` property.

### `sumBurnedAreaForSpecificMonth(month, startYear, endYear, region)` → `ee.Image`

| Parameter | Type | Description |
|---|---|---|
| `month` | int (1–12) | Calendar month |
| `startYear`, `endYear` | int | Climatology bounds (2004, 2024) |
| `region` | `ee.Geometry` | Study area extent |

Returns the pixel-wise count of years (0–21) that recorded a burn in that
month, cast to `double`.

### `sumBurnedAreaForAllMonths(startYear, endYear, region)` → `ee.Image`

Calls `sumBurnedAreaForSpecificMonth` for all 12 months and sums the
results into one all-months composite.

### `calculateBurnedAreaAndFrequency(feature)` → `ee.FeatureCollection`

| Parameter | Type | Description |
|---|---|---|
| `feature` | `ee.Feature` | One park polygon with an `ORIG_NAME` property |

Returns 5 features (one per buffer distance), each with the fields listed
in the [output schema](data-outputs.md#output-csv-schema). Closes over
module-level `months`, `burnedAreaImages`, `bufferDistances`.

### `harmoniseGlad(img)` → `ee.Image`

`img`: single-band GLAD image, native codes. Returns a single band named
`landcover`, values 1–9 (class 8/Clouds never appears from this source).

### `remapEsri(image)` → `ee.Image`

`image`: single-band ESRI image, native codes `1,2,4,5,7,8,9,10,11`.
Returns a single band named `landcover`, values 1–9.

### `getLandCoverYear(year)` → `ee.Image`

| Year range | Source | Function called |
|---|---|---|
| 2000–2020 | GLAD GLCLU2020 v2 | `harmoniseGlad()` |
| 2021–2024 | ESRI Global LULC 10 m | `remapEsri()` after annual mosaic |
| other |, | `ee.Image(0)` fallback |

### `getClimateForYear(year)` → `ee.Image`

`year`: calendar year, filtered Jan 1–Dec 31. Returns 8 bands: `Tmean_C`,
`Tmin_C`, `Tmax_C`, `Tdew_C`, `Precip_mm`, `SurfaceP_hPa`, `WindU`,
`WindV`.

### `calculateBurnedAreaAndLandUse(feature, landCover, year)` → `ee.FeatureCollection`

| Parameter | Type | Description |
|---|---|---|
| `feature` | `ee.Feature` | One park polygon |
| `landCover` | `ee.Image` | Output of `getLandCoverYear(year)` for the matching year |
| `year` | int | Benchmark year, forwarded to `getClimateForYear` |

Returns 5 features (one per buffer), each with the full schema documented
on [Data & Outputs](data-outputs.md#output-csv-schema).

### `processParkYearSeason(park, year, season)` → `ee.Feature`

| Parameter | Type | Description |
|---|---|---|
| `park` | `ee.Feature` | One park polygon with `ORIG_NAME` |
| `year` | `ee.Number` | Calendar year of the season's start |
| `season` | `{label, startMonth, endMonth}` | Dry (10→3) or Wet (4→9); `startMonth > endMonth` means the season crosses the year boundary |

Returns a geometry-less feature with `Park`, `Year`, `Season`,
`BurnedArea_km2`, `Rainfall_mm`.

### Constants referenced throughout

| Name | Value | Used by |
|---|---|---|
| `months` | `['Oct','Nov','Dec','Jan','Feb','Mar']` | Scripts 02, 05 |
| `bufferDistances` | `[0, 5000, 10000, 15000, 20000]` m | Scripts 02, 05 |
| Burned-area reduce scale | 500 m | All burn-frequency `reduceRegion` calls |
| Land-cover reduce scale | 30 m | All `frequencyHistogram` calls |
| Climate reduce scale | 11,132 m | All ERA5-Land `reduceRegion` calls (native grid) |
| Climatology length | 22 years | `AvgBurnPerYear` normalisation |
