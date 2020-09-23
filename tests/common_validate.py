import re
import ipaddress
import datetime
import logging
import os
import json

from car_framework.context import Context, context

class Struct(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [Struct(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, Struct(b) if isinstance(b, dict) else b)

def context_patch():

    context_args = {
        'car_service': 'https://example.com/api/car/v2',
        'api_key': None,
        'api_password': 'abc-xyz',
        'source': 'AWS-TEST',
        'debug': False,
        'last_model_state_id': "1580649320000",
        'current_time': "1580649321920",
    }
    Context(Struct(context_args))

    context().last_model_state_id = context().args.last_model_state_id
    context().current_time = context().args.current_time

class JsonResponse:
    """
     Summary conversion of json data to dictionary.
          """
    def __init__(self, response_code, filename):
        self.status_code = response_code
        self.filename = filename

    def status_code(self):
        return self.status_code

    def json(self):
        cur_path = os.path.dirname(__file__)
        abs_file_path = os.path.join(cur_path, "aws_test_log", self.filename)
        json_file = open(abs_file_path)
        json_str = json_file.read()
        json_data = json.loads(json_str)
        return json_data

    def text(self):
        cur_path = os.path.dirname(__file__)
        abs_file_path = os.path.join(cur_path, "aws_test_log", self.filename)
        json_file = open(abs_file_path)
        json_str = json_file.read()
        return json_str


class MockJsonResponse:
    """
    Summary Json response handler
        """
    def __init__(self, response_code, obj):
        self.status_code = response_code
        self.text = str(obj)

    def json(self):
        json_data = json.loads(self.text)
        return json_data


class JsonTextResponse:
    """
    Summary Json text response handler
        """
    def __init__(self, response_code, obj):
        self.status_code = response_code
        self.text = str(obj)

    def status_code(self):
        return self.status_code

    def text(self):
        return self.text


