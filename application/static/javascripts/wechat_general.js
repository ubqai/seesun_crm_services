
$(function(){
	$("#scanQRCode0").click(function(){
		alert("11")
		wx.scanQRCode({
			desc: 'scanQRCode desc'
		});
	});
	$("#scanQRCode1").click(function(){
		alert("22")
		wx.scanQRCode({
			needResult: 1,
			desc: 'scanQRCode desc',
			success: function (res) {
				alert(JSON.stringify(res));
			}
		});
	});
})
