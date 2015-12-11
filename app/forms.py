from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ProjectForm(Form):
    name = StringField('name', validators=[DataRequired()])
    awis_access_id = StringField('awis_access_id', validators=[DataRequired()])
    awis_secret_access_key = StringField('awis_secret_access_key', validators=[DataRequired()])
    intercom_app_id = StringField('intercom_app_id', validators=[DataRequired()])
    intercom_app_api_key = StringField('intercom_app_api_key', validators=[DataRequired()])

    submit = SubmitField('Add')
