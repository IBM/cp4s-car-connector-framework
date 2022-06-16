from datetime import datetime
import json
import jsonpickle
import os
import shutil
import uuid

from car_framework.context import context
from car_framework.full_import import BaseFullImport


class JsonField():
    def __init__(self, obj):
        self.obj = obj


class Mutation():
    def __init__(self, collection_name, data):
        self.collection_name = collection_name
        self.data = data
        self.var_count = 0
        self.vars = {}


    def save(self, file_path):
        data = jsonpickle.encode(self)
        with open(file_path, 'w') as outfile:
            outfile.write(data)


    @staticmethod
    def load(file_path):
        with open(file_path, 'r') as inpfile:
            data = inpfile.read()
            mutation = jsonpickle.decode(data)
            return mutation


    def serialize(self):
        body = '''
            {
                insert_%s(objects: [ %s ]) { affected_rows }
            }
        ''' % (self.collection_name, ',\n'.join( map(lambda item: self._serialize_object(item), self.data) ))

        args = ''
        if self.vars: args = '(%s)' % ', '.join( map(lambda var: f'${var}: jsonb', self.vars.keys()) )

        query = 'mutation %s %s' % (args, body)
        if self.vars: return {'query': query, 'variables': self.vars}
        else: return {'query': query}


    def _serialize_object(self, obj):
        return '{%s}' % ', '.join(map(lambda item: self._serialize_field(item[0], item[1]), obj.items()))


    def _serialize_field(self, name, value):
        if isinstance(value, JsonField): return '%s: %s' % (name, self._serialize_json_field(value))
        elif type(value) == int or type(value) == float: return '%s: %s' % (name, value)
        else: return '%s: "%s"' % (name, str(value))


    def _serialize_json_field(self, value):
        self.var_count += 1
        self.vars['var%d' % self.var_count] = value.obj
        return '$var%d' % self.var_count



class BaseDataHandler():

    source = None
    report = None
    source_report = None
    collections = {}
    collection_keys = {}
    edges = {}
    edge_keys = {}

    def __init__(self):
        self.export_data_dir = os.path.join(context().args.export_data_dir, datetime.now().strftime('%Y-%m-%d_%H:%M:%S_r%f'))

    # Adds the collection data
    def add_item_to_collection(self, name, object):
        objects = self.collections.get(name)
        if not objects:
            objects = []
            self.collections[name] = objects

        keys = self.collection_keys.get(name)
        if not keys:
            keys = []
            self.collection_keys[name] = keys

        if not object['external_id'] in self.collection_keys[name]:
            objects.append(object)
            self.collection_keys[name].append(object['external_id'])

        # dump collection to file to free memory
        if len(self.collections[name]) >= context().args.export_data_page_size:
            self._save_export_data_file(name, self.collections[name])
            self.collections[name] = []

    # Adds the edge between two vertices

    def add_edge(self, name, object):
        objects = self.edges.get(name)
        if not objects:
            objects = []
            self.edges[name] = objects

        keys = self.edge_keys.get(name)
        if not keys:
            keys = []
            self.edge_keys[name] = keys

        key = '#'.join(str(x) for x in object.values())
        if not key in self.edge_keys[name]:
            object['source'] = context().args.source
            object['reported_at'] = context().report_time
            objects.append(object)
            self.edge_keys[name].append(key)

        # dump edges to file to free memory
        if len(self.edges[name]) >= context().args.export_data_page_size:
            self._save_export_data_file(name, self.edges[name])
            self.edges[name] = []

    def send_collections(self, importer):
        context().logger.info('Creating vertices')
        for name, data in self.collections.items():
            # save residual data
            if len(data) > 0:
                self._save_export_data_file(name, data)
            self._send(name, importer)
        context().logger.info('Creating vertices: done %s', {key: len(value) for key, value in self.collection_keys.items()})

    def send_edges(self, importer):
        context().logger.info('Creating edges')
        for name, data in self.edges.items():
            # save residual data
            if len(data) > 0:
                self._save_export_data_file(name, data)
            self._send(name, importer)
        context().logger.info('Creating edges done: %s', {key: len(value) for key, value in self.edge_keys.items()})

    def _create_export_data_dir(self, name):
        dir_path = os.path.join(self.export_data_dir, name)
        if not os.path.exists(dir_path):
            context().logger.debug('Creating export_data dir: %s', dir_path)
            os.makedirs(dir_path)

        return dir_path

    def _delete_export_data_dir(self, export_data_dir):
        if not context().args.keep_export_data_dir and os.path.exists(export_data_dir):
            context().logger.debug('Delete export_data dir: %s', export_data_dir)
            shutil.rmtree(export_data_dir)

    def _save_export_data_file(self, name, data):
        dir_path = self._create_export_data_dir(name)
        filename = os.path.join(dir_path, '%s.json' % str(uuid.uuid4())[0:8])
        mutation = Mutation(name, data)
        mutation.save(filename)
        return filename

    def _send(self, name, importer):
        dir_path = os.path.join(self.export_data_dir, name)
        for _, _, files in os.walk(dir_path):
            for data_file in files:
                mutation = Mutation.load(os.path.join(dir_path, data_file))
                importer.send_mutation(mutation)
        self._delete_export_data_dir(dir_path)

    def printData(self):
        context().logger.debug("Vertexes to be created:")
        context().logger.debug(self.collections)
        context().logger.debug("Edges to be created:")
        context().logger.debug(self.edges)
