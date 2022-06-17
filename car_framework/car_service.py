from cmath import log
import json, urllib
from enum import Enum
from car_framework.util import check_status_code, get, get_json, deprecate, recoverable_failure_status_code, RecoverableFailure, UnrecoverableFailure
from car_framework.context import context
import time

CAR_SCHEMA = '/carSchema'
GRAPH_QL = '/query'

MODEL_STATE_ID = 'model_state_id'
max_wait_time = 60


def graphql_list(items):
    return ', '.join( map(lambda item: graphql_arg_value(item), items ))

def graphql_arg_value(value):
    if type(value) == int or type(value) == float: return f'{value}'
    if isinstance(value, list): return '[%s]' % graphql_list(value)
    return '"%s"' % str(value)

def graphql_arg(key, value):
    return '%s: %s' % (key, graphql_arg_value(value))

def graphql_args(kwargs):
    return ', '.join( map(lambda item: graphql_arg(item[0], item[1]), kwargs.items()) )


class CarService(object):

    def __init__(self, communicator):
        self.communicator = communicator


    def create_source_if_needed(self):
        source = context().args.source
        res = self.query_graphql('''
            {
                source(where: {id: {_eq: "%s"}}) { id }
            }''' % (source))
        res = get(res, 'data.source')
        if len(res) > 0: return

        res = self.query_graphql('''
            mutation {
                insert_source(objects: {id: "%s", name: "%s"}) {
                    affected_rows
                }
            }''' % (source, source))

        affected_rows = get(res, 'data.insert_source.affected_rows')
        if affected_rows == 1: return
        raise Exception('Failed to create the "source" object: %s' % json.dumps(res))


    def get_model_state_id(self):
        res = self.query_graphql('''
            {
                source(where: {id: {_eq: "%s"}}) { properties }
            }''' % (context().args.source))
        properties = get(res, 'data.source')
        if len(properties) != 1: return None
        properties = properties[0].get('properties')
        if not properties: return None
        properties = json.loads(properties)
        return properties.get(MODEL_STATE_ID)


    def save_model_state_id(self, new_model_state_id):
        self.query_graphql(r'''
            mutation {
                update_source(where: {id: {_eq: "%s"}}, _set: {properties: "{\"%s\":\"%s\"}"}) {
                    affected_rows
                }
            }''' % (context().args.source, MODEL_STATE_ID, new_model_state_id))


    def reset_model_state_id(self):
        self.save_model_state_id('')


    def send_mutation(self, mutation):
        return self._query_graphql(mutation.serialize())


    def delete_vertices(self, collection, ids):
        self._async_action('soft_delete_vertices', collection=collection, ids=ids)


    def search_collection(self, resource, attribute, search_id, fields):
        query= "{ %s(where: {%s: {_eq: \"%s\"}}) {  %s  }}" % (resource, attribute, search_id, ','.join(fields))
        result = self.query_graphql(query)
        if result:
            return result["data"]
        else:  
            return None


    def query_graphql(self, query):
        return self._query_graphql({'query': query})


    def _query_graphql(self, data):
        r = self.communicator.post(GRAPH_QL, data=json.dumps(data))
        check_status_code(r.status_code, 'Accessing CAR Graphql query API')
        return get_json(r)


    def prepare_full_import(self, report_time):
        self._async_action('prepare_full_import', source=context().args.source, report_time=report_time)


    def complete_full_import(self):
        self._async_action('complete_full_import', source=context().args.source)


    def prepare_incremental_import(self, report_time):
        self._async_action('prepare_incremental_import', source=context().args.source, report_time=report_time)


    def complete_incremental_import(self):
        self._async_action('complete_incremental_import', source=context().args.source)


    def compose_paginated_list(self, ids):
        output = {}
        page = 1
        limit = 1800
        length = 0
        for id in ids:
            id = str(id)
            length += len(id)
            if (length > (limit * page)):
                page += 1

            if not output.get(page):
                output[page] = []
            output[page].append(id)

        return output


    def get_extension(self, key):
        endpoint = '%s/%s' % (CAR_SCHEMA, key)
        r = self.communicator.get(endpoint)
        if r.status_code == 200:
            return get_json(r)
        if r.status_code == 404:
            return None
        raise Exception('Error when getting schema extension: %d' % r.status_code)


    def setup_extension(self, extension):
        data = {
            'key': extension.key,
            'owner': extension.owner,
            'version': extension.version,
            'schema': json.loads(extension.schema)
        }
        r = self.communicator.post(CAR_SCHEMA, data=json.dumps(data))
        if r.status_code not in (200, 201):
            raise Exception('Error when posting schema extension: %d' % r.status_code)


    def limit_edges_to_report(self, source, vertex_collection, edge_collections, ids, report_time):
        self._async_action('limit_edges_to_report', source=source, collection=vertex_collection, edge_collections=edge_collections, vertex_ids=ids, report_time=report_time)


    def _async_action_wait(self, action, async_job_id):
        while True:
            time.sleep(2)
            res = self.query_graphql('''
                query MyQuery {
                    %s(id: "%s") {
                        errors
                        output {
                        error
                        }
                      }
                    }''' % (action, async_job_id))

            res = get(res, 'data.' + action)
            if res.get('errors') != None:
                raise UnrecoverableFailure('Error: ' + str(res.get('errors')))
            res = res.get('output')
            if res == None: continue
            if res.get('error') != None:
                raise UnrecoverableFailure('Error: ' + str(res.get('error')))
            break


    def _async_action(self, action_name, **kwargs):
        res = self.query_graphql('''
            mutation {
                %s(%s)
            }''' % (action_name, graphql_args(kwargs)))
        if res.get('errors'):
            raise UnrecoverableFailure('Failed operation: "%s". Error: %s' % (action_name, str(res.get('errors'))))
        data = res['data']
        error = data.get('error')
        if error:
            raise UnrecoverableFailure('Failed operation: "%s". Error: %s' % (action_name, error))
        async_job_id = data.get(action_name)
        if not async_job_id:
            raise UnrecoverableFailure('Async job ID is not found for operation: "%s"' % action_name)
        self._async_action_wait(action_name, async_job_id)
