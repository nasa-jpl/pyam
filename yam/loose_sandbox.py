"""Contains the LooseSandbox class."""

from __future__ import absolute_import

import itertools
import os

from . import sandbox
from . import yam_exception
from . import module_configuration_utils
from .module import WorkModuleType


class LooseSandbox(sandbox.Sandbox):
    """A sandbox that is created from list of module names.

    It is not associated with any package.

    """

    def __init__(
        self,
        module_names,
        sandbox_path,
        revision_control_system,
        file_system,
        database_reader,
        repository_url,
        configuration_writer,
        default_branch,
        release_directory,
    ):
        """Initialize."""
        sandbox.Sandbox.__init__(self)

        self.__module_names = module_names
        """
        set(module_names) | set(
            itertools.chain(
                *[
                    _dependencies(m, database_reader.module_dependencies)
                    for m in module_names
                ]
            )
        )
        """

        self.__sandbox_path = sandbox_path
        self.__revision_control_system = revision_control_system
        self.__file_system = file_system
        self.__database_reader = database_reader
        self.__repository_url = repository_url
        self.__configuration_writer = configuration_writer
        self.__default_branch = default_branch
        self.__release_directory = release_directory

    def check_out(
        self,
        parent_directory,
        progress_callback,
        work_module_type=WorkModuleType.NONE,  # default is to use link module
    ):  # pylint: disable=unused-argument
        """LooseSandbox implementation of sandbox.check_out()."""
        if self.__file_system.path_exists(self.__sandbox_path):
            raise yam_exception.YamException("Sandbox already exists at path '{path}'".format(path=self.__sandbox_path))

        # Make sandbox directory
        self.__file_system.make_directory(path=self.__sandbox_path)

        # Check out the common directory from main branch.
        # assumes SVN repository for now
        self.__revision_control_system._pkg_check_out(
            source="{url}/common/trunk".format(url=self.__repository_url),
            target=os.path.join(self.__sandbox_path, "common"),
        )

        # get a module_directory object with latest link/work modules
        # available for this raw list of modules
        module_dictionary = module_configuration_utils.get_latest_available_modules(
            self.__module_names,
            work_module_type=work_module_type,
            #             work_branch=work_branch,    # specified branch work module
            #             tagged_branch=tagged_branch,  # tagged release work module
            #             main_branch=main_branch,     # main trunk work module
            revision_control_system=self.__revision_control_system,
            release_directory=self.__release_directory,
            database_reader=self.__database_reader,
            default_branch=self.__default_branch,
            file_system=self.__file_system,
            parent_directory=parent_directory,
            progress_callback=progress_callback,
        )

        # Write sandbox YAM.config file
        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=os.path.join(self.__sandbox_path, "YAM.config"),
            work_module_dictionary=module_dictionary["work_modules"],
            link_module_dictionary=module_dictionary["link_modules"],
            default_branch=self.__default_branch,
        )

        # Make a symlink to common/Makefile in the root of the sandbox.
        # The symlink should be relative to the sandbox.
        self.__file_system.symbolic_link(
            source=os.path.join("common", "Makefile"),
            link_name=os.path.join(self.__sandbox_path, "Makefile"),
        )

        # Make "src" directory
        self.__file_system.make_directory(path=os.path.join(self.__sandbox_path, "src"))


def _dependenciesOBSOLETE(node, resolve, seen=None):
    """Return all of dependencies of "node".

    "resolve" is used to determine dependencies.

    """
    if not seen:
        seen = set()

    if node in seen:
        return set()
    else:
        seen |= {node}

        found_dependencies = resolve(node)
        if not found_dependencies:
            found_dependencies = set()
        results = set(found_dependencies)

        for d in found_dependencies:
            results |= _dependencies(d, resolve, seen)

        return results
