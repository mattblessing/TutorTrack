$(document).ready(function () {

    $("#emailInput").on({
        blur: function () {
            var email = $(this).val();
            if ((email.length < 5) || (email.indexOf("@") == -1) || (email.lastIndexOf(".") < email.lastIndexOf("@") + 2) || (email.indexOf(" ") != -1) || (email.lastIndexOf(".") > email.length - 3)) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#emailInput").hasClass("is-invalid") || $("#emailInput").hasClass("is-valid")) {
                var email = $(this).val();
                if ((email.length < 5) || (email.indexOf("@") == -1) || (email.lastIndexOf(".") < email.lastIndexOf("@") + 2) || (email.indexOf(" ") != -1) || (email.lastIndexOf(".") > email.length - 3)) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

    // Make "Invalid password" disappear when user starts typing again
    $("#passwordInput").on({
        blur: function () {
            var password = $(this).val();
            if (password.length < 1) {
                $(this).addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid");
            }
        },
        keyup: function () {
            if ($("#passwordInput").hasClass("is-invalid")) {
                var password = $(this).val();
                if (password.length < 1) {
                    $(this).addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid");
                }
            }
        }
    });

});