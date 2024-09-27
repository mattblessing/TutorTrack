$(document).ready(function () {

    $("#tutorFirstnameInput").on({
        blur: function () {
            var firstname = $(this).val();
            if (firstname.length < 1 || firstname.length > 20) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#tutorFirstnameInput").hasClass("is-invalid") || $("#tutorFirstnameInput").hasClass("is-valid")) {
                var firstname = $(this).val();
                if (firstname.length < 1 || firstname.length > 20) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

    $("#tutorSurnameInput").on({
        blur: function () {
            var surname = $(this).val();
            if (surname.length < 1 || surname.length > 40) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#tutorSurnameInput").hasClass("is-invalid") || $("#tutorSurnameInput").hasClass("is-valid")) {
                var surname = $(this).val();
                if (surname.length < 1 || surname.length > 40) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

    $("#tutorEmailInput").on({
        blur: function () {
            var email = $(this).val();
            if ((email.length < 5) || (email.indexOf("@") == -1) || (email.lastIndexOf(".") < email.lastIndexOf("@") + 2) || (email.indexOf(" ") != -1) || (email.lastIndexOf(".") > email.length - 3)) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#tutorEmailInput").hasClass("is-invalid") || $("#tutorEmailInput").hasClass("is-valid")) {
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

