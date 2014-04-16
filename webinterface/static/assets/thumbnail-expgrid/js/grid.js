

function Grid (grid, globalstate) {

		// list of items
	var $grid = $( grid ),
		// the items
		$items = $grid.children( 'li' ),
		// current expanded item's index
		current = -1,
		// position (top) of the expanded item
		// used to know if the preview will expand in a different row
		previewPos = -1,
		// extra amount of pixels to scroll the window
		scrollExtra = 0,
        // Fixed offset for nav bar
        scrollNavBar = $( '#top-nav').outerHeight()+5,
		// extra margin when expanded (between preview overlay and the next items)
		marginExpanded = 10,
		$window = $( window ), winsize,
		$body = $( 'html, body' ),
		// transitionend events
		transEndEventNames = {
			'WebkitTransition' : 'webkitTransitionEnd',
			'MozTransition' : 'transitionend',
			'OTransition' : 'oTransitionEnd',
			'msTransition' : 'MSTransitionEnd',
			'transition' : 'transitionend'
		},
		transEndEventName = transEndEventNames[ Modernizr.prefixed( 'transition' ) ],
		// support for csstransitions
		support = Modernizr.csstransitions,
		// default settings
		settings = {
			minHeight : 300,
			speed : 350,
			easing : 'ease'
        };
        //curstate = {};




    var thisgrid = this;


    this.init = function ( config ) {
		
		// the settings..
		settings = $.extend( true, {}, settings, config );
        thisgrid.isloading = false;

//		// preload all images
//		$grid.imagesLoaded( function() {
//
//			// save item´s size and offset
//			saveItemInfo( true );
//			// get window´s size
//			getWinSize();
//			// initialize some events
//			initEvents();
//
//		} );
        initEvents();

        // Add next grid to load during infinite scrolling
//        if (!$grid.data().hasOwnProperty('gridcount')) $grid.data('gridcount',0);
//        var nextgridcount = $grid.data('gridcount')+1;
        thisgrid.$loaderdiv = $('<div id="og-infinite-loader"></div>')
        $grid.after(thisgrid.$loaderdiv);

        //curstate = globalstate;

	}

	// add more items to the grid.
	// the new items need to appended to the grid.
	// after that call Grid.addItems(theItems);
	this.addItems = function( $newitems , $gridcontainer) {

        //console.log('Attempt to add images...');
        if (!thisgrid.isloading) {
            //console.log('Not busy loading: adding more images');
            thisgrid.isloading = true;
            showLoader();

            $newitems.appendTo($gridcontainer);
            $items = $items.add( $newitems );

    //		$newitems.each( function() {
    //			var $item = $( this );
    //			$item.data( {
    //				offsetTop : $item.offset().top,
    //				height : $item.height()
    //			} );
    //		} );

            //initItemsEvents( $newitems );
            //refreshItemInfo($gridcontainer,imid);

            // preload all images
            $gridcontainer.imagesLoaded( function() {

                // save item´s size and offset
                saveItemInfo( $newitems, true );
                // get window´s size
                getWinSize();
                // initialize some events
                //initEvents();
                initItemsEvents( $newitems );

                if (globalstate.asid) showThmAnnotationData($newitems);

                // if a preview exists and previewPos is different (different row) from item´s top then close it
                if( $('.og-expanded').length <= 0 ) $(globalstate.imid_ui()).trigger('click');

                thisgrid.isloading = false;
                hideLoader();
                //console.log('Images have finished loading!');

            } );
        }
//        else {
//            console.log('Still loading images... Not adding more.');
//        }

	}
/*
    function refreshItemInfo($gridcontainer,imid) {

        // preload all images
        $gridcontainer.imagesLoaded( function() {

            // save item´s size and offset
            saveItemInfo( true );
            // get window´s size
            getWinSize();
            // initialize some events
            //initEvents();
            initItemsEvents( $items );

            $(imid).trigger('click');

        } );
    }
*/

    // saves the item´s offset top and height (if saveheight is true)
    function saveItemInfo ($newitems, saveheight ) {
        $newitems.each( function() {
            var $item = $( this );
            var itemoffset = $item.offset().top;
            if ($('.og-expander').length>0) {  // if preview is open:
                if ( itemoffset >= $('.og-expander').offset().top) { // if item appears below the open preview, account for the preview's height
                    itemoffset = itemoffset- $('.og-expander').height();
                }
            }
            $item.data( 'offsetTop', itemoffset );
            if( saveheight ) {
                $item.data( 'height', $item.height() );
            }
        } );
    }

    function initEvents() {

        // when clicking an item, show the preview with the item´s info and large image.
        // close the item if already expanded.
        // also close if clicking on the item´s cross
        initItemsEvents( $items );

        // on window resize get the window´s size again
        // reset some values..
        $window.on( 'debouncedresize', function() {
            //console.log('Resize event');
            scrollExtra = 0;
            previewPos = -1;
            var preview = $.data( this, 'preview'),
                curritem = this.$item;
            if( typeof preview != 'undefined' ) {
                hidePreview();
            }
            setTimeout(function () {
                // save item´s offset
                saveItemInfo($items);
                getWinSize();
                //$(globalstate.imid_ui()).trigger('click');
                //showPreview(curritem);
            },500);
        } );

    }

	function initItemsEvents( $items ) {
		$items.on( 'click', 'span.og-close', function() {
			hidePreview();
			return false;
		} ).children( 'a' ).on( 'click', function(e) {

			var $item = $( this ).parent();
			// check if item already opened
            current === $item.index() ? hidePreview() : showPreview( $item );
            $('.og-active-thm').removeClass('og-active-thm');
            $( this ).addClass('og-active-thm');
			return false;
		} );
	}

	function getWinSize() {
		winsize = { width : $window.width(), height : $window.height() };
	}

	function showPreview( $item ) {

		var preview = $.data( this, 'preview' ),
			// item´s offset top
			position = $item.data( 'offsetTop' );

		scrollExtra = 0;

		// if a preview exists and previewPos is different (different row) from item´s top then close it
		if( typeof preview != 'undefined' ) {
            //console.log('Preview is open');

			// not in the same row
			if( previewPos !== position ) {
				// if position > previewPos then we need to take te current preview´s height in consideration when scrolling the window
				if( position > previewPos ) {
					scrollExtra = preview.height;
				}
                previewPos = position;
                preview.move($item);
                preview.update($item);
//				hidePreview();
                return false;
            }
            // same row
            else {
                preview.update( $item );
                return false;
            }
        }

        // update previewPos
        previewPos = position;
        // initialize new preview for the clicked item
        preview = $.data( this, 'preview', new Preview( $item ) );
        // expand preview overlay
        preview.open();
    }

    this.scrollToCurrentPreview = function() {
        //var preview = $.data( thisgrid, 'preview' );
        if ($('.og-expanded').length)
            $body.animate( { scrollTop : $('.og-expanded').offset().top- scrollNavBar },settings.speed );
    }

	function hidePreview() {
		current = -1;
        //console.log('current='+current+' hide preview');
        var preview = $.data( this, 'preview' );
		preview.close();
		$.removeData( this, 'preview' );
	}

    function checkIfLoading () {
        return this.isloading;
    }


    // the preview obj / overlay
    function Preview( $item ) {
        this.$item = $item;
        this.expandedIdx = this.$item.index();
        $item.addClass('og-exp-spacer');
        this.create();
        this.update();
    }

	Preview.prototype = {
		create : function() {
            //console.log('create preview');
			// create Preview structure:
			//this.$title = $( '<h3></h3>' );
			this.$description = $( '<p class="og-sidepanel"></p>' );
			this.$loading = $( '<div class="og-loading"><i class="icon-spinner icon-spin icon-large"></i></div>' );

            // setup nav bar and tools
            this.$prevlink = $('<li id="btn-previm"><a href="javascript:void(0)" title="Previous"><i class="icon-chevron-left"></i></a></li>'),
            this.$nextlink = $('<li id="btn-nextim"><a href="javascript:void(0)" title="Next" ><i class="icon-chevron-right"></i></a></li>'),
            this.$closelink= $('<li id="btn-closeim"><a href="javascript:void(0)" title="Close"><i class="icon-remove"></i></a></li>'),
            this.$toolslink= $('<li id="btn-imgtools"><a href="javascript:void(0)"><i class="icon-wrench"></i></a></li>'),
            this.$anotlink = $('<li id="btn-imganot"><a href="javascript:void(0)"><i class="icon-tags"></i></a></li>'),
            this.$infolink = $('<li id="btn-imginfo"><a href="javascript:void(0)"><i class="icon-info-sign"></i></a></li>'),
            this.$navtitle = $('<span class="navbar-brand"></span>'),
            this.$navtools = $('<ul class="nav navbar-nav"></ul>').append(this.$infolink,this.$anotlink,this.$toolslink),
            this.$navctrl  = $('<ul class="nav navbar-nav navbar-right"></ul>').append(this.$prevlink, this.$nextlink, this.$closelink);

            this.$thmNav = $('<div class="og-navbar"></div>');
            this.$thmNav.addClass('navbar navbar-default');
            this.$thmNav.html('');
            this.$thmNav.append(this.$navtitle,this.$navtools,this.$navctrl);

            this.$prevlink.find('a').click(function () {thisgrid.clickPrevItem()});
            this.$nextlink.find('a').click(function () {thisgrid.clickNextItem()});
            this.$closelink.find('a').click(function () {thisgrid.clickCurrItem()});

            // create panels
            this.$toolpanel = createPanel (
                'imgtools',
                'Tools',
                'icon-wrench',
                [   {icon:'icon-zoom-in', content:'zoom',onshow:initZoom},
                    {icon:'icon-adjust', content:'tools'}],
                '#btn-imgtools',
                'og-sidepane',
                {top:10, left:10},
                true
            );

            this.$infopanel = createPanel (
                'imginfo',
                'Information',
                'icon-info-sign',
                [{icon:'icon-bar-chart', content:'info',onshow: getImageInfo}],//,{icon:'icon-globe', content:'map'}],
                '#btn-imginfo',
                'og-dragpane',
//                'og-sidepane',
                {top:100, left:10}
            );
            this.$anotpanel = createPanel (
                'imganot',
                'Annotate',
                'icon-tags',
                [   {icon:'icon-align-left', content:'Tag list', onshow:createTaglist},
                    {icon:'icon-th',content:'Tag grid', onshow:createTaggrid},
                    {icon:'icon-picture',content:'Tags in this image', onshow:updateTagTally},
                    {icon:'icon-sitemap',content:'Graphical tags: not implemented yet'},
                    {icon:'icon-star', content:'My favorite tags: not implemented yet'}],
                '#btn-imganot',
                'og-sidepane',
                {top:100, left:10},
                (globalstate.asid) ? true : false
            );

            this.$description.append(this.$anotpanel,this.$infopanel,this.$toolpanel);


            this.$details = $( '<div class="og-details"></div>' ).append( this.$thmNav, this.$description );
            this.$fullimage = $( '<div class="og-fullimg"></div>' ).append( this.$loading );
            this.$previewInner = $( '<div class="og-expander-inner"></div>' ).append(this.$fullimage, this.$details);
			this.$previewEl = $( '<div class="og-expander"></div>' ).append( this.$previewInner );
			// append preview element to the item
			this.$item.append( this.getEl() );
			// set the transitions for the preview and the item
			if( support ) {
				this.setTransition();
			}

            // initialise all draggable panels
//            initPanel('#'+this.$toolpanel.attr('id'));
            initAllPanels();
        },
		update : function( $item ) {
            //console.log('update preview');

			if( $item ) {
				this.$item = $item;
			}

            //console.log('EXIDX: '+this.expandedIdx+', IDX: '+this.$item.index());
			
			// if already expanded remove class "og-expanded" from current item and add it to new item
			if( current !== -1 ) {
                //console.log('A current item is found!');
				var $currentItem = $items.eq( current );
				$currentItem.removeClass( 'og-expanded' );
                //$currentItem.attr('style','');
				this.$item.addClass( 'og-expanded' );
				// position the preview correctly
				this.positionPreview();
			}

			// update current value
			current = this.$item.index();
            //console.log('current='+current+' update preview');

			// update preview´s content
			var $itemEl = this.$item.children( 'a' ),
				eldata = {
					largesrc : $itemEl.data( 'largesrc' ),
					id : $itemEl.data( 'id' ),
                    description : $itemEl.data( 'description' ),
                    href : $itemEl.attr('href')
                };




            //this.$description.addClass('well');

            this.$navtitle.html( 'ID: '+eldata.id );
			//this.$description.html( eldata.description );
			//this.$href.attr( 'href', eldata.href );

            //console.log(eldata.href);
//            history.pushState(null, '', eldata.href);
            history.replaceState(null, '', eldata.href);
            globalstate.imid = parseInt(eldata.id);
            this.$navctrl.find('li a').tooltip({trigger:'hover',placement:'top',container:'body'});


            // fix up heights and widths
            this.$fullimage.outerWidth(this.$previewInner.width()-this.$details.outerWidth(true)-10);


			var self = this;


			// remove the current image in the preview
			if( typeof self.$largeImg != 'undefined' ) {
				self.$largeImg.remove();
			}


			// preload large image and add it to the preview
			// for smaller screens we don´t display the large image (the media query will hide the fullimage wrapper)
			if( self.$fullimage.is( ':visible' ) ) {
				this.$loading.show();
				$( '<img/>' ).load( function() {
					var $img = $( this );
					if( $img.attr( 'src' ) === self.$item.children('a').data( 'largesrc' ) ) {
						self.$loading.hide();
						self.$fullimage.find( 'img' ).remove();
						self.$largeImg = $img.fadeIn( settings.speed );
						self.$fullimage.append( self.$largeImg );

                        // init zoom once image has loaded
                        // init annotation data once image has loaded, but wait until transition is completed
                        setTimeout(function () {
                            initZoom();
                            getImageInfo();
                            initAnnotationData();
                        },settings.speed+100);
					}
				} ).attr( {src: eldata.largesrc, id: 'og-main-img'});
			}

            //updateAllPanels();
            attachImgMouseEvents(self.$previewEl); //$fullimage
            //$('.og-contextmenu').remove();


        },
        move : function ($item) {
            var $old_spacer_item = $('.og-exp-spacer'),
                $old_expanded_item = $('.og-expanded');

            var item_height = this.itemHeight;

            this.$thmNav.find('a').tooltip('hide');
            $old_spacer_item.css( 'height', $old_expanded_item.data( 'height' ) );
            $old_spacer_item.removeClass('og-exp-spacer');
            $old_expanded_item.removeClass('og-expanded');
            $item.addClass('og-expanded og-exp-spacer');

            $item.css('height',item_height);
            this.$previewEl.appendTo($item);
            current === $item.index();
            this.expandedIdx = $item.index();
//            this.setHeights();
//            // scroll to position the preview in the right place
//            this.positionPreview();
//            self.$item.removeClass( ' og-exp-spacer' );
        },
		open : function() {
            //console.log('open preview');

			setTimeout( $.proxy( function() {
                // set the height for the preview and the item
				this.setHeights();
				// scroll to position the preview in the right place
				this.positionPreview();
                // update panel positions
                //reshowOpenPanels();

            }, this ), 25 );

            // bind left and right arrow keys to preview nav
            var preview = this;
            preview.enable_keyboard_nav=true;
            $(document).bind("keydown.arrows", function(event) {
                if (preview.enable_keyboard_nav && !$("input").is(":focus")) {
                    if (event.keyCode == 37) { // right arrow
                        thisgrid.clickPrevItem();
                        preview.enable_keyboard_nav = false;
                    } else if (event.keyCode == 39) {
                        thisgrid.clickNextItem(); // left arrow
                        preview.enable_keyboard_nav = false;
                    }
                    setTimeout(function () {preview.enable_keyboard_nav = true},500);
                }
            });

		},
		close : function() {
            //console.log('close preview');


            // hide all open panels (do not close them)
            destroyAllPanels();
             $(document).unbind("keydown.arrows");
            this.$thmNav.find('a').tooltip('hide');
            this.$thmNav.remove();
            globalstate.imid = 0;

            var self = this,
				onEndFn = function() {
					if( support ) {
						$( this ).off( transEndEventName );
					}
					self.$item.removeClass( 'og-expanded' );
					self.$previewEl.remove();
				};

			setTimeout( $.proxy( function() {

				if( typeof this.$largeImg !== 'undefined' ) {
					this.$largeImg.fadeOut( 'fast' );
				}
				this.$previewEl.css( 'height', 0 );
				// the current expanded item (might be different from this.$item)
				var $expandedItem = $items.eq( this.expandedIdx );
                //console.log(this.expandedIdx);
				$expandedItem.css( 'height', $expandedItem.data( 'height' ) ).on( transEndEventName, onEndFn );

				if( !support ) {
					onEndFn.call();
				}
			}, this ), 25 );
			return false;
		},
		calcHeight : function() {

			var heightPreview = winsize.height - this.$item.data( 'height' ) - marginExpanded,
				itemHeight = winsize.height;

			if( heightPreview < settings.minHeight ) {
				heightPreview = settings.minHeight;
				itemHeight = settings.minHeight + this.$item.data( 'height' ) + marginExpanded;
			}

			this.height = heightPreview - scrollNavBar;
			this.itemHeight = itemHeight- scrollNavBar;

		},
		setHeights : function() {

			var self = this,
				onEndFn = function() {
					if( support ) {
						self.$item.off( transEndEventName );
					}
					self.$item.addClass( 'og-expanded' );
				};

			this.calcHeight();
			this.$previewEl.css( 'height', this.height );
			this.$item.css( 'height', this.itemHeight ).on( transEndEventName, onEndFn );

			if( !support ) {
				onEndFn.call();
			}

		},
		positionPreview : function() {
            //console.log('position preview');
            $('.annotation-point').remove();

            var self = this;

//			thisgrid.scrollToCurrentPreview().promise().done(function(){
//                updateAllPanels();
//            });
            this.scrollToPreview().promise().done(
                function () {
                    updateAllPanels();
                }
            );
		},
        scrollToPreview : function () {
            // scroll page
            // case 1 : preview height + item height fits in window´s height
            // case 2 : preview height + item height does not fit in window´s height and preview height is smaller than window´s height
            // case 3 : preview height + item height does not fit in window´s height and preview height is bigger than window´s height
            var position = this.$item.data( 'offsetTop' ),
                previewOffsetT = this.$previewEl.offset().top - scrollExtra,
                scrollVal = this.height + this.$item.data( 'height' ) + marginExpanded <= winsize.height ? position : this.height < winsize.height ? previewOffsetT - ( winsize.height - this.height ) : previewOffsetT;

            return $body.animate( { scrollTop : scrollVal- scrollNavBar },settings.speed );
        },
		setTransition  : function() {
			this.$previewEl.css( 'transition', 'height ' + settings.speed + 'ms ' + settings.easing );
			this.$item.css( 'transition', 'height ' + settings.speed + 'ms ' + settings.easing );
		},
		getEl : function() {
			return this.$previewEl;
		}
	}


    this.clickNextItem = function() {
        $('.og-expanded').next().children('a').trigger('click');
    }

    this.clickPrevItem = function() {
        $('.og-expanded').prev().children('a').trigger('click');
    }

    this.clickCurrItem = function () {
        $('.og-expanded > a').trigger('click');
    }



    // paramters for panels (load if already cached)
    var panelparams = {},
        stored = localStorage['panelparams'];
    if (stored) panelparams = JSON.parse(stored);


    /**
     *
     * @param panelid
     * @param show
     */
     this.togglePanel = function(panelid,show) {

        if (panelparams[panelid].open==false || show) {
            //console.log('show panel: '+panelid);
            if (!$(panelparams[panelid].btnid).hasClass('active')) $(panelparams[panelid].btnid).addClass('active');
            $(panelid).show();
            setPanelPos(panelid);
        }
        else {
            //console.log('hide panel: '+panelid);
            $(panelparams[panelid].btnid).removeClass('active');
            $(panelid).hide();
        }
        updatePanelData(panelid);
    }
    this.toggleDraggable = function (panelid) {
        if ($(panelid).hasClass('og-sidepane')) {
            makeDraggablePanel(panelid);
        }
        else {
            makeDocakablePanel(panelid);
        }
        updatePanelData (panelid);
    }

    function destroyAllPanels() {
        $('.og-grid .og-panel').each(function(i) {
            $(this).remove();
            $(panelparams['#'+$(this).attr('id')].btnid).unbind("click");
        });
    }


    function initAllPanels () {
        $('.og-grid .og-panel').each(function(i) {
            initPanel ('#'+$(this).attr('id'));
        });
    }
    function initPanel (panelid) {
        //console.log('init panel: '+panelid);

        // make panel draggable
        if ($(panelid).hasClass('og-dragpane')) makeDraggablePanel(panelid);

        // activate button to access panel
        var btnid = panelparams[panelid].btnid;
        $(btnid).click( function() {
            thisgrid.togglePanel(panelid);
        });
        $(btnid).attr('title',panelparams[panelid].title);
        $(btnid).tooltip({trigger:'hover',placement:'top',container:'body'});
        $(panelid+' .nav a[data-toggle="tab"]').on('shown', function (e) {
            updatePanelData(panelid);
            //console.log('tab shown '+panelparams[panelid].tabno);
        });
    }
    function makeDraggablePanel(panelid) {
        //console.log('make draggable');

        // Move to new container
        $(panelid).appendTo('.og-expander-inner');
        $(panelid+' #btn-panelpos').attr('class', 'icon-signin');
        $(panelid).removeClass('og-sidepane').addClass('og-dragpane');
        // make draggable
        $(panelid).draggable({
            scroll: false,
            containment: ".og-expander",
            //stack: ".og-dragpane",
            stop: function() {
                updatePanelData(panelid);
            }
        });
//        $(panelid).resizable({
//            containment: ".og-expander",
//            stop: function() {
//                updatePanelData(panelid);
//            }
//        });
        $(panelid).disableSelection();
        setPanelPos(panelid);
        panelparams[panelid].type = 'og-dragpane';
        //$(panelid+' #btn-panelpos').attr('class', 'icon-check-empty');
    }
    function makeDocakablePanel(panelid) {
        //console.log('make docakable');
        $(panelid+' #btn-panelpos').attr('class', 'icon-external-link');
        $(panelid).removeClass('og-dragpane').addClass('og-sidepane');
        $(panelid).appendTo('.og-sidepanel');
        $(panelid).draggable('destroy');
        //$(panelid).resizable('destroy');
        $(panelid).attr('style', 'display:block;');
        panelparams[panelid].type = 'og-sidepane';
    }



    function updateAllPanels() {
        $('.og-grid .og-panel').each(function(i) {
            updatePanel ('#'+$(this).attr('id'));
        });

        //if (!$('.og-sidepane')) $('.og-sidepanel').hide();
        //else $('.og-sidepanel').show();
    }
    function updatePanel (panelid) {
        //console.log('update panel: '+panelid);

        // make panel draggable
        if ($(panelid).hasClass('og-dragpane') && !$(panelid).is('.ui-draggable'))
            makeDraggablePanel(panelid);
        else if ($(panelid).hasClass('og-sidepane') && $(panelid).is('.ui-draggable'))
            makeDocakablePanel(panelid);

        //if (panelparams[panelid].open && !$(panelid).is(":visible")) togglePanel(panelid,true);
        if (panelparams[panelid].open) thisgrid.togglePanel(panelid,true);

        // trigger tab show event
        $(panelid+' ul.nav a[data-tabid="' + panelparams[panelid].tabno +'"]').tab('show');

    }

    function setPanelPos(panelid) {
        if ($(panelid).hasClass('og-dragpane')) {

            //console.log('BEFORE: top: '+panelparams[panelid].pos.top+' left: '+panelparams[panelid].pos.left);
            var maxtop = $window.innerHeight() - $(panelid).innerHeight()-100,
                maxleft = $window.innerWidth() - $(panelid).innerWidth()- 2;
            var top = Math.min(panelparams[panelid].pos.top, maxtop),
                left = Math.min(panelparams[panelid].pos.left,maxleft);

            $(panelid).css({
                position:'absolute'
                //width: panelparams[panelid].size.width,
                //height: panelparams[panelid].size.height
            });
            $(panelid).position({
                my: 'left top',
                at: 'left+'+left+' top+'+top,
                of: '.og-expander'
            });
        }
    }

    function updatePanelData (panelid) {
        panelparams[panelid].open = $(panelid).is(':visible');
        if ($(panelid+' .nav li.active a[data-toggle="tab"]').length)
            panelparams[panelid].tabno = $(panelid+' .nav li.active a[data-toggle="tab"]').data('tabid');
        if ($(panelid).hasClass('og-dragpane') && $(panelid).is(':visible')) {
            panelparams[panelid].pos = $(panelid).position();
            panelparams[panelid].size = {width: $(panelid).width(), height: $(panelid).height()};
            panelparams[panelid].type = 'og-dragpane';
        }
        else {
            panelparams[panelid].type = 'og-sidepane';
        }
        //console.log(panelparams);
        localStorage['panelparams'] = JSON.stringify(panelparams);
        $('#imganot .tab-pane').each(function() {
//            setFullHeight('#'+$(this).attr('id')+' .antag-taglist','.og-details');
            setFullHeight('#' + $(this).attr('id'), '.og-details');
            //console.log($(this).attr('id')+' .antag-taglist');
        });
    }



    // 'imgtools', 'Tools', 'icon-wrench', [{icon:'icon-adjust', content:'tools'},{icon:'icon-zoom-in', content:'zoom'}]
    function createPanel (panelid,title,icon,items,btnid,type,pos,open) {
        pos = ((typeof pos !== 'undefined') ? pos : {top: 0, left:0});
        open = ((typeof open !== 'undefined') ? open : false);

        if( ! panelparams.hasOwnProperty('#'+panelid)) panelparams['#'+panelid] = {};
        if( ! panelparams['#'+panelid].hasOwnProperty('title')) panelparams['#'+panelid].title = title;
        if( ! panelparams['#'+panelid].hasOwnProperty('btnid')) panelparams['#'+panelid].btnid = btnid;
        if( ! panelparams['#'+panelid].hasOwnProperty('open')) panelparams['#'+panelid].open = open;
        if( ! panelparams['#'+panelid].hasOwnProperty('pos')) panelparams['#'+panelid].pos = pos;
        if ( ! panelparams['#'+panelid].hasOwnProperty('open')) panelparams['#'+panelid].open = $('#'+panelid).is(':visible') ? true : false;
        if( ! panelparams['#'+panelid].hasOwnProperty('tabno')) panelparams['#'+panelid].tabno = 0;
        if( ! panelparams['#'+panelid].hasOwnProperty('type')) panelparams['#'+panelid].type = type;


        var $panel, $navbar, $tabs, $title, $navul, $navctrl, $tablink, $tabli, active, $panelposlink, $panelhidelink;

        $title = $('<span class="navbar-brand" ><i class="'+icon+'"></i> '+title+'</span>');
        $navctrl = $('<ul class="nav navbar-nav navbar-right"></ul>');

        $panelposlink = $('<li><a href="javascript:void(0)"><i id="btn-panelpos" class="icon-external-link"></i></a></li>');
        $panelhidelink = $('<li><a href="javascript:void(0)"><i class="icon-minus"></i></a></li>');
        $navctrl.append($panelposlink,$panelhidelink);
        $panelposlink.find('a').click(function () {thisgrid.toggleDraggable('#'+panelid)});
        $panelhidelink.find('a').click(function () {thisgrid.togglePanel('#'+panelid)});

        $navul = $('<ul class="nav navbar-nav "></ul>');
        $tabs = $('<div class="tab-content"></div>');

        for (var i in items) {
            active = '';//(i==panelparams['#'+panelid].tabno) ? 'active' : '';
            $tablink = $('<a data-tabid="'+i+'" href="#'+panelid+'-'+i+'" data-toggle="tab" data-trigger="click"><i class="'+items[i].icon+'"></i></a>');
            if (items[i].hasOwnProperty('onshow')) $tablink.on('shown',items[i].onshow);
            $tabli = $('<li class="'+active+'" title="'+items[i].content+'"></li>');
            $tabli.tooltip({trigger:'hover',placement:'top',container:'body'})
            $navul.append( $tabli.append($tablink));
            $tabs.append( $('<div class="tab-pane '+active+'" id="'+panelid+'-'+i+'">'+items[i].content+'</div>'));
        }

        $navbar=$('<div class="navbar"></div>').append($title,$navul,$navctrl);

        $panel = $('<div id="'+panelid+'" class="og-panel"></div>').append($navbar,$tabs);

        //$panel.addClass(type);
        $panel.addClass(panelparams['#'+panelid].type);


        //$panel.data('btnid',btnid);

        return $panel;
    }

    function initZoom () {
        var zoomid='#imgtools-0',
            imgid = '#og-main-img',
            zoompanelclass = 'zoompanel';

        var imgH2W = $(imgid).height()/$(imgid).width();

//        if ($(zoomid+'>.'+zoompanelclass).length > 0 ) {
//            $zoompanel  =$(zoomid+'>.'+zoompanelclass);
//        }
//        else {

            var $zoompanel=$('<div class="'+zoompanelclass+'"><i class="icon-circle"></i></div>'),
            //var $zoompanel=$('<div class="'+zoompanelclass+'"></div>'),
                $zoomslider = $('<div id="zoomslider"></div>');

            if (!$zoompanel.data().hasOwnProperty('zoomwidth')) $zoompanel.data().zoomwidth=3000;
            $(zoomid).html($zoompanel.append($zoomslider));
            $zoomslider.slider({
                orientation:'vertical',
                range: 'min',
                min:1360,
                max:8000,
                value:$zoompanel.data().zoomwidth,
                slide: function (e,ui) {
                    imgH2W = $(imgid).height()/$(imgid).width();
                    $zoompanel.data().zoomwidth = ui.value;
                    $zoompanel.css({'background-size': ui.value+'px '+(ui.value*imgH2W)+'px'});
                    //$(this).find('.ui-slider-handle').text(Math.round(ui.value/13.6));
                }
            })
//        }

        $zoompanel.css({'background-image':'url("'+$(imgid).attr('src')+'")', 'background-size': $zoompanel.data().zoomwidth+'px '+($zoompanel.data().zoomwidth*imgH2W)+'px'});
    }

    function getImageInfo() {
        var infoid = '#imginfo-0',
            imginfo = thlist.getImageInfo(globalstate.imid);

        var position = imginfo.position.replace(/.*\(|\)/gi,'').split(' ');
        $(infoid).html('<b>Image ID:</b> '+globalstate.imid+' (<a href="javascript:void(0)" onclick="$(\'#map-nav\').tab(\'show\')">show on map</a>)');
        $(infoid).append('<br><b>Timestamp:</b> '+imginfo.date_time);
        $(infoid).append('<br><b>Depth:</b> '+imginfo.depth+' m');
        $(infoid).append('<br><b>LAT:</b> '+position[1]);
        $(infoid).append('<br><b>LON:</b> '+position[0]);

        if (imginfo.measurements.length > 0) {
            for (var i= 0; i < imginfo.measurements.length; i++) {
                $(infoid).append('<br><b>'+imginfo.measurements[i].name+': </b>'+imginfo.measurements[i].value+' '+imginfo.measurements[i].units);
            }
        }
        $(infoid).enableSelection();
    }

    function attachImgMouseEvents() {
        $('.og-expander').data('draw',false);
        $('.og-expander').disableSelection();
        //Capture and handle mouse events on thumbnail grid
        $grid.on("mousemove mousedown mouseup contextmenu", imgMouseEvents );

    }

    function showPointContextMenu($point) {
        //console.log($point.data());
        var select_action = "Select all similar",
            select = true;
        if ($point.hasClass('apcol-selected')) {
            select_action = "Unselect all similar";
            select = false;
        }

        var point_offset_top = $point.offset().top+$point.height()/2 - $grid.offset().top,
            point_offset_left = $point.offset().left+$point.width()/2,
            $modifier_item = $('<li><a href="javascript:void(0)">Add modifier</a></li>'),
            $comment_item = $('<li><a href="javascript:void(0)">Add comment</a></li>'),
            $select_label = $('<li><a href="javascript:void(0)">'+select_action+'</a></li>');

        var $menu = $('<div class="og-contextmenu" style="top:'+point_offset_top+'px;left:'+point_offset_left+'px;"></div>').append($('<ul class="nav nav-stacked"></ul>').append($select_label,$modifier_item,$comment_item));

        $modifier_item.click(function() {
            showPointModifiers($point,$menu);
        });
        $comment_item.click(function() {
            show_note('Not implemented yet','This feature has not been implemented yet. Please stand by.','error',true);
            $menu.remove();
        });

        $select_label.click(function() {
            $('.annotation-point[data-title="' + $point.attr('data-title') + '"]').each(function(i, el) {
                selectAnnotationPoint(el, select);
            });
            $menu.remove();
        });


        if ($('.og-contextmenu').length>0) $('.og-contextmenu').remove();
        $grid.append($menu);
    }


    function showTagContextMenu($tag,x,y) {
        //console.log($point.data());
        var offset_top = y - $grid.offset().top,// - $tag.parent().offset().top,
            offset_left = x,// - $tag.parent().offset().left,
            $fav_item = $('<li><a href="javascript:void(0)">Add to favourites</a></li>'),
            $exmpl_item = $('<li><a href="javascript:void(0)">See examples</a></li>');

        var $menu = $('<ul class="og-contextmenu nav nav-stacked" style="top:'+offset_top+'px;left:'+offset_left+'px;"></ul>').append($exmpl_item,$fav_item);

        $exmpl_item.click(function () {
            showTagExampleModal($tag.data().label);
            $menu.remove();
        });
        $fav_item.click(function() {
            show_note('Not implemented yet','This feature has not been implemented yet. Please stand by.','error',true);
            $menu.remove();
        });

        if ($('.og-contextmenu').length>0) $('.og-contextmenu').remove();
        $grid.append($menu);
    }


    function showPointModifiers($point,$menu) {
        $menu.html('');
        var $modifiers = $('<select multiple="multiple" id="id_deployment_ids" name="deployment_ids" size="10" style="width:150px"></select>');
        var $submit = '';
        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: '/api/dev/qualifier_code/?limit=0',
            success: function (mds) {
                if (mds.objects.length > 0) {
                    for (var i = 0; i < mds.objects.length; i++) {
                        $modifiers.append('<OPTION VALUE="'+mds.objects[i].resource_uri+'">'+mds.objects[i].modifier_name);
                    }
                    $submit = $('<button style="width:150px">Update</button>');
                    $submit.click(function() {
                        var modifiers_arr = [], modifier_names = [];
                        $modifiers.children("option").filter(":selected").each(function (i, o) {
                            modifiers_arr.push($(o).val());
                            modifier_names.push($(o).text());
                            //modifiers_arr = $(this).val();
                        });
//                        console.log(modifiers_arr);
//                        console.log(modifier_names);
//                        console.log($point.data('resource_uri'));

                        //console.log($point.data());
                        //updateModifiers($point.data('resource_uri'), modifiers_arr);
                        labelSelectedPoints(null, '', '', modifiers_arr, modifier_names);
                        $menu.remove();
                    });
                    selectAnnotationPoint($point[0],true);
                }
                else {
                    $modifiers.append('<OPTION VALUE="">No modifiers found');
                }
            }
        });
        $menu.append($modifiers,$('<br>'),$submit);
    }




    function imgMouseEvents( e ) {

        var dp = $('.og-expander');

        if (e.type == 'contextmenu'){
            if ($(e.target).hasClass('annotation-point') ) {
                e.preventDefault();
                showPointContextMenu($(e.target));
            }
            else if ($(e.target).hasClass('annotation-tag')) {
                e.preventDefault();
                showTagContextMenu($(e.target), e.pageX, e.pageY);
            }
        }
        else if (e.type == 'mousedown' && $(e.target).parents('.og-contextmenu').length==0) {
            $('.og-contextmenu').remove();
        }

        if ($(e.target).hasClass('og-fullimg') || $(e.target).attr('id')=='og-main-img' || dp.data('draw')) {

            var pageX = e.pageX - dp.offset().left,
                pageY = e.pageY - dp.offset().top,
                dpLast = dp.find('.drawnBox'),
                dpLast_data = dpLast.data();

            if ( e.type === 'mousemove' ) {
                var drawCSS = {};

                // If drawing is initiated.
                if ( dp.data('draw') ) {
                    // Determine the direction.
                    // xLeft
                    if ( dpLast_data.pageX > pageX ) {
                        drawCSS['right'] = dp.width() - dpLast_data.pageX,
                            drawCSS['left'] = 'auto',
                            drawCSS['width'] = dpLast_data.pageX - pageX;
                    }
                    // xRight
                    else if ( dpLast_data.pageX < pageX ) {
                        drawCSS['left'] = dpLast_data.pageX,
                            drawCSS['right'] = 'auto',
                            drawCSS['width'] = pageX - dpLast_data.pageX;
                    }

                    // yUp
                    if ( dpLast_data.pageY > pageY ) {
                        drawCSS['bottom'] = dp.height() - dpLast_data.pageY,
                            drawCSS['top'] = 'auto',
                            drawCSS['height'] = dpLast_data.pageY - pageY;
                    }
                    // yDown
                    else if ( dpLast_data.pageY < pageY ) {
                        drawCSS['top'] = dpLast_data.pageY,
                            drawCSS['bottom'] = 'auto',
                            drawCSS['height'] = pageY - dpLast_data.pageY;
                    }
                    dpLast.css( drawCSS );
                }
            }

            if ( e.type === 'mousedown' && e.which == 1) { // if mouse down (with left click) start draw
                // If ".drawnBox.last" doesn't exist, create it.
                if ( dpLast.length < 1 ) dpLast = $('<div class="drawnBox"></div>');
                dpLast.appendTo( dp );
                e.preventDefault();
                dp.data('draw',true);
                dpLast.data({ "pageX": pageX, "pageY": pageY });
                dpLast.removeClass('hide');

            }
            else if ( e.type === 'mouseup' && dp.data('draw') ) { // if mouse up while drawing, end drawing
                var bbleft = dpLast.offset().left,
                    bbright = dpLast.offset().left+dpLast.width(),
                    bbtop = dpLast.offset().top,
                    bbbottom = dpLast.offset().top+dpLast.height(),
                    aptop, apleft;

                $('.annotation-point').each(function() {
                    aptop = $(this).offset().top - parseInt($(this).css('margin-top'));
                    apleft = $(this).offset().left - parseInt($(this).css('margin-left'));
                    if (apleft < bbright
                        && apleft > bbleft
                        && aptop < bbbottom
                        && aptop > bbtop) selectAnnotationPoint(this);
                });
                dp.data('draw',false);
                dpLast.remove();
            }
        }

        // update zoom if over image or annotation point and zoom panel is visible
        if(($(e.target).attr('id')=='og-main-img' || $(e.target).hasClass('annotation-point')) && $('#imgtools-0').is(":visible")) {
            //console.log('update zoom');
            var $zoomBox = $('#imgtools-0>.zoompanel'),
                $mainimg = $('#og-main-img'),
                $zoompoint = $zoomBox.find('i');

            var imgX = e.pageX - $mainimg.offset().left,
                imgY = e.pageY - $mainimg.offset().top,
                imgwidth = $mainimg.width(),
                imgheight = $mainimg.height(),
                boxwidth=$zoomBox.width(),
                boxheight=$zoomBox.height(),
                imgscale=$zoomBox.data().zoomwidth/imgwidth;

            var bgimgoffset_x = boxwidth/2-(imgX)*imgscale,
                bgimgoffset_y = boxheight/2-(imgY)*imgscale;

            $zoomBox.css('background-position',bgimgoffset_x+'px '+bgimgoffset_y+'px');
            if ($(e.target).hasClass('annotation-point')) { // if annotation point, show point in zoom
                var zoompoint_x = $(e.target).data().position.x*imgscale*imgwidth + bgimgoffset_x,
                    zoompoint_y = $(e.target).data().position.y*imgscale*imgheight + bgimgoffset_y;

                $zoompoint.css({top:zoompoint_y+'px',left:zoompoint_x+'px'});
                $zoompoint.show();
                //console.log(zoompoint_x+', '+zoompoint_y);
            } else {
                $zoompoint.hide();
            }
        }
    }
/*
	return { 
		init : init,
		addItems : addItems,
        saveItemInfo : saveItemInfo,
        isloading : checkIfLoading()
        //clickNextItem : clickNextItem,
        //clickPrevItem : clickPrevItem,
        //clickCurrItem : clickCurrItem,
        //togglePanel : togglePanel,
        //toggleDraggable: toggleDraggable
	};
*/
};

/*
function isScrolledIntoView(elem)
{
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}
*/
/*****************************************************************************
 * Annotation points
 *****************************************************************************/

var taglist = new AnnotationAPI({});




/*****************************************************************************
 * Additional plugins
 *****************************************************************************/


/*
 * debouncedresize: special jQuery event that happens once after a window resize
 *
 * latest version and complete README available on Github:
 * https://github.com/louisremi/jquery-smartresize/blob/master/jquery.debouncedresize.js
 *
 * Copyright 2011 @louis_remi
 * Licensed under the MIT license.
 */
var $event = $.event,
    $special,
    resizeTimeout;

$special = $event.special.debouncedresize = {
    setup: function() {
        $( this ).on( "resize", $special.handler );
    },
    teardown: function() {
        $( this ).off( "resize", $special.handler );
    },
    handler: function( event, execAsap ) {
        // Save the context
        var context = this,
            args = arguments,
            dispatch = function() {
                // set correct event type
                event.type = "debouncedresize";
                $event.dispatch.apply( context, args );
            };

        if ( resizeTimeout ) {
            clearTimeout( resizeTimeout );
        }

        execAsap ?
            dispatch() :
            resizeTimeout = setTimeout( dispatch, $special.threshold );
    },
    threshold: 250
};

// ======================= imagesLoaded Plugin ===============================
// https://github.com/desandro/imagesloaded

// $('#my-container').imagesLoaded(myFunction)
// execute a callback when all images have loaded.
// needed because .load() doesn't work on cached images

// callback function gets image collection as argument
//  this is the container

// original: MIT license. Paul Irish. 2010.
// contributors: Oren Solomianik, David DeSandro, Yiannis Chatzikonstantinou

// blank image data-uri bypasses webkit log warning (thx doug jones)
var BLANK = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==';

$.fn.imagesLoaded = function( callback ) {
    var $this = this,
        deferred = $.isFunction($.Deferred) ? $.Deferred() : 0,
        hasNotify = $.isFunction(deferred.notify),
        $images = $this.find('img').add( $this.filter('img') ),
        loaded = [],
        proper = [],
        broken = [];

    // Register deferred callbacks
    if ($.isPlainObject(callback)) {
        $.each(callback, function (key, value) {
            if (key === 'callback') {
                callback = value;
            } else if (deferred) {
                deferred[key](value);
            }
        });
    }

    function doneLoading() {
        var $proper = $(proper),
            $broken = $(broken);

        if ( deferred ) {
            if ( broken.length ) {
                deferred.reject( $images, $proper, $broken );
            } else {
                deferred.resolve( $images );
            }
        }

        if ( $.isFunction( callback ) ) {
            callback.call( $this, $images, $proper, $broken );
        }
    }

    function imgLoaded( img, isBroken ) {
        // don't proceed if BLANK image, or image is already loaded
        if ( img.src === BLANK || $.inArray( img, loaded ) !== -1 ) {
            return;
        }

        // store element in loaded images array
        loaded.push( img );

        // keep track of broken and properly loaded images
        if ( isBroken ) {
            broken.push( img );
        } else {
            proper.push( img );
        }

        // cache image and its state for future calls
        $.data( img, 'imagesLoaded', { isBroken: isBroken, src: img.src } );

        // trigger deferred progress method if present
        if ( hasNotify ) {
            deferred.notifyWith( $(img), [ isBroken, $images, $(proper), $(broken) ] );
        }

        // call doneLoading and clean listeners if all images are loaded
        if ( $images.length === loaded.length ){
            setTimeout( doneLoading );
            $images.unbind( '.imagesLoaded' );
        }
    }

    // if no images, trigger immediately
    if ( !$images.length ) {
        doneLoading();
    } else {
        $images.bind( 'load.imagesLoaded error.imagesLoaded', function( event ){
            // trigger imgLoaded
            imgLoaded( event.target, event.type === 'error' );
        }).each( function( i, el ) {
                var src = el.src;

                // find out if this image has been already checked for status
                // if it was, and src has not changed, call imgLoaded on it
                var cached = $.data( el, 'imagesLoaded' );
                if ( cached && cached.src === src ) {
                    imgLoaded( el, cached.isBroken );
                    return;
                }

                // if complete is true and browser supports natural sizes, try
                // to check for image status manually
                if ( el.complete && el.naturalWidth !== undefined ) {
                    imgLoaded( el, el.naturalWidth === 0 || el.naturalHeight === 0 );
                    return;
                }

                // cached images don't fire load sometimes, so we reset src, but only when
                // dealing with IE, or image is complete (loaded) and failed manual check
                // webkit hack from http://groups.google.com/group/jquery-dev/browse_thread/thread/eee6ab7b2da50e1f
                if ( el.readyState || el.complete ) {
                    el.src = BLANK;
                    el.src = src;
                }
            });
    }

    return deferred ? deferred.promise( $this ) : $this;
};