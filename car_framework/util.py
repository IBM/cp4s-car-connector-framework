from enum import Enum


BATCH_SIZE = 20


def recoverable_failure_status_code(status_code):
    return status_code in (302, 400, 401, 403, 408, 500, 503, 504)


def check_for_error(status):
    if status.status != ImportJobStatus.FAILURE: return
    if recoverable_failure_status_code(status.status_code):
        raise RecoverableFailure('Import job failure. Status code: %d, Error: %s' % (status.status_code, status.error))
    else:
        raise UnrecoverableFailure('Import job failure. Status code: %d, Error: %s' % (status.status_code, status.error))


class RecoverableFailure(Exception):
    def __init__(self, message):
        from car_framework.context import context
        context().logger.error(message)
        self.message = message


class UnrecoverableFailure(Exception):
    def __init__(self, message):
        from car_framework.context import context
        context().logger.error(message)
        self.message = message


class IncrementalImportNotPossible(Exception):
    callback = None
    def __init__(self, message):
        from car_framework.context import context
        context().logger.info(message)
        self.message = message


def get_json(response):
    try: return response.json()
    except: return {}


class ImportJobStatus(object):

    FAILURE = 0
    IN_PROGRESS = 1
    SUCCESS = 2

    def __init__(self):
        self.status = ImportJobStatus.FAILURE
        self.status_code = 0
        self.error = 'Inknown'
