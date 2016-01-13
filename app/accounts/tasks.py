import logging
from collections import defaultdict

from requests.exceptions import ReadTimeout, ConnectionError
from funcy.seqs import ichunks

from app import celery, app
from app.accounts.utils import transform_email_if_useful


logger = logging.getLogger(__name__)


@celery.task(default_retry_delay=0, max_retries=3)
def handle_intercom_users(project_id):
    """ Background task which runs after creation of project.
    Fetch and filter users from Intercom. After that call task for
    fetching information from the AWIS.
    """
    from app.accounts.models import Project

    # Maximum items per request for Intercom's bulk update
    CHUNK_SIZE = 100

    project = Project.query.filter(Project.id == project_id).first()
    if not project:
        logger.error('Project with id == {} does not exist'.format(project_id))
        return

    def _fetch_users():
        counter = 0
        client = project.get_intercom_client()

        for user in client.get_users():
            if not user['email']:
                continue

            logger.info('Handle email: %s', user['email'])

            user_email = transform_email_if_useful(user['email'],
                                                   user['user_id'])

            if not user_email:
                logger.info('Unuseful email. Skip.')
                continue

            # TODO: remove this code in production
            if 0 < app.config['AWIS_USER_LIMIT_FOR_PROJECT'] < counter:
                logger.info('Limit for project has been reached.')
                break

            counter += 1
            yield user_email

    try:
        for emails in ichunks(CHUNK_SIZE, _fetch_users()):
            fetch_and_update_information.delay(emails, project_id)
    except (ReadTimeout, ConnectionError) as e:
        handle_intercom_users.retry(exc=e)


@celery.task
def fetch_and_update_information(emails, project_id):
    from app.accounts.models import Project

    project = Project.query.filter(Project.id == project_id).first()
    if not project:
        logger.error('Project with id == %s does not exist', project_id)
        return

    # {domain.com: [users_id, user_id], ...}
    domains_map = defaultdict(list)
    for e in emails:
        key, value = e.split('@')[::-1]
        domains_map[key].append(value)

    with project.start_awis_session() as awis:
        awis.url_info(domains_map.keys(),
                      'UsageStats', 'SiteData', 'Language', 'RankByCountry')

        for domain, node, result_row in awis.iter_results('ContentData'):
            result_row['lang'] = awis.get_value(node, 'Language/Locale')
            result_row['site_data'] = {
                'title': awis.get_value(
                    node, 'SiteData/Title', default='-'),
                'description': awis.get_value(
                    node, 'SiteData/Description', default='-'),
                'online_since': awis.get_value(
                    node, 'SiteData/OnlineSince', default='-'),
            }

        for domain, node, result_row in awis.iter_results('TrafficData'):
            if result_row['lang']:
                result_row['country_rank'] = awis.get_value(
                    node, 'Country[@Code="{0}"]Rank'.format(
                        result_row['lang'].upper()))

            # Try to determinate the best rank over all countries by raw select
            if result_row['country_rank'] is None:
                result_row['country_rank'] = min([
                    int(e.text) for e in
                    node.findall('.//awis:Country/awis:Rank',
                                 awis.api.NS_PREFIXES)
                    if e.text] or [None])

            result_row['rank_value'] = awis.get_value(
                node, 'Reach/Rank/Value')

            result_row['per_million'] = awis.get_value(
                node, 'Reach/PerMillion/Value')

            result_row['page_views_per_million'] = awis.get_value(
                node, 'PageViews/PerMillion/Value')

        notes = []
        users = []

        for domain, data in awis.session_result.items():
            note_body = ('Title: {title}\n'
                         'Descr: {description}\n'
                         'Since: {online_since}\n'.format(
                         **data.pop('site_data')))

            for user_id in domains_map[domain]:
                # Put note to the bulk update
                notes.append(dict(user_id=user_id, body=note_body))

                # Put user to the bulk update
                users.append(dict(user_id=user_id, custom_attributes=data))

    intercom = project.get_intercom_client()
    intercom.update_users(users, prefix='AWIS')
    intercom.create_notes(notes)
