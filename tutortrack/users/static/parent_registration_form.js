// Validation for any added child fields
function blurValidateChildFirstname() {
    var childFirstname = $(this).val();
    if (childFirstname.length < 1 || childFirstname.length > 20) {
        $(this).removeClass("is-valid").addClass("is-invalid");
    } else {
        $(this).removeClass("is-invalid").addClass("is-valid");
    }
}

function keyupValidateChildFirstname() {
    if ($(this).hasClass("is-invalid") || $(this).hasClass("is-valid")) {
        var childFirstname = $(this).val();
        if (childFirstname.length < 1 || childFirstname.length > 20) {
            $(this).removeClass("is-valid").addClass("is-invalid");
        } else {
            $(this).removeClass("is-invalid").addClass("is-valid");
        }
    }
}

function blurValidateChildSurname() {
    var childSurname = $(this).val();
    if (childSurname.length < 1 || childSurname.length > 40) {
        $(this).removeClass("is-valid").addClass("is-invalid");
    } else {
        $(this).removeClass("is-invalid").addClass("is-valid");
    }
}

function keyupValidateChildSurname() {
    if ($(this).hasClass("is-invalid") || $(this).hasClass("is-valid")) {
        var childSurname = $(this).val();
        if (childSurname.length < 1 || childSurname.length > 40) {
            $(this).removeClass("is-valid").addClass("is-invalid");
        } else {
            $(this).removeClass("is-invalid").addClass("is-valid");
        }
    }
}

// Add validation to every child form on page when form is returned to user and page is reloaded
function childFormValidation() {
    var $forms = $(".childForm");

    $forms.each(function (i) {
        var $form = $(this);
        $form.find("#childFirstnameInput").blur(blurValidateChildFirstname);
        $form.find("#childFirstnameInput").keyup(keyupValidateChildFirstname);
        $form.find("#childSurnameInput").blur(blurValidateChildSurname);
        $form.find("#childSurnameInput").keyup(keyupValidateChildSurname);
    });
}

const TEMPLATE_INDEX = /(-)_(-)/;

// Replace the template index of an element (-_-) with the given index (e.g., -1-)
function replaceTemplateIndex(value, index) {
    // $1 and $2 are the "-"s in TEMPLATE_INDEX
    return value.replace(TEMPLATE_INDEX, "$1" + index + "$2");
}

// Adjust the indices of form fields when removing items
function adjustIndices(removedIndex) {
    var $forms = $(".childForm");

    $forms.each(function (i) {
        var $form = $(this);
        var index = parseInt($form.attr("data-index"));
        var newIndex = index - 1;

        if (index < removedIndex) {
            // Don"t adjust indices
            return;
        }

        // Change ID in child form
        $form.attr("id", $form.attr("id").replace(index, newIndex));
        $form.attr("data-index", newIndex);

        // Change IDs in child form fields
        $form.find("label, input").each(function (j) {
            var $item = $(this);

            if ($item.is("label")) {
                // Update labels
                $item.attr("for", $item.attr("for").replace(index, newIndex));
            } else {
                // Update other fields
                $item.attr("id", $item.attr("id").replace(index, newIndex));
                $item.attr("name", $item.attr("name").replace(index, newIndex));
            }
        });
    });
}

function addForm() {
    var $templateForm = $("#child-_-form");

    if ($templateForm.length === 0) {
        return;
    }

    // Get last index
    var $lastForm = $(".childForm").last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.attr("data-index")) + 1;
    }

    // Maximum of 20 child forms
    if (newIndex >= 20) {
        return;
    }

    // Add new child form
    var $newForm = $templateForm.clone();
    // Add elements to child form - ID and index
    $newForm.attr("id", replaceTemplateIndex($newForm.attr("id"), newIndex));
    $newForm.attr("data-index", newIndex);

    $newForm.find("label, input").each(function (i) {
        var $item = $(this);

        if ($item.is("label")) {
            // Update labels
            $item.attr("for", replaceTemplateIndex($item.attr("for"), newIndex));
        } else {
            // Update other fields
            $item.attr("id", replaceTemplateIndex($item.attr("id"), newIndex));
            $item.attr("name", replaceTemplateIndex($item.attr("name"), newIndex));
        }
    });

    // Append new child form to group of child forms
    $("#childForms-container").append($newForm);
    $newForm.addClass("childForm");
    $newForm.removeClass("is-hidden");
    // Add validation and remove child feature
    $newForm.find(".removeChild").click(removeForm);
    $newForm.find("#childFirstnameInput").blur(blurValidateChildFirstname);
    $newForm.find("#childFirstnameInput").keyup(keyupValidateChildFirstname);
    $newForm.find("#childSurnameInput").blur(blurValidateChildSurname);
    $newForm.find("#childSurnameInput").keyup(keyupValidateChildSurname);
}

function removeForm() {
    var $removedForm = $(this).closest(".childForm");
    var removedIndex = parseInt($removedForm.attr("data-index"));

    var $lastForm = $(".childForm").last();
    var lastIndex = parseInt($lastForm.attr("data-index"));

    if (lastIndex == 0) {
        return; // Cannot have less than one child form
    }

    $removedForm.remove();

    // Update indices
    adjustIndices(removedIndex);
}

$(document).ready(function () {

    // First name validation
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

    // Surname validation
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

    // Email validation
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

    // Password validation
    $("#parentPasswordInput").on({
        blur: function () {
            var password = $(this).val();
            var capital = new RegExp("[A-Z]");
            if ((password.length < 8) || !$(this).val().match(capital)) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
            if ($("#parentConfirmPasswordInput").hasClass("is-invalid") || $("#parentConfirmPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var confirmPassword = $("#parentConfirmPasswordInput").val();
                if (password == confirmPassword && $(this).hasClass("is-valid")) {
                    $("#parentConfirmPasswordInput").removeClass("is-invalid").addClass("is-valid");
                } else {
                    $("#parentConfirmPasswordInput").removeClass("is-valid").addClass("is-invalid");
                }
            }
        },
        keyup: function () {
            if ($("#parentPasswordInput").hasClass("is-invalid") || $("#parentPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var capital = new RegExp("[A-Z]");
                if ((password.length < 8) || !$(this).val().match(capital)) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
            if ($("#parentConfirmPasswordInput").hasClass("is-invalid") || $("#parentConfirmPasswordInput").hasClass("is-valid")) {
                var password = $(this).val();
                var confirmPassword = $("#parentConfirmPasswordInput").val();
                if (password == confirmPassword && $(this).hasClass("is-valid")) {
                    $("#parentConfirmPasswordInput").removeClass("is-invalid").addClass("is-valid");
                } else {
                    $("#parentConfirmPasswordInput").removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

    // Confirm password validation
    $("#parentConfirmPasswordInput").on({
        blur: function () {
            var confirmPassword = $(this).val();
            var password = $("#parentPasswordInput").val();
            if (password == confirmPassword && $("#parentPasswordInput").hasClass("is-valid")) {
                $(this).removeClass("is-invalid").addClass("is-valid");
            } else {
                $(this).removeClass("is-valid").addClass("is-invalid");
            }
        },
        keyup: function () {
            if ($("#parentConfirmPasswordInput").hasClass("is-invalid") || $("#parentConfirmPasswordInput").hasClass("is-valid")) {
                var confirmPassword = $(this).val();
                var password = $("#parentPasswordInput").val();
                if (password == confirmPassword && $("#parentPasswordInput").hasClass("is-valid")) {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                } else {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                }
            }
        }
    });

    $("#tutorCodeInput").on({
        blur: function () {
            var tutorCode = $(this).val();
            if (tutorCode.length != 6) {
                $(this).removeClass("is-valid").addClass("is-invalid");
            } else {
                $(this).removeClass("is-invalid").addClass("is-valid");
            }
        },
        keyup: function () {
            if ($("#tutorCodeInput").hasClass("is-invalid") || $("#tutorCodeInput").hasClass("is-valid")) {
                var tutorCode = $(this).val();
                if (tutorCode.length != 6) {
                    $(this).removeClass("is-valid").addClass("is-invalid");
                } else {
                    $(this).removeClass("is-invalid").addClass("is-valid");
                }
            }
        },
        keypress: function (key) { // "which" determines what key was pressed
            if (key.which != 8 && key.which != 0 && (key.which < 48 || key.which > 57)) {
                return false;
            }
        }
    });

    // Assign functions to add/remove child buttons
    $("#addChild").click(addForm);
    $(".removeChild").click(removeForm);

    // Make the template child form not required so it doesn"t affect validation of form
    $("#child-_-form childFirstnameInput").attr("required", "false");
    $("#child-_-form childSurnameInput").attr("required", "false");

    childFormValidation();

});

