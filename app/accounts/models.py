import uuid

from flask_user import UserMixin
from flask.ext.login import current_user
from intercom import Intercom, Subscription

from app import db
from common import models
from common.intercom import IntercomContextManager
from common.awis import AWISContextManager


class User(db.Model, UserMixin, models.BaseModelMixin):
    __tablename__ = 'users'

    email = db.Column(db.Unicode(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    confirmed_at = db.Column(db.DateTime())
    reset_password_token = db.Column(db.String(100), nullable=False,
                                     default='')

    is_enabled = db.Column(db.Boolean(), nullable=False, default=False)
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)

    projects = db.relationship('Project', back_populates='user')

    def __unicode__(self):
        return self.email

    def is_active(self):
        # HACK for Flask-Login :/
        return self.is_enabled


class Project(db.Model, models.BaseModelMixin, models.CreateAndModifyMixin):
    __tablename__ = 'projects'

    title = db.Column(db.Unicode(255), nullable=False)

    intercom_app_id = db.Column(db.Unicode(255), nullable=False, unique=True)
    intercom_api_key = db.Column(db.Unicode(255), nullable=False)
    intercom_webhooks_internal_secret = db.Column(db.Unicode(255))
    intercom_subscription_id = db.Column(db.Unicode(255))

    aws_access_id = db.Column(db.Unicode(255), nullable=False, unique=True)
    aws_secret_access_key = db.Column(db.Unicode(255), nullable=False)

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                        nullable=False)
    user = db.relationship('User', back_populates='projects')

    def __unicode__(self):
        return self.title

    @classmethod
    def get_for_current_user_or_404(cls, pk):
        return cls.get_or_404(cls.user_id == current_user.id, cls.id == pk)

    def use_intercom_credentials(project):
        """ Initiate contextmanager for working with Intercom.
        """
        return IntercomContextManager(project.intercom_app_id,
                                      project.intercom_api_key)

    def use_awis_credentials(project):
        """ Initiate contextmanager for working with AWIS.
        """
        return AWISContextManager(project.aws_access_id,
                                  project.aws_secret_access_key)

    def delete(self):
        if self.intercom_subscription_id:
            with self.use_intercom_credentials():
                sub = Subscription()
                sub.id = self.intercom_subscription_id
                sub.delete()
        return super(Project, self).delete()
