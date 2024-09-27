$(document).ready(function (e) {
    $("#childInput").on("change", function () {
        $.ajax({
            type: "POST",
            url: "/view/sessions",
            data: $("#childSelect").serialize(),
            success: function (data) {
                $("#sessions").html(data); // Update sessions display for new child
            }
        });
    });
});

