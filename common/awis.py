import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from awis import AwisApi
from funcy import chunks

logger = logging.getLogger(__name__)


class AWISContextManager:
    def __init__(self, access_id, secret_access_key, workers_count=10):
        self.auth = (access_id.encode('utf-8'),
                     secret_access_key.encode('utf-8'))
        self.workers_count = workers_count
        self.closed = False

    def __enter__(self):
        self.api = AwisApi(*self.auth)
        self.session_result = {}
        self.session_list_of_raw_result = []
        return self

    def __exit__(self, *args):
        self.closed = True
        # TODO: handle exceptions
        pass

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
            tasks = [executor.submit(request, chunk, categories)
                     for chunk in chunks(CHUNK_SIZE, domains)]

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
