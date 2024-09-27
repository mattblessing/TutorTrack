$(document).ready(function () {

    $("#resendEmailInput").on({
        blur: function () {
            var email = $(this).val();
            if ((email.length < 5) || (email.indexOf("@") == -1) || (email.lastIndexOf(".") < email.lastIndexOf("@") + 2) || (email.indexOf(" ") != -1) || (email.lastIndexOf(".") > email.length - 3)) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#resendEmailInput").hasClass("is-invalid") || $("#resendEmailInput").hasClass("is-valid")) {
                var email = $(this).val();
                if ((email.length < 5) || (email.indexOf("@") == -1) || (email.lastIndexOf(".") < email.lastIndexOf("@") + 2) || (email.indexOf(" ") != -1) || (email.lastIndexOf(".") > email.length - 3)) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

});