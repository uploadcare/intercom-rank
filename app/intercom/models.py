import logging
from app import db

from common import models
from app.accounts.utils import email_is_useful, extract_domain
from app.accounts.tasks import fetch_and_update_information


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


def new_domain_added_to_black_list(sender, instance, **kwargs):
    users = IntercomUser.query.filter(
        IntercomUser.domain == instance.domain,
        IntercomUser.is_useful_domain == True  # NOQA
    ).order_by(IntercomUser.project_id.asc()).all()

    project_map = {}
    for user in users:
        project_map.setdefault(user.project_id, []).append(user)

    for project_id, users in project_map.items():
        client = users[0].project.get_intercom_client()
        users_data = []

        for user in users:
            user.is_useful_domain = False
            db.session.add(user)
            users_data.append(dict(
                user_id=user.user_id,
                custom_attributes={
                    'lang': None,
                    'country_rank': None,
                    'rank_value': None,
                    'per_million': None,
                    'page_views_per_million': None,
                }
            ))

        client.update_users(users_data, prefix='AWIS')
        db.session.commit()


def domain_removed_from_black_list(sender, instance, **kwargs):
    users = IntercomUser.query.filter(
        IntercomUser.domain == instance.domain,
        IntercomUser.is_useful_domain == False  # NOQA
    ).order_by(IntercomUser.project_id.asc()).all()

    project_map = {}
    for user in users:
        project_map.setdefault(user.project_id, []).append(user)

    for project_id, users in project_map.items():
        emails = []
        for user in users:
            user.is_useful_domain = True
            db.session.add(user)
            emails.append(user.transformed_email)

        db.session.commit()
        fetch_and_update_information.delay(emails, project_id)


models.post_save.connect(new_domain_added_to_black_list,
                         sender='accounts.FreeEmailProvider')
models.pre_delete.connect(domain_removed_from_black_list,
                          sender='accounts.FreeEmailProvider')
