from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from sqlalchemy import text
from tutortrack import db, bcrypt
from tutortrack.users.forms import ResetForm


class ParentAccountForm(FlaskForm):
    firstname = StringField(
        "First name",
        validators=[DataRequired(
            message="Please provide your first name."), Length(max=20)]
    )
    surname = StringField(
        "Surname",
        validators=[DataRequired(
            message="Please provide your surname."), Length(max=40)]
    )
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(
            message="Please provide a valid email address.")]
    )
    submit = SubmitField("Update")

    def validate_email(self, email):
        if email.data.lower() != current_user.email:
            with db.engine.connect() as conn:
                emailSearch = conn.execute(
                    text("SELECT * FROM User WHERE Email=:email"),
                    {"email": email.data.lower()}
                ).fetchall()
            if len(emailSearch) != 0:
                raise ValidationError(
                    "An account already exists for that email address.")


class TutorAccountForm(ParentAccountForm):
    tutorCode = StringField("Tutor code")


class ChangePasswordForm(ResetForm):
    currentPassword = PasswordField(
        "Current password",
        validators=[
            DataRequired(message="Please provide a valid password.")
        ]
    )

    def validate_currentPassword(self, currentPassword):
        if bcrypt.check_password_hash(
            current_user.password,
            currentPassword.data
        ) == False:
            raise ValidationError("Incorrect password.")

    def validate_password(self, password):
        if bcrypt.check_password_hash(
            current_user.password,
            password.data
        ) == True:
            raise ValidationError("Please enter a new password.")


class DeleteAccountForm(FlaskForm):
    submit = SubmitField("Delete Account")


class SearchForm(FlaskForm):
    search = StringField()
    submit = SubmitField()


class AddChildForm(FlaskForm):
    childFirstname = StringField(
        "First name",
        validators=[
            DataRequired(message="Please provide your child's first name."),
            Length(max=20)
        ]
    )
    childSurname = StringField(
        "Surname",
        validators=[
            DataRequired(message="Please provide your child's surname."),
            Length(max=40)
        ]
    )
    submit = SubmitField("Add Child")
