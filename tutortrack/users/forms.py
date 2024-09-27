from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, IntegerField,
    FieldList, FormField, Form
)
from wtforms.fields import EmailField
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, Regexp, NumberRange, ValidationError
)
from sqlalchemy import text
from tutortrack import db, bcrypt


class TutorRegistrationForm(FlaskForm):
    firstname = StringField(
        "First name",
        validators=[
            DataRequired(message="Please provide your first name."),
            Length(max=20)
        ]
    )
    surname = StringField(
        "Surname",
        validators=[
            DataRequired(message="Please provide your surname."),
            Length(max=40)
        ]
    )
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Please provide a valid email address.")
        ]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters."),
            Regexp(
                ".*[A-Z].*", message="Password must contain a capital letter."
            )
        ]
    )
    confirmPassword = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords do not match.")
        ]
    )
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        with db.engine.connect() as conn:
            emailSearch = conn.execute(
                text("SELECT * FROM User WHERE Email=:email"),
                {"email": email.data.lower()}
            ).fetchall()
        if len(emailSearch) != 0:
            if emailSearch[0][5] == 0:
                raise ValidationError(
                    "An unconfirmed account exists for that email address."
                )
            else:
                raise ValidationError(
                    "An account already exists for that email address."
                )


class ChildForm(Form):
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


class ParentRegistrationForm(TutorRegistrationForm):
    tutorCode = IntegerField(
        "Tutor code",
        validators=[
            DataRequired(),
            NumberRange(
                min=100000,
                max=999999,
                message="Please provide a valid tutor code."
            )
        ]
    )
    children = FieldList(FormField(ChildForm), min_entries=1, max_entries=20)

    def validate_tutorCode(self, tutorCode):
        with db.engine.connect() as conn:
            tutorCodeSearch = conn.execute(
                text("SELECT * FROM Tutor WHERE TutorID=:tutorID"),
                {"tutorID": tutorCode.data}
            ).fetchall()
        if len(tutorCodeSearch) == 0:
            raise ValidationError("That tutor code does not exist.")


class EmailForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Please provide a valid email address.")
        ]
    )
    submit = SubmitField("Resend")

    def validate_email(self, email):
        with db.engine.connect() as conn:
            emailSearch = conn.execute(
                text("SELECT * FROM User WHERE Email=:email"),
                {"email": email.data.lower()}
            ).fetchall()
        if len(emailSearch) == 0:
            raise ValidationError(
                "An account hasn't been created for that email address."
            )


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Please provide a valid password.")]
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")

    def validate_email(self, email):
        with db.engine.connect() as conn:
            emailSearch = conn.execute(
                text("SELECT * FROM User WHERE Email=:email"),
                {"email": email.data.lower()}
            ).fetchall()
        if len(emailSearch) == 0:
            raise ValidationError(
                "An account doesn't exist for that email address."
            )

    def validate_password(self, password):
        with db.engine.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM User WHERE Email=:email"),
                {"email": self.email.data.lower()}
            ).fetchall()
        if len(user) != 0:
            userPassword = user[0][4]
            if bcrypt.check_password_hash(userPassword, password.data) == False:
                raise ValidationError("Incorrect password.")


class RequestResetForm(EmailForm):
    submit = SubmitField("Submit")

    def validate_email(self, email):
        with db.engine.connect() as conn:
            confirmedSearch = conn.execute(
                text("SELECT Confirmed FROM User WHERE Email=:email"),
                {"email": email.data.lower()}
            ).fetchall()
        if len(confirmedSearch) != 0:
            if confirmedSearch[0][0] == 0:
                raise ValidationError(
                    "An unconfirmed account exists for that email address."
                )
        else:
            raise ValidationError(
                "An account doesn't exist for that email address."
            )


class ResetForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters."),
            Regexp(
                ".*[A-Z].*",
                message="Password must contain a capital letter."
            )
        ]
    )
    confirmPassword = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords do not match.")
        ]
    )
    submit = SubmitField("Submit")
