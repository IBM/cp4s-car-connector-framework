from enum import Enum
from jwcrypto import jwk, jwe
from pathlib import Path
import json
import os
from os import listdir
from os.path import isfile, join

BATCH_SIZE = 20
SECRET_FILE_PATH = "/etc/secrets"
deprecate_msg_printed = {}


def deprecate(func):
    fn_name = '%s.%s' % (func.__module__, func.__name__)
    def inner(*args, **kwargs):
        global depricate_msg_printed
        if not deprecate_msg_printed.get(fn_name):
            from car_framework.context import context
            context().logger.warning('%s function is deprecated and will be removed in upcoming versions. Consider rewriting the request without using %s' % (fn_name, func.__name__))
            deprecate_msg_printed[fn_name] = True
        return func(*args, **kwargs)
    return inner


def recoverable_failure_status_code(status_code):
    return status_code in (302, 400, 401, 403, 408, 500, 503, 504)


def check_for_error(status):
    if status.status != ImportJobStatus.FAILURE: return
    if recoverable_failure_status_code(status.status_code):
        raise RecoverableFailure('Import job failure. Status code: %d, Error: %s' % (status.status_code, status.error))
    else:
        raise UnrecoverableFailure('Import job failure. Status code: %d, Error: %s' % (status.status_code, status.error))


def get_json(response):
    try: return response.json()
    except: return {}

class ErrorCode(Enum):
    # https://komodor.com/learn/exit-codes-in-containers-and-kubernetes-the-complete-guide/
    ## kubectl preserved
    # Exit Code 0
    # Exit Code 1: Application Error
    # Exit Code 125
    # Exit Code 126: Command Invoke Error
    # Exit Code 127: File or Directory Not Found
    # Exit Code 128: Invalid Argument Used on Exit
    # Exit Code 134: Abnormal Termination (SIGABRT)
    # Exit Code 137: Immediate Termination (SIGKILL)
    # Exit Code 139: Segmentation Fault (SIGSEGV)
    # Exit Code 143: Graceful Termination (SIGTERM)
    # Exit Code 255: Exit Status Out Of Range

    # If the Exit Code is 0 – the container exited normally, no troubleshooting is required
    # If the Exit Code is between 1-128 – the container terminated due to an internal error, such as a missing or invalid command in the image specification
    # If the Exit Code is between 129-255 – the container was stopped as the result of an operating signal, such as SIGKILL or SIGINT
    # If the Exit Code was exit(-1) or another value outside the 0-255 range, kubectl translates it to a value within the 0-255 range.

    GENERAL_APPLICATION_FAILURE = 1 # Unknown
    CONNECTOR_RUNTIME_INVALID_PARAMETER = 2 # python command argumens problem 
    RECOVERABLE_DEFAULT_FAILURE = 10 # RecoverableFailure exception default code
    # RECOVERABLE_DATABASE_FAILURE = 11 # Database is not ready
    # RECOVERABLE_UPDATE_COLLECTION_FAILURE = 12 # Error occurred while pathcing collection
    # RECOVERABLE_UPDATE_EDGE_FAILURE = 13 # Error occurred while updating edge
    # RECOVERABLE_IMPORT_JOB_FAILURE = 14 # Import job failure
    UNRECOVERABLE_FAILURE_DEFAULT = 20 # UnrecoverableFailure exception default code
    DATASOURCE_FAILURE_DEFAULT = 50 # Unknown
    DATASOURCE_FAILURE_CONNECT = 51 # Service unavailable
    DATASOURCE_FAILURE_AUTH = 52 # Authentication fail
    DATASOURCE_FAILURE_FORBIDDEN = 53 # Forbidden
    DATASOURCE_FAILURE_INVALID_PARAMETER = 54 # Invalid parameter
    DATASOURCE_FAILURE_DATA_PROCESS = 55 # Error while processing received data

class BaseConnectorFailure(Exception):
    def __init__(self, message, code: int):
        from car_framework.context import context
        context().logger.error(message)
        self.message = message
        self.code = code

class RecoverableFailure(BaseConnectorFailure):
    def __init__(self, message, code=ErrorCode.RECOVERABLE_DEFAULT_FAILURE.value):
        super().__init__(message, code)

class UnrecoverableFailure(BaseConnectorFailure):
    def __init__(self, message, code=ErrorCode.UNRECOVERABLE_FAILURE_DEFAULT.value):
        super().__init__(message, code)

class IncrementalImportNotPossible(Exception):
    callback = None
    def __init__(self, message):
        from car_framework.context import context
        context().logger.info(message)
        self.message = message

class DatasourceFailure(BaseConnectorFailure):
    def __init__(self, message, code=ErrorCode.DATASOURCE_FAILURE_DEFAULT.value):
        super().__init__(message, code)


class ImportJobStatus(object):

    FAILURE = 0
    IN_PROGRESS = 1
    SUCCESS = 2

    def __init__(self):
        self.status = ImportJobStatus.FAILURE
        self.status_code = 0
        self.error = 'Unknown'

def _get_conf() -> str:
    conf_path = Path(SECRET_FILE_PATH)
    if not conf_path.exists():
        return False

    conf_encrypted = {}
    for file in os.listdir(SECRET_FILE_PATH):
        if file != ".jwk":
            with Path(os.path.join(SECRET_FILE_PATH, file)).open() as fp:
                encrypted_var = fp.read()
                conf_encrypted[file] = encrypted_var
    return conf_encrypted


def _get_key_text() -> str:
    # key.jwk is in a random UUID dir
    jwk_path = Path("/etc/secrets/.jwk/key.jwk")
    with jwk_path.open() as fp:
        key_text = fp.read()
    return key_text


def decrypt_secrets() -> dict:
    from car_framework.context import context
    try:
        conf_encrypted = _get_conf()
        if not conf_encrypted:
            return False
        key_text = _get_key_text()
        key = jwk.JWK.from_json(key_text)
        conf_decrypted = {}
        for file in conf_encrypted:
            jwe_obj = jwe.JWE.from_jose_token(conf_encrypted[file])
            jwe_obj.decrypt(key)
            conf_decrypted[file] = jwe_obj.plaintext.decode("utf-8")

        return conf_decrypted

    except Exception:
        from car_framework.context import context
        context().logger.exception("Error extracting secrets")
        return {}

class objectview(object):
    def __init__(self, d):
        self.__dict__ = d