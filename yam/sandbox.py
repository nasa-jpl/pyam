"""Contains the Sandbox class."""

from __future__ import absolute_import

import abc

from . import module_saving_utils
from . import module_configuration_utils
from .module import WorkModuleType


class Sandbox(object):
    """Represents a sandbox."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def check_out(
        self,
        work_module_type=WorkModuleType.NONE,  # default is to use link module
        # to_work
        #             work_branch=False,  # unique branch work module
        #             tagged_branch=False,  # tagged release work module
        #             main_branch=False  # main trunk work module
    ):
        """Create the sandbox on the file system.

        Structure of a sandbox is below. (There are other directories, but
        those are created by the Makefile.)

        sandbox-+-src/
                |-common/
                |-Makefile (symlink to common/Makefile)
                `-YAM.config

        """


def write_sandbox_configuration_with_latest(
    module_names,
    configuration_filename,
    default_branch,
    release_directory,
    database_reader,
    configuration_writer,
    file_system,
    revision_control_system,
    parent_directory,
    progress_callback,
    work_module_type=WorkModuleType.NONE,  # default is to use link module
):
    """Write a configuration file that points to the latest link modules.

    The latest link modules are determined by the database.

    """

    """
    THIS METHOD IS OBSOLETE. IT IS BEING KEPT AROUND ONLY TO KEEP THE
    UNIT TESTS HAPPY. DO NOT USE OTHERWISE.
    """

    # print('NNN', module_names)
    # get a module_directory object with latest link/work modules
    # available for this raw list of modules
    module_dictionary = module_configuration_utils.get_latest_available_modules(
        module_names,
        work_module_type=work_module_type,
        revision_control_system=revision_control_system,
        release_directory=release_directory,
        database_reader=database_reader,
        default_branch=default_branch,
        file_system=file_system,
        parent_directory=parent_directory,
        progress_callback=progress_callback,
    )

    # print('LLL', module_dictionary)
    # Write sandbox YAM.config file
    configuration_writer.write_sandbox_configuration(
        configuration_filename=configuration_filename,
        work_module_dictionary=module_dictionary["work_modules"],
        link_module_dictionary=module_dictionary["link_modules"],
        default_branch=default_branch,
    )

    return
