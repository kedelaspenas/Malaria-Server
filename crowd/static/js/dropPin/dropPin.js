/*!
* dropPin - because image maps are icky
* http://duncanheron.github.com/dropPin/
*
*/
(function( $ ){

	var pinType = -1;

	$.fn.dropPin = function(method) {

		var defaults = {
		fixedHeight: 500,
		fixedWidth: 500,
		dropPinPath: '/js/dropPin/',
		pin: 'dropPin/defaultpin@2x.png',
		pinF: '../static/images/pinF.png',
        pinV: '../static/images/pinV.png',
        pinO: '../static/images/pinO.png',
        pinM: '../static/images/pinM.png',
		backgroundImage: 'dropPin/access-map.png',
		backgroundColor: '#9999CC',
		xoffset : 12,
		yoffset : 37, //need to change this to work out icon heigh/width then subtract margin from it
		cursor: 'crosshair',
		pinclass: '',
		userevent: 'click',
		hiddenXid: '#xcoord', //used for saving to db via hidden form field
		hiddenYid: '#ycoord', //used for saving to db via hidden form field
		pinX: false, //set to value if you pass pin co-ords to overirde click binding to position
		pinY: false, //set to value if you pass pin co-ords to overirde click binding to position
		pinDataSet: '', //array of pin coordinates for front end render
		pinType: -1
	}



	var methods = {
		init: function(options) {

			var options =  $.extend(defaults, options);
			var thisObj = this;

			this.css({'cursor' : options.cursor/*, 'background-color' : options.backgroundColor /*, 'background-image' : "url('"+options.backgroundImage+"')"*/,'height' : options.fixedHeight , 'width' : options.fixedWidth});
			this.html("<img src='"+options.backgroundImage+"' />");
			var i = 10;
			
			thisObj.on(options.userevent, function (ev) {
                if (pinType == -1)
                    return;

				$('.pin').remove();

				i = i + 10;
				var $img = $(thisObj);
				var offset = $img.offset();
				var x = ev.pageX - offset.left;
				var y = ev.pageY - offset.top;

				var xval = (x - options.xoffset);
				var yval = (y - options.yoffset);
				var imgC = $('<img class="pin">');
				imgC.css('top', yval+'px');
				imgC.css('left', xval+'px');
				imgC.css('z-index', i);
				
				imgC.attr('src',  options.pin);

				imgC.appendTo(thisObj);
				$(options.hiddenXid).val(xval);
				$(options.hiddenYid).val(yval);

				// add hidden fields - can use these to save to database
				var hiddenCtl= $('<input type="hidden" name="hiddenpin" class="pin">');
		        hiddenCtl.css('top', y);
		        hiddenCtl.css('left', x);
		        hiddenCtl.val("(" + x + "," + y + ")");
                if(pinType == 0) {
                    hiddenCtl.attr('maltype', 'F');
                } else if (pinType == 1) {
                    hiddenCtl.attr('maltype', 'V');
                } else if (pinType == 2) {
                    hiddenCtl.attr('maltype', 'O');
                } else if (pinType == 3) {
                    hiddenCtl.attr('maltype', 'M');
                }
		        hiddenCtl.appendTo(thisObj);

			});

		},
		dropMulti: function(options) {

			var justremoved = false;

			var options =  $.extend(defaults, options);
			var thisObj = this;

			thisObj.css({'cursor' : options.cursor/*, 'background-color' : options.backgroundColor , 'background-image' : "url('"+options.backgroundImage+"')"*/,'height' : options.fixedHeight , 'width' : options.fixedWidth});
			thisObj.append("<img id='zoom_01' style='z-index: -2' src='"+options.backgroundImage+"' height='"+options.fixedHeight+"px' width='"+options.fixedWidth+"px' data-zoom-image='"+options.zoomImage+"' />");
			var i = 10;

			//var test = $('#map img');

			//test.on(options.userevent, function (ev) {
			thisObj.on(options.userevent, function (ev) {

				if(!justremoved) {

					i = i + 10;
					var $img = $(thisObj);
					var offset = $img.offset();
					var x = ev.pageX - offset.left;
					var y = ev.pageY - offset.top;

					var xval = (x - options.xoffset);
					var yval = (y - options.yoffset);
					var imgC = $('<img class="pin">');

					imgC.css('top', yval+'px');
					imgC.css('left', xval+'px');
					imgC.css('z-index', i);

					if(pinType == 0) {
                        imgC.attr('src',  options.pinF);
                    } else if (pinType == 1) {
                        imgC.attr('src',  options.pinV);
                    } else if (pinType == 2) {
                        imgC.attr('src',  options.pinO);
                    } else if (pinType == 3) {
                        imgC.attr('src',  options.pinM);
                    }
                    
					imgC.attr('pinnum', i);
					imgC.attr('pinType', pinType)

					imgC.appendTo(thisObj);
					// console.log(ev.target);
					$(options.hiddenXid).val(xval);
					$(options.hiddenYid).val(yval);

					// add hidden fields - can use these to save to database
					var hiddenCtl= $('<input type="hidden" name="hiddenpin" class="pin">');
			        hiddenCtl.css('top', y);
			        hiddenCtl.css('left', x);
			        hiddenCtl.val("(" + x + "," + y + ")");
			        hiddenCtl.attr('pinnum', i);
					if(pinType == 0) {
                        hiddenCtl.attr('maltype', 'F');
                    } else if (pinType == 1) {
                        hiddenCtl.attr('maltype', 'V');
                    } else if (pinType == 2) {
                        hiddenCtl.attr('maltype', 'O');
                    } else if (pinType == 3) {
                        hiddenCtl.attr('maltype', 'M');
                    }
			        hiddenCtl.appendTo(thisObj);

			        imgC.on(options.userevent, function (ev) {
                        if(imgC.attr('pinType') == pinType) {
                            imgC.remove();
                            hiddenCtl.remove();
                            i = i - 10;
                            justremoved = true;
                        }
					});
		    	}
		    	
		    	justremoved = false;

			});

		},
		showPin: function(options) {

			var options =  $.extend(defaults, options);

			this.css({'cursor' : options.cursor, 'background-color' : options.backgroundColor , 'background-image' : "url('"+options.backgroundImage+"')",'height' : options.fixedHeight , 'width' : options.fixedWidth});

			var xval = (options.pinX);
			var yval = (options.pinY);
			var imgC = $('<img class="pin">');
			imgC.css('top', yval+'px');
			imgC.css('left', xval+'px');

			imgC.attr('src',  options.pin);

			imgC.appendTo(this);
			$(options.hiddenXid).val(xval);
			$(options.hiddenYid).val(yval);

		},
		showPins: function(options) {

			var options =  $.extend(defaults, options);

			this.css({'cursor' : options.cursor, 'background-color' : options.backgroundColor , 'background-image' : "url('"+options.backgroundImage+"')",'height' : options.fixedHeight , 'width' : options.fixedWidth});

			for(var i=0; i < (options.pinDataSet).markers.length; i++)
			{
				var dataPin = options.pinDataSet.markers[i];

				var imgC = $('<img rel="/map-content.php?id='+dataPin.id+'" class="pin '+options.pinclass+'" style="top:'+dataPin.ycoord+'px;left:'+dataPin.xcoord+'px;">');
			  	if(dataPin.pinType == 0) {
                    imgC.attr('src',  options.pinF);
                } else if (dataPin.pinType == 1) {
                    imgC.attr('src',  options.pinV);
                } else if (dataPin.pinType == 2) {
                    imgC.attr('src',  options.pinO);
                } else if (dataPin.pinType == 3) {
                    imgC.attr('src',  options.pinM);
                }
				imgC.attr('title',  dataPin.title);

				imgC.appendTo(this);
			}

		},

		pinTypeNone: function(options) {

            var options =  $.extend(defaults, options);
            var thisObj = this;

            pinType = -1;

        },

		pinTypeF: function(options) {

            var options =  $.extend(defaults, options);
            var thisObj = this;

            pinType = 0;

        },

        pinTypeV: function(options) {

            var options =  $.extend(defaults, options);
            var thisObj = this;

            pinType = 1;

        },

        pinTypeO: function(options) {

            var options =  $.extend(defaults, options);
            var thisObj = this;

            pinType = 2;

        },

        pinTypeM: function(options) {

            var options =  $.extend(defaults, options);
            var thisObj = this;

            pinType = 3;

        }
	};

	if (methods[method]) {

		return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));

	} else if (typeof method === 'object' || !method) {

		return methods.init.apply(this, arguments);

	} else {

		alert("method " + method + " does not exist");

	}


}

})( jQuery );
