"""Database related exceptions."""

from __future__ import absolute_import

from . import yam_exception


class ConnectionException(yam_exception.YamException):
    """Exception raised when connecting to database fails."""


class NonExistentModuleException(yam_exception.YamException):
    """Exception raised when module is found to not exist."""

    def __init__(self, module_name):
        yam_exception.YamException.__init__(
            self,
            "{module} does not exist in database".format(module=module_name),
        )


class NonExistentPackageException(yam_exception.YamException):
    """Exception raised when package is found to not exist."""

    def __init__(self, package_name):
        yam_exception.YamException.__init__(
            self,
            "{package} does not exist in database".format(package=package_name),
        )
