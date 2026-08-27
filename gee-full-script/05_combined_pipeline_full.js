// NOTE: this script assumes 03_landcover_harmonisation_full.js has already been
// pasted above it in the same Code Editor session (it reuses harmoniseGlad,
// remapEsri, getLandCoverYear, lcDict, and esri_lulc10 from that script).

// -----------------------------
// PARKS
// -----------------------------
var parks = ee.FeatureCollection('projects/ee-desmond/assets/NewParkMerged')
  .select(['ORIG_NAME']);

// Burned area assets (20-year climatology)
var months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'];
var burnedAreaAssets = [
  'projects/ee-desmond/assets/SummedBurnedArea_Month10',
  'projects/ee-desmond/assets/SummedBurnedArea_Month11',
  'projects/ee-desmond/assets/SummedBurnedArea_Month12',
  'projects/ee-desmond/assets/SummedBurnedArea_Month1',
  'projects/ee-desmond/assets/SummedBurnedArea_Month2',
  'projects/ee-desmond/assets/SummedBurnedArea_Month3'
];
var burnedAreaImages = burnedAreaAssets.map(function(asset) {
  return ee.Image(asset);
});

// Buffer distances (0-20 km)
var bufferDistances = ee.List.sequence(0, 20, 5)
  .map(function(d) { return ee.Number(d).multiply(1000); });

// ======================================================================
// CLIMATE (ERA5-Land monthly aggregates, converted to physical units)
// ======================================================================
function getClimateForYear(year) {

  var start = ee.Date.fromYMD(year, 1, 1);
  var end   = ee.Date.fromYMD(year, 12, 31);

  var era5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
      .filterDate(start, end)
      .select([
        'temperature_2m',
        'temperature_2m_min',
        'temperature_2m_max',
        'dewpoint_temperature_2m',
        'total_precipitation_sum',
        'surface_pressure',
        'u_component_of_wind_10m',
        'v_component_of_wind_10m'
      ])
      .mean();

  var Tmean_C = era5.select('temperature_2m').subtract(273.15).rename('Tmean_C');
  var Tmin_C  = era5.select('temperature_2m_min').subtract(273.15).rename('Tmin_C');
  var Tmax_C  = era5.select('temperature_2m_max').subtract(273.15).rename('Tmax_C');
  var Tdew_C  = era5.select('dewpoint_temperature_2m').subtract(273.15).rename('Tdew_C');

  var Precip_mm = era5.select('total_precipitation_sum')
                      .multiply(1000)
                      .rename('Precip_mm');

  var SurfaceP_hPa = era5.select('surface_pressure')
                         .divide(100)
                         .rename('SurfaceP_hPa');

  var WindU = era5.select('u_component_of_wind_10m').rename('WindU');
  var WindV = era5.select('v_component_of_wind_10m').rename('WindV');

  return ee.Image.cat([
    Tmean_C, Tmin_C, Tmax_C, Tdew_C,
    Precip_mm, SurfaceP_hPa, WindU, WindV
  ]);
}

// ======================================================================
// LANDCOVER YEAR RESOLVER (see 03_landcover_harmonisation_full.js)
// ======================================================================
var years = [2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023, 2024];

// ======================================================================
// MAIN ANALYSIS FUNCTION
// ======================================================================
function calculateBurnedAreaAndLandUse(feature, landCover, year) {

  var results = bufferDistances.map(function(bufferDistance) {

    // Buffer geometry
    var geom = ee.Algorithms.If(
      ee.Number(bufferDistance).eq(0),
      feature.geometry(),
      feature.geometry().buffer(bufferDistance)
    );
    geom = ee.Geometry(geom);

    var burnFrequencyDict = ee.Dictionary({});
    var burnedAreaDict     = ee.Dictionary({});

    // -----------------------------------------------------------
    // CLIMATE (already converted: degC, mm, hPa)
    // -----------------------------------------------------------
    var climate = getClimateForYear(year).reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: geom,
      scale: 11132,     // ERA5-Land resolution
      maxPixels: 1e13
    });

    // -----------------------------------------------------------
    // BURNED AREA STATS
    // -----------------------------------------------------------
    months.forEach(function(month, index) {

      var burnedImage = burnedAreaImages[index];

      var burnFreq = burnedImage.reduceRegion({
        reducer: ee.Reducer.sum(),
        geometry: geom,
        scale: 500,
        maxPixels: 1e13
      }).get('BurnDate');

      var areaSqKm = ee.Number(burnFreq).multiply(500 * 500).divide(1e6);

      burnFrequencyDict = burnFrequencyDict.set(month + '_BurnFrequency', burnFreq);
      burnedAreaDict    = burnedAreaDict.set(month + '_BurnedArea_sqkm', areaSqKm);
    });

    // -----------------------------------------------------------
    // LAND COVER HISTOGRAM
    // -----------------------------------------------------------
    var landCoverStats = landCover.reduceRegion({
      reducer: ee.Reducer.frequencyHistogram(),
      geometry: geom,
      scale: 30,
      maxPixels: 1e13
    }).get('landcover');

    // -----------------------------------------------------------
    // SUMMARY METRICS
    // -----------------------------------------------------------
    var bufferAreaSqKm = ee.Number(geom.area()).divide(1e6);
    var totalBurns     = ee.Number(burnFrequencyDict.values().reduce(ee.Reducer.sum()));
    var totalPixels    = bufferAreaSqKm.divide(0.0009);   // 30m LC pixels
    var avgBurnPerPixel = totalBurns.divide(totalPixels);
    var avgBurnPerYear  = avgBurnPerPixel.divide(22);     // climatology length

    // -----------------------------------------------------------
    // MERGE ALL PROPERTIES
    // -----------------------------------------------------------
    var props = ee.Dictionary({
      'ORIG_NAME': feature.get('ORIG_NAME'),
      'Year': year,
      'Buffer_km': ee.Number(bufferDistance).divide(1000),
      'BufferArea_sqkm': bufferAreaSqKm,
      'TotalPixels': totalPixels,
      'AvgBurnPerPixel': avgBurnPerPixel,
      'AvgBurnPerYear': avgBurnPerYear,
      'LandUseDistribution': landCoverStats,

      'ERA5_Tmean_C': climate.get('Tmean_C'),
      'ERA5_Tmin_C':  climate.get('Tmin_C'),
      'ERA5_Tmax_C':  climate.get('Tmax_C'),
      'ERA5_Tdew_C':  climate.get('Tdew_C'),
      'ERA5_Precip_mm': climate.get('Precip_mm'),
      'ERA5_SurfacePressure_hPa': climate.get('SurfaceP_hPa'),
      'ERA5_WindU': climate.get('WindU'),
      'ERA5_WindV': climate.get('WindV')
    })
    .combine(burnFrequencyDict)
    .combine(burnedAreaDict);

    return ee.Feature(geom, props);
  });

  return ee.FeatureCollection(results);
}

// ======================================================================
// RUN ANALYSIS
// ======================================================================
var allResults = ee.FeatureCollection([]);

years.forEach(function(y) {
  var lcImg = getLandCoverYear(y);

  var yearFC = ee.FeatureCollection(
    parks.map(function(f) {
      return calculateBurnedAreaAndLandUse(f, lcImg, y);
    }).flatten()
  );

  allResults = allResults.merge(yearFC);
});

// ======================================================================
// EXPORT
// ======================================================================
Export.table.toDrive({
  collection: allResults,
  description: 'BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2',
  fileFormat: 'CSV',
  folder: 'GEE'
});

Export.table.toAsset({
  collection: allResults,
  description: 'BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_Asset',
  assetId: 'projects/ee-desmond/assets/BurnedArea_LC_Climate_ESRI_GLAD_2000_2024'
});
