$(document).ready(function () {

	$(".form-control").keyup(function () { // Remove invalid input message when user begins to retype input
		$(this).removeClass("is-invalid");
	});

});
