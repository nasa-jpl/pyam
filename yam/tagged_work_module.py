"""Contains the TaggedWorkModule class."""

from __future__ import absolute_import

import os

from . import module_saving_utils
from . import savable_module
from . import work_module
from . import yam_log
from . import revision_control_system as rcs


class TaggedWorkModule(work_module.WorkModule):
    """A WorkModule that is checked out from an existing tagged release.

    The checked out code is read-only and commits cannot be made.

    """

    def __init__(
        self,
        module_name,
        tag,
        revision_control_system,
        parent_directory,
        database_reader,
        database_writer,
        file_system,
    ):
        """Initialize.

        Source code will not be modifiable as we will not be branching
        off our own branch.

        """
        vcs_type = database_reader.vcs_type(module_name)
        vcs_root = database_reader.module_repository_url(module_name)
        module_branch_data = rcs.ModuleBranchData(
            module_name=module_name, release_tag=tag, branch_id=None, vcs_type=vcs_type, vcs_root=vcs_root
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
        self.__database_reader = database_reader
        self.__database_writer = database_writer
        self.__file_system = file_system
        """
        self.__revision_control_system = revision_control_system[vcs_type]
        """
        self.__module_name = module_name
        self.__module_path = os.path.join(parent_directory, module_name)

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
        """TaggedWorkModule implementation of savable_module.save().

        Return the new revision tag.

        """
        # TODO: Move this to client so that main_work_module benefits too.
        release_note_message = module_saving_utils.format_message(release_note_message)

        self.pre_save_check(release_directory)

        date_time = self.__database_reader.local_date_time()

        if release_directory:
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
            readmes = module_saving_utils.module_readmes(self.__module_path)
            destination_path = module_saving_utils.move_module_for_release(
                module_path=self.__module_path,
                module_name=self.__module_name,
                new_revision_tag=self.__tag,
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

            progress_callback("Updating database")

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

            # create links for ChangeLog etc files
            # print("LLLL", changelogs_path)
            if release_directory and changelogs_path:
                for f in ["ChangeLog", "ReleaseNotes"]:
                    # print('TTTT', destination_path + '/' + f)
                    if self.__file_system.path_exists(destination_path + "/" + f):
                        progress_callback("Creating symbolic links for {} file".format(f))
                        dest_link = "module-{m}-{r}-Build{b}-{f}".format(
                            m=self.__module_name, r=self.__tag, b=new_build_id, f=f
                        )
                        if self.__file_system.path_exists(changelogs_path + "/" + dest_link):
                            os.remove(changelogs_path + "/" + dest_link)
                        os.symlink(
                            destination_path + "/" + f,
                            changelogs_path + "/" + dest_link,
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

    def generate_log(self):
        """TaggedWorkModule implementation of savable_module.generate_log().

        Return empty string: these can only be saved as build releases, so we
        aren't actually making any changes

        """
        return ""

    # def _version_name(self):
    def _repo_tag_name(self):
        """Return version name  instance."""
        return self.module_branch_data().repoReleaseTag()
        """
        return work_module.releases_name(
            module_name=self.__module_name,
            revision_tag=self.__tag
        )
        """

    def _repository_urlOBSOLETE(self):
        """Return full repository URL to this module instance."""
        return work_module.releases_url(
            module_name=self.__module_name,
            revision_tag=self.__tag,
            database_reader=self.__database_reader,
        )

    def _trunk_urlOBSOLETE(self, module_name):
        """Return full repository URL to this module trunk."""
        return work_module.main_branch_url(module_name=module_name, database_reader=self.__database_reader)

    def _post_check_out(self, module_directory):
        """Implementation of work_module._post_check_out().

        Change permissions after checking out.

        """
        for filename in self.rcs().list_files(module_directory):
            # print(filename)
            self.__file_system.make_read_only(filename)

    def pre_save_check(self, release_directory):
        """TaggedWorkModule implementation of pre_save_check().

        The logic is described here:

          https://dartslab.jpl.nasa.gov/dlabbugs/show_bug.cgi?id=250

        In that bug report Abhi says:

          If a tagged version of a module is checked out as a work module, running 'pyam
          save' on it errors out saying that one cannot save a tagged work module. This
          error actually does not make sense, and is currently breaking build-releases
          (since pyam-build is currently set up to check out tagged work modules).

          Clearly we do not want to release a tagged work module if it is behind or not
          in sync with the main trunk. If the tagged module corresponds to the latest
          release, then it should be in sync with the main trunk. In this case, pyam
          save should allow saving this module to make a build release. Note that
          commits are disallowed (via a commit hook) for tagged work modules, so it can
          never be ahead of the main trunk.

          The only times we should disallow saving of a tagged work module is when:

          a) the tagged module does not correspond to the latest release and is hence
          behind the main trunk.

          b) there happen to be commits on the main trunk (not the recommended way),
          which cause the tagged module to therefore be behind the main trunk.

          So we need to modify 'pyam save' to check for the above two conditions for a
          tagged work module, and if we are good with these, then the save should
          proceed. The normal save process should find that there are no new changes in
          the tagged module, and should proceed to make a build release.

        Thus this functions tests the conditions a and b above

        """

        # branch_url = self._repository_url()
        # trunk_url = self._trunk_url(module_name=self.__module_name)

        yam_log.say("\n++++ Doing pre_save check for the {} module".format(self.__module_name))

        module_saving_utils.basic_module_check(
            module_path=self.__module_path,
            expected_url=self.module_branch_data(),  # branch_url,
            revision_control=self.rcs(),
        )

        # Check if we are on the latest revision.
        latest_revision_tag = self.__database_reader.latest_module_information(module_name=self.__module_name)["tag"]
        if self.__tag != latest_revision_tag:
            msg = "Checked out module '{module}' is for '{release}' release ', ".format(
                release=self.__tag, module=self.__module_name
            ) + "while we are expecting the latest '{release} release'".format(release=latest_revision_tag)
            raise savable_module.PreSaveException(msg)

        # Check that there aren't any extra commits on trunk. We (the release)
        # should be ahead of trunk
        self.rcs().hasMainTrunkCommits(self.module_branch_data())

        #         pysvnclient = self.rcs()._client()
        #         revision_revision = pysvnclient.log(branch_url, limit=1)[
        #             0
        #         ].revision.number
        #         trunk_revision = pysvnclient.log(trunk_url, limit=1)[0].revision.number
        #         if trunk_revision > revision_revision:
        """
                msg = "Module '{module}' has main trunk commits - latest {release} release SVN tag is '{current}', ".format(
                    release=self.__tag,
                    module=self.__module_name,
                    current=revision_revision,
                ) + "while trunk SVN tag is '{trunk}'".format(
                    trunk=trunk_revision
                )
            raise savable_module.PreSaveException(msg)
        """
        module_saving_utils.pre_save_check(file_system=self.__file_system, release_directory=release_directory)
        yam_log.say("--- DONE - Doing pre_save check for the {} module".format(self.__module_name))

    def sync(self, to_release=None, to_branch=None, progress_callback=lambda _: None):
        """Sync up to the latest revision of this module.

        Return a tuple (revision_tag, branch_id) representing the revision tag
        we synced to and the new branch ID.

        This involves switching to the latest revision in place.

        """
        # print('OKKK0')
        # Get the latest revision tag.
        latest_revision_tag = self.__database_reader.latest_module_information(
            module_name=self.__module_name, release=to_release
        )["tag"]
        if latest_revision_tag == self.__tag and not to_branch:
            # We already on the latest revision.
            progress_callback(
                "Module '{m}' already has the {r} latest version".format(m=self.__module_name, r=self.__tag)
            )
            return (self.__tag, None)

        # print('OKKK1')
        # Make sure we have the expected repository URL.
        if not self.rcs().isTaggedCheckout(self.__module_path):

            # TODO: Move RepositoryURLMismatchError to a different module.
            expected_url = self.module_branch_data().uri()
            actual_url = self.rcs().url(path=self.__module_path)
            # actual_url = self.rcs().url(path=self.__module_path)
            # expected_url = self._repository_url()
            # if actual_url != expected_url:
            # TODO: Move RepositoryURLMismatchError to a different module.
            raise savable_module.RepositoryURLMismatchError(expected_url=expected_url, actual_url=actual_url)

        # print('OKKK2')
        new_url_data = None
        if not to_branch:
            # print('OKKK2.1')
            # switch to the latest release if not there already
            if latest_revision_tag != self.__tag:
                """
                new_url = work_module.releases_url(
                    module_name=self.__module_name,
                    revision_tag=latest_revision_tag,
                    database_reader=self.__database_reader,
                )
                """
                # print('OKKK3')
                new_url_data = self.module_branch_data().with_release_tag(latest_revision_tag)
                progress_callback(
                    "Switching to latest '{r}' revision for '{m}' module".format(
                        r=latest_revision_tag, m=self.__module_name
                    )
                )
                self.rcs().switch_to_tag(path=self.__module_path, tag_url=new_url_data)

        else:
            # print('OKKK2.2')
            from . import branched_work_module

            # Create branch off of latest revision (if there is collision, create a
            # unique name).
            yam_log.say("Create branch off of latest revision for the {} module".format(self.__module_name))
            # print('OKKK2.3', latest_revision_tag, to_branch)
            new_branch_id = branched_work_module._create_unique_branch(
                # module_name=self.__module_name,
                module_branch_data=self.module_branch_data(),
                revision_tag=latest_revision_tag,
                branch_id=to_branch,
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
                revision_control_system=self.rcs(),
            )

            # print('OKKK2.4')
            branchnm = self.__module_name + "-" + latest_revision_tag + "-" + new_branch_id
            progress_callback("Switching to the new '{}' branch for '{}' module".format(branchnm, self.__module_name))
            yam_log.say("Switching to the new '{}' branch for '{} module'".format(branchnm, self.__module_name))

            # Merge old branch into new branch (use reintegrateBranch()).
            # yam_log.say('Merging the {} module into the main trunk'.format(self.__module_name))
            """
            new_url = work_module.feature_branches_url(
                module_name=self.__module_name,
                revision_tag=latest_revision_tag,
                branch_id=new_branch_id,
                database_reader=self.__database_reader,
            )
            """
            # print('OKKK4')
            new_url_data = self.module_branch_data().with_release_tag(latest_revision_tag, new_branch_id)

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

        return (latest_revision_tag, to_branch)
