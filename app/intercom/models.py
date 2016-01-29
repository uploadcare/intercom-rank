import logging

from funcy import with_prev

from app import db
from common import models
from app.accounts.utils import email_is_useful, extract_domain
from app.accounts.tasks import (fetch_and_update_information,
                                erase_awis_information)


logger = logging.getLogger(__name__)


class IntercomUser(db.Model, models.BaseModelMixin):
    """ Because the Intercom's API doesn't provide any filtration we prefer
    to store information about Intercom's users on our side for increasing
    the performance of further operations with them.
    """
    __talbename__ = 'intercom_users'
    __table_args__ = (
        db.Index('project_user_index', 'project_id', 'user_id', unique=True),
        db.Index('project_domain_index', 'project_id', 'domain'),
    )

    project_id = db.Column(db.Integer(), db.ForeignKey('projects.id'),
                           nullable=False)
    project = db.relationship('Project', back_populates='intercom_users')

    domain = db.Column(db.Unicode(255), nullable=False)
    user_id = db.Column(db.Integer)

    is_useful_domain = db.Column(db.Boolean(), nullable=False, default=False)

    def __unicode__(self):
        return '{0.project_id}:{0.user_id}'.format(self)

    @classmethod
    def iter_and_sync(cls, project):
        client = project.get_intercom_client()

        for user_data in client.iter_users():
            if not user_data['email']:
                logger.warning('User don\'t have an email. Skip it.')
                continue

            email, user_id = user_data['email'], user_data['user_id']
            logger.info('Handle email: %s', email)
            row = cls.get_or_create(project, user_id, email, commit=False)

            yield row

        # TODO: write/find a contextprocessor for this?
        db.session.commit()

    @property
    def transformed_email(self):
        """ Construct a fake email address for internal use.
        """
        return '{}@{}'.format(self.user_id, self.domain)

    @classmethod
    def get_or_create(cls, project, user_id, email, commit=False):
        user_id = int(user_id)

        row = cls.query.filter(cls.project_id == project.id,
                               cls.user_id == user_id).first()

        if row is None:
            logger.info('Create information about new user: %s', email)
            row = cls(project_id=project.id, user_id=user_id)

        row.is_useful_domain = email_is_useful(email)
        row.domain = extract_domain(email)
        db.session.add(row)

        if commit:
            db.session.commit()

        return row

    @classmethod
    def iterate_over_changed_items(cls, domain, is_useful, commit=True):
        """ Iterator which changes ``.is_useful_domain`` property and gives a
        way to do are addition actions after that (e.g. commit changes :)
        """
        rows = cls.query.filter(
            cls.domain == domain, cls.is_useful_domain != is_useful
        ).order_by(cls.project_id.asc()).all()

        for row, prev_row in with_prev(rows):
            row.is_useful_domain = is_useful
            db.session.add(row)

            yield row, prev_row

        if commit:
            db.session.commit()


class FreeEmailProviderListChanged:
    """ Register common common operations which need to process when the
    FreeEmailProvider has been added or deleted.
    """
    def __init__(self, signal, task, is_useful_domain, collect_attribute):
        self.task = task
        self.collect_attribute = collect_attribute
        self.is_useful_domain = is_useful_domain
        signal.connect(self, sender='accounts.FreeEmailProvider')

    def __call__(self, sender, instance, **kwargs):
        users = IntercomUser.iterate_over_changed_items(
            instance.domain, self.is_useful_domain, commit=False)

        tmp = []
        for user, prev_user in users:
            # Project changed: commit our changes
            if prev_user and user.project_id != prev_user.project_id:
                db.session.commit()
                self.task.delay(tmp, prev_user.project_id)
                tmp = []

            tmp.append(getattr(user, self.collect_attribute))

        # If after iteration we still have unstaged data
        if tmp:
            db.session.commit()
            self.task.delay(tmp, user.project_id)


free_email_provider_added = \
    FreeEmailProviderListChanged(signal=models.post_save,
                                 task=erase_awis_information,
                                 is_useful_domain=False,
                                 collect_attribute='user_id')

free_email_provider_deleted = \
    FreeEmailProviderListChanged(signal=models.pre_delete,
                                 task=fetch_and_update_information,
                                 is_useful_domain=True,
                                 collect_attribute='transformed_email')
