//to change the text as the file uploaded
$(function(){
	
	function preview1(file,ele) {
			var img = new Image(), url = img.src = URL.createObjectURL(file)
			var $img = $(img);
			$img.addClass("full-img");
			img.onload = function() {
					URL.revokeObjectURL(url)
					ele.replaceWith($img);
			}
	}
	
	$(".file input").bind("change",function(e){
		var file = e.target.files[0];
		var ele=$(this).parent().parent().next(".pic-upload").children("img");
		preview1(file,ele)	
	})
	$(".inbox-file").bind("change",function(e){
		var file = e.target.files[0];
		var ele=$(this).next("img");
		preview1(file,ele)	
	})	
})

//添加和删除item
$(function(){
	//names进行重新排列
	function refresh(_names){
		var names=_names;
		var items=$(".item-wrapper").find(".form-item");
		items.each(function(index,ele){
			var inputs=$(ele).find("input,select");
			inputs.each(function(_index,_ele){
				$(_ele).attr("name",names[_index]+index);
			})		
		});
	}
	
	//增加item
	function add_item(_names){
		var clone=$(".item-template").clone();
		clone.removeClass("item-template")
			.find(".del-item").removeClass("hidden")
			.on("click",function(){
				$(this).parent().parent().remove();
				refresh(_names);
			});	
		$(".item-wrapper").append(clone);
		//refresh(_names);	
	}
	
	//增加产品目录
	$(".new-product-category").click(function(){
		add_item(["names[]"])
	})
	//增加产品属性
	$(".new-product-feature").click(function(){
		add_item(["names[]"])
	})
	$(".new-product-option").click(function(){
		add_item(["names[]"])
	})
	$(".new-product").click(function(){
		add_item(["names[]"])
	})
})
 