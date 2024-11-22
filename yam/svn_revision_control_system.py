"""Contains an SVN implementation of the RevisionControlSystem class."""

from __future__ import absolute_import

import contextlib
import re
import signal
import sys
import tempfile
from typing import Optional

from . import pysvn_verbose as pysvn
from . import revision_control_system
from . import module_saving_utils
from . import yam_exception
from . import yam_log


class SVNRevisionControlSystem(revision_control_system.RevisionControlSystem):
    """An SVN implementation of the RevisionControlSystem class."""

    def __init__(
        self,
        username,
        login_callback,
        trust_ssl_server_callback,
        use_merge_info=True,
        progress_callback=None,
    ):
        """Create an instance of svn_revision_control_system.

        username can be set to None to use the default username.

        login_callback is a callback for retrieving login information if
        such information is required. The callback takes as parameters
        (realm, username, may_save). It needs to return
        (retcode, username, password, save). See pysvn documentation
        for details. Set login_callback to None to disable it.

        trust_ssl_server_callback is called when SVN is unsure about trusting
        a server's SSL certificate. The callback takes a dictionary called
        trust_dict as input and returns (retcode, accepted_failures, save).
        See pysvn documentation for more details.

        If use_merge_info is True, we use SVN's newer merge tracking
        capability. This should be set to False when dealing with SVN servers
        older than version 1.5.

        progress_callback is called when data transfer occurs. The function has
        two parameters. The first is the number of bytes transferred. The
        second parameter is a boolean that indicates transfer completion when
        True. Set progress_callback to None to disable it.

        """
        revision_control_system.RevisionControlSystem.__init__(self)

        # NOTE: Do not store a pysvn.Client as an attribute. Some versions of
        #       pysvn are buggy and do strange things if the Client is used
        #       for more than one check-out command.
        self.__username = username
        self.__login_callback = login_callback
        self.__trust_ssl_server_callback = trust_ssl_server_callback
        self.__use_merge_info = use_merge_info

        # We only enable this for particular calls via
        # _progress_context_manager().
        self.__progress_callback = progress_callback

        self.vcs = "svn"

    def _pkg_check_out(self, source: str, target: str):
        """SVN implementation of revision_control_system._check_out()."""
        self.__check_out(source, target)

    def __check_out(self, source: str, target: str):
        """SVN implementation of revision_control_system._check_out()."""
        client = self._client()

        # Validate to avoid Subversion bug.
        # http://subversion.tigris.org/issues/show_bug.cgi?id=4099
        # print('YYY', source)
        if not client.is_url(source):
            raise yam_exception.YamException("Not a valid Subversion URL: '{source}'".format(source=source))

        with _progress_context_manager(self.__progress_callback, client):
            try:
                yam_log.say("SVN checkout of {} ".format(source) + " into {}".format(target))
                client.checkout(url=source, path=target)
            except pysvn.ClientError as error:
                raise yam_exception.YamException(
                    "Could not check out '{source}'; {error}".format(source=source, error=error)
                )

    def module_check_out(self, source: revision_control_system.ModuleBranchData, target: str):
        """SVN implementation of revision_control_system.module_check_out()."""
        # self._check_out(source.uri(), target)
        self.__check_out(svn_uri(source), target)

    def export_file(self, source, target):
        """SVN implementation of revision_control_system.check_out()."""
        client = self._client()

        # Validate to avoid Subversion bug.
        # http://subversion.tigris.org/issues/show_bug.cgi?id=4099
        if not client.is_url(source):
            raise yam_exception.YamException("Not a valid Subversion URL: '{source}'".format(source=source))

        with _progress_context_manager(self.__progress_callback, client):
            try:
                yam_log.say("SVN checkout of {} ".format(source) + " into {}".format(target))
                client.export(src_url_or_path=source, dest_path=target)
            except pysvn.ClientError as error:
                raise yam_exception.YamException(
                    "Could not check out '{source}'; {error}".format(source=source, error=error)
                )

    def check_in(self, path, log_message, wmpath=""):
        """SVN implementation of revision_control_system.check_in()."""
        client = self._client()
        with _progress_context_manager(self.__progress_callback, client):
            try:
                yam_log.say("SVN checkin of {} ".format(path))
                client.checkin(path=path, log_message=log_message)
            except pysvn.ClientError as error:
                raise yam_exception.YamException("Could not commit '{path}'; {error}".format(path=path, error=error))

    def make_directory(self, path):
        """SVN implementation of revision_control_system.make_directory()."""
        client = self._client()
        try:
            yam_log.say("SVN mkdir for {} ".format(path))
            client.mkdir(url_or_path=path, log_message="", make_parents=True)
        except pysvn.ClientError as exception:
            # Unfortunately, pysvn doesn't have finer-grained exceptions. Thus
            # we use this abomination.
            message = str(exception)
            del exception

            if message.lower().strip().endswith("permission denied"):
                raise revision_control_system.PermissionException(message)
            else:
                raise revision_control_system.DirectoryAlreadyExists(path_or_url=path)

    def update(self, path):
        """SVN implementation of revision_control_system.update()."""
        path = path._module_path
        client = self._client()
        with _progress_context_manager(self.__progress_callback, client):
            try:
                yam_log.say("Running SVN update for {} ".format(path))
                client.update(path=path)
            except pysvn.ClientError:  # pragma: NO COVER
                # Subversion < 1.7 raises exception on conflict.
                pass

    def working_copy_exists(self, path):
        """SVN implementation of working_copy_exists()."""
        try:
            yam_log.say("Checking SVN whether {} path exists".format(path))
            yam_log.say("Checking SVN status of {} path".format(path))
            if len(self._client().status(path=path, recurse=False)) <= 0:
                return False

            # Under pysvn 1.7.10, this happens when the path is not a working
            # directory.
            yam_log.say("Getting svn info for {} path".format(path))
            entry = self._client().info(path)
            return bool(entry)
        except pysvn.ClientError:
            return False
        except SystemError:  # pragma: NO COVER
            raise yam_exception.YamException("Working copy '{}' is incomplete; " "try removing it first".format(path))

    def branch(
        self,
        source_url: revision_control_system.ModuleBranchData,
        destination_url: revision_control_system.ModuleBranchData,
    ):
        """SVN implementation of revision_control_system.branch()."""
        surl = svn_uri(source_url)
        durl = svn_uri(destination_url)
        self._branch_uri(surl, durl)

    def _branch_uri(self, source_url: str, destination_url: str):
        """SVN implementation of revision_control_system.branch()."""
        surl = source_url
        durl = destination_url
        try:
            yam_log.say("SVN copy of {} url ".format(surl) + " {} url".format(durl))
            self._client().copy(src_url_or_path=surl, dest_url_or_path=durl)
        except pysvn.ClientError as exception:  # pragma: NO COVER
            # pragma: NO COVER
            raise yam_exception.YamException(str(exception))

    def _switch_to_branch_uri(self, path, branch_url: str):
        """SVN implementation of revision_control_system.switch_to_branch()."""
        try:
            yam_log.say("Switching {} path ".format(path) + " to {} branch".format(branch_url))
            client = self._client()
            client.switch(path=path, url=branch_url)
            client.update(path=path)
        except pysvn.ClientError as exception:  # pragma: NO COVER
            # pragma: NO COVER
            raise yam_exception.YamException(str(exception))

    def switch_to_branch(self, path: str, branch_url: revision_control_system.ModuleBranchData):
        """SVN implementation of revision_control_system.switch_to_branch()."""
        self._switch_to_branch_uri(path, svn_uri(branch_url))

    def switch_to_tag(self, path: str, tag_url: revision_control_system.ModuleBranchData):
        self.switch_to_branch(path, tag_url)

    def reintegrate(
        self,
        path,
        target_data: revision_control_system.ModuleBranchData,
        archive_data: revision_control_system.ModuleBranchData,
    ):
        """SVN implementation of revision_control_system.merge()."""

        # Remember URL of path for merging
        target_url = svn_uri(target_data)
        archive_url = svn_uri(archive_data)
        branch_url = self.url(path)

        client = self._client()

        error_message = ""
        try:
            # Switch path to be on target_url's branch
            client.switch(path=path, url=target_url)
        except pysvn.ClientError as error:  # pragma: NO COVER
            # SVN < 1.7 raises exception on conflict.
            yam_log.say("switch failed: {}".format(error))
            error_message = str(error)  # pragma: NO COVER

        # Newer SVN (ones that use merge_info) are able to handle unversioned
        # files in merges; and they barf appropriately, as needed. Older SVN are
        # confused more easily, so we manually check for uncommitted files. This
        # check is overly draconian, and wil barf even for benign unversioned
        # files. But this is only for ancient SVN, so that's fine
        if not self.__use_merge_info:
            uncommitted_filenames = self.uncommitted_files(path)
            if uncommitted_filenames:
                error_message = "Conflict during switch for {files}".format(files=uncommitted_filenames)

        if error_message:
            try:
                # Rollback the switch we did before
                client.switch(path=path, url=branch_url)
            except pysvn.ClientError:  # pragma: NO COVER
                # Give up if we can't switch back
                pass  # pragma: NO COVER

            raise revision_control_system.ReintegrationException(message="Merge canceled; {e}".format(e=error_message))

        with _progress_context_manager(self.__progress_callback, client):
            try:
                self._reintegrate(
                    client=client,
                    url_or_path=branch_url,
                    revision=pysvn.Revision(pysvn.opt_revision_kind.head),
                    local_path=path,
                )
            except pysvn.ClientError as error:  # pragma: NO COVER
                yam_log.say("Merge failed: {}. Do you have uncommitted files in a renamed directory?".format(error))
                client.switch(path=path, url=branch_url)
                raise revision_control_system.ReintegrationException(
                    message="Merge canceled; {e}".format(e=error)
                )  # pragma: NO COVER

        try:
            # Move branch_url to archive_url to mark it dead
            client.move(src_url_or_path=branch_url, dest_url_or_path=archive_url)

            client.update(path=path)
        except pysvn.ClientError as exception:  # pragma: NO COVER
            # pragma: NO COVER
            raise yam_exception.YamException(str(exception))

    def markBranchDead(self, wmpath: str):
        pass

    def tag(
        self,
        destination_url: revision_control_system.ModuleBranchData,
        message: Optional[str] = None,
        path: Optional[str] = None,
    ):
        raise ValueError("This method should never be called for SVN.")

    def exists_module_branch(self, module_branch_data: revision_control_system.ModuleBranchData):
        """SVN implementation of revision_control_system.exists_module_branch()."""
        uri = svn_uri(module_branch_data)
        return self._exists(url=uri)

    def _exists(self, url: str):
        """SVN implementation of revision_control_system.exists()."""
        # uri = module_branch_data.uri()
        try:
            yam_log.say("Checking SVN that {} url exists ".format(url))
            self._client().list(url_or_path=url, recurse=False)
            return True
        except pysvn.ClientError:
            return False

    def url(self, path):
        """SVN implementation of revision_control_system.url()."""
        self._raise_exception_on_non_working_copy(path)

        yam_log.say("Getting SVN info for {} path ".format(path))
        entry = self._client().info(path)
        return entry.url

    def getPathModuleData(self, wm_path: str):
        """
        Create and return the ModuleBranchData for this checked out area.
        """
        import os.path

        # module_name = os.path.basename(wm_path)
        # verify that the path points to the top level of a module under src
        assert os.path.basename(os.path.dirname(wm_path)) == "src"

        wm_uri = self.url(wm_path)

        wm_parent_uri = os.path.dirname(wm_uri)
        branch_id = None
        dead_flag = False
        # print('KKKK1', wm_uri)
        if os.path.basename(wm_uri) == "trunk":
            # on the main trunk
            module_name = os.path.basename(wm_parent_uri)
            release_tag = "main"
            vcs_root = os.path.dirname(os.path.dirname(wm_parent_uri))
        else:
            categ = os.path.basename(wm_parent_uri)
            module_name = os.path.basename(os.path.dirname(wm_parent_uri))
            repo_tag = os.path.basename(wm_uri)
            vcs_root = os.path.dirname(os.path.dirname(os.path.dirname(wm_parent_uri)))
            from . import revision_tag_utils

            mod, release_tag, branch_id = revision_tag_utils.repotag_to_release_branch(repo_tag)
            assert mod == module_name
            # print('KKKK1', categ, wm_parent_uri)
            if categ in ["featureBranches", "deadBranches"]:
                # extract the branch
                assert branch_id
                if categ == "deadBranches":
                    dead_flag = True
            elif categ == "releases":
                # extract release tag
                pass
            else:
                assert 0
        module_branch_data = revision_control_system.ModuleBranchData(
            module_name=module_name,
            release_tag=release_tag,
            branch_id=branch_id,
            vcs_type="svn",
            vcs_root=vcs_root,
            dead_branch=dead_flag,
        )
        return module_branch_data

    def isTaggedCheckout(self, wm_path):

        wm_url = self.url(wm_path)
        # strip out the release tag from the url
        import os.path

        wm_url_parent = os.path.dirname(wm_url)

        # if the tail of wm_url_parent is 'releases' then this is a
        # tagged checkout
        return os.path.basename(wm_url_parent) == "releases"

    def isMainTrunkCheckout(self, wm_path):

        wm_url = self.url(wm_path)
        # strip out the release tag from the url
        import os.path

        # wm_url_parent = os.path.dirname(wm_url)

        # if the tail of wm_url_parent is 'trunk' then this is a
        # tagged checkout
        return os.path.basename(wm_url) == "trunk"

    def hasMainTrunkCommits(self, tagged_module_data: revision_control_system.ModuleBranchData):

        module_name = tagged_module_data._module_name
        tag = tagged_module_data._release_tag
        # expecting tagged module data
        assert tag
        assert not tagged_module_data._branch_id

        branch_url = svn_uri(tagged_module_data)
        trunk_url = svn_uri(tagged_module_data.with_release_tag("main"))
        pysvnclient = self._client()
        revision_revision = pysvnclient.log(branch_url, limit=1)[0].revision.number
        trunk_revision = pysvnclient.log(trunk_url, limit=1)[0].revision.number
        # print('LLLL',  trunk_revision,revision_revision)
        if trunk_revision > revision_revision:
            msg = "Module '{module}' has main trunk commits - latest {release} release SVN tag is '{current}', ".format(
                release=tag,  # self.__tag,
                module=module_name,  # self.__module_name,
                current=revision_revision,
            ) + "while trunk SVN tag is '{trunk}'".format(trunk=trunk_revision)
            from . import savable_module

            raise savable_module.PreSaveException(msg)

    def uncommitted_files(self, path):
        """SVN implementation of uncommitted_files()."""
        client = self._client()

        def is_committed(status):
            def _status_is_normal(status):
                return status in [
                    pysvn.wc_status_kind.none,
                    pysvn.wc_status_kind.normal,
                ]

            return _status_is_normal(status.text_status) and _status_is_normal(status.prop_status)

        def is_unversioned(status):
            def _status_is_unversioned(status):
                return status in [pysvn.wc_status_kind.unversioned]

            # print('KKK', status, pysvn.wc_status_kind.unversioned, status.text_status, status.prop_status, _status_is_unversioned(status.text_status))
            return _status_is_unversioned(status.text_status)

        # We set ignore to True so that unversioned files with the ignore
        # property set, don't get reported.
        #
        # We set get_all to False since we only care about local modifications.
        try:
            yam_log.say("Looking for uncommitted version-controlled files under {} path ".format(path))
            yam_log.say("Checking SVN status for {} path ".format(path))
            return [
                s.path
                for s in client.status(path=path, ignore=True, get_all=False)
                if (not is_unversioned(s)) and (not is_committed(s))
            ]
        except pysvn.ClientError:
            raise revision_control_system.NotAWorkingCopyException(path=path)

    def generate_logs_since_last_branch(self, path, ignored_paths=()):
        """SVN implementation of generate_logs_since_last_branch()."""
        client = self._client()

        yam_log.say("Getting log message for {} path".format(path))
        logs = self._log(
            client=client,
            url_or_path=path,
            discover_changed_paths=True,
            # Don't read logs before the start of the
            # branch.
            strict_node_history=True,
            include_merged_revisions=True,
        )

        yam_log.say("Getting SVN repository for the {} path".format(path))
        repo_url = client.info(path)["repos"]
        yam_log.say("Getting SVN relative repo path for the {} path".format(path))
        repo_relative_path_url = client.info(path)["url"].replace(repo_url, "")

        # Join non-empty non-ignored logs
        earliest_revision_number = _earliest_revision(logs).number
        return "\n\n".join(
            filter(
                len,
                [
                    _format_log(
                        log=l,
                        common_path=repo_relative_path_url,
                        ignored_paths=ignored_paths,
                        earliest_revision_number=earliest_revision_number,
                    )
                    for l in logs
                    if "message" in l and l["message"] != _default_commit_message
                ],
            )
        )

    def generate_logs_since_divergence(
        self,
        path,
        tagged_url: revision_control_system.ModuleBranchData,
        # path_url : revision_control_system.ModuleBranchData =None,
        ignored_paths=(),
    ):
        """SVN implementation of generate_logs_since_divergence()."""
        client = self._client()

        last_common_revision = _earliest_revision(self._log(client=client, url_or_path=svn_uri(tagged_url)))

        # print('YYY', last_common_revision)

        """
        # use the path for path_url if the latter is undefined
        if not path_url:
            path_url_str = path
        else:
            path_url_str = svn_uri(path_url)
        """

        # get the main trunk URL
        path_url_str = svn_uri(tagged_url.with_release_tag(release_tag="main", branch_id=None))

        # Note that this is revision_end because the log is in reverse order
        # (starting at head).
        yam_log.say("Getting log message for {} path".format(path))
        # yam_log.say("Getting log message for the main trunk")
        logs = self._log(
            client=client,
            url_or_path=path_url_str,
            revision_end=last_common_revision,
            discover_changed_paths=True,
        )

        repo_url = client.info(path)["repos"]
        repo_relative_path_url = client.info(path)["url"].replace(repo_url, "")

        # Join non-empty non-ignored logs.
        return "\n\n".join(
            filter(
                len,
                [
                    _format_log(
                        log=l,
                        common_path=repo_relative_path_url,
                        ignored_paths=ignored_paths,
                    )
                    for l in logs
                ],
            )
        )

    def generate_diff(
        self,
        from_data: revision_control_system.ModuleBranchData,
        to_data: revision_control_system.ModuleBranchData = None,
        path: str = "",
        ignored_paths=(),
    ):
        """SVN implementation of revision_control_system.generate_diff()."""

        # ensure that one, and only one, or path and to_data are defined
        assert not (path and to_data)
        assert path or to_data

        from_url = svn_uri(from_data)
        if path:
            to_url = self.url(path)
        else:
            to_url = svn_uri(to_data)
        yam_log.say("Getting SVN diffs between {} and".format(from_url) + " and {} url".format(to_url))
        self.url_check(url=from_url)
        self.url_check(url=to_url)

        fallback = "Cannot display: non-UTF-8 text"

        try:
            tmp_diff = self._client().diff(
                tmp_path=tempfile.gettempdir(),
                url_or_path=from_url,
                url_or_path2=to_url,
                revision2=pysvn.Revision(pysvn.opt_revision_kind.head),
                revision1=pysvn.Revision(pysvn.opt_revision_kind.head),
                ignore_ancestry=True,
            )
        except UnicodeError:  # pragma: NO COVER
            # We need to catch this exception since pysvn has a bug. It
            # incorrectly assumes everything is UTF-8.
            return fallback  # pragma: NO COVER

        # This will be needed if pysvn ever fixes the above bug.
        if sys.version_info[0] == 3:  # pragma: NO COVER
            tmp_diff = decode(tmp_diff, fallback=fallback)  # pragma: NO COVER

        # Filter out diffs from ignored_paths.
        filtered_diff_lines = []
        current_filename = None
        for line in tmp_diff.split("\n"):
            if line.startswith("Index:"):
                current_filename = re.sub(pattern="^Index: ", repl="", string=line)
                if current_filename in ignored_paths:
                    # add note to output that we will skip diffs for the file
                    filtered_diff_lines.append(current_filename + ": Skipping diffs (uninteresting)")

            if current_filename not in ignored_paths:
                filtered_diff_lines.append(line)

        return "\n".join(filtered_diff_lines)

    def url_check(self, url):
        """Raise NonExistentURLException exception on finding non-existent URLs."""
        if not self._exists(url=url):
            raise revision_control_system.NonExistentURLException(url=url)

    def has_modificationsOBSOLETE(self, from_url, to_url):
        """SVN implementation of has_modifications()."""
        yam_log.say("Checking SVN for modifications between {} and".format(from_url) + " and {} url".format(to_url))
        self.url_check(revision_control_system=self, url=from_url)
        self.url_check(revision_control_system=self, url=to_url)

        return bool(
            self._client().diff_summarize(
                url_or_path1=from_url,
                url_or_path2=to_url,
                revision2=pysvn.Revision(pysvn.opt_revision_kind.head),
                revision1=pysvn.Revision(pysvn.opt_revision_kind.head),
                ignore_ancestry=True,
            )
        )

    def isConsistent(self, path, expected_data: revision_control_system.ModuleBranchData):
        # return True if the checked out path's svn uri matches the expected value
        flag = svn_uri(expected_data) == self.url(path)
        # print('MMMM', svn_uri(expected_data), self.url(path), flag)
        return flag

    def modified_paths_since_divergence(self, path, tagged_url: revision_control_system.ModuleBranchData):
        """SVN implementation of modified_paths_since_divergence()."""
        client = self._client()

        last_common_revision = _earliest_revision(self._log(client=client, url_or_path=svn_uri(tagged_url)))

        root_url = client.info2(path)[0][1]["repos_root_URL"]

        paths = []
        path_url = self.url(path=path)
        # Note that this is revision_end because the log is in reverse order
        # (starting at head).
        for log in self._log(
            client=client,
            url_or_path=path,
            revision_end=last_common_revision,
            discover_changed_paths=True,
            include_merged_revisions=True,
        ):
            for c in log.changed_paths:
                relative_path = (root_url + c.path).replace(path_url, "").lstrip("/")
                if relative_path:
                    paths.append(relative_path)
                elif c.action != "A":
                    # Ignore the creation of the URL directory itself.
                    paths.append(".")

        return list(set(paths))

    def add_file(self, path):
        """SVN implementation of revision_control_system.add_file()."""
        try:
            yam_log.say("Adding {} path to SVN".format(path))
            self._client().add(path=path)
        except pysvn.ClientError as exception:
            raise revision_control_system.AlreadyUnderRevisionControl(str(exception))

    def list_files(self, path):
        """SVN implementation of revision_control_system.list_files()."""
        try:
            yam_log.say("Getting list of files for {} path from SVN".format(path))
            for item in self._client().list(url_or_path=path, recurse=True):
                filename = item[0]["path"]
                if filename:
                    yield filename
        except pysvn.ClientError:
            pass

    def create_module(self, vcs_root: str, module_name: str, bare: bool):
        # Create the VCS structure for the new module in the rep for R1-00 release

        root = vcs_root + "/Modules/{}".format(module_name)

        # check that the module does not already exist in the repo
        module_branch_data = revision_control_system.ModuleBranchData(
            vcs_root=vcs_root, module_name=module_name, release_tag="main", vcs_type="svn"
        )
        if self.exists_module_branch(module_branch_data):
            raise yam_exception.YamException(
                "Module '{m}' already exists in the {r} SVN repository".format(m=module_name, r=vcs_root)
            )

        # create SVN structure for the new module
        # print('NNNN', root + '/trunk')
        self.make_directory(root + "/trunk")
        self.make_directory(root + "/deadBranches")
        self.make_directory(root + "/featureBranches")
        self.make_directory(root + "/releases")
        # self.make_directory(root + '/releases/{}-R1-00'.format(module_name))

        """
        self.make_directory(
            os.path.dirname(
                work_module.dead_branches_url(
                    module_name=module_name,
                    revision_tag="",
                    branch_id="",
                    database_reader=self.__database_reader,
                )
            )
        )

        self.make_directory(
            os.path.dirname(
                work_module.feature_branches_url(
                    module_name=module_name,
                    revision_tag="",
                    branch_id="",
                    database_reader=self.__database_reader,
                )
            )
        )

        self.make_directory(
            os.path.dirname(
                work_module.releases_url(
                    module_name=module_name,
                    revision_tag=revision_tag,
                    database_reader=self.__database_reader,
                )
            )
        )
        """

    def create_and_commit_basic_module_files(self, vcs_root, module_name, file_system, build_system, bare):
        """Check out trunk and add basic files.

        Return the working copy path.

        """
        root = vcs_root + "/Modules/{}/trunk".format(module_name)
        working_copy_path = file_system.create_temporary_directory()
        self.__check_out(source=root, target=working_copy_path)

        build_system.create_module_files(
            module_name=module_name,
            module_path=working_copy_path,
            top_level_file_callback=self.add_file,
        )

        self.check_in(path=working_copy_path, log_message="pyam: Add initial files")

        return working_copy_path

    def _raise_exception_on_non_working_copy(self, path):
        """Raise NotAWorkingCopyException if path is not a working copy."""
        if not self.working_copy_exists(path=path):
            raise revision_control_system.NotAWorkingCopyException(path=path)

    def _reintegrate(self, client, url_or_path, revision, local_path):
        """Merge-reintegrate into a branch."""
        revision = pysvn.Revision(pysvn.opt_revision_kind.head)

        if self.__use_merge_info:
            client.merge_reintegrate(
                url_or_path=url_or_path,
                revision=revision,
                local_path=local_path,
            )

            # We successfully merged and our local copy now has the
            # modifications. I possibly want to just commit them. Maybe. I'm
            # SURE that I want to commit the mergeinfo, however, so I do that
            # here
            #
            # Never mind. pysvn is broken, and this doesn't work. There's no way
            # to commit '.' without committing all its children. recurse=False
            # should do it, but it doesn't work (commits children).
            # depth='empty' should work too, but it complains about also wanting
            # recurse, regardless of whether recurse is given or not. Life is
            # too short to spend time on this, so I'm giving up
            #     yam_log.say(
            #         "Checking in mergeinfo in '{}'".format(local_path + "/."))
            #     client.checkin(path=local_path + "/.",
            #                    log_message="Committing mergeinfo",
            #                    recurse=False)

            # since pysvn is broken, we use a system level call to svn
            # to commit the mergeinfo

            # print('AAAA0')
            yam_log.say(
                'Using system "svn commit" call to commit mergeinfo for {} path (since pysvn is currently broken)'.format(
                    url_or_path
                )
            )
            import subprocess

            p = subprocess.Popen(
                [
                    "svn",
                    "commit",
                    "--depth",
                    "empty",
                    "-m",
                    "Committing mergeinfo",
                    local_path,
                ],
                stdout=subprocess.PIPE,
            )

            out = p.stdout.read()

            # print('DDDDD0',  out)
            # print('AAAA1')

        else:
            # For older SVN servers.
            _emulated_reintegrate(
                client=client,
                url_or_path=url_or_path,
                revision=revision,
                local_path=local_path,
            )

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
        """Return SVN log."""
        if not self.__use_merge_info:
            # For older SVN servers.
            include_merged_revisions = False

        try:
            yam_log.say("Getting log messages for {} path".format(url_or_path))
            return client.log(
                url_or_path=url_or_path,
                revision_start=revision_start,
                revision_end=revision_end,
                discover_changed_paths=discover_changed_paths,
                strict_node_history=strict_node_history,
                include_merged_revisions=include_merged_revisions,
            )
        except pysvn.ClientError as exception:
            if "mergeinfo" in str(exception):
                raise yam_exception.YamException(
                    "Subversion repository version is too old; " "it does not support merge tracking"
                )

    def _client(self):
        """Return a pysvn client instance.

        This is necessary to work around some bug in some versions of
        pysvn. This is probably better anyway to avoid sharing of state.

        """
        client = pysvn.Client()
        yam_log.say("Setting SVN client's user name to {}".format(self.__username))
        client.set_default_username(self.__username)

        if self.__login_callback:
            client.callback_get_login = self.__login_callback

        if self.__trust_ssl_server_callback:
            client.callback_ssl_server_trust_prompt = self.__trust_ssl_server_callback

        def get_log_message():
            """Return default log message."""
            return True, _default_commit_message

        client.callback_get_log_message = get_log_message

        return client


def svn_uri(module_branch_data: revision_control_system.ModuleBranchData):
    """
    Return a svn uri for locating the release/branch in the revision
    control system
    """
    # must have a release id, either 'main' or release tag such as 'Rx-xxx'
    release_tag = module_branch_data._release_tag

    branch_id = module_branch_data._branch_id

    # cannot have branch for the main trunk
    assert not (release_tag == "main" and branch_id)
    vcs_root = module_branch_data._vcs_root
    module_name = module_branch_data._module_name

    if 1:
        result = "{root}/Modules/{m}".format(root=vcs_root, m=module_name)

        if release_tag == "main":
            # main trunk URI
            result += "/trunk"
        else:
            if branch_id:
                # branch URI
                area = "deadBranches" if module_branch_data._dead_branch else "featureBranches"
                result += "/{a}/{m}-{r}-{b}".format(m=module_name, a=area, r=release_tag, b=branch_id)
            else:
                # release URI
                result += "/releases/{m}-{r}".format(m=module_name, r=release_tag)
        return result


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


def _relative_path(svn_log_change, common_path):
    """Return path relative to common_path."""
    relative_path = svn_log_change.path.replace(common_path, "").lstrip("/")
    return relative_path if relative_path else "."


def _emulated_reintegrate(client, url_or_path, revision, local_path):
    """Reintegration merge for older SVN servers (<1.5).

    This is emulating,

    merge_reintegrate(url_or_path,
                      revision,
                      local_path)

    """
    # Find revision range. It starts when the branched was first created.
    logs = client.log(
        url_or_path=url_or_path,
        # Don't read logs before the start of the branch.
        strict_node_history=True,
    )

    # Do the merge from earlier revision (when branch was created)
    # to revision (parameter)
    client.merge(
        url_or_path1=url_or_path,
        revision1=_earliest_revision(logs),
        url_or_path2=url_or_path,
        revision2=revision,
        local_path=local_path,
    )


def _earliest_revision(logs):
    """Return earliest revision in logs."""
    return pysvn.Revision(
        pysvn.opt_revision_kind.number,
        min([l["revision"].number for l in logs]),
    )


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
