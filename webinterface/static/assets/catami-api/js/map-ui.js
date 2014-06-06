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

	//Map view code to get moved out later.
	//prep some data we need to use to display the points
	this.wmsUrl = geoserverUrl + '/wms';
	this.wfsUrl = geoserverUrl + '/wfs';
	//this.wmsLayerName = wmsLayerName;
	this.deploymentExtentUrl = deploymentExtentUrl;
	this.collectionExtentUrl = collectionExtentUrl;
	this.hostname = location.hostname;

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

    this.depOriginLayerName = '';
	this.depImageLayerName = '';
	this.selImageLayerName = '';
	this.filtImageLayerName = '';

	//this.AUVimageSelectionFilter = [];
	//this.ExploreFilter = [];

	var baseMap = this;




	/**
	 *
	 * @param $mapobj
	 */
	this.init = function($mapobj, $mappanel) {
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
			numZoomLevels : 10,
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
        }, {minScale: 150000}));
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

		OpenLayers.Control.ListenToClick = OpenLayers.Class(OpenLayers.Control, 
			{
			    defaultHandlerOptions: {
			        'single': true,
			        'pixelTolerance': 0,
			        'stopSingle': false
			    },

			    initialize: function(options) {
			        this.handlerOptions = OpenLayers.Util.extend(
			            {}, this.defaultHandlerOptions
			        );
			        OpenLayers.Control.prototype.initialize.apply(
			            this, arguments
			        ); 
			        this.handler = new OpenLayers.Handler.Click(
			            this, {
			                'click': this.onClick,
			            }, this.handlerOptions
			        );
			    }, 

			    onClick: function(evt) {
			        // Remove focus from the selected input box
					// $('input:focus').blur();
					$('#deploymentSelect').trigger('chosen:close');
			    }
			}
		);
		var ctmControl = new OpenLayers.Control.ListenToClick({
		    handlerOptions: {
		        'single': true,
		        'pixelTolerance': 0,
		        'stopSingle': false
		    }
		});
		this.mapInstance.addControl(ctmControl);
		ctmControl.activate();

		this.mapInstance.events.on({
//			"zoomend": function(e) {
				// This is not necessary as we are dealing with the loading of the image layers through the maxScale 
				//		option when the layers are created.
				// console.log( "this.getZoom(): " + baseMap.mapInstance.getZoom() );
// 				if( baseMap.mapInstance.getZoom() < 9 ) {
// 					baseMap.mapInstance.getLayersByName('Deployment images')[0].setVisibility(false);
// 					baseMap.mapInstance.getLayersByName('Selected images')[0].setVisibility(false);
// 				} else {
// 					baseMap.mapInstance.getLayersByName('Deployment images')[0].setVisibility(true);
// 					baseMap.mapInstance.getLayersByName('Selected images')[0].setVisibility(true);
// 				}
//			},
            "moveend" : function(e) {
                // The below code highlights the deployment origin markers if there is a deployment within this marker
                //  that has been selected
                // If no deployemnt has been selected
                if( $('#deploymentSelect').val() === null || typeof $('#deploymentSelect').val() === 'undefined' ) {
                    return;
                }
                // Get the deployment origin layer
                depLayer = baseMap.mapInstance.getLayersByName(baseMap.depOriginLayerName)[0];
                // Get the select control and clear all features
                selectCtrl = baseMap.mapInstance.getControlsBy('id', 'selectCtrl')[0];
                // Get IDs of selected deployments
                for( dSel = 0; dSel < $('#deploymentSelect').val().length; dSel++ ) {
                    id = ($('#deploymentSelect').val()[dSel]).toString();

                    // Get the deployment layer feature corresponding to this id
                    featInd = depLayer.features.map( function(e) {
                        f = [];
                        for(i = 0; i < e.cluster.length; i++)
                            f.push( e.cluster[i].fid.split('.')[1] );
                        return f;
                    }).map( function(e) {return e.indexOf(id);} ).map( function(e) { return e >= 0;} ).indexOf( true );

                    selectCtrl.highlight( depLayer.features[featInd] );
                }
            }
		});


		this.isInitialised = true;
	}

	this.setFullHeight = function() {
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
		// overide default settings with layersettings
		var settings = {
			markersize : 5,
			markercol : "000000",
			isclickable : false
		};
		$.extend(settings, layersettings);
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
						this.vendorParams = {
							'FILTER' : filter
						};
					},
					getfeatureinfo : function(event) {
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
	this.addDeployments = function(layername) {
		// Create the layer if it does not already exist
		if (this.mapInstance.getLayersByName(layername).length != 0) {
			console.log("WARNING: We should never end here!");
			return;
		}
        this.depOriginLayerName = layername;

		function style(fill,stroke,size, op) {
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

		var deploymentlayer = new OpenLayers.Layer.Vector( layername, {
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
					"default":   style("#000000", "#000000", 4),
//					"select": style("#cccccc", "#000000", 4),
                    "select":    style("#0000ff", "#ffffff", 4),
					"highlight": style("#000000", "#ffffff", 8, 1)
				}),
				projection: baseMap.projection.geographic
		});
        deploymentlayer.events.on({
			"featureselected" : zoomToDeployments,
            "loadend" : function(evt) {
                baseMap.mapInstance.zoomToExtent(evt.object.getDataExtent());
		    }
		});
		this.mapInstance.addLayer(deploymentlayer);

		
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
		highlightCtrl.id = "highlightCtrl";
		this.mapInstance.addControl(highlightCtrl);
		highlightCtrl.activate();

		var selectCtrl = new OpenLayers.Control.SelectFeature(deploymentlayer
            , {
            eventListeners : {
                featurehighlighted : function(event) {
                    console.log('selectCtrl featurehighlighted');
                    // Remove focus from the selected input box
                    //$('input:focus').blur();
                }
            }
            }
        );
        selectCtrl.id = "selectCtrl";
		this.mapInstance.addControl(selectCtrl);
		selectCtrl.activate();


	};
	/**
	 * Event function for when we hover over a deployment
	 */
	function showDeploymentInfo(event) {
		if (event.feature.cluster.length == 0) {
			return;
		}
		
		var $depinfo,
            depid = 0,
            checked = '',
            filtdepids = [],
            selecteddpls = '',
            otherdpls = '',
            i;

//        baseMap.$dplinfo.html('<ul></ul>');

        // Deselect all
        //$('#deploymentSelect :selected').prop('selected', false);

        // Disable everything that has not been selected
        $('#deploymentSelect option:not(selected)').each( function() { this.disabled = true; } );

        // add other unselected deployments
        for (i = 0, len = event.feature.cluster.length; i < len; i++) {
            depid = event.feature.cluster[i].fid.split('.')[1];
            // enable again
            $('#deploymentSelect').find('option[value="'+depid+'"]').prop('disabled', false);
		}

         // add selected deployments
        for (i = 0; i < baseMap.filters.deployments.length; i++) {
            depid = baseMap.filters.deployments[i].id;
            $('#deploymentSelect').find('option[value="'+depid+'"]').prop('selected', true);
            $('#deploymentSelect').find('option[value="'+depid+'"]').prop('disabled', false);
        }

        $('#deploymentSelect').trigger('chosen:updated');
        $('#deploymentSelect').trigger('chosen:open');
	    baseMap.updateChosenDropHeight();

//        baseMap.$imginfo.parent().hide();
//        baseMap.$dplinfo.parent().show();
//        baseMap.$infopane.show(200);

	}

	/**
	 * Zoom to a deployment
	 **/
	function zoomToDeployments(event) {
		// parse the deployment ids
		// baseMap.test = event;
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

        // Open the dropdown again
        $('#deploymentSelect').trigger('chosen:open');
	}



	this.showImages = function(layername) {
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
			showFeatureInfo.id = "showFeautreInfo";
			this.mapInstance.addControl(showFeatureInfo);
			showFeatureInfo.activate();
		}
	};


    function getImageInfo (id) {
        var imginfo = thlist.getImageInfo(id);
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
		
        return $thumb;
    }

	/**
	 * Creates a WMS layer
	 *
	 * layername: - Name of layer
	 * minscale: minimum scale at which it is shown
	 * visible: visibility at creation
	 * color: [optional] color of the markers
	 */
	this.addImageLayer = function(layername, minscale, visible, color) {
		color = (( typeof color !== 'undefined') ? color : "0000FF");
		
		// add the selection layer if required
		var imglayer = new OpenLayers.Layer.WMS(
			layername, 
			this.wmsUrl, 
			{
                layers: 'catami:catamidb_images',
                format: 'image/gif',
                transparent: 'TRUE',
                // sld: "http://" + baseMap.hostname + "/geoserverstyle?prop=depth&min=35.0&max=50.0"
                sld : "http://" + baseMap.hostname + "/geoserverSimplestyle?name=catami:catamidb_images&colour="+color+"&size=5"
        	}, 
			{
                transitionEffect: 'resize',
				tileOptions: {maxGetUrlLength: 2048}, 
				isBaseLayer : false,
				
				alwaysInRange: false,
				minScale: minscale,
				maxExtend: "auto",
				maxResolution: "auto"
            }
		);
		imglayer.events.on({
            // TODO: change to use a different method instead of this
			"loadstart": function(e) {
				// show a busy dialog
				show_busy("Updating selection...");
			},
			"loadend": function(e) {
				// hide the busy dialog
				hide_busy();
			}
//            ,
//			"visibilitychanged": function(e) {
//				// console.log("visibilitychanged");
//			},
//			"move": function(e) {
//				// console.log("move");
//			}
		})
		imglayer.setVisibility(visible);
        this.mapInstance.addLayer(imglayer);
		
        var showFeatureInfoCtrl = new OpenLayers.Control.WMSGetFeatureInfo(
		{
            url: baseMap.wmsUrl,
            title: 'ClickImg',
            layers: baseMap.mapInstance.getLayersByName(layername),
            queryVisible: true,
            hover: false,
            output: "object",
            infoFormat: "application/vnd.ogc.gml",
            maxFeatures: 9,
            eventListeners: 
			{
	    		nogetfeatureinfo : function(event) 
				{
                    
	    		},
				getfeatureinfo: function (event) 
				{
                	if (event.features.length > 0) {
                    	baseMap.$imginfo.html('');
                    	var fid, $thumb;
                        for (var i = 0; i < event.features.length; i++) {
                            fid = event.features[i].attributes.img_id;
                            $thumb = getImageInfo(fid);
                            baseMap.$imginfo.append($thumb);
                        }
                        baseMap.$imginfo.parent().show();
                        baseMap.$infopane.show(200);
                	}
				}
        	}
		});
		showFeatureInfoCtrl.id = "showFeatureInfoCtrl";
        this.mapInstance.addControl(showFeatureInfoCtrl);
        showFeatureInfoCtrl.activate();
	}

	/**
	 *
	 * 
	 *
	 * 
	 */
	this.showSelectedImages = function() {
		var deployments = [],
			numDeployments = this.filters.deployments.length;
			
		if( numDeployments == 0) {
			this.mapInstance.getLayersByName(this.selImageLayerName)[0].setVisibility(false);
			this.mapInstance.getLayersByName(this.filtImageLayerName)[0].setVisibility(false);
		}
		else {
			this.mapInstance.getLayersByName(this.selImageLayerName)[0].setVisibility(true);
			this.mapInstance.getLayersByName(this.filtImageLayerName)[0].setVisibility(true);
		
			// From the deployment filter get the selected deployments
	        // TODO: get info about deployments and use these to adjust the deployment color and filter ranges
			// Have a look at the way the image info is retrieved above in getfeatureinfo event
			for (var i=0 ; i < numDeployments; i++) {
				deployments.push( this.filters.deployments[i].id );
			}
		

		
			// Update the image and filter layers
			var filters = [];
			filters.push(this.getSelectFilters());
			this.updateMapUsingFilter(filters, this.selImageLayerName );
		
			filters = this.getFilters();
			this.updateMapUsingFilter(filters, this.filtImageLayerName );
		}
		
		// Update buttons
        this.updateSelectionInfo();
	};




	/**
	 * Will update the bounds of the map given a bounds criteria and url
	 * for querying the extent.  The bounds criteria can be:
	 *  'deployment_ids=[]'
	 *  'collection_id=[]'
	 */
	this.updateMapBounds = function(boundsCriteria, extentUrl) {
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
        var filter = [],
			selectfilters = [];

        // Get deployment filters
        if (this.filters.deployments.length > 0) {
			for (var i=0 ; i < this.filters.deployments.length; i++) {
                selectfilters.push(new OpenLayers.Filter.Comparison({
                    type: OpenLayers.Filter.Comparison.EQUAL_TO,
                    property: "deployment_id",
                    value: parseInt(this.filters.deployments[i].id)
                }));
            }
			
			filter = new OpenLayers.Filter.Logical({
	            	type: OpenLayers.Filter.Logical.OR,
	            	filters: selectfilters 
				});
        }
		// Should not be necessary any more 
		// else { // dirty hack - if no deployments selected, then make an invalid filter
//             selectfilters.push(new OpenLayers.Filter.Comparison({
//                 type: OpenLayers.Filter.Comparison.EQUAL_TO,
//                 property: "deployment_id",
//                 value: -1
//             }));
//         }

        if (selectfilters.length > 0) return filter;
        else return null;
    }
	/**
	 * Creates a filter based on the ranges set and bounding boxes drawn
	 */
    this.getRangeFilters = function () {
        var filters = [],
            bboxfilters = [],
            key;

        // get range filters
        for (key in this.filters.featranges) {
			var filtvalues = this.filters.featranges[key];
            filters.push(new OpenLayers.Filter.Comparison({
                type: OpenLayers.Filter.Comparison.BETWEEN,
                property: key,
                lowerBoundary: filtvalues[0],
                upperBoundary: filtvalues[1]
            }));
        }

        // get BBox filters
		for (key in this.filters.BBoxes) {
            bboxfilters.push(new OpenLayers.Filter.Spatial({
                type: OpenLayers.Filter.Spatial.BBOX,
                property: "position",
                value: this.filters.BBoxes[key]
            }));
        }

        if (bboxfilters.length > 0) {
			filters.push(new OpenLayers.Filter.Logical({
            	type: OpenLayers.Filter.Logical.OR,
            	filters: bboxfilters
        	}));
		}

        if (filters.length > 0) return filters;
        else return null;
    }

	/**
	 * Returns the selected filters, if any. Otherwise return an empty list.
	 */
    this.getFilters = function () {
        var filters = [],
            rangefilters = this.getRangeFilters(),
            selectfilters = this.getSelectFilters();

        if (selectfilters !== null) {
			
	        if (rangefilters != null) {
				filters = rangefilters;
	        }

			filters.push( selectfilters );
		}
		
        return filters;
    }

    this.updateDeploymentFilter = function() {

        this.filters.deployments = [];

        // Get the select DOM
        $dplselect = $('#deploymentSelect');
        if( $dplselect.val() !== null ) {
            // Loop through selected deployments in the multiselect
            for (var i=0 ; i < $dplselect.val().length ; i++) {
                id = $dplselect.val()[i];
                name = $dplselect.find("option[value='" + id + "']").text();
                this.filters.deployments.push({
                    id: id,
                    name: name
                });

                // TODO: move this code to an independent function
                // check selected in info panel, otherwise add to info panel
                $dplinfo = baseMap.$dplinfo.find("input[value='" + id + "']");
                $dplinfo.prop('checked', true);
            }
        }
    }

    this.updateChosenDropHeight = function() {
        // Hight of the results section
        resultsHeight = $('.chosen-results').height();
        // Hight of the map area
        mapHeight = $('#map-panel-container').height();
        // TODO: get the margin of the .chosen-drop from the css instead of coding it here (the 10px)
        $('.chosen-drop').css('max-height', mapHeight-10+'px');
        // The min height of 50px is for when the results section is empty because there was no matching to the text
        //  search
        $('.chosen-drop').height( Math.max(Math.min( mapHeight, resultsHeight), 50) );
    }

    this.addDeploymentSelectNew = function($container, $infocontainer, layername) {

        var $dplselect = $('<select multiple id="deploymentSelect" name="deploymentSelect"> </select>');
        addCampaignsToSelect($dplselect);
        $container.append($dplselect);

        $dplselect.chosen({
            placeholder_text_multiple: "Choose deployments",
            search_contains: true, // searches any place in the word. Set to false to only search from beginning of the word
            enable_split_word_search: false, // match the entire text
            no_results_text: "Oops, no deployments found:", // show if no results found
            display_selected_options: true, // Already selected options should be included (so we can deselect them)
            display_disabled_options: false, // Hide options that are diabled
            single_backstroke_delete: false, // first backspace selects, second one deletes
            width: $container.innerWidth()+'px' // set it here of set the width of the select box above
        });


        $dplselect.on('change', function (evt, params) {
            checked = (params.type === 'checked') ? true : false;
            unchecked = (params.type === 'unchecked') ? true : false;
            diveID = params.id;
            console.log('Dive #'+diveID+' is ' + (checked?'checked':(unchecked?'unchecked':'selected')));

            // Added/Removed
            if( params.type === 'checked' || params.type === 'unchecked') {
                baseMap.updateDeploymentFilter();
                baseMap.showSelectedImages();
                if( $dplselect.val() !== null ) {
                    baseMap.updateMapBounds("deployment_ids=" + $dplselect.val(), baseMap.deploymentExtentUrl);
                }
                // No deployments selected
                else {
                    console.log('all deployments deselected. zooming all the way out');
                    baseMap.mapInstance.getControlsBy('id', 'selectCtrl')[0].unselectAll();
                    baseMap.mapInstance.zoomToExtent(
                       baseMap.mapInstance.getLayersByName('Deployment origins')[0].getDataExtent() );
                }
            }
            // Zoom to selection
            else if( params.type === 'selected' ) {
                baseMap.updateMapBounds("deployment_ids=" + [diveID], baseMap.deploymentExtentUrl);
            }
            // The dive was de-selected
            else if($dplselect.val() !== null) {
                baseMap.updateMapBounds("deployment_ids=" + $dplselect.val(), baseMap.deploymentExtentUrl);
            }

        });

        $dplselect.on( 'chosen:showing_dropdown', function(evt, params) {
            baseMap.updateChosenDropHeight();
        });
        $dplselect.on( 'chosen:new_results', function(evt, params) {
            baseMap.updateChosenDropHeight();
        });
        $dplselect.on( 'chosen:no_results', function(evt, params) {
            baseMap.updateChosenDropHeight();
        });

    }


    /**
     * Given a multiselect object this AJAX function retrieves the available campains and adds these to the multiselect
     * TODO: how do we add a search icon to the multiselect??
     */
    function addCampaignsToSelect($dplselect) {
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
    /**
     * The actual function that appends a deployment to the multiselect object
     */
    function addDeploymentsToSelect ($dplselect, cmpid) {
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
    this.addPanel = function ($container, panelinfo, style) {
	    style = (( typeof style !== 'undefined') ? style : '');
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

            var $panelcontent = $('<div id="' + panelinfo.id + '-content" class="map-panel-content" style="'+style+'"></div>');
            $panel.append($panelcontent);
            $container.append($panel);

            return $panelcontent;
        }
        else {
            return $container.find('#' + panelinfo.id+'-content');
        }

    }



    this.addInfoPane = function ($container, panelid) {
        var $infopane = $('<div id="'+ panelid+'" class="og-dragpane map-pane-draggable"></div>');

        this.$imginfo = this.addPanel($infopane, {id:'img-info',icon:'icon-picture',title:'Nearby images', closeable:true});
        this.$dplinfo = this.addPanel($infopane, {id: 'dpl-info', icon: 'icon-list', title: 'Deployment list', closeable: true}, 'white-space: nowrap');	
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
        var $slider = $('<div id="'+feature+'-slider"></div>'),
			infoidMin = feature + '-rangeMin',
            infoidMax = feature + '-rangeMax',
            $infoMin = $('<input type="number" class="form-control input-sm" min="' +params.range[0]+ '" max="'+params.range[1]+'" name="infoMin" id="' + infoidMin + '" value="" size="8">'),
            $infoMax = $('<input type="number" class="form-control input-sm" min="' +params.range[0]+ '" max="'+params.range[1]+'" name="infoMax" id="' + infoidMax + '" value="" size="8">'),
            filtertitle = feature[0].toUpperCase() + feature.substring(1) + ' range: ', // capitalise first letter
            $btn = $('<span id="'+feature+'-button" class="btn btn-xs" >' + feature + ' filter &nbsp;<a href="javascript: void(0);"><i class="icon-remove-sign"></i><a/></span><br>');
        
			
		// create slider
		$slider.data('infoidMin', '#'+infoidMin);
		$slider.data('infoidMax', '#'+infoidMax);
        $slider.slider({
            range: true,
            min: params.range[0],
            max: params.range[1],
            step: params.step,
            values: params.range,
            slide: function (event, ui) {
				$($slider.data('infoidMin')).val(ui.values[ 0 ]);
		        $($slider.data('infoidMax')).val(ui.values[ 1 ]);
            },
            change: function (event, ui) {
                currMinVal = ui.values[0];
		        currMaxVal = ui.values[1];
		        minVal = $slider.slider("option", "min");
		        maxVal = $slider.slider("option", "max");
				
				// Update slider text
				$($slider.data('infoidMin')).val(currMinVal);
		        $($slider.data('infoidMax')).val(currMaxVal);
				
				// Remove filter value and hide button
				if (currMinVal == minVal && currMaxVal == maxVal) {
					$btn.hide();
					// and delete from the featranges
					delete baseMap.filters.featranges[feature];
				}
		        // create button in side panel
		        else {
					$btn.show();
					// Add to featranges
					baseMap.filters.featranges[feature] = $slider.slider("values");
		        }
				
				
				// Update map
                baseMap.showSelectedImages();
            }
        });
		// Event managers for the text fields
		$infoMin.change(function () {
		    currVal = $slider.slider("option", "values");
		    newMinVal = $($slider.data('infoidMin')).val();
		    $slider.slider("option", "values", [newMinVal, currVal[1]]);
		});

		$infoMax.change(function () {
		    currVal = $slider.slider("option", "values");
		    newMaxVal = Math.min($($slider.data('infoidMax')).val(), $slider.slider("option", "max"));
		    $slider.slider("option", "values", [currVal[0], newMaxVal]);
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
		var $filtcont = $('<div class="row"></div>').append($('<div class="col-sm-12"></div>').append($('<div class="input-group input-group-sm"></div>').append( 
			$infoMin, "<span class=input-group-addon>to</span>", $infoMax, "<span class=input-group-addon>"+params.unit+"</span>")));   
        $container.append($("<div style='margin: 10px;'></div>").append(filtertitle, "<br>", $filtcont, "<br>", $slider));
		$($slider.data('infoidMin')).val($slider.slider("values", 0));
		$($slider.data('infoidMax')).val($slider.slider("values", 1));
		$infocontainer.append($btn);

	}
	/**
	 * Creates a date filter and adds it to the given container
	 * TODO: I can't find a onChange event for the datepicker. This results in showing/hiding the filter button as well 
	 * 		as the filter variable in different places. Can we find a nicer event management?
	 */
	this.addDateFilter = function ($container,$infocontainer,layername,feature,params) {
        var $fromdate = $('<input type="text" class="form-control input-sm" name="fromdate" placeholder="From date" id="fromdate" size="8">'),
            $todate   = $('<input type="text" class="form-control input-sm" name="todate"   placeholder="To date"   id="todate"   size="8">'),
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
					baseMap.showSelectedImages();
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
                    $fromdate.datepicker("option", "maxDate", dateText);
                    
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
					baseMap.showSelectedImages();
				}
            }
        });
        $todate.datepicker('setDate', params.to);


		// Create button
		$btn.hide();
		$btn.find("a").click(function () {
			$fromdate.datepicker('setDate', params.from);
			$todate.datepicker('setDate', params.to);
			// There is no way to trigger a onChange on the date picker. As such I have to do this both places.
			// TODO: Can we figure a way to trigger onChange?
			// The following three lines should ideally not be here
			$btn.hide();
			delete baseMap.filters.featranges[feature];
			// Update map
			baseMap.showSelectedImages();
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
        // var $filtcont = $('<span></span>').append($fromdate, ' to ', $todate);
		var $filtcont = $('<div class="row"></div>').append($('<div class="col-sm-12"></div>').append($('<div class="input-group input-group-sm"></div>').append( 
			$fromdate, "<span class=input-group-addon>to</span>", $todate)));   
        $container.append($("<div style='margin: 10px;'></div>").append(filtertitle, "<br>", $filtcont));
		$infocontainer.append($btn);
    }
	/**
	 *
	 * Creates a bounding box filter and adds it to the given container
	 *
	 */
    this.addBBoxFilter = function ($container, $infocontainer,layername) {
        var $bboxdraw = $('<button type="button" id="bboxdraw" class="btn btn-xs btn-group btn-group-xs" title="Draw a bounding box around the images you would like to add to your selection."><i class="icon-crop"></i> Create</button>'),
			$bboxedit = $('<button type="button" id="bboxedit" class="btn btn-xs btn-group btn-group-xs" title="Edit a bounding box by selecting it."><i class="icon-edit"></i> Edit</button>'),
			$bboxdel  = $('<button type="button" id="bboxdel"  class="btn btn-xs btn-group btn-group-xs" title="Delete a bounding box by selecting it."><i class="icon-remove-sign"></i> Delete</button>'),
			$btn = $('<span id="bbox-button" class="btn btn-xs" >Crop filters &nbsp;<a href="javascript: void(0);"><i class="icon-remove-sign"></i><a/></span><br>');
		// Setup button action callbacks
        $bboxdraw.click(function (){
            baseMap.toggleBBoxDraw();
        });
        $bboxdraw.tooltip({
			html: true, 
			placement: 'left', 
			trigger:'hover'
		});
        $bboxedit.click(function (){
            baseMap.toggleBBoxEdit();
        });
        $bboxedit.tooltip({
			html: true, 
			placement: 'left', 
			trigger:'hover'
		});
        $bboxdel.click(function (){
            baseMap.toggleBBoxDel();
        });
        $bboxdel.tooltip({
			html: true, 
			placement: 'left', 
			trigger:'hover'
		});
		
		// Create a separate layer to show the drawn bounding boxes
		var layernameBoundingBoxes = 'Bounding boxes';
        if (baseMap.mapInstance.getLayersByName(layernameBoundingBoxes).length == 0) {
				
			var bbLayer = new OpenLayers.Layer.Vector(layernameBoundingBoxes);
			bbLayer.events.on({
				'beforefeaturemodified': function(evt) {
					// Unused
				},
				'afterfeaturemodified': function(evt) {
					var filterBounds = evt.feature.geometry.getBounds().clone();
					filterBounds.transform(baseMap.projection.mercator, baseMap.projection.geographic);
					baseMap.filters.BBoxes[evt.feature.id] = filterBounds;
					// Update view
					baseMap.showSelectedImages();
					
					baseMap.toggleBBoxEdit();
				},
				'featureselected': function(evt) {
					// Perform this only when the bbdelete button is selected
					if( baseMap.mapInstance.getControl('bboxdelCtrl').active ) {
						// Delete from filter list
						delete baseMap.filters.BBoxes[evt.feature.id];
						// Delete from layer
						evt.object.removeFeatures( evt.object.getFeatureById(evt.feature.id) );
						// Update view
						baseMap.showSelectedImages();
						
						baseMap.toggleBBoxDel();
					}
				}
			});
			baseMap.mapInstance.addLayer(bbLayer);
			
			// A modifier to edit the bounding boxes
			var bboxeditCtrl = new OpenLayers.Control.ModifyFeature(bbLayer);
			bboxeditCtrl.mode = OpenLayers.Control.ModifyFeature.RESIZE | 
						 OpenLayers.Control.ModifyFeature.RESHAPE |
						 OpenLayers.Control.ModifyFeature.DRAG;
						 //TODO: If we activate the ROTATE, which we should, we need to change the way the actual 
						 // filtering is done too in the project creation python code to use Polygon instead
						 // of min/max filters
						  //OpenLayers.Control.ModifyFeature.ROTATE;
			bboxeditCtrl.id = 'bboxeditCtrl';
        	
			bboxdelCtrl = new OpenLayers.Control.SelectFeature(bbLayer);
			bboxdelCtrl.id = 'bboxdelCtrl';
			
			// A controller to draw bounding boxes
    		var bboxdrawCtrl =  new OpenLayers.Control.DrawFeature(
				bbLayer, 
				OpenLayers.Handler.RegularPolygon, 
				{
					handlerOptions: {
					    irregular: true
					},
					eventListeners: {
					    "featureadded": function (evt) {
							var filterBounds = evt.feature.geometry.getBounds().clone();
							filterBounds.transform(baseMap.projection.mercator, baseMap.projection.geographic);
							baseMap.filters.BBoxes[evt.feature.id] = filterBounds;
														
							baseMap.showSelectedImages();
							baseMap.toggleBBoxDraw();
							$btn.show();
					    }
					}
			    }
			);
    		bboxdrawCtrl.id = "bboxdrawCtrl";
			
			
			// Create button
			$btn.hide();
			$btn.find("a").click(function () {
				
				$btn.hide();
				baseMap.mapInstance.getLayersByName('Bounding boxes')[0].removeAllFeatures();
				delete baseMap.filters.BBoxes;
				baseMap.filters.BBoxes = [];
				// Update map
				baseMap.showSelectedImages();
	        });
			$btn.tooltip({
				html: true, 
				placement: 'left', 
				trigger:'hover',
				title: function() {
					var msg = '', i = 1;
					for( var key in baseMap.filters.BBoxes) {
			            var bbox = [baseMap.filters.BBoxes[key].left.toFixed(2), 
									baseMap.filters.BBoxes[key].bottom.toFixed(2), 
									baseMap.filters.BBoxes[key].right.toFixed(2), 
									baseMap.filters.BBoxes[key].top.toFixed(2)];
						msg += i + ': [' + bbox.join(',') + ']<br>';
						i++;
			        }
					return msg;
				}
			});
			$btn.tooltip("show");
			$infocontainer.append($btn);
			
			baseMap.mapInstance.addControls([bboxdrawCtrl, bboxeditCtrl, bboxdelCtrl]);
			
        }

		
        $container.append($("<div style='margin: 10px;'></div>").append( "Crop box tools:<br>", $bboxdraw, $bboxedit, $bboxdel ));
		
    }

	/**
	 * Toggles the bounding box draw button and deals with the controllers
	 */
    this.toggleBBoxDraw = function (forcedeselect) {
        forcedeselect = (( typeof forcedeselect !== 'undefined') ? forcedeselect : false);
        if ($('#bboxdraw').hasClass('active') || forcedeselect) {
			baseMap.mapInstance.getControl('bboxdrawCtrl').deactivate();
            $('#bboxdraw').removeClass('active');
        }
        else {
			baseMap.mapInstance.getControl('bboxdrawCtrl').activate();
            $('#bboxdraw').addClass('active');
        }
    }
	/**
	 * Toggles the bounding box edit button and deals with the controllers
	 */
	this.toggleBBoxEdit = function() {
        if ($('#bboxedit').hasClass('active') ) {
			baseMap.mapInstance.getControl('bboxeditCtrl').deactivate();
			baseMap.mapInstance.getControl('highlightCtrl').activate();
            $('#bboxedit').removeClass('active');
        }
        else {
			// We need to deactivate the highlightCtrl before the bbmod control actually 
			// 	gets activated. This is probably because it is also a vector layer!?
			baseMap.mapInstance.getControl('highlightCtrl').deactivate();
			baseMap.mapInstance.getControl('bboxeditCtrl').activate();
            $('#bboxedit').addClass('active');
        }
	}
	/**
	 * Toggles the bounding box delete button and deals with the controllers
	 */
	this.toggleBBoxDel = function() {
        if ($('#bboxdel').hasClass('active')) {
			baseMap.mapInstance.getControl('bboxdelCtrl').deactivate();
			baseMap.mapInstance.getControl('highlightCtrl').activate();
            $('#bboxdel').removeClass('active');
        }
        else {
			// We need to deactivate the highlightCtrl before the bbmod control actually 
			// 	gets activated. This is probably because it is also a vector layer!?
			baseMap.mapInstance.getControl('highlightCtrl').deactivate();
			baseMap.mapInstance.getControl('bboxdelCtrl').activate();
            $('#bboxdel').addClass('active');
        }
	}	
	
	/**
	 * Sets up the button and info text in the selection pane
	 *
	 * $container - The pane to add the button and text to
	 */
	this.addSelectionInfo = function($container) {
		baseMap.$selectedpanel = $container;
		
		var $createbtn = $('<button id="create-button" class="btn btn-info disabled" style="width:100%; margin-top:10px;"><i class="icon-plus"></i> New Project with selection</button>');
		$createbtn.click(function () {
            baseMap.openNewCollectionModal()
        });
		//$createbtn.hide();
		
		var $infobtn = $('<div id="info-button" class="alert" style="margin-top:10px"></div>');
		$infobtn.hide();
		
		baseMap.$selectedpanel.append($infobtn, $createbtn);
	}
	
    /**
     * Updates the selection info area depending on the selections made and whether the user is logged in
     */
    this.updateSelectionInfo = function () {
        var showcreatbtn = false;

        // Don't continue until the panel has been created
        if( typeof baseMap.$selectedpanel === 'undefined' ) {
        		return;
        }
        
        // If there are any deployments selected then set the showcreatebtn=true
        if (baseMap.filters.deployments != null && baseMap.filters.deployments.length > 0) {
        	showcreatbtn = true;
        }
        
        
        if (showcreatbtn && !globalstate.isloggedin) {
            $('#info-button').html("<b>NOTE:</b> you need to be logged in to create a Project");
            $('#info-button').show();
			
			$('#create-button').addClass('disabled');
            //$('#create-button').hide();
        }
        else if (showcreatbtn && globalstate.isloggedin) {
        	$('#info-button').hide();
        	
            $('#create-button').removeClass('disabled');
            //$('#create-button').show();
        }
        else {
            $('#info-button').html("<b>NOTE</b>: no images selected. Use the tools above to add images to your project.");
            $('#info-button').show();
            
			$('#create-button').addClass('disabled');
            //$('#create-button').hide();
        }
    }

    this.openNewCollectionModal = function () {
		// prepare clform
		var key, ids = [];
		for (var i = 0; i < this.filters.deployments.length; i++) {
			ids.push(this.filters.deployments[i].id)
		}
		$('#clform').find('#id_deployment_ids').val(ids.join(','));

		for (key in this.filters.featranges) {
			$('#clform').find('#id_'+key).val(this.filters.featranges[key][0] + ',' + this.filters.featranges[key][1]);
	 	}

		var bboxarr = [];
		for (key in this.filters.BBoxes) {
            var bbox = [this.filters.BBoxes[key].left, this.filters.BBoxes[key].bottom, this.filters.BBoxes[key].right, this.filters.BBoxes[key].top];
			bboxarr.push(bbox.join(','));
        }
        if (bboxarr.length > 0) {
            $('#clform').find('#id_bboxes').val(bboxarr.join(':'));
        }

		// Show modal
        $('#new-collection-modal').modal('show');
    }


}