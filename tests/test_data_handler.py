import unittest
from unittest.mock import patch
from pytest import raises

from car_framework.data_handler import BaseDataHandler
from tests.common_validate import JsonResponse, context_patch

class TestDataHandler(unittest.TestCase):
    """Car Service Unit test cases"""


    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_valid_collection_data(mocked_send_get):
        context_patch()
        mock_response = JsonResponse(200, 'import_schema_v2.json')
        mocked_send_get.return_value = mock_response
        
        asset = {
            "external_id": "10000000-d27a-4398-9869-000000000000",
            "name": "Asset Name",
            "operating_systems": "Cisco IOS XE 3.15.0S"
        }
        ipaddress = {
            '_key': '10.0.0.1'
        }
        macaddress = {
            '_key': '01:01:01:01:01:01'
        }
        hostname = {
            '_key': 'Host Name',
            'external_id': 'External ID'
        }

        data_handler = BaseDataHandler()
        data_handler.add_collection('asset', asset, 'external_id')
        data_handler.add_collection('ipaddress', ipaddress, '_key')
        data_handler.add_collection('macaddress', macaddress, '_key')
        data_handler.add_collection('hostname', hostname, '_key')

        assert data_handler.collections['asset'][0] == asset
        assert data_handler.collections['ipaddress'][0] == ipaddress
        assert data_handler.collections['macaddress'][0] == macaddress
        assert data_handler.collections['hostname'][0] == hostname

    @staticmethod
    @patch('car_framework.communicator.Communicator.get')
    def test_not_valid_collection_data(mocked_send_get):
        context_patch()
        mock_response = JsonResponse(200, 'import_schema_v2.json')
        mocked_send_get.return_value = mock_response
        
        asset = {
            'external_id': None,
            'name': None
        }
        ipaddress = {
            '_key': 's10.0.0.1'
        }
        macaddress = {
            '_key': '0g:01:01:01:01:01'
        }
        hostname = {
            '_key': None,
        }
        hostname2 = {
            '_key': 'External & ID',
        }

        data_handler = BaseDataHandler()
        
        # data_handler.add_collection('asset', {}, 'external_id')
        data_handler.add_collection('asset', asset, 'external_id')
        data_handler.add_collection('ipaddress', ipaddress, '_key')
        data_handler.add_collection('macaddress', macaddress, '_key')
        data_handler.add_collection('hostname', hostname, '_key')
        data_handler.add_collection('hostname', hostname2, '_key')

        assert 'asset' not in data_handler.collections
        assert 'ipaddress' not in data_handler.collections
        assert 'macaddress' not in data_handler.collections
        assert 'hostname' not in data_handler.collections
