import argparse, traceback, sys

from car_framework.context import Context, context
from car_framework.util import IncrementalImportNotPossible, RecoverableFailure, UnrecoverableFailure


class BaseApp(object):
    def __init__(self, description):
        self.parser = argparse.ArgumentParser(description=description)
        self.parser.add_argument('-car-service-url', dest='car_service', type=str, required=True, help='URL of the CAR ingestion service')
        self.parser.add_argument('-car-service-key', dest='api_key', type=str, required=True, help='API key for CAR ingestion service')
        self.parser.add_argument('-car-service-password', dest='api_password', type=str, required=True, help='Password for CAR ingestion service')

        # source id to uniquely identify each data source
        self.parser.add_argument('-source', dest='source', type=str, required=True, help='Unique source id for the data source')

        self.parser.add_argument('-d', dest='debug', action='store_true', help='Enables DEBUG level logging')


    def setup(self):
        args = self.parser.parse_args()
        Context(args)


    def run(self):
        try:
            try:
                context().logger.info('Attempting incremental import...')
                context().inc_importer.run()
            except IncrementalImportNotPossible as e:
                context().logger.info('Attempting full import...')
                context().full_importer.run()

            context().logger.info('Done.')

        except RecoverableFailure as e:
            context().logger.info('Recoverable failure: ' + e.message)
            context().logger.info('Incremental import will be attempted again in the nex run.')
            sys.exit(1)
        except UnrecoverableFailure as e:
            context().logger.info('Unrecoverable failure: ' + e.message)
            context().logger.info('Incremental import will not be possible in the nex run.')
            context().car_service.reset_model_state_id()
            sys.exit(1)
        except Exception as e:
            context().logger.exception(e)
            context().logger.error(traceback.format_exc())
            traceback.print_exc()
            sys.exit(1)
