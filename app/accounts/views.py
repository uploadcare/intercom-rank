import json
import logging
from flask import (request, Blueprint, abort, render_template, redirect,
                   url_for, flash)
from flask.views import MethodView
from flask.ext.user import login_required
from flask.ext.login import current_user


from common.decorators import render_to
from app import app, csrf
from app.accounts.models import User, Project
from app.accounts.forms import ProjectForm
from app.accounts.utils import transform_email_if_useful
from app.accounts.tasks import fetch_and_update_information


accounts_app = Blueprint('accounts', __name__)
logger = logging.getLogger(__name__)


@accounts_app.route('/')
@render_to('index.jade')
@login_required
def dashboard():
    return redirect(url_for('accounts.projects_list'))


@accounts_app.route('/projects/')
@render_to('projects/list.jade')
@login_required
def projects_list():
    projects = (Project.query
                .filter(Project.user_id == current_user.id)
                .order_by(Project.id.asc()).all())
    return locals()


@accounts_app.route('/projects/add/', methods=('GET', 'POST'))
@render_to('projects/form.jade')
@login_required
def project_add():
    form = ProjectForm()

    if form.validate_on_submit():
        project = Project()

        form.populate_obj(project)
        try:
            form.create_subsciption_for(project)
        except Exception:
            logger.exception('Intercom subscription errror')
            flash('Can\'t create subscription on Intercom\'s events. '
                  'Probably you provide an incorrect APP_ID or API_KEY.',
                  'danger')
            return locals()

        project.user_id = current_user.id
        project.save()

        flash('Project has been added', 'success')
        return redirect(url_for('accounts.projects_list'))

    return locals()


@accounts_app.route('/projects/<int:pk>/', methods=('GET', 'POST'))
@render_to('projects/form.jade')
@login_required
def project_update(pk):
    project = Project.get_for_current_user_or_404(pk)

    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        form.populate_obj(project)
        project.user_id = current_user.id
        project.save()
        flash('Project has been updated', 'success')
        return redirect(url_for('accounts.projects_list'))

    return locals()


@accounts_app.route('/projects/<int:pk>/remove/', methods=('GET', 'POST'))
@login_required
def project_remove(pk):
    project = Project.get_for_current_user_or_404(pk)
    project.delete()
    flash('Project has been removed', 'success')
    return redirect(url_for('accounts.projects_list'))


@csrf.exempt
@accounts_app.route('/projects/hook/<internal_secret>/', methods=('POST',))
def handle_intercom_hooks(internal_secret):
    project = Project.query.filter(
        Project.intercom_webhooks_internal_secret == internal_secret).first()

    if not project:
        raise abort(400)

    user = request.json['data']['item']
    user_email = transform_email_if_useful(user['email'], user['user_id'])

    if user_email:
        fetch_and_update_information.delay([user_email], project.id)

    return json.dumps({'status': 'ok'})
