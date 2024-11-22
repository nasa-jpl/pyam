"""Interface for modules that can be saved."""

from __future__ import absolute_import

import abc

from . import yam_exception


class SavableModule(object):
    """Represents an instance of a module that can be saved."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save(
        self,
        release_note_message,
        username,
        release_directory,
        keep_release,
        build_system,
        operating_system_name,
        site_name,
        host_ip,
        bug_id=None,
        desired_build_id=None,
        release_information_callback=lambda module_name, revision_tag, build_id, site_name, release_note_entry, change_log_entry, diff: None,
        progress_callback=lambda _: None,
    ):
        """Save the branch.

        Return the new (up-to-date) revision tag (for example 'R5-01a').

        This will increment the revision tag and make this instance of the
        module the latest version. An exception will be raised if a save() is
        attempted when no source code is checked out. An UncommittedFileError
        will be raised if files are uncommitted.

        release_directory is the directory in which the module directory will
        be placed after we are done with it. It should already exist. The
        released module will be placed in

        <release_directory>/Module-Releases/<module_name>/<module_name>-<tag>

        release_information_callback is a function that takes in three keyword
        arguments: release_note_entry, change_log_entry, and diff. All three
        are strings.

        """

    @abc.abstractmethod
    def generate_log(self):
        """Return a string containing the log of changes."""

    @abc.abstractmethod
    def pre_save_check(self, release_directory):
        """Check if save is possible.

        Otherwise raise a PreSaveException.

        """


class PreSaveException(yam_exception.YamException):
    """Exception raised when preconditions for saving a module are not met."""


class RepositoryURLMismatchError(PreSaveException):
    """
    Exception raised when a mismatching repository URL is encountered.

    This is used when the BranchedWorkModule's branch ID and revision
    tag don't match the information in the checked out directory.

    """

    def __init__(self, expected_url, actual_url):
        super(RepositoryURLMismatchError, self).__init__(
            "Repository is expected to be '{expected}', but we ".format(expected=expected_url)
            + "instead see '{actual}' in the checked out directory".format(actual=actual_url)
        )

        self.expected_url = expected_url
        self.actual_url = actual_url
