from car_framework.util import DatasourceFailure

class BaseAssetServer:
    def test_connection(self):
        raise DatasourceFailure("AssetServer.test_connection not implemented")