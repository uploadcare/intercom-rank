import uuid

from flask import url_for
from flask.ext.login import current_user
from wtforms import SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.accounts.models import Project
from common.forms import BaseForm, TrackChangesStringField


def default_string_field(label, **extra):
    validators = extra.pop('validators', [])
    validators.append(DataRequired())
    return TrackChangesStringField(label, validators=validators, **extra)


class UniqueValue:
    def __init__(self, per_user=False):
        self.per_user = per_user

    def __call__(self, form, field):
        args = [getattr(Project, field.name) == field.data]

        if self.per_user:
            args.append(Project.user_id == current_user.id)

        if form.obj:
            args.append(Project.id != form.obj.id)

        if Project.query.filter(*args).first():
            raise ValidationError(
                '%s must be an unique' % str(field.label).title())


class ProjectForm(BaseForm):
    title = default_string_field('title',
                                 validators=[UniqueValue(per_user=True)])

    intercom_app_id = default_string_field(
        'intercom app_id', validators=[UniqueValue()])
    intercom_api_key = default_string_field('intercom api_key')

    aws_access_id = default_string_field('AWS access_id')
    aws_secret_access_key = default_string_field('AWS secret_access_key')

    submit = SubmitField('Save')
    repeat_import = SubmitField('Re-Import')

    def create_subscription_for(self, project):
        project.intercom_webhooks_internal_secret = str(uuid.uuid4())
        client = project.get_intercom_client()
        sub = client.subscribe(
            hook_url=url_for(
                'accounts.handle_intercom_hooks',
                internal_secret=project.intercom_webhooks_internal_secret,
                _external=True),
            topics=['user.created']
        )
        project.intercom_subscription_id = sub['id']
