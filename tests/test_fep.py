from flask import url_for

from tests.base import TestCase
from app.accounts.models import FreeEmailProvider


class FreeEmailProviderTestCase(TestCase):
    def setUp(self):
        super(FreeEmailProviderTestCase, self).setUp()
        self.url = url_for('accounts.free_email_providers_list')

        self.items = [FreeEmailProvider(domain='%s+freedomain.com' % i)
                      for i in range(10)]
        self.db.session.add_all(self.items)
        self.db.session.commit()

    def test_login_required_for_list(self):
        response = self.client.get(self.url)
        self.assertRedirectToLogin(response, self.url)

    def test_login_required_for_add(self):
        response = self.client.post(self.url)
        self.assertRedirectToLogin(response, self.url)

    def test_listing_works(self):
        self.login()
        response = self.client.get(self.url)

        self.assert200(response)
        self.assertTemplateUsed('fep/list.jade')

        content = response.data.decode('utf-8')
        for item in self.items:
            self.assertTrue(item.domain in content)

    def test_add_duplicate(self):
        self.login()

        response = self.client.post(self.url,
                                    data={'domain': self.items[0].domain})
        self.assert200(response)

        form = self.get_context_variable('form')
        self.assertTrue(form.errors)
        self.assertEqual(len(self.items), FreeEmailProvider.query.count())

    def test_empty_submit(self):
        self.login()

        response = self.client.post(self.url)
        self.assert200(response)

        form = self.get_context_variable('form')
        self.assertTrue(form.errors)

    def test_add(self):
        self.login()
        domain = 'unique.new.domain'

        response = self.client.post(self.url, data={'domain': domain})
        self.assert200(response)

        form = self.get_context_variable('form')
        self.assertFalse(form.errors)

        self.assertTrue(FreeEmailProvider.query.filter(
            FreeEmailProvider.domain == domain).first())

    def test_remove(self):
        self.login()
        target = self.items[0]
        url = url_for('accounts.free_email_provider_remove', pk=target.id)

        response = self.client.post(url, follow_redirects=True)
        self.assert200(response)

        self.assertEqual(None, FreeEmailProvider.query.filter(
            FreeEmailProvider.domain == target.domain
        ).first())

