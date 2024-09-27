$(document).ready(function () {

    $("#type-1").click(function () { // When "subtopic" is selected
        if ($("#parentTopic option").length == 0) {
            $("#type-0").prop("checked", true); // Select "topic" by default if no topics that can be a parent topic exist
            $("#type-0").click();
        }
    });

    $("[name='type']").on("click", function () { // When "type" choice is changed
        if ($(this).is(":checked") && $(this).val() == "subtopic" && $("#parentTopic option").length != 0) {
            $("#parentTopic").attr("hidden", false);
        } else {
            $("#parentTopic").attr("hidden", true);
        }
    });

    $("[name='type']").each(function () { // When page is first loaded
        if ($(this).is(":checked") && $(this).val() == "subtopic" && $("#parentTopic option").length != 0) {
            $("#parentTopic").attr("hidden", false);
        } else {
            $("#parentTopic").attr("hidden", true);
        }
    })

    $(".form-control").keyup(function () { // Remove invalid input message when user begins to retype input
        $(this).removeClass("is-invalid");
    });

});