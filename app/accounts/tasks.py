import logging
import asyncio
from itertools import chain

from requests.exceptions import ReadTimeout, ConnectionError
from funcy.seqs import ichunks
from celery import chord

from app import celery, FREE_EMAILS_SET


logger = logging.getLogger(__name__)


@celery.task(default_retry_delay=0, max_retries=3)
def handle_intercom_users(project_id):
    """ Background task which runs after creation of project.
    Fetch and filter users from Intercom. After that call task for
    fetching information from AWIS.
    """
    from app.accounts.models import Project

    # Maximum items per request for Intercom's bulk update
    CHUNK_SIZE = 10

    project = Project.query.filter(Project.id == project_id).first()
    if not project:
        logger.error('Project with id == {} does not exist'.format(project_id))
        return

    def _fetch_users():
        with project.use_intercom_credentials() as intercom:
            for user in intercom.users():
                email_domain = (user.email or '').split('@')[-1]

                if not email_domain or email_domain in FREE_EMAILS_SET:
                    continue

                logger.info('Handle email: %s', user.email)

                yield '{}@{}'.format(user.user_id, email_domain)

    try:
        for emails in ichunks(CHUNK_SIZE, _fetch_users()):
            fetch_and_update_information.delay(emails, project_id)
    except (ReadTimeout, ConnectionError) as e:
        handle_intercom_users.retry(exc=e)


@celery.task
def fetch_and_update_information(emails, project_id):
    # Maximum items per request for AWIS
    CHUNK_SIZE = 5

    # {domain.com: users_id, ...}
    domains_map = dict(e.split('@')[::-1] for e in emails)

    tasks = [awis_info.s(batch) for batch in
             ichunks(CHUNK_SIZE, domains_map.keys())]
    callback = update_intercom_users.s(project_id=project_id,
                                       domains_map=domains_map)

    chord(tasks)(callback)


@celery.task
def awis_info(domains):
    # NOTE: write real code
    logger.info('Make AWIS request')
    logger.info(domains)

    # ========> TODO: remove this
    import time; time.sleep(1)
    import random, string

    # Returns data for user_id
    result = dict.fromkeys(domains)

    for d in domains:
        result[d] = {'AWIS_ATTR': ''.join(
            random.sample(string.ascii_letters, 5))}

    return result


@celery.task
def update_intercom_users(data, project_id, domains_map):
    from app.accounts.models import Project

    # Make list: [{user_id: 12, other_data}, ...]
    result = [
        dict(data, user_id=domains_map[domain])
        for row in data
        for domain, data in row.items()
    ]

    project = Project.query.filter(Project.id == project_id).first()
    if not project:
        logger.error('Project with id == %s does not exist', project_id)
        return

    with project.use_intercom_credentials() as intercom:
        intercom.users_bulk_update(result)
