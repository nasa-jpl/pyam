"""Contains the BuildSystem interface class."""

from __future__ import absolute_import

import abc


class BuildSystem(object):
    """Handles building source code."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build(self, module_names, sandbox_directory):
        """Build binaries/libraries from source code.

        Returns True if successful, otherwise False.

        """

    @abc.abstractmethod
    def clean(self, module_names, sandbox_directory):
        """Remove previously built binaries.

        Returns True if successful, otherwise False.

        """

    @abc.abstractmethod
    def make_links(self, module_names, sandbox_directory, release_directory):
        """Create the symbolic links for this directory.

        Returns True if successful, otherwise False.

        """

    @abc.abstractmethod
    def remove_links(self, module_names, sandbox_directory, release_directory):
        """Remove the symbolic links that were previously created.

        Returns True if successful, otherwise False.

        """

    @abc.abstractmethod
    def create_build_files(
        self,
        path,
        release_directory,
        operating_system_name,
        top_level_file_callback=lambda _: None,
    ):
        """Create build files at path.

        These files will be used by the build system.
        top_level_file_callback will be passed each the path to each
        file and directory at the top level.

        """

    @abc.abstractmethod
    def create_module_files(self, module_name, module_path, top_level_file_callback=lambda _: None, use_git=False):
        """Create files for a new module at module_path.

        These files will be used by the build system.
        top_level_file_callback will be passed each the path to each
        file and directory at the top level.

        The use_git arg is temporary, here until we can use the SQL db to
        decide whether to use git commands
        or svn commands

        """

    @abc.abstractmethod
    def build_dependencies(self, module_path, release_directory):
        """Return build dependencies.

        Returned dictionary is of the form.

        {<other_module>: {<header_file>, ..., <header_file>},
         ...
         <other_module>: {<header_file>, ..., <header_file>},
        }

        """

    @abc.abstractmethod
    def check_build_server(self, sandbox_directory):
        """Return True if build server is accessible."""
