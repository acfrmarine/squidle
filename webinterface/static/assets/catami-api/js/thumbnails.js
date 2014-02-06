function ThumnailAPI(usrsettings) {
    var settings = {
        api_baseurl: '/api/dev/image/',
        linkurl: "/imageannotate/"
    }
    if (usrsettings.settings) $.extend(settings, usrsettings.settings);  // override defaults with input arguments

    var config = {
        theme: 'th-default',
        format: '',
        shownav: true,
        navformat: ''
    }
    if (usrsettings.config) $.extend(config, usrsettings.config);  // override defaults with input arguments
    if (!config.format) getFormat(config.theme);

    var ajaxobj = ''; // variable to reference current ajax object

    // Initialise meta info
    this.meta = {
        limit: '',
        next: '',
        offset: '',
        previous: '',
        total_count: '',
        start: '',
        end: ''
    }


    this.setFormat = function(newformat) {
        config.format = newformat;
    }


    /**
     *
     * @param outputelement
     */
    this.clearThumbnails = function (outputelement) {
        if (typeof(ajaxobj)=='object') ajaxobj.abort(); // cancel previous request (in case it is still loading to prevent asynchronous munging of data)
        $(outputelement).html('');
    }

    /**
     *
     * @param outputelement
     * @param filter
     */
    this.appendThumnails = function (outputelement, apistring) {
        var parent = this;
        var obj = {};
        var apistringviewer = '';
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: apistring,
            success: function (img) {
                if (img.objects.length > 0) {
                    for (var i = 0; i < img.objects.length; i++) {
                        obj = getThObj(img.objects[i]);
                        obj.itemoffset = img.meta.offset + i;
                        obj.apistring = encodeURIComponent(apistring);
                        obj.apistringviewer = updateQueryStringParameter(apistring, 'limit', 10);
                        obj.apistringviewer = updateQueryStringParameter(obj.apistringviewer, 'offset', obj.itemoffset);
                        obj.apistringviewer = encodeURIComponent(obj.apistringviewer);
                        //obj.apistringviewer = encodeURIComponent(apistring.replace(/limit=([^&]$|[^&]*)/i, 'limit=10'));
                        $(outputelement).append(formatThObj(config.format, obj));
                    }
                }
                else {
                    $(outputelement).append('<p class="alert alert-error">No items to display.</p>');
                }
                $.extend(parent.meta, img.meta);
                parent.meta.start = img.meta.offset+1;
                parent.meta.end = Math.min((img.meta.offset + img.meta.limit), img.meta.total_count);
            }
        });
    }

    /**
     *
     * @param outputelement
     * @param filter
     */
    this.getNewThumbnails = function (outputelement, filter) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        this.clearThumbnails(outputelement);
        this.appendThumnails(outputelement, settings.api_baseurl + filter);
    }

    /**
     *
     * @param obj
     * @return {Object}
     */
    function getThObj(obj) {
        return objout = {
            id: obj.id,
            pose: obj.pose,
            resource_uri: obj.resource_uri,
            thumbnail_location: obj.thumbnail_location,
            web_location: obj.web_location,
            collection: obj.collection,
            measurements: obj.measurements
        };
    }

    /**
     *
     * @param format
     * @param obj
     * @return {String|XML|void}
     */
    function formatThObj(format, obj) {
        return format.replace(/{(.*?)}/g, function (match, string) {
            return typeof obj[string] != 'undefined'
                ? obj[string]
                : match;
        });
    }

    /**
     *
     * @param theme
     * @return {String}
     */
    function getFormat(theme) {
        if (theme == 'th-fancybox') {
            config.format = '<a class="'+theme+'" rel="gallery1" href="{web_location}"><img src="{thumbnail_location}"/></a>';
        } else if (theme == 'th-annotate') {
            config.format = '<a class="'+theme+' imageframe" href="'+settings.linkurl+'{id}/?offset={itemoffset}&apistring={apistringviewer}" data-fancybox-group="al{itemoffset}" data-fancybox-type="iframe"><img src="{thumbnail_location}"/></a>';
        } else if (theme == 'th-catamiviewer') {
            config.format = '<a class="'+theme+'" href="'+settings.linkurl+'{id}/?offset={itemoffset}&apistring={apistringviewer}" ><img src="{thumbnail_location}" /></a>';
        } else {
            config.format = '<a class="'+theme+'" href="{web_location}"><img src="{thumbnail_location}"/></a>';
        }
    }
}


function updateQueryStringParameter(uri, key, value, add) {
    add = ((typeof add !== 'undefined') ? add : false);
    var re = new RegExp("([?|&])" + key + "=.*?(&|$)", "i");
    //var re = new RegExp("" + key + "=.*?(&|$)", "i");
    var separator = uri.indexOf('?') !== -1 ? "&" : "?";
    if (uri.match(re)) {
        if (add) {
            var oldval = parseFloat(getQueryStringParameter(uri, key));
            //console.log(oldval);
            //var oldval = parseInt(parammatch[0].substr(parammatch[0].indexOf("=") + 1));
            return uri.replace(re, '$1' + key + "=" + (oldval + value) + '$2');
        } else {
            return uri.replace(re, '$1' + key + "=" + value + '$2');
        }
    }
    else {
        return uri + separator + key + "=" + value;
    }
}

function getQueryStringParameter(uri, key) {
    key = key.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regex = new RegExp("[\\?&]" + key + "=([^&#]*)"),
        results = regex.exec(uri);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

/***************************************************************************************
 *
 * @param usrsettings
 * @constructor
 */
function ImageAPI (usrsettings) {
    var settings = {
        api_baseurl: '/api/dev/image/',
        linkurl: ""
    }
//    if (usrsettings !== 'undefined') {
//        if (usrsettings.settings) $.extend(settings, usrsettings.settings);  // override defaults with input arguments
//    }
    var ajaxobj = ''; // variable to reference current ajax object

    this.getImageObj = function(id) {
        var obj = {};
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_baseurl+id+'/',
            success: function (img) {
                obj = getImObj(img);
            }
        });
        return obj;
    }

    this.meta = {
        next_id: 0,
        previous_id: 0
    }

    this.getImageNav = function(apistring, newoffset) {
        apistring = updateQueryStringParameter(apistring, 'limit', 3);
        apistring = updateQueryStringParameter(apistring, 'offset', newoffset);
        var currentoffset = parseInt(getQueryStringParameter(apistring, 'offset'));
        if (currentoffset>0) {
            apistring = updateQueryStringParameter(apistring, 'offset', -1, true);
        }

        var thiscaller = this;
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: apistring,
            success: function (img) {
                if (img.objects.length > 1) {
                    if (currentoffset===0) {
                        thiscaller.meta.previous_id = 0;
                        thiscaller.meta.next_id = img.objects[1].id;
                    } else if (currentoffset===parseInt(img.meta.total_count)-1) {
                        thiscaller.meta.previous_id = img.objects[0].id;
                        thiscaller.meta.next_id = 0;
                    } else {
                        thiscaller.meta.previous_id = img.objects[0].id;
                        thiscaller.meta.next_id = img.objects[2].id;
                    }
                }
                //console.log(thiscaller.meta.next_id);
                //console.log(thiscaller.meta.previous_id);
            }
        });
    }

    /**
     *
     * @param id
     * @param imgelement
     */
    this.getImage = function (id,imgelement) {
        var obj = this.getImageObj(id);
        $(imgelement).attr('src',obj.web_location);
    }

    /**
     *
     * @param obj
     * @return {*}
     */
    function getImObj(obj) {
        return objout = {
            id: obj.id,
            measurements: obj.measurements,
            pose: obj.pose,
            resource_uri: obj.resource_uri,
            thumbnail_location: obj.thumbnail_location,
            web_location: obj.web_location
        };
    }
}