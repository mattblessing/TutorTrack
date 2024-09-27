$(document).ready(function () {

    $("#childInput").on("change", function () {
        $.ajax({
            type: "POST",
            url: "/create/topic",
            data: {
                child: $("#childInput").val(),
                ajax: true
            },
            success: function (data) {
                if (data.error) {
                    $("#parentTopicInput").empty()
                    $("#type-0").prop("checked", true);
                    $("#type-0").click();
                } else {
                    $("#parentTopicInput").empty()
                    $.each(data, function (index, choice) {
                        $("#parentTopicInput").append($("<option></option>").attr("value", choice[0]).text(choice[1]));
                    });
                }
            }
        });
    });

    $("#type-1").click(function () {
        if ($("#parentTopic option").length == 0) {
            $("#type-0").prop("checked", true);
            $("#type-0").click();
        }
    });

    // When form is returned due to invalid input, topic/subtopic selection needs to be remembered, otherwise type will always be reset to topic
    var selectedType = localStorage.getItem("selectedType");
    if (!selectedType) {
        var selectedType = "topic";
    }
    $("#" + selectedType).click(); // Select the last selected type as default
    $("#" + selectedType).prop("checked", true);

    $("[name='type']").on("click", function () { // Cannot choose subtopic if there are no other topics
        if ($("[name='type']").is(":checked") && $(this).val() == "subtopic" && $("#parentTopic option").length != 0) {
            $("#parentTopic").attr("hidden", false);
            localStorage.setItem("selectedType", $(this).attr("id"));
        } else {
            $("#parentTopic").attr("hidden", true);
            localStorage.setItem("selectedType", $(this).attr("id"));
        }
    });

    // As selectedType variable may be subtopic due to last time form was opened, this may need to be disallowed due to there being no available parent topics
    if ($("#" + selectedType).is(":checked") && $("#" + selectedType).val() == "subtopic" && $("#parentTopic option").length != 0) {
        $("#parentTopic").attr("hidden", false);
    } else {
        $("#parentTopic").attr("hidden", true);
        $("#type-0").prop("checked", true);
        $("#type-0").click();
    }

    $(".form-control").keyup(function () { // Remove invalid input message when user begins to retype input
        $(this).removeClass("is-invalid");
    });

});


