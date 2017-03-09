$(function(){
	$("body").niceScroll({cursorwidth: '0',cursorborder: '0'});
	$(".my-nav").niceScroll({cursorwidth: '0',cursorborder: '0'});
	$('#sidebar').metisMenu();
})
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
			index==0?index="":"";
			inputs.each(function(_index,_ele){
				names[_index].indexOf("[]")>0?$(_ele).attr("name",names[_index]):$(_ele).attr("name",names[_index]+index);
			})		
		});
	}
	
	//增加item
	function add_item(_names){
		var clone=$(".item-template").clone();
		clone.find("input").val("");
		clone.removeClass("item-template")
			.find(".del-item").removeClass("hidden")
			.on("click",function(){
				$(this).parent().parent().remove();
				refresh(_names);
			});	
		$(".item-wrapper").append(clone);
		refresh(_names);	
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
		add_item(["name"])
	})
	//库存
	$(".new-inventory").click(function(){
		add_item(["uer_id","production_date","valid_until","batch_no","stocks"])
	})
})
//去除textarea的htmltag
function delHtmlTag(str){
    return str.replace(/<[^>]+>/g,"");
}
$(function(){
	var str=$("textarea").val();
	$("textarea").val(delHtmlTag(str));
})

//增加图片
$(function(){
		//names进行重新排列
	function refresh(_name){
		var name=_name;
		var pics=$(".pic-wrapper").find("input[type=file]");
		pics.each(function(index,ele){
			$(ele).attr("name",name+index)	
		});
	}
	//增加item
	function add_pic(_name){
		var clone=$(".pic-template").clone();
		var name=clone.removeClass("pic-template").find("input[type=file]").attr("name");
		clone.find("input[type=file]").remove();
		var new_file=$("<input type='file'>")
		new_file.attr("name",name)
			.attr("id",name)
			.addClass("inbox-file");
		clone.prepend(new_file);
		$(".pic-add").before(clone);
		refresh(_name);	
	}
	$(".pic-add").click(function(){
		add_pic("image_file_");
	});

	//organization.user 
	$("#select_user_type").change(function(){
		if ($(this).children('option:selected').val()==3) {
			$(this).parent().parent().children('#search_user_dept_ranges').css("display", "")
			$(this).parent().parent().children('#search_user_sale_range').css("display", "none")
			$(this).parent().parent().children('#search_user_sale_range_province').css("display", "none")
		}
		else {
			$(this).parent().parent().children('#search_user_dept_ranges').css("display", "none")
			$(this).parent().parent().children('#search_user_sale_range').css("display", "")
			$(this).parent().parent().children('#search_user_sale_range_province').css("display", "")
		};
	});

	//organization.user 
	$("#select_sale_range_province").change(function(){
		var province_id=$(this).children('option:selected').val()
		var level_grade=4
		var data = {
			"parent_id":province_id,
		};
		$.ajax({
			type: 'GET',
			url: '/organization/user/get_sale_range_by_parent/'+level_grade,
			data: data, 
			dataType: 'json', 
			beforeSend:function(){
				$("#loading").css("display", "");
				$("#select_sale_range").attr("disabled","disabled");
			},
			success: function(json_array) { 
				var json = eval(json_array);
				$("#select_sale_range option").remove()
				$("#select_sale_range").append("<option selected value='__None'></option>");
				$.each(json, function (key,value) {
					$("#select_sale_range").append("<option value='"+key+"'>"+value+"</option>");
				}); 
			},
			error: function(xhr, type) {
				alert("级联销售范围获取失败,请直接选择")
			},
			complete: function(xhr, type) {
				$("#loading").css("display", "none");
				$("#select_sale_range").removeAttr("disabled");
			}
		});
	});
})
//datetimePicker
$(function(){
	$(".datetimePicker").datetimepicker({
		timepicker:false,
		format:'Y/m/d'
	});
})