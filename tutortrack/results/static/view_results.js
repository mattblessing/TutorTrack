$(document).ready(function () {
    $("#childInput").on("change", function () {
        var child = $(this).val();
        $.ajax({
            type: "POST",
            url: "/view/results",
            data: {
                child: child,
                childChange: true
            },
            success: function (data) {
                $("#topicInput").empty()
                $.each(data.topics, function (index, choice) { // Set new topic selection options
                    $("#topicInput").append($("<option></option>").attr("value", choice[0]).text(choice[1]));
                });
                $("#topicInput").val(0); // Set default selection to "All topics"
                $("#results").html(data.results); // Display new results
            }
        });
    });
    $("#topicInput").on("change", function () {
        var child = $("#childInput").val();
        var topic = $(this).val();
        $.ajax({
            type: "POST",
            url: "/view/results",
            data: {
                child: child,
                topic: topic,
                topicChange: true
            },
            success: function (data) {
                $("#results").html(data); // Display new results
            }
        });
    });
});

