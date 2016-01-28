import collections

import mock
from requests import RequestException
from tests.base import TestCase
from app.intercom.service import IntercomClient, TIMEOUT, RETRY_COUNT


@mock.patch('app.intercom.service.session')
class IntercomClientTestCase(TestCase):
    def test_init(self, *args):
        client = IntercomClient('app_id', 'api_key', 5)

        self.assertEqual(client.app_id, 'app_id')
        self.assertEqual(client.api_key, 'api_key')
        self.assertEqual(client.auth, ('app_id', 'api_key'))
        self.assertEqual(client.workers_count, 5)

    def test_get_headers(self, *args):
        client = IntercomClient('', '')
        extra_headers = {'X-Extra': 'Header-Value'}
        headers = client.get_headers(**extra_headers)

        self.assertEqual(headers['Accept'], 'application/json')
        self.assertEqual(headers['X-Extra'], 'Header-Value')

    def test_iter_users(self, session):
        client = IntercomClient(app_id='app_id', api_key='api_key')
        pages = 2

        response = mock.Mock()

        def _json():
            result = {
                'users': ['user_one', 'user_two'],
                'pages': {
                    'next': ''
                }
            }

            if response.json.call_count == pages:
                return result

            result['pages']['next'] = \
                'http://next.url/page=%s' % (response.json.call_count + 1)

            return result

        response.json.side_effect = _json
        session.get.return_value = response

        result = client.iter_users()
        self.assertIsInstance(result, collections.Iterable)

        result = list(result)

        self.assertEqual(response.raise_for_status.call_count, 2)
        self.assertEqual(session.get.call_count, 2)
        self.assertListEqual(
            ['user_one', 'user_two', 'user_one', 'user_two'],
            result
        )

        _common = dict(auth=client.auth, headers=client.get_headers(),
                       timeout=TIMEOUT)

        session.get.assert_has_calls([
            mock.call(
                'https://api.intercom.io/users?page=1&per_page=50&order=desc',
                **_common
            ),
            mock.call().raise_for_status(),
            mock.call().json(),
            mock.call('http://next.url/page=2', **_common),
            mock.call().raise_for_status(),
            mock.call().json(),
        ])

    def test_iter_users_retry(self, session):
        session.get.side_effect = RequestException
        client = IntercomClient(app_id='app_id', api_key='api_key')
        result = client.iter_users()

        self.assertRaises(RequestException, list, result)
        self.assertEqual(session.get.call_count, RETRY_COUNT)

    def test_update_users(self, session):
        user_data = [
            dict(user_id=1,
                 custom_attributes={'key': 'value'},
                 some_attr='some_value'),
            dict(user_id=2,
                 custom_attributes={'key': 'value2'},
                 some_attr='some_value2'),
        ]

        response = mock.Mock()
        response.json.return_value = {}
        session.post.return_value = response

        client = self._get_client()

        result = client.update_users(user_data, prefix='AA')
        self.assertDictEqual(result, {})

        session.post.assert_called_once_with(
            'https://api.intercom.io/bulk/users',
            json=dict(
                items=[
                    {
                        'method': 'post',
                        'data_type': 'user',
                        'data': {
                            'user_id': 1,
                            'custom_attributes': {'AA_key': 'value'},
                            'some_attr': 'some_value'
                        }
                    },
                    {
                        'method': 'post',
                        'data_type': 'user',
                        'data': {
                            'user_id': 2,
                            'custom_attributes': {'AA_key': 'value2'},
                            'some_attr': 'some_value2'
                        }
                    },
                ]
            ),
            auth=client.auth,
            headers=client.get_headers(),
            timeout=TIMEOUT
        )
        self.assertTrue(response.raise_for_status.call_count, 1)
        self.assertTrue(response.json.call_count, 1)

    def test_update_users_retry(self, session):
        session.post.side_effect = RequestException
        client = self._get_client()

        self.assertRaises(RequestException, client.update_users, [])
        self.assertEqual(session.post.call_count, RETRY_COUNT)

    def test_create_notes(self, session):
        data = [
            dict(user_id=1, body='body1'),
            dict(user_id=2, body='body2'),
        ]
        response = mock.Mock()
        session.post.return_value = response

        client = self._get_client()

        result = client.create_notes(data)
        self.assertEqual(result, None)
        self.assertEqual(session.post.call_count, len(data))
        self.assertTrue(response.raise_for_status.called)
        self.assertTrue(response.json.called)

        session.post.assert_has_calls([
            mock.call(
                'https://api.intercom.io/notes',
                json=dict(user={'user_id': 1}, body='body1'),
                auth=client.auth,
                headers=client.get_headers()
            ),
            mock.call().raise_for_status(),
            mock.call().json(),
            mock.call(
                'https://api.intercom.io/notes',
                json=dict(user={'user_id': 2}, body='body2'),
                auth=client.auth,
                headers=client.get_headers()
            ),
            mock.call().raise_for_status(),
            mock.call().json(),
        ])

    def test_create_notes_retry(self, session):
        data = [
            dict(user_id=1, body='body1'),
            dict(user_id=2, body='body2'),
        ]
        session.post.side_effect = RequestException
        client = self._get_client()

        self.assertRaises(RequestException, client.create_notes, data)
        self.assertEqual(session.post.call_count, RETRY_COUNT * len(data))

    def test_subscribe(self, session):
        hook_url = 'http://test.test/hook_url'
        topics = ['topic']

        response = mock.Mock()
        response.json.return_value = {'id': 'subscription-id'}
        session.post.return_value = response

        client = self._get_client()
        result = client.subscribe(hook_url, topics)

        self.assertEqual(result, response.json.return_value)

        session.post.assert_called_once_with(
            'https://api.intercom.io/subscriptions',
            json=dict(
                service_type='web',
                url=hook_url,
                topics=topics,
            ),
            auth=client.auth,
            headers=client.get_headers(),
        )
        self.assertEqual(response.raise_for_status.call_count, 1)
        self.assertEqual(response.json.call_count, 1)

    def test_subscribe_retry(self, session):
        session.post.side_effect = RequestException
        client = self._get_client()

        self.assertRaises(RequestException, client.subscribe, '', '')
        self.assertEqual(session.post.call_count, RETRY_COUNT)

    def test_unsubscribe(self, session):
        subscription_id = 'some-subscription-id'
        client = self._get_client()

        response = mock.Mock()
        response.json.return_value = {}
        session.delete.return_value = response

        result = client.unsubscribe(subscription_id)
        self.assertDictEqual(result, response.json.return_value)

        session.delete.assert_called_once_with(
            'https://api.intercom.io/subscriptions/%s' % subscription_id,
            auth=client.auth,
            headers=client.get_headers(),
        )
        self.assertEqual(response.raise_for_status.call_count, 1)
        self.assertEqual(response.json.call_count, 1)

    def test_unsubscribe_retry(self, session):
        session.delete.side_effect = RequestException
        client = self._get_client()

        self.assertRaises(RequestException, client.unsubscribe, '')
        self.assertEqual(session.delete.call_count, RETRY_COUNT)

    def _get_client(self):
        return IntercomClient('app_id', 'api_key')
