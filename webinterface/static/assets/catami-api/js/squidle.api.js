/***********************************************************************************************************************
 * Class: SquidleAPI
 * Creating lists of collections and worksets.
 *
 * @param preview_fnc
 * @param select_fnc
 * @constructor
 **********************************************************************************************************************/

function SquidleAPI(usrconfig) {

    // Default display config
    var config = {
        api_baseurl: '/api/dev/',
        format: false
    }
    if (usrconfig) $.extend(config, usrconfig);  // override defaults with input arguments

    /* Public methods
     ******************************************************************************************************************/

    /**
     *
     * @param resource
     * @param filter
     * @param $outputelement
     * @param format
     */
    this.getItems = function($outputelement, resource, filter, format) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        format = (typeof format !== 'undefined') ? format : config.format;

        var obj, $el, _this=this;
        $outputelement.data('api-ajax', $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: config.api_baseurl + resource + filter,
            success: function (qs) {
                if (qs.objects.length > 0) {
                    for (var i = 0; i < qs.objects.length; i++) {
                        obj = getAPIObj(resource, qs.objects[i]);
                        $el = $(_this.formatAPIObj(format, obj));
                        $el.data('apidata',obj);
                        $outputelement.append( $el );
                    }
                }
                else {
                    $outputelement.append("<p class='ajax-empty'>No \""+resource+"\" items to display.</p>");
                }
                $outputelement.data('api-ajax',false);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest);
                $outputelement.append("<p class='ajax-error'>There was an error processing your request ("+errorThrown+")</p>");
                $outputelement.data('api-ajax',false);
            }
        }));
    }


    /**
     *
     * @param format
     * @param clobj
     * @returns {XML|string|void}
     */
    this.formatAPIObj = function (format, clobj) {
        return format.replace(/{(.*?)}/g, function (match, string) {
            //alert(string+' : '+match+' : '+clobj[string]);
            return typeof clobj[string] != 'undefined'
                ? clobj[string]
                : match
                ;
        });
    }

    /**
     *
     * @param resource
     * @param obj
     * @returns {*}
     */
    function getAPIObj(resource, obj) {
        if (resource == 'collection') {
            return  {
                id: obj.id,
                name: obj.name,
                description: obj.description,
                username: obj.owner.username,
                image_count: obj.image_count,
                parent_id: obj.parent_id,
                parent: obj.parent,
                creation_info: obj.creation_info,
                creation_date: obj.creation_date.substr(0, 10),
                access: "Public",//access: (obj.is_public) ? 'Public' : 'Private',
                type: (obj.parent_id) ? 'Workset' : 'Project'
            }
        }
        else {
            return obj;
        }
    }

}



$.fn.SquidleAPIgetItems = function( filters ) {
    var apifilter = "";
    if (this.data('api-filter')) apifilter += this.data('api-filter');
    if (filters) apifilter += filters;

    var sqapi = new SquidleAPI();
    sqapi.getItems(this , this.data('api-resource') , apifilter , this.data('api-format'));

    return sqapi;
}