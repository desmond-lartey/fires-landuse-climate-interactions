// =====================================
// PARKS & YEARS
// =====================================
var parks = ee.FeatureCollection('projects/ee-desmond/assets/NewParkMerged')
  .select(['ORIG_NAME']);
var years = ee.List.sequence(2004, 2024);
var seasons = [
  {label: 'Dry', startMonth: 10, endMonth: 3},   // Oct -> Mar
  {label: 'Wet', startMonth: 4, endMonth: 9}     // Apr -> Sep
];

// =====================================
// DATASETS
// =====================================
var MODIS_BA = ee.ImageCollection('MODIS/006/MCD64A1')
  .select('BurnDate')
  .filter(ee.Filter.date('2004-01-01', '2024-12-31'));

var ERA5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
  .select('total_precipitation_sum');   // meters

// =====================================
// PROCESS ONE (park, year, season)
// =====================================
var processParkYearSeason = function(park, year, season) {
  var geom = park.geometry();
  var parkName = park.get('ORIG_NAME');
  var start = ee.Date.fromYMD(year, season.startMonth, 1);
  var end = ee.Algorithms.If(
    ee.Number(season.startMonth).gt(season.endMonth),
    ee.Date.fromYMD(ee.Number(year).add(1), season.endMonth, 28),
    ee.Date.fromYMD(year, season.endMonth, 28)
  );
  end = ee.Date(end);

  // --------------------------
  // BURNED AREA (km2)
  // --------------------------
  var BA_season = MODIS_BA
    .filterDate(start, end)
    .map(function(img) {
      return ee.Image.pixelArea()
        .updateMask(img.select('BurnDate').gt(0))
        .divide(1e6);  // m2 -> km2
    })
    .sum();

  var baDict = BA_season.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geom,
    scale: 500,
    maxPixels: 1e13
  });

  var burnedArea_km2 = ee.Number(
    ee.Algorithms.If(
      baDict.contains('area'),
      baDict.get('area'),
      0
    )
  );

  // --------------------------
  // RAINFALL (ERA5 -> mm)
  // --------------------------
  var rainImg = ERA5
    .filterDate(start, end)
    .sum()                       // total over season
    .multiply(1000)              // m -> mm
    .rename('rainfall_mm');

  var rainDict = rainImg.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: geom,
    scale: 27830,                // ERA5 native resolution
    maxPixels: 1e13
  });

  var rainfall_mm = ee.Number(
    ee.Algorithms.If(
      rainDict.contains('rainfall_mm'),
      rainDict.get('rainfall_mm'),
      0
    )
  );

  // --------------------------
  // RETURN FEATURE
  // --------------------------
  return ee.Feature(null, {
    'Park': parkName,
    'Year': year,
    'Season': season.label,
    'BurnedArea_km2': burnedArea_km2,
    'Rainfall_mm': rainfall_mm
  });
};

// =====================================
// PROCESS ALL PARKS, YEARS, SEASONS
// =====================================
var features = [];
var parkList = parks.toList(parks.size());
for (var p = 0; p < parkList.size().getInfo(); p++) {
  var park = ee.Feature(parkList.get(p));
  for (var y = 0; y < years.size().getInfo(); y++) {
    var year = ee.Number(years.get(y));
    for (var s = 0; s < seasons.length; s++) {
      var feature = processParkYearSeason(park, year, seasons[s]);
      features.push(feature);
    }
  }
}
var outputFC = ee.FeatureCollection(features);

// =====================================
// EXPORT TO DRIVE
// =====================================
Export.table.toDrive({
  collection: outputFC,
  description: 'BurnedArea_ERA5Seasonal_2004_2024',
  folder: 'GEE',
  fileFormat: 'CSV',
  selectors: ['Park', 'Year', 'Season', 'BurnedArea_km2', 'Rainfall_mm']
});
