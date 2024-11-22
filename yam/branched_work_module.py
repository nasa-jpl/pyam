"""Contains the BranchedWorkModule class."""

from __future__ import absolute_import

import os.path
import os
import re


from . import module_saving_utils

# from . import maintenance_saving_utils
from . import revision_tag_utils
from . import savable_module
from . import saving_utils
from . import work_module
from . import yam_exception
from . import yam_log
from git import Repo
from . import revision_control_system as rcs


class BranchedWorkModule(work_module.WorkModule, savable_module.SavableModule):
    """A WorkModule that is branched from an existing tagged release."""

    def __init__(
        self,
        module_name,
        tag,
        branch_id,
        revision_control_system,
        parent_directory,
        database_reader,
        database_writer,
        file_system,
    ):
        """Initialize."""
        # print("branched KKK", module_name, tag, branch_id)
        savable_module.SavableModule.__init__(self)

        branch_id = filter_legal_branch_id(branch_id)

        vcs_type = database_reader.vcs_type(module_name)

        # need this to keep unit tests happy
        if not vcs_type:
            vcs_type = "svn"
        vcs_root = database_reader.module_repository_url(module_name)
        module_branch_data = rcs.ModuleBranchData(
            module_name=module_name,
            release_tag=tag,
            branch_id=branch_id,
            vcs_type=vcs_type,
            vcs_root=vcs_root,
        )

        work_module.WorkModule.__init__(
            self,
            module_name=module_name,
            revision_control_system=revision_control_system,
            parent_directory=parent_directory,
            module_branch_data=module_branch_data,
            # vcs_type=vcs_type
        )

        self.__tag = tag
        self.__branch_id = branch_id

        self.__database_reader = database_reader
        self.__database_writer = database_writer
        self.__file_system = file_system

        # Keep local references to these for the save() method (even though
        # we've passed them to WorkModule). Don't put getter methods in base
        # class!
        self.__module_path = os.path.join(parent_directory, module_name)
        self.__module_name = module_name
        self.__revision_tag = tag
        """
        self.__revision_control_system = revision_control_system[vcs_type]
        """

    def isMaintenanceBranchOBSOLETE(self):
        """
        Return True if this is a maintenance branch module.
        """
        if re.search("Maintenance", self.__branch_id):
            return True
        else:
            return False

    def maintenanceBranchTuple(self):
        """
        Return maintenance branch value as a tuple.

                For example,

                'Orion-MaintenanceM05'   to     ('Orion', '05')

                'Orion-Maintenance'   to     ('Orion', None)

                'myuser'     to     (None, None)
        """
        return revision_tag_utils.branch_to_maintenance_tuple(self.__branch_id)

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
        """BranchedWorkModule implementation of savable_module.save().

        Return the new revision tag.

        """
        # print("DDDD")
        # print(self.__module_path)
        # TODO: Move this to client so that main_work_module benefits too.
        release_note_message = module_saving_utils.format_message(release_note_message)

        yam_log.say("Get main branch url for the {} module".format(self.__module_name))
        # maint_branch_id = self.__branch_id
        ## print("BRANCH ID", self.__branch_id)

        """
        main_branch_url = work_module.main_branch_url(
            module_name=self.__module_name,
            database_reader=self.__database_reader,
        )
        """

        yam_log.say("Get dead branches url for the {} module".format(self.__module_name))

        """
        archive_url = work_module.dead_branches_url(
            module_name=self.__module_name,
            revision_tag=self.__tag,
            branch_id=self.__branch_id,
            database_reader=self.__database_reader,
        )
        """
        self.pre_save_check(release_directory)

        date_time = self.__database_reader.local_date_time()

        # Only make a source release if there are changes
        ## print("revision_tag", self.__revision_tag)
        yam_log.say("Get url for the {} work module".format(self.__module_name))

        """
        old_release_url = work_module.releases_url(
            module_name=self.__module_name,
            revision_tag=self.__revision_tag,
            database_reader=self.__database_reader,
        )
        """
        # print("old release url", old_release_url)

        # ******* fix old_release_url for maintenance releases *******

        # get maintenance release info in case this is a maintenance branch
        maintenance_name, maint_num = self.maintenanceBranchTuple()

        # we should be on the branch, and not a tagged maintenance release
        assert not maint_num

        yam_log.say("Checking if there are committed changes for the {} module".format(self.__module_name))
        """
        if self.__revision_control_system.vcs =="git":
            self.__revision_control_system.tag = self.__revision_tag
            self.__revision_control_system.branch_name = f"{self.__module_name}-{self.__revision_tag}-{self.__branch_id}"
            self.__revision_control_system.repo = Repo(old_release_url)
            old_release_url = f"{self.__module_name}-{self.__revision_tag}-{self.__branch_id}"
        """
        vcs_type = self.module_branch_data()._vcs_type

        old_release_data = self.module_branch_data().with_branch_id(None)
        changed_paths = self.rcs().modified_paths_since_divergence(
            path=self.__module_path, tagged_url=old_release_data  # old_release_url
        )

        if changed_paths:
            # There are committed changes to the module. Proceed to make
            # a regular release of the module.
            yam_log.say("Generating diff statistics for module '{m}'".format(m=self.__module_name))
            progress_callback("Generating diff statistics for module '{m}'".format(m=self.__module_name))

            # Generate diff for statistics we send to the database
            if mkdiff:
                diff_lines = (
                    self.rcs()
                    .generate_diff(
                        from_data=old_release_data,  # old_release_url,
                        path=self.__module_path,
                        #                 to_url=self.rcs().url(
                        #                     path=self.__module_path
                        #                 ),
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

            # print('ZZZ', diff_lines)
            if maintenance_name:
                # we are on a maintenance branch
                # print("IN MAINTENANCE")
                release_path = os.path.join(release_directory, "Module-Releases", self.__module_name)

                # maintenance_name=self.__branch_id.split('-')[0]

                # get the maintenance branch and maintenace release number
                # get last maint release on this maintenance branch
                last_maint_release_num = self.__database_reader.latest_maintenance_release_num(
                    self.__module_name, self.__tag, maintenance_name
                )
                # if none, use 0 as new maintance release number, else increment
                if last_maint_release_num < 0:
                    maintenance_num = 0
                else:
                    maintenance_num = last_maint_release_num + 1

                ## print("self.__tag=", self.__tag, self.__branch_id)

                new_maintenance_num = str(maintenance_num).zfill(2)
                ## print("new_maintenance_num", new_maintenance_num)

                # new_revision_tag = self.__revision_tag + '-' + self.__branch_id + 'M'+non_random_id
                from . import concrete_configuration_reader

                new_revision_tag = revision_tag_utils.tuple_to_maintenace_tag_suffix(
                    (
                        self.__revision_tag,
                        None,
                        maintenance_name,
                        new_maintenance_num,
                    )
                )
                new_release_tag = self.__revision_tag

            else:

                new_revision_tag = revision_tag_utils.incremented(revision_tag=self.__revision_tag)
                new_release_tag = new_revision_tag
                maintenance_name = None
                maintenance_num = None

            # print("NEW REVISION TAG", new_revision_tag)

            # print("new_revision_tag", new_revision_tag)
            revision_control_log = self.generate_log()
            # print('TTT 1', revision_control_log)
            yam_log.say("Generating change log entries for the {} module".format(self.__module_name))
            change_log_entry = module_saving_utils.generate_change_log_entry(
                bug_id=bug_id,
                new_revision_tag=new_revision_tag,
                date_time=date_time,
                username=username,
                revision_control_log=revision_control_log,
                # use_git = self.rcs().vcs == "git"
            )

            # Writing of meta files should come after reintegration to avoid
            # problems. If a problem occurs, we automatically roll back to the
            # original state before the "save" command was issued.
            # if self.rcs().vcs == "git":
            # print("UUUUU")
            # print(self.module_branch_data().repoPath())
            # module_saving_utils.tag_git_module(Repo(self.module_branch_data().repoPath()), new_revision_tag)

            yam_log.say("Updating the YamVersion.h file for the {} module".format(self.__module_name))
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
            yam_log.say("Updating ReleaseNotes file for the {} module".format(self.__module_name))
            release_note_entry = saving_utils.update_release_notes(
                message=release_note_message,
                new_revision_tag=new_revision_tag,
                date_time=date_time,
                file_system=self.__file_system,
                path=self.__module_path,
                revision_control_system=self.rcs(),
            )

            yam_log.say("Updating ChangeLog file for the {} module".format(self.__module_name))
            # print('BBB', change_log_entry)
            # print('KKKKKKKKK3', os.system(f'git -P -C {self.__module_path} status'))
            module_saving_utils.update_change_log(
                change_log_entry=change_log_entry,
                file_system=self.__file_system,
                module_path=self.__module_path,
                revision_control_system=self.rcs(),
            )

            # print('TTT 2', change_log_entry)
            if maintenance_name:
                progress_callback("Tagging '{m}' maintenance release".format(m=self.__module_name))

                yam_log.say("Tagging {} maintenance release".format(self.__module_name))

                progress_callback("MAINTENANCE BRANCH RECOGNIZED")
                ## print("self.__tag", self.__tag)

                original_source_url = self.rcs().url(self.__module_path)
                ## print("original_source_url", original_source_url, self.__module_path)
                curr_module_data = self.module_branch_data()

            else:
                ###original_source_url = main_branch_url
                # merge regular branch into the main trunk
                progress_callback("Merging '{m}' into main branch".format(m=self.__module_name))

                yam_log.say("Merging the {} module into the main trunk".format(self.__module_name))

                # maint_branch_id = self.__branch_id
                vcs_type = self.module_branch_data()._vcs_type
                if False and vcs_type == "git":
                    main_branch_data = self.module_branch_data()
                else:
                    main_branch_data = self.module_branch_data().with_release_tag("main", "")

                merge_into_main(
                    branch_id=self.__branch_id,
                    module_path=self.__module_path,
                    main_branch_url=main_branch_data,  # self.module_branch_data(),#.with_release_tag('main', ''), # main_branch_url,
                    archive_url=self.module_branch_data().with_dead_branch(),  # archive_url,
                    revision_control=self.rcs(),
                    release_note_message=release_note_message,
                )
                curr_module_data = self.module_branch_data().with_release_tag("main", None)

            ## print('maintenance_name=', maintenance_name, 'maintenance_num=', maintenance_num)
            module_saving_utils.release_module(
                module_name=self.__module_name,
                module_path=self.__module_path,
                new_revision_tag=new_revision_tag,  # can be R4-06j-ProjA-Maintenance03
                new_release_tag=new_release_tag,  #  R4-06j
                # original_branch_url=original_source_url,
                original_branch_data=curr_module_data,  # self.module_branch_data(),
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
                latest_link=not maintenance_name,
                progress_callback=progress_callback,
                maintenance_name=maintenance_name,
                maintenance_num=maintenance_num,
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

            # Remove this branch from "branches" column of tagged release.
            yam_log.say("Updating database with source release info for the {} module".format(self.__module_name))
            if not maintenance_name:
                # add DEAD suffix to the branch entry for the release in the database
                self.__database_writer.rename_branch(
                    module_name=self.__module_name,
                    revision_tag=self.__tag,
                    branch_id=self.__branch_id,
                    new_branch_id=self.__branch_id + "-DEAD",
                )

            return (new_revision_tag, None)

        elif release_directory and keep_release:
            # Just a build release since there are no committed
            # changes. Move the module to the release area since a
            # release directory has been provided and saving there has
            # been enabled
            progress_callback("Making a build release since no source code was changed")
            yam_log.say(
                "Making a build release since no source code was changed for the {} module".format(self.__module_name)
            )

            yam_log.say("Getting build release ID for the {} module".format(self.__module_name))
            new_build_id = module_saving_utils.generate_build_id(
                module_name=self.__module_name,
                database_reader=self.__database_reader,
                desired_build_id=desired_build_id,
            )

            # Move file system directory to release area.
            yam_log.say("Moving the module directory to the release area for the {} module".format(self.__module_name))

            # maint_branch_id= self.__branch_id

            readmes = module_saving_utils.module_readmes(self.__module_path)
            module_saving_utils.move_module_for_release(
                module_path=self.__module_path,
                module_name=self.__module_name,
                new_revision_tag=self.__tag,
                build_id=new_build_id,
                changelogs_path=changelogs_path,
                release_directory=release_directory,
                keep_release=keep_release,
                latest_link=not maintenance_name,
                file_system=self.__file_system,
                build_system=build_system,
                database_writer=self.__database_writer,
                database_reader=self.__database_reader,
                revision_control_system=self.rcs(),
                progress_callback=progress_callback,
            )

            # Write release information to the database
            yam_log.say("Updating database with build release info for the {} module".format(self.__module_name))
            self.__database_writer.write_module_build_release_information(
                module_name=self.__module_name,
                revision_tag=self.__tag,
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
                revision_tag=self.__tag,
                build_id=new_build_id,
                site_name=site_name,
                release_note_entry="",
                change_log_entry="",
                diff="",
            )

            return (self.__tag, new_build_id)
        else:
            raise savable_module.PreSaveException(
                "'{}' will not be saved since it has no changes".format(self.__module_name)
            )

    def pre_save_check(self, release_directory):
        """BranchedWorkModule implementation of pre_save_check()."""
        # branch_url = self._repository_url()
        # if self.rcs().vcs == "git":
        #    self.rcs().repo = Repo(self.__module_path)

        yam_log.say("\n++++ Doing pre_save check for the {} module".format(self.__module_name))
        """
        archive_url = work_module.dead_branches_url(
            module_name=self.__module_name,
            revision_tag=self.__tag,
            branch_id=self.__branch_id,
            database_reader=self.__database_reader,
        )
        """
        _pre_save_check(
            module_path=self.__module_path,
            module_name=self.__module_name,
            revision_tag=self.__revision_tag,
            branch_id=self.__branch_id,
            expected_url=self.module_branch_data(),  # branch_url,
            revision_control_system=self.rcs(),
            database_reader=self.__database_reader,
            database_writer=self.__database_writer,
            file_system=self.__file_system,
            release_directory=release_directory,
            non_existent_archive_url=self.module_branch_data().with_dead_branch(),  # archive_url,
        )
        yam_log.say("--- DONE - Doing pre_save check for the {} module".format(self.__module_name))

    def sync(
        self,
        commit,
        to_release=None,
        to_branch=None,
        progress_callback=lambda _: None,
    ):
        """Sync up to the latest revision of this module.

        Return a tuple (revision_tag, branch_id) representing the revision tag
        we synced to and the new branch ID.

        This involves branching from the latest revision and merging our
        changes into that branch. The old branch will be archived.

        """
        # Get the latest revision tag.
        yam_log.say("Get latest release tag for the {} module".format(self.__module_name))
        latest_revision_tag = self.__database_reader.latest_module_information(
            module_name=self.__module_name, release=to_release
        )["tag"]
        # print('MMMMMMMMMMMMMMMM', latest_revision_tag, self.__tag)

        # nothing to do if we are already on the desired branch
        if latest_revision_tag == self.__tag:
            # We already on the latest revision.
            # return (self.__tag, self.__branch_id)

            if not to_branch or to_branch == self.__branch_id:
                branchnm = self.__tag + "-" + self.__branch_id
                progress_callback(
                    "Module '{m}' already on sync up branch is {r}".format(m=self.__module_name, r=branchnm)
                )
                yam_log.say("Module '{m}' latest release is {r}".format(m=self.__module_name, r=branchnm))
                return (self.__tag, self.__branch_id)

        yam_log.say("Get dead branches url for the {} module".format(self.__module_name))
        """
        archive_url = work_module.dead_branches_url(
            module_name=self.__module_name,
            revision_tag=self.__tag,
            branch_id=self.__branch_id,
            database_reader=self.__database_reader,
        )
        """
        archive_url_data = self.module_branch_data().with_dead_branch()
        # do some basic checks
        _basic_check(
            module_path=self.__module_path,
            module_name=self.__module_name,
            expected_url=self.module_branch_data(),  # self._repository_url(),
            revision_control_system=self.rcs(),
            non_existent_archive_url=archive_url_data,  # archive_url,
        )

        # verify that the module does not have uncommitted files
        uncommitted_module_files = self.rcs().uncommitted_files(self.__module_path)
        if uncommitted_module_files:
            raise yam_exception.YamException(
                "Found uncommitted files: '{files}'; ".format(files=uncommitted_module_files)
            )

        progress_callback(
            "Branching off latest revision '{r}' for '{m}'".format(r=latest_revision_tag, m=self.__module_name)
        )

        # Create branch off of latest revision (if there is collision, create a
        # unique name).
        yam_log.say("Create branch off of latest revision for the {} module".format(self.__module_name))
        if not to_branch:
            to_branch = self.__branch_id
        merged_branch_id = _create_unique_branch(
            # module_name=self.__module_name,
            module_branch_data=self.module_branch_data(),
            revision_tag=latest_revision_tag,
            branch_id=to_branch,
            database_reader=self.__database_reader,
            database_writer=self.__database_writer,
            revision_control_system=self.rcs(),
        )

        progress_callback("Merging into the new branch '{}'".format(merged_branch_id))
        yam_log.say("Merging into the new branch '{}'".format(merged_branch_id))

        # Merge old branch into new branch (use reintegrateBranch()).
        yam_log.say("Merging the {} module into the main trunk".format(self.__module_name))
        """
        new_branch_url = work_module.feature_branches_url(
            module_name=self.__module_name,
            revision_tag=latest_revision_tag,
            branch_id=merged_branch_id,
            database_reader=self.__database_reader,
        )
        """
        new_branch_data = self.module_branch_data().with_release_tag(latest_revision_tag, merged_branch_id)
        # Reintegrate, but don't commit. Let the user handle committing.

        #        yam_log.say(
        #            "merged_branch_id ::: '{a}' MODULE PATH: '{b}' NEW_BRANCH_URL::: '{c}' ARCHINVE URL ::: '{d}'".format(a = merged_branch_id, b = self._module_path, c= new_branch_url, d =archive_url))

        self.rcs().reintegrate(
            path=self.__module_path,
            target_data=new_branch_data,
            archive_data=archive_url_data,
        )

        # Remove this branch from "branches" column of old tagged release.
        yam_log.say("Removeing branch from the database for the {} module".format(self.__module_name))
        self.__database_writer.rename_branch(
            module_name=self.__module_name,
            revision_tag=self.__tag,
            branch_id=self.__branch_id,
            new_branch_id=self.__branch_id + "-DEAD",
        )

        """
        print('TTTT',  self.__module_path)
        self.rcs().markBranchDead(wmpath=self.__module_path)
        """

        if commit:
            try:
                yam_log.say("Try committing the merged directory for the {} module".format(self.__module_name))
                self.rcs().check_in(path=self.__module_path, log_message="Sync")
            except yam_exception.YamException as exception:
                # If there is a merge conflict let the user handle it later.
                # We need to continue on and return the (tag, branch) tuple,
                # otherwise the sandbox configuration will be out of sync with
                # the module.
                progress_callback(str(exception))

        return (latest_revision_tag, merged_branch_id)

    def generate_log(self):
        """BranchedWorkModule implementation of savable_module.generate_log().

        Return a string contains the log of changes.

        """
        # if self.rcs().vcs == "git":
        #    return "FAKE LOG"
        previous_release_tag = self.__database_reader.latest_module_information(
            module_name=self.__module_name, release=None
        )["tag"]

        # print('prev tag=', previous_release_tag)
        """
        previous_release_url = work_module.releases_url(
            module_name=self.__module_name,
            revision_tag=previous_release_tag,
            database_reader=self.__database_reader,
        )

        # print('prev url=', previous_release_url)
        trunk_url = work_module.main_branch_url(
            module_name=self.__module_name,
            database_reader=self.__database_reader,
        )
        """

        # print('trunk url=', trunk_url)

        # get any commit messages on the main trunk
        trunk_logs = self.rcs().generate_logs_since_divergence(
            path=self.__module_path,
            # path_url=self.module_branch_data().with_release_tag(release_tag='main',
            #                                                   branch_id=None), # trunk_url,
            tagged_url=self.module_branch_data().with_release_tag(
                release_tag=previous_release_tag, branch_id=None
            ),  # previous_release_url,
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        )

        # print('trunk_logs=', trunk_logs)

        # get commit messages on the branch
        branch_logs = self.rcs().generate_logs_since_last_branch(
            path=self.__module_path,
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        )

        # print('branch_logs=', branch_logs)
        # combine the branch and trunk commit messages
        if trunk_logs:
            trunk_logs = trunk_logs.replace("Modules/%s/trunk/" % self.__module_name, "")
            return branch_logs + "\n\n" + trunk_logs
        else:
            return branch_logs

    # def _version_name(self):
    def _repo_tag_name(self):
        """Return version name instance."""
        """
        return work_module.feature_branches_name(
            module_name=self.__module_name,
            revision_tag=self.__tag,
            branch_id=self.__branch_id
        )
        """
        return self.module_branch_data().repoBranchTag()

    def _repository_urlOBSOLETE(self):
        """Return the full repository URL to this module instance."""
        # Using git, we don't want a url we want the branch info
        if self.__database_reader.vcs_type(self.__module_name) == "git":
            # return f"{self.__module_name},{self.__tag},{self.__branch_id}"#self.__module_path
            return self.__module_name
        return work_module.feature_branches_url(
            module_name=self.__module_name,
            revision_tag=self.__tag,
            branch_id=self.__branch_id,
            database_reader=self.__database_reader,
        )

    def _pre_check_out(self):
        """BranchedWorkModule implementation work_module._pre_check_out()."""
        #####repository_destination_url = self._repository_url()
        # print("REPO URL in BRANCHED_WORK_MOD: ", repository_destination_url)

        # create the desired branch if it does not already exist
        # print('JJJ0', self.module_branch_data().uri())
        # print('JJJ1', self.module_branch_data().dumpStr())
        _create_branch(
            revision_control_system=self.rcs(),
            database_reader=self.__database_reader,
            database_writer=self.__database_writer,
            # repository_destination_url=repository_destination_url,
            repository_destination_url=self.module_branch_data(),
            module_branch_data=self.module_branch_data(),
            # module_name=self.__module_name,
            # tag=self.__tag,
            # branch_id=self.__branch_id,
        )

        """
        release_parent_url = os.path.dirname(
            work_module.releases_url(
                module_name=self.__module_name,
                revision_tag=self.__tag,
                database_reader=self.__database_reader,
            )
        )
        """

        # This is for the case where we have alread have checked out a
        #  tagged work module in the sandbox. Don't worry about
        # changes since tagged check outs should not have changes. Just switch it to our branch.
        if self.rcs().working_copy_exists(self.__module_path):
            # and release_parent_url == os.path.dirname(self.rcs().url(self.__module_path)):
            # release_data = self.module_branch_data().with_branch_id(None)
            # wm_url = self.rcs().url(self.__module_path)
            # if release_parent_url == wm_url:

            # check if the checked out module is a tagged checkout of this module - and if so do the switch
            if self.rcs().isTaggedCheckout(self.__module_path):
                # switch the module to the branch
                self.rcs().switch_to_branch(
                    path=self.__module_path, branch_url=self.module_branch_data()  # repository_destination_url
                )

            # a tagged checkout typically has files checked out as read
            # only, so make them writeable
            for filename in self.rcs().list_files(self.__module_path):
                self.__file_system.make_writable(filename)


class NotLatestRevisionError(savable_module.PreSaveException):
    """Exception raised when trying to save a non-latest branch.

    It means it needs to be saved.

    """

    def __init__(self, module_name, current_revision_tag, latest_revision_tag):
        savable_module.PreSaveException.__init__(
            self,
            "Module '{module_name}' is on revision '{current}' instead of "
            "latest revision '{latest}'; ".format(
                module_name=module_name,
                current=current_revision_tag,
                latest=latest_revision_tag,
            )
            + "It needs to be synced up to the latest revision",
        )
        self.module_name = module_name


def filter_legal_branch_id(branch_id):
    """Return the branch ID if it is legal.

    Legal characters are alphanumeric characters, underscores, and hyphens.

    Raise an exception if the branch ID contains one or more illegal
    characters.

    """
    if not branch_id or not re.match("^[a-zA-Z0-9_-]+$", branch_id):
        raise yam_exception.YamException(
            "Illegal character(s) used in branch ID '{branch_id}'; ".format(branch_id=branch_id)
            + "legal IDs are composed of one or more alphanumeric "
            "characters, underscores, or hyphens"
        )
    elif branch_id.endswith("-DEAD"):
        raise yam_exception.YamException(
            "Branch ID '{branch_id}' must not end with the string '-DEAD' as "
            "it is reserved".format(branch_id=branch_id)
        )
    else:
        return branch_id


def _create_branch(
    revision_control_system,
    database_reader,
    database_writer,
    repository_destination_url: rcs.ModuleBranchData,
    module_branch_data: rcs.ModuleBranchData,
    # module_name,
    # tag,
    # branch_id,
):
    """Create a branch off of an existing release.

    If the branch already exists in the repository, we will use the
    existing branch.

    """
    vcs_type = module_branch_data._vcs_type
    module_name = module_branch_data._module_name
    release_tag = module_branch_data._release_tag
    branch_id = module_branch_data._branch_id

    # vcs = "git" if database_reader.vcs_type(module_name)=="git" else "svn"
    # Make sure that tag module we are branching off of exists

    # print('OKKK1')
    """
    if vcs_type=="git":
        # we really should be checking that the release tag exists, not whether the repo exists
        assert 0

        repository_source_url = work_module.main_branch_url(
            module_name=module_name,
            database_reader=database_reader,
            use_git=True
        )
    else:
        repository_source_url = work_module.releases_url(
        module_name=module_name,
        revision_tag=tag,
        database_reader=database_reader,
        )
    """

    # verify that the release to branch from actually exists
    # if not revision_control_system.exists(url=repository_source_url):
    # print('TTTTTTTT0', release_tag, branch_id)
    release_tag_data = module_branch_data.with_branch_id(None)
    if not revision_control_system.exists_module_branch(module_branch_data=release_tag_data):
        raise yam_exception.YamException(
            "Could not find tag '{tag}' for module '{module}' in repository "
            "'{repo}'".format(
                module=module_name, tag=release_tag, repo=release_tag_data.dumpStr()  # repository_source_url
            )
        )

    # print('LOKKK2')
    # Make sure we aren't making a branch module that was previously marked
    # dead.
    dead_branch_data = repository_destination_url.with_dead_branch()
    # if revision_control_system.exists(
    if revision_control_system.exists_module_branch(module_branch_data=dead_branch_data):
        # print('LOKKK2.4', dead_branch_data.uri())
        #         url=work_module.dead_branches_url(
        #             module_name=module_name,
        #             branch_id=filter_legal_branch_id(branch_id),
        #             revision_tag=tag,
        #             database_reader=database_reader,
        #         )
        #     ) and vcs!="git":
        raise yam_exception.YamException(
            "Branch '{name}-{tag}-{branch_id}' is marked as dead".format(
                name=module_name,
                tag=release_tag,
                branch_id=branch_id,
                #     name=module_name, tag=tag, branch_id=branch_id
            )
        )
    # print('XXXX', repository_source_url)
    # print('GGGG', repository_destination_url)

    # print('OKKK3')
    # Only create the branch if it hasn't been created in the past
    """
    if vcs == "git":
        if not revision_control_system.branch_exists(f"{module_name}-{tag}-{branch_id}"):
            revision_control_system.branch(
            source_url=repository_source_url,
            branch_name=f"{module_name},{tag},{branch_id}",
        )
    elif not revision_control_system.exists(url=repository_destination_url):
        revision_control_system.branch(
            source_url=repository_source_url,
            destination_url=repository_destination_url,
        )
    """

    # print('OKKK4', release_tag_data.uri(), module_branch_data.uri())
    # Only create the branch if it hasn't been created in the past
    # print('VVVV', repository_destination_url.dump())
    if not revision_control_system.exists_module_branch(module_branch_data=repository_destination_url):
        # create a new branch
        # print('CCCC', repository_destination_url.uri(), module_branch_data.uri())
        revision_control_system.branch(
            ####source_url=release_tag_data, #release_tag_data,  # repository_source_url,
            source_url=repository_destination_url.with_branch_id(None),
            destination_url=repository_destination_url,
        )
        # Update database with the new branch information
        database_writer.append_branch(module_name=module_name, revision_tag=release_tag, branch_id=branch_id)


def _create_unique_branch(
    # module_name,
    module_branch_data,
    revision_tag,
    branch_id,
    database_reader,
    database_writer,
    revision_control_system,
):
    """Create a branch.

    If one already exists with the specified branch ID, we
    will append a suffix to it to make it unique.

    Return the unique branch ID.

    """
    suffix = ""
    count = 0
    while True:
        new_branch_id = branch_id + suffix
        """
        new_branch_url = work_module.feature_branches_url(
            module_name=module_name,
            revision_tag=revision_tag,
            branch_id=new_branch_id,
            database_reader=database_reader,
        )
        """
        new_branch_data = module_branch_data.with_release_tag(revision_tag, new_branch_id)
        # if revision_control_system.exists(url=new_branch_url):
        if revision_control_system.exists_module_branch(new_branch_data):
            count += 1
            # suffix = '-merged{c}'.format(c=count)
            suffix = "{c}".format(c=count)
        else:
            break
    del branch_id

    # print('TTTT', module_branch_data.uri(), new_branch_data.uri())
    _create_branch(
        revision_control_system=revision_control_system,
        database_reader=database_reader,
        database_writer=database_writer,
        repository_destination_url=new_branch_data,  # new_branch_url,
        module_branch_data=module_branch_data,
        # module_name=module_name,
        # tag=revision_tag,
        # branch_id=new_branch_id,
    )

    return new_branch_id


def _basic_check(
    module_path,
    module_name,
    expected_url: rcs.ModuleBranchData,
    revision_control_system,
    non_existent_archive_url: rcs.ModuleBranchData,
):
    """Raise exception if working copy does not match specified parameters.

    Or if there are missing files ("ReleaseNotes", "ChangeLog").

    """
    yam_log.say("\n++++ Doing basic check for the {} module".format(module_name))

    module_saving_utils.basic_module_check(
        module_path=module_path,
        expected_url=expected_url,
        revision_control=revision_control_system,
    )

    # Check that there isn't already a dead branch for our branch
    # TODO: hacky way to get around the fact that we don't have a different folder for each branch
    # if revision_control_system.vcs == "git":
    #    non_existent_archive_url=non_existent_archive_url+"/"
    if revision_control_system.exists_module_branch(module_branch_data=non_existent_archive_url):
        raise savable_module.PreSaveException(
            "Module '{m}' is probably dead since it is found in the dead "
            "branches area '{url}'".format(m=module_name, url=non_existent_archive_url)
        )
    yam_log.say("--- DONE - Doing basic check for the {} module\n".format(module_name))


def _pre_save_check(
    module_path,
    module_name,
    revision_tag,
    branch_id,
    expected_url: rcs.ModuleBranchData,
    revision_control_system,
    database_reader,
    database_writer,
    file_system,
    release_directory,
    non_existent_archive_url: rcs.ModuleBranchData,
):
    """Raise appropriate exception based on error condition."""
    _basic_check(
        module_path=module_path,
        module_name=module_name,
        expected_url=expected_url,
        revision_control_system=revision_control_system,
        non_existent_archive_url=non_existent_archive_url,
    )

    # Check if we are on the latest revision.
    # print('JJJ _pre_save_check revision_tag=', revision_tag, branch_id)
    latest_revision_tag = database_reader.latest_module_information(module_name=module_name, release=None)["tag"]
    if not re.search("Maintenance", branch_id):
        if revision_tag != latest_revision_tag:
            raise NotLatestRevisionError(
                module_name=module_name,
                current_revision_tag=revision_tag,
                latest_revision_tag=latest_revision_tag,
            )

    module_saving_utils.pre_save_check(file_system=file_system, release_directory=release_directory)

    # We do not want to reintegrate the branch only to find out later that
    # we can not write to the database.
    _test_write_permission(
        module_name=module_name,
        revision_tag=revision_tag,
        branch_id=branch_id,
        database_writer=database_writer,
    )


def _test_write_permission(module_name, revision_tag, branch_id, database_writer):
    """Test writing to the database."""
    # This will raise exception on permission error. Otherwise, it will do
    # nothing by renaming a branch to itself.
    database_writer.rename_branch(
        module_name=module_name,
        revision_tag=revision_tag,
        branch_id=branch_id,
        new_branch_id=branch_id,
    )


class MergeConflict(yam_exception.YamException):
    """Exception raised when merge conflict occurs."""

    def __init__(self):
        yam_exception.YamException.__init__(
            self,
            "Merge conflict occurred. Note: uncommitted files in a renamed directory create a merge conflict",
        )


def merge_into_main(
    branch_id,
    module_path,
    main_branch_url: rcs.ModuleBranchData,
    archive_url: rcs.ModuleBranchData,
    revision_control,
    release_note_message,
):
    """Reintegrate (merge) back into the main branch.

    Then commit. Raise MergeConflict if necessary.

    """
    # print("MERGE DATAS:")
    # print(branch_id, module_path, main_branch_url, archive_url, release_note_message)
    from . import revision_control_system

    # if revision_control.vcs=="git":
    #    module_path = main_branch_url.repoPath()

    try:
        # print("OOO")
        # print(module_path)
        revision_control.reintegrate(
            path=module_path,
            target_data=main_branch_url,
            archive_data=archive_url,
        )
    except revision_control_system.ReintegrationException:  # pragma: NO COVER
        # If reintegration failed, then we are already switched to the
        # main branch.
        raise MergeConflict  # pragma: NO COVER

    if release_note_message:
        log_message = release_note_message
    else:
        # TODO: default log message is not correct. branch_id is not the actual branch name.
        log_message = "pyam: Reintegrate '{branch}' back into main " "branch".format(branch=branch_id)

    try:
        # print('KKKKKKKKK3', os.system(f'git -P -C {module_path} status'))
        revision_control.check_in(path=module_path, log_message=log_message, wmpath=module_path)
    except yam_exception.YamException:
        # At this point, we are on the main branch.
        raise MergeConflict
