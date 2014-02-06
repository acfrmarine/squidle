//need so the ajax queries can make it outside the projects domain and contact geoserver
OpenLayers.ProxyHost = "/proxy/?url=";
//OpenLayers.ProxyHost = "/cgi-bin/proxy.cgi?url=";

/**
 * Used for WMS mapping purposes. Takes a WMSUrl and WMS Layer name and configures a map.
 *
 * @param wmsUrl - The URL of the Web Map Service, we are using geoserver
 * @param wmsLayerName - The name of the WMS Layer
 * @param divName - This is the name of the <div> in which the map is bound to in the page
 * @param deploymentExtentUrl - This is the name of the url to query for deployment extents
 * @param collectionExtentUrl - This is the name of the url to query for collection extents
 * FIXME: Note sure why or whether we need to pass in these urls.
 * @constructor
 */

function BaseMap(geoserverUrl, divName, deploymentExtentUrl, collectionExtentUrl, globalstate) {
	//Map view code to get moved out later.
	//prep some data we need to use to display the points
    this.wmsUrl = geoserverUrl + '/wms';
    this.wfsUrl = geoserverUrl + '/wfs';
    //this.wmsLayerName = wmsLayerName;
	this.deploymentExtentUrl = deploymentExtentUrl;
	this.collectionExtentUrl = collectionExtentUrl;
	this.hostname = location.hostname;
	
	this.browseEnabled = true;

    console.log("wmsUrl: " + this.wmsUrl);
    console.log("wfsUrl: " + this.wfsUrl);
    console.log("divName: " + divName);
	console.log("deploymentExtentUrl: " + deploymentExtentUrl);
	console.log("collectionExtentUrl: " + collectionExtentUrl);

	/* Filter based on the deployment id */
	this.filter_1_1 = new OpenLayers.Format.Filter({
		version : "1.1.0"
	});
	this.filter = new OpenLayers.Filter.Logical({
		type : OpenLayers.Filter.Logical.OR,
		filters : []
	});

	/* Setting up the projection details here, so that 4326 projected data can be displayed on top of
	 * base layers that use the google projection */
	this.xml = new OpenLayers.Format.XML();
	this.geographic = new OpenLayers.Projection("EPSG:4326");
	this.mercator = new OpenLayers.Projection("EPSG:900913");
	this.world = new OpenLayers.Bounds(-180, -89, 180, 89).transform(this.geographic, this.mercator);
	
	this.AUVimageSelectionFilter = [];
	this.ExploreFilter = [];

	//map setting based on projections
	var options = {
		projection : this.mercator,
		//displayProjection: geographic,
		units : "m",
		maxExtent : this.world,
		maxResolution : 156543.0399,
		numZoomLevels : 25,
		controls : [
			new OpenLayers.Control.Navigation(), 
			new OpenLayers.Control.PanZoomBar(), 
			new OpenLayers.Control.LayerSwitcher({'ascending' : false}),
			//new OpenLayers.Control.Permalink(),
			new OpenLayers.Control.ScaleLine(),
			//new OpenLayers.Control.Permalink('permalink'),
			new OpenLayers.Control.MousePosition(), 
			new OpenLayers.Control.OverviewMap(), 
			new OpenLayers.Control.KeyboardDefaults()]
	};

	//map is assigned to the given div
	this.mapInstance = new OpenLayers.Map(divName, options);

	/*set up the open street map base layers, need to set some extra resolution information here so that
	 we can zoom beyond OSM's maximum zoom level of 18*/
	var osm = new OpenLayers.Layer.OSM(null, null, {
		resolutions : [156543.03390625, 78271.516953125, 39135.7584765625, 19567.87923828125, 9783.939619140625, 4891.9698095703125, 2445.9849047851562, 1222.9924523925781, 611.4962261962891, 305.74811309814453, 152.87405654907226, 76.43702827453613, 38.218514137268066, 19.109257068634033, 9.554628534317017, 4.777314267158508, 2.388657133579254, 1.194328566789627, 0.5971642833948135, 0.25, 0.1, 0.05],
		serverResolutions : [156543.03390625, 78271.516953125, 39135.7584765625, 19567.87923828125, 9783.939619140625, 4891.9698095703125, 2445.9849047851562, 1222.9924523925781, 611.4962261962891, 305.74811309814453, 152.87405654907226, 76.43702827453613, 38.218514137268066, 19.109257068634033, 9.554628534317017, 4.777314267158508, 2.388657133579254, 1.194328566789627, 0.5971642833948135],
		transitionEffect : 'resize',
		isBaseLayer : true,
		minZoomLevel : 1,
		maxZoomLevel : 25,
		numZoomLevels : 25,
		sphericalMercator : true
	});
	//    var google_maps = new OpenLayers.Layer.Google(
	//    "Google Maps", {
	//    numZoomLevels: 20
	//    }
	//    );
	//    var google_satellite = new OpenLayers.Layer.Google(
	//    "Google Satellite", {
	//    type: google.maps.MapTypeId.SATELLITE,
	//    numZoomLevels: 20
	//    }
	//    );
	//    this.mapInstance.addLayers([osm, google_maps, google_satellite]);
	this.mapInstance.addLayers([osm]);


	//url = "http://"+geoserverurl+":8080/geoserver/wms"
	//url = "http://" + geoserverurl + "/geoserver/wms"
	var style = new OpenLayers.Style({
		pointRadius : "${radius}",
		fillColor : "#ffcc66",
		fillOpacity : 0.8,
		strokeColor : "#cc6633",
		strokeWidth : "${width}",
		strokeOpacity : 0.8
	}, {
		context : {
			width : function(feature) {
				return (feature.cluster) ? 2 : 1;
			},
			radius : function(feature) {
				var pix = 2;
				if (feature.cluster) {
					pix = Math.min(feature.attributes.count, 7) + 2;
				}
				return pix;
			}
		}
	});
	
	this.layers = {
		// Deployments were originally setup as a WMS layer.  However, these can be shown as a vector layer as there are
		// relatively few deployments.  We will use the OpenLayers clustering to group deployments.
		// Reminder: have to setup proxy.cgi for WFS layers to work
		
		AUVdeployments: new OpenLayers.Layer.Vector("AUVdeployments", {
			 strategies: [new OpenLayers.Strategy.Fixed(),
			 new OpenLayers.Strategy.Cluster()],
			 protocol: new OpenLayers.Protocol.WFS({
                 url: this.wfsUrl,
                 featureType: "catamidb_deployment",
                 featureNS: "http://catami"
			 }),
			 styleMap: new OpenLayers.StyleMap({
                 "default": style,
                 "select": {
                     fillColor: "#8aeeef",
                     strokeColor: "#32a8a9"
                 }
			 }),
			 projection: this.geographic
		 }, {maxScale: 150000}),
//		 AUVdeploymentsWMS: new OpenLayers.Layer.WMS("AUVdeploymentsWMS", this.wmsUrl,
//		 {
//		     //layers: 'catami:catamidb_deployment',
//		     layers: 'catami:catamidb_deployment',
//		     format: 'image/gif',
//		     transparent: 'TRUE',
//			 sld: "http://"+this.hostname+"/geoserverDeploymentSimplestyle?colour=00FF00&size=15"
//			 //sld: "http://"+geoserverurl+"/geoserverstyle?prop=depth&min=35.0&max=50.0"
//		 }),
		 //projection: this.geographic
		 //}),
		 //{maxScale: 150000}),
         
         AUVpolygonSelection: new OpenLayers.Layer.Vector("AUVpolygonSelection", null),
		 AUVimagesSelection: new OpenLayers.Layer.WMS("AUVimagesSelection", this.wmsUrl, {
			 layers: 'catami:catamidb_images',
			 format: 'image/gif',
			 transparent: 'TRUE',
  			 sld : "http://" + this.hostname + "/geoserverSimplestyle?name=catami:catamidb_images&colour=00FF00&size=5"
		 }, {minScale: 150000}),
		 AUVimages: new OpenLayers.Layer.WMS("AUVimages", this.wmsUrl, {
			 layers: 'catami:catamidb_images',
			 format: 'image/gif',
			 transparent: 'TRUE',
			 sld: "http://"+ this.hostname+"/geoserverstyle?prop=depth&min=35.0&max=50.0"
		 }, {minScale: 150000}),

		AUVcollection : new OpenLayers.Layer.WMS("AUVcollection", this.wmsUrl,
		{
			layers : 'catami:collection_images',
			format : 'image/gif',
			transparent : 'TRUE',
			filter : this.xml.write(this.filter_1_1.write(this.filter)),
			sld : "http://" + this.hostname + "/geoserverSimplestyle?name=catami:collection_images&colour=0000FF&size=1"
		}, {isBaseLayer: false}), //{minScale: 150000}),
		AUVworkset : new OpenLayers.Layer.WMS("AUVworkset", this.wmsUrl,
		{
			layers : 'catami:collection_images',
			format : 'image/gif',
			transparent : 'TRUE',
			filter : this.xml.write(this.filter_1_1.write(this.filter)),
			sld : "http://" + this.hostname + "/geoserverSimplestyle?name=catami:collection_images&colour=FF0000&size=9"
		}, {isBaseLayer: false}), //{minScale: 150000}),
		AUVcurrentImage : new OpenLayers.Layer.Markers("AUVcurrentImage"),
		/*AUVcurrentImage: new OpenLayers.Layer.WMS("AUVcurrentImage", this.wmsUrl,
		{
		layers: 'catami:catamidb_images',
		format: 'image/gif',
		transparent: 'TRUE',
		filter: this.xml.write(this.filter_1_1.write(this.filter)),
		},
		{minScale: 150000}),*/
		/* Started playing with the IMOS AODN geoserver.  Looks like it would be pretty straightforward to import layers
		from there.*/
		/*IMOSAUVdeployments : new OpenLayers.Layer.WMS("IMOSAUVdeployments",
		"http://geoserver.imos.org.au/geoserver/wms",
		{
		layers: 'helpers:auv_tracks',
		styles: '',
		projection: this.geographic,
		format: 'image/gif',
		transparent: 'TRUE',
		tiled: 'TRUE',
		//sld: "http://"+this.hostname+"/geoserverDeploymentSimplestyle?colour=FF0000&size=9"
		},
		{
		isBaseLayer: false,
		transitionEffect: 'resize',
		buffer: 0,
		displayOutsideMaxExtent: true
		}),*/
		/*IMOSAUVimages : new OpenLayers.Layer.WMS("IMOSAUVimages",
		"http://geoserver.imos.org.au/geoserver/wms",
		{
		layers: 'helpers:auv_images_vw',
		styles: '',
		projection: this.geographic,
		format: 'image/gif',
		transparent: 'TRUE',
		tiled: 'TRUE'
		},
		{
		isBaseLayer: false,
		transitionEffect: 'resize',
		buffer: 0,
		minScale: 150000,
		displayOutsideMaxExtent: true
		}),*/
	};
//    console.log(this.layers.AUVimages);
//
//	console.log(this.layers.AUVcollection)

	//console.log(this.layers['AUVdeployments']);
//	for (var key in this.layers) {
//		this.mapInstance.addLayer(this.layers[key]);
//	}

	/**
	 * Show list of deployments when hovering over deployment vector icons
	 **/
	var showDeploymentInfo = function(event) {
		console.log(event);
		if (event.feature.cluster.length > 0)
		{
			var deploymentIds = [];
	        var infoid = '#map-info';
	        $(infoid).html('<b>Deployments IDs:</b><br/> ');
	        //+' (<a href="javascript:void(0)" onclick="$(\'#map-nav\').tab(\'show\')">show image</a>)');
			
			for (var i = 0, len = event.feature.cluster.length; i < len; i++) {
				var fid = event.feature.cluster[i].fid.split(".");
				var short_name = event.feature.cluster[i].data.short_name;
				deploymentIds[i] = fid[1];
				$(infoid).append(short_name + "<br/>");
			}
			
	        /*var thumbid = '#map-thumb';
	        console.log(imginfo.images[0].thumbnail_location);
	        $(thumbid).html('<a  href="javascript:void(0)"><img src="'+imginfo.images[0].thumbnail_location+'"/></a>')*/
		}
	};


	/**
	 * Zoom to a deployment
	 **/
	function zoomToDeployments(event) {
		// parse the deployment ids
		var deploymentIds = [];
		for (var i = 0, len = event.feature.cluster.length; i < len; i++) {
			var fid = event.feature.cluster[i].fid.split(".");
			deploymentIds[i] = fid[1];
		}
		// update the map bounds to zoom into the deployment
		if (deploymentIds.length > 0) {
			baseMap.updateMapBounds("deployment_ids=" + deploymentIds, baseMap.deploymentExtentUrl);//(deploymentIds);
		}
		// hide the popup if it was visible
		//event.feature.popup.hide();

		//var f = event.feature;
		console.log(event.feature);
	}


	 
	 /*select = new OpenLayers.Layer.Vector("Selection", {styleMap:
	 new OpenLayers.Style(OpenLayers.Feature.Vector.style["select"])
	 });
	 hover = new OpenLayers.Layer.Vector("Hover");
	 this.mapInstance.addLayers([hover, select]);

	 this.controls['box'].events.register("featureselected", this, function(e) {
		 select.addFeatures([e.feature]);
		 console.log(select);
	 });
	 this.controls['box'].events.register("featureunselected", this, function(e) {
	 select.removeFeatures([e.feature]);
	 });
	 this.controls['box'].events.register("hoverfeature", this, function(e) {
	 hover.addFeatures([e.feature]);
	 });
	 this.controls['box'].events.register("outfeature", this, function(e) {
	 hover.removeFeatures([e.feature]);
	 });
	 this.controls['polygon'].events.register("selected", this, function(event){
	 console.log('Selected event: ');
	 console.log(event);
	 });*/

	var baseMap = this;
	/*  Get information about the AUVdeployments when presented as WMS
	deploymentSelection = new OpenLayers.Control.WMSGetFeatureInfo({
		url: this.wmsUrl,
		title: 'Zoom to deployments by clicking',
		layers: [this.layers['AUVdeploymentsWMS']],
		queryVisible: true,
		output: "object",
		infoFormat: "application/vnd.ogc.gml",
		eventListeners: {
			nogetfeatureinfo: function(event) {console.log('No queryable layers found');},
			getfeatureinfo: function(event) {
			// parse the deployment ids
			console.log('Deployment clicked')
			console.log(event)
			var deploymentIds = [];
			for (var i=0, len=event.features.length; i<len; i++) {
				var fid = event.features[i].fid.split(".");
				deploymentIds[i] = fid[1];
			}
			// update the map bounds to zoom into the deployment
			if (deploymentIds.length > 0) {
				baseMap.updateMapForDeployments(deploymentIds);
				}
			}
		}
	});
	this.mapInstance.addControl(deploymentSelection);
	deploymentSelection.activate();*/
	
	// select individual poses by clicking the map
	poseSelection = new OpenLayers.Control.WMSGetFeatureInfo({
		url : this.wmsUrl,
		title : 'Identify features by clicking',
		layers : [this.layers['AUVworkset']],
		queryVisible : true,
		output : "object",
		infoFormat : "application/vnd.ogc.gml",
		eventListeners : {
			nogetfeatureinfo : function(event) {
				console.log('No queryable layers found');
			},
			beforegetfeatureinfo : function(event) {
			  // build CQL_FILTER param list from active info layer CQL_FILTER params
			  var layers = this.findLayers();
			  var filter = "";
			  for (var i = 0, len = layers.length; i < len; i++) {
			    if (i > 0) 	filter += ";";
			    var lyrCQL = layers[i].params.FILTER
			    if (lyrCQL != null) {
			      filter += lyrCQL;
			    }
			  }
			  console.log(filter);
			  this.vendorParams = { 'FILTER': filter	};
			},
			getfeatureinfo : function(event) {
				console.log(event);
				var imageNames =  [];
				if (event.features.length > 0)
				{
//					fid = event.features[0].fid.split(".");
//					console.log(fid[1]);
                    fid = event.features[0].attributes.id;

				    baseMap.updateMapForSelectedImage(fid);
				    globalstate.imid = fid;
				}
			}
		}
	});
	this.mapInstance.addControl(poseSelection);
	poseSelection.activate();

	// select individual poses by clicking the map
	/*    poseSelectionIMOS = new OpenLayers.Control.WMSGetFeatureInfo({
	 url: "http://geoserver.imos.org.au/geoserver/wms",
	 title: 'Identify features by clicking',
	 layers: [this.layers['IMOSAUVimages']],
	 queryVisible: true,
	 output: "object",
	 infoFormat: "application/vnd.ogc.gml",
	 eventListeners: {
	 nogetfeatureinfo: function(event) {console.log('No queryable layers found');},
	 getfeatureinfo: function(event) {
	 console.log('Selected IMOS image pose')
	 console.log(event);
	 }
	 }
	 });
	 this.mapInstance.addControl(poseSelectionIMOS);
	 poseSelectionIMOS.activate();

	 // select individual poses by clicking the map
	 poseSelectionIMOSdeployments = new OpenLayers.Control.WMSGetFeatureInfo({
	 url: "http://geoserver.imos.org.au/geoserver/wms",
	 title: 'Identify features by clicking',
	 layers: [this.layers['IMOSAUVdeployments']],
	 queryVisible: true,
	 output: "object",
	 infoFormat: "application/vnd.ogc.gml",
	 eventListeners: {
	 nogetfeatureinfo: function(event) {console.log('No queryable layers found');},
	 getfeatureinfo: function(event) {
	 console.log('Selected IMOS deployment')
	 console.log(event);
	 }
	 }
	 });
	 this.mapInstance.addControl(poseSelectionIMOSdeployments);
	 poseSelectionIMOSdeployments.activate();
	 */

	format = 'image/png';

	/**
	 * Given a filter array, this function will query the WMS and update the map
	 * with the result.
	 *
	 * @param filterArray
	 */
	this.updateMapUsingFilter = function(filterArray, layerName) {
		console.log("Applying map filter");

		var filter_logic = new OpenLayers.Filter.Logical({
			type : OpenLayers.Filter.Logical.AND,
			filters : filterArray
		});
		var xml = new OpenLayers.Format.XML();
		var new_filter = xml.write(this.filter_1_1.write(filter_logic));

		var layer = this.layers[layerName];
		layer.params['FILTER'] = new_filter;
		layer.redraw();

	};


	/**
	 * Removes all layers from the map
	 */
	this.clearMap = function() {
		this.currentFilter = [];
	}


	// Toggle the control tool
	this.toggleControl = function(element) {
		console.log('Toggling control to:'+element.value)
		for (var key in this.controls) {
			var control = this.controls[key];
			if (element.value == key && element.checked) {
				console.log('Turning on:'+key)
				control.activate();
			} else {
				console.log('Turning off:'+key)
				control.deactivate();
			}
		}
	};

	/**
	 *
	 * Will take a collectionId and update the collection layer and
	 * set the map boundaries
	 *
	 * @param collectionId
	 */
    this.updateMapForCollection = function (clid, layername) {
        var filter_array = [];

        if (this.mapInstance.getLayersByName(layername).length == 0)
            this.mapInstance.addLayer(this.layers[layername]);

        filter_array.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "collection_id",
            value: clid
        }));

        this.updateMapUsingFilter(filter_array, layername);
        
        this.browseEnabled = false;
    };


	/**
	 *
	 * Will take an imageId and update the currentImage layer and
	 * set the map boundaries
	 *
	 * @param imageId
	 */
	this.updateMapForSelectedImage = function(imageId) {
        if (this.mapInstance.getLayersByName('AUVcurrentImage').length == 0)
            this.mapInstance.addLayer(this.layers['AUVcurrentImage']);

        var mapInstance = this.mapInstance;
		var geographic = this.geographic;
		var mercator = this.mercator;
		var apistring = '/api/dev/pose/?images=' + imageId, imginfo = {};
		$.ajax({
			dataType : "json",
			async: false, // prevent asyncronous mode to allow setting of variables within function
			url: apistring,
			success: function(img) {
				if (img.objects.length > 0) {
					imginfo = img.objects[0];
				}
			}
		});
		var position = imginfo.position.replace(/.*\(|\)/gi, '').split(' ');
		mapInstance.getLayersByName('AUVcurrentImage')[0].clearMarkers();
		var location = new OpenLayers.LonLat(position[0], position[1]).transform(geographic, mercator);
		var marker = new OpenLayers.Marker(location);
		var size = new OpenLayers.Size(25, 40);
		var offset = new OpenLayers.Pixel(-(size.w / 2), -size.h);
		marker.icon = new OpenLayers.Icon('/static/images/map-marker-md.png', size, offset);
		marker.icon.size = size;
		marker.icon.offset = offset;
		//var icon = new OpenLayers.Icon('/static/images/Map-Marker-Chartreuse.png', size, offset);
		//var icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
		mapInstance.getLayersByName('AUVcurrentImage')[0].addMarker(marker);

		//        $.ajax({
		//            dataType: "json",
		//            async: false,  // prevent asyncronous mode to allow setting of variables within function
		//            url: '/api/dev/simplepose/'+imageId,
		//            success: function (img) {
		//console.log(img);
		//            var imgPoint = img.position.replace("(", "").replace(")", "").split(" ");
		//            console.log(imgPoint);
		//            console.log(mapInstance.getLayersByName('AUVcurrentImage')[0]);
		//            console.log(mapInstance.layers);
		//            mapInstance.getLayersByName('AUVcurrentImage')[0].clearMarkers();
		//
		//            var location = new OpenLayers.LonLat(imgPoint[1], imgPoint[2]).transform(geographic, mercator);
		//            var size = new OpenLayers.Size(21,25);
		//            var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
		//            var icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
		//            mapInstance.getLayersByName('AUVcurrentImage')[0].addMarker(new OpenLayers.Marker(location), icon);
		//            }
		//        });
		/*
		 this.layers['AUVcurrentImage'] = new OpenLayers.Layer.Vector("AUVcurrentImage",
		 {
		 strategies: [new OpenLayers.Strategy.Fixed(),
		 new OpenLayers.Strategy.Cluster()],
		 protocol: new OpenLayers.Protocol.WFS({
		 url: "http://"+geoserverurl+":8080/geoserver/wfs",
		 featureType: "catamidb_images",
		 featureNS: "http://catami"
		 }),
		 styleMap: new OpenLayers.StyleMap({
		 "default": style,
		 "select": {
		 fillColor: "#8aeeef",
		 strokeColor: "#32a8a9"
		 }
		 }),
		 projection: this.geographic,
		 //filter: new OpenLayers.Filter.Comparison({
		 //    type: OpenLayers.Filter.Comparison.EQUAL_TO,
		 //    property: "id",
		 //    value: imageId
		 //}),
		 },
		 {maxScale: 150000});
		 this.layers['AUVcurrentImage'].redraw();

		 console.log(this.layers['AUVcurrentImage']);
		 */
		/*
		 var filter_array = [];

		 filter_array.push(new OpenLayers.Filter.Comparison({
		 type: OpenLayers.Filter.Comparison.EQUAL_TO,
		 property: "id",
		 value: imageId
		 }));

		 this.updateMapUsingFilter(filter_array, 'AUVcurrentImage');

		 // now update the map bounds.
		 //this.updateMapBounds("id="+imageId, this.deploymentExtentUrl);
		 */
	};

	/**
	 * Update the map for a set of deployments
	 **/
	this.showDeployments = function(deploymentIds) {
        var mapInstance = this.mapInstance;
        if (mapInstance.getLayersByName('AUVdeployments').length == 0) {
            mapInstance.addLayer(this.layers['AUVdeployments']);
            this.layers['AUVdeployments'].events.register(
                'loadend', this,
                function (evt) {
                    if (this.browseEnabled == true) {
                        console.log('AUVdeployments loaded');
                        console.log(evt.object);
                        console.log(evt.object.getDataExtent());
                        mapInstance.zoomToExtent(evt.object.getDataExtent());
                    }
                }
            );
            var highlightCtrl = new OpenLayers.Control.SelectFeature(this.layers['AUVdeployments'], {
                hover: true,
                highlightOnly: true,
                renderIntent: "temporary",
                handlerOptions: {'delay': 5000},
                /*
                 * could update some information about the highlighted deployments
                 */
                eventListeners: {
                    //beforefeaturehighlighted: report,
                    featurehighlighted: showDeploymentInfo
                }
            });
            this.mapInstance.addControl(highlightCtrl);
            highlightCtrl.activate();

            var select = new OpenLayers.Control.SelectFeature(
                this.layers['AUVdeployments']
            );
            mapInstance.addControl(select);
            select.activate();
            this.layers['AUVdeployments'].events.on({"featureselected": zoomToDeployments});
        }

		//this.updateMapBounds("deployment_ids="+deploymentIds, this.deploymentExtentUrl)
	};

    this.showImages = function () {
        if (this.mapInstance.getLayersByName('AUVimages').length == 0) {
            this.mapInstance.addLayer(this.layers['AUVimages']);
           
            /**
             * Controls for navigation, box and polygon selection of features
             **/
            this.controls = {
                navigation: new OpenLayers.Control.Navigation(),
                box: new OpenLayers.Control.DrawFeature(this.layers['AUVpolygonSelection'],
                        OpenLayers.Handler.RegularPolygon,
                        {
                        	handlerOptions: {irregular: true},
                        	eventListeners: {
                        		"featureAdded": function (event) {
                        			console.log(event)
                        			var filterBounds = event.feature.geometry.getBounds().clone();
                        			filterBounds.transform(baseMap.mercator, baseMap.geographic);
					                var filter = new OpenLayers.Filter.Spatial({
					                   type: OpenLayers.Filter.Spatial.BBOX,
					                   property: "position",
					                   value: filterBounds})
						            baseMap.updateMapForSelection(filter, 'AUVimagesSelection');
                       			}
                        	}
                        }),
                /*polygon: new OpenLayers.Control.SLDSelect(
                    OpenLayers.Handler.Polygon,
                    {
                        displayClass: 'olControlSLDSelectPolygon',
                        layers: [this.layers['AUVimages']],
                     }
                 )*/
                   
            };

            for (var key in this.controls) {
                this.mapInstance.addControl(this.controls[key]);
                console.log(this.controls[key])
            }

            showFeatureInfo = new OpenLayers.Control.WMSGetFeatureInfo({
                url: this.wmsUrl,
                title: 'Identify features by hovering',
                //layers : [this.layers['AUVworkset']],
                layers: [this.layers['AUVimages']],
                queryVisible: true,
                hover: true,
                output: "object",
                infoFormat: "application/vnd.ogc.gml",
                maxFeatures: 1,
                eventListeners: {
                    getfeatureinfo: function (event) {
                        console.log('hover getFeatureInfo')
                        console.log(event);

                        if (event.features.length > 0) {
//                    fid = event.features[0].fid.split(".");
//					imginfo = thlist.getImageInfo(fid[1]);
                            fid = event.features[0].attributes.id;
                            imginfo = thlist.getImageInfo(fid);
                            console.log(imginfo);

                            var infoid = '#map-info';
                            $(infoid).html(event.text);
                            var position = imginfo.position.replace(/.*\(|\)/gi, '').split(' ');
                            var parseWebLocation = imginfo.images[0].web_location.split('/');
                            var imgName = parseWebLocation[parseWebLocation.length - 1];
                            $(infoid).html('<b>Image ID:</b> ' + imginfo.id);//+' (<a href="javascript:void(0)" onclick="$(\'#map-nav\').tab(\'show\')">show image</a>)');
                            $(infoid).append('<br><b>Name:</b> ' + imgName);
                            $(infoid).append('<br><b>Timestamp:</b> ' + imginfo.date_time);
                            $(infoid).append('<br><b>Depth:</b> ' + imginfo.depth + ' m');
                            $(infoid).append('<br><b>LAT:</b> ' + position[1]);
                            $(infoid).append('<br><b>LON:</b> ' + position[0]);
                            if (imginfo.measurements.length > 0) {
                                for (var i = 0; i < imginfo.measurements.length; i++) {
                                    $(infoid).append('<br><b>' + imginfo.measurements[i].name + ': </b>' + imginfo.measurements[i].value + ' ' + imginfo.measurements[i].units);
                                }
                            }

                            var thumbid = '#map-thumb';
                            console.log(imginfo.images[0]);
                            $(thumbid).html('<a class="fancybox" href="'+imginfo.images[0].web_location+'" title="'+imgName+'"><img src="' + imginfo.images[0].thumbnail_location + '"/></a>')
                            $('.fancybox').fancybox();
                        }
                    }
                }
            });
            this.mapInstance.addControl(showFeatureInfo);
            showFeatureInfo.activate();
        }
    };
	
	 /**
	 *
	 * Will take a Bounding Box filter and update the image selection layer
	 *
	 * @param BBOXfilter
	 */
    this.updateMapForSelection = function(BBOXfilter, layername) {
        if (this.mapInstance.getLayersByName(layername).length == 0)
            this.mapInstance.addLayer(this.layers[layername]);
        if (this.mapInstance.getLayersByName('AUVpolygonSelection').length == 0) {
            this.mapInstance.addLayer(this.layers['AUVpolygonSelection']);
            this.layers['AUVimagesSelection'].events.on({
                "visibilitychanged": function(evt) {
        			this.setVisibility(evt.object.getVisibility());
    			},
                scope: this.layers['AUVpolygonSelection']});
        }

        // push the new selection box onto the list of currently active filters
        this.AUVimageSelectionFilter.push(BBOXfilter);
        console.log(this.AUVimageSelectionFilter);
        // update the seleciton layer to reflect the new selection
		var filter_logic = new OpenLayers.Filter.Logical({
			type : OpenLayers.Filter.Logical.OR,
			filters : this.AUVimageSelectionFilter
		});
				
		var filterCombined = this.ExploreFilter;
		filterCombined.push(filter_logic)
		
		console.log(filterCombined)

        this.updateMapUsingFilter(filterCombined, layername)
        //this.updateMapUsingFilter(this.AUVimageSelectionFilter, layername)
		/*var xml = new OpenLayers.Format.XML();
		var new_filter = xml.write(this.filter_1_1.write(filter_logic));

		var layer = this.layers[layername];
		layer.params['FILTER'] = new_filter;
		layer.redraw();*/
		
    };
	/**
	 * Zoom to encompass all deployments
	 */    



	/**
	 * Will update the bounds of the map given a bounds criteria and url
	 * for querying the extent.  The bounds criteria can be:
	 *  'deployment_ids=[]'
	 *  'collection_id=[]'
	 */
	this.updateMapBounds = function(boundsCriteria, extentUrl) {
		var mapInstance = this.mapInstance;
		var geographic = this.geographic;
		var mercator = this.mercator;
		$.ajax({
			type : "POST",
			url : extentUrl,
			data : boundsCriteria,
			success : function(response, textStatus, jqXHR) {
				var boundsArr = response.extent.replace("(", "").replace(")", "").split(",");
				var bounds = new OpenLayers.Bounds();
				bounds.extend(new OpenLayers.LonLat(boundsArr[0], boundsArr[1]));
				bounds.extend(new OpenLayers.LonLat(boundsArr[2], boundsArr[3]));
				mapInstance.zoomToExtent(bounds.transform(geographic, mercator));
			}
		});
	};

	/**
	 *
	 * Used for constructing the filter in which to run on the WMS
	 *
	 * @param minDepth
	 * @param maxDepth
	 * @param minAltitude
	 * @param maxAltitude
	 * @param minTemperature
	 * @param maxTemperature
	 * @param minSalinity
	 * @param maxSalinity
	 * @returns {Array}
	 */
	this.createExploreFilterArray = function(depth_range,
											 altitude_range,
//											 tempretature_range,
//											 salinity_range,
											 deploymentIds) {

		this.ExploreFilter = [
			new OpenLayers.Filter.Comparison({
				type : OpenLayers.Filter.Comparison.BETWEEN,
				property : "depth",
				lowerBoundary : depth_range[0],
				upperBoundary : depth_range[1]
			}), 
			new OpenLayers.Filter.Comparison({
				type : OpenLayers.Filter.Comparison.BETWEEN,
				property : "altitude",
				lowerBoundary : altitude_range[0],
				upperBoundary : altitude_range[1]
			}), 
//			new OpenLayers.Filter.Comparison({
//				type : OpenLayers.Filter.Comparison.BETWEEN,
//				property : "temperature",
//				lowerBoundary : minTemperature,
//				upperBoundary : maxTemperature
//			}),
//			new OpenLayers.Filter.Comparison({
//				type : OpenLayers.Filter.Comparison.BETWEEN,
//				property : "salinity",
//				lowerBoundary : minSalinity,
//				upperBoundary : maxSalinity
//			})
		];

        /*
		var deploymentIdFilter = [];
		for (var i = 0; i < deploymentIds.length; i++) {
			deploymentIdFilter.push(new OpenLayers.Filter.Comparison({
				type : OpenLayers.Filter.Comparison.EQUAL_TO,
				property : "deployment_id",
				value : deploymentIds[i]
			}));
		}

		deploymentIdFilter = new OpenLayers.Filter.Logical({
			type : OpenLayers.Filter.Logical.OR,
			filters : deploymentIdFilter
		});

		filter.push(deploymentIdFilter);
        */

        //console.log(this.ExploreFilter);
		return this.ExploreFilter;
	};    
};



