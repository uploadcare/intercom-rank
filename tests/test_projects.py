from datetime import datetime

import mock
from flask import url_for

from tests.base import TestCase
from app.accounts.models import Project, User


class ProjectsTestCase(TestCase):
    list_url = '/projects/'
    add_url = '/projects/add/'

    def test_login_required_for_list(self):
        response = self.client.get(self.list_url)
        self.assertRedirectToLogin(response, self.list_url)

    def test_user_see_list_page(self):
        self.login()
        response = self.client.get(self.list_url)

        self.assert200(response)
        self.assertTemplateUsed('projects/list.jade')

    def test_login_required_for_add(self):
        response = self.client.get(self.add_url)
        self.assertRedirectToLogin(response, self.add_url)

        response = self.client.post(self.add_url)
        self.assertRedirectToLogin(response, self.add_url)

    def test_user_see_add_form(self):
        self.login()
        response = self.client.get(self.add_url)

        self.assert200(response)
        self.assertTemplateUsed('projects/form.jade')

    @mock.patch('common.intercom.IntercomClient.subscribe')
    def test_add_with_valid_data(self, subscribe):
        subscribe.return_value = {'id': 'some-id'}

        valid_data = dict(
            title='title',
            intercom_app_id='intercom_app_id',
            intercom_api_key='intercom_api_key',
            aws_access_id='aws_access_id',
            aws_secret_access_key='aws_secret_access_key',
        )
        self.login()
        response = self.client.post(self.add_url, data=valid_data,
                                    follow_redirects=True)

        self.assert200(response)

        projects = self.get_context_variable('projects')

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].title, valid_data['title'])
        self.assertTrue(subscribe.called)

    def test_invalid_data_not_added(self):
        self.login()
        response = self.client.post(self.add_url)

        self.assert200(response)

        form = self.get_context_variable('form')
        self.assertTrue(form.errors)


class ProjectUpdateTestCase(TestCase):
    def setUp(self):
        super(ProjectUpdateTestCase, self).setUp()
        self.project = Project(
            title='title',
            intercom_app_id='intercom_app_id',
            intercom_api_key='intercom_api_key',
            aws_access_id='aws_access_id',
            aws_secret_access_key='aws_secret_access_key',
            user_id=self.user.id)
        self.project.save()
        self.url = url_for('accounts.project_update', pk=self.project.id)

    def test_page_not_allowed_for_anon(self):
        response = self.client.get(self.url)
        self.assertRedirectToLogin(response, self.url)

    def test_only_owner_can_see_project(self):
        other_user = User(
            email='test@test.com',
            password=self.app.user_manager.hash_password('password'),
            is_enabled=True,
            is_admin=True,
            confirmed_at=datetime.utcnow())
        other_user.save()
        self.login(email='test@test.com', password='password')

        response = self.client.get(self.url)
        self.assert404(response)

    def test_incorrect_values_submited(self):
        self.login()

        response = self.client.post(self.url, data={'title': ''})
        self.assert200(response)

        form = self.get_context_variable('form')
        self.assertTrue(form.errors)

    @mock.patch('app.accounts.views.handle_intercom_users')
    def test_updated_project(self, handle_intercom_users):
        self.login()

        new_values = dict(
            title='title1',
            intercom_app_id='intercom_app_id1',
            intercom_api_key='intercom_api_key1',
            aws_access_id='aws_access_id1',
            aws_secret_access_key='aws_secret_access_key1',
        )

        response = self.client.post(self.url, data=new_values,
                                    follow_redirects=True)
        self.assert200(response)

        project = Project.query.filter(Project.id == self.project.id).first()

        for k, v in new_values.items():
            self.assertEqual(getattr(project, k), v)

        handle_intercom_users.delay.assert_called_once_with(self.project.id)

    @mock.patch('app.accounts.views.handle_intercom_users')
    def test_intercom_keys_not_changed(self, handle_intercom_users):
        self.login()

        data = dict(
            title='new_title',
            intercom_app_id=self.project.intercom_app_id,
            intercom_api_key=self.project.intercom_api_key,
            aws_access_id=self.project.aws_access_id,
            aws_secret_access_key=self.project.aws_secret_access_key,
        )

        response = self.client.post(self.url, data=data, follow_redirects=True)

        project = Project.query.filter(Project.id == self.project.id).first()

        self.assert200(response)
        self.assertFalse(handle_intercom_users.delay.called)
        self.assertEqual(project.title, 'new_title')

    @mock.patch('app.accounts.views.handle_intercom_users')
    def test_force_job_start(self, handle_intercom_users):
        self.login()

        data = dict(
            title=self.project.title,
            intercom_app_id=self.project.intercom_app_id,
            intercom_api_key=self.project.intercom_api_key,
            aws_access_id=self.project.aws_access_id,
            aws_secret_access_key=self.project.aws_secret_access_key,
            repeat_import='Re-Import'
        )

        response = self.client.post(self.url, data=data, follow_redirects=True)

        self.assert200(response)
        handle_intercom_users.delay.assert_called_once_with(self.project.id)
