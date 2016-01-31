import re
import logging
import time
import random
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

import requests
import bleach
from funcy import retry, log_calls, pluck, chunks


logger = logging.getLogger(__name__)

session = requests.session()
TIMEOUT = 30
RETRY_COUNT = 3


def _timeout(i):
    from app import app
    if app.config.get('TESTING'):
        return 0
    return 2 ** i


def wait(wait_range=15):
    wait_time = random.choice(range(wait_range))
    logger.info('Wait %s seconds.', wait_time)
    time.sleep(wait_time)


requests_retry = retry(RETRY_COUNT, errors=requests.RequestException,
                       timeout=_timeout)


class IntercomError(Exception):
    """ Base exception for IntercomClient.
    """


class IntercomValidationError(IntercomError):
    """ Incorrect value for one of the request's parameter.
    """


class IntercomClient:
    """ Client for making requests to the Intercom's API.
    Ref: https://developers.intercom.io/docs
    """
    # TODO: Add validation for incoming and outgoing values
    # See: https://github.com/nicolaiarocci/cerberus
    base_url = 'https://api.intercom.io'

    def __init__(self, app_id, api_key, workers_count=10):
        self.app_id = app_id
        self.api_key = api_key
        self.auth = (app_id, api_key)
        self.workers_count = workers_count

    def get_headers(self, **extra):
        default = {'Accept': 'application/json'}
        default.update(extra)
        return default

    def get_executor(self):
        return ThreadPoolExecutor(self.workers_count)

    @log_calls(logger.debug)
    def iter_users(self, per_page=50, order='desc'):
        VALID_ORDERS = ('desc', 'asc')
        if order not in VALID_ORDERS:
            raise IntercomValidationError('order can by %s' % VALID_ORDERS)

        @requests_retry
        def _request(url):
            response = session.get(url,
                                   auth=self.auth,
                                   headers=self.get_headers(),
                                   timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()

        url = '{0}/users?page=1&per_page={1}&order={2}'.format(
            self.base_url, per_page, order)

        while True:
            response = _request(url)

            for user_data in response['users']:
                yield user_data

            if response['pages']['next']:
                url = response['pages']['next']
            else:
                break

    @log_calls(logger.debug)
    def update_users(self, users_data, prefix=None):
        """ Uses Intercom's bulk update.
        """
        CHUNK_SIZE = 50  # Intercom's limitation

        @requests_retry
        def request(chunk_of_users_data):
            url = '{0}/bulk/users'.format(self.base_url)
            response = session.post(
                url,
                json={'items': [
                    {
                        'method': 'post',
                        'data_type': 'user',
                        'data': apply_prefix_for_user_data(ch, prefix)
                    } for ch in chunk_of_users_data]
                },
                auth=self.auth,
                headers=self.get_headers(),
                timeout=TIMEOUT)
            # TODO: re-raise custom exception for 429 HTTP error
            # for further handling (e.g. retry celery task)
            response.raise_for_status()
            result = response.json()

            try:
                status_url = result['links']['self']
                logger.debug('Bulk update status: %s', status_url)
            except KeyError:
                logger.error('Weird response from Intercom: %r', result)

            return result

        with self.get_executor() as executor:
            for _ in executor.map(request, chunks(CHUNK_SIZE, users_data)):
                pass

    @log_calls(logger.debug)
    def update_user(self, user_data, prefix=None):
        """ Update a single user
        """
        @requests_retry
        def request(user_data):
            url = '{0}/users'.format(self.base_url)
            response = session.post(
                url,
                json=apply_prefix_for_user_data(user_data, prefix),
                auth=self.auth,
                headers=self.get_headers(),
                timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()

        return request(user_data)

    @log_calls(logger.debug)
    def create_notes(self, data, force=False):
        url = '{0}/notes'.format(self.base_url)

        @requests_retry
        def request(row):
            wait()

            response = session.post(
                url,
                json=dict(user={'user_id': row['user_id']}, body=row['body']),
                auth=self.auth,
                headers=self.get_headers(),
            )

            response.raise_for_status()
            return response.json()

        def iter_data(data):
            if force:
                return iter(data)

            # Filter notes for excluding duplicates
            exist_notes = self.get_notes(pluck('user_id', data))

            for row in data:
                user_id, body = str(row['user_id']), row['body']

                if user_id not in exist_notes:
                    yield row
                    continue

                bodies = map(normalize_note,
                             pluck('body', exist_notes[user_id]))
                if normalize_note(body) not in bodies:
                    yield row
                    continue

                logger.debug(
                    'The note with this body already exists: %r', row)

        with ThreadPoolExecutor(self.workers_count) as executor:
            for _ in executor.map(request, iter_data(data)):
                pass

    @log_calls(logger.debug)
    def get_notes(self, users_ids):
        """ Fetch notes for users. Returns a dict like: {user_id: [note, note]}
        """
        url = '{0}/notes'.format(self.base_url)

        @requests_retry
        def request(user_id):
            response = session.get(
                url,
                data={'user_id': user_id},
                auth=self.auth,
                headers=self.get_headers(),
            )

            response.raise_for_status()
            result = response.json()
            result['user_id'] = str(user_id)
            return result

        result = {}

        with ThreadPoolExecutor(self.workers_count) as executor:
            for row in executor.map(request, users_ids):
                result[row['user_id']] = row['notes']

        return result

    @log_calls(logger.debug)
    def subscribe(self, hook_url, topics):
        url = '{0}/subscriptions'.format(self.base_url)

        @requests_retry
        def request(hook_url, topics):
            response = session.post(
                url,
                json=dict(
                    service_type='web',
                    url=hook_url,
                    topics=topics
                ),
                auth=self.auth,
                headers=self.get_headers()
            )

            response.raise_for_status()
            return response.json()

        return request(hook_url, topics)

    @log_calls(logger.debug)
    def unsubscribe(self, subscription_id):
        url = '{0}/subscriptions/{1}'.format(self.base_url, subscription_id)

        @requests_retry
        def request(url):
            response = session.delete(
                url,
                auth=self.auth,
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()

        return request(url)


def apply_prefix_for_user_data(user_data, prefix=None):
    if not prefix or 'custom_attributes' not in user_data:
        return user_data

    user_data = deepcopy(user_data)
    user_data['custom_attributes'] = {
        '_'.join((prefix, k)): v
        for k, v in user_data['custom_attributes'].items()
    }

    return user_data


def normalize_note(body):
    """ Used for comparing notes.
    """
    body = bleach.clean(body, strip=True)
    return re.sub('\s', '', body).lower()
