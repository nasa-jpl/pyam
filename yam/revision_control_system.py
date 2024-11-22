"""Contains the RevisionControlSystem interface class."""

from __future__ import absolute_import

import abc

from . import yam_exception
from typing import Optional


class ModuleBranchData(object):
    """
    Data defining the module release/branch info
    """

    def __init__(self, module_name, vcs_type, vcs_root, release_tag=None, branch_id=None, dead_branch=False):
        self._module_name = module_name

        # must have a release id, either 'main' or release tag such as 'Rx-xxx'
        # assert release_tag
        # cannot have branch for the main trunk
        # assert not (release_tag == 'main' and branch_id)

        self._release_tag = release_tag  # module_name+'-'+release_tag
        self._branch_id = branch_id
        self._vcs_type = vcs_type

        self._full_tag = module_name + "-" + release_tag if release_tag else module_name
        # the repo root path
        self._vcs_root = vcs_root
        self._dead_branch = dead_branch
        # path to repo in users sandbox
        self._module_path = None

    def __str__(self):
        return self.dumpStr()

    def release_tag(self):
        """ "Creates the release tag, which is module_name+release_tag"""
        return self._module_name + "-" + self._release_tag

    def clone(self):
        """
        Return a new ModuleBranchData instance with branch_id set to the
        specified value
        """
        return ModuleBranchData(
            module_name=self._module_name,
            vcs_type=self._vcs_type,
            vcs_root=self._vcs_root,
            release_tag=self._release_tag,
            branch_id=self._branch_id,
            dead_branch=self._dead_branch,
        )

    def __eq__(self, other):
        """
        Return True if this object has the same field as other.
        """
        return (
            other._module_name == self._module_name
            and other._vcs_type == self._vcs_type
            and other._vcs_root == self._vcs_root
            and other._release_tag == self._release_tag
            and other._branch_id == self._branch_id
            and other._dead_branch == self._dead_branch
        )

    def with_branch_id(self, branch_id):
        """
        Return a new ModuleBranchData instance with branch_id set to the
        specified value
        """
        result = self.clone()
        result._branch_id = branch_id
        return result

    def with_release_tag(self, release_tag, branch_id=None):
        """
        Return a new ModuleBranchData instance with specified release_tag
        and branch_id
        """
        assert release_tag
        assert not (branch_id and release_tag == "main")
        result = self.clone()
        result._release_tag = release_tag
        result._branch_id = branch_id
        return result

    def with_dead_branch(self):
        """
        Return a new ModuleBranchData instance with branch_id set to the
        specified value
        """
        result = self.clone()
        result._dead_branch = True
        return result

    def dump(self, indent=""):
        """
        Print content as a string for debugging
        """
        print(self.dumpStr(), indent)

    def repoPath(self) -> str:
        if self._vcs_type == "git":
            # Git repos will have the Modules folder already included if necessary.
            return "{url}/{name}".format(url=self._vcs_root, name=self._module_name)
        else:
            # SVN repos should have /Modules added to the URL.
            return "{url}/Modules/{name}".format(url=self._vcs_root, name=self._module_name)

    # def uri(self, release_tag : str =None, branch_id: str =None) -> str:
    # def dump(self, release_tag : str =None, branch_id: str =None) -> str:
    def dumpStr(self, indent="") -> str:
        """
        Return content as a string for debugging
        """
        if self._vcs_type == "git":
            # Git repos will have the Modules folder already included if necessary.
            msg = "{url}/{name},{r},{b}".format(
                url=self._vcs_root, name=self._module_name, r=self._release_tag, b=self._branch_id, d=self._dead_branch
            )
        else:
            # SVN repos should have /Modules added to the URL.
            msg = "{url}/Modules/{name},{r},{b}".format(
                url=self._vcs_root, name=self._module_name, r=self._release_tag, b=self._branch_id, d=self._dead_branch
            )
        return msg

        """
        # must have a release id, either 'main' or release tag such as 'Rx-xxx'
        if release_tag is None:
            release_tag = self._release_tag
        assert release_tag

        if branch_id is None:
            branch_id = self._branch_id

        # cannot have branch for the main trunk
        assert not (release_tag == 'main' and branch_id)

        if self._vcs_type=='svn':
            result =  '{root}/Modules/{m}'.format(root=self._vcs_root, m= self._module_name)

            if release_tag == 'main':
                # main trunk URI
                result +=  '/trunk'
            else:
                if branch_id:
                    # branch URI
                    area = 'deadBranches' if self._dead_branch else 'featureBranches'
                    result +=  '/{a}/{m}-{r}-{b}'.format(m= self._module_name,
                                                         a=area,
                                                         r=release_tag,
                                                         b=branch_id)
                else:
                    # release URI
                    result +=  '/releases/{m}-{r}'.format(m= self._module_name,
                                                          r=release_tag)
            return result

        elif self._vcs_type=='git':
            # return the file system path to the git repo
            url = "{url}/Modules/{name},{r},{b}".format(url=self._vcs_root, #database_reader.module_repository_url(module_name),
                                                        name=self._module_name, r=release_tag,b=branch_id)
            return url
    """

    def repoBranchTag(self):
        """
        Return the repo tag name for the branch,i.e.<module-name>-<release_tag>-<branch_id>
        """
        assert self._branch_id
        assert self._release_tag
        assert self._release_tag != "main"
        # return f"{self._release_tag}-{self._branch_id}"
        return "{m}-{r}-{b}".format(m=self._module_name, r=self._release_tag, b=self._branch_id)

    def repoReleaseTag(self):
        """
        Return the repo tag name for the release,i.e.<module-name>_<release_tag>
        """
        assert self._release_tag
        assert self._release_tag != "main"
        # return self._release_tag
        return "{m}-{r}".format(
            m=self._module_name,
            r=self._release_tag,
        )


class RevisionControlSystem(object):
    """A class that interfaces to a revision control system."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _pkg_check_out(self, source: str, target: str):
        """
        Check out the contents of the source URL and put it in the target
        directory. This method is SVN specific and only meant to be used
        for package level check outs.
        """

    @abc.abstractmethod
    def module_check_out(self, source: ModuleBranchData, target: str):
        """Check out the source for a module and put it in the target directory."""

    @abc.abstractmethod
    def check_in(self, path: str, log_message: str, wmpath: str = ""):
        """
        Check in the changes on the specified path. If wmpath is non-null,
        use the wmpath repo
        """

    @abc.abstractmethod
    def markBranchDead(self, wmpath: str):
        """
        Mark the branch for the checked out module as dead.
        """

    @abc.abstractmethod
    def isConsistent(self, path, expected_data: ModuleBranchData):
        """
        Return True if the checked out path's branch/tag is consistent with
        the expected data.
        """

    @abc.abstractmethod
    def create_module(self, vcs_root: str, module_name: str, bare: bool):
        """
        Create the VCS structure for the new module in the repo for a R1-00
        release. If bare is True, then git will create bare repo. This
        variable has effect forSVN
        """

    @abc.abstractmethod
    def create_and_commit_basic_module_files(self, vcs_root: str, module_name: str, file_system, build_system, bare):
        """
        Add basic module files when creating a new module.
        """

    @abc.abstractmethod
    def hasMainTrunkCommits(self, tagged_module_data: ModuleBranchData):
        """
        Return True if there are main trunk commits beyond the tagged module
        release. Normally used with latest tagged module data.
        """

    @abc.abstractmethod
    def getPathModuleData(self, wm_path: str) -> ModuleBranchData:
        """
        Return a ModuleBranchData instance with the release_tag/branch info
        for the work modules path.
        """

    @abc.abstractmethod
    def isTaggedCheckout(self, wm_path: str):
        """
        Return True if the work module path pointed to is for a tagged release checkout.
        """

    @abc.abstractmethod
    def isMainTrunkCheckout(self, wm_path: str):
        """
        Return True if the work module path pointed to is for a main trunk checkout.
        """

    @abc.abstractmethod
    def make_directory(self, path: str):
        """Make a revision controlled directory at this path.

        Parent directories will be created if they do not exist.

        Raise a DirectoryAlreadyExists if the directory already exists.

        """

    @abc.abstractmethod
    def update(self, path: str):
        """Update the contents of path to the latest revision."""

    @abc.abstractmethod
    def working_copy_exists(self, path: str):
        """Return true if a checked out working copy exists at the given path."""

    @abc.abstractmethod
    def branch(self, source_url: ModuleBranchData, destination_url: ModuleBranchData):
        """Make a branch from source_url and name it destination_url."""

    @abc.abstractmethod
    def tag(self, destination_url: ModuleBranchData, message: Optional[str] = None, path: Optional[str] = None):
        """Create a tag from destination_url."""

    @abc.abstractmethod
    def switch_to_branch(self, path: str, branch_url: ModuleBranchData):
        """Switch the working directory to the branch_url branch."""

    @abc.abstractmethod
    def switch_to_tag(self, path: str, tag_url: ModuleBranchData):
        """Switch the working directory to the tag."""

    @abc.abstractmethod
    def reintegrate(self, path, target_data: ModuleBranchData, archive_data: ModuleBranchData):
        """
        path : path on file system with the original branch
        target_data:  the destination branch to merge into
        archive_data: the new name to give the original branch to mark it as dead

        Merge the working copy's branch back into the target_data branch.

        After merge is complete, mark the original branch as dead by
        renaming the branch of the path to archive_data.

        At the end, path will be working off of the target_data branch.
        """

    @abc.abstractmethod
    def exists_module_branch(self, module_branch_data: ModuleBranchData) -> bool:
        """
        Return True if the specified module revision/brach exists in the
        repo (including as a dead branch).
        """

    @abc.abstractmethod
    def url(self, path):
        """Return revision control URL of path. Deprecated - do not use."""

    @abc.abstractmethod
    def uncommitted_files(self, path: str):
        """Return list of uncommitted version-controlled files."""

    # TODO: Get rid of this and just use the other log generating method for
    #       everything.
    @abc.abstractmethod
    def generate_logs_since_last_branch(self, path: str, ignored_paths=()):
        """Return string representing all logs since the branch was created.

        This should not return log information about the branch-creation event.

        Paths in ignored_paths tuple will be excluded from the log. These paths
        are relative to path parameter.

        """

    @abc.abstractmethod
    def generate_logs_since_divergence(
        self,
        path,
        tagged_url: ModuleBranchData,
        # path_url : ModuleBranchData = None,
        ignored_paths=(),
    ):
        """Return string representing all logs on path since the divergence.

        tagged_url is a tagged branch that was at some point branched from
        path's URL.

        paths_url can be used for repo URL when it is different from
        that of the path.

        Paths in ignored_paths tuple will be excluded from the log. These paths
        are relative to path parameter.

        """

    @abc.abstractmethod
    def generate_diff(
        self, from_data: ModuleBranchData, to_data: ModuleBranchData, path: str, ignored_paths=()
    ):  # to_url,
        """
        Return string representing diff since the beginning of the branch on
        the specified path (or the to_data revision info).

        The diff is in unified format.
        """

    @abc.abstractmethod
    def modified_paths_since_divergence(self, path, tagged_url: ModuleBranchData):
        """Return a list of changed files."""

    #     @abc.abstractmethod
    #     def has_modifications(self, from_url : str, to_url : str):
    #         """Return True if there are unreleased committed changes on the path. Avid using."""

    @abc.abstractmethod
    def add_file(self, path):
        """Put file under revision control.

        This is done recursively if path is a directory.

        A AlreadyUnderRevisionControl exception will be raised if a file is
        already under revision control.

        """

    @abc.abstractmethod
    def list_files(self, path):
        """Yield list of files under revision control."""


class NotAWorkingCopyException(yam_exception.YamException):
    """Raised when encountering a path that is not a working copy."""

    def __init__(self, path):
        yam_exception.YamException.__init__(self, "Path '{path}' is not a working copy".format(path=path))
        self.path = path


class DirectoryAlreadyExists(yam_exception.YamException):
    """Raised when trying to create a directory that already exists."""

    def __init__(self, path_or_url):
        yam_exception.YamException.__init__(
            self,
            "Cannot create directory '{d}' as it already exists".format(d=path_or_url),
        )
        self.path_or_url = path_or_url


class PermissionException(yam_exception.YamException):
    """Raised when a permission error occurs."""


class NonExistentURLException(yam_exception.YamException):
    """Raised when encountering a URL that does not exist in the repository."""

    def __init__(self, url):
        yam_exception.YamException.__init__(self, "URL '{url}' does not exist".format(url=url))
        self.url = url


class ReintegrationException(yam_exception.YamException):
    """Raised when a reintegration merge fails."""


class AlreadyUnderRevisionControl(yam_exception.YamException):
    """Raised when an added file is already under revision control."""


def url_checkOBSOLETE(revision_control_system, url):
    """Raise NonExistentURLException exception on finding non-existent URLs."""
    if not revision_control_system.exists(url=url):
        raise NonExistentURLException(url=url)
