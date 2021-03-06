from flask.ext.testing import TestCase as _TestCase

from app import app, db
from app.accounts.utils import create_admin


class TestCase(_TestCase):
    db = db

    def create_app(self):
        app.config.from_object('tests.settings_test')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()
        self.user = create_admin()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email=None, password=None):
        data = dict(
            email=email or self.app.config['ADMIN_USER']['email'],
            password=password or self.app.config['ADMIN_USER']['password'],
            remember=True,
        )
        return self.client.post('/user/sign-in', data=data,
                                follow_redirects=True)

    def logout(self):
        return self.client.get('/user/sign-out', follow_redirects=True)

    def assertRedirectToLogin(self, response, next_url):
        expected = '/user/sign-in?next=http%3A//localhost{0}'.format(next_url)
        self.assertRedirects(response, expected)
