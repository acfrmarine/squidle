var map = new OpenLayers.Map('map_container', {
    allOverlays: true,
    displayProjection: new OpenLayers.Projection("EPSG:4326")}),

    esriOcean = new OpenLayers.Layer.XYZ("ESRI Ocean Basemap",
        "http://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/${z}/${y}/${x}",
        {
            sphericalMercator: true,
            isBaseLayer: true,
            numZoomLevels: 13
        }
    );

map.addLayers([esriOcean]);
map.setCenter(new OpenLayers.LonLat(115, -25).transform(
	new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), 6);
