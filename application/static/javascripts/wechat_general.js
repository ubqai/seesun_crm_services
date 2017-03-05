
$(function(){
	$("#scanQRCode").click(function(){
		wx.scanQRCode({
			needResult: 1,
			desc: 'scanQRCode desc',
			success: function (res) {
				document.getElementById("text-verification").value=res['resultStr']
				document.getElementById("btn-verification").disabled=false
			},
			fail: function(res) {
				alert("错误:"+res['errMsg']+"!!\n请重试或使用公众号中的校验真伪按钮")
			}
		});
	});
	
	// $("#btn-verification").click(function(){
	// 	document.getElementById("text-verification").value=''
	// 	document.getElementById("btn-verification").disabled=true
	// });
})
