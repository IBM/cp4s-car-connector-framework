from car_framework.util import check_for_error, BATCH_SIZE
from car_framework.context import context


class BaseImport(object):

    def __init__(self):
        self.statuses = []

    def send_mutation(self, mutation):
        status = context().car_service.send_mutation(mutation)
        check_for_error(status)

    def get_last_model_state_id(self):
        return context().car_service.get_model_state_id()

    def save_new_model_state_id(self, new_model_state_id):
        return context().car_service.save_model_state_id(new_model_state_id)
