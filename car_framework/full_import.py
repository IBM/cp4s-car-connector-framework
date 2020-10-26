from car_framework.car_service import CarDbStatus
from car_framework.base_import import BaseImport
from car_framework.util import RecoverableFailure, check_for_error
from car_framework.context import context


class BaseFullImport(BaseImport):
    def __init__(self):
        super().__init__()


    def import_vertices(self):
        raise NotImplementedError()


    def import_edges(self):
        raise NotImplementedError()


    def create_source_report_object(self):
        raise NotImplementedError()


    def get_new_model_state_id(self):
        raise NotImplementedError()


    def init(self):
        db_status = context().car_service.get_db_status()
        if db_status == CarDbStatus.FAILURE:
            raise RecoverableFailure('Database is not ready.')

        source_report_data = self.create_source_report_object()
        status = context().car_service.import_data(source_report_data)
        check_for_error(status)

        self.statuses.append(status)
        self.wait_for_completion_of_import_jobs()
        context().car_service.enter_full_import_in_progress_state()
        self.new_model_state_id = self.get_new_model_state_id()


    def complete(self):
        context().car_service.exit_full_import_in_progress_state()
        self.save_new_model_state_id(self.new_model_state_id)
        context().logger.info('Done.')


    def run(self):
        self.init()
        self.import_vertices()
        self.wait_for_completion_of_import_jobs()
        self.import_edges()
        self.wait_for_completion_of_import_jobs()
        self.complete()
