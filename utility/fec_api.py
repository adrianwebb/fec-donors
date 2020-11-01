import os
import time
import requests
import logging


logger = logging.getLogger(__name__)


class OpenFECException(Exception):
    pass


class OpenFECAPI(object):

    def __init__(self, command, year, page_count = 100):
        self.command = command
        self.year = year
        self.page_count = page_count

        self.api_key = os.environ.get('OPENFEC_API_KEY', None)

        self.ratelimit_remaining = 100
        self.wait_time = 0.5


    def fetch(self):
        raise NotImplementedError('Fetch command must be implemented in subclasses')


    def request(self, endpoint, options):
        url = "https://api.open.fec.gov/v1/{}".format(endpoint)
        params = dict(options)

        if not self.api_key:
            raise OpenFECException('Environment variable OPENFEC_API_KEY required with your API key')

        self.command.info("Requesting {} with options: {}".format(endpoint, options))
        params['api_key'] = self.api_key
        params['per_page'] = self.page_count
        response = self._throttled_request(url, params)
        logger.debug(response.url)

        if response.status_code != 200:
            raise OpenFECException("OpenFEC API returned status code: %s".format(response.status_code))

        return response.json()

    def _throttled_request(self, url, params):
        response = None

        if not self.ratelimit_remaining == 0:
            response = requests.get(url, params = params)
            self.ratelimit_remaining = int(response.headers['x-ratelimit-remaining'])

        if self.ratelimit_remaining == 0 or response.status_code == 429:
            while self.ratelimit_remaining == 0 or response.status_code == 429:
                self.wait_time *= 1.5

                logger.warn("API rate limit exceeded. Waiting {} seconds".format(self.wait_time))
                time.sleep(self.wait_time)

                response = requests.get(url, params = params)
                self.ratelimit_remaining = int(response.headers['x-ratelimit-remaining'])

        self.wait_time = 0.5
        return response
