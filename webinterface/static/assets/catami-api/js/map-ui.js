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

function BaseMap(geoserverUrl, deploymentExtentUrl, collectionExtentUrl, globalstate) {
	console.log("Function BaseMap");
	//Map view code to get moved out later.
	//prep some data we need to use to display the points
	this.wmsUrl = geoserverUrl + '/wms';
	this.wfsUrl = geoserverUrl + '/wfs';
	//this.wmsLayerName = wmsLayerName;
	this.deploymentExtentUrl = deploymentExtentUrl;
	this.collectionExtentUrl = collectionExtentUrl;
	this.hostname = location.hostname;

	this.filtLayername = "filter layer";
	this.filtLayerColor = "00FF00";

//	this.browseEnabled = true;
	this.isInitialised = false;

	/* Setting up the projection details here, so that 4326 projected data can be displayed on top of
	 * base layers that use the google projection */
	this.projection = {
		geographic : new OpenLayers.Projection("EPSG:4326"),
		mercator : new OpenLayers.Projection("EPSG:900913")
	};

	this.filters = {
        featranges : [],
		BBoxes : [],
        deployments : []
	}

	//this.AUVimageSelectionFilter = [];
	//this.ExploreFilter = [];

	var baseMap = this;

	/**
	 *
	 * @param $mapobj
	 */
	this.init = function($mapobj, $mappanel) {
		console.log("Function init");
		// set map object
		this.$mapobj = $mapobj;
        this.$mappanel = $mappanel;
		// set map to be full height
		this.setFullHeight();
		//map extent based on projections
		//var world_extent = new OpenLayers.Bounds(-180, -89, 180, 89).transform(baseMap.projection.geographic, baseMap.projection.mercator);
		// create map instance
		this.mapInstance = new OpenLayers.Map($mapobj.get(0), {
			projection : baseMap.projection.mercator,
			//displayProjection: geographic,
			units : "m",
			//maxExtent: world_extent,
            maxResolution : 156543.0399,
			numZoomLevels : 25,
            center : [14431310.938232, -3013453.4026953],
            controls : [new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.LayerSwitcher({'ascending' : true}),
                //new OpenLayers.Control.Permalink(),
                new OpenLayers.Control.ScaleLine(),
                //new OpenLayers.Control.Permalink('permalink'),
                new OpenLayers.Control.MousePosition(),
                new OpenLayers.Control.OverviewMap(),
                new OpenLayers.Control.KeyboardDefaults({autoActivate:false})]
		});
		// add baselayer
//		this.mapInstance.addLayer(new OpenLayers.Layer.OSM(null, null, {
//			resolutions : [156543.03390625, 78271.516953125, 39135.7584765625, 19567.87923828125, 9783.939619140625, 4891.9698095703125, 2445.9849047851562, 1222.9924523925781, 611.4962261962891, 305.74811309814453, 152.87405654907226, 76.43702827453613, 38.218514137268066, 19.109257068634033, 9.554628534317017, 4.777314267158508, 2.388657133579254, 1.194328566789627, 0.5971642833948135, 0.25, 0.1, 0.05],
//			serverResolutions : [156543.03390625, 78271.516953125, 39135.7584765625, 19567.87923828125, 9783.939619140625, 4891.9698095703125, 2445.9849047851562, 1222.9924523925781, 611.4962261962891, 305.74811309814453, 152.87405654907226, 76.43702827453613, 38.218514137268066, 19.109257068634033, 9.554628534317017, 4.777314267158508, 2.388657133579254, 1.194328566789627, 0.5971642833948135],
//			transitionEffect : 'resize',
//			isBaseLayer : true,
//			minZoomLevel : 1,
//			maxZoomLevel : 25,
//			numZoomLevels : 25,
//			sphericalMercator : true
//		}));


        this.mapInstance.addLayer(new OpenLayers.Layer.Google("Google Map", {
            numZoomLevels: 20
        }, {minScale: 150000}));
        this.mapInstance.addLayer(new OpenLayers.Layer.Google("Google Satellite", {
            type: google.maps.MapTypeId.SATELLITE,
            numZoomLevels: 20
        }, {maxScale: 150000}));
        this.mapInstance.addLayer(new OpenLayers.Layer.XYZ("ESRI Ocean Basemap",
            "http://services.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/${z}/${y}/${x}",
            {
                sphericalMercator: true,
                isBaseLayer: true,
                numZoomLevels: 20,
                wrapDateLine: true
            }
        ));
//        this.mapInstance.addLayer(new OpenLayers.Layer.WMS(
//            "baselayer",
//            "http://tilecache.emii.org.au/cgi-bin/tilecache.cgi/1.0.0/",
//            {
//                layers: 'HiRes_aus-group' ,
//                wrapDateLine: true,
//            }
//        ));

		this.isInitialised = true;
	}

	this.setFullHeight = function() {
		// console.log("Function setFullHeight");
        this.$mapobj.height($(window).height() - this.$mapobj.offset().top);
        this.$mappanel.parent().height($(window).height() - this.$mappanel.parent().offset().top);
        //this.$mapobj.width($(window).width()- this.$mappanel.parent().width());
    }
    /**
     * Given a filter array, this function will query the WMS and update the map
     * with the result.
     *
     * @param filterArray
     */
    this.updateMapUsingFilter = function (filterArray, layerName) {
		console.log("Function updateMapUsingFilter");
        console.log("\tApplying map filter to layer: '"+ layerName + "'");

        var filter_1_1 = new OpenLayers.Format.Filter({
            version: "1.1.0"
        });

        var filter_logic = new OpenLayers.Filter.Logical({
            type: OpenLayers.Filter.Logical.AND,
            filters: filterArray
        });
        var xml = new OpenLayers.Format.XML();
        var new_filter = xml.write(filter_1_1.write(filter_logic));

        var layer = this.mapInstance.getLayersByName(layerName)[0];
        //        var layer = this.layers[layerName];
        layer.params['FILTER'] = new_filter;

        layer.redraw();
		console.log("END updateMapUsingFilter");
    };



	/**
	 * Will take a collectionId and update the collection layer and
	 * set the map boundaries
	 *
	 * @param clid
	 * @param layername
	 * @param layersettings {markersize,markercol,isclickable}
	 */
	this.updateMapForCollection = function(clid, layername, layersettings) {
			console.log("Function updateMapForCollection");
		// overide default settings with layersettings
		var settings = {
			markersize : 5,
			markercol : "000000",
			isclickable : false
		};
		$.extend(settings, layersettings);
		//console.log(settings);

		// Create layer if it does not exist
		if (this.mapInstance.getLayersByName(layername).length == 0) {
			//this.mapInstance.addLayer(this.layers[layername]);

			this.mapInstance.addLayer(new OpenLayers.Layer.WMS(layername, this.wmsUrl, {
				layers : 'catami:collection_images',
				format : 'image/gif',
				transparent : 'TRUE',
				sld : "http://" + baseMap.hostname + "/geoserverSimplestyle?name=catami:collection_images&colour=" + settings.markercol + "&size=" + settings.markersize
				//transitionEffect: 'resize'
			}, {
				tileOptions: {maxGetUrlLength: 2048}, 
				isBaseLayer : false
			}));
		}

		// apply collection id filter
		var filter_array = [];
		filter_array.push(new OpenLayers.Filter.Comparison({
			type : OpenLayers.Filter.Comparison.EQUAL_TO,
			property : "collection_id",
			value : clid
		}));

		this.updateMapUsingFilter(filter_array, layername);

//		this.browseEnabled = false;

		if (settings.isclickable) {
			// select individual poses by clicking the map
			var poseSelection = new OpenLayers.Control.WMSGetFeatureInfo({
				url : this.wmsUrl,
				title : 'Identify features by clicking',
				layers : this.mapInstance.getLayersByName(layername),
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
							if (i > 0)
								filter += ";";
							var lyrCQL = layers[i].params.FILTER
							if (lyrCQL != null) {
								filter += lyrCQL;
							}
						}
						console.log(filter);
						this.vendorParams = {
							'FILTER' : filter
						};
					},
					getfeatureinfo : function(event) {
						console.log(event);
						var imageNames = [];
						if (event.features.length > 0) {
							var fid = event.features[0].attributes.id;
							baseMap.updateMapForSelectedImage(fid);
							globalstate.imid = fid;
						}
					}
				}
			});
			this.mapInstance.addControl(poseSelection);
			poseSelection.activate();
		}
	};

	/**
	 *
	 * Will take an imageId and update the currentImage layer and
	 * set the map boundaries
	 *
	 * @param imageId
	 */
	this.updateMapForSelectedImage = function(imageId, layername) {
			console.log("Function updateMapForSelectedImage");
		layername = (( typeof layername !== 'undefined') ? layername : "Current Image");
		if (this.mapInstance.getLayersByName(layername).length == 0) {
			//this.layers[layername] = new OpenLayers.Layer.Markers(layername);
			this.mapInstance.addLayer(new OpenLayers.Layer.Markers(layername));
		}

		var imginfo = thlist.getImageInfo(imageId);

		this.mapInstance.getLayersByName(layername)[0].clearMarkers();
		var position = imginfo.position.replace(/.*\(|\)/gi, '').split(' ');
		var location = new OpenLayers.LonLat(position[0], position[1]).transform(baseMap.projection.geographic, baseMap.projection.mercator);
		var marker = new OpenLayers.Marker(location);
		var size = new OpenLayers.Size(25, 40);
		var offset = new OpenLayers.Pixel(-(size.w / 2), -size.h);
		marker.icon = new OpenLayers.Icon('/static/images/map-marker-md.png', size, offset);
		//		marker.icon.size = size;
		//		marker.icon.offset = offset;
		//var icon = new OpenLayers.Icon('/static/images/Map-Marker-Chartreuse.png', size, offset);
		//var icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
		this.mapInstance.getLayersByName(layername)[0].addMarker(marker);
	};

	/**
	 * Update the map for a set of deployments
	 **/
	this.showDeployments = function(layername) {
		console.log("Function showDeployments");
		console.log("  layername=" +layername)
		
		var mapInstance = this.mapInstance;
		
		// Create the layer if it does not already exist
		layername = (( typeof layername !== 'undefined') ? layername : "Deployment origins");
		if (mapInstance.getLayersByName(layername).length == 0) {

            function style(fill,stroke,size, op){

                return new OpenLayers.Style({
                    pointRadius: "${radius}",
                    fillColor: fill,//"#ffcc66",
                    //fillOpacity: op,
                    strokeColor: stroke,
                    strokeOpacity: 1,
                    strokeWidth : "${stroke}",
                    fillOpacity: (typeof op !== 'undefined') ? op : "${opacity}"
                }, {
                    context: {
                        stroke : function(feature) {
                        	return (feature.attributes.count > 1) ? 3 : 1.5;
                        },
                        opacity: function(feature) {
                            return (feature.attributes.count > 1) ? 0.6 : 0.4;
                        },
                        radius: function (feature) {
                            return Math.round(5 * Math.log(feature.attributes.count + 1) + size);
                        }
                    }
                });

            }

            var deploymentlayer = new OpenLayers.Layer.Vector(layername, {
                strategies: [
                    new OpenLayers.Strategy.Fixed(),
                    new OpenLayers.Strategy.Cluster()
                ],
                protocol: new OpenLayers.Protocol.WFS({
                    url: this.wfsUrl,
                    featureType: "catamidb_deployment"
                    //featureNS : "http://catami"
                }),
                styleMap: new OpenLayers.StyleMap({
                    "default": style("#000000", "#000000", 4),
                    "select": style("#cccccc", "#000000", 4),
                    "highlight": style("#000000", "#ffffff", 8, 1)
                }),
                projection: baseMap.projection.geographic
            });

            mapInstance.addLayer(deploymentlayer);
            deploymentlayer.events.register('loadend', this, function(evt) {
				//if (this.browseEnabled == true) {
					mapInstance.zoomToExtent(evt.object.getDataExtent());
				//}
			});
			var highlightCtrl = new OpenLayers.Control.SelectFeature(deploymentlayer, {
				hover : true,
				highlightOnly : true,
				renderIntent : "highlight",
				handlerOptions : {
					//'delay' : 5000
				},
				/*
				 * could update some information about the highlighted deployments
				 */
				eventListeners : {
					//beforefeaturehighlighted: report,
					featurehighlighted : showDeploymentInfo
				}
			});
			this.mapInstance.addControl(highlightCtrl);
			highlightCtrl.activate();

			var select = new OpenLayers.Control.SelectFeature(deploymentlayer);
			mapInstance.addControl(select);
			select.activate();
            deploymentlayer.events.on({
				"featureselected" : zoomToDeployments
			});
		}
		console.log("END showDeployments");
		//this.updateMapBounds("deployment_ids="+deploymentIds, this.deploymentExtentUrl)
	};
	/**
	 * Event function for when we hover over a deployment
	 */
	function showDeploymentInfo(event) {
		console.log("Function showDeploymentInfo");

		if (event.feature.cluster.length == 0) {
			return;
		}
		
		var $depinfo,
            depid = 0,
            checked = '',
            filtdepids = [],
            selecteddpls = '',
            otherdpls = '';

        console.log(event);


        baseMap.$dplinfo.html('');

        // add selected deployments
        for (var i = 0; i < baseMap.filters.deployments.length; i++) {
            $depinfo = getDeploymentCheckbox(baseMap.filters.deployments[i].id, baseMap.filters.deployments[i].name, 'checked');
            baseMap.$dplinfo.append($depinfo);
            filtdepids.push(baseMap.filters.deployments[i].id); // create array of selected deployment ids
        }

        // add other unselected deployments
        for (var i = 0, len = event.feature.cluster.length; i < len; i++) {
            depid = event.feature.cluster[i].fid.split('.')[1];
            if ($.inArray(depid, filtdepids) < 0) {
                //$depinfo = $('<a href="javascript:void(0)">' + event.feature.cluster[i].data.short_name + '</a>');
                $depinfo = getDeploymentCheckbox(depid, event.feature.cluster[i].data.short_name, '');
                baseMap.$dplinfo.append($depinfo);
            }
		}


        baseMap.$imginfo.parent().hide();
        baseMap.$dplinfo.parent().show();
        baseMap.$infopane.show(200);

	}

    function getDeploymentCheckbox (id,name,checked) {
		console.log("Function getDeploymentCheckbox");
		
        var $depinfo = $('<label class="checkbox"><input type="checkbox" value="' + id + '" '+checked+' > ' + name + '</label>');
        $depinfo.data('depid', id);
        $depinfo.click(function () {
            if ($(this).find('input')[0].checked) $('#deploymentSelect').multiselect('select', $(this).data('depid'));
            else $('#deploymentSelect').multiselect('deselect', $(this).data('depid'));
        });

        return $depinfo;
    }

	/**
	 * Zoom to a deployment
	 **/
	function zoomToDeployments(event) {
			console.log("Function zoomToDeployments");
		// parse the deployment ids
		//baseMap.test = event;
		var deploymentIds = [];
		for (var i = 0, len = event.feature.cluster.length; i < len; i++) {
			var fid = event.feature.cluster[i].fid.split(".");
			// TODO: this needs to be fixed to extract the ID from the layer
			deploymentIds[i] = fid[1];
		}
		// update the map bounds to zoom into the deployment
		if (deploymentIds.length > 0) {
			baseMap.updateMapBounds("deployment_ids=" + deploymentIds, baseMap.deploymentExtentUrl);
			//(deploymentIds);
		}
		// hide the popup if it was visible
		//this.setFullHeight = ide();

		//var f = event.feature;
		//console.log(event.feature);
	}



	this.showImages = function(layername) {
			console.log("Function showImages");
		layername = (( typeof layername !== 'undefined') ? layername : "Images");
		if (this.mapInstance.getLayersByName(layername).length == 0) {
			var ImagesLayer = this.mapInstance.addLayer(new OpenLayers.Layer.WMS(layername, this.wmsUrl, {
				//layers : 'catami:catamidb_images',
				layers : 'catamidb_images',
				format : 'image/gif',
				transparent : 'TRUE',
				sld : "http://" + baseMap.hostname + "/geoserverstyle?prop=depth&min=35.0&max=50.0"
				
			}, { tileOptions: {maxGetUrlLength: 2048}, //transitionEffect: 'resize'
				minScale : 150000
			}));

			var showFeatureInfo = new OpenLayers.Control.WMSGetFeatureInfo({
				url : this.wmsUrl,
				title : 'Identify features by clicking',
				//layers : [this.layers['AUVworkset']],
				layers : baseMap.mapInstance.getLayersByName(layername),
				queryVisible : true,
				hover : false,
				output : "object",
				infoFormat : "application/vnd.ogc.gml",
				maxFeatures : 6,
				eventListeners : {
					getfeatureinfo : function(event) {
					console.log("showImages:");
					console.log(event);

                        if (event.features.length > 0) {
                            baseMap.$imginfo.html('');
                            var fid, $thumb;
                            for (var i=0 ; i < event.features.length ; i++ ) {
                                fid = event.features[i].attributes.img_id;
                                $thumb = getImageInfo(fid);
                                baseMap.$imginfo.append($thumb);
                            }
                            //baseMap.$imginfo.append("<br><br>");
                            baseMap.$imginfo.parent().show();
                            baseMap.$infopane.show(200);
                        }
                    }
				}
			});
			this.mapInstance.addControl(showFeatureInfo);
			showFeatureInfo.activate();
		}
	};


    function getImageInfo (id) {
		// console.log("Function getImageInfo");
        var imginfo = thlist.getImageInfo(id);
        //console.log(imginfo);

        var position = imginfo.position.replace(/.*\(|\)/gi, '').split(' ');
        var parseWebLocation = imginfo.images[0].web_location.split('/');
        var imgName = parseWebLocation[parseWebLocation.length - 1];

        var infotxt = '<b>Name:</b> ' + imgName;
        infotxt += '<br><b>ID:</b> ' + imginfo.id;
        infotxt += '<br><b>Depth:</b> ' + Math.round(imginfo.depth * 100) / 100 + ' m';
        infotxt += '<br><b>LAT:</b> ' + Math.round(position[1] * 1000000) / 1000000;
        infotxt += '<br><b>LON:</b> ' + Math.round(position[0] * 1000000) / 1000000;
        infotxt += '<br><b>TS:</b> ' + imginfo.date_time.split('.')[0];
        // display other sensor measurements
//                                if (imginfo.measurements.length > 0) {
//                                    for (var i = 0; i < imginfo.measurements.length; i++) {
//                                        $(infoid).append('<br><b>' + imginfo.measurements[i].name + ': </b>' + imginfo.measurements[i].value + ' ' + imginfo.measurements[i].units);
//                                    }
//                                }

        var $thumb = $('<a href="' + imginfo.images[0].web_location + '" title="' + infotxt + '" ><img src="' + imginfo.images[0].thumbnail_location + '"/></a> ');
        $thumb.tooltip({trigger: "hover", html: true, placement: 'right'});
        $thumb.fancybox();
		
		// console.log("END getImageInfo");
        return $thumb;
    }

	/**
	 *
	 * 
	 *
	 * 
	 */
	this.showSelectedImages = function(selectlayername, nocreate, color) {
		console.log("Function showSelectedImages: " + selectlayername);
		
        nocreate = (( typeof nocreate !== 'undefined') ? nocreate : false);
		console.log("\tColor="+color);
		color = (( typeof color !== 'undefined') ? color : "0000FF");
		
		var //selectlayername = baselayername + ' (selected)',
            selectedpanelid = 'mapselected',
            $selectedpanel;

		// check if there is a selection
		// if (this.getSelectFilters() == null) {
			// if there is no selection, remove selection layer if it exists
//			if (this.mapInstance.getLayersByName(selectlayername).length != 0) {
//                //this.mapInstance.getLayersByName(selectlayername)[0].hide();
//				this.mapInstance.getLayersByName(selectlayername)[0].destroy();
//                this.mapInstance.removeControl(this.mapInstance.getControlsBy('title','ClickImg')[0]);
//			}
	        //$('#' + selectedpanelid).hide();
			// console.log("\tNo filters selected");
	// 	} 
		
		if (this.mapInstance.getLayersByName(selectlayername).length == 0 && !nocreate) {
			// add the selection layer if required
			var imglayer = new OpenLayers.Layer.WMS(selectlayername, this.wmsUrl, {
                layers: 'catami:catamidb_images',
                format: 'image/gif',
                transparent: 'TRUE',
                // sld: "http://" + baseMap.hostname + "/geoserverstyle?prop=depth&min=35.0&max=50.0"
                sld : "http://" + baseMap.hostname + "/geoserverSimplestyle?name=catami:catamidb_images&colour="+color+"&size=5"
            }, {//tileOptions: {maxGetUrlLength: 2048},
                transitionEffect: 'resize',//, minScale: 150000}), // selection layer should always be visible
				tileOptions: {maxGetUrlLength: 2048}, 
				isBaseLayer : false
            });
            this.mapInstance.addLayer(imglayer);
			console.log("\tCreated new layer: " + selectlayername);
//            var highlightLayer = new OpenLayers.Control.GetFeature({
//                protocol: OpenLayers.Protocol.WFS.fromWMSLayer(imglayer),
//                box: true,
//                hover: true,
//                multipleKey: "shiftKey",
//                toggleKey: "ctrlKey"
//            });
//            this.mapInstance.addControl(highlightLayer);
//            highlightLayer.activate();

            var showFeatureInfo = new OpenLayers.Control.WMSGetFeatureInfo({
                url: baseMap.wmsUrl,
                title: 'ClickImg',
                layers: baseMap.mapInstance.getLayersByName(selectlayername),
                queryVisible: true,
                hover: false,
                output: "object",
                infoFormat: "application/vnd.ogc.gml",
                maxFeatures: 9,
                eventListeners: {
			    	nogetfeatureinfo : function(event) {
						console.log('No queryable layers found');
			    	},
					getfeatureinfo: function (event) {
						console.log('getfeatureinfo got ' + event.features.length + ' features');
						console.log(event);
						console.log(baseMap.mapInstance.getLayersByName(selectlayername));
	                    if (event.features.length > 0) {
	                        baseMap.$imginfo.html('');
	                        var fid, $thumb;
	                        for (var i = 0; i < event.features.length; i++) {
	                            fid = event.features[i].attributes.img_id;
	                            console.log(fid);
	                            $thumb = getImageInfo(fid);
	                            baseMap.$imginfo.append($thumb);
	                        }
	                        baseMap.$imginfo.parent().show();
	                        baseMap.$infopane.show(200);
	                    }
					}
                }
            });

            baseMap.mapInstance.addControl(showFeatureInfo);
            showFeatureInfo.activate();
		}




        if (this.mapInstance.getLayersByName(selectlayername).length > 0) {

            var filterCombined = this.getFilters();
            this.updateMapUsingFilter(filterCombined, selectlayername);
        }
        this.updateSelectionInfo();
        //$selectedpanel = $('#' + selectedpanelid + '-content');
        //this.updateSelectionInfo(baseMap.$selectedpanel);
        //$('#' + selectedpanelid).show();


		//this.updateMapUsingFilter(this.AUVimageSelectionFilter, layername)
		/*var xml = new OpenLayers.Format.XML();
		 var new_filter = xml.write(this.filter_1_1.write(filter_logic));

		 var layer = this.layers[layername];
		 layer.params['FILTER'] = new_filter;
		 layer.redraw();*/
		console.log("END showSelectedImages");
		console.log("");
		console.log("");
	};




	/**
	 * Will update the bounds of the map given a bounds criteria and url
	 * for querying the extent.  The bounds criteria can be:
	 *  'deployment_ids=[]'
	 *  'collection_id=[]'
	 */
	this.updateMapBounds = function(boundsCriteria, extentUrl) {
		// console.log("Function updateMapBounds");
		
		var mapInstance = this.mapInstance;
		//var geographic = baseMap.projection.geographic;
		//var mercator = baseMap.projection.mercator;
		$.ajax({
			type : "POST",
			url : extentUrl,
			data : boundsCriteria,
			success : function(response, textStatus, jqXHR) {
				var boundsArr = response.extent.replace("(", "").replace(")", "").split(",");
				var bounds = new OpenLayers.Bounds();
				bounds.extend(new OpenLayers.LonLat(boundsArr[0], boundsArr[1]));
				bounds.extend(new OpenLayers.LonLat(boundsArr[2], boundsArr[3]));
				mapInstance.zoomToExtent(bounds.transform(baseMap.projection.geographic, baseMap.projection.mercator));
			}
		});
	};

	/**
	 *
	 */
    this.getSelectFilters = function () {
		console.log("Function getSelectedFilters");
        var selectfilters = [];

        // Get deployment filters
        console.log("\tDeployments selected: ");
        if (this.filters.deployments.length > 0) {
            for (var i=0 ; i < this.filters.deployments.length; i++) {
				console.log("\t\t" + this.filters.deployments[i].id);
                selectfilters.push(new OpenLayers.Filter.Comparison({
                    type: OpenLayers.Filter.Comparison.EQUAL_TO,
                    property: "deployment_id",
                    value: parseInt(this.filters.deployments[i].id)
                }));
            }
        } else { // dirty hack - if no deployments selected, then make an invalid filter
			console.log("\t\tNONE");
            selectfilters.push(new OpenLayers.Filter.Comparison({
                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                property: "deployment_id",
                value: -1
            }));
        }

        console.log('\tSelect filters:');
        console.log(selectfilters);
		
		console.log("END getSelectedFilters");
        if (selectfilters.length > 0) return new OpenLayers.Filter.Logical({
            type: OpenLayers.Filter.Logical.OR,
            filters: selectfilters });
        else 
          	return null;
    }
	/**
	 * Creates a filter based on the ranges set and bounding boxes drawn
	 */
    this.getRangeFilters = function () {
		console.log("Function getRangeFilters");
        var filters = [],
            bboxfilters = [];

        // get range filters
        for (var key in this.filters.featranges) {
            //var filtvalues = this.filters.featranges[key]();
            var filtvalues = this.filters.featranges[key];
            //console.log(filtvalues);
            filters.push(new OpenLayers.Filter.Comparison({
                type: OpenLayers.Filter.Comparison.BETWEEN,
                property: key,
                lowerBoundary: filtvalues[0],
                upperBoundary: filtvalues[1]
            }));
        }

        // get BBox filters
        for (var i = 0; i < this.filters.BBoxes.length; i++) {
            bboxfilters.push(new OpenLayers.Filter.Spatial({
                type: OpenLayers.Filter.Spatial.BBOX,
                property: "position",
                value: this.filters.BBoxes[i]
            }));
            //console.log(bboxes);
        }

        if (bboxfilters.length > 0) 
			filters.push(new OpenLayers.Filter.Logical({
            	type: OpenLayers.Filter.Logical.OR,
            	filters: bboxfilters
        	}));

		console.log("END getRangeFilters");
        if (filters.length > 0) return filters;
        else return null;
    }

	/**
	 * Returns the selected filters, if any. Otherwise return an empty list.
	 */
    this.getFilters = function () {
		console.log("Function getFilters");
        var filters = [],
            rangefilters = this.getRangeFilters(),
            selectfilters = this.getSelectFilters();


        if (rangefilters != null) {
            console.log('\tadd range filters')
            filters = rangefilters;
        }
        if (selectfilters != null) {
            console.log('\tadd select filters');
            filters.push(selectfilters);
        }

		
        console.log(filters);
		console.log("END getFilters");
        return filters;
    }





    this.addBBoxSelect = function ($container, layername) {
		console.log("Function addBBoxSelect");
        var $bboxbtn = $('<button type="button" class="btn btn-default pull-right btn-sm" title="Draw a bounding box around the images you would like to add to your selection."><i class="icon-crop"></i> BOX</button>');

        layername = this.filtLayername;
		layercolor = this.filtLayerColor;
		
        $bboxbtn.click(function (){
             var layernameBoundingBoxes = 'Bounding boxes';
        
            if (baseMap.mapInstance.getLayersByName(layernameBoundingBoxes).length == 0) {
            	baseMap.mapInstance.addLayer(new OpenLayers.Layer.Vector(layernameBoundingBoxes, null))
	    		var bbctrl =  new OpenLayers.Control.DrawFeature( 
					baseMap.mapInstance.getLayersByName(layernameBoundingBoxes)[0], OpenLayers.Handler.RegularPolygon, {
						handlerOptions: {
						    irregular: true
						},
						eventListeners: {
						    "featureadded": function (event) {
								var filterBounds = event.feature.geometry.getBounds().clone();
								filterBounds.transform(baseMap.projection.mercator, baseMap.projection.geographic);
								baseMap.filters.BBoxes.push(filterBounds);
								// baseMap.showSelectedImages(layername);
								baseMap.showSelectedImages(layername, false, layercolor);
								toggleBBoxSelect(bbctrl, $bboxbtn,true);
						    }
						}
				    }
				);
	    
				baseMap.mapInstance.addControl(bbctrl);
            }

            toggleBBoxSelect(bbctrl, $bboxbtn);
        });
        $bboxbtn.tooltip({trigger:'hover'});

        $container.append("<br>Crop selected deployments:",$bboxbtn);
        //baseMap.mapcontrols.$bboxbtn = $bboxbtn;
    }

    function toggleBBoxSelect (bbctrl, $bboxbtn, forcedeselect) {
			console.log("Function toggleBBoxSelect");
        forcedeselect = (( typeof forcedeselect !== 'undefined') ? forcedeselect : false);
        if ($bboxbtn.hasClass('active') || forcedeselect) {
            bbctrl.deactivate();
            //baseMap.mapcontrols.nav.activate();
            $bboxbtn.removeClass('active');
        }
        else {
            bbctrl.activate();
            //baseMap.mapcontrols.nav.deactivate();
            $bboxbtn.addClass('active');
        }
    }

	/**
	 *
	 */
    this.addDeploymentSelect = function ($container, layername) {
		console.log("Function addDeploymentSelect: " + layername);
		
        var $dplselect = $('<select multiple id="deploymentSelect" name="deploymentSelect"> </select>');


        addCampaignsToSelect($dplselect);
//        addDeploymentsToSelect($dplselect);


        $container.append($dplselect);

        //$dplselect.jAutochecklist({width: $container.innerWidth(), absolutePosition:true, popupSizeDelta: 150});
        $dplselect.multiselect({
            maxHeight: 400,
            buttonWidth: $container.innerWidth(),
            enableCaseInsensitiveFiltering: true,
            buttonText: function (options, select) {
                if (options.length == 0) return '<i class="icon-th-list"></i> Select deployment(s)';
                else if (options.length == 1) return '<i class="icon-th-list"></i> '+ options.length+' deployment selected';
                else return '<i class="icon-th-list"></i> ' + options.length + ' deployments selected';
            },
            onChange: function (element, checked) {
                var id,name,$dplinfo;
                baseMap.$dplinfo.find("input").prop('checked',false);  // deselect deployment property
                baseMap.filters.deployments = [];
                if ($dplselect.val() != null) {
                    baseMap.updateMapBounds("deployment_ids=" + $dplselect.val(), baseMap.deploymentExtentUrl);
                    for (var i =0 ; i < $dplselect.val().length ; i++) {
                        id = $dplselect.val()[i];
                        name = $dplselect.find("option[value='" + id + "']").text();
                        baseMap.filters.deployments.push({
                            id: id,
                            name: name
                        });
                        //console.log($dplselect.find("option[value='" + $dplselect.val()[i] + "']").text());

                        // check selected in info panel, otherwise add to info panel
                        $dplinfo = baseMap.$dplinfo.find("input[value='" + id + "']");
                        $dplinfo.prop('checked', true);
//                        if ($dplinfo.length <= 0) $dplinfo.prop('checked', true);
//                        else baseMap.$dplinfo.prepend(getDeploymentCheckbox(id,name,'checked'));
                    }
                }
                
                //baseMap.showSelectedImages(layername, baseMap.getSelectFilters());
                //baseMap.showSelectedImages(layername, baseMap.getFilters());
                baseMap.showSelectedImages(layername,false);
            }
        });

        // Configure multiselect popout
        var $popout = $container.find('.multiselect-container');

        // set height
        $popout.css({'max-height': baseMap.$mapobj.innerHeight()});
        // set position
        $popout.css({position:'absolute',
            top: Math.max(-$popout.outerHeight()/2 , baseMap.$mapobj.offset().top - $popout.parent().offset().top),
            left: -$popout.outerWidth(),
            'z-index': 9999,
            width: $popout.outerWidth()
        });


//        $dplselect.change(function() {
//            baseMap.filters.deployments = $dplselect.val();
//            baseMap.showSelectedImages(layername);
//            baseMap.updateMapBounds("deployment_ids=" + $dplselect.val(), baseMap.deploymentExtentUrl);
//        });

        //baseMap.mapcontrols.$dplselect = $dplselect;

    }

    function addCampaignsToSelect($dplselect) {
		console.log("Function addCampainsToSelect");
		
        $.ajax({
            dataType: "json",
            async: false,
            url: '/api/dev/campaign/?limit=0&order_by=short_name',
            success: function (cmp) {
                var $cmpgrp, dplcount;
                if (cmp.objects.length > 0) {
                    for (var i = 0; i < cmp.objects.length; i++) {
                        $cmpgrp = $('<optgroup></optgroup>');
                        dplcount = addDeploymentsToSelect($cmpgrp, cmp.objects[i].id);
                        $cmpgrp.attr('label',cmp.objects[i].short_name + ' ('+ dplcount+')');
                        $dplselect.append($cmpgrp);
                    }
                }
            }
        });
    }

    function addDeploymentsToSelect ($dplselect, cmpid) {
		console.log("Function addDeploymentsToSelect");
		
        var cmpstr = ( typeof cmpid !== 'undefined') ? '&campaign=' + cmpid : '';
        var dplcount = 0;
        $.ajax({
            dataType: "json",
            async: false,
            url: '/api/dev/deployment/?limit=0&order_by=short_name'+ cmpstr,
            success: function (dpl) {
                if (dpl.objects.length > 0) {
                    for (var i = 0; i < dpl.objects.length; i++) {
                        $dplselect.append('<OPTION VALUE="' + dpl.objects[i].id + '">' + dpl.objects[i].short_name + '</option>');
                        dplcount ++;
                    }
                }
                else {
                    $dplselect.append('<OPTION VALUE="" disabled="true">No dpeloyments found</option>');
                }
            }
        });
        return dplcount;
    }



    /**
     *
     * @param $container
     * @param panelinfo
     * @returns {*|jQuery|HTMLElement} panel content element
     */
    this.addPanel = function ($container, panelinfo) {
		//console.log("Function addPanel");
		
        // check if panel exists, otherwise create it
        if ($container.find('#'+ panelinfo.id).length <= 0) {
            var $panel = $('<div id="' + panelinfo.id + '" class="map-panel og-panel"></div>');

            $panel.html($('<div class="navbar"><i class="' + panelinfo.icon + ' navbar-brand">&nbsp;' + panelinfo.title + '</i></div>'));

            // Add close link and handle behaviour to hide panel
            if (panelinfo.closeable) {
                $panel.find('.navbar').append('<ul class="nav navbar-nav navbar-right"><li><a href="javascript:void(0)" class="hide-link"><i class="icon-remove"></i></a></li></ul>');
                $panel.find('.hide-link').click(function () {
                    // hide panel
                    $panel.hide();
                    // check if parent has visible children, otherwise hide parent pane
                    var hideparent = true;
                    $panel.parent().children().each(function (i, ch) {
                        if ($(ch).is(':visible')) hideparent = false;
                    });
                    if (hideparent) $panel.parent().hide();
                });
            }

            var $panelcontent = $('<div id="' + panelinfo.id + '-content" class="map-panel-content"></div>');
            $panel.append($panelcontent);
            $container.append($panel);

            return $panelcontent;
        }
        else {
            return $container.find('#' + panelinfo.id+'-content');
        }

    }



    this.addInfoPane = function ($container, panelid) {
		//console.log("Function addInfoPane");
        var $infopane = $('<div id="'+ panelid+'" class="og-dragpane map-pane-draggable"></div>');

        this.$imginfo = this.addPanel($infopane, {id:'img-info',icon:'icon-picture',title:'Nearby images', closeable:true});
        this.$dplinfo = this.addPanel($infopane, {id: 'dpl-info', icon: 'icon-list', title: 'Deployment list', closeable: true});
        this.$infopane = $infopane;

        $container.append($infopane);

        // make infopane draggable
        $infopane.draggable({
            scroll: false,
            containment: "body"
        });

        // hide panels initially
        this.$infopane.hide();
        this.$imginfo.parent().hide();
        this.$dplinfo.parent().hide();
    }


	/**
	 * Creates a range filter and adds it to the given container
	 */
    this.addRangeFilter = function ($container,$infocontainer,layername,feature,params) {
		console.log("Function addRangeFilter: "+feature);

		layercolor = this.filtLayerColor;		
		
        var $slider = $('<div id="'+ feature+'-slider" style="margin-left:10px; margin-right:10px;"></div>'),
            infoid = feature + '-range',
            $info = $('<span id="' + infoid + '"></span>'),
            filtertitle = feature[0].toUpperCase() + feature.substring(1) + ' range: ', // capitalise first letter
            $btn = $('<span id="'+infoid+'-button" class="btn btn-xs" >' + feature + ' filter &nbsp;<a href="javascript: void(0);"><i class="icon-remove-sign"></i><a/></span><br>');
        
			
		// create slider
        $slider.data('infoid', '#'+infoid);
        $slider.slider({
            range: true,
            min: params.range[0],
            max: params.range[1],
            step: params.step,
            values: params.range,
            slide: function (event, ui) {
                $($slider.data('infoid')).html(ui.values[ 0 ] +' - '+ ui.values[ 1 ]);
            },
            change: function (event, ui) {
                currMinVal = ui.values[0];
		        currMaxVal = ui.values[1];
		        minVal = $slider.slider("option", "min");
		        maxVal = $slider.slider("option", "max");
				console.log("min/max="+minVal + "/"+ maxVal);
				console.log("current="+currMinVal + "/"+currMaxVal);
				
				// Update slider text
                $($slider.data('infoid')).html(ui.values[ 0 ] +' - '+ ui.values[ 1 ]);
				
				if (currMinVal == minVal && currMaxVal == maxVal) {
					$btn.hide();
					// and delete from the featranges
					delete baseMap.filters.featranges[feature];
				}
		        // create button in side panel
		        else {
					// TODO: is not updating correctly
					// should tooltip be destroyed and recreated? check out best way to update bootstrap tooltip title
					$btn.show();
					// Add to featranges
					baseMap.filters.featranges[feature] = $slider.slider("values");
		        }
				
				
				// Update map
                baseMap.showSelectedImages(layername, false, layercolor);
            }
        });
		
		// Create button
		$btn.hide();
		$btn.find("a").click(function () {
	        minVal = $slider.slider("option", "min");
	        maxVal = $slider.slider("option", "max");
            $slider.slider("option", "values", [minVal, maxVal]);
        });
		$btn.tooltip({
			html: true, 
			placement: 'left', 
			trigger:'hover',
			title: function() {
		        var values = $slider.slider("values");
				var rangeinfo = feature + ": " + values[0] + "-" + values[1];
				return rangeinfo;
			}
		});
		$btn.tooltip("show");
		
		// Add to containers
        $container.append(filtertitle, $info, params.unit, $slider,'<br>');
        $($slider.data('infoid')).html($slider.slider("values", 0) +' - '+  $slider.slider("values", 1));
		$infocontainer.append($btn);

	}
	/**
	 * Creates a date filter and adds it to the given container
	 */
	this.addDateFilter = function ($container,$infocontainer,layername,feature,params) {
			console.log("Function addDateFilter");

			layercolor = this.filtLayerColor;		


            var $fromdate = $('<input type="text" name="fromdate" placeholder="From date" id="fromdate" size="8">'),
                $todate   = $('<input type="text" name="todate"   placeholder="To date"   id="todate"   size="8">'),
                filtertitle = "Date range:",
				infoid = feature,
				$btn = $('<span id="'+infoid+'-button" class="btn btn-xs" >' + feature + ' filter &nbsp;<a href="javascript: void(0);"><i class="icon-remove-sign"></i><a/></span><br>');
			
            $fromdate.datepicker({
                changeMonth: true,
                changeYear: true,
                dateFormat: 'yy-mm-dd',
				minDate: params.from,
				maxDate: params.to,
                onClose: function (dateText, inst) {
					if( dateText != "" ) {
	                    // restrict the end date
	                    $todate.datepicker("option", "minDate", dateText);
						
						// Get min/max and current selected
						var to = new Date(params.to);
						var from = new Date(params.from);
						var selTo = $todate.datepicker("getDate");
						var selFrom = $fromdate.datepicker("getDate");
						// If at the ends remove filter
						if (from.getDate()==selFrom.getDate() && 
							from.getMonth()==selFrom.getMonth() && 
							from.getYear() == selFrom.getYear() && 
							to.getDate()==selTo.getDate() && 
							to.getMonth()==selTo.getMonth() && 
							to.getYear() == selTo.getYear() ) {
							delete baseMap.filters.featranges[feature];
							$btn.hide();
						}
						else {
							baseMap.filters.featranges[feature] = [$fromdate.val() , $todate.val()];
							$btn.show();
						}
						
						// Update map
						baseMap.showSelectedImages(layername, false, layercolor);
					}
                }
            });
            $fromdate.datepicker('setDate', params.from);
			
            $todate.datepicker({
                changeMonth: true,
                changeYear: true,
                dateFormat: 'yy-mm-dd',
				minDate: params.from,
				maxDate: params.to,
                onClose: function (dateText, inst) {
					if( dateText != "") {
	                    // restrict the start date
	                    $fromdate.datepicker("option", "maxDate", selectedDate);
	                    
						// Get min/max and current selected
						var to = new Date(params.to);
						var from = new Date(params.from);
						var selTo = $todate.datepicker("getDate");
						var selFrom = $fromdate.datepicker("getDate");
						// If at the ends remove filter
						if (from.getDate()==selFrom.getDate() && 
							from.getMonth()==selFrom.getMonth() && 
							from.getYear() == selFrom.getYear() && 
							to.getDate()==selTo.getDate() && 
							to.getMonth()==selTo.getMonth() && 
							to.getYear() == selTo.getYear()) {
							delete baseMap.filters.featranges[feature];
							$btn.hide();
						}
						else {
							baseMap.filters.featranges[feature] = [$fromdate.val() , $todate.val()];
							$btn.show();
						}
						
						// Update map
						baseMap.showSelectedImages(layername, false, layercolor);
					}
                },
				onChangeMonthYear: function(year, month, inst) {
					console.log("here");
				}
            });
            $todate.datepicker('setDate', params.to);


			// Create button
			$btn.hide();
			$btn.find("a").click(function () {
				$fromdate.datepicker('setDate', params.from);
				$todate.datepicker('setDate', params.to);
	        });
			$btn.tooltip({
				html: true, 
				placement: 'left', 
				trigger:'hover',
				title: function() {
			        var values = [$fromdate.val() , $todate.val()];
					var rangeinfo = feature + ": " + values[0] + " to " + values[1];
					return rangeinfo;
				}
			});
			$btn.tooltip("show");
			
			// Add to containers
            var $filtcont = $('<span class="pull-right"></span>').append($fromdate, ' to ', $todate);
            $container.append(filtertitle, $filtcont,'<br>');
			$infocontainer.append($btn);
    }

    // TODO: this is a bit ugly - remove code duplication
    /**
     *
     * @param $container (optional - needs to be set on first call)
     */
    this.updateSelectionInfo = function ($container) {
		//console.log("Function updateSelectionInfo");
		return;
		
    if ( typeof $container !== 'undefined') baseMap.$selectedpanel = $container;

        var rangeinfo = '',
            bboxinfo = '',
            dplinfo = '',
            dplids = [],
            showcreatbtn = false,
            $newclform = $('#clform');

        // baseMap.$selectedpanel.html('');		
		

		// Show number of deployments and their info
        if (baseMap.filters.deployments != null) {
            for (var i = 0; i < baseMap.filters.deployments.length; i++) {
                dplinfo += baseMap.filters.deployments[i].name + '<br>';
                dplids.push(baseMap.filters.deployments[i].id)
                showcreatbtn = true;
            }
            if (dplinfo != '') {
				// TODO: Why <a>??
                baseMap.$selectedpanel.append($('<a href="#_" class="btn btn-xs" title="' + dplinfo + '">Deployments <span class="badge">' + i + '</span></a> ').popover({html: true, placement: 'topRight', trigger: 'hover'}));
                $newclform.find('#id_deployment_ids').val(dplids.join(','));
            }
        }
		
		// Show the range filters		// 
		//         var i = 0;
		//         for (var key in baseMap.filters.featranges) {
		//             rangeinfo = key + ': ' + baseMap.filters.featranges[key][0] + ' to ' + baseMap.filters.featranges[key][1] + '<br>';
		//             // $newclform.find('#id_'+key).val(baseMap.filters.featranges[key][0] + ',' + baseMap.filters.featranges[key][1])
		// 	        if (rangeinfo != '')  {
		// 		
		//         var $rangebtn = $('<span class="btn btn-xs" title="' + rangeinfo + '">' + key + ' filter &nbsp;<a href="javascript: void(0);"><i class="icon-remove-sign"></i><a/></span>');
		// 
		//         $rangebtn.find("a").click(function (){
		// 			console.log("filter before: " + baseMap.filters.featranges);
		// 			console.log("removing: " + key);
		// 			delete baseMap.filters.featranges[key];
		// 			
		// 			baseMap.
		// 			
		// 			console.log("filter after : " + baseMap.filters.featranges);
		// 			baseMap.showSelectedImages();
		// 		});
		//         $rangebtn.tooltip({html: true, placement: 'topRight', trigger:'hover'});
		// 
		//         //baseMap.$selectedpanel.append($rangebtn);
		// 		//baseMap.$selectedpanel.append($('<a class="btn btn-xs" title="' + rangeinfo + '" id="range_'+i+'" onclick="this.removeRangeFilter('+i+');" >' + key + ' filter &nbsp;<span class="badge">X</span></a> ').popover({html: true, placement: 'topRight', trigger:'hover'}));
		// 	}
		//             i++;
		//         }
		// 
		// // Show bounding boxes
		//         var bboxarr = [];
		//         var bbox = [];
		//         for (var i = 0; i < baseMap.filters.BBoxes.length; i++) {
		//             bbox = [baseMap.filters.BBoxes[i].left , baseMap.filters.BBoxes[i].bottom , baseMap.filters.BBoxes[i].right , baseMap.filters.BBoxes[i].top];
		//             bboxinfo += 'Box 1: ' + bbox.join(',') + '<br>';
		//             bboxarr.push(bbox.join(','));
		//             showcreatbtn = true;
		//         }
		//         if (bboxinfo != '') {
		//             baseMap.$selectedpanel.append($('<a class="btn btn-xs" title="' + bboxinfo + '">Bounding boxes <span class="badge">' + i + '</span></a> ').popover({html: true, placement: 'topRight', trigger: 'hover'}));
		//             $newclform.find('#id_bboxes').val(bboxarr.join(':'));
		//         }

        var $createbtn = $('<button class="btn btn-info disabled" style="width:100%; margin-top:10px;"><i class="icon-plus"></i> New Project with selection</button>');


        if (showcreatbtn && !globalstate.isloggedin) {
            baseMap.$selectedpanel.append('<div class="alert" style="margin-top:10px"><b>NOTE:</b> you need to be logged in to create a Project</div>');
        }
        else if (showcreatbtn && globalstate.isloggedin) {
            $createbtn.removeClass('disabled');
            $createbtn.click(function () {
                baseMap.openNewCollectionModal()
            });
        }
        else {
            baseMap.$selectedpanel.append('<div class="alert"><b>NOTE</b>: no images selected. Use the tools above add images to your project.</div>');
        }

        baseMap.$selectedpanel.append($createbtn);
		// console.log("END updateSelectionInfo");
    }

    this.openNewCollectionModal = function () {
		// console.log("Function openNewCollectonModal");

        $('#new-collection-modal').modal('show');
    }


	this.GetElementInsideContainer = function(containerID, childID) {
	    var elm = document.getElementById(childID);
	    var parent = elm ? elm.parentNode : {};
	    return (parent.id && parent.id === containerID) ? elm : {};
	}
	
	console.log("END BaseMap");
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

/*
 IMOSAUVdeployments : new OpenLayers.Layer.WMS("IMOSAUVdeployments",
 "http://geoserver.imos.org.au/geoserver/wms",
 {
 layers: 'helpers:auv_tracks',
 styles: '',
 projection: baseMap.projection.geographic,
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
 }),
 IMOSAUVimages : new OpenLayers.Layer.WMS("IMOSAUVimages",
 "http://geoserver.imos.org.au/geoserver/wms",
 {
 layers: 'helpers:auv_images_vw',
 styles: '',
 projection: baseMap.projection.geographic,
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
 }),
 */
