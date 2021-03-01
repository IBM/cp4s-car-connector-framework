from car_framework.util import check_for_error, BATCH_SIZE
from car_framework.context import context


class BaseImport(object):

    def __init__(self):
        self.statuses = []

    def create_source_report_object(self):
        raise NotImplementedError()

    def wait_for_completion_of_import_jobs(self):
        context().car_service.check_import_status(self.statuses)
        for status in self.statuses:
            check_for_error(status)
        self.statuses = []

    def send_data(self, name, data):
        envelope = self.create_source_report_object()
        envelope[name] = data
        status = context().car_service.import_data(envelope)
        check_for_error(status)
        self.statuses.append(status)
        if len(self.statuses) == BATCH_SIZE:
            self.wait_for_completion_of_import_jobs()

    def send_data_from_file(self, name, data_file):
        status = context().car_service.import_data_from_file(data_file)
        check_for_error(status)
        self.statuses.append(status)
        if len(self.statuses) == BATCH_SIZE:
            self.wait_for_completion_of_import_jobs()

    def get_last_model_state_id(self):
        return context().car_service.get_model_state_id()

    def save_new_model_state_id(self, new_model_state_id):
        return context().car_service.save_model_state_id(new_model_state_id)
