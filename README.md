# Car Connector Framework

## Develop a connector

Use connectors/reference_connector from [cp4s-car-connectors](https://github.com/IBM/cp4s-car-connectors) project as an example of how this framework is to be used.

A CAR connector project will need to extend the framework classes: [BaseFullImport](https://github.com/IBM/cp4s-car-connector-framework/blob/develop/car_framework/full_import.py), [BaseIncrementalImport](https://github.com/IBM/cp4s-car-connector-framework/blob/develop/car_framework/inc_import.py), [BaseApp](https://github.com/IBM/cp4s-car-connector-framework/blob/develop/car_framework/app.py), [BaseAssetServer](https://github.com/IBM/cp4s-car-connector-framework/blob/develop/car_framework/server_access.py) and [BaseDataHandler](https://github.com/IBM/cp4s-car-connector-framework/blob/develop/car_framework/data_handler.py), and implement abstract methods of those classes.

Things to note:

* All communications with CAR digestion microservice are managed by the framework. Connector code normally does not need to access CAR digestion microservice directly

* The framework is trying to make some intelligent choice for whether to run full vs incremental import. Normally, for performance reasons we would always prefer to run incremental import if one is possible. Some examples of when it is not possible are:
  * The model states for generating delta are not available
  * The model on the CAR side is empty
  * The previous incremental import session failed and a new incremental import session can potentially create a gap in the model data

* Because of the above the the connector code should properly use (throw/raise) one of three following exceptions when detecting failures:
  * [RecoverableFailure](https://github.com/IBM/cp4s-car-connector-framework/blob/99554ac2cfa0732af090c46be9e356beb015934e/car_framework/util.py#L77) is to be used when the failure cannot potentially create a data gap and we can attempt an incremental import session when running next time. One example of a recoverable failure is a connectivity problem.
  * [UnrecoverableFailure](https://github.com/IBM/cp4s-car-connector-framework/blob/99554ac2cfa0732af090c46be9e356beb015934e/car_framework/util.py#L81) is to be used when the failure can potentially create a data gap and we must run full import session to recover.
  * [DatasourceFailure](https://github.com/IBM/cp4s-car-connector-framework/blob/99554ac2cfa0732af090c46be9e356beb015934e/car_framework/util.py#L92) is to be used when there is datasource API issues.

RecoverableFailure and UnrecoverableFailure are mostly handled in the framework. DatasourceFailure is to be used in the connector code with [a corresponding error code](https://github.com/IBM/cp4s-car-connector-framework/blob/99554ac2cfa0732af090c46be9e356beb015934e/car_framework/util.py#L35). Example: `return ErrorCode.TRANSMISSION_AUTH_CREDENTIALS.value`. 
If none of the Failure classes is used, the framework will raise a [GENERAL_APPLICATION_FAILURE](https://github.com/IBM/cp4s-car-connector-framework/blob/99554ac2cfa0732af090c46be9e356beb015934e/car_framework/app.py#L106) (Unknown error) and print the error stack. 

For more information use guides
* https://github.com/IBM/cp4s-car-connectors/blob/develop/README.md
* https://github.com/IBM/cp4s-car-connectors/blob/develop/guide-build-connectors.md
* https://github.com/IBM/cp4s-car-connectors/tree/develop/connectors/reference_connector
* https://github.com/IBM/cp4s-car-connectors/blob/develop/best-practices.md


## Test deploy
https://github.com/IBM/cp4s-car-connectors/blob/develop/deployment/README.md


## Publish

Use the guide from [PUBLISH.md](./PUBLISH.md)