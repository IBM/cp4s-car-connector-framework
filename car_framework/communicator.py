import requests
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
        self.api_key = context().args.api_key
        self.password = context().args.api_password


    def send_request(self, req, func, url, **args):
        try:
            resp = func(url, auth=HTTPBasicAuth(self.api_key, self.password), allow_redirects=False, headers=self.headers, **args)
            context().logger.debug('%s %s, status code: %d, response data: %s' % (req, url, resp.status_code, get_json(resp)))
            if resp.status_code != 200:
                context().logger.warn('%s %s, status code: %d, response data: %s, request params: %s, request data: %s' % (req, 
                    url, resp.status_code, get_json(resp), args.get('params'), args.get('data')))
            return resp
        except (ConnectionError, ConnectTimeout) as e:
            context().logger.error('Error while sending %s request: %s' % (req, str(e)))
            return Response(503, {'error' : str(e)})
    

    def post(self, url, **args):
        return self.send_request('POST', requests.post, url, **args)


    def get(self, url, **args):
        return self.send_request('GET', requests.get, url, **args)


    def patch(self, url, **args):
        return self.send_request('PATCH', requests.patch, url, **args)


    def delete(self, url, **args):
        return self.send_request('DELETE', requests.delete, url, **args)
