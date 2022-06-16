from car_framework.base_import import BaseImport
from car_framework.context import context
from car_framework.util import IncrementalImportNotPossible


class BaseIncrementalImport(BaseImport):
    def __init__(self):
        super().__init__()
        self.updated_vertices = {}


    def get_new_model_state_id(self):
        raise NotImplementedError()


    def get_data_for_delta(self, last_model_state_id, new_model_state_id):
        raise NotImplementedError()


    def import_vertices(self):
        raise NotImplementedError()


    def import_edges(self):
        raise NotImplementedError()


    def delete_vertices(self):
        raise NotImplementedError()


    def get_owned_edges(collection):
        raise NotImplementedError()


    def add_updated_vertex(self, collection, id):
        ids = self.updated_vertices.get(collection)
        if ids == None:
            ids = []
            self.updated_vertices[collection] = ids
        ids.append(id)


    def limit_edges_of_updated_vertices_to_current_report(self):
        for collection in self.updated_vertices.keys():
            edge_collections = self.get_owned_edges(collection)
            if edge_collections:
                context().car_service.limit_edges_to_report(context().args.source, collection, edge_collections, self.updated_vertices[collection], context().report_time)


    def run(self):
        context().car_service.create_source_if_needed()
        last_model_state_id = self.get_last_model_state_id()
        if not last_model_state_id:
            raise IncrementalImportNotPossible('"Last known model state" is not available.')

        new_model_state_id = self.get_new_model_state_id()
        if not new_model_state_id:
            raise IncrementalImportNotPossible('Current model state is not available.')

        if last_model_state_id == new_model_state_id:
            context().logger.info('The source model has not changed.')
            return

        context().car_service.prepare_incremental_import(context().report_time)
        self.get_data_for_delta(last_model_state_id, new_model_state_id)
        self.import_vertices()
        self.import_edges()
        self.limit_edges_of_updated_vertices_to_current_report()
        self.delete_vertices()
        context().car_service.complete_incremental_import()

        self.save_new_model_state_id(new_model_state_id)
