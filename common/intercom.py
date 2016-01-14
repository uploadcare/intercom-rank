import logging
from concurrent.futures import ThreadPoolExecutor

import requests
from funcy import retry, log_calls


logger = logging.getLogger(__name__)

session = requests.session()
TIMEOUT = 30

requests_retry = retry(3, errors=requests.RequestException,
                       timeout=lambda a: 2 ** a)


class IntercomClient:
    """ Client for making requests to the Intercom's API.
    Ref: https://developers.intercom.io/docs
    """
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

    @log_calls(logger.debug)
    def get_users(self, per_page=25, order='desc'):
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
        url = '{0}/bulk/users'.format(self.base_url)

        def apply_prefix(row, prefix):
            if prefix and 'custom_attributes' in row:
                row['custom_attributes'] = {
                    '_'.join((prefix, k)): v
                    for k, v in row['custom_attributes'].items()
                }
            return row

        @requests_retry
        def request(url, users_data, prefix):
            response = session.post(
                url,
                json={'items': [
                    {'method': 'post', 'data_type': 'user',
                     'data': apply_prefix(d, prefix)} for d in users_data]},
                auth=self.auth,
                headers=self.get_headers(),
                timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()

        return request(url, users_data, prefix)

    @log_calls(logger.debug)
    def create_notes(self, data):
        url = '{0}/notes'.format(self.base_url)

        @requests_retry
        def request(row):
            if 'user_id' in row:
                row['user'] = {
                    'user_id': row.pop('user_id')
                }

            response = session.post(
                url,
                json=row,
                auth=self.auth,
                headers=self.get_headers(),
            )

            response.raise_for_status()
            return response.json()

        with ThreadPoolExecutor(self.workers_count) as executor:
            for _ in executor.map(request, data):
                pass

    @log_calls(logger.debug)
    def subscribe(self, hook_url, topics):
        logger.debug('IntercomClient.subscribe')
        logger.debug(hook_url)

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
