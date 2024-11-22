"""Contains the PackageSandbox class."""

from __future__ import absolute_import

import abc
import os

from . import name_utils
from . import sandbox
from . import yam_exception
from .module import WorkModuleType


class PackageSandbox(sandbox.Sandbox):
    """A sandbox that is checked out from a previously released package.

    A package consists of a configuration file and a few other files.

    """

    def __init__(self, package_name, sandbox_path, revision_control_system, file_system):
        """Initialize."""
        sandbox.Sandbox.__init__(self)

        self.__package_name = name_utils.filter_package_name(name=package_name)
        self.__sandbox_path = sandbox_path
        self.__revision_control_system = revision_control_system
        self.__file_system = file_system

    def check_out(
        self,
        progress_callback,
        work_module_type=WorkModuleType.NONE,  # default is to use link module
        # to_work
        # work_branch=False, tagged_branch=False, main_branch=False
        #             work_branch=False,  # unique branch work module
        #             tagged_branch=False,  # tagged release work module
        #             main_branch=False  # main trunk work module
    ):
        """PackageSandbox implementation of sandbox.check_out()."""
        if self.__file_system.path_exists(self.__sandbox_path):
            raise yam_exception.YamException("Sandbox already exists at path '{path}'".format(path=self.__sandbox_path))

        # Check out "YAM.config" and related files along with "common"
        # directory.
        self._check_out_package_data_files(
            package_name=self.__package_name,
            sandbox_path=self.__sandbox_path,
            revision_control_system=self.__revision_control_system,
            file_system=self.__file_system,
            work_module_type=work_module_type,
            parent_directory=self.__sandbox_path,
            progress_callback=progress_callback,
        )

        # Make a symlink to common/Makefile in the root of the sandbox.
        # The symlink should be relative to the sandbox.
        self.__file_system.symbolic_link(
            source=os.path.join("common", "Makefile"),
            link_name=os.path.join(self.__sandbox_path, "Makefile"),
        )

        # Make "src" directory
        self.__file_system.make_directory(path=os.path.join(self.__sandbox_path, "src"))

    @abc.abstractmethod
    def _check_out_package_data_files(
        self,
        package_name,
        sandbox_path,
        revision_control_system,
        file_system,
        parent_directory,
        progress_callback,
        work_module_type=WorkModuleType.NONE,  # default is to use link module
        # to_work
        #             work_branch=False,  # unique branch work module
        #             tagged_branch=False,  # tagged release work module
        #             main_branch=False  # main trunk work module
    ):
        """Check out the data files for this sandbox from the package.

        This includes the "YAM.config" and related files. This also
        includes the "common" directory.

        """


def main_branch_url(package_name, database_reader):
    """Return repository URL to main branch."""
    return "{url}/Packages/{name}/trunk".format(
        url=database_reader.package_repository_url(package_name),
        name=package_name,
    )


def releases_url(package_name, revision_tag, database_reader, check_dead=True):
    """
    Return repository URL to releases. The check_dead option is only
    needed for fixing up missing relatives info for package releases in
    the database. This option can be removed if such fixing up is no
    longer needed.
    """
    return "{url}/Packages/{name}/releases/{name}-{tag}".format(
        url=database_reader.package_repository_url(package_name, check_dead),
        name=package_name,
        tag=revision_tag,
    )


def common_url(package_name, database_reader):
    """Return repository URL to common directory.

    The common directory contains the package configuration information.

    """
    return "{url}/common/trunk".format(url=database_reader.package_repository_url(package_name))


def common_trunk_url(database_reader):
    """Return repository URL to trunk common directory.

    The common directory contains the package configuration information.

    """
    return "{url}/common/trunk".format(url=database_reader.default_repository_url())


def move_package_for_release(
    package_path,
    package_name,
    new_revision_tag,
    release_directory,
    file_system,
    progress_callback,
):
    """Move to release directory, set permissions, and update "Latest" symlink.

    Package will be moved to
        "<release_directory>/Pkg-Releases/<package_name>/
         <package_name>-<tag>"

    """
    directory_name = "{m}-{tag}".format(m=package_name, tag=new_revision_tag)

    destination_path = os.path.join(release_directory, "Pkg-Releases", package_name, directory_name)

    progress_callback("Moving package to release area '{dest}'".format(dest=destination_path))

    file_system.move(source_path=package_path, destination_path=destination_path)

    # make the file within the release directory read-only
    file_system.make_read_only_recursively(destination_path)

    # Update the "Latest" symlink.
    latest_link_path = os.path.join(release_directory, "Pkg-Releases", package_name, "Latest")

    # This should be relative to the 'Latest' link.
    file_system.symbolic_link(source=directory_name, link_name=latest_link_path)
