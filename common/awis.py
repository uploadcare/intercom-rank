import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from awis import AwisApi
from funcy import chunks
from redis import Redis

from app import redis_pool


logger = logging.getLogger(__name__)


class AWISContextManager:
    def __init__(self, access_id, secret_access_key, workers_count=5):
        self.auth = (access_id.encode('utf-8'),
                     secret_access_key.encode('utf-8'))
        self.workers_count = workers_count
        self.closed = False
        self.cache = Cache()

    def __enter__(self):
        self.api = AwisApi(*self.auth)
        self.session_result = {}
        self.session_list_of_raw_result = []
        return self

    def __exit__(self, *args):
        # Save new values (or update exists)
        for d, data in self.session_result.items():
            self.cache.set(d, data)

        self.closed = True

    def url_info(self, domains, *categories):
        """ Wrapper over `AwisApi.url_info` for parallel processing.
        """
        if self.closed:
            raise AttributeError('Session is closed')

        CHUNK_SIZE = 5  # AWIS`s limit

        def request(domains, categories):
            logger.info('AWIS request for %s', domains)
            return self.api.url_info(domains, *categories)

        with ThreadPoolExecutor(self.workers_count) as executor:
            tasks = [
                executor.submit(request, chunk, categories)
                for chunk in chunks(CHUNK_SIZE, self.handle_cache(domains))
            ]

            for future in as_completed(tasks):
                self.session_list_of_raw_result.append(future.result())

    def get_value(self, root, path, default=None):
        """ Shortcut for fetching first node.
        """
        path = self.handle_path(path)
        return getattr(root.find(path, self.api.NS_PREFIXES), 'text', default)

    def iter_results(self, path):
        """ Iterator for filling results for a particular domain.
        """
        path = self.handle_path(path)
        for tree in self.session_list_of_raw_result:
            for node in tree.findall(path, self.api.NS_PREFIXES):
                domain = self.get_value(node, 'DataUrl')
                result_row = self.session_result.setdefault(
                    domain, defaultdict(lambda: None))

                yield domain, node, result_row

    @staticmethod
    def handle_path(path):
        # TODO: compile reg-exp?
        return './/awis:%s' % (path.strip('.//').strip('/')
                               .replace('/', '/awis:'))

    def handle_cache(self, domains):
        """ Filter domains which already in cache and put them into the result.
        """
        for d in domains:
            cached_value = self.cache.get(d)

            if cached_value:
                self.session_result[d] = cached_value
                continue

            yield d


class Cache:
    key_tmpl = 'AWIS:cache:%s'

    def __init__(self):
        self.redis = Redis(connection_pool=redis_pool)
        self.default_expire = 60 * 60 * 24 * 7  # 7 days

    def get_key(self, domain):
        return self.key_tmpl % domain

    def get(self, domain):
        key = self.get_key(domain)
        value = self.redis.get(key)

        if value:
            logger.debug('Domain %s found in cache', domain)
            value = json.loads(value.decode('utf-8'))

        return value

    def set(self, domain, value):
        key = self.get_key(domain)
        self.redis.set(key, json.dumps(value), ex=self.default_expire)
