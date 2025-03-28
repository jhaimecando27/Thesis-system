from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import widgets, SelectMultipleField, SubmitField, ValidationError


class UploadForm(FlaskForm):
    file = FileField(
        "csv",
        validators=[
            FileRequired(),
            FileAllowed(["csv"], "Invalid file format. Please upload a CSV file only."),
        ],
    )
    submit = SubmitField("Upload")


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def length_check(form, field):
    if len(field.data) > 10 or len(field.data) < 3:
        raise ValidationError(
            "Invalid selection. The object ID must be between 3 and 10."
        )


class SelectionForm(FlaskForm):
    options = MultiCheckboxField("Options", validators=[length_check], coerce=str)
    submit = SubmitField("Submit")
