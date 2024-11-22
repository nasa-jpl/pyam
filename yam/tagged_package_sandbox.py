"""Contains the TaggedPackageSandbox class."""

from __future__ import absolute_import

from . import package_sandbox
from . import module_configuration_utils
from . import sandbox
from .module import WorkModuleType


class TaggedPackageSandbox(package_sandbox.PackageSandbox):
    """A sandbox that is checked out from an existing release of a package."""

    def __init__(
        self,
        package_name,
        tag,
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

        self.__tag = tag
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
    ):  # pylint: disable=unused-argument
        """Implementation of package_sandbox._check_out_package_data_files().

        Checked out files will not be writable.

        """
        full_repository_url = package_sandbox.releases_url(
            package_name=package_name,
            revision_tag=self.__tag,
            database_reader=self.__database_reader,
        )

        # Check out the tagged package directory, which contains the "common"
        # directory and yam files.
        # assumes SVN repository for now
        revision_control_system._pkg_check_out(source=full_repository_url, target=sandbox_path)

        file_system.make_read_only_recursively(sandbox_path)

        # print('QQQQ1', self.__default_branch, work_branch, tagged_branch, main_branch)
        # if work_branch or tagged_branch or main_branch:
        if work_module_type != WorkModuleType.NONE:
            # transform the link modules into work modules
            # if work_branch or tagged_branch or main_branch:
            import os

            config_file = os.path.join(sandbox_path, "YAM.config")
            module_dictionary = self.__configuration_reader.read_sandbox_configuration(
                configuration_filename=config_file
            )

            # update the module_directory object with the link/work modules
            # available for this module configuration
            if 1:
                # to_work = work_branch or tagged_branch or main_branch
                to_work = WorkModuleType.NONE not in work_module_type
                module_configuration_utils.update_with_available_modules(
                    module_dictionary,
                    to_work=to_work,
                    # $work_branch=work_branch,    # specified branch
                    # tagged_branch=tagged_branch,  # tagged release
                    # main_branch=False,     # main trunk
                    branch="",  # no branch
                    # revision_control_system=revision_control_system,
                    release_directory=self.__release_directory,
                    database_reader=self.__database_reader,
                    # default_branch='',  #self.__default_branch,
                    # default_branch=self.__default_branch,
                    file_system=file_system,
                )
            else:
                # this is old BAD code that gets the latest versions of
                # the modules instead of the versions for this package
                # release
                module_names = list(module_dictionary.get("link_modules", {}).keys()) + list(
                    module_dictionary.get("work_modules", {}).keys()
                )

                module_dictionary = module_configuration_utils.get_latest_available_modules(
                    module_names,
                    work_module_type=work_module_type,
                    revision_control_system=revision_control_system,
                    release_directory=self.__release_directory,
                    database_reader=self.__database_reader,
                    default_branch=self.__default_branch,
                    file_system=file_system,
                    parent_directory=parent_directory,
                    progress_callback=progress_callback,
                )

            os.rename(config_file, config_file + ".bak")
            self.__configuration_writer.write_sandbox_configuration(
                configuration_filename=config_file,
                work_module_dictionary=module_dictionary["work_modules"],
                link_module_dictionary=module_dictionary["link_modules"],
                default_branch=self.__default_branch,
            )
