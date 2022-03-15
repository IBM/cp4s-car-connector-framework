"""Unit test cases for Car Service"""

import os
import json
from os.path import join
import unittest
from unittest.mock import patch
from car_framework.communicator import Communicator
from car_framework.car_service import CarService, CarDbStatus
from car_framework.util import RecoverableFailure, UnrecoverableFailure
from tests.common_validate import context, context_patch, JsonResponse, MockJsonResponse


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
LOGGER = ""
SOURCE = 'AWS-CAR-demo'
UPDATES_DIR = os.path.dirname(os.path.realpath(__file__))


class TestCarService(unittest.TestCase):
    """Car Service Unit test cases"""

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_get_model_state_id(mocked_send_get):
        """Unit test for getting model state id"""
        context_patch()
        model_state_id = """{
                      "model_state_id": "1580649320000"
                    }"""
        mocked_send_get.return_value = MockJsonResponse(200, model_state_id)
        status = context().car_service.get_model_state_id()
        assert status == json.loads(model_state_id)['model_state_id']

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_db_status_ready(mocked_send_get):
        """Unit test for database status is ready"""
        context_patch()
        mock_response = JsonResponse(200, 'database_is_ready.json')
        mocked_send_get.return_value = mock_response
        status = context().car_service.get_db_status()
        assert status == CarDbStatus.READY

    @staticmethod
    @patch('car_framework.communicator.Communicator.post')
    @patch('car_framework.communicator.Communicator.get')
    @patch('car_framework.car_service.CarService.wait_until_done')
    def test_db_create_database(mocked_wait, mocked_send_get, mocked_send_post):
        """Unit test for create new database if not exist"""
        context_patch()
        mocked_send_get.return_value = JsonResponse(400, 'database_not_found.json')
        job_id = """{
                      "job_id": "84cb53ee-58a2-4d49-b0c3-ad4370008841-ACCT_722724471"
                    }"""
        mocked_send_post.return_value = MockJsonResponse(200, job_id)
        mocked_wait.return_value = CarDbStatus.READY
        status = context().car_service.get_db_status()
        assert status == CarDbStatus.NEWLY_CREATED

    @staticmethod
    @patch('car_framework.communicator.Communicator.patch')
    @patch('car_framework.communicator.Communicator.get')
    def test_db_status_failed(mocked_send_get, mocked_send_patch):
        """Unit test for database status check failed"""
        context_patch()
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
        assert status == CarDbStatus.FAILURE

    @patch('car_framework.communicator.Communicator.delete')
    def test_delete_data_failed(self, mocked_send_delete):
        """Unit test for delete data error"""
        context_patch()
        external_ids = ["7594a7860caaf0bdb5a3b68c341773bf004e3e14"]
        mocked_send_delete.return_value = JsonResponse(400, 'data_import_error_response.json')
        
        with self.assertRaises(Exception) as error:
            context().car_service.delete('asset', external_ids)

        self.assertIsInstance(error.exception, RecoverableFailure)

    @staticmethod
    @patch('car_framework.communicator.Communicator.post')
    @patch('car_framework.car_service.CarService.wait_until_done')
    def test_enter_full_import_in_progress(mocked_wait, mocked_send_post):
        """Unit test for full import ready check"""
        context_patch()
        job_id = """{
                    "job_id": "84cb53ee-58a2-4d49-b0c3-ad4370008841-ACCT_722724471"
                    }"""
        mocked_send_post.return_value = MockJsonResponse(200, job_id)
        mocked_wait.return_value = CarDbStatus.READY
        full_import_status = context().car_service.enter_full_import_in_progress_state()
        assert full_import_status is 200

    @staticmethod
    @patch('car_framework.communicator.Communicator.patch')
    def test_edge_patch(mock_patch_request):
        """Unit test for edge disable"""
        context_patch()
        job_id = """{
                        "job_id": "84cb53ee-58a2-4d49-b0c3-ad4370008841-ACCT_722724471"
                    }"""
        mock_patch_request.return_value = MockJsonResponse(200, job_id)
        edge_dict = {
            'from': 'aws/124',
            'to': 'sample_user',
            'edge_type': 'database_user'}
        status = context().car_service.edge_patch('aws', edge_dict, {"active": False})
        assert status['job_id'] == json.loads(job_id)['job_id']

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_graph_attribute_search(mock_get_request):
        """Unit test cases for attribute search"""
        context_patch()
        mock_get_request.return_value = JsonResponse(200, 'attribute_search.json')
        app_name = 'application-ebs-test'
        status = context().car_service.graph_attribute_search('application', 'name', app_name)
        assert status is not None
        assert status[0]['name'] == app_name

    @staticmethod
    @patch('car_framework.communicator.Communicator.patch')
    def test_node_patch_value(mock_patch_request):
        """Unit test cases for patch value"""
        context_patch()
        response = """{
            "success": "True",
            "message": "Node/s has been updated successfully"
        }"""
        mock_patch_request.return_value = MockJsonResponse(200, response)
        tag1 = {'resource_id': 'db-SW7U4PNNHP5K4FSQ7SVHYOJH6E',
               'resource_type': 'database',
               'name': 'database-new'}
        tag2 = {'resource_id': 'db-SW7U4PNNHP5K4FSQ7SVHYOJH6E',
                'resource_type': 'database',
                'pending_update': 'active'}
        status1 = context().car_service.database_patch_value(tag1)
        status2 = context().car_service.database_patch_value(tag2)
        assert status1['success'] == 'True'
        assert status2['success'] == 'True'

    @patch('car_framework.communicator.Communicator.get')
    def test_attribute_search_recoverable_exception(self, mocked_send_get):
        """Unit test for attribute search exception"""
        context_patch()

        response = {}
        mocked_send_get.return_value = MockJsonResponse(403, response)

        results = context().car_service.graph_attribute_search('application', 'name', 'app_name-ebs')

        assert len(results['result']) == 0
        assert len(results['related']) == 0

    
    @patch('car_framework.communicator.Communicator.get')
    def test_attribute_search_unrecoverable_exception(self, mocked_send_get):
        """Unit test for attribute search exception"""
        context_patch()

        response = {}
        mocked_send_get.return_value = MockJsonResponse(502, response)

        results = context().car_service.graph_attribute_search('application', 'name', 'app_name-ebs')

        assert len(results['result']) == 0
        assert len(results['related']) == 0
        

    # @patch('car_framework.communicator.Communicator.patch')
    # def test_node_patch_exception(self, mock_log_details):
    #     """ Unit test for attribute search exception"""
    #     mock_log_details.side_effect = Exception({
    #         "errors": [{
    #             "code": "unexpected_error",
    #             "message": "AQL: backend unavailable, cluster node: 'PRMR-l7wgvwkt', endpoint: "
    #                        "'ssl://arangodb-dbserver-l7wgvwkt.arangodb-int.default.svc:8529', error: 'service "
    #                        "unavailable' ( ""while executing) "}],
    #         "trace": "af00971c-4cc8-47e6-83c9-b57ee562bdab"
    #     })
    #     tag = {'resource_id': 'db-SW7U4PNNHP5K4FSQ7SVHYOJH6E',
    #            'resource_type': 'database',
    #            'name': 'database-new'}
    #     context_patch()
    #     with self.assertRaises(Exception) as error:
    #         context().car_service.node_patch_value(tag)
    #     the_exception = error.exception
    #     with self.assertRaises(Exception) as error:
    #         context().car_service.database_patch_value(tag)
    #     the_exception_next = error.exception
    #     assert the_exception.args[0]['status'] == 'FAILURE'
    #     assert the_exception_next.args[0]['status'] == 'FAILURE'
