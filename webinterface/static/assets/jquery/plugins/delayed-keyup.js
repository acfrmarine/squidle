(function($){
    $.widget("ui.onDelayedKeyup", {
        _init : function() {
            var self = this;
            $(this.element).keyup(function() {
                if(typeof(window['inputTimeout']) != "undefined"){
                    window.clearTimeout(inputTimeout);
                }
                var handler = self.options.handler;
                window['inputTimeout'] = window.setTimeout(function() {
                    handler.call(self.element) }, self.options.delay);
            });
        },
        options: {
            handler: $.noop(),
            delay: 500
        }
    });
})(jQuery);