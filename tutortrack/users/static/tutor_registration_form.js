$(document).ready(function () {

    // First name validation
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

    // Surname validation
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

    // Email validation
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

    // Password validation
    $("#tutorPasswordInput").on({
        blur: function () {
            var password = $(this).val();
            var capital = new RegExp("[A-Z]");
            if ((password.length < 8) || !$(this).val().match(capital)) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
            if ($("#tutorConfirmPasswordInput").hasClass("is-invalid") || $("#tutorConfirmPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var confirmPassword = $("#tutorConfirmPasswordInput").val();
                if (password == confirmPassword && $(this).hasClass("is-valid")) {
                    $("#tutorConfirmPasswordInput").removeClass("is-invalid").addClass("is-valid");
                } else {
                    $("#tutorConfirmPasswordInput").removeClass("is-valid").addClass("is-invalid");
                }
            }
        },
        keyup: function () {
            if ($("#tutorPasswordInput").hasClass("is-invalid") || $("#tutorPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var capital = new RegExp("[A-Z]");
                if ((password.length < 8) || !$(this).val().match(capital)) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
            if ($("#tutorConfirmPasswordInput").hasClass("is-invalid") || $("#tutorConfirmPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var confirmPassword = $("#tutorConfirmPasswordInput").val();
                if (password == confirmPassword && $(this).hasClass("is-valid")) {
                    $("#tutorConfirmPasswordInput").removeClass("is-invalid").addClass("is-valid");
                } else {
                    $("#tutorConfirmPasswordInput").removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

    // Confirm password validation
    $("#tutorConfirmPasswordInput").on({
        blur: function () {
            var confirmPassword = $(this).val();
            var password = $("#tutorPasswordInput").val();
            if (password == confirmPassword && $("#tutorPasswordInput").hasClass("is-valid")) {
                $(this).removeClass("is-invalid").addClass("is-valid");
            } else {
                $(this).removeClass("is-valid").addClass("is-invalid");
            }
        },
        keyup: function () {
            if ($("#tutorConfirmPasswordInput").hasClass("is-invalid") || $("#tutorConfirmPasswordInput").hasClass("is-valid")) {
                var confirmPassword = $(this).val();
                var password = $("#tutorPasswordInput").val();
                if (password == confirmPassword && $("#tutorPasswordInput").hasClass("is-valid")) {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                } else {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

});