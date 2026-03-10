import logging
from pythonjsonlogger import json as jsonlogger
from datetime import datetime, timezone

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        if log_record is None:
            log_record = {}

        super().add_fields(log_record, record, message_dict)

        if not log_record.get('ibm_datetime'):
            log_record['ibm_datetime'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        args = context().args if context() else None

        if args:
            if not log_record.get('connector') and getattr(args, "CONNECTOR_NAME", None):
                log_record['connector'] = args.CONNECTOR_NAME

            if not log_record.get('source') and getattr(args, "CONNECTION_NAME", None):
                log_record['source'] = args.CONNECTION_NAME

            if not log_record.get('version') and getattr(args, "CONNECTOR_VERSION", None):
                log_record['version'] = args.CONNECTOR_VERSION

        # safe assignment
        log_record['level'] = (log_record.get('level') or record.levelname or "").lower()
        log_record['message'] = log_record.get('message') or record.getMessage()
        log_record['label'] = log_record.get('label') or record.name

def create_logger(debug = False):
    logger = logging.getLogger()
    logger.setLevel(debug and logging.DEBUG or logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(debug and logging.DEBUG or logging.INFO)
    format_string = '%(ibm_datetime)s %(level)s %(label)s %(message)s'
    formatter = CustomJsonFormatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def read_config(file_path, args):
    import json 

    try:
        with open(file_path) as f:
            config_file = json.load(f)
            args.CONNECTOR_NAME = config_file.get('connection', {}).get('type', {}).get('displayName', {})
    except Exception:
        args.CONNECTOR_NAME = ""


class Context(object):
    def __init__(self, args):
        global global_context
        global_context = self

        from car_framework.car_service import CarService
        from car_framework.communicator import Communicator
        self.args = args
        if not args.CONNECTOR_NAME:
            read_config('configurations/config.json', self.args)
        self.logger = create_logger(args.debug)
        self.car_service = CarService(Communicator())
        

global_context = None
def context():
    return global_context
