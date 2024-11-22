"""Contains the MainWorkModule class."""

from __future__ import absolute_import

import os

from . import module_saving_utils
from . import revision_tag_utils
from . import savable_module
from . import saving_utils
from . import work_module
from . import yam_log
from . import revision_control_system as rcs


class MainWorkModule(work_module.WorkModule, savable_module.SavableModule):
    """A WorkModule that lives on the main branch."""

    def __init__(
        self,
        module_name,
        revision_control_system,
        parent_directory,
        database_reader,
        database_writer,
        file_system,
    ):
        """Create a representation of a Yam module.

        This is a module whose source code can be checked out.

        Keyword arguments:
        parent_directory -- The parent directory in which this module will be
        checked out.

        """
        savable_module.SavableModule.__init__(self)

        vcs_type = database_reader.vcs_type(module_name)
        vcs_root = database_reader.module_repository_url(module_name)
        module_branch_data = rcs.ModuleBranchData(
            module_name=module_name, release_tag="main", branch_id=None, vcs_type=vcs_type, vcs_root=vcs_root
        )

        work_module.WorkModule.__init__(
            self,
            module_name=module_name,
            revision_control_system=revision_control_system,
            parent_directory=parent_directory,
            module_branch_data=module_branch_data,
            # vcs_type=vcs_type
        )

        self.__database_reader = database_reader
        self.__database_writer = database_writer
        self.__file_system = file_system

        self.__module_name = module_name
        self.__module_path = os.path.join(parent_directory, module_name)
        """
        self.__revision_control_system = revision_control_system[vcs_type]
        """

    def save(
        self,
        release_note_message,
        username,
        release_directory,
        keep_release,
        changelogs_path,
        build_system,
        operating_system_name,
        site_name,
        host_ip,
        bug_id=None,
        desired_build_id=None,
        release_information_callback=(
            lambda module_name, revision_tag, build_id, site_name, release_note_entry, change_log_entry, diff: None
        ),
        progress_callback=lambda _: None,
        mkdiff=True,
    ):
        """MainWorkModule implementation of savable_module.save()."""

        #### main_branch_url = self._repository_url()

        # check that this module is releaasable
        self.pre_save_check(release_directory)

        """
        # get the tag for the last module release
        last_release_tag = (
            self.__database_reader.latest_module_information(
                module_name=self.__module_name, release=None)['tag'])

        # get the repo url for the last module release
        old_url = work_module.releases_url(
            module_name=self.__module_name,
            revision_tag=previous_release_tag,
            database_reader=self.__database_reader)

        # get list of files that have changed between the current module
        # path and the last release (basically we are looking for main
        # trunk commits)
        changed_paths = (
            self.rcs().modified_paths_since_divergence(
                path=self.__module_path,
                tagged_url=old_url))
        """

        # get the tag for the last module release
        last_release_tag = self.__database_reader.latest_module_information(
            module_name=self.__module_name, release=None
        )["tag"]
        old_release_data = self.module_branch_data().with_release_tag(last_release_tag, None)

        # get a list of the files that have changed since the last
        # module release due to main trunk commits
        changed_paths = self._main_trunk_commits(last_release_tag=last_release_tag)

        date_time = self.__database_reader.local_date_time()

        if changed_paths:
            # There are committed changes to the module. Proceed to make
            # a regular release of the module.
            progress_callback("Generating diff statistics for module '{m}'".format(m=self.__module_name))

            # Generate diff for statistics we send to the database
            if mkdiff:
                diff_lines = (
                    self.rcs()
                    .generate_diff(
                        from_data=old_release_data,  # old_release_url,
                        path=self.__module_path,
                        #                 from_url=work_module.releases_url(
                        #                     module_name=self.__module_name,
                        #                     revision_tag=last_release_tag,
                        #                     database_reader=self.__database_reader,
                        #                 ),
                        #                 to_url=main_branch_url,
                        ignored_paths=(
                            "ReleaseNotes",
                            "ChangeLog",
                            "YamVersion.h",
                            "swig/docstrings.i",
                        ),
                    )
                    .split("\n")
                )
            else:
                diff_lines = ["SKIPPED DIFF GENERATION PER USER REQUEST"]

            new_revision_tag = revision_tag_utils.incremented(revision_tag=last_release_tag)

            # Update the "YamVersion.h" file.
            module_saving_utils.update_yam_version_file(
                module_name=self.__module_name,
                new_revision_tag=new_revision_tag,
                module_path=self.__module_path,
                file_system=self.__file_system,
                revision_control_system=self.rcs(),
            )

            # Add entries to ReleaseNotes and ChangeLog.
            # We only get return values so that we can pass the data to
            # release_information_callback.
            release_note_entry = saving_utils.update_release_notes(
                message=release_note_message,
                new_revision_tag=new_revision_tag,
                date_time=date_time,
                file_system=self.__file_system,
                path=self.__module_path,
                revision_control_system=self.rcs(),
            )

            revision_control_log = self.generate_log()
            change_log_entry = module_saving_utils.generate_change_log_entry(
                bug_id=bug_id,
                new_revision_tag=new_revision_tag,
                date_time=date_time,
                username=username,
                revision_control_log=revision_control_log,
            )

            module_saving_utils.update_change_log(
                change_log_entry=change_log_entry,
                file_system=self.__file_system,
                module_path=self.__module_path,
                revision_control_system=self.rcs(),
            )

            # Release the module. This involves creating the new release
            # branch, updating the database, and moving the module to
            # the release area.
            module_saving_utils.release_module(
                module_name=self.__module_name,
                module_path=self.__module_path,
                new_revision_tag=new_revision_tag,
                new_release_tag=new_revision_tag,
                # original_branch_url=main_branch_url,
                original_branch_data=self.module_branch_data(),
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
                file_system=self.__file_system,
                revision_control_system=self.rcs(),
                build_system=build_system,
                diff_lines=diff_lines,
                modified_paths=changed_paths,
                changelogs_path=changelogs_path,
                username=username,
                date_time=date_time,
                operating_system_name=operating_system_name,
                site_name=site_name,
                host_ip=host_ip,
                release_directory=release_directory,
                keep_release=keep_release,
                latest_link=True,
                progress_callback=progress_callback,
                maintenance_name=None,
                maintenance_num=None,
            )

            # Call post-save callback
            release_information_callback(
                module_name=self.__module_name,
                revision_tag=new_revision_tag,
                build_id=None,
                site_name=site_name,
                release_note_entry=release_note_entry,
                change_log_entry=change_log_entry,
                diff="\n".join(diff_lines),
            )

            return (new_revision_tag, None)
        elif release_directory and keep_release:
            # Just a build release since there are no committed
            # changes. Move the module to the release area since a
            # release directory has been provided and saving there has
            # been enabled
            progress_callback("Making a build release since no source code was changed")

            new_build_id = module_saving_utils.generate_build_id(
                module_name=self.__module_name,
                database_reader=self.__database_reader,
                desired_build_id=desired_build_id,
            )

            readmes = module_saving_utils.module_readmes(self.__module_path)

            # Move file system directory to release area.
            module_saving_utils.move_module_for_release(
                module_path=self.__module_path,
                module_name=self.__module_name,
                new_revision_tag=last_release_tag,
                build_id=new_build_id,
                changelogs_path=changelogs_path,
                release_directory=release_directory,
                keep_release=keep_release,
                latest_link=True,
                file_system=self.__file_system,
                build_system=build_system,
                database_writer=self.__database_writer,
                progress_callback=progress_callback,
            )

            # Write release information to the database
            progress_callback("Updating database with readmes: {}".format(readmes))

            self.__database_writer.write_module_build_release_information(
                module_name=self.__module_name,
                revision_tag=last_release_tag,
                build_id=new_build_id,
                username=username,
                date_time=date_time,
                readmes=readmes,
                operating_system_name=operating_system_name,
                site_name=site_name,
                host_ip=host_ip,
                release_path=release_directory,
            )

            # Call post-save callback
            release_information_callback(
                module_name=self.__module_name,
                revision_tag=last_release_tag,
                build_id=new_build_id,
                site_name=site_name,
                release_note_entry="",
                change_log_entry="",
                diff="",
            )

            return (last_release_tag, new_build_id)
        else:
            raise savable_module.PreSaveException(
                "'{}' will not be saved since it has no changes".format(self.__module_name)
            )

    def pre_save_check(self, release_directory):
        """MainWorkModule implementation of savable_module.pre_save_check()."""
        # main_branch_url = self._repository_url()

        _pre_save_check(
            module_path=self.__module_path,
            expected_url=self.module_branch_data(),  # main_branch_url,
            revision_control_system=self.rcs(),
            file_system=self.__file_system,
            release_directory=release_directory,
        )

    def generate_log(self):
        """MainWorkModule implementation of savable_module.generate_log()."""
        previous_release_tag = self.__database_reader.latest_module_information(
            module_name=self.__module_name, release=None
        )["tag"]

        """
        previous_release_url = work_module.releases_url(
            module_name=self.__module_name,
            revision_tag=previous_release_tag,
            database_reader=self.__database_reader,
        )
        """

        return self.rcs().generate_logs_since_divergence(
            path=self.__module_path,
            # tagged_url=previous_release_url,
            tagged_url=self.module_branch_data().with_release_tag(
                release_tag=previous_release_tag, branch_id=None
            ),  # previous_release_url,
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        )

    # def _version_name(self):
    def _repo_tag_name(self):
        """Return version name  instance."""
        return work_module.main_branch_name()

    def _repository_urlOBSOLETE(self):
        """Return full repository URL to this module instance."""
        return work_module.main_branch_url(module_name=self.__module_name, database_reader=self.__database_reader)

    def _main_trunk_commits(self, last_release_tag):
        """
        Return list of files that have been modified by main trunk commits
        since the last module release.
        """
        # get the repo url for the last module release
        """
        old_url = work_module.releases_url(
            module_name=self.__module_name,
            revision_tag=last_release_tag,
            database_reader=self.__database_reader,
        )
        """

        old_release_data = self.module_branch_data().with_release_tag(last_release_tag, None)

        # get list of files that have changed between the current module
        # path and the last release (basically we are looking for main
        # trunk commits)
        changed_paths = self.rcs().modified_paths_since_divergence(
            path=self.__module_path,
            tagged_url=old_release_data,  # old_release_url
            # tagged_url=old_url
        )
        return changed_paths

    def sync(self, to_release=None, to_branch=None, progress_callback=lambda _: None):
        """
        For main trunk module, there is no merging, and the sync command
        simply switches to the specified tagged release/branch. An error
        is thrown if there are unreleased commits on the main trunk.

        Return a tuple (revision_tag, branch_id) representing the revision tag
        we synced to and the new branch ID.

        """
        # get the tag for the last module release
        last_release_tag = self.__database_reader.latest_module_information(
            module_name=self.__module_name, release=None
        )["tag"]

        # get a list of the files that have changed since the last
        # module release due to main trunk commits
        changed_paths = self._main_trunk_commits(last_release_tag=last_release_tag)

        # raise error is there have been main trunk commits since the
        # last module release. Force the user to release these commits.
        if changed_paths:
            raise ValueError(
                "Cannot sync a main trunk module with main trunk commits. The following files have main trunk commits: %s"
                % list(map(str, changed_paths))
            )

        # Get the latest revision tag for the specified release tag (???)
        """
        requested_revision_tag = self.__database_reader.latest_module_information(
            module_name=self.__module_name, release=to_release
        )[
            "tag"
        ]
        """

        # if a release tag has been specified, then verify that this
        # release (regular or maintenance) exists
        if to_release:
            tag, build, maintbr, maintid = revision_tag_utils.split_tag(to_release)
            self.__database_reader.module_information(self.__module_name, tag, maintbr, maintid)

            # print('DD', to_branch)
            requested_revision_tag = to_release
        else:
            # use the latest revision tag for the specified release tag
            # is none specified
            requested_revision_tag = last_release_tag

        # Make sure we have the expected repository URL.
        """
        actual_url = self.rcs().url(path=self.__module_path)
        expected_url = self._repository_url()
        if actual_url != expected_url:
        """
        if not self.rcs().isMainTrunkCheckout(self.__module_path):

            # TODO: Move RepositoryURLMismatchError to a different module.
            expected_url = self.module_branch_data().uri()
            actual_url = self.rcs().url(path=self.__module_path)
            # print('JJJJ', self.__module_path, expected_url, actual_url)
            raise savable_module.RepositoryURLMismatchError(expected_url=expected_url, actual_url=actual_url)

        if not to_branch:
            # no branch is requested, so switch to the tagged release
            """
            new_url = work_module.releases_url(
                module_name=self.__module_name,
                revision_tag=requested_revision_tag,
                database_reader=self.__database_reader,
            )
            """
            new_url_data = self.module_branch_data().with_release_tag(requested_revision_tag)
            progress_callback(
                "Switching to revision '{r}' for '{m} module'".format(r=requested_revision_tag, m=self.__module_name)
            )

        else:
            from . import branched_work_module

            # if branch exists, simply switch to it, else create the
            # branch and siwtch to it

            # get the repo URL for the proposed branch
            """
            new_url = work_module.feature_branches_url(
                module_name=self.__module_name,
                revision_tag=requested_revision_tag,
                branch_id=to_branch,
                database_reader=self.__database_reader,
            )
            """
            new_url_data = self.module_branch_data().with_release_tag(requested_revision_tag, to_branch)

            # print('MMMM', to_branch)
            # create the branch if it does not already exist
            branched_work_module._create_branch(
                # module_name=self.__module_name,
                # tag=requested_revision_tag,
                # branch_id=to_branch,
                module_branch_data=new_url_data,
                repository_destination_url=new_url_data,
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
                revision_control_system=self.rcs(),
            )

            branchnm = self.__module_name + "-" + requested_revision_tag + "-" + to_branch
            progress_callback("Moving to the '{}' branch for '{}' module".format(branchnm, self.__module_name))
            yam_log.say("Moving to the '{}' branch for '{}' module".format(branchnm, self.__module_name))

            """
            yam_log.say(
                'Creating branch off of {} revision for the {} module'.format(requested_revision_tag,
                                                                            self.__module_name))
            new_branch_id = branched_work_module._create_unique_branch(
                module_name=self.__module_name,
                revision_tag=requested_revision_tag,
                branch_id=to_branch,
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
                revision_control_system=self.rcs())
            # Merge old branch into new branch (use reintegrateBranch()).
            yam_log.say(
                'Merging the {} module into the main trunk'.format(self.__module_name))
            new_url = work_module.feature_branches_url(
                module_name=self.__module_name,
                revision_tag=requested_revision_tag,
                branch_id=new_branch_id,
                database_reader=self.__database_reader)
            """
            # Reintegrate, but don't commit. Let the user handle committing.

            #        yam_log.say(
            #            "new_branch_id ::: '{a}' MODULE PATH: '{b}' NEW_BRANCH_URL::: '{c}' ARCHINVE URL ::: '{d}'".format(a = new_branch_id, b = self._module_path, c= new_branch_url, d =archive_url))
            """
            self.rcs().reintegrate(path=self.__module_path,
                                                       original_url=new_branch_url,
                                                       archive_url=archive_url)
            """

        self.rcs().switch_to_branch(path=self.__module_path, branch_url=new_url_data)

        self._post_check_out(self.__module_path)

        return (requested_revision_tag, to_branch)


def _pre_save_check(
    module_path,
    expected_url: rcs.ModuleBranchData,
    revision_control_system,
    file_system,
    release_directory,
):
    """Raise appropriate exception based on error condition."""
    module_saving_utils.basic_module_check(
        module_path=module_path,
        expected_url=expected_url,
        revision_control=revision_control_system,
    )

    module_saving_utils.pre_save_check(file_system=file_system, release_directory=release_directory)
