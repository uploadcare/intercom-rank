import uuid

from flask import url_for
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


def default_string_field(name, **extra):
    return StringField(name, validators=[DataRequired()], **extra)


class ProjectForm(Form):
    title = default_string_field('title')

    intercom_app_id = default_string_field('intercom app_id')
    intercom_api_key = default_string_field('intercom api_key')

    aws_access_id = default_string_field('AWS access_id')
    aws_secret_access_key = default_string_field('AWS secret_access_key')

    submit = SubmitField('Save')

    def create_subscription_for(self, project):
        project.intercom_webhooks_internal_secret = uuid.uuid4()
        client = project.get_intercom_client()
        sub = client.subscribe(
            hook_url=url_for(
                'accounts.handle_intercom_hooks',
                internal_secret=project.intercom_webhooks_internal_secret,
                _external=True),
            topics=['user.created']
        )
        project.intercom_subscription_id = sub['id']


class ProjectChnageForm(Form):
    title = default_string_field('title')
    submit = SubmitField('Save')
