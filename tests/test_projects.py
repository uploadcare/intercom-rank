import mock
from flask import session

from tests.base import TestCase
from app.accounts.models import Project


class ProjectsTestCase(TestCase):
    list_url = '/projects/'
    add_url = '/projects/add/'

    def assertRedirectToLogin(self, response, next_url):
        expected = '/user/sign-in?next=http%3A//localhost{0}'.format(next_url)
        self.assertRedirects(response, expected)

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
