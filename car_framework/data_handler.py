from datetime import datetime
import json
import os
import shutil
import uuid

from car_framework.context import context


def get_report_time():
    delta = datetime.utcnow() - datetime(1970, 1, 1)
    milliseconds = delta.total_seconds() * 1000
    return milliseconds


class BaseDataHandler():

    source = None
    report = None
    source_report = None
    collections = {}
    collection_keys = {}
    edges = {}
    edge_keys = {}

    def __init__(self):
        self.timestamp = get_report_time()
        self.export_data_dir = os.path.join(context().args.export_data_dir, datetime.now().strftime('%Y-%m-%d_%H:%M:%S_r%f'))

    def create_source_report_object(self):
        raise NotImplementedError()

        # Adds the collection data
    def add_collection(self, name, object, key):
        objects = self.collections.get(name)
        if not objects:
            objects = []
            self.collections[name] = objects

        keys = self.collection_keys.get(name)
        if not keys:
            keys = []
            self.collection_keys[name] = keys

        if not object[key] in self.collection_keys[name]:
            objects.append(object)
            self.collection_keys[name].append(object[key])

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

        keys = self.collection_keys.get(name)
        if not keys:
            keys = []
            self.edge_keys[name] = keys

        key = '#'.join(str(x) for x in object.values())
        if not key in self.edge_keys[name]:
            object['report'] = self.report['_key']
            object['source'] = context().args.source
            object['active'] = True
            object['timestamp'] = self.report['timestamp']
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
        envelope = self.create_source_report_object()
        envelope[name] = data
        filename = os.path.join(dir_path, '%s.json' % str(uuid.uuid4())[0:8])
        with open(filename, 'w') as outfile:
            json.dump(envelope, outfile)
        return filename

    def _send(self, name, importer):
        dir_path = os.path.join(self.export_data_dir, name)
        for _, _, files in os.walk(dir_path):
            for data_file in files:
                with open(os.path.join(dir_path, data_file), 'r') as outfile:
                    importer.send_data_from_file(name, outfile)
        self._delete_export_data_dir(dir_path)

    def printData(self):
        context().logger.debug("Vertexes to be created:")
        context().logger.debug(self.collections)
        context().logger.debug("Edges to be created:")
        context().logger.debug(self.edges)
