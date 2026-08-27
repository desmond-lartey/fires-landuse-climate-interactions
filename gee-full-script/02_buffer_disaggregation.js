// Load the national parks shapefile
var parks = ee.FeatureCollection('projects/ee-desmond/assets/NewParkMerged')
  .select(['ORIG_NAME']);

// Define the months of interest
var months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'];

// Load the summed burned area images for each month from your assets
var burnedAreaAssets = [
  'projects/ee-desmond/assets/SummedBurnedArea_Month10',
  'projects/ee-desmond/assets/SummedBurnedArea_Month11',
  'projects/ee-desmond/assets/SummedBurnedArea_Month12',
  'projects/ee-desmond/assets/SummedBurnedArea_Month1',
  'projects/ee-desmond/assets/SummedBurnedArea_Month2',
  'projects/ee-desmond/assets/SummedBurnedArea_Month3'
];

// Load the burned area images
var burnedAreaImages = burnedAreaAssets.map(function(asset) {
  return ee.Image(asset);
});

// Define buffer distances in meters
var bufferDistances = ee.List.sequence(0, 20, 5).map(function(distance) {
  return ee.Number(distance).multiply(1000);
});

// Function to calculate burned area and frequency for each park and buffer
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
        reducer: ee.Reducer.sum(),
        geometry: bufferedGeometry,
        scale: 500,
        maxPixels: 1e13
      }).get('BurnDate');

      var burnedAreaSqKm = ee.Number(burnFrequency).multiply(500 * 500).divide(1e6); // Convert to sqkm

      burnFrequencyDict = burnFrequencyDict.set(month, burnFrequency);
      burnedAreaDict = burnedAreaDict.set(month, burnedAreaSqKm);
    });

    // Calculate additional metrics
    var bufferAreaSqKm = ee.Number(bufferedGeometry.area()).divide(1e6); // Area in sqkm
    var totalPixels = bufferAreaSqKm.divide(0.25); // Each pixel is 0.25 sqkm
    var avgBurnPerPixel = ee.Number(burnFrequencyDict.values().reduce(ee.Reducer.sum())).divide(totalPixels);
    var avgBurnPerYear = avgBurnPerPixel.divide(22); //  22 years of data

    // Create a feature with the buffered geometry and properties
    return ee.Feature(bufferedGeometry, {
      'ORIG_NAME': feature.get('ORIG_NAME'),
      'Bufferdist': ee.Number(bufferDistance).divide(1000),
      'Oct_BurnFrequency': burnFrequencyDict.get('Oct'),
      'Nov_BurnFrequency': burnFrequencyDict.get('Nov'),
      'Dec_BurnFrequency': burnFrequencyDict.get('Dec'),
      'Jan_BurnFrequency': burnFrequencyDict.get('Jan'),
      'Feb_BurnFrequency': burnFrequencyDict.get('Feb'),
      'Mar_BurnFrequency': burnFrequencyDict.get('Mar'),
      'Oct_BurnedArea_sqkm': burnedAreaDict.get('Oct'),
      'Nov_BurnedArea_sqkm': burnedAreaDict.get('Nov'),
      'Dec_BurnedArea_sqkm': burnedAreaDict.get('Dec'),
      'Jan_BurnedArea_sqkm': burnedAreaDict.get('Jan'),
      'Feb_BurnedArea_sqkm': burnedAreaDict.get('Feb'),
      'Mar_BurnedArea_sqkm': burnedAreaDict.get('Mar'),
      'TotalPixels': totalPixels,
      'AvgBurnPerPixel': avgBurnPerPixel,
      'AvgBurnPerYear': avgBurnPerYear,
      'BufferArea_sqkm': bufferAreaSqKm
    });
  });

  return ee.FeatureCollection(results);
}

// Apply the function to each park and flatten the results
var allResults = ee.FeatureCollection(parks.map(calculateBurnedAreaAndFrequency).flatten());

// Add layers to the map for visual inspection
Map.addLayer(parks, {}, 'National Parks');

bufferDistances.getInfo().forEach(function(bufferDistance) {
  var bufferLayer = parks.map(function(feature) {
    return ee.Feature(
      ee.Algorithms.If(
        ee.Number(bufferDistance).eq(0),
        feature.geometry(),
        feature.geometry().buffer(bufferDistance)
      )
    );
  });
  Map.addLayer(bufferLayer, {}, 'Buffer ' + bufferDistance / 1000 + ' km');
});

burnedAreaImages.forEach(function(image, index) {
  Map.addLayer(image, {min: 0, max: 100, palette: ['4e0400', '951003', 'c61503', 'ff1901']}, 'Burned Area Month ' + months[index]);
});

// Center the map on the area of interest
Map.centerObject(parks, 6);

// Export the results to a CSV file
Export.table.toDrive({
  collection: allResults,
  description: 'BurnedAreaAndFrequencyResults',
  fileFormat: 'CSV',
  folder: 'GEE'
});

//To export the shapefiles

// Buffer distances in meters
var bufferDistances = ee.List.sequence(0, 20, 5).map(function(distance) {
  return ee.Number(distance).multiply(1000);
});

// Build FeatureCollections for each buffer distance
var bufferCollections = bufferDistances.map(function(bufferDistance) {

  var fc = parks.map(function(feature) {
    var geom = ee.Algorithms.If(
      ee.Number(bufferDistance).eq(0),
      feature.geometry(),
      feature.geometry().buffer(bufferDistance)
    );

    // Wrap geometry into a Feature safely
    var newFeat = ee.Feature(ee.Geometry(geom));

    // Copy ONLY non-geometry properties
    return newFeat.copyProperties(feature, feature.propertyNames());
  });

  return ee.FeatureCollection(fc)
           .set('buffer_m', bufferDistance);
});

// Export the results to a SHP file
bufferDistances.getInfo().forEach(function(bufferDistance, index) {

  var fc = ee.FeatureCollection(bufferCollections.get(index));

  Export.table.toDrive({
    collection: fc,
    description: 'Buffer_' + bufferDistance + '_m',
    fileFormat: 'SHP',
    folder: 'GEE'
  });

});

// Export the results to an Earth Engine asset
Export.table.toAsset({
  collection: allResults,
  description: 'BurnedAreaAndFrequencyResultsAsset',
  assetId: 'projects/ee-desmond/assets/BurnedAreaAndFrequencyResultsAsset'
});
