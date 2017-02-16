//to change the text as the file uploaded
$(function(){
	
	function preview1(file) {
			var img = new Image(), url = img.src = URL.createObjectURL(file)
			var $img = $(img)
			$img.addClass("full-img")
			img.onload = function() {
					URL.revokeObjectURL(url)
					$('.pic-upload').empty().append($img)
			}
	}
	
	$(".file input").bind("change",function(e){
		var file = e.target.files[0]
		preview1(file)	
	})	
})
