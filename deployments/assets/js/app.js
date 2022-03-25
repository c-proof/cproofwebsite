var config = {
  geojson: "/gliderdata/deployments/cproof-deployments.geojson",
  title: "C-PROOF Glider Deployments",
  layerName: "Glider Tracks",
  sortProperty: "deployment_start",
  sortOrder: "desc"
};

var properties = [
{
  value: "deployment_name",
  label: "Deployment Name",
  table: {
    visible: true,
    sortable: true
  },
  filter: {
    type: "string"
  },
  info: false
},
{
  value: "active",
  label: "Active",
  table: {
    visible: true,
    sortable: true
  },
  filter: {
    type: "boolean",
    operators: ['equal', 'not_equal'],
    input: 'radio',
    values: [true, false],
  },
  info: true
},
{
  value: "deployment_start",
  label: "Deployment Start",
  table: {
    visible: true,
    sortable: true
  },
  filter: {
    type: "datetime",
    vertical: true,
    multiple: true,
    operators: ["greater", "less", "equal", "not_equal"],
    values: []
  }
},
{
  value: "deployment_end",
  label: "Deployment End",
  table: {
    visible: true,
    sortable: true
  },
  filter: {
    type: "datetime",
    vertical: true,
    multiple: true,
    operators: ["greater", "less", "equal", "not_equal"],
    values: []
  }
},
{
  value: "glider_name",
  label: "Glider Name",
  table: {
    visible: true,
    sortable: true
  },
  filter: {
    type: "string"
  },
  info: true
},
{
  value: "glider_model",
  label: "Glider Model",
  table: {
    visible: true,
    sortable: true
  },
  filter: {
    type: "string"
  },
  info: true
},
{
  value: "comment",
  label: "Comment",
  table: {
    visible: true,
    sortable: true
  },
  filter: {
    type: "string"
  },
  info: true
},
{
  value: "url", 
  label: "URL",
  table: {
    visible: true,  
    sortable: true, //jp added 
    formatter: urlFormatter,  //jp added 
    width: 300, 
  },
  filter: {
    type: "string"  //jp added
  },
  info: true //jp added
}];

// some stations...
var LineP = {
  "type": "FeatureCollection",
  "name": "Line P Stations",
  "features": [
    { "type": "Feature", "properties": { "name": "P4" }, "geometry": { "type": "Point", "coordinates": [ -126. - 40./60., 48.+39./60. ] } },
    { "type": "Feature", "properties": { "name": "P8" }, "geometry": { "type": "Point", "coordinates": [ -128. - 40./60., 48.+49./60. ] } },
    { "type": "Feature", "properties": { "name": "P12" }, "geometry": { "type": "Point", "coordinates": [ -130. - 40./60., 48.+58.2/60. ] } },
    { "type": "Feature", "properties": { "name": "P16" }, "geometry": { "type": "Point", "coordinates": [ -134. - 40./60., 49.+17./60. ] } },
    { "type": "Feature", "properties": { "name": "P20" }, "geometry": { "type": "Point", "coordinates": [ -138. - 40./60., 49.+34./60. ] } },
    { "type": "Feature", "properties": { "name": "P26" }, "geometry": { "type": "Point", "coordinates": [ -145., 50. ] } },
  ]
};

$(function() {
  $(".title").html(config.title);
  $("#layer-name").html(config.layerName);
});

function buildConfig() {
  filters = [];
  table = [{
    field: "action",
    title: "<i class='fa fa-gear'></i>&nbsp;Action",
    align: "center",
    valign: "middle",
    width: "75px",
    cardVisible: false,
    switchable: false,
    formatter: function(value, row, index) {
      return [
        '<a class="zoom" href="javascript:void(0)" title="Zoom" style="margin-right: 10px;">',
          '<i class="fa fa-search-plus"></i>',
        '</a>',
        '<a class="identify" href="javascript:void(0)" title="Identify">',
          '<i class="fa fa-info-circle"></i>',
        '</a>'
      ].join("");
    },
    events: {
      "click .zoom": function (e, value, row, index) {
        map.fitBounds(featureLayer.getLayer(row.leaflet_stamp).getBounds());
        highlightLayer.clearLayers();
        highlightLayer.addData(featureLayer.getLayer(row.leaflet_stamp).toGeoJSON());
      },
      "click .identify": function (e, value, row, index) {
        identifyFeature(row.leaflet_stamp);
        highlightLayer.clearLayers();
        highlightLayer.addData(featureLayer.getLayer(row.leaflet_stamp).toGeoJSON());
      }
    }
  }];

  $.each(properties, function(index, value) {
    // Filter config
    if (value.filter) {
      var id;
      if (value.filter.type == "integer") {
        id = "cast(properties->"+ value.value +" as int)";
      }
      else if (value.filter.type == "double") {
        id = "cast(properties->"+ value.value +" as double)";
      }
      else {
        id = "properties->" + value.value;
      }
      filters.push({
        id: id,
        label: value.label
      });
      $.each(value.filter, function(key, val) {
        if (filters[index]) {
          // If values array is empty, fetch all distinct values
          if (key == "values" && val.length === 0) {
            alasql("SELECT DISTINCT(properties->"+value.value+") AS field FROM ? ORDER BY field ASC", [geojson.features], function(results){
              distinctValues = [];
              $.each(results, function(index, value) {
                distinctValues.push(value.field);
              });
            });
            filters[index].values = distinctValues;
          } else {
            filters[index][key] = val;
          }
        }
      });
    }
    // Table config
    if (value.table) {
      table.push({
        field: value.value,
        title: value.label
      });
      $.each(value.table, function(key, val) {
        if (table[index+1]) {
          table[index+1][key] = val;
        }
      });
    }
  });

  buildFilters();
  buildTable();
}

// Basemap Layers
var mapboxOSM = L.tileLayer('https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri and data providers'
});

var mapboxOcean = L.tileLayer('https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri and data providers'
});

var mapboxSat = L.tileLayer("https://{s}.tiles.mapbox.com/v4/mapbox.streets-satellite/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZnVsY3J1bSIsImEiOiJjaXI1MHZnNGcwMW41ZnhucjNkOTB1cncwIn0.4ZADnELXGBXsN_RxnPK3Sw", {
  maxZoom: 19,
  subdomains: ["a", "b", "c", "d"],
  attribution: 'Basemap <a href="https://www.mapbox.com/about/maps/" target="_blank">© Mapbox © OpenStreetMap</a>'
});

var highlightLayer = L.geoJson(null, {
  style: function (feature) {
    return {
      color: feature.properties.color,
      weight: 6,
      opacity: 1,
      clickable: false
    };
  }
});

function highlighttheLayer(target) {
  console.log('highlight')
  console.log(target)

  target.setStyle({opacity: 0.9});

  if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    target.bringToFront();
  }
}

function highlightFeature(e) {
  var target = e.target;
  highlighttheLayer(target);
}

function resetHighlight(e) {
   featureLayer.resetStyle(e.target);
}

var featureLayer = L.geoJson(null, {
  name: "Glider Tracks",
  filter: function(feature, layer) {
    return feature.geometry.coordinates[0] !== 0 && feature.geometry.coordinates[1] !== 0;
  },
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
  onEachFeature: function (feature, layer) {
    if (feature.properties) {
      layer.on({
        click: function (e) {
          identifyFeature(L.stamp(layer));
          highlightLayer.clearLayers();
          highlightLayer.addData(featureLayer.getLayer(L.stamp(layer)).toGeoJSON());
        },
        mouseover: function (e) {
          highlightLayer.clearLayers();
          highlightLayer.addData(featureLayer.getLayer(L.stamp(layer)).toGeoJSON());
        },
        mouseout: function (e) {
          highlightLayer.clearLayers();
        }
      });
    }
  }
});

var slocumIcon = L.icon({
  iconUrl: 'assets/images/slocum_glider.png',
  iconSize:     [38, 45],
  iconAnchor:   [18, 22]
});

var linepLayer = L.geoJson(null, {
  pointToLayer: function(feature, latlng){
    label = String(feature.properties.name); // Must convert to string, .bindTooltip can't use straight 'feature.properties.attribute'
    var marker = new L.CircleMarker(latlng, {
      radius: 2,
      fillColor: 'darkblue',
      color: 'darkblue',
      opacity: 0.7,
      fillOpacity: 0.7,
      zIndexOffset: -10
    });
    return marker;
  }
})

linepLayer.addData(LineP);

var glideLayer = L.layerGroup(null, {name: "Glider Marker"})

// This won't actually get added to the map, but will populate glideLayer
var gliderLayer = L.geoJson(null, {
  filter: function(feature, layer) {
    return feature.geometry.coordinates[0] !== 0 && feature.geometry.coordinates[1] !== 0 &&  feature.properties.active == true;
  },
  style: function (feature) {
    return {
      color: "#000000",
      weight: 0,
      opacity: 0.0,
      clickable: false
    };
  },
  onEachFeature: function (feature, layer) {
    numPts = feature.geometry.coordinates.length;
    var beg = feature.geometry.coordinates[numPts-1];
    var marker = L.marker([beg[1], beg[0]],
      {icon: slocumIcon}
    );
    glideLayer.addLayer(marker)
  }
});

// Fetch the GeoJSON file
$.getJSON(config.geojson, function (data) {
  geojson = data;
  features = $.map(geojson.features, function(feature) {
    return feature.properties;
  });
  featureLayer.addData(data);
  gliderLayer.addData(data);
  buildConfig();
  $("#loading-mask").hide();
});

var map = L.map("map", {
  layers: [mapboxOSM, mapboxOcean, featureLayer, highlightLayer, glideLayer, linepLayer]
}).fitWorld();

// ESRI geocoder
var searchControl = L.esri.Geocoding.Controls.geosearch({
  useMapBounds: 17
}).addTo(map);

// Info control
var info = L.control({
  position: "bottomleft"
});

// Custom info hover control
info.onAdd = function (map) {
  this._div = L.DomUtil.create("div", "info-control");
  this.update();
  return this._div;
};
info.update = function (props) {
  this._div.innerHTML = "";
};
info.addTo(map);
$(".info-control").hide();

// Larger screens get expanded layer control
if (document.body.clientWidth <= 767) {
  isCollapsed = true;
} else {
  isCollapsed = false;
}
var baseLayers = {
  "Ocean Topography": mapboxOSM,
};
var overlayLayers = {
  "Waypoints":      linepLayer,
  "Glider Tracks": featureLayer,
  "Active Gliders": glideLayer,
};
var layerControl = L.control.layers(baseLayers, overlayLayers, {
  collapsed: isCollapsed
}).addTo(map);

// scale:
L.control.scale().addTo(map);
//cursor position lat/lng
L.control.mousePosition().addTo(map);

// Filter table to only show features in current map bounds
map.on("moveend", function (e) {
  syncTable();
});

map.on("click", function(e) {
  highlightLayer.clearLayers();
});

// Table formatter to make links clickable
function urlFormatter (value, row, index) {
  if (typeof value == "string" && (value.indexOf("http") === 0 || value.indexOf("https") === 0)) {
    return "<a href='"+value+"' target='_blank'>"+value+"</a>";
  }
}

function buildFilters() {
  $("#query-builder").queryBuilder({
    allow_empty: true,
    filters: filters,
    plugins: {
      'sql-support': {
        boolean_as_integer: false
      }
    }
  });
}

function applyFilter() {
  var query = "SELECT * FROM ?";
  var sql = $("#query-builder").queryBuilder("getSQL", false, false).sql;
  if (sql.length > 0) {
    query += " WHERE " + sql;
  }
  alasql(query, [geojson.features], function(features){
		featureLayer.clearLayers();
		featureLayer.addData(features);
		syncTable();
	});
}


function buildTable() {
  $("#table").bootstrapTable({
    cache: false,
    height: $("#table-container").height(),
    undefinedText: "",
    striped: false,
    pagination: false,
    minimumCountColumns: 1,
    sortName: config.sortProperty,
    sortOrder: config.sortOrder,
    toolbar: "#toolbar",
    search: true,
    trimOnSearch: false,
    showColumns: true,
    showToggle: true,
    columns: table,
    onClickRow: function (row) {
      // do something!
    },
    onDblClickRow: function (row) {
      // do something!
    }
  });

  map.fitBounds(featureLayer.getBounds());
  // map.setView([50., -130], zoom=6)

  $(window).resize(function () {
    $("#table").bootstrapTable("resetView", {
      height: $("#table-container").height()
    });
  });
}

function syncTable() {
  tableFeatures = [];
  featureLayer.eachLayer(function (layer) {
    layer.feature.properties.leaflet_stamp = L.stamp(layer);
    if (map.hasLayer(featureLayer)) {
      tableFeatures.push(layer.feature.properties);
      // This limits to whats in the map, but we don't really want that....
      //      if (map.getBounds().contains(layer.getBounds())) {
      //        tableFeatures.push(layer.feature.properties);
      //      }
    }
  });
  $("#table").bootstrapTable("load", JSON.parse(JSON.stringify(tableFeatures)));
  var featureCount = $("#table").bootstrapTable("getData").length;
  if (featureCount == 1) {
    $("#feature-count").html($("#table").bootstrapTable("getData").length + " visible feature");
  } else {
    $("#feature-count").html($("#table").bootstrapTable("getData").length + " visible features");
  }
}

function identifyFeature(id) {
  var featureProperties = featureLayer.getLayer(id).feature.properties;
  var content = "<table class='table table-striped table-bordered table-condensed'>";
  $.each(featureProperties, function(key, value) {
    if (!value) {
      value = "";
    }
    if (typeof value == "string" && (value.indexOf("http") === 0 || value.indexOf("https") === 0)) {
      value = "<a href='" + value + "' target='_blank'>" + value + "</a>";
    }
    $.each(properties, function(index, property) {
      if (key == property.value) {
        if (property.info !== false) {
          content += "<tr><th>" + property.label + "</th><td>" + value + "</td></tr>";
        }
      }
    });
  });
  content += "<table>";
  $("#feature-info").html(content);
  $("#featureModal").modal("show");
}

function switchView(view) {
  if (view == "split") {
    $("#view").html("Split View");
    location.hash = "#split";
    $("#table-container").show();
    $("#table-container").css("height", "45%");
    $("#map-container").show();
    $("#map-container").css("height", "55%");
    $(window).resize();
    if (map) {
      map.invalidateSize();
    }
  } else if (view == "map") {
    $("#view").html("Map View");
    location.hash = "#map";
    $("#map-container").show();
    $("#map-container").css("height", "100%");
    $("#table-container").hide();
    if (map) {
      map.invalidateSize();
    }
  } else if (view == "table") {
    $("#view").html("Table View");
    location.hash = "#table";
    $("#table-container").show();
    $("#table-container").css("height", "100%");
    $("#map-container").hide();
    $(window).resize();
  }
}

$("[name='view']").click(function() {
  $(".in,.open").removeClass("in open");
  if (this.id === "map-graph") {
    switchView("split");
    return false;
  } else if (this.id === "map-only") {
    switchView("map");
    return false;
  } else if (this.id === "graph-only") {
    switchView("table");
    return false;
  }
});

$("#about-btn").click(function() {
  $("#aboutModal").modal("show");
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#filter-btn").click(function() {
  $("#filterModal").modal("show");
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#chart-btn").click(function() {
  $("#chartModal").modal("show");
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#view-sql-btn").click(function() {
  alert($("#query-builder").queryBuilder("getSQL", false, false).sql);
});

$("#apply-filter-btn").click(function() {
  applyFilter();
});

$("#reset-filter-btn").click(function() {
  $("#query-builder").queryBuilder("reset");
  applyFilter();
});

$("#extent-btn").click(function() {
  map.fitBounds(featureLayer.getBounds());
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#download-csv-btn").click(function() {
  $("#table").tableExport({
    type: "csv",
    ignoreColumn: [0],
    fileName: "data"
  });
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#download-excel-btn").click(function() {
  $("#table").tableExport({
    type: "excel",
    ignoreColumn: [0],
    fileName: "data"
  });
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#download-pdf-btn").click(function() {
  $("#table").tableExport({
    type: "pdf",
    ignoreColumn: [0],
    fileName: "data",
    jspdf: {
      format: "bestfit",
      margins: {
        left: 20,
        right: 10,
        top: 20,
        bottom: 20
      },
      autotable: {
        extendWidth: false,
        overflow: "linebreak"
      }
    }
  });
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#chartModal").on("shown.bs.modal", function (e) {
  drawCharts();
});
