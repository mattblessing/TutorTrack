from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Length
from tutortrack import db


class CreateTopicForm(FlaskForm):
    child = SelectField(
        "Select child",
        validators=[DataRequired(message="Please select a child.")]
    )
    name = StringField(
        "Topic name",
        validators=[
            DataRequired(message="Please provide a valid name."),
            Length(max=40)
        ]
    )
    type = RadioField(
        choices=[("topic", "Topic"), ("subtopic", "Subtopic")],
        default="topic"
    )
    parentTopic = SelectField("Parent topic", validate_choice=False)
    submit = SubmitField("Submit")


class UpdateTopicForm(CreateTopicForm):
    child = SelectField("Select child", validate_choice=False)
    submit = SubmitField("Update")
