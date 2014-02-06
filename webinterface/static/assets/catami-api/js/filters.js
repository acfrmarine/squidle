/**
 * Class for creating API filter string from input elements.
 *
 * An example filter could be:
 *
 <div class="btn-group api-filter">
 <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">Parameter name: <span class="api-filt-text">Default text</span> <span class="caret"></span></a>
 <ul class="dropdown-menu">
 <li><label class="radio"><input type="radio" name="grp" id="param" value="VALUE1" checked>Option 1</label></li>
 <li><label class="radio"><input type="radio" name="grp" id="param" value="VALUE2">Option 2</label></li>
 </ul>
 </div>
 *
 * NOTE: the class of the div: "api-filter"
 *       the class of the span: "api-filt-text"
 *       the id attribute of the input "param" is the name of the api filter parameter
 *       the value attribute of the input is the value of the api filter parameter
 *       the label and the input is used to set the content "api-filt-text" span
 *
 * In JS, you would initialise with:
 *
 filt=new ApiFilter(function {  // constructor with onChange method
        update_filter();
    });
 filt.init;                      // initialise
 filt.update;                    // initial update using defaults (optional)

 function update_filter() {      // function called when filter is updated
        filterstring = filt.get;
        // Do stuff with filterstring
    }
 *
 * @param updatefnc
 * @constructor
 */


function ApiFilter(updatefnc) {

    this.update = updatefnc;

    /**
     * Searches for all radio buttons contained within the "api-filter" class and
     * sets change functions for filter radio buttons
     */
    this.init = function () {
        $('.api-filter').find('input:radio').each(function (i, obj) {
            $(obj).on('change', function () {
                updatefnc();
            });
        });
    }


    /**
     * Searches for input elements contained within in the "api-filter" class and
     * uses their names and values to construct a filter string.
     * It also updates the html of the nearest parent element containing the "api-filt-text" class label
     * @return {String}
     */
    this.get = function () {
        var filter = 'format=json';

        // Extract values from radio button elements
        $('.api-filter input:radio:checked').each(function (i, obj) {
            if ($(obj).val() != '') {
                filter += '&' + $(obj).attr('id') + '=' + $(obj).val();
                //alert($(obj).parent().text());
            }
            $(obj).closest(".api-filter").find('.api-filt-text').html($(obj).parent().text());
        });

        // Extract values from hidden elements
        $('.api-filter input[type=hidden]').each(function (i, obj) {
            if ($(obj).val() != '') {
                filter += '&' + $(obj).attr('id') + '=' + $(obj).val();
            }
        });

        return filter;
    }
}
