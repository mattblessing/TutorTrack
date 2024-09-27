$(document).ready(function (e) {
	$("#searchInput").on("keyup", function () { // Searches occur dynamically as user types
		$.ajax({
			type: "POST",
			url: "/parent/accounts",
			data: $("#searchBar").serialize(),
			success: function (data) {
				$("#parents").html(data); // Parent accounts display updates with search
			}
		});
	});

	$("#searchBar").on("keyup keypress", function (key) {
		if (key.which === 13) { // Do not allow user to press enter to submit the form - refreshes page
			key.preventDefault();
			return false;
		}
	});
});

