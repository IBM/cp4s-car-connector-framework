import requests, os
from requests.exceptions import ConnectionError, ConnectTimeout, RetryError
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from car_framework.util import get_json
from car_framework.context import context

default_api_version = '/v2'

class Response(object):
    def __init__(self, sc, data):
        self.status_code = sc
        self.data = data

    def json(self):
        return self.data


class CallbackRetry(Retry):
    def increment(self, method, url, *args, **kwargs):
        try:
            self.retry_callback(url, self.get_backoff_time())
        except Exception:
            context().logger.info('CallbackRetry raised an exception, ignoring')
        return super(CallbackRetry, self).increment(method, url, *args, **kwargs)

    def retry_callback(self, url, backoff_time):
        context().logger.info('Retry after %s sec invoked with url %s' % (backoff_time, url))


class Communicator(object):
    def __init__(self):
        self.headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}

        auth_token = context().args.CAR_SERVICE_AUTHTOKEN
        if auth_token:
            self.headers['Authorization'] = 'car-token ' + auth_token
            self.base_url = context().args.CAR_SERVICE_URL_FOR_AUTHTOKEN
            self.basic_auth = None
        else:
            self.basic_auth = HTTPBasicAuth(context().args.CAR_SERVICE_KEY, context().args.CAR_SERVICE_PASSWORD)
            self.base_url = context().args.CAR_SERVICE_URL

        if not self.base_url.endswith('/'):
            self.base_url = self.base_url + '/'

        retry_strategy = CallbackRetry(
            total=3,
            backoff_factor=10,
            raise_on_status=False,
            status_forcelist=[403, 429, 503],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)


    def make_url(self, path):
        if path.startswith('http'):
            context().logger.warn('A URL is passed in to the Communicator instead of a path: ' + path)
            return path

        if path.startswith('/'): path = path[1:]
        return self.base_url + path


    def send_request(self, req, func, path, **args):
        try:
            url = self.make_url(path)
            if 'api_version' in args:
                url = url.replace(default_api_version, args['api_version'])
                del args['api_version']

            resp = func(url, auth=self.basic_auth, allow_redirects=False, headers=self.headers, **args)
            context().logger.debug('%s %s, status code: %d, response data: %s' % (req, url, resp.status_code, get_json(resp)))
            if resp.status_code not in (200, 201):
                context().logger.warn('%s %s, status code: %d, response data: %s, request params: %s, request data: %s' % (req,
                    url, resp.status_code, get_json(resp), args.get('params'), args.get('data')))
            return resp
        except RetryError as e:
            context().logger.error('Max retries exceeded error while sending %s request: %s' % (req, str(e)))
            return Response(503, {'error' : str(e)})
        except (ConnectionError, ConnectTimeout) as e:
            context().logger.error('Error while sending %s request: %s' % (req, str(e)))
            return Response(503, {'error' : str(e)})


    def post(self, path, **args):
        return self.send_request('POST', self.http.post, path, **args)


    def get(self, path, **args):
        return self.send_request('GET', self.http.get, path, **args)


    def patch(self, path, **args):
        return self.send_request('PATCH', self.http.patch, path, **args)


    def delete(self, path, **args):
        return self.send_request('DELETE', self.http.delete, path, **args)
