"""Contains DatabaseWriter interface class."""

from __future__ import absolute_import

import abc

from . import yam_exception


class DatabaseWriter(object):
    """A database that stores Yam metadata."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def append_branch(self, module_name, revision_tag, branch_id):
        """Append to the list of branches for the given module."""

    @abc.abstractmethod
    def rename_branch(self, module_name, revision_tag, branch_id, new_branch_id):
        """Rename a branch.

        If this branch_id is found in the branches cell, for the given
        module_name and revision_tag, we will rename it to
        new_branch_id.

        """

    @abc.abstractmethod
    def write_module_source_release_information(
        self,
        module_name,
        revision_tag,
        username,
        date_time,
        changed_api_filename_list,
        readmes,
        num_files_changed,
        num_lines_added,
        num_lines_removed,
        operating_system_name,
        site_name,
        host_ip,
        release_path,
        maintenance_name,
        maintenance_num,
    ):
        """Insert a new row with information about a newly released module."""

    @abc.abstractmethod
    def write_module_build_release_information(
        self,
        module_name,
        revision_tag,
        build_id,
        username,
        date_time,
        readmes,
        operating_system_name,
        site_name,
        host_ip,
        release_path,
    ):
        """Insert a new row with information about a newly released module."""

    @abc.abstractmethod
    def write_package_release_information(self, package_name, link_modules, revision_tag, username, date_time):
        """Insert a new row with information about a newly released package."""

    @abc.abstractmethod
    def register_new_module(self, module_name, repository_keyword, vcs_type):
        """Register a previously non-existent module with the database."""

    @abc.abstractmethod
    def register_new_package(self, package_name, repository_keyword):
        """Register a previously non-existent package with the database."""

    @abc.abstractmethod
    def unregister_module(self, module_name, undo=False):
        """Unregister an existing module from the database."""

    @abc.abstractmethod
    def unregister_package(self, package_name):
        """Unregister an existing package from the database."""

    @abc.abstractmethod
    def populate_package_relatives(self, pkg_name, release_tag, link_modules):
        """Write the relatives information for this package release into the database."""

    @abc.abstractmethod
    def initialize_database(self):
        """Initialize the database.

        This is called for new databases only. A
        DatabaseAlreadyInitializedException will be thrown if called on
        an already initialized database.

        """

    @abc.abstractmethod
    def write_build_dependencies(self, module_name, dependency_dictionary):
        """Populate API dependencies.

        dependency_dictionary is of the following form.

        {<other_module>: {<header_file>, ..., <header_file>},
         ...
         <other_module>: {<header_file>, ..., <header_file>},
        }

        """


class DatabaseAlreadyInitializedException(yam_exception.YamException):
    """Exception raised when trying to initialize more than once."""

    def __init__(self, message):
        yam_exception.YamException.__init__(
            self,
            "Database is already initialized" + "; " + message if message else "",
        )


class ModuleAlreadyExistsException(yam_exception.YamException):
    """Exception raised when module is found to already exist."""

    def __init__(self, module_name):
        yam_exception.YamException.__init__(
            self,
            "{module} already exists in database".format(module=module_name),
        )


class PackageAlreadyExistsException(yam_exception.YamException):
    """Exception raised when package is found to already exist."""

    def __init__(self, package_name):
        yam_exception.YamException.__init__(
            self,
            "{package} already exists in database".format(package=package_name),
        )
