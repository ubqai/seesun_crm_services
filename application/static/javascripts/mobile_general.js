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
	
	if($(".navbar").length>0){
		var key;
		$(window).bind("scroll", function(){
				var dis = document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;
				if(dis>60&&key!=1) {
						$(".navbar").addClass("fixed-menu");
						$(".header").addClass("fixed-margin-2");
						key=1;
				}else if(dis<=60){
						$(".navbar").removeClass("fixed-menu");
						$(".header").removeClass("fixed-margin-2");
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

//file
function fileText(ele){
	ele.bind("change",function(){
    var text=this.value;
    var text_array=text.split("\\");
    var file_name=text_array[text_array.length-1];
    $(this).parent().find("label").html(file_name);
    var format=file_name.split(".")[1];
  })
}
$(function(){
  //to change the text as the file uploaded
	fileText($(".file input"));
	pre_pic($(".file input"));
})

//datetimePicker
$(function(){
	$(".datetimePicker").datetimepicker({
		timepicker:false,
		format:'Y/m/d'
	});
})

//调整ckedit的图片大小
$(function(){
	$(".ck-wrapper").find("img").each(function(index,ele){
		var max_width=$(".ck-wrapper>p").width(); 
		$(ele).width()>max_width? $(ele).css("max-width","100%").css("height","auto"):"";
	})
})

//下拉框
$(function(){
	$(".slide-trigger").click(function(){
		$(this).parent().find(".slide-panel").slideToggle();
		$(this).toggleClass("border-none");
	});
})

$(function(){
	$(".much-more").click(function(){
		$(this).parent().parent().find(".over-p").toggleClass("hidden");
	})
})

//预览图片
function preview1(file,ele) {
	var img = new Image(), url = img.src = URL.createObjectURL(file)
	var $img = $(img);
	$img.addClass("full-img");
	$img.css("height","96px")
	img.onload = function() {
			URL.revokeObjectURL(url)
			ele.replaceWith($img);
	}
}
function pre_pic(elem){
	elem.bind("change",function(e){
		var file = e.target.files[0];
		var ele=$(this).parent().find("img");
		preview1(file,ele)	
	})	
}	
//增加图片
$(function(){
	$(".pic-add").click(function(){
		var clone=$(".pic-template").clone();
		clone.removeClass("hidden").removeClass("pic-template");
		pre_pic(clone.find("input"));
		fileText(clone.find("input"));
		clone.find(".pic-del").click(function(){
			$(this).parent().remove();
		})	
		$(this).before(clone);
	})	
})

