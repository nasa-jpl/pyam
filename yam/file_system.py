"""Contains FileSystem interface class."""

from __future__ import absolute_import

import abc


class FileSystem(object):
    """Methods for accessing/modifying the file system."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def make_read_only(self, filename):
        """Make a file read only."""

    @abc.abstractmethod
    def make_read_only_recursively(self, directory):
        """Drill down directory and make all files read only."""

    @abc.abstractmethod
    def make_writable(self, filename):
        """Make a file writable."""

    @abc.abstractmethod
    def path_exists(self, path):
        """Return True if the path exists on the file system."""

    @abc.abstractmethod
    def list_directory(self, path):
        """Return list filenames in a directory."""

    @abc.abstractmethod
    def make_directory(self, path):
        """Create a directory at path.

        Parent paths will be created if they do not exist.

        """

    @abc.abstractmethod
    def remove_directory(self, path):
        """Remove directory at path.

        This is recursive.

        """

    @abc.abstractmethod
    def move(self, source_path, destination_path, progress_callback=lambda _: None):
        """Move a file or directory from source_path to destination_path.

        If the source_path cannot be removed, it should be copied
        instead.

        """

    @abc.abstractmethod
    def symbolic_link(self, source, link_name, progress_callback=lambda _: None):
        """Create symbolic link pointing to source and call it link_name.

        If a symbolic link already exists at link_name, we will remove
        it beforehand.

        """

    @abc.abstractmethod
    def write_to_file(self, string_data, filename):
        """Write string_data to file.

        If a file already exists, it will be overwritten.

        """

    @abc.abstractmethod
    def read_file(self, filename):
        """Read string data from file filename."""

    @abc.abstractmethod
    def find_dangling_links(self, path):
        """Return list of dangling symbolic links."""

    @abc.abstractmethod
    def common_prefix(self, path_list):
        """Return common prefix of all paths in path_list."""

    @abc.abstractmethod
    def resolve_path(self, path):
        """Return real path.

        This will resolve symbolic links and also resolves things like
        "..".

        """

    @abc.abstractmethod
    def create_temporary_directory(self):
        """Create a temporary directory and return the path to it."""

    @abc.abstractmethod
    def execute(self, filename, working_directory):
        """Execute program at the given path.

        Return (exit_status, output, error). Throw an OSError if
        filename cannot be executed.

        """
