from car_framework.base_import import BaseImport
from car_framework.context import context


class BaseFullImport(BaseImport):
    def __init__(self):
        super().__init__()


    def import_vertices(self):
        raise NotImplementedError()


    def import_edges(self):
        raise NotImplementedError()


    def get_new_model_state_id(self):
        raise NotImplementedError()


    def init(self):
        context().car_service.create_source_if_needed()
        context().car_service.prepare_full_import(context().report_time)
        self.new_model_state_id = self.get_new_model_state_id()


    def complete(self):
        context().car_service.complete_full_import()
        self.save_new_model_state_id(self.new_model_state_id)
        context().logger.info('Done.')


    def run(self):
        self.init()
        self.import_vertices()
        self.import_edges()
        self.complete()
