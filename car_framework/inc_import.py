from car_framework.base_import import BaseImport
from car_framework.context import context
from car_framework.util import IncrementalImportNotPossible, RecoverableFailure
from car_framework.car_service import CarDbStatus


class BaseIncrementalImport(BaseImport):
    def __init__(self):
        super().__init__()


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


    def run(self):
        db_status = context().car_service.get_db_status()
        if db_status == CarDbStatus.FAILURE:
            raise RecoverableFailure('Database is not ready.')
        if db_status == CarDbStatus.NEWLY_CREATED:
            raise IncrementalImportNotPossible('Newly created CAR database is detected.')

        last_model_state_id = self.get_last_model_state_id()
        if not last_model_state_id:
            raise IncrementalImportNotPossible('"Last known model state" is not available.')

        new_model_state_id = self.get_new_model_state_id()
        if not new_model_state_id:
            raise IncrementalImportNotPossible('Current model state is not available.')

        self.get_data_for_delta(last_model_state_id, new_model_state_id)
        self.import_vertices()
        self.wait_for_completion_of_import_jobs()
        self.import_edges()
        self.wait_for_completion_of_import_jobs()
        self.delete_vertices()

        self.save_new_model_state_id(new_model_state_id)
