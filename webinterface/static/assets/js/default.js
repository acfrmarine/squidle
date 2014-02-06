

/**********************************************************************
 * Top navigation bar functions
 **********************************************************************/
$('#top-nav > .navbar-nav > li').tooltip({trigger:'hover',placement:'bottom'});
$('#nav-icon-link').tooltip({trigger:'hover',placement:'bottom'});
//$('#top-nav > .navbar-nav > li > a').mouseenter(function() {
//    //$(this).append('<span> '+$(this).attr('title')+'</span>');
//});
//$('#top-nav > .navbar-nav > li > a').mouseleave(function() {
//    //$(this).find('span').remove();
//});

/**********************************************************************
 * General useful behaviours
 **********************************************************************/

// General popovers and tooltips
$("[rel=tooltip]").tooltip();
$("[rel=popover-roll]").popover({ trigger: "hover" });
$("[rel=popover]").popover();

// Custom tab activation to make hashes persistent in url
// do not use data-toggle="tab" attribute
$('.nav-tabs a').on('click',function (e) {
    e.preventDefault();
    $(this).tab('show');
    history.pushState(null, '', $(this).attr('href'));
});

// Allow links to change URL without page refresh
$('.href-nofollow a').on('click',function (e) {
    e.preventDefault();
    history.pushState(null, '', $(this).attr('href'));
});


/**********************************************************************
 * Ajax setup for Tastypie API
 **********************************************************************/
function setupAjax() {
    // Setup CSRF Token for ajax calls to tastiepie API
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
}


/**********************************************************************
 * Notification functions
 **********************************************************************/

/**
 * Function to display notifications to the user.
 *
 * @param title : title of the note (string)
 * @param msg   : message to display (string)
 * @param type  : type (string, optional, values: 'success' | ['info'] | 'error')
 * @param hide  : whether or not to auto hide (bool, optional, vals: true | [false])
 */
function show_note(title,msg,type,hide) {
    type = ((typeof type !== 'undefined') ? type : 'info');
    hide = ((typeof hide !== 'undefined') ? hide : false);
    $.pnotify({
        title: title,
        text: msg,
        type: type, // success | info | error
        hide: hide,
        icon: false,
        history: false,
        sticker: false
    });
}


var busynotice = false;
function show_busy(title) {
    if (busynotice) {
        busynotice.pnotify_display();
    } else {
        busynotice = $.pnotify({
            title: title,
            text: '<div class="progress progress-striped active"><div class="progress-bar" style="width: 100%"></div></div>',
            nonblock: true,
            hide: false,
            type: 'info',
            icon: false,
            history: false,
            closer: false,
            sticker: false
        });
    }
}
function hide_busy() {
    if (busynotice.pnotify_remove) busynotice.pnotify_remove();
    busynotice = false;
}


/**********************************************************************
 * Check if an element is scrolled into view
 **********************************************************************/
function isInView($el) {
    if ($el.length && $el.is(':visible')) {
        var docViewTop = $(window).scrollTop(),
            docViewBottom = docViewTop + $(window).height(),
            elemTop = $el.offset().top,
            elemBottom = elemTop + $el.height();

        return ((elemBottom >= docViewTop) && (elemTop <= docViewBottom)
            && (elemBottom <= docViewBottom) &&  (elemTop >= docViewTop) );
    }
    else return false;
}
