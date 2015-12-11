from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ProjectForm(Form):
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Add')
