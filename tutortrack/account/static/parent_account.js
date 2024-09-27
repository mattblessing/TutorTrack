var confirmationBox = document.getElementById("confirmationBox")

confirmationBox.addEventListener("show.bs.modal", function (event) {
    // Button that triggered the modal
    var button = event.relatedTarget
    // Get the data from data-bs-child attribute (the childID)
    var childID = button.getAttribute("data-bs-child")
    // Update the modal"s content so that the delete button deletes the correct child
    var deleteButton = confirmationBox.querySelector(".modal-footer a")
    deleteButton.href = "/delete/child" + childID
})

$(document).ready(function () {

    $("#parentFirstnameInput").on({
        blur: function () {
            var firstname = $(this).val();
            if (firstname.length < 1 || firstname.length > 20) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#parentFirstnameInput").hasClass("is-invalid") || $("#parentFirstnameInput").hasClass("is-valid")) {
                var firstname = $(this).val();
                if (firstname.length < 1 || firstname.length > 20) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

    $("#parentSurnameInput").on({
        blur: function () {
            var surname = $(this).val();
            if (surname.length < 1 || surname.length > 40) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#parentSurnameInput").hasClass("is-invalid") || $("#parentSurnameInput").hasClass("is-valid")) {
                var surname = $(this).val();
                if (surname.length < 1 || surname.length > 40) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        }
    });

    $("#parentEmailInput").on({
        blur: function () {
            var email = $(this).val();
            if ((email.length < 5) || (email.indexOf("@") == -1) || (email.lastIndexOf(".") < email.lastIndexOf("@") + 2) || (email.indexOf(" ") != -1) || (email.lastIndexOf(".") > email.length - 3)) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#parentEmailInput").hasClass("is-invalid") || $("#parentEmailInput").hasClass("is-valid")) {
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