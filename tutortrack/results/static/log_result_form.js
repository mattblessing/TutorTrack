$(document).ready(function () {

    $("#childInput").on("change", function () {
        $.ajax({
            type: "POST",
            url: "/log/result",
            data: {
                child: $("#childInput").val(),
                ajax: true
            },
            success: function (data) {
                if (data.error) {
                    $("#topicInput").empty();
                    $("#noTopic").text("No topics exist for this child. Create a topic before logging a result!");
                } else {
                    $("#topicInput").empty()
                    $.each(data, function (index, choice) {
                        // Create new options for topic select
                        $("#topicInput").append($("<option></option>").attr("value", choice[0]).text(choice[1]));
                    });
                    $("#noTopic").text("");
                }
            }
        });
    });

    if ($("#topicInput option").length == 0) {
        $("#noTopic").text("No topics exist for this child. Create a topic before logging a result!");
    } else {
        $("#noTopic").text("");
    }

    $(".form-control").keyup(function () { // Remove invalid input message when user begins to retype input
        $(this).removeClass("is-invalid");
    });

});


