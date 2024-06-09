# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


# Base exception class
class StockAppException(Exception):
    pass


class RecorderInitializationError(StockAppException):
    """Error type for re-initialization when starting an experiment"""


class LoadObjectError(StockAppException):
    """Error type for Recorder when can not load object"""


class ExpAlreadyExistError(Exception):
    """Experiment already exists"""
