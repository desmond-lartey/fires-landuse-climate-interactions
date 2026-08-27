var esri_lulc10 = ee.ImageCollection ('projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS')

// ===============================
// ESRI 9-class dictionary (canonical)
// ===============================
var lcDict = {
  names: [
    "Water",
    "Trees",
    "Flooded Vegetation",
    "Crops",
    "Built Area",
    "Bare Ground",
    "Snow/Ice",
    "Clouds",
    "Rangeland"
  ],
  colors: [
    "#1A5BAB", // 1 Water
    "#358221", // 2 Trees
    "#87D19E", // 3 Flooded Vegetation
    "#FFDB5C", // 4 Crops
    "#ED022A", // 5 Built Area
    "#EDE9E4", // 6 Bare Ground
    "#F2FAFF", // 7 Snow/Ice
    "#C8C8C8", // 8 Clouds
    "#C6AD8D"  // 9 Rangeland
  ]
};

// ===============================
// GLAD -> ESRI DICTIONARY (harmonised to 9 classes)
// ===============================
var gladToEsri = ee.Dictionary({

  // ===== WATER (200-211 etc.) =====
  200:1, 201:1, 202:1, 203:1, 204:1, 207:1,
  208:1, 209:1, 210:1, 211:1,

  // ===== TREES (25-96, 126-196) =====

  // Stable trees
  25:2, 26:2, 27:2, 28:2, 29:2, 30:2, 31:2, 32:2,
  33:2, 34:2, 35:2, 36:2, 37:2, 38:2, 39:2, 40:2,
  41:2, 42:2, 43:2, 44:2, 45:2, 46:2, 47:2, 48:2,

  // Disturbed (49-72)
  49:2, 50:2, 51:2, 52:2, 53:2, 54:2, 55:2, 56:2,
  57:2, 58:2, 59:2, 60:2, 61:2, 62:2, 63:2, 64:2,
  65:2, 66:2, 67:2, 68:2, 69:2, 70:2, 71:2, 72:2,

  // Gains (73-96)
  73:2, 74:2, 75:2, 76:2, 77:2, 78:2, 79:2, 80:2,
  81:2, 82:2, 83:2, 84:2, 85:2, 86:2, 87:2, 88:2,
  89:2, 90:2, 91:2, 92:2, 93:2, 94:2, 95:2, 96:2,

  // Stable (126-148)
  126:2, 127:2, 128:2, 129:2, 130:2, 131:2, 132:2, 133:2,
  134:2, 135:2, 136:2, 137:2, 138:2, 139:2, 140:2, 141:2,
  142:2, 143:2, 144:2, 145:2, 146:2, 147:2, 148:2,

  // Disturbance (149-172)
  149:2, 150:2, 151:2, 152:2, 153:2, 154:2, 155:2, 156:2,
  157:2, 158:2, 159:2, 160:2, 161:2, 162:2, 163:2, 164:2,
  165:2, 166:2, 167:2, 168:2, 169:2, 170:2, 171:2, 172:2,

  // Height gain (173-196)
  173:2, 174:2, 175:2, 176:2, 177:2, 178:2, 179:2, 180:2,
  181:2, 182:2, 183:2, 184:2, 185:2, 186:2, 187:2, 188:2,
  189:2, 190:2, 191:2, 192:2, 193:2, 194:2, 195:2, 196:2,

  // ===== FLOODED VEGETATION (100-124) =====
  100:3, 101:3, 102:3, 103:3, 104:3, 105:3, 106:3,
  107:3, 108:3, 109:3, 110:3, 111:3, 112:3, 113:3,
  114:3, 115:3, 116:3, 117:3, 118:3, 119:3, 120:3,
  121:3, 122:3, 123:3, 124:3,

  // ===== RANGELAND / SHORT VEGETATION (0-24) =====
  // mapped to class 9 (Rangeland), not 8
  0:9, 1:9, 2:9, 3:9, 4:9, 5:9, 6:9, 7:9, 8:9, 9:9,
  10:9, 11:9, 12:9, 13:9, 14:9, 15:9, 16:9, 17:9,
  18:9, 19:9, 20:9, 21:9, 22:9, 23:9, 24:9,

  // ===== CROPS (244-249) =====
  244:4, 245:4, 246:4, 247:4, 248:4, 249:4,

  // ===== BUILT-UP (250-253) =====
  250:5, 251:5, 252:5, 253:5,

  // ===== SNOW/ICE (241-243) =====
  241:7, 242:7, 243:7

  // Clouds (8) do not exist in GLAD -> class 8 will just be absent
});

// =============
// GLAD HARMONISATION
// =============
function harmoniseGlad(img) {
  return img.remap(
    gladToEsri.keys().map(ee.Number.parse),
    gladToEsri.values().map(ee.Number.parse)
  ).rename('landcover');  // consistent name
}

var landmask = ee.Image("projects/glad/OceanMask").lte(1);
var glad_raw_2000 = ee.Image('projects/glad/GLCLU2020/v2/LCLUC_2000')
  .select(0)
  .updateMask(landmask);

var glad_esri_2000 = harmoniseGlad(glad_raw_2000);

Map.addLayer(
  glad_esri_2000,
  {min: 1, max: 9, palette: lcDict.colors},
  'GLAD 2000 -> ESRI 9-class'
);

// Define a dictionary which will be used to make legend and visualize image on map
var dict = {
  "names": [
    "Water", "Trees", "Flooded Vegetation", "Crops", "Built Area",
    "Bare Ground", "Snow/Ice", "Clouds", "Rangeland"
  ],
  "colors": [
    "#1A5BAB", "#358221", "#87D19E", "#FFDB5C", "#ED022A",
    "#EDE9E4", "#F2FAFF", "#C8C8C8", "#C6AD8D"
  ]};

function remapper(image){
  var remapped = image.remap([1,2,4,5,7,8,9,10,11],[1,2,3,4,5,6,7,8,9])
  return remapped
}

function remapEsri(image) {
  return image.remap(
    [1,2,4,5,7,8,9,10,11], // original ESRI classes
    [1,2,3,4,5,6,7,8,9]    // harmonised 9-class scheme
  ).rename('landcover');
}

// Add image to the map
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2017-01-01','2017-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2017 LULC 10m')
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2018-01-01','2018-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2018 LULC 10m')
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2019-01-01','2019-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2019 LULC 10m')
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2020-01-01','2020-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2020 LULC 10m')
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2021-01-01','2021-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2021 LULC 10m')
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2022-01-01','2022-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2022 LULC 10m')
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2023-01-01','2023-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2023 LULC 10m')
Map.addLayer(ee.ImageCollection(esri_lulc10.filterDate('2024-01-01','2024-12-31').mosaic()).map(remapper), {min:1, max:9, palette:dict['colors']}, '2024 LULC 10m')

var years = [2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023, 2024];

function getLandCoverYear(year) {
  // ESRI LULC (2021-2024)
  if (year >= 2021) {
    var esriImage = esri_lulc10
      .filterDate(year + '-01-01', year + '-12-31')
      .mosaic()
      .select(0);
    return remapEsri(esriImage);
  }
  // GLAD (2000-2020)
  if (year >= 2000 && year <= 2020) {
    var gladImage = ee.Image('projects/glad/GLCLU2020/v2/LCLUC_' + year)
      .select(0);
    return harmoniseGlad(gladImage);
  }
  // Fallback
  return ee.Image(0).rename('landcover');
}

Export.image.toAsset({
  image: glad_esri_2000,
  description: 'Export_GLAD_Harmonised_ESRI_30m_2000',
  assetId: 'projects/ee-desmond/assets/GLAD_harmonised_30m_2000',
  scale: 30,
  maxPixels: 1e13
});
