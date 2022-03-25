
// Basemap Layers
var mapboxOSM = L.tileLayer('https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri'
});

var mapboxOcean = L.tileLayer('https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri'
});


var featureLayer = L.geoJson(null, {
  style: function (feature) {
    return {
      color: feature.properties.color,
      weight: 4,
      opacity: 0.6,
      fillColor: feature.properties.color,
      fillOpacity: 0.6,
      clickable: true
    };
  },
});

// Fetch the GeoJSON file
$.getJSON("/gliderdata/deployments/cproof-deployments_argo.geojson", function (data) {
  geojson = data;
  features = $.map(geojson.features, function(feature) {
    return feature.properties;
  });
  featureLayer.addData(data);
  $("#loading-mask").hide();
});

var map = L.map("mapfront", {
  layers:  [mapboxOcean, mapboxOSM, featureLayer]
}).setView([50., -133], zoom=5)


// Larger screens get expanded layer control
if (document.body.clientWidth <= 767) {
  isCollapsed = true;
} else {
  isCollapsed = false;
}
var baseLayers = {
  "Ocean Labels": mapboxOSM,
};

var layerControl = L.control.layers(baseLayers, overlayLayers, {
}).addTo(map);
