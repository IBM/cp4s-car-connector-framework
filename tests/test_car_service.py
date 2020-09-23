"""Unit test cases for Car Service"""

import os
from os.path import join
import unittest
from unittest.mock import patch
from car_framework.communicator import Communicator
from car_framework.car_service import CarService
from tests.common_validate import context, context_patch, JsonResponse, MockJsonResponse


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
LOGGER = ""
SOURCE = 'AWS-CAR-demo'
UPDATES_DIR = os.path.dirname(os.path.realpath(__file__))
DB_FAILURE = 0
DB_READY = 1
DB_NEW = 2


class TestCarService(unittest.TestCase):
    """Car Service Unit test cases"""

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_db_status_ready(mocked_send_request):
        """Unit test for database status is ready"""
        mock_response = JsonResponse(200, 'database_is_ready.json')
        mocked_send_request.return_value = mock_response
        status = context().car_service.get_db_status()
        assert status == DB_READY

    @staticmethod
    @patch('car_framework.communicator.Communicator.post')
    @patch('car_framework.communicator.Communicator.get')
    @patch('car_framework.car_service.CarService.wait_until_done')
    def test_db_create_database(mocked_wait, mocked_send_get, mocked_send_post):
        """Unit test for create new database if not exist"""
        mocked_send_get.return_value = JsonResponse(400, 'database_not_found.json')
        job_id = """{
                      "job_id": "84cb53ee-58a2-4d49-b0c3-ad4370008841-ACCT_722724471"
                    }"""
        mocked_send_post.return_value = MockJsonResponse(200, job_id)
        mocked_wait.return_value = 'COMPLETE'
        status = context().car_service.get_db_status()
        assert status == DB_NEW

    @staticmethod
    @patch('car_framework.communicator.Communicator.patch')
    @patch('car_framework.car_service.CarService.wait_until_done')
    @patch('car_framework.communicator.Communicator.get')
    def test_db_status_success(mocked_send_get, mocked_wait, mocked_send_patch):
        """Unit test for database status check success"""
        mocked_send_get.return_value = JsonResponse(200, 'database_missing indexes.json')
        job_id = """{
                      "job_id": "84cb53ee-58a2-4d49-b0c3-ad4370008841-ACCT_722724471"
                    }"""
        mocked_send_patch.return_value = MockJsonResponse(200, job_id)
        mocked_wait.return_value = 'COMPLETE'
        status = context().car_service.get_db_status()
        assert status == DB_READY

    @staticmethod
    @patch('car_framework.communicator.Communicator.patch')
    @patch('car_framework.communicator.Communicator.get')
    def test_db_status_failed(mocked_send_get, mocked_send_patch):
        """Unit test for database status check failed"""
        db_failure = """{"status":"ERROR"}"""
        db_response = """{
                        "databases": [{
                                "name": "assets-ACCT_722724471","graph_name": "","missing_collections": [],
                                "collections_without_indexes": [],"collections": [],"is_ready": false
                            }]
                    }"""
        job_id = """{
                      "job_id": "84cb53ee-58a2-4d49-b0c3-ad4370008841-ACCT_722724471"
                    }"""
        mocked_send_get.side_effect = [MockJsonResponse(200, db_response),
                                       MockJsonResponse(200, db_failure)]
        mocked_send_patch.return_value = MockJsonResponse(200, job_id)
        status = context().car_service.get_db_status()
        assert status == DB_FAILURE

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    @patch('car_framework.communicator.Communicator.post')
    def test_import_files_status(mocked_send_post, mocked_send_get):
        """Unit test for import file status check success"""
        file = ['aws_test_log/asset_host.json']
        mocked_send_post.return_value = JsonResponse(200, 'import_data_response.json')
        status_return = """{
                            "success":true,
                            "incomplete_imports":[],
                            "notfound_imports":[],
                            "error_imports":[]
                             }"""
        mocked_send_get.return_value = MockJsonResponse(200, status_return)
        status = context().car_service.import_files(files=file)
        assert status is not None
        assert status[0]['status'] == 'SUCCESS'
        assert status[0]['status_code'] == 200
        assert status[0]['file'] is not None

    @staticmethod
    @patch('car_framework.communicator.Communicator.post')
    def test_import_files_error(mocked_send_post):
        """Unit test for import file status check error"""
        file = ['aws_test_log/asset_host.json']
        mocked_send_post.return_value = JsonResponse(400, 'data_import_error_response.json')
        status = context().car_service.import_files(files=file)
        assert status is not None
        assert status[0]['status'] == 'FAILURE'
        assert status[0]['error'] is not None

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    @patch('car_framework.communicator.Communicator.post')
    def test_import_status_check_failure(mocked_send_post, mocked_send_get):
        """Unit test for import file status check failure"""
        file = ['aws_test_log/asset_host.json']

        bad_return = """{
                        "id": "7f13a1af-f6de-4c86-af76-e615b87cfd05-ACCT_722724471",
                        "status": "FAILED",
                        "message": "unable to import"
                        }"""
        mocked_send_post.return_value = MockJsonResponse(400, bad_return)
        status_return = """{
                               "success":true,
                               "incomplete_imports":[],
                               "notfound_imports":[],
                               "error_imports":[{"id":"7f13a1af-f6de-4c86-af76-e615b87cfd05-ACCT_722724471", 
                               "error":"data_mal_formed"}]
                                }"""
        mocked_send_get.return_value = MockJsonResponse(200, status_return)
        status = context().car_service.import_files(files=file)
        assert status is not None
        assert status[0]['status'] == 'FAILURE'

    @staticmethod
    @patch('car_framework.communicator.Communicator.send_delete_request')
    def test_delete_data_failed(mocked_send_delete):
        """Unit test for delete data error"""
        external_id = "7594a7860caaf0bdb5a3b68c341773bf004e3e14"
        mocked_send_delete.return_value = JsonResponse(400, 'data_import_error_response.json')
        delete = context().car_service.delete('asset', external_id)
        assert delete is not None
        assert delete['status'] == 'FAILURE'
        assert delete['error']['errors'][0]['code'] == 'data_mal_formed'

    @staticmethod
    @patch('car_framework.communicator.Communicator.post')
    def test_enter_full_import_in_progress(mocked_send_post):
        """Unit test for full import ready check"""
        import_status = """{
                "success":true,
                "message":"ready for full import"
                }"""
        mocked_send_post.return_value = MockJsonResponse(200, import_status)
        full_import_status = context().car_service.enter_full_import_in_progress_state()
        assert full_import_status is None

    @staticmethod
    @patch('car_framework.communicator.Communicator.patch')
    def test_edge_patch(mock_patch_request):
        """Unit test for edge disable"""
        job_id = """{
                              "job_id": "84cb53ee-58a2-4d49-b0c3-ad4370008841-ACCT_722724471"
                            }"""
        mock_patch_request.return_value = MockJsonResponse(200, job_id)
        edge_dict = {
            'from': 'aws/124',
            'to': 'sample_user',
            'edge_type': 'database_user'}
        status = context().car_service.edge_patch('aws', edge_dict, {"active": False})
        assert status['status'] == 'SUCCESS'
        assert status['status_code'] == 200
        assert status['resource_id'] is not None
        assert status is not None

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_graph_search(mock_get_request):
        """Unit test cases for graph search"""
        mock_get_request.return_value = JsonResponse(200, 'db_car_search.json')
        search_id = 'db-SW7U4PNNHP5K4FSQ7SVHYOJH6E'
        status = context().car_service.graph_search('database', search_id)
        assert status['result'] is not None
        assert (status['result']['external_id'][0]).__contains__(search_id)

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_graph_attribute_search(mock_get_request):
        """Unit test cases for attribute search"""
        mock_get_request.return_value = JsonResponse(200, 'attribute_search.json')
        app_name = 'application-ebs-test'
        status = context().car_service.graph_attribute_search('application', 'name', app_name)
        assert status is not None
        assert status[0]['name'] == app_name

    # @staticmethod
    # @patch('car_framework.communicator.Communicator.patch')
    # def test_node_patch_value(mock_patch_request):
    #     """Unit test cases for patch value"""
    #     response = """{
    #         "success": "True",
    #         "message": "Node/s has been updated successfully"
    #     }"""
    #     mock_patch_request.return_value = MockJsonResponse(200, response)
    #     tag = {'resource_id': 'db-SW7U4PNNHP5K4FSQ7SVHYOJH6E',
    #            'resource_type': 'database',
    #            'name': 'database-new'}
    #     tag1 = {'resource_id': 'db-SW7U4PNNHP5K4FSQ7SVHYOJH6E',
    #             'resource_type': 'database',
    #             'pending_update': 'active'}
    #     status = context().car_service.database_patch_value(tag)
    #     status1 = context().car_service.database_patch_value(tag1)
    #     status2 = context().car_service.node_patch_value(tag)
    #     assert status, status2 is not None
    #     assert status1 is not None
    #     assert status['status'] == 'SUCCESS'
    #     assert status['status_code'] == 200

    @staticmethod
    @patch('car_framework.communicator.Communicator.patch')
    def test_source_revision(mock_patch_request):
        """Unit test cases for incremental time run"""
        response = """{
            "success": "True",
            "message": "Node/s has been updated successfully"
        }"""
        mock_patch_request.return_value = MockJsonResponse(200, response)
        status = context().car_service.source_revision(context)
        assert status is not None
        assert status['status'] == 'SUCCESS'
        assert status['status_code'] == 200

    @patch('car_framework.communicator.Communicator.patch')
    def test_source_revision_exception(self, mock_log_details):
        """Unit test for source revision exception"""
        mock_log_details.side_effect = Exception({
            "httpCode": "404",
            "httpMessage": "Not Found",
            "moreInformation": "No resources match requested URI"
        })
        context_patch()
        with self.assertRaises(Exception) as error:
            context().car_service.source_revision(context)
        the_exception = error.exception
        assert the_exception.args[0]['status'] == 'FAILURE'

    @patch('car_framework.communicator.Communicator.get')
    def test_attribute_search_exception(self, mock_log_details):
        """Unit test for attribute search exception"""
        mock_log_details.side_effect = Exception({
            "httpCode": "405",
            "httpMessage": "Method Not Allowed",
            "moreInformation": "The method is not allowed for the requested URL"
        })
        context_patch()
        with self.assertRaises(Exception) as error:
            context().car_service.graph_attribute_search('application', 'name', 'app_name-ebs')
        the_exception = error.exception
        assert the_exception.args[0]['status'] == 'FAILURE'

    @patch('car_framework.communicator.Communicator.get')
    def test_search_exception(self, mock_log_details):
        """Unit test for graph search exception"""
        mock_log_details.side_effect = Exception({
            "errors": [{
                "code": "unexpected_error",
                "message": "AQL: backend unavailable, cluster node: 'PRMR-l7wgvwkt', endpoint: "
                           "'ssl://arangodb-dbserver-l7wgvwkt.arangodb-int.default.svc:8529', error: 'service "
                           "unavailable' ( ""while executing) "}],
            "trace": "af00971c-4cc8-47e6-83c9-b57ee562bdab"
        })
        context_patch()
        with self.assertRaises(Exception) as error:
            context().car_service.graph_search('application', 'app_name-ebs')
        the_exception = error.exception
        assert the_exception.args[0]['status'] == 'FAILURE'

    @patch('car_framework.communicator.Communicator.patch')
    def test_node_patch_exception(self, mock_log_details):
        """ Unit test for attribute search exception"""
        mock_log_details.side_effect = Exception({
            "errors": [{
                "code": "unexpected_error",
                "message": "AQL: backend unavailable, cluster node: 'PRMR-l7wgvwkt', endpoint: "
                           "'ssl://arangodb-dbserver-l7wgvwkt.arangodb-int.default.svc:8529', error: 'service "
                           "unavailable' ( ""while executing) "}],
            "trace": "af00971c-4cc8-47e6-83c9-b57ee562bdab"
        })
        tag = {'resource_id': 'db-SW7U4PNNHP5K4FSQ7SVHYOJH6E',
               'resource_type': 'database',
               'name': 'database-new'}
        context_patch()
        with self.assertRaises(Exception) as error:
            context().car_service.node_patch_value(tag)
        the_exception = error.exception
        with self.assertRaises(Exception) as error:
            context().car_service.database_patch_value(tag)
        the_exception_next = error.exception
        assert the_exception.args[0]['status'] == 'FAILURE'
        assert the_exception_next.args[0]['status'] == 'FAILURE'
