"""Contains the MainPackageSandbox class."""

from __future__ import absolute_import

import os

from . import package_sandbox
from . import sandbox
from . import module_configuration_utils
from .module import WorkModuleType


class MainPackageSandbox(package_sandbox.PackageSandbox):
    """A sandbox that is checked out from the main branch of a package.

    This sandbox can be saved, which involves saving the configuration file
    and a few other files.

    The procedure for creating a sandbox has been reverse engineered from the
    old yam since the procedure doesn't seem to be documented. See below for
    the steps for checking out a package sandbox from the main branch.

    1. Check out a sandbox from somewhere main branch of "Packages" repository
       directory.
    2. Check out common from main branch of "common" repository directory.
    3. Make symbolic link in the root of the sandbox pointing to
       "common/Makefile".
    4. Recreate the YAM.config based on YAM.modules.
    5. Create the src directory.
    6. Call "make mklinks".

    """

    def __init__(
        self,
        package_name,
        sandbox_path,
        revision_control_system,
        file_system,
        database_reader,
        configuration_reader,
        configuration_writer,
        default_branch,
        release_directory,
    ):
        """Initialize."""
        package_sandbox.PackageSandbox.__init__(
            self,
            package_name=package_name,
            sandbox_path=sandbox_path,
            revision_control_system=revision_control_system,
            file_system=file_system,
        )

        self.__database_reader = database_reader
        self.__configuration_reader = configuration_reader
        self.__configuration_writer = configuration_writer
        self.__default_branch = default_branch
        self.__release_directory = release_directory

    def _check_out_package_data_files(
        self,
        package_name,
        sandbox_path,
        revision_control_system,
        file_system,
        parent_directory,
        progress_callback,
        work_module_type=WorkModuleType.NONE,  # default is to use link module
    ):  # pylint: disable=W0613
        """Implementation of _check_out_package_data_files()."""

        # assumes SVN repository for now
        revision_control_system._pkg_check_out(
            source=package_sandbox.main_branch_url(
                package_name=package_name,
                database_reader=self.__database_reader,
            ),
            target=sandbox_path,
        )

        # assumes SVN repository for now
        revision_control_system._pkg_check_out(
            source=package_sandbox.common_url(
                package_name=package_name,
                database_reader=self.__database_reader,
            ),
            target=os.path.join(sandbox_path, "common"),
        )

        module_names = self.__configuration_reader.read_package_information(
            package_configuration_filename=os.path.join(sandbox_path, "common", "YAM.modules"),
            package_name=package_name,
        )

        # get a module_directory object with latest link/work modules
        # available for this raw list of modules
        module_dictionary = module_configuration_utils.get_latest_available_modules(
            module_names,
            work_module_type=work_module_type,
            #             work_branch=work_branch,    # unique branch work modules
            #             tagged_branch=tagged_branch,  # tagged release work modules
            #             main_branch=main_branch,     # main trunk work modules
            revision_control_system=revision_control_system,
            release_directory=self.__release_directory,
            database_reader=self.__database_reader,
            default_branch=self.__default_branch,
            file_system=file_system,
            parent_directory=parent_directory,
            progress_callback=progress_callback,
        )

        # Write sandbox YAM.config file
        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=os.path.join(sandbox_path, "YAM.config"),
            work_module_dictionary=module_dictionary["work_modules"],
            link_module_dictionary=module_dictionary["link_modules"],
            default_branch=self.__default_branch,
        )
