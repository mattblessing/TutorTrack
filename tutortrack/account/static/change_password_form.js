$(document).ready(function () {

    $("#currentPasswordInput").on({
        blur: function () {
            var password = $(this).val();
            if (password.length < 1) {
                $(this).addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid");
            }
        },
        keyup: function () {
            if ($("#currentPasswordInput").hasClass("is-invalid")) {
                var password = $(this).val();
                if (password.length < 1) {
                    $(this).addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid");
                }
            }
        }
    });

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
                var confirmPasswordword = $("#confirmPasswordInput").val();
                if (password == confirmPasswordword && $(this).hasClass("is-valid")) {
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
                var confirmPasswordword = $("#confirmPasswordInput").val();
                if (password == confirmPasswordword && $(this).hasClass("is-valid")) {
                    $("#confirmPasswordInput").removeClass("is-invalid").addClass("is-valid");
                } else {
                    $("#confirmPasswordInput").removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

    $("#confirmPasswordInput").on({
        blur: function () {
            var confirmPasswordword = $(this).val();
            var password = $("#passwordInput").val();
            if (password == confirmPasswordword && $("#passwordInput").hasClass("is-valid")) {
                $(this).removeClass("is-invalid").addClass("is-valid");
            } else {
                $(this).removeClass("is-valid").addClass("is-invalid");
            }
        },
        keyup: function () {
            if ($("#confirmPasswordInput").hasClass("is-invalid") || $("#confirmPasswordInput").hasClass("is-valid")) {
                var confirmPasswordword = $(this).val();
                var password = $("#passwordInput").val();
                if (password == confirmPasswordword && $("#passwordInput").hasClass("is-valid")) {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                } else {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

});

