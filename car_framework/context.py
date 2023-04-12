import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        # use inherited constructor
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        if not log_record.get('ibm_datetime'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['ibm_datetime'] = now
        
        if not log_record.get('connector') and context().args.CONNECTOR_NAME:
            log_record['connector'] = context().args.CONNECTOR_NAME
        
        if not log_record.get('source') and context().args.CONNECTION_NAME:
            log_record['source'] = context().args.CONNECTION_NAME
        
        if not log_record.get('version') and context().args.CONNECTOR_VERSION:
            log_record['version'] = context().args.CONNECTOR_VERSION

        # assign values to log_record
        log_record['level'] = log_record['level'].lower() if log_record.get('level') else record.levelname
        log_record['message'] = log_record['message'] if log_record.get('log') else record.message
        log_record['label'] = log_record['label'] if log_record.get('type') else record.name

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
