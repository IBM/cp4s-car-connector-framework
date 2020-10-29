# Car Connector Framework

Use [car-reference-connector](https://github.com/IBM/cp4s-car-reference-connector) project as an example of how this framework is to be used.

A CAR connector project will need to extend the framework classes: BaseFullImport, BaseIncrementalImport, BaseApp and implement abstract methods of those classes.

Things to note:

* All communications with CAR digestion microservice are managed by the framework. Connector code normally does not need to access CAR digestion microservice directly

* The framework is trying to make some intelligent choice for whether to run full vs incremental import. Normally, for performance reasons we would always prefer to run incremental import if one is possible. Some examples of when it is not possible are:
  * The model states for generating delta are not available
  * The model on the CAR side is empty
  * The previous incremental import session failed and a new incremental import session can potentially create a gap in the model data

* Because of the above the the connector code should properly use (throw/raise) one of two following exceptions when detecting failures:
  * RecoverableFailure is to be used when the failure cannot potentially create a data gap and we can attempt an incremental import session when running next time. One example of a recoverable failure is a connectivity problem.
  * UnrecoverableFailure is to be used when the failure can potentially create a data gap and we must run full import session to recover.

