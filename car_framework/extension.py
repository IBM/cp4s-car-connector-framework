from sys import version
from car_framework.context import context


class SchemaExtension(object):
    def __init__(self, key, owner, version, schema):
        self.key = key
        self.owner = owner
        self.version = version
        self.schema = schema

    def setup(self):
        current_version = context().car_service.get_extension(self.key)
        if current_version:
            if current_version['version'] == self.version: return
            if int(self.version) < int(current_version['version']):
                raise Exception('More recent version of schema extension is already set up: %s' % current_version.version)

        context().car_service.setup_extension(self)
