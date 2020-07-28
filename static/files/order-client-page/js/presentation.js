/* Полезные функции */
Number.prototype.clamp = function(min, max) {
  return Math.min(Math.max(this, min), max);
};
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
function fullScreen(elem) {
	if(elem !== false){
		if(elem.requestFullscreen){
			elem.requestFullscreen();
		}else if(elem.msRequestFullscreen){
			elem.msRequestFullscreen();
		}else if(elem.mozRequestFullScreen){
			elem.mozRequestFullScreen();
		}else if(elem.webkitRequestFullscreen){
			elem.webkitRequestFullscreen();
		}
		$(elem).mousemove(function(e){
			e.stopPropagation();
			e.stopImmediatePropagation();
			$this = $(this);
			clearTimeout(timer);
			$this.removeClass('sleep');
			timer = setTimeout(function(){
				$this.addClass('sleep');
			},1000);
		});
	}else{
		if(document.cancelFullScreen){
			document.cancelFullScreen();
		}else if(document.webkitCancelFullScreen){
			document.webkitCancelFullScreen();
		}else if(document.mozCancelFullScreen){
			document.mozCancelFullScreen();
		}
	}
}

var timer;

(function() {
	/* Коллекция поддерживаемых анимация смены слайдов */
	var effects = {
		slideRight : function(c){
			c.css('left','100%').animate({left:0},300).next().animate({left:'-100%'},300);
		},
		smooth : function(c){
			c.next().animate({opacity:0},300);
		},
		spin : function(c){
			c = c.next();
			$({deg: 0}).animate({deg: 360}, {
				duration: 900,
				step: function(now) {
					c.css({
						transform: 'rotate(' + now + 'deg) scale('+(1 - (now / 360))+','+(1 - (now / 360))+')',
						opacity: 1 - (now / 360),
					});
				}
			});
		},
		perspective : function(c){
			n = c.next().css('transform','perspective(900px)')
			c.css('transform','perspective(900px)')
			$({deg: 0}).animate({deg: 180}, {
				duration: 700,
				step: function(now) {
					if(now > 90){
						n.css('opacity',0);
					}
					n.css({
						'transform': 'rotateY(' + now + 'deg)',
						'-webkit-transform': 'rotateY(' + now + 'deg)',
					});
					c.css({
						'transform': 'rotateY(' + (180-now) + 'deg)',
						'-webkit-transform': 'rotateY(' + (180-now) + 'deg)',
					});
				},
				complete: function(){
					c.css('transform','');
				}
			});
		},
	};
	/* Список всех фотографий с параметрами */
	var json = {};
	$('[data-pn]').each(function(index, item){
		var $item 	 = $(item);
		var data_pn  = $item.data('pn');

		var data_src = $item.data('src');
		var image_paths       = data_src.split(",");
		image_paths 		  = image_paths.filter(function(e){return e});

		image_paths_main_array = [];
		for(i=1;i<=image_paths.length;i++)
		{
			image_path_style_dict = {};
			
			image_path_style_dict['id'] 		= image_paths[i-1];
			image_path_style_dict['duration']   = 1;

			if(i%3 == 1 )
			{
				image_path_style_dict['effect']     = 'spin';
			}
			else if(i%3 == 2)
			{
				image_path_style_dict['effect']     = 'perspective';
			}
			else
			{
				image_path_style_dict['effect']     = 'smooth';
			}
			

			image_paths_main_array.push(image_path_style_dict);
		}

		json[data_pn]  = image_paths_main_array;
		
	});


	// var json = {
	// 	1 : [
	// 		{
	// 			id : 1,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 1,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 1,
	// 			duration : 1,
	// 			effect : 'perspective',
	// 		},
	// 		{
	// 			id : 1,
	// 			duration : 3,
	// 			effect : 'smooth',
	// 		},
	// 	],
	// 	2 : [
	// 		{
	// 			id : 2,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 2,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 2,
	// 			duration : 1,
	// 			effect : 'perspective',
	// 		},
	// 		{
	// 			id : 2,
	// 			duration : 3,
	// 			effect : 'smooth',
	// 		},
	// 	],
	// 	3 : [
	// 		{
	// 			id : 3,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 3,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 3,
	// 			duration : 1,
	// 			effect : 'perspective',
	// 		},
	// 		{
	// 			id : 3,
	// 			duration : 3,
	// 			effect : 'smooth',
	// 		},
	// 	],
	// 	4 : [
	// 		{
	// 			id : 4,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 4,
	// 			duration : 1,
	// 			effect : 'spin',
	// 		},
	// 		{
	// 			id : 4,
	// 			duration : 1,
	// 			effect : 'perspective',
	// 		},
	// 		{
	// 			id : 4,
	// 			duration : 3,
	// 			effect : 'smooth',
	// 		},
	// 	],
	// };

	/* Инициализация галерей */
	var $all = {};
	$('[data-pn]').each(function(index, item){
		var $item = $(item);
		var data = $item.data();
		$all[data.pn] = $item;
		$item.scrolled = 0;
		$item.current = 0;
		$item.to = function(index, e, loop){
			if(e == true && index == json[data.pn].length){
				index = 0;
				e = 0;
			}else if(e == false && index == -1){
				index = json[data.pn].length - 1;
				e = 11;
			}
			if(loop === undefined && this.timeout !==undefined){
				clearTimeout(this.timeout);
				$(this).find('.pn-play').removeClass('active');
			}
			if(this.current != index || loop !== true){
				if(e !== undefined){
					var ribbon = this.find('.pn-ribbon');
					if(typeof(e) != 'number'){
						var half = typeof(e) == 'boolean' ? e : ((e.pageX - ribbon.offset().left) > ribbon.width()/2);
						if(!(((this.scrolled >= this.find('li').length - 9) && half) || ((this.scrolled <= 0) && !half))){
							this.scrolled = this.scrolled + (!half ? -1 : 1);
						}
					}else{
						this.scrolled = (index - 8).clamp(0, json[data.pn].length - 1);
					}
					ribbon.children().animate({left:(-this.scrolled * 92)+'px'}, 300);
					this.find('.pn-carret').animate({left:(92 * (index))+'px'},300);
				}
				var c = this.find('.pn-current');
				this.find('.pn-temp').remove();
				c.clone().removeClass('pn-current').addClass('pn-temp').insertAfter(c);
				c.css('background-image','url('+json[data.pn][index].id+')')
				effects[(json[data.pn][index].effect && effects[json[data.pn][index].effect]) ? json[data.pn][index].effect : 'smooth'](c);
				this.current = index;
			}
			if(loop !== undefined){
				if(!loop){
					clearTimeout(this.timeout);
					return;
				}
				var last = json[data.pn][this.current + 1] === undefined;
				this.timeout = setTimeout(function(){
					if(last){
						$item.to(0, 0, false);
						$item.find('.pn-play').removeClass('active');
					}else{
						$item.to($item.current + 1, true, true);
					}
				},(json[data.pn][$item.current].duration !== undefined ? json[data.pn][$item.current].duration : 3) * 1000);
			}
		}

		var lis = '<div class="pn-carret"></div>';
		$item.addClass('pn-container')//.css('width','100%').css('height','705px')
		.html('<span class="pn-fullscreen fa fa-2x fa-arrows-alt"></span><div class="pn-current"></div><div class="pn-prev"><i class="fa fa-angle-left"></i></div><div class="pn-next"><i class="fa fa-angle-right"></i></div><div class="pn-bar"></span><span class="fa fa-3x pn-play"><i class="fa-angle-right"></i><i class="fa-angle-left"></i></span><div class="pn-ribbon"><ul class="pn-train"></ul></div></div>')
		.find('.pn-play').click(function(e){
			if($(this).hasClass('active')){
				$item.to(0, 0, false);
			}else{
				$item.to($item.current, undefined, true);
			}
			$(this).toggleClass('active');
		});
		$item.find('.pn-prev, .pn-next').click(function(){
			var next = $(this).hasClass('pn-next');
			var index = ($item.current + (next ? 1 : -1));
			if (index != $item.current){
				$item.to(index, next);
			}
		});
		$item.find('.pn-fullscreen').click(function(){
			fullScreen($(this).hasClass('active') ? false : $item[0]);
			$(this).toggleClass('active');
		});

		for(var i = 0; i < json[data.pn].length; i++){
			lis += '<li style="background-image:url('+json[data.pn][i].id+')"></li>';
		}
		$item.find('.pn-train').html(lis).css('width',$item.find('.pn-train').children('li').length * 92 + 'px').children('li').click(function(e){
			$(this).parent().children('li').removeClass('active');
			$(this).addClass('active');
			$item.to($(this).index() - 1, e);
		});
	});


	/* Подгрузка изображений */
	var loadImage = function(i, j){
		console.log(json[i][j].id)
		var img = new Image;
		img.src = json[i][j].id;
		json[i][j].loading = true;
		img.onload = function(){
			delete json[i][j].loading;
			if(($all[i] !== undefined) && (j == 0)){
				$all[i].to($all[i].current);
			}
		}
		img = null;
	}
	for(var i = 1; i < Object.size(json)+1; i++){
		for(var j = 0; j < json[i].length; j++){
			if(typeof(json[i][j]) == 'number'){ json[i][j] = { id : json[i][j] }; }
			loadImage(i, j);
		}
	}
})();
