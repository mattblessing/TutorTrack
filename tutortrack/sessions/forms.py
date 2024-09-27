from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.fields import DateField, TimeField
from wtforms.validators import (
    DataRequired, Length, ValidationError, NumberRange
)
import datetime


class LogSessionForm(FlaskForm):
    child = SelectField(
        "Select child",
        validators=[DataRequired(message="Please select a child.")]
    )
    date = DateField(
        "Date",
        validators=[DataRequired(message="Please provide a valid date.")]
    )
    time = TimeField(
        "Time",
        format="%H:%M",
        validators=[DataRequired(message="Please provide a valid time.")]
    )
    duration = IntegerField(
        "Duration",
        validators=[DataRequired(message="Please provide a valid duration.")]
    )
    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(message="Please provide a valid description"),
            Length(max=500)
        ]
    )
    childFocus = TextAreaField(
        "Child focus",
        validators=[
            DataRequired(message="Please provide a valid description."),
            Length(max=500)
        ]
    )
    ranking = IntegerField(
        "Session ranking (out of 10)",
        validators=[
            DataRequired(message="Please provide a valid ranking."),
            NumberRange(
                min=1, max=10, message="Please provide a valid ranking."
            )
        ]
    )
    submit = SubmitField("Submit")

    def validate_date(self, date):
        if date.data > datetime.date.today():
            raise ValidationError("You cannot enter a future date.")

    def validate_time(self, time):
        if (
            time.data > datetime.datetime.now().time() and
            self.date.data >= datetime.date.today()
        ):
            raise ValidationError("You cannot enter a future time.")


class UpdateSessionForm(LogSessionForm):
    child = SelectField("Select child", validate_choice=False)
    submit = SubmitField("Update")
