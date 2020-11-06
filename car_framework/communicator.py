import requests, os
from requests.exceptions import ConnectionError, ConnectTimeout
from requests.auth import HTTPBasicAuth
from car_framework.util import get_json
from car_framework.context import context


class Response(object):
    def __init__(self, sc, data):
        self.status_code = sc
        self.data = data

    def json(self):
        return self.data


class Communicator(object):
    def __init__(self):
        self.headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}

        auth_token = context().args.api_token
        if auth_token:
            self.headers['Authorization'] = 'car-token ' + auth_token
            self.base_url = context().args.car_service_token_url
            self.basic_auth = None
        else:
            self.basic_auth = HTTPBasicAuth(context().args.api_key, context().args.api_password)
            self.base_url = context().args.car_service_apikey_url

        if not self.base_url.endswith('/'):
            self.base_url = self.base_url + '/'


    def make_url(self, path):
        if path.startswith('http'):
            context().logger.warn('A URL is passed in to the Communicator instead of a path: ' + path)
            return path

        if path.startswith('/'): path = path[1:]
        return self.base_url + path


    def send_request(self, req, func, path, **args):
        try:
            url = self.make_url(path)
            resp = func(url, auth=self.basic_auth, allow_redirects=False, headers=self.headers, **args)
            context().logger.debug('%s %s, status code: %d, response data: %s' % (req, url, resp.status_code, get_json(resp)))
            if resp.status_code != 200:
                context().logger.warn('%s %s, status code: %d, response data: %s, request params: %s, request data: %s' % (req,
                    url, resp.status_code, get_json(resp), args.get('params'), args.get('data')))
            return resp
        except (ConnectionError, ConnectTimeout) as e:
            context().logger.error('Error while sending %s request: %s' % (req, str(e)))
            return Response(503, {'error' : str(e)})


    def post(self, path, **args):
        return self.send_request('POST', requests.post, path, **args)


    def get(self, path, **args):
        return self.send_request('GET', requests.get, path, **args)


    def patch(self, path, **args):
        return self.send_request('PATCH', requests.patch, path, **args)


    def delete(self, path, **args):
        return self.send_request('DELETE', requests.delete, path, **args)
