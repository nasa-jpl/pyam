"""Contains an GIT implementation of the RevisionControlSystem class."""

from __future__ import absolute_import

import contextlib
import os
import signal

from git import Repo
from pathlib import Path
from typing import Set, Optional

# from sympy import source

from . import pysvn_verbose as pysvn
from . import revision_control_system
from . import module_saving_utils
from . import yam_exception
from . import yam_log


class GITRevisionControlSystem(revision_control_system.RevisionControlSystem):
    """A GitVN implementation of the RevisionControlSystem class."""

    _progress_callback = lambda _: None

    def __init__(
        self,
        username,
        login_callback,
        trust_ssl_server_callback,
        use_merge_info=True,
        progress_callback=None,
    ):
        """Create an instance of git_revision_control_system.

        username can be set to None to use the default username.

        progress_callback is called when data transfer occurs. The function has
        two parameters. The first is the number of bytes transferred. The
        second parameter is a boolean that indicates transfer completion when
        True. Set progress_callback to None to disable it.

        """
        revision_control_system.RevisionControlSystem.__init__(self)

        self.__username = username
        self.__login_callback = login_callback
        self.__trust_ssl_server_callback = trust_ssl_server_callback
        self.__use_merge_info = use_merge_info
        self.repo = None
        # if true then the repo is the remote master repo, else the local working copy
        self.remote_git_repo = True
        # these are set when checking out
        # self.branch_id = None
        # self.tag = None
        # self.branch_name = None
        self.vcs = "git"

        # set to true to create a bare git repo (needed for network use)
        # self._bare = True

        # We only enable this for particular calls via
        # _progress_context_manager().
        self.__progress_callback = progress_callback

    def _pkg_check_out(self, source: str, target: str):
        """SVN implementation of revision_control_system._check_out()."""
        # NOT NEEDED OR IMPLMENTED. This method is currently only used
        # for package related check outs
        assert 0

    def _check_out1(self, repo_path: str, module_name, tag, branch_id, target: str):
        """GIT implementation of revision_control_system.check_out().
        This is called clone in git.
        If SOURCE is None, use the root of the repo associated with self.repo as source instead.
        """
        if not repo_path:
            repo_path = self.repo.git.rev_parse("--show-toplevel")  # Repo(source).git
            Repo.clone_from(repo_path, target)
            self.repo = Repo(target)
            return
        else:
            # The repo was already created. Now, we just need to switch to the correct branch.
            self.repo = Repo(target)

        if tag and branch_id:
            # We've got a full branch name. This branch has already been created. Just switch to it.
            branch_id = f"{module_name}-{tag}-{branch_id}"
            self.repo.git.checkout(branch_id)
            return

        if tag != "main":
            # This is a tagged checkout. Just checkout the tag.
            self.repo.git.checkout(module_name + "-" + tag)
        else:
            # We want the main branch.
            self.repo.git.checkout("main")

    def _check_outOBSOLETE(self, source: str, target: str):
        """GIT implementation of revision_control_system.check_out().
        This is called clone in git.
        If SOURCE is None, use the root of the repo associated with self.repo as source instead.
        """
        # source_uri = source.uri()
        if not source:
            source = self.repo.git.rev_parse("--show-toplevel")  # Repo(source).git
            self.repo.git.clone(source, target)
            return
        if self.tag and self.branch_id:  # "," in source:
            # print("ALL BRANCHES")
            # print(self.repo.git.branch())
            # branch_id = source.replace(",","-")
            branch_id = f"{source}-{self.tag}-{self.branch_id}"
            source = self.repo.git.rev_parse("--show-toplevel")
            self.repo.git.clone("-b", branch_id, source, target)
            return
        if self.tag:
            self.repo.git.clone("--depth=1", "--branch", self.tag, source, target)
            return

        self.repo.git.clone(source, target)

    def _check_outDISCARD(self, source: str, tag, branch_id, target: str):
        """GIT implementation of revision_control_system.check_out().
        This is called clone in git.
        If SOURCE is None, use the root of the repo associated with self.repo as source instead.
        """
        # source_uri = source.uri()
        # print('NNN', source, tag, bracnch_id, target)
        if not source:
            source = self.repo.git.rev_parse("--show-toplevel")  # Repo(source).git
            self.repo.git.clone(source, target)
            return
        if tag and branch_id:  # "," in source:
            # print("ALL BRANCHES")
            # print(self.repo.git.branch())
            # branch_id = source.replace(",","-")
            branch_id = f"{source}-{tag}-{branch_id}"
            source = self.repo.git.rev_parse("--show-toplevel")
            self.repo.git.clone("-b", branch_id, source, target)
            return
        if self.tag:
            self.repo.git.clone("--depth=1", "--branch", tag, source, target)
            return

        self.repo.git.clone(source, target)

    def module_check_out(self, source: revision_control_system.ModuleBranchData, target: str):
        """GIT implementation of revision_control_system.check_out().
        This is called clone in git.
        If SOURCE is None, use the root of the repo associated with self.repo as source instead.
        """
        repo_path = module_repo_path(source)

        # FIX: this is incorrect, we should be checking out the specific branch
        # print('LLLL', repo_path, target)
        # print('XXXX', source.dumpStr())
        self._check_out1(repo_path, source._module_name, source._release_tag, source._branch_id, target)  # repo_path,

    def export_file(self, source, target):
        """GIT implementation of revision_control_system.check_out()."""
        assert 0

    def check_in(self, path, log_message, wmpath=""):
        """GIT implementation of revision_control_system.check_in().
        This is called commit in git
        """
        if wmpath:
            # use the working path repo to do the commit
            from git import Repo

            wmrepo = Repo(wmpath)
            wmrepo.git.pull()
            wmrepo.git.add(update=True)
            wmrepo.index.commit(log_message)
            wmrepo.git.push()
        else:
            self.repo.index.commit(log_message)

    def make_directory(self, path):
        """GIT implementation of revision_control_system.make_directory()."""
        # want to make sure we use the right git repo, so get the path to the
        # top level of the repo that path is in, then add it
        git = Repo(path, search_parent_directories=True).git
        git_root = git.rev_parse("--show-toplevel")
        Repo(git_root).git.add(path)

    def update(self, path):
        """GIT implementation of revision_control_system.update()."""
        repo = Repo(path._module_path)
        if repo.head.is_detached:
            # We are on a tag, do a fetch rather than a pull.
            repo.git.fetch("--all")
        else:
            repo.git.pull()

    def tag_git_moduleOBSOLETE(self, module_name, revision_tag, repo=None):
        repo = repo or self.repo

        repo.git.tag(module_name + "-" + revision_tag)

    @classmethod
    def working_copy_exists(cls, path):
        """GIT implementation of working_copy_exists()."""
        if not os.path.exists(path):
            return False

        # get top level of repo this path is in, then check if path is tracked by that repo
        git = Repo(path, search_parent_directories=True).git
        git_root = git.rev_parse("--show-toplevel")
        repo = Repo(git_root)

        # Get the path relative to the git_root
        rel_path = str(Path(path).resolve().relative_to(Path(git_root)))

        if not repo.git.ls_files(rel_path):
            return False
        return True

    def switch_to_branch(self, path, branch_url):
        """GIT implementation of revision_control_system.switch_to_branch()."""
        repo = Repo(path)
        branches = _get_branches_and_tags(repo)
        git = repo.git

        if branch_url._branch_id:
            branch = branch_url.repoBranchTag()
        else:
            assert branch_url._release_tag != "main"
            branch = branch_url.repoReleaseTag()

        if branch in branches:
            # Swtich to branch if it already exists
            git.checkout(branch)
        else:
            # Create a new branch
            git.checkout("-b", branch)
            git.push("--set-upstream", "origin", branch)

    def switch_to_tag(self, path, tag_url):
        """
        Checkout the given tag.
        """
        Repo(path).git.fetch(
            "--all", "--tags"
        )  # Fetch tags to ensure we have the tag we are trying to switch to in the local repo
        Repo(path).git.checkout(tag_url.repoReleaseTag())  # Checkout the tag

    def tag(
        self,
        destination_url: revision_control_system.ModuleBranchData,
        message: Optional[str] = None,
        path: Optional[str] = None,
    ):
        """
        Create an annotated tag for self.repo. The message used for the tag is
        given by the optional message keyword. If none is given, then the message
        will be:

        Tag for {tag} release.

        Parameters
        ----------
        destination_url : revision_control_system.ModuleBranchData
            Destination_url contains the new tag name.
        message : Optional[str]
            Message for the annotated tag.
        path : Optional[str]
            Path the git repo. If none, then self.repo is used.
        """
        new_tag = destination_url.repoReleaseTag()
        if path:
            repo = Repo(path)
        else:
            repo = self.repo
        _create_tag(repo, new_tag, message)

    def branch(
        self,
        source_url: revision_control_system.ModuleBranchData,
        destination_url: revision_control_system.ModuleBranchData,
    ):

        # Start by fetching to ensure we have all of the latest branch info
        # This won't update the current branch. This is only an issue if we are branching off the
        # current branch. In this method, we only branch off of a tag or main. Therefore, if we are
        # on branch main, we also need to do a git pull. We handle this case below.
        self.repo.git.fetch()

        if destination_url._branch_id:
            assert destination_url.repoReleaseTag() == source_url.repoReleaseTag()
            # create a feature branch

            # branch_off = source_url.repoBranchTag() if source_url._branch_id else source_url._full_tag
            branch_off = destination_url.repoReleaseTag()

            # Ensure this branch exists locally. If it does not, pull it from remote.
            _fetch_branch(self.repo, branch_off)

            new_branch = destination_url.repoBranchTag()
        else:
            # create a tagged release branch off of main
            branch_off = "main"
            if _get_current_branch(self.repo) == "main":
                # Do a pull if we are currently on main. This is needed since local main
                # may be different than origin main.
                self.repo.git.pull()

            new_branch = destination_url.repoReleaseTag()
        self.repo.git.branch(new_branch, branch_off)
        self.repo.git.push("--set-upstream", "origin", new_branch)

    def reintegrate(
        self,
        path,
        target_data: revision_control_system.ModuleBranchData,
        archive_data: revision_control_system.ModuleBranchData,
    ):
        """GIT implementation of revision_control_system.merge()."""
        # print("QQQQQ")
        # print(path)
        # print(target_data)
        # print(archive_data)

        # WHERE IS "path" being used

        # create the repo for the desination branch
        # when saving, path is the module_repo path
        # when syncing, path is the path to the module in the sandbox

        # save : target_data = remote main branch

        # sync: target_data = new branch off of latest in remote

        source_data = self.getPathModuleData(path)
        assert source_data._branch_id
        branch_name = source_data.repoBranchTag()
        #         print("XXXX")
        #         print(source_data)
        #         print(target_data)
        #         print(target_data.repoPath())
        #         print(branch_name)

        if 0 and target_data._release_tag == "main":
            # for sync
            # print("JJJJ MERGE SYNCING")
            git = Repo(path).git
            # git.fetch("origin", target_data.repoBranchTag())
            # print('OKKK1', git.status())
            git.switch("main")
            # print('SSSS', git.diff('main', branch_name))
            # print('OKKK2', git.status())
            git.merge(branch_name, no_commit=True, verbose=True)
            remote_git = Repo(target_data.repoPath()).git
            remote_git.branch("-m", branch_name, branch_name + "_dead")
            # git.switch(target_data.repoReleaseTag())

        bare_repo = True
        # git = Repo(path).git
        if target_data._release_tag == "main":

            # for save
            # print("JJJJ MERGE SAVE MAIN")

            diff = self.generate_diff(from_data=source_data, path=path)
            # print('DIFF', diff)
            # repo = Repo(target_data.repoPath())

            if not bare_repo:
                repo = self.repo
                remote_git = repo.git
                remote_git.merge(branch_name)
            else:
                repo = Repo(path)
                wmgit = repo.git
                # bring the destination branch into the local repo
                dest_branch = "main"
                wmgit.fetch("origin", dest_branch)
                # switch the local path to the destination branch
                wmgit.switch(dest_branch)
                # merge the old branch into the new branch
                # print('XXXX', branch_name)

                wmgit.merge(branch_name, no_commit=True)

            _rename_branch(repo, branch_name, branch_name + "_dead")

        else:
            # for sync
            # print("JJJJ MERGE SYNCING")

            wmgit = Repo(path).git
            # bring the destination branch into the local repo
            dest_branch = target_data.repoBranchTag()
            wmgit.fetch("origin", dest_branch)
            # switch the local path to the destination branch
            wmgit.switch(dest_branch)
            # merge the old branch into the new branch
            wmgit.merge(branch_name, no_commit=True)

            _rename_branch(self.repo, branch_name, branch_name + "_dead")

    def markBranchDead(self, wmpath: str):

        # return
        source_data = self.getPathModuleData(wmpath)
        assert source_data._branch_id
        branch_name = source_data.repoBranchTag()
        """
        wmgit = Repo(wmpath).git
        wmgit.branch("-m",branch_name,
                     branch_name+"_dead")
        """
        _rename_branch(self.repo, branch_name, branch_name + "_dead")

    def exists_module_branchOBSOLETE(self, module_branch_data: revision_control_system.ModuleBranchData):
        """GIT implementation of revision_control_system.exists()."""
        # Sometimes, we check if a branch exists. In this case, the url will have no slashes
        # and will have a "-" in it. Otherwise we just check if a dir exists like normal
        # if "," in url and "/" not in url:
        #    url = url.replace(",","-")
        #    print("EXISTS BRANCH?=",url)
        #    return self.branch_exists(url)

        # FIX - we should really be checking for the existence of a tag - not a path
        # FIX - handling of dead branches

        if module_branch_data._dead_branch:
            return False
        return os.path.isdir(module_repo_path(module_branch_data))

    def exists_module_branch(self, module_branch_data: revision_control_system.ModuleBranchData):
        """ "We can't use the regular exists method for checking branches like we do in svn
        because branches are not folders anymore."""

        # Get repo branches
        branches = _get_branches_and_tags(self.repo)

        if module_branch_data._dead_branch:
            # this means we are checking if this branch has been merged into main before
            dead_branch_name = module_branch_data.repoBranchTag() + "_dead"
            return dead_branch_name in branches
            # merged_branches = self.repo.git.branch("main", merged=True)
            # return module_branch_data.repoBranchTag() in merged_branches
        if module_branch_data._branch_id:
            # have a branch
            branch_name = module_branch_data.repoBranchTag()
            # print("BRANCHESS: ", branches, branch_name)
            return branch_name in branches
        else:
            # have a release tag

            tag_name = module_branch_data._full_tag  # release_tag()   # repoReleaseTag()
            # print("BRANCHESS: ", branches, tag_name)
            return tag_name in branches

            assert 0

            tags = self.repo.git.tag()

            return tag_name in tags

    def branch_existsODSOLETE(self, branch_name):
        """ "We can't use the regular exists method for checking branches like we do in svn
        because branches are not folders anymore."""
        branches = self.repo.git.branch()
        # print("BRANCHESS: ", branches)
        return branch_name in branches

    def _exists(self):
        """GIT implementation of revision_control_system.exists()."""
        # Sometimes, we check if a branch exists. In this case, the url will have no slashes
        # and will have a "-" in it. Otherwise we just check if a dir exists like normal
        # if "," in url and "/" not in url:
        #    url = url.replace(",","-")
        #    print("EXISTS BRANCH?=",url)
        #    return self.branch_exists(url)

        # we should really be checking for the existence of a tag - not a path
        assert 0
        return os.path.isdir(url)

    def create_module(self, vcs_root: str, module_name: str, bare: bool):
        # Create the VCS structure for the new module in the repo for R1-00 release

        # create git structure for the new module

        import tempfile

        self._temp_dir = tempfile.TemporaryDirectory()

        path = "{r}/{name}".format(r=vcs_root, name=module_name)
        exists = False
        try:
            from git import cmd

            cmd.Git().ls_remote(path)
            exists = True
        except:
            pass
        if exists:
            if not "https://" in path and not "git@" in path:
                # Only raise an exception if https://  or git@ is not in the path. If https:// or
                # git@ is in the path we expect the module to exist, and will not try to re-create
                # it downstream.
                raise yam_exception.YamException(
                    "Git repo for the '{m}' module already exists at {r}".format(m=module_name, r=path)
                )

        # No need for this anymore, as we are doing it with the try/catch above. The try/except above
        # should work with local modules and modules using the git daemon.
        # repo_path = Path(path)
        # if repo_path.exists():
        #     raise yam_exception.YamException(
        #         "Git repo for the '{m}' module already exists at {r}".format(m=module_name, r=repo_path.absolute())
        #     )
        # os.mkdir(path)
        # repo_path.mkdir(parents=True)
        # assert os.path.isdir(path)

        # print('MMMM', path)
        # create_git_repo(repo_path, bare=bare)
        # main_branch_url = os.path.join(release_directory , module_name)

        # Create or use SSH to initialize a bare git repo
        repo_path = Path("{r}/{name}".format(r=self._temp_dir.name, name=module_name))
        dark = str(vcs_root)
        ind = dark.find("jpl.nasa.gov") + 12
        module_storage_area = dark[ind:]
        create_git_repo(repo_path, path, module_storage_area, module_name, bare=bare)

        # Get a local copy of that repo
        repo = Repo(repo_path, search_parent_directories=True)
        self.repo = repo

        # apply the module name as a tag so we can recover it for main trunk checkouts
        # repo.git.tag(module_name)

        # print('NNN', os.system(f'git -P -C {path} status'))

        """
        repo = Repo(main_branch_url)
        self.__revision_control_system.repo = repo
        #main_branch_url should be path to gitrepo
        revision_tag = "R1-00"
        create_and_commit_basic_module_files_git(
            url=main_branch_url,
            module_name=module_name,
            file_system=self.__file_system,
            build_system=self.__build_system,
            revision_control_system=self.__revision_control_system,
        )
        """
        assert os.path.isdir(repo_path)

    def create_and_commit_basic_module_files(self, vcs_root, module_name, file_system, build_system, bare):

        from pathlib import Path

        repoPath = "{r}/{name}".format(r=vcs_root, name=module_name)
        if bare:
            from git import Repo

            path = file_system.create_temporary_directory()
            # check out the empty repo so we can add files to it
            # print('REPO=', repoPath, 'tmppath=', path)
            self.repo = Repo.clone_from(repoPath, path)

            # Create main branch or switch to it if it already exists
            branches = _get_branches_and_tags(self.repo)
            if "main" in branches:
                # Swtich to branch if it already exists
                self.repo.git.checkout("main")
            else:
                # Create a new branch
                self.repo.git.checkout("-b", "main")
        else:
            path = "{r}/{name}".format(r=vcs_root, name=module_name)
            path = repoPath

        build_system.create_module_files(module_name=module_name, module_path=path)
        log_message = "pyam: Add initial files"
        if bare:
            # use the working path repo to do the commit
            from git import Repo

            wmrepo = Repo(path)
            for i in ["ChangeLog", "Makefile", "Makefile.yam", "ReleaseNotes", "YamVersion.h"]:
                # self.add_file(i)
                wmrepo.git.add(i)
            wmrepo.index.commit(log_message)
            self.repo.git.push("--set-upstream", "origin", "main")
            wmrepo.git.push()
            # self.check_in(path=None, log_message="pyam: Add initial files")
        else:
            self.add_file(path)

            # dont need to pass path for git because the repo object knows what repo to commit
            self.check_in(path=None, log_message=log_message)

        revision_tag = f"{module_name}-R1-00"
        ###self.tag_git_module(module_name, revision_tag)
        # module_saving_utils.tag_git_module(self.repo, revision_tag)

        if not bare:
            branch_off = "main"  # destination_url.repoReleaseTag()
            new_branch = revision_tag
            self.repo.git.branch(new_branch, branch_off)

        # git = Repo(path).git
        # git.switch(revision_tag)

        return path

    def url(self, path):
        """GIT implementation of revision_control_system.url()."""
        # return pathlib.PurePath(path)
        return os.path.basename(os.path.normpath(path))

    def isConsistent(self, path, expected_data: revision_control_system.ModuleBranchData):
        """
        Return True if the checked out path's branch/tag is consistent with
        the expected data.
        """
        # print("VVVVV")
        # print('CCCC', path, expected_data.dumpStr())
        # os.system(f'ls {path}')
        if expected_data._branch_id:
            curr_branch = Repo(path).git.branch(show_current=True)
            return curr_branch == expected_data.repoBranchTag()
            # print(expected_data.repoBranchTag())
            # return False

        if not expected_data._branch_id:  # and curr_branch != expected_data.repoReleaseTag():
            # check for main trunk
            # print('BBBBB2', path)
            if expected_data._release_tag == "main":
                # print('BBBB3')
                return self.isMainTrunkCheckout(path)

            # check that the release tags match
            latest_tag = Repo(path).git.describe(tags=True)
            return latest_tag == expected_data._full_tag

            # return False
            # print(expected_data.repoReleaseTag())
            # return False
        # if not os.path.basename(os.path.normpath(path)) == os.path.basename(os.path.normpath(expected_data.repoPath())):
        #    return False
        # return True
        assert 0

    def hasMainTrunkCommits(self, tagged_module_data: revision_control_system.ModuleBranchData):
        """
        Get difference between current commit and tip of the main branch.
        """

        # This repo is from a tagged work module, so it's depth=1. Therefore,
        # we can't just do `git diff main`, since we are not on a branch and
        # main will not appear in `git branch -a`. What we do instead is fetch
        # the tip of the main branch, which will be saved temporarily as
        # FETCH_HEAD. Then, we do a diff between HEAD and FETCH_HEAD, which will
        # effectively check for new main trunk commits that are newer than the
        # current HEAD location.
        self.repo = Repo(tagged_module_data._module_path)
        self.repo.git.fetch("--depth=1", "origin", "main")
        diffs = self.repo.git.diff("HEAD", "FETCH_HEAD", name_only=True)
        if diffs:
            module_name = tagged_module_data._module_name
            tag = tagged_module_data._release_tag
            msg = f"Module '{module_name}' has main branch commits - latest git release tag is {tag}"
            from . import savable_module

            raise savable_module.PreSaveException(msg)

    def getPathModuleData(self, wm_path: str) -> revision_control_system.ModuleBranchData:
        git = Repo(wm_path).git
        # This gives us just the name of just the branch we are on
        branch = git.rev_parse("HEAD", abbrev_ref=True)
        # check if we are a tagged repo, in which case we use tags to find branch info
        if self.isTaggedCheckout(wm_path):
            # the last tag is the most recent, which is the one we are on
            split_tag = git.describe(tags=True).split("-")
            module_name = split_tag[0]
            rev_tag = "-".join(split_tag[1:])
            branch_id = None

            # brname = Repo(wm_path).git.rev_parse("HEAD", abbrev_ref=True)
            # split_tag = brname.split("-")
            # module_name = git.tag()[-1]

        elif self.isMainTrunkCheckout(wm_path):
            #  if we are a main
            # branch_id = "main"
            branch_id = None
            # print("TTT TAGS")
            # print(git.describe(tags=True))
            split_tag = git.describe(tags=True).split("-")
            module_name = split_tag[0]
            # rev_tag = '-'.join(split_tag[1:])
            rev_tag = "main"
        else:
            # its a branched checkout
            # print('NNN', branch)
            branch = branch.split("-")
            module_name, rev_tag, branch_id = branch[0], "-".join(branch[1:3]), "-".join(branch[3:])
        #         print("KKKK")
        #         print(wm_path)
        #         print("RRR")
        #         print(Repo(wm_path).git.remote("-v"))

        root = Repo(wm_path).git.remote("get-url", "origin")
        root = root.rsplit("/", 1)[0]
        # Using rsplit here rather than Path, because Path gets rid of the "//" used by
        # https://... repos
        # root = Path(root).parents[0]
        #         print("PPP")
        #         print(root)
        # print(root[1])
        data = revision_control_system.ModuleBranchData(
            module_name=module_name,
            vcs_type="git",
            # USE remote -v for vcs_root
            # TODO CHANGE
            vcs_root=root,  # database_reader.module_repository_url(module_name),
            release_tag=rev_tag,
            branch_id=branch_id,
            dead_branch=False,
        )
        return data

    def isTaggedCheckout(self, wm_path):
        # rev-parse returns HEAD if we are not on a branch, which is the case if it is a tagged checkout

        brname = Repo(wm_path).git.rev_parse("HEAD", abbrev_ref=True)
        return brname == "HEAD"

        # get the branch name
        # print('CHK TAGG', brname)
        # return Repo(wm_path).git.rev_parse("HEAD", abbrev_ref=True) == "HEAD"

    def isMainTrunkCheckout(self, wm_path):
        curr_branch = Repo(wm_path).git.branch(show_current=True)
        return curr_branch == "main"

        """
        brname =  Repo(wm_path).git.rev_parse("HEAD", abbrev_ref=True)
        #print('CHK MAN', brname)
        return brname == 'main'
        #return Repo(wm_path).git.rev_parse("HEAD", abbrev_ref=True) == "main"
        """

    def uncommitted_files(self, path):
        """GIT implementation of uncommitted_files()."""
        # Uncommited means that the files were tracked at one point (ie. git add was done one them)
        # to check for this I use "git diff" to see if there are any unstaged changes
        # (meaning a tracked file is modified but not added)
        # and I also use "git diff --staged" to check for files that are added, but not committed
        # if there's a way to check for both in one command we can use that instead
        git = Repo(path).git
        unstaged = git.diff(name_only=True)
        staged = git.diff(staged=True, name_only=True)
        # print("DIFFS for uncommited files:")
        # print(unstaged)
        # print(staged)
        return unstaged + staged

    def generate_logs_since_last_branch(self, path, ignored_paths=()):
        """GIT implementation of generate_logs_since_last_branch()."""
        # return "dummy logs since last branch"
        # return f"{new_revision_tag} {date_time.ctime()} PLACEHOLDER BRANCH CHANGELOG\n"
        mod_data = self.getPathModuleData(wm_path=path)
        assert mod_data._branch_id
        # repo = Repo(path)
        # logs = repo.git.log()
        # print('LLLL', logs)
        last_release_tag = mod_data.release_tag()
        branch_tag = mod_data.repoBranchTag()

        repo = Repo(path)
        local_branches = _get_branches_and_tags(repo, local_only=True)
        if last_release_tag in local_branches:
            b1 = last_release_tag
        else:
            b1 = "remotes/origin/" + last_release_tag
        if branch_tag in local_branches:
            b2 = branch_tag
        else:
            b2 = "remotes/origin/" + branch_tag

        logs = repo.git.log(f"{b1}..{b2}")

        return logs
        # return f"PLACEHOLDER BRANCH CHANGELOG\n"

    def generate_logs_since_divergence(
        self,
        path,
        tagged_url: revision_control_system.ModuleBranchData,
        # path_url : revision_control_system.ModuleBranchData =None,
        ignored_paths=(),
    ):
        """GIT implementation of generate_logs_since_divergence()."""
        # assert 0
        # return "dummy logs since divergence"
        # return f"{tagged_url.release_tag()} {date_time.ctime()} PLACEHOLDER DIVERGENCE CHANGELOG\n"
        #  return f"{tagged_url.release_tag()}  PLACEHOLDER DIVERGENCE CHANGELOG\n"
        repo = Repo(path)
        last_release_tag = tagged_url.release_tag()
        local_branches = _get_branches_and_tags(repo, local_only=True)
        if last_release_tag in local_branches:
            b1 = last_release_tag
        else:
            b1 = "remotes/origin/" + last_release_tag
        if "main" in local_branches:
            b2 = "main"
        else:
            b2 = "remotes/origin/main"
        logs = repo.git.log(f"{b1}..{b2}")
        return logs

    def generate_diff(
        self,
        from_data: revision_control_system.ModuleBranchData,
        to_data: revision_control_system.ModuleBranchData = None,
        path: str = "",
        ignored_paths=(),  # to_url,
    ):
        """GIT implementation of revision_control_system.generate_diff()."""
        # FROM_URL is the branch name
        # to_url = self._revision_control_system.url(path)
        # print("YYYY")
        # print(from_data)
        # print(path)
        # ensure that one, and only one, or path and to_data are defined
        assert not (path and to_data)
        assert path or to_data

        if path:
            branch_name = Repo(path).git.branch(show_current=True)
            repo = Repo(path)
        else:
            branch_name = to_data._full_tag
            repo = self.repo

        # Run fetch to get any new branches or tags
        repo.git.fetch()

        if branch_name != "main":
            # print('GGG1', path, f"{from_data._full_tag}..{branch_name}")
            # need to specify remotes/origin/ when branch is a remote-only branch
            local_branches = _get_branches_and_tags(repo, local_only=True)
            if from_data._full_tag in local_branches:
                b1 = from_data._full_tag
            else:
                b1 = "remotes/origin/" + from_data._full_tag
            if branch_name in local_branches:
                b2 = branch_name
            else:
                b2 = "remotes/origin/" + branch_name
            diff = repo.git.diff(f"{b1}..{b2}")
        else:
            last_release_tag = from_data.release_tag()
            local_branches = _get_branches_and_tags(repo, local_only=True)
            if last_release_tag in local_branches:
                b1 = last_release_tag
            else:
                b1 = "remotes/origin/" + last_release_tag
            if "main" in local_branches:
                b2 = "main"
            else:
                b2 = "remotes/origin/main"
            diff = repo.git.diff(f"{b1}..{b2}")
        #         ("GEN DIFF:")
        #         print(diff)
        return diff

    def has_modificationsOBSOLETE(self, from_url, to_url):
        """GIT implementation of has_modifications()."""
        pass

    def modified_paths_since_divergence(self, path, tagged_url: revision_control_system.ModuleBranchData):
        """GIT implementation of modified_paths_since_divergence()."""
        # Here, tagged_url is actually the branch name.
        # print("PATHS FOR DIFFING")
        # print(path)
        # print(tagged_url)
        branch_name = Repo(path).git.branch(show_current=True)
        repo = Repo(path)

        # Need to fetch so we have the tags locally. We can't do diffs against a remote tag.
        repo.git.fetch()

        # print('MMMM', branch_name, tagged_url._full_tag)
        if branch_name != "main":
            # print('GGG3', path, f"{tagged_url._full_tag}..{branch_name}")
            # diff=self.repo.git.diff(f"{branch_name}..{tagged_url._full_tag}", name_only=True)
            # self.repo.git.fetch("origin", branch_name)
            # self.repo.git.fetch("origin", tagged_url._full_tag)

            # need to use origin/ prefix to branch name in a remote repo
            # per
            # https://stackoverflow.com/questions/33152725/git-diff-gives-ambigious-argument-error

            # need to specify remotes/origin/ when branch is a remote-only branch
            local_branches = _get_branches_and_tags(repo, local_only=True)
            if tagged_url._full_tag in local_branches:
                b1 = tagged_url._full_tag
            else:
                b1 = "remotes/origin/" + tagged_url._full_tag
            if branch_name in local_branches:
                b2 = branch_name
            else:
                b2 = "remotes/origin/" + branch_name
            diff = repo.git.diff(f"{b1}..{b2}")
            # diff = self.repo.git.diff(f"origin..{branch_name}", name_only=True)
        else:
            last_release_tag = tagged_url.release_tag()
            local_branches = _get_branches_and_tags(repo, local_only=True)
            if last_release_tag in local_branches:
                b1 = last_release_tag
            else:
                b1 = "remotes/origin/" + last_release_tag
            if "main" in local_branches:
                b2 = "main"
            else:
                b2 = "remotes/origin/main"
            diff = repo.git.diff(f"{b1}..{b2}", "--name-only")
            # print('GGG4', f'refs/heads/{last_release_tag}..refs/heads/main')
        # diff=self.repo.git.diff(f"{tagged_url.repoBranchTag()}..{tagged_url._release_tag}", name_only=True)
        #         print("DIFF FILE NAMES for remote and changes")
        #         print(diff)

        # Return diff as a list. Really, the svn version does a list of paths. We could implement that in the future
        # but at least this way the string stays intact and doesn't get split up into individual characters.
        return diff.split("\n")

    def add_file(self, path=None):
        """Git implementation of revision_control_system.add_file().
        NOTE: Abstract Class says that it should error if already added. Currently doesn't.
        """
        git = self.repo.git
        # if not self.is_git_repo(git):
        #    raise Exception("Can not add, given repo is not initialized")
        git.add(path)

    def is_git_repo(self, git):
        """Check if the given git object is a repo or not. Just check if any simple
        Git command works"""
        # print("CHECKING IF GIT REPO")
        try:
            log = git.status()
        except git.exc.GitCommandError:
            return False
        return True
        # return git.rev_parse("--is-inside-work-tree")
        # git rev-parse --is-inside-work-tree

    def list_files(self, path):
        """GIT implementation of revision_control_system.list_files()."""
        git = Repo(path).git
        # print("BRANCHES: ", git.branch())
        # print("PATH ", path)
        if not self.is_git_repo(git) or "main" not in git.branch():
            # if we are not in a git repo
            # or there is no main branch in the repo (like when we want to list files of a tagged module)
            # we use this because ls_tree only works in git modules
            return os.listdir(path)
        return git.ls_tree("-r", "main", "--name-only")
        # print("FILES UNDER GIT: ", files)
        # return files

    def _raise_exception_on_non_working_copy(self, path):
        """Raise NotAWorkingCopyException if path is not a working copy."""
        if not self.working_copy_exists(path=path):
            raise revision_control_system.NotAWorkingCopyException(path=path)

    def _reintegrate(self, client, url_or_path, revision, local_path):
        """Merge-reintegrate into a branch."""
        pass

    def _log(
        self,
        client,
        url_or_path,
        revision_start=pysvn.Revision(pysvn.opt_revision_kind.head),
        revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, 0),
        discover_changed_paths=False,
        strict_node_history=True,
        include_merged_revisions=False,
    ):
        """Return GIT log."""
        pass

    def _client(self):
        pass


# def getBranchReference(repo, brname):
#     """
#     Return the branch reference
#     """
#     branches = [x for x in repo.branches if x.name == brname]
#     assert len(branches) == 1
#     return branches[0]


def module_repo_path(module_branch_data: revision_control_system.ModuleBranchData):
    """
    Return the path to the repo
    """
    return "{root}/{name}".format(root=module_branch_data._vcs_root, name=module_branch_data._module_name)


def _format_log(log, common_path, ignored_paths, earliest_revision_number=None):
    """Return a string representing the log entry.

    path_url will be removed from the paths. Empty string will be
    returned for logs with only ignored paths.

    """
    changes = []
    for c in log.changed_paths:
        relative_path = _relative_path(c, common_path=common_path)
        if relative_path in ignored_paths:
            continue
        elif log.revision.number == earliest_revision_number and c.copyfrom_path:
            # Ignore the log of the branch being made
            pass
        else:
            changes.append("  {action} {path}".format(action=c.action, path=relative_path))

    if changes:
        upper_text = module_saving_utils.format_message(log["message"])
        upper_text = upper_text + "\n\n  " if upper_text else ""
        upper_text += "SVN revision: {svn_rev}".format(svn_rev=log.revision.number)

        return """* {upper_text}
{changes}""".format(
            upper_text=upper_text, changes="\n".join(changes)
        ).strip()
    else:
        return ""


def create_git_repo(git_repo_path, path, module_storage_area: str, module_name: str, bare):
    # bare = True
    if "ssh://" in str(path):
        # This repo is going to be remote. Create it using SSH
        import subprocess

        if bare:
            ssh_cmd = f'ssh einstein.jpl.nasa.gov "(cd {module_storage_area}; git init --shared --initial-branch=main --bare {module_name}.git)"'
        else:
            ssh_cmd = f'ssh einstein.jpl.nasa.gov "(cd {module_storage_area}; git init --shared --initial-branch=main {module_name})"'

        # Commenting line below as it was deemded as high risk. Uncomment at your own discretion.
        # subprocess.Popen(ssh_cmd, shell=True).wait()

        repo = Repo.clone_from(path, git_repo_path)
    elif "https://" in str(path) or "git@" in str(path) or "jpl.nasa.gov" in str(path):
        # This repo has already been initialized elsewhere.
        repo = Repo.clone_from(path, git_repo_path)
    else:
        # Create the repo at the path given
        Repo.init(path, initial_branch="main", bare=bare)
        repo = Repo.clone_from(path, git_repo_path)
    if not bare:
        repo.git.add(str(git_repo_path) + "/.")
        repo.index.commit("Initial Commit for Register New Module Test")
        repo.git.push()

    # print("Done initializing repo")
    # repo.git.config('receive.denyCurrentBranch'='updateInstead')

    if not bare:
        # we need the following since we are not using a bare
        # repository, and we want to be able to push from main
        # branch. See
        # https://stackoverflow.com/questions/11117823/git-push-error-refusing-to-update-checked-out-branch
        cwriter = repo.config_writer("global")
        # cwriter.set_value('core', 'fileMode', 'false')
        cwriter.set_value("receive", "denyCurrentBranch", "updateInstead")

        cwriter.release()


def _relative_path(svn_log_change, common_path):
    """Return path relative to common_path."""
    pass


def _emulated_reintegrate(client, url_or_path, revision, local_path):
    """Reintegration merge for older SVN servers (<1.5).

    This is emulating,

    merge_reintegrate(url_or_path,
                      revision,
                      local_path)

    """
    pass


def _earliest_revision(logs):
    """Return earliest revision in logs."""
    pass


@contextlib.contextmanager
def _progress_context_manager(progress_callback, client):
    """Manage progress callback.

    We call it a final time when the transfer is complete.

    """
    # Must be a list for callback to be able to mutate the value
    interrupted = [False]

    def cancel(_, __):
        """Called by interrupt signal."""
        interrupted[0] = True

    def cancel_called():
        """Return True if cancel was called."""
        return interrupted[0]

    # Must handle signal directly for PySVN to properly cancel procedure
    old_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, cancel)
    client.callback_cancel = cancel_called
    print_time_last = [None]

    try:
        if progress_callback:
            try:
                # There is no point accessing the total bytes since SVN
                # seems to never know this and always reports -1. Note
                # that pysvn.callback_progress is undocumented. Careful
                client.callback_progress = lambda current, _: progress_callback(current, print_time_last)
                yield
            finally:
                client.callback_progress = None
                if not interrupted[0]:
                    # done
                    progress_callback()
        else:
            yield
    finally:
        client.callback_cancel = None
        signal.signal(signal.SIGINT, old_handler)

        if interrupted[0]:
            raise KeyboardInterrupt


def _create_tag(repo: Repo, tag: str, message: Optional[str] = None):
    """
    Create an annotated tag for the repo. The message used for the tag is
    given by the optional message keyword. If none is given, then the message
    will be:

    Tag for {tag} release.

    Parameters
    ----------
    repo : Repo
        Repo to add the tag to.
    tag : str
        Name of the annotated tag.
    message : Optional[str]
        Message for the annotated tag.
    """
    if not message:
        message = f"Tag for {tag} release."

    repo.git.tag("-a", tag, "-m", message)
    repo.git.push("origin", tag)


def _get_current_branch(repo: Repo) -> str:
    """
    Returns the current branch of the repo.

    Parameters
    ----------
    repo : Repo
        Git repo

    Returns
    -------
    str
        Current branch name.
    """
    local_branches = repo.git.branch().split("\n")
    for b in local_branches:
        if "*" in b:
            return b.replace("*", "").split()

    raise ValueError("Could not find current branch of repo.")


def _fetch_branch(repo: Repo, branch: str) -> None:
    """
    Pull branch from remote if it does not exist locally.

    Parameters
    ----------
    repo : Repo
        Git repo
    branch : str
        Branch
    """

    branches = _get_branches_and_tags(repo, local_only=True)
    if branch not in branches:
        repo.git.fetch()
        repo.git.branch(branch, "origin/" + branch)


def _get_branches_and_tags(
    repo: Repo, local_only: bool = False, remote_only: bool = False, include_tags: bool = True
) -> Set[str]:
    """
    Get the local and remote branches and tags of a git repo. Note,
    remote branches will have the "remotes/origin/" removed.

    Parameters
    ----------
    repo : Repo
        Repo to check the branches of.
    local_only : bool, optional
        Return only local branch names. (Default value = False)
    remote_only : bool, optional
        Return only remote branch names. (Default value = False)
    include_tags : bool, optional
        Include tag names in the return values. (Default value = True)

    Returns
    -------
    Set[str]
        A set containing all of the branch names and (optionally) tag names.
    """

    if local_only and remote_only:
        raise ValueError("Cannot specify local_only and remote_only in _get_branches_and_tags.")
    if local_only:
        branch_str = repo.git.branch()
    elif remote_only:
        branch_str = repo.git.branch("-r")
    else:
        branch_str = repo.git.branch("-a")
    if include_tags:
        branch_str += "\n" + repo.git.tag()
    branches = {
        x.replace("origin/", "").replace("remotes/", "").replace("*", "").replace("->", "").strip()
        for x in branch_str.split("\n")
    }
    branches.discard("")
    return branches


def _rename_branch(repo: Repo, old_name: str, new_name: str):
    if old_name not in _get_branches_and_tags(repo, local_only=True):
        # Checkout the old branch if it does not exist
        curr_branch = _get_current_branch(repo)
        repo.git.switch(old_name)
        repo.git.switch(curr_branch)

    repo.git.branch("-m", old_name, new_name)
    repo.git.push("-u", "origin", new_name)
    if old_name in _get_branches_and_tags(repo, remote_only=True):
        repo.git.push("origin", "--delete", old_name)


def decode(byte_string, fallback, encodings=("utf-8", "latin-1")):
    """Guess encoding and return Unicode."""
    if not isinstance(byte_string, bytes):
        return byte_string

    for encoding in encodings:
        try:
            return byte_string.decode(encoding)
        except UnicodeError:
            pass

    return fallback


_default_commit_message = "pyam: Default commit message"
