from wtforms import SubmitField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
# Used for the child and topic selections
from tutortrack.results.forms import LogResultForm


class ReportForm(LogResultForm):
    startDate = DateField(
        "Start date",
        validators=[DataRequired(
            message="Please provide a valid start date."
        )]
    )
    endDate = DateField(
        "End date",
        validators=[DataRequired(message="Please provide a valid end date.")]
    )
    submit = SubmitField("Change dates")
