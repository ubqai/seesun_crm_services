function test(){
	console.log("it is all ok");
}
//menu固定
$(function(){
	if($(".nav-tab").length>0){
		var key;
		$(window).bind("scroll", function(){
				var dis = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
				if(dis>60&&key!=1) {
						$(".nav-tab").addClass("fixed-menu");
						$(".header").addClass("fixed-margin");
						key=1;
				}else if(dis<=60){
						$(".nav-tab").removeClass("fixed-menu");
						$(".header").removeClass("fixed-margin");
						key=0;
				}
		})			
	}
})
//menu移动 -- not used anymore
$(function(){
	$("#to_sport").click(function(){
		$("html,body").animate({scrollTop:$("#sport").offset().top-50},300)
	});
	$("#to_business").click(function(){
		$("html,body").animate({scrollTop:$("#business").offset().top-80},300)
	});
	$("#to_customer").click(function(){
		$("html,body").animate({scrollTop:$("#customer").offset().top-80},300)
	});
})
//myCarousel
$(function(){
	$('#myCarousel').carousel('pause')
	$("#myCarousel").swipe( {
		//Single swipe handler for left swipes
		swipeLeft:function(event, direction, distance, duration, fingerCount) {
			$(this).carousel("next");
		},
		swipeRight:function(event, direction, distance, duration, fingerCount) {
			$(this).carousel("prev");
		},
		//Default is 75px, set to 0 for demo so any distance triggers swipe
		threshold:0
	});
})

//modal touch hidden
$(function(){	
	var stop=function(){
		e=window.event;
		e.preventDefault();
    e.stopPropagation();
	};
	$('.modal').on('show.bs.modal', function () {
		$("body").on("touchmove",stop);
	})
	$('.modal').on('hide.bs.modal', function () {
		$("body").off("touchmove",stop);
	})
})

//stepper
$(function(){
	$(".add-btn").on("touchstart",function(){
		var value=$(this).prev().val();
		value++;
		$(this).prev().val(value);
	})
	$(".del-btn").on("touchstart",function(){
		var value=$(this).next().val();
		value==0?"":value--;
		$(this).next().val(value);
	})
})
