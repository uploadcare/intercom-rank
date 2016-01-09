import logging
from concurrent.futures import ThreadPoolExecutor

import requests
from intercom import Intercom, User


logger = logging.getLogger(__name__)

session = requests.session()
TIMEOUT = 30


class IntercomContextManager:
    def __init__(self, app_id, api_key):
        self.auth = (app_id, api_key)

    def __enter__(self):
        Intercom.app_id, Intercom.app_api_key = self.auth
        return self

    def __exit__(self, *args):
        Intercom.app_id = Intercom.app_api_key = None
        # TODO: handle exceptions

    def users_bulk_update(self, data):
        logger.info('Intercom bulk update.')
        logger.info(data)
        # return self._real_bulk_update(data)

        def update(row):
            user_id = row.pop('user_id')
            User.create(user_id=user_id, custom_attributes=row)

        with ThreadPoolExecutor(5) as executor:
            for _ in executor.map(update, data):
                pass

    def _real_bulk_update(self, data):
        # Temporarily disabled because API does not working. Wrote a ticket.
        response = session.post(
            'https://api.intercom.io/bulk/users',
            auth=self.auth,
            headers={'Accept': 'application/json'},
            params={'items': [
                {'method': 'post', 'data_type': 'user',
                 'data': {'user_id': d.pop('user_id'),
                          'custom_attributes': d}} for d in data]},
            timeout=TIMEOUT)
        response.raise_for_status()
        logger.info(response.json())
        return response

    def users(self):
        """ Interator over users.
        """
        # TODO impement own solution and drop python-intercom
        for user in User.all():
            yield user
