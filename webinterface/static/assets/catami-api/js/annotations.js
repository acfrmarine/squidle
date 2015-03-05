function AnnotationAPI (usrsettings) {
    var settings = {
        api_tag_baseurl: '/api/dev/annotation_code/',
        api_pts_baseurl: '/api/dev/point_annotation/',
        linkurl: ""
    }
    if (usrsettings) $.extend(settings, usrsettings);  // override defaults with input arguments
    //console.log(settings);

    var config = {
        theme: 'as-default',
        format: ''
    }
    if (usrsettings.config) $.extend(config, usrsettings.config);  // override defaults with input arguments
    //if (!config.format) getFormat(config.theme);

    // variable to reference current ajax object
    var ajaxobj = '',
        ajaxpointsobj = '';

    // Initialise meta info
    this.meta_tags = {
        limit: '',
        next: '',
        offset: '',
        previous: '',
        total_count: '',
        start: '',
        end: ''
    }

    // Initialise meta info
    this.meta_pts = {
        limit: '',
        next: '',
        offset: '',
        previous: '',
        total_count: '',
        start: '',
        end: ''
    }

    this.setFormat = function(format) {
        config.format = format;
    }

    this.clearTags = function (outputelement) {
        if (typeof(ajaxobj)=='object') ajaxobj.abort(); // cancel previous request (in case it is still loading to prevent asynchronous munging of data)
        $(outputelement).html('');
    }


    this.getTags = function (filter, outputelement, update_container_fnc) {
        var delim = (settings.api_tag_baseurl.indexOf('?') === -1) ? "?" : "&";
        filter = ((typeof filter !== 'undefined') ? delim + filter : '');
        var parent = this;
        var list = '';
        //console.log(settings.api_tag_baseurl + filter);
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,//true,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_tag_baseurl + filter,
            success: function (objs) {
                var obj = {};
                $.extend(parent.meta_tags, objs.meta);
                parent.meta_tags.start = objs.meta.offset+1;
                parent.meta_tags.end = Math.min((objs.meta.offset + objs.meta.limit), objs.meta.total_count);
                if (objs.objects.length > 0) {
                    for (var i = 0; i < objs.objects.length; i++) {
                        obj = getTagObj(objs.objects[i]);
                        list += formatObj(config.format, obj);
                        $(outputelement).append(formatObj(config.format, obj));
                    }
                }
                else {
                    $(outputelement).append('<p class="alert alert-error">No items to display.</p>');
                }

                if (update_container_fnc) update_container_fnc(outputelement);
            }
        });
        if (outputelement) {
            if (!$(outputelement).hasClass(config.theme)) $(outputelement).addClass(config.theme);
//            $(outputelement).append(list);
        }
        //return list;
    }


    this.getNewTags = function (filter, outputelement, update_container_fnc) {
        this.clearTags(outputelement);
        this.getTags(filter, outputelement, update_container_fnc);
    }


    this.getTagInfo = function (uri) {
        var taginfo = {};
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: uri,
            success: function (obj) {
                taginfo = obj;
            }
        });
        return taginfo;
    }

    this.getAnnotationPoints = function (filter) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        //console.log(settings.api_pts_baseurl + filter);
        var parent = this;
        var list = [];

        //if (typeof(ajaxpointsobj)=='object') ajaxpointsobj.abort(); // cancel previous request (in case it is still loading to prevent asynchronous munging of data)

        ajaxpointsobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_pts_baseurl + filter,
            success: function (objs) {
                var obj = {};
                $.extend(parent.meta_pts, objs.meta);
                parent.meta_pts.start = objs.meta.offset+1;
                parent.meta_pts.end = Math.min((objs.meta.offset + objs.meta.limit), objs.meta.total_count);
                if (objs.objects.length > 0) {
                    for (var i = 0; i < objs.objects.length; i++) {
                        obj = getPtObj(objs.objects[i]);
                        list.push(obj);
                    }
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest);
                list=false;
            }
        });
        return list;
    }




    /**
     *
     * @param obj
     * @return {Object}
     */
    function getTagObj(obj) {
        return {
            id: obj.id,
            code_name: obj.code_name,
            caab_code: obj.caab_code,
            cpc_code: obj.cpc_code,
            description: obj.description,
            parent: obj.parent,
            parent_id: obj.parent_id,
            point_colour: obj.point_colour,
            resource_uri: obj.resource_uri
        };
    }

    function getPtObj(obj) {

        var unlabeled = '/api/dev/annotation_code/1/';
        return {
            id: obj.id,
            annotation_set: obj.annotation_set,
            image: obj.image,
            label: obj.label,
            label_name: obj.label_name,
            label_colour:obj.label_colour,
            level: obj.level,
            qualifiers: obj.qualifier_names,
            x: obj.x,
            y: obj.y,
            resource_uri: obj.resource_uri,
            cssid: 'ap-'+obj.id,
            scored: (obj.label !== unlabeled) ? true : false
        }
    }

    /**
     *
     * @param format
     * @param obj
     * @return {String|XML|void}
     */
    function formatObj(format, obj) {
        return format.replace(/{\[(.*?)\]}/g, function (match, string) {
            return typeof obj[string] != 'undefined'
                ? obj[string]
                : match;
        });
    }
}

//var pointList = [];

/**
 *
 */
function selectAnnotationPoint(item, select) {
    // if select is defined, force state, otherwise toggle
    var selectpoint = (typeof select !== 'undefined') ? select : ! $(item).hasClass('apcol-selected');

    if (selectpoint) {
//        $(item).removeClass (function (index, css) {
//            return (css.match (/\bapcol-\S+/g) || []).join(' ');
//        }).addClass('apcol-selected');
//        $(item).addClass('icon-bullseye');
        $(item).addClass('icon-bullseye apcol-selected');
        $('#antag-search').focus();
        //$(item).css('color', '#FF0000');
        $(item).css({"font-size": "22px", "margin": "-11px"});
    } else { // deselect point
//        var apcol_class = ($(item).data().scored) ? 'apcol-scored' : 'apcol-default';
//        $(item).removeClass('apcol-selected icon-bullseye').addClass(apcol_class);
        $(item).removeClass('apcol-selected icon-bullseye');
        $(item).animate({"font-size": "14px", "margin": "-7px"}, 300);
    }
    /*
     var isSelected = false;
     for (var i = 0; i < pointList.length; i++) {
        if (pointList[i].cssid == item.id) {
            if (pointList[i].selected == true) {
                var apcol_class = (pointList[i].scored) ? 'apcol-scored' : 'apcol-default';
                $(item).removeClass (function (index, css) {
                    return (css.match (/\bapcol-\S+/g) || []).join(' ');
                }).addClass(apcol_class);
                pointList[i].selected = false;
            } else {
                $(item).removeClass (function (index, css) {
                    return (css.match (/\bapcol-\S+/g) || []).join(' ');
                }).addClass('apcol-selected');
                pointList[i].selected = true;
                $('#antag-search').focus();
            }
        }
    }
    */
}

function mouseoverAnPt(thispoint) {
    //var thistitle = $(thispoint).attr('data-original-title');
    $(thispoint).css({"font-size" : "22px", "margin":"-11px"});
    //$('[data-original-title="' + thistitle + '"]').tooltip('show');
    //console.log(thistitle);
}

function mouseoutAnPt(thispoint) {
    //var thistitle = $(thispoint).attr('data-original-title');
    if ($(thispoint).hasClass('apcol-selected'))
        $(thispoint).css({"font-size": "22px", "margin": "-11px"});
    else
        $(thispoint).animate({"font-size" : "14px", "margin":"-7px"}, 300);
    //$('[data-original-title="' + thistitle + '"]').tooltip('hide');
    //$(thispoint).tooltip('hide');
}

/**
 *
 */
function setAnnotationPoints() {
    var $mainimg = $('#og-main-img');
    var $activethm = $('.og-active-thm');
    //showLoader();
    var pointList = taglist.getAnnotationPoints('image='+curstate.imid+'&annotation_set='+curstate.asid+'&limit=0');

    //console.log(pointList);

    if (pointList && $mainimg.length >0) {
        var imgwidth = $mainimg.width(),
            imgheight = $mainimg.height(),
            imgoffsettop = $mainimg.offset().top-$mainimg.parent().offset().top,
            imgoffsetleft = $mainimg.offset().left-$mainimg.parent().offset().left;


        //console.log('OFFSET: '+imgoffsettop+', '+imgoffsetleft);
        $.each(pointList, function(i,thispoint) {
            //var apcol_class =  (thispoint.scored) ? 'apcol-scored icon-circle' : 'apcol-default icon-circle-blank';
            var top = Math.round(imgoffsettop+thispoint.y*imgheight),
                left = Math.round(imgoffsetleft+thispoint.x*imgwidth);

//            var $anpt = $('<i id="'+thispoint.cssid+'" class="annotation-point '+apcol_class+'" '+
//                'style="top:'+top+'px; left:'+left+'px; color:#'+thispoint.label_colour+';"></i>');
//            $anpt.mouseenter(function(){mouseoverAnPt(this);});
//            $anpt.mouseleave(function(){mouseoutAnPt(this);});
//            $anpt.click(function(){selectAnnotationPoint(this);})
//            $anpt.data({scored:thispoint.scored,
//                label:thispoint.label,
//                label_name:thispoint.label_name,
//                label_colour:'#'+thispoint.label_colour,
//                resource_uri:thispoint.resource_uri,
//                qualifiers : thispoint.qualifiers,
//                position:{x:thispoint.x , y:thispoint.y},
//                imgposition: {top:top, left:left}});

            var thispointdata = {scored: thispoint.scored,
                label: thispoint.label,
                label_name: thispoint.label_name,
                label_colour: '#' + thispoint.label_colour,
                resource_uri: thispoint.resource_uri,
                qualifiers: thispoint.qualifiers,
                position: {x: thispoint.x, y: thispoint.y},
                imgposition: {top: top, left: left}};

            var $anpt = updatePoint(thispointdata);

            $mainimg.after($anpt.fadeIn(1 + Math.floor(Math.random() * 1000)));
            // tooltip function (title and modifiers)
//            $anpt.tooltip({placement: 'right',
//                container: 'body',
//                html: true,
//                title: function() {
//                    var title = $(this).data('label_name'); // add label name
//                    $.each($(this).data('qualifiers'), function (i, l) { // add list of modifiers
//                        title += "<br>-"+l;
//                    });
//                    return title;
//                }
//            });

        });
        showThmAnnotationData($activethm.parent('li.thm'), pointList.length);
    } else {
        show_note('Error loading points','There was an error loading the points. Click <a href="javascript:void(0)" onclick="setAnnotationPoints()">here</a> to try again.','error',false)
    }
    //hideImgLoader();
}

/**
 * Create or update point labels
 *
 * @param thispoint : either a dictionary object containing fields to create a new point, or an existing jquery object
 * with all the data associated with the existing point.
 * @returns {*|jQuery|HTMLElement}
 */
function updatePoint(thispoint) {

    if (thispoint instanceof jQuery) { // if point is existing jqery object (already initialised point)
        var $anpt = thispoint;
        thispoint = $anpt.data();
    }
    else { // if initial dictionary, create annotation point
        var $anpt = $('<i id="' + thispoint.cssid + '" style="top:' + thispoint.imgposition.top + 'px; left:' + thispoint.imgposition.left + 'px;"></i>');
        $anpt.data(thispoint);
        $anpt.addClass("annotation-point");
        $anpt.mouseenter(function () {
            mouseoverAnPt(this);
        });
        $anpt.mouseleave(function () {
            mouseoutAnPt(this);
        });
        $anpt.click(function () {
            selectAnnotationPoint(this);
        });
        $anpt.tooltip({placement: 'right',
            container: $anpt,
            html: true,
            title: function () {
                var title = $(this).data('label_name'); // add label name
                $.each($(this).data('qualifiers'), function (i, l) { // add list of modifiers
                    title += "<br>-" + l;
                });
                return title;
            }
        });
    }
    if (thispoint.scored) $anpt.removeClass('icon-circle-blank').addClass('icon-circle');
    else $anpt.removeClass('icon-circle').addClass('icon-circle-blank');
    $anpt.css('color', thispoint.label_colour);

    return $anpt;
}

function showImgLoader() {
    //if (!$('.og-loading').data().hasOwnProperty('active')) $('.og-loading').data().active=0;
    //$('.og-loading').data().active++;
    $('.og-loading').fadeIn(2000,'easeInCubic');
}

function hideImgLoader() {
    //$('.og-loading').data().active--;
    //if ($('.og-loading').data().active <= 0)  $('.og-loading').hide();
    $('.og-loading').hide();
}

/**
 *
 * @param label
 * @param value
 */
function labelSelectedPoints(label, label_name, label_colour, qualifiers, qualifier_names) {
    //'{ "objects": [{"resource_uri": "/api/dev/point_annotation/2/", "label": "/api/dev/annotation_code/273/"}]}'
    qualifiers = (typeof qualifiers !== 'undefined') ? qualifiers : null;
    qualifier_names = (typeof qualifier_names !== 'undefined') ? qualifier_names : [];
    var patchdata = {objects: []};
    //var selectedinds = [];
    var unlabeled = '/api/dev/annotation_code/1/';
    var labelclass = 'apcol-default';
    var $activethm = $('.og-active-thm');
    $('.apcol-selected').each(function () {
        if (label != null || qualifiers != null) {
            var newpointlabel = {resource_uri: $(this).data().resource_uri};
            if (label != null) newpointlabel.label = label;
            if (qualifiers != null) newpointlabel.qualifiers = qualifiers;
            patchdata.objects.push(newpointlabel);
        }
    });
    if (patchdata.objects.length > 0) {
        showImgLoader();
        console.log(patchdata);
        console.log(JSON.stringify(patchdata));
        $.ajax({
            url: '/api/dev/point_annotation/',
            type: 'PATCH',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(patchdata),
            success: function(response, textStatus, jqXhr) {
                $('.apcol-selected').each(function () {


                    if (label != null) {
                        // Update label counts
                        if (label != unlabeled && $(this).data().label == unlabeled) $activethm.data().annotation_labelled_count++;
                        else if (label == unlabeled && $(this).data().label != unlabeled) $activethm.data().annotation_labelled_count--;

                        // Update label meta data
                        $(this).data().label = label;
                        $(this).data().label_name = label_name;
                        $(this).data().label_colour = label_colour;
                        $(this).data().scored = ($(this).data().label != unlabeled);
                    }

                    if (qualifiers != null) $(this).data().qualifiers = qualifier_names;

                    // update point appearance
                    updatePoint($(this));

                    // unselect point
                    selectAnnotationPoint(this, false);

//                    $(this).animate({"font-size": "30px", "margin": "-15px"}, 100).animate({"font-size": "14px", "margin": "-7px"}, 400);
//                    $(this).removeClass('apcol-selected icon-bullseye');

                });
                updateTagTally();
                showThmAnnotationData($activethm.parent('li.thm'));
                //console.log(tagTally);
                hideImgLoader();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR);
                if (errorThrown == 'UNAUTHORIZED')
                    show_note(errorThrown,'You do not have permission to change these labels. Check your login.', 'error');
                else
                    show_note('Error','Error assigning labels: '+errorThrown, 'error');
                hideImgLoader();
            }
        });
    }
    /*

    for (var i = 0; i < pointList.length; i++) {
        if (pointList[i].selected == true) {
            patchdata.objects.push({resource_uri: pointList[i].resource_uri, label: label});
            patchpoints = true;
            selectedinds.push(i);
            //console.log(i+': '+pointList[i].selected);
        }
    }
    if (patchpoints) {
        $.ajax({
            url: '/api/dev/point_annotation/',
            type: 'PATCH',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(patchdata),
            success: function(response, textStatus, jqXhr) {
                for (var i=0 ; i<selectedinds.length ; i++) {
                    pointList[selectedinds[i]].selected = false;
                    pointList[selectedinds[i]].scored = true;
                    pointList[selectedinds[i]].label = label;
                    pointList[selectedinds[i]].label_name = label_name;


                    $('#'+pointList[selectedinds[i]].cssid).tooltip('destroy');
                    $('#'+pointList[selectedinds[i]].cssid).animate({"font-size" : "+=16", "margin":"-=8"}, 100).animate({"font-size" : "-=16", "margin":"+=8"}, 400);
                    $('#'+pointList[selectedinds[i]].cssid).attr('data-title',label_name);

                    if (label != unlabeled) {
                        $('#'+pointList[selectedinds[i]].cssid).tooltip({placement: 'right', container:'body'});
                        labelclass = 'apcol-scored';
                    }
                    $('#'+pointList[selectedinds[i]].cssid).removeClass (function (index, css) {
                        return (css.match (/\bapcol-\S+/g) || []).join(' ');
                    }).addClass(labelclass);
                }
                updateTagTally();
                //console.log(tagTally);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(XMLHttpRequest);
                show_note('Error','There was an error while processing your request: '+errorThrown, 'error');
            }
        });
    }
    */
}


// TODO: this is a useful jquery plugin for filtering on data value and should be moved somewhere else
$.fn.filterData = function (key, value) {
    return this.filter(function () {
        return $(this).data(key) == value;
    });
};

function mouseoverTagTally(title) {
    //$('[data-original-title="' + title + '"]').tooltip('show');
//    $('.annotation-point[data-label_name="' + title + '"]').css({"font-size" : "+=16px", "margin":"-=8px"});
    $('.annotation-point').filterData('label_name',title).css({"font-size": "+=16px", "margin": "-=8px"});
}
function mouseoutTagTally(title) {
    //$('[data-original-title="' + title + '"]').tooltip('hide');
//    $('.annotation-point[data-title="' + title + '"]').animate({"font-size": "-=10px", "margin": "+=5px"}, 400);
    //$('.annotation-point[data-label_name="' + title + '"]').css({"font-size": "-=16px", "margin": "+=8px"});
    //$('.annotation-point').filterData('label_name', title).css({"font-size": "-=16px", "margin": "+=8px"});
    $('.annotation-point').filterData('label_name', title).each(
        function(i,thispoint) {
            mouseoutAnPt(thispoint)
        });
}

function updateTagTally() {
    //console.log('tag tally');

    var containerid = '#imganot-2';
    var tagTally={}, $tag, tallykey;
    $('.annotation-point').each(function(){
        tallykey = $(this).data().label_name;
        if (tagTally.hasOwnProperty(tallykey)) tagTally[tallykey].tally++;
        else tagTally[tallykey] = {label:$(this).data().label , label_name:$(this).data().label_name , tally : 1, label_colour: $(this).data().label_colour};
    });
    /*
    for (var i = 0; i < pointList.length; i++) {
        var tallykey = pointList[i].label_name;
        if (tagTally.hasOwnProperty(tallykey)) tagTally[tallykey].tally++;
        else tagTally[tallykey] = {label: pointList[i].label,label_name : pointList[i].label_name,tally : 1};
    }
    */

    $(containerid).html('<div class="antag-taglist">Labels in this image:<br></div>');

    for(var key in tagTally) {
        //console.log(key + ': ' + tagTally[key]);
        $(containerid+'>.antag-taglist').append('<a class="annotation-tag" href="javascript:void(0)" '+
            'data-label="'+tagTally[key].label+'"'+
            'onclick="labelSelectedPoints(\''+tagTally[key].label+'\',\''+tagTally[key].label_name+'\',\''+tagTally[key].label_colour+'\');"'+
            'onmouseover="mouseoverTagTally(\''+key+'\')"'+
            'onmouseout="mouseoutTagTally(\''+key+'\')">'+key+' <span class="badge">'+tagTally[key].tally+'</span></a><br> ');
    }
    updateTagContainer(containerid+' .antag-taglist');
}

function showThmAnnotationData($items, newtotal) {
    var labeled, total, bgcol, $tagel;
    $items.each(function () {
        $el = $(this).find('a.thm-link');
        labeled = $el.data().annotation_labelled_count;

        if ($el.data().annotation_count==0 && newtotal) {
            $el.data().annotation_count = newtotal;
        }
        total = $el.data().annotation_count;

        if (total > 0) {
            if (labeled <= 0) bgcol = 'red';
            else if (labeled == total) bgcol = 'rgb(69, 184, 69)';
            else bgcol = 'yellow';
            if ($el.find('span.og-annotation-count').length <= 0) {
                $tagel = $('<span class="og-annotation-count" style="color:' + bgcol + '">' + labeled + '</span>');
                $tagel.tooltip({trigger: 'hover', container: 'body', title: function() {
                    $el = $(this).parent('a.thm-link');
                    return $el.data().annotation_labelled_count + '/' + $el.data().annotation_count + ' points labeled'
                }});
                $el.append($tagel);
            }
            else {
                var $acount = $el.find('span.og-annotation-count');
                $acount.css('color', bgcol);
                $acount.html(labeled);
            }
        }
    });
}

function createTaglist() {
    //console.log('tag list');
    var containerid = '#imganot-0';


    var format = '<a class="annotation-tag" href="javascript:void(0)" onclick="labelSelectedPoints(\'{[resource_uri]}\',\'{[code_name]}\',\'#{[point_colour]}\');" rel="label-popover" '+
        'data-label="{[resource_uri]}" data-content="<b>CAAB Code:</b> {[caab_code]}<br><b>Short Code:</b> {[cpc_code]}<br>insert image<br>{[description]}" data-original-title="{[code_name]}">{[code_name]}</a><br> ';
    $(containerid).html('<input type="text" id="antag-search" class="input-small" style="width:100%;" placeholder="Search all available labels" autocomplete="off"><div class="antag-taglist"></div>');

    taglist.setFormat(format);
    taglist.getNewTags('limit=0&order_by=code_name',containerid+'>.antag-taglist',updateTagContainer);
    $(containerid+" a[rel=label-popover]").popover({ trigger: "hover",placement:'leftTop',html:true,delay:200 });

    // prevent body scrolling when scrolling div
    //$(containerid + '>.antag-taglist').bind('mousewheel DOMMouseScroll', function (e) {
    $(containerid).bind('mousewheel DOMMouseScroll', function (e) {
        var delta = e.originalEvent.wheelDelta || -e.originalEvent.detail;
        this.scrollTop += ( delta < 0 ? 1 : -1 ) * 30;
        e.preventDefault();
    });

    $(containerid+'>#antag-search').click(function() {
        this.select();
    });
    $(containerid+'>#antag-search').focus(function(){
        this.select();
    });
    $(containerid+">#antag-search").onDelayedKeyup({
        handler: function() {
            //console.log('keyup!');
            $("[rel=label-popover]").popover('hide');
            var searchstr = '&code_name__icontains='+encodeURIComponent($(this).val());
//            var searchstr = '';
//            var searchwords = $(this).val().split(' ');
//            $.each (searchwords, function(i,word) {
//                searchstr += '&code_name__icontains='+word;
//            });

            taglist.setFormat(format);
            taglist.getNewTags('limit=0&order_by=code_name'+searchstr,containerid+'>.antag-taglist');
            $("[rel=label-popover]").popover({ trigger: "hover",placement:'leftTop',html:true,delay:200 });
        },
        delay: 500
    });
    //updateTagContainer(containerid);
}

function createTaggrid () {
    //console.log('tag grid');
    var containerid = '#imganot-1';
    var format = '<a class="annotation-tag badge" href="javascript:void(0)" style="background-color:#{[point_colour]}" onclick="labelSelectedPoints(\'{[resource_uri]}\',\'{[code_name]}\',\'#{[point_colour]}\');" rel="label-popover" '+
        'data-label="{[resource_uri]}" data-content="<b>CAAB Code:</b> {[caab_code]}<br><b>Short Code:</b> {[cpc_code]}<br>insert image<br>{[description]}" data-original-title="{[code_name]}">{[cpc_code]}</a> ';

    $(containerid).html('<div class="antag-taglist"></div>');

    taglist.setFormat(format);
    taglist.getNewTags('limit=0&order_by=code_name',containerid+'>.antag-taglist',updateTagContainer);
    $(containerid+" a[rel=label-popover]").popover({ trigger: "hover",placement:'leftTop',html:true,delay:200 });
    //$("[rel=label-popover]").popover({ trigger: "hover" });

    // prevent body scrolling when scrolling div
//    $(containerid+'>.antag-taglist').bind( 'mousewheel DOMMouseScroll', function ( e ) {
    $(containerid).bind('mousewheel DOMMouseScroll', function (e) {
        var delta = e.originalEvent.wheelDelta || -e.originalEvent.detail;
        this.scrollTop += ( delta < 0 ? 1 : -1 ) * 30;
        e.preventDefault();
    });
    //updateTagContainer(containerid);
}

function updateTagContainer(containerid) {
    setFullHeight(containerid,'.og-details');
    prependInfoMsg(containerid);
}

function prependInfoMsg(el) {
    if (!curstate.asid)
        $(el).prepend('<div class="alert alert-danger"><b>WARNING:</b> no Annotationset selected. To select/create an annotation run, click <a href="#dataset-modal" data-toggle="modal">here</a> or use the dropdown menu at the top.</div>');
}

function setFullHeight(el,parent) {
    if ($(el).parents('.og-panel').hasClass('og-sidepane')) {
        var usedheight= 0,
            fullheight = $(parent).height(),
            currentheight = $(el).outerHeight(true);
        $(parent).children().each(function() {
            usedheight+=$(this).outerHeight(true);
        });
        $(el).css('max-height',(fullheight - usedheight + currentheight)+'px');

        // Check that parent is not still bigger ie if it has a min size, we will be wasting space
        // TODO: this needs to account for the heights of other children in the parent
        if ($(el).height() < $(el).parent().height()) $(el).css('max-height',$(el).parent().height());
    }
}

function initAnnotationData() {
    //$('.annotation-point').remove();
    if (curstate.asid) {
        setAnnotationPoints();
        updateTagTally();
        //createTaglist();
        //createTaggrid();
    }
    /*
    if (curstate.asid && curstate.isloggedin) {
        setAnnotationPoints();
        updateTagTally();
        //createTaglist();
        //createTaggrid();
    }
    else if (curstate.asid && !curstate.isloggedin) {
        curstate.asid = 0;
        show_note('Error!','You need to be logged in to view annotation data','error',false);
    }
    */
}







/**************************************************************************************************
 *
 * @param usrsettings
 * @constructor
 */

function AnnotationSetAPI (usrsettings) {
    var settings = {
        api_baseurl: '/api/dev/point_annotation_set/',
        linkurl: ""
    }
    if (usrsettings.settings) $.extend(settings, usrsettings.settings);  // override defaults with input arguments

    var config = {
        theme: 'as-default',
        format: ''
    }
    if (usrsettings.config) $.extend(config, usrsettings.config);  // override defaults with input arguments
    //if (!config.format) getFormat(config.theme);

    // variable to reference current ajax object
    var ajaxobj = '';

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

    this.clearAnnotationSets = function (outputelement) {
        if (typeof(ajaxobj)=='object') ajaxobj.abort(); // cancel previous request (in case it is still loading to prevent asynchronous munging of data)
        $(outputelement).html('');
    }


    this.getAnnotationSets = function (filter, outputelement) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        var parent = this;
        var list = '';
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_baseurl + filter,
            success: function (objs) {
                var obj = {};
                $.extend(parent.meta, objs.meta);
                parent.meta.start = objs.meta.offset+1;
                parent.meta.end = Math.min((objs.meta.offset + objs.meta.limit), objs.meta.total_count);
                if (objs.objects.length > 0) {
                    for (var i = 0; i < objs.objects.length; i++) {
                        obj = getAsObj(objs.objects[i]);
                        list += formatObj(config.format, obj);
                    }
                }
                else {
                    list = '<p class="ajax-empty">No items to display.</p>';
                }
            }
        });
        if (outputelement) {
            if (!$(outputelement).hasClass(config.theme)) $(outputelement).addClass(config.theme);
            $(outputelement).append(list);
        }
        return list;
    }


    this.getNewAnnotationSets = function (filter, outputelement) {
        this.clearAnnotationSets(outputelement);
        this.getAnnotationSets(filter, outputelement);
    }

    this.getAnnotationInfo = function (id, outputelement) {

        var api_url = settings.api_baseurl + '?id=' + id;
        var asobj = '';

        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: api_url,
            success: function (cl) {
                asobj = getAsObj(cl.objects[0]);
            }
        });
        if (outputelement) {
            if (!$(outputelement).hasClass(config.theme)) $(outputelement).addClass(config.theme);
            $(outputelement).html(formatObj(config.format, asobj));
        }
        return asobj;
    }

    /**
     *
     * @param obj
     * @return {Object}
     */
    function getAsObj(obj) {
        return objout = {
            id: obj.id,
            collection: obj.collection,
            count: obj.count,
            methodology: obj.methodology,
            name: obj.name,
            owner: obj.owner,
            resource_uri: obj.resource_uri
        };
    }

    /**
     *
     * @param format
     * @param obj
     * @return {String|XML|void}
     */
    function formatObj(format, obj) {
        return format.replace(/{(.*?)}/g, function (match, string) {
            return typeof obj[string] != 'undefined'
                ? obj[string]
                : match;
        });
    }
}