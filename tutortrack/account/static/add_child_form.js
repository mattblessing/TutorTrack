$(document).ready(function () {

    $("#childFirstnameInput").on({
        blur: function () {
            var firstname = $(this).val();
            if (firstname.length < 1 || firstname.length > 20) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#childFirstnameInput").hasClass("is-invalid") || $("#childFirstnameInput").hasClass("is-valid")) {
                var firstname = $(this).val();
                if (firstname.length < 1 || firstname.length > 20) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

    $("#childSurnameInput").on({
        blur: function () {
            var surname = $(this).val();
            if (surname.length < 1 || surname.length > 40) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#childSurnameInput").hasClass("is-invalid") || $("#childSurnameInput").hasClass("is-valid")) {
                var surname = $(this).val();
                if (surname.length < 1 || surname.length > 40) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

});