"""Contains DatabaseReader interface class."""

from __future__ import absolute_import

import abc

from . import yam_exception


class DatabaseReader(object):
    """A database that stores Yam metadata."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def module_names(self):
        """Return a list of names of the modules in the database."""

    @abc.abstractmethod
    def package_names(self):
        """Return a list of names of the packages in the database."""

    @abc.abstractmethod
    def module_history(self, module_names, limit, before, after, ascending):
        """Return dictionary with information about a module's history.

        Returns a list of dictionaries containing 'tag', 'build', 'user',
        and 'datetime'.

        'tag' for example could be 'R1-01a'.
        'build' for example could be the string '03'.
        'user' is a username string.
        'branches' is a comma-separated list of branch names.
        'datetime' is a datetime object.

        """

    @abc.abstractmethod
    def latest_maintenance_release_num(self, module_name, release_tag, maintenance_branch):
        """
        Return last maintenance release number (eg. R4-06j) on the specified release's
        maintenance branch (eg. ProjectA)
        """

    @abc.abstractmethod
    def latest_module_information(self, module_name, release=None):
        """Return dictionary with information about a module's latest release.

        The dictionary contains 'tag', 'build', 'user',
        'branches' and 'datetime'.

        'tag' for example could be 'R1-01a'.
        'build' for example could be the string '03'.
        'user' is a username string.
        'branches' is a comma-separated list of branch names.
        'datetime' is a datetime object.

        """

    @abc.abstractmethod
    def latest_module_information_as_of(self, module_name, release=None, date=None):
        """
        For a module release (eg. R4-52s), return dictionary with information
        about a module's latest release as of certain data.

        This release was the latest as of the given date. If date==None, use the
        latest one available. The rest works exactly as
        latest_module_information():

        The dictionary contains 'tag', 'build', 'user',
        'branches' and 'datetime'.

        'tag' for example could be 'R1-01a'.
        'build' for example could be the string '03'.
        'user' is a username string.
        'branches' is a comma-separated list of branch names.
        'datetime' is a datetime object.

        """

    @abc.abstractmethod
    def module_information(self, module_name, revision_tag):
        """Return dictionary with information about a module.

        The dictionary contains 'build', 'user', 'branches', and
        'datetime'.

        'build' for example could be the string '03'.
        'user' is a username string.
        'branches' is a comma-separated list of branch names.
        'datetime' is a datetime object.

        """

    @abc.abstractmethod
    def all_module_packages(self, type):
        """
        Return dictionary with list of all current modules/packages. The
        'type' argument can take 'MODULE or PACKAGE values.

        The returned dictionary contains name, id, Nreleases, obsolete, repository fields
        'datetime'.
        """

    @abc.abstractmethod
    def has_package_relatives(self, pkg_name, release_tag):
        """
        Return True if the relatives info for this package release is in the database.
        """

    @abc.abstractmethod
    def latest_package_revision_tag(self, package_name):
        """Return the latest revision tag of a package."""

    @abc.abstractmethod
    def module_repository_url(self, module_name):
        """Return a module's repository URL."""

    @abc.abstractmethod
    def package_repository_url(self, package_name):
        """Return package's repository URL."""

    @abc.abstractmethod
    def local_date_time(self):
        """Return a datetime object representing the local of the server.

        Ideally, we would use UTC, but Yam is set up to use local time
        in its "datetime" column.

        """

    @abc.abstractmethod
    def obsolete_builds(self):
        """Return set of names of modules whose builds are obsolete."""

    @abc.abstractmethod
    def module_dependencies(self, module_name):
        """Return set of names of modules that "module_name" depends on."""

    @abc.abstractmethod
    def module_dependents(self, module_name):
        """Return set of names of modules that depend on "module_name"."""


class ModuleLookupException(yam_exception.YamException):
    """Exception raised when not finding module."""


class PackageLookupException(yam_exception.YamException):
    """Exception raised when not finding package."""


class RepositoryLookupException(yam_exception.YamException):
    """Exception raised when URL for repository keyword is not found."""
