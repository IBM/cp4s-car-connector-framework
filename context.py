import logging

def create_logger(debug = False):
    logger = logging.getLogger()
    logger.setLevel(debug and logging.DEBUG or logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(debug and logging.DEBUG or logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class Context(object):
    def __init__(self, args):
        global global_context
        global_context = self

        from car_framework.car_service import CarService
        from car_framework.communicator import Communicator
        self.args = args
        self.logger = create_logger(args.debug)
        self.car_service = CarService(Communicator())
        

global_context = None
def context():
    return global_context
