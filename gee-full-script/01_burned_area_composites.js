// Define the extent covering all the required national parks
var area = geometry; // Use the geometry you defined in the GEE interface

// Define the time range
var startDate = '2004-01-01';
var endDate = '2025-01-01';

// Load the MODIS MCD64A1 dataset for burned area
var modisCollection = ee.ImageCollection("MODIS/061/MCD64A1")
                        .filterDate(startDate, endDate)
                        .filterBounds(area);

// Function to process and mosaic burned area data for a given date
function processBurnedArea(date, region) {
  var filtered = modisCollection.filterDate(date, ee.Date(date).advance(1, 'month'));
  var mosaicked = filtered.mosaic().clip(region);
  var burned = mosaicked.select('BurnDate').gt(0).selfMask();
  return burned.set('date', date);
}

// Function to sum burned area for a specific month across multiple years
function sumBurnedAreaForSpecificMonth(month, startYear, endYear, region) {
  var dateList = ee.List.sequence(startYear, endYear).map(function(year) {
    return ee.Date.fromYMD(year, month, 1);
  });

  var monthlyBurned = ee.ImageCollection.fromImages(
    dateList.map(function(date) {
      return processBurnedArea(date, region);
    })
  );

  var summedBurned = monthlyBurned.sum().set('month', month).toDouble();
  return summedBurned;
}

// Function to sum burned area for all months across multiple years
function sumBurnedAreaForAllMonths(startYear, endYear, region) {
  var monthList = ee.List.sequence(1, 12);

  var allBurned = ee.ImageCollection.fromImages(
    monthList.map(function(month) {
      return sumBurnedAreaForSpecificMonth(month, startYear, endYear, region);
    })
  );

  var summedBurned = allBurned.sum().toDouble();
  return summedBurned;
}

// Inspect and display the burned area for each month across all years
var startYear = 2004;
var endYear = 2024;

var monthSummedImages = [];

// Process each month and add it to the map
for (var month = 1; month <= 12; month++) {
  (function(month) {
    var summedBurned = sumBurnedAreaForSpecificMonth(month, startYear, endYear, area);
    monthSummedImages.push(summedBurned);

    // Export the results for each month to Google Drive
    Export.image.toDrive({
      image: summedBurned,
      description: 'SummedBurnedArea_Month' + month,
      scale: 500,
      region: area,
      fileFormat: 'GeoTIFF'
    });

    // Display the results for each month on the map for verification
    Map.addLayer(summedBurned, {min: 0, max: 30, palette: ['white', 'red']}, 'Summed Burned Area Month ' + month);

    // Print the results to the console for debugging
    summedBurned.evaluate(function(res) {
      print('Summed Burned Area for Month ' + month + ' (2004-2024):', res);
    });
  })(month);
}

// Inspect and display the burned area for all months across all years
var summedBurnedForAllMonths = sumBurnedAreaForAllMonths(startYear, endYear, area);

// Export the results for all months to Google Drive
Export.image.toDrive({
  image: summedBurnedForAllMonths,
  description: 'SummedBurnedArea_AllMonths',
  scale: 500,
  region: area,
  fileFormat: 'GeoTIFF'
});

// Display the results for all months on the map for verification
Map.addLayer(summedBurnedForAllMonths, {min: 0, max: 30,   palette:  ['4e0400', '951003', 'c61503', 'ff1901' ]}, 'Summed Burned Area All Months');

// Center the map on the area of interest
Map.centerObject(area, 6);

// Print the results for all months to the console for debugging
summedBurnedForAllMonths.evaluate(function(res) {
  print('Summed Burned Area for All Months (2004-2024):', res);
});

print("Script executed successfully. Check the map layers and Google Drive for the exported images.");

// --- Optional: export the same composites straight to EE assets ---
// for (var month = 1; month <= 12; month++) {
//   (function(month) {
//     var summedBurned = sumBurnedAreaForSpecificMonth(month, startYear, endYear, area);
//     var assetId = 'projects/YOUR_PROJECT/assets/SummedBurnedArea_Month' + month;
//     Export.image.toAsset({
//       image: summedBurned,
//       description: 'SummedBurnedArea_Month' + month,
//       assetId: assetId,
//       scale: 500,
//       region: area,
//       maxPixels: 1e13
//     });
//   })(month);
// }
//
// var assetIdAllMonths = 'projects/YOUR_PROJECT/assets/SummedBurnedArea_AllMonths';
// Export.image.toAsset({
//   image: summedBurnedForAllMonths,
//   description: 'SummedBurnedArea_AllMonths',
//   assetId: assetIdAllMonths,
//   scale: 500,
//   region: area,
//   maxPixels: 1e13
// });
