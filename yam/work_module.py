"""Contains the WorkModule class."""

from __future__ import absolute_import

import abc
import os

from . import module
from . import name_utils
from . import yam_exception
from . import yam_log


class WorkModule(module.Module):
    """An instance of a Yam module whose source code can be checked out."""

    def __init__(self, module_name, revision_control_system, parent_directory, module_branch_data):
        """Initialize.

        Keyword arguments:
        parent_directory -- the parent directory in which this module will be
        checked out

        """
        module.Module.__init__(self)

        vcs_type = module_branch_data._vcs_type
        self.__module_name = name_utils.filter_module_name(name=module_name)
        self.__Revision_Control_System = revision_control_system[vcs_type]
        self.__parent_directory = parent_directory
        self.__module_path = os.path.join(parent_directory, module_name)
        module_branch_data._module_path = self.__module_path
        self.__module_branch_data = module_branch_data
        self.__do_exists_check = False

        # self.vcs_type = vcs_type

        module._module_branch_data = module_branch_data
        if vcs_type == "git":
            # We need a local copy of the git repo to be able to do things like check/create branches.

            # First, check if we already have a local copy.
            from git import Repo
            from . import git_revision_control_system as grcs

            module_directory = os.path.join(self.__parent_directory, self.__module_name)
            if grcs.GITRevisionControlSystem.working_copy_exists(module_directory):
                # The working copy already exists on the local sandbox. Just use that.
                self._git_repo = Repo(module_directory)
            else:
                # Checkout a copy into the local sandbox. We set __do_exist_check to False
                # to skip the check in check_out later.
                grcs.GITRevisionControlSystem._progress_callback(
                    "Checking out source code for '{name}' module (main)".format(
                        name=self.__module_name,
                    )
                )
                repo_path = grcs.module_repo_path(module_branch_data)
                self._git_repo = Repo.clone_from(repo_path, module_directory)
                self.__do_exists_check = False
            self.__Revision_Control_System.remote_git_repo = True
        else:
            self._git_repo = None

    @abc.abstractmethod
    def _repository_urlOBSOLETE(self):
        """Return release name for this module instance."""

    @abc.abstractmethod
    # def _version_name(self):
    def _repo_tag_name(self):
        """Return the repo tag name for this work module."""

    def rcs(self):
        """
        Return the revision control system for this work module
        """
        if self.__module_branch_data._vcs_type == "git":
            self.__Revision_Control_System.repo = self._git_repo
        return self.__Revision_Control_System

    def check_out(self, progress_callback=lambda _: None):
        """Check out the source code for this Yam module."""
        self._pre_check_out()

        module_directory = os.path.join(self.__parent_directory, self.__module_name)
        # print("MOD DIR: ", module_directory)
        # repo_url = self.rcs().repo.git.rev_parse("--show-toplevel")
        # print("MOD REPO URL: ", repo_url)
        # self.rcs().check_out( None,module_directory)

        if self.rcs().working_copy_exists(path=module_directory) and self.__do_exists_check:
            # verify that the module is not already checked out in the specified location
            # Skip this check if pyam just checkout out the git module on the main branch into the sandbox.
            """
            if self.rcs().url(
                path=module_directory
            ) != self._repository_url():
            """
            # if self.rcs().isMainTrunkCheckout(module_directory):
            path_data = self.rcs().getPathModuleData(module_directory)
            if self.__module_branch_data != path_data:
                raise yam_exception.YamException(
                    "Module directory '{directory}' for '{module}' already exists, ".format(
                        directory=module_directory, module=module_directory
                    )
                    + "but it does not match the expected branch/tag; "
                    "either fix the sandbox configuration or delete the "
                    'module directory before building. Expected "{}" which does not match the YAM.config "{}" value'.format(
                        self.rcs().url(path=module_directory),
                        # self._repository_url(),
                        self.__module_branch_data.dumpStr(),
                    )
                )
        else:
            progress_callback(
                "Checking out source code for '{name}' module ({version})".format(
                    name=self.__module_name,
                    # version=self._version_name()
                    version=self._repo_tag_name(),
                )
            )

            # if self.vcs == "git":
            #    self.rcs().check_out(
            #    source=f"{self.__module_name},{self.__tag},{self.__branch_id}",
            #    target=module_directory,
            # )

            # print("REPO URL FOR CHECKOUT: ", self._repository_url())
            self.rcs().module_check_out(
                source=self.module_branch_data(),  #  self._repository_url(),
                target=module_directory,
            )

            # Only mark as read only on the first check out. Otherwise, we will
            # end up marking build files as read only.
            self._post_check_out(module_directory=module_directory)

    def _pre_check_out(self):
        """Called before checking out source code."""

    def _post_check_out(self, module_directory):
        """Called after checking out source code."""

    def module_branch_data(self):
        """Return the module branch data for this work module."""
        return self.__module_branch_data


def feature_branches_urlOBSOLETE(module_name, revision_tag, branch_id, database_reader):
    """Return repository URL to feature branches."""
    if database_reader.vcs_type(module_name) == "git":
        return database_reader.module_repository_url(module_name) + f"/Modules/{module_name}"
    return database_reader.module_repository_url(
        module_name
    ) + "/Modules/{name}/featureBranches/{name}-{tag}-{branch_id}".format(
        name=module_name, tag=revision_tag, branch_id=branch_id
    )


def check_working_copy(sandbox_root_directory, module_name, revision_control_system):
    """Raise exception if release path is not valid."""
    # for m in module_names:
    if 1:
        yam_log.say("Checking whether {} work module is checked out".format(module_name))
        if not revision_control_system.working_copy_exists(os.path.join(sandbox_root_directory, "src", module_name)):
            raise yam_exception.YamException("Module '{m}' is not checked out".format(m=module_name))


def raise_exception_on_uncommitted_files(revision_control_system, module_name, sandbox_root_directory):
    """Raise an exception if there are uncommitted version-controlled files."""
    # dangling_links = []

    # for m in module_names:
    if 1:
        module_path = sandbox_root_directory + "/src/" + module_name
        uncommitted_module_files = revision_control_system.uncommitted_files(module_path)
        if uncommitted_module_files:
            raise UncommittedFilesException(uncommitted_files=uncommitted_module_files)


def on_main_branch(module_path, revision_control_system):
    """Return True if module is on main branch."""
    return revision_control_system.url(module_path).endswith("/trunk")


def main_branch_urlOBSOLETE(module_name, database_reader, use_git=False):
    """Return repository URL to main branch."""
    # u = database_reader.module_repository_url(module_name)
    if use_git or database_reader.vcs_type(module_name) == "git":
        url = "{url}/Modules/{name}".format(url=database_reader.module_repository_url(module_name), name=module_name)
        return url
    return "{url}/Modules/{name}/trunk".format(url=database_reader.module_repository_url(module_name), name=module_name)


def releases_urlOBSOLETE(module_name, revision_tag, database_reader):
    """Return repository URL to releases."""
    if database_reader.vcs_type(module_name) == "git":
        return "{url}/Modules/{name}".format(
            # return "{url}/Releases/Module-Releases/{name}/{name}-{tag}".format(
            url=database_reader.module_repository_url(module_name),
            name=module_name,
            tag=revision_tag,
        )
    return "{url}/Modules/{name}/releases/{name}-{tag}".format(
        url=database_reader.module_repository_url(module_name),
        name=module_name,
        tag=revision_tag,
    )


def dead_branches_urlOBSOLETE(module_name, revision_tag, branch_id, database_reader):
    """Return repository URL to feature branches."""
    if database_reader.vcs_type(module_name) == "git":
        return f"{module_name},{revision_tag},{branch_id}"  # "doesnt_matter"
        # purposefully nonexistant so dead branches never cause problem for git
        return "{url}/Moduless/{name}".format(
            # return "{url}/Releases/Module-Releases/{name}/{name}-{tag}-{branch_id}".format(
            url=database_reader.module_repository_url(module_name),
            name=module_name,
            # tag=revision_tag,
            # branch_id=branch_id,
        )
    return "{url}/Modules/{name}/deadBranches/{name}-{tag}-{branch_id}".format(
        url=database_reader.module_repository_url(module_name),
        name=module_name,
        tag=revision_tag,
        branch_id=branch_id,
    )


def feature_branches_nameOBSOLETE(module_name, revision_tag, branch_id):
    """Return repository URL to feature branches."""
    return "{name}-{tag}-{branch_id}".format(name=module_name, tag=revision_tag, branch_id=branch_id)


def main_branch_name():
    """Return repository URL to main branch."""
    return "main"


def releases_nameOBSOLETE(module_name, revision_tag):
    """Return repository URL to releases."""
    return "{name}-{tag}".format(name=module_name, tag=revision_tag)


def dead_branches_nameOBSOLETE(module_name, revision_tag, branch_id):
    """Return repository URL to feature branches."""
    return "(DEAD) {name}-{tag}-{branch_id}".format(name=module_name, tag=revision_tag, branch_id=branch_id)


class UncommittedFilesException(yam_exception.YamException):
    """
    Exception raised if there are uncommitted version-controlled files in
    a work module.
    """

    def __init__(self, uncommitted_files):
        yam_exception.YamException.__init__(
            self,
            "The following version-controlled files are uncommitted:\n    {files}".format(
                files="\n    ".join(uncommitted_files)
            ),
        )
