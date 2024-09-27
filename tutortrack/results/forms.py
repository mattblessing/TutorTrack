from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, ValidationError, NumberRange
import datetime


class LogResultForm(FlaskForm):
    child = SelectField(
        "Select child",
        validators=[DataRequired(message="Please select a child.")]
    )
    topic = SelectField("Select topic", validate_choice=False)
    date = DateField(
        "Date completed",
        validators=[DataRequired(message="Please provide a valid date.")]
    )
    type = SelectField(
        "Type of work",
        choices=[
            "Worksheet", "Test", "Quiz", "Textbook questions", "Essay",
            "Project", "Other"
        ],
        validators=[DataRequired(message="Please provide a valid work type.")]
    )
    studentMark = IntegerField(
        "Student mark",
        validators=[
            DataRequired(message="Please provide a valid student mark."),
            NumberRange(min=0, message="Please provide a valid student mark.")
        ]
    )
    totalMark = IntegerField(
        "Total mark",
        validators=[
            DataRequired(message="Please provide a valid total mark."),
            NumberRange(min=0, message="Please provide a valid student mark.")
        ]
    )
    submit = SubmitField("Submit")

    def validate_totalMark(self, totalMark):
        if (
            isinstance(self.studentMark.data, int) and
            isinstance(self.totalMark.data, int)
        ):
            if self.studentMark.data > totalMark.data:
                raise ValidationError(
                    "The total mark cannot be less than the student mark."
                )

    def validate_date(self, date):
        if date.data > datetime.date.today():
            raise ValidationError("You cannot enter a future date.")


class UpdateResultForm(LogResultForm):
    child = SelectField("Select child", validate_choice=False)
    submit = SubmitField("Update")
