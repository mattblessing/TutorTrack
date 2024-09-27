$(document).ready(function () {

    $("#passwordInput").on({
        blur: function () {
            var password = $(this).val();
            var capital = new RegExp("[A-Z]");
            if ((password.length < 8) || !$(this).val().match(capital)) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
            if ($("#confirmPasswordInput").hasClass("is-invalid") || $("#confirmPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var confirmPassword = $("#confirmPasswordInput").val();
                if (password == confirmPassword && $(this).hasClass("is-valid")) {
                    $("#confirmPasswordInput").removeClass("is-invalid").addClass("is-valid");
                } else {
                    $("#confirmPasswordInput").removeClass("is-valid").addClass("is-invalid");
                }
            }
        },
        keyup: function () {
            if ($("#passwordInput").hasClass("is-invalid") || $("#passwordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var capital = new RegExp("[A-Z]");
                if ((password.length < 8) || !$(this).val().match(capital)) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
            if ($("#confirmPasswordInput").hasClass("is-invalid") || $("#confirmPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var confirmPassword = $("#confirmPasswordInput").val();
                if (password == confirmPassword && $(this).hasClass("is-valid")) {
                    $("#confirmPasswordInput").removeClass("is-invalid").addClass("is-valid");
                } else {
                    $("#confirmPasswordInput").removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

    $("#confirmPasswordInput").on({
        blur: function () {
            var confirmPassword = $(this).val();
            var password = $("#passwordInput").val();
            if (password == confirmPassword && $("#passwordInput").hasClass("is-valid")) {
                $(this).removeClass("is-invalid").addClass("is-valid");
            } else {
                $(this).removeClass("is-valid").addClass("is-invalid");
            }
        },
        keyup: function () {
            if ($("#confirmPasswordInput").hasClass("is-invalid") || $("#confirmPasswordInput").hasClass("is-valid")) {
                var confirmPassword = $(this).val();
                var password = $("#passwordInput").val();
                if (password == confirmPassword && $("#passwordInput").hasClass("is-valid")) {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                } else {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

});

