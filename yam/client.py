"""Contains Client class."""

from __future__ import absolute_import

# from git import Repo
# from pathlib import Path
import collections
import os
import textwrap
import shutil


from . import branched_work_module
from . import loose_sandbox
from . import main_package_sandbox
from . import main_work_module
from . import module_saving_utils
from . import name_utils
from . import package_sandbox
from . import revision_tag_utils
from . import saving_utils
from . import tagged_package_sandbox
from . import tagged_work_module
from . import work_module
from . import yam_exception
from . import yam_log
from . import configuration_reader
from . import module_configuration_utils
from .module import WorkModuleType
from . import revision_control_system as rcs
from functools import partial
from typing import Optional


###############################################
# some constants (should be moved to a configuration file so users can customize

# list of module relative paths for files whose commit diffs should not
# be included in module release emails sent out to users
##MODULE_DIFFS_IGNORE_PATHS = ['swig/docstrings.i']

###############################################


class Client(object):
    """Class that does executes the top level Yam commands."""

    def __init__(
        self,
        database_reader,
        database_writer,
        revision_control_system,
        build_system,
        file_system,
        default_repository_url,
        configuration_reader,
        configuration_writer,
        default_branch,
    ):
        self.__database_reader = database_reader
        self.__database_writer = database_writer
        self.__revision_control_system = revision_control_system
        self.__build_system = build_system
        self.__file_system = file_system
        self.__default_repository_url = default_repository_url
        self.__configuration_reader = configuration_reader
        self.__configuration_writer = configuration_writer
        self.__default_branch = default_branch

        # if True, then git will create bare module repos. This member
        # has no effect for SVN
        self._bare_repo = True

    def build_modules(self, module_names, sandbox_root_directory):
        """Build a module based on the contents of YAM.config."""
        self.__build_system.build(module_names=module_names, sandbox_directory=sandbox_root_directory)

    def reader(self):
        return self.__database_reader

    def set_revision_control_system(self, rcs):
        """
        Set the dictionary of different version control systems (svn/git)
        """
        self.__revision_control_system = rcs

    def check_out_modules(
        self,
        module_names,
        sandbox_root_directory,
        release_directory,
        relink=True,
        progress_callback=lambda _: None,
    ):
        # print("CHECKING OUT: ", module_names)
        # print("SANDBOX_ROOT_DIR: ", sandbox_root_directory)
        # print("RELEASE_DIR: ", release_directory)
        """Check out modules based on the contents of YAM.config."""
        _check_release_directory(release_directory, self.__file_system, require=False)

        _check_sandbox_directory(sandbox_root_directory, self.__file_system)

        for name in module_names:
            tag, branch_id = self.__configuration_reader.read_work_module_information(
                configuration_filename=os.path.join(sandbox_root_directory, "YAM.config"),
                module_name=name,
            )
            # vcs_type = self.__database_reader.vcs_type(name)
            mod_inst = self._module_instance(
                module_name=name, sandbox_root_directory=sandbox_root_directory, tag=tag, branch_id=branch_id
            )
            """
            if vcs_type == "git":

                module_url = work_module.main_branch_url(
                    module_name=name, database_reader=self.__database_reader, use_git=True
                )
                #print("MOD URL: ", module_url)
                repo=Repo(module_url,search_parent_directories=True)
                self.__revision_control_system.repo = repo
                self.__revision_control_system.branch_id = branch_id
                self.__revision_control_system.tag = tag
                mod_inst.vcs="git"
            """
            mod_inst.check_out(progress_callback)
        if relink:
            self.__build_system.remove_links(
                module_names=module_names,
                sandbox_directory=sandbox_root_directory,
                release_directory=release_directory,
            )

            self.__build_system.make_links(
                module_names=module_names,
                sandbox_directory=sandbox_root_directory,
                release_directory=release_directory,
            )

    def _module_instance(self, module_name, sandbox_root_directory, tag, branch_id):
        """Return Yam module object.

        Return a module with the specified name given the sandbox
        configuration.

        """
        _check_sandbox_directory(sandbox_root_directory, self.__file_system)

        # tag, branch_id = self.__configuration_reader.read_work_module_information(
        #    configuration_filename=os.path.join(
        #        sandbox_root_directory, "YAM.config"
        #    ),
        #    module_name=module_name,
        # )

        # print('CHECKOUT', module_name, 'tag=', tag, 'branch_id=', branch_id)

        if branch_id and tag:
            module = branched_work_module.BranchedWorkModule(
                module_name=module_name,
                tag=tag,
                branch_id=branch_id,
                file_system=self.__file_system,
                revision_control_system=self.__revision_control_system,
                parent_directory=os.path.join(sandbox_root_directory, "src"),
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
            )
        elif not branch_id and tag:
            module = tagged_work_module.TaggedWorkModule(
                module_name=module_name,
                tag=tag,
                file_system=self.__file_system,
                revision_control_system=self.__revision_control_system,
                parent_directory=os.path.join(sandbox_root_directory, "src"),
                database_reader=self.__database_reader,
                database_writer=None,
            )
        elif branch_id and not tag:
            raise yam_exception.YamException(
                "In the sandbox configuration, if a branch ID is " "specified, a revision tag must also be specified"
            )
        else:
            assert not branch_id
            assert not tag

            module = main_work_module.MainWorkModule(
                module_name=module_name,
                revision_control_system=self.__revision_control_system,
                parent_directory=os.path.join(sandbox_root_directory, "src"),
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
                file_system=self.__file_system,
            )

        # if self.__database_reader.vcs_type(module_name) == "git":
        #    return module, branch_id, tag
        return module

    def save_modules(
        self,
        module_names,
        sandbox_root_directory,
        release_note_message,
        username,
        release_directory,
        keep_release,
        changelogs_path,
        operating_system_name,
        site_name,
        host_ip,
        empty_log_filter=lambda x: x,
        bug_id=None,
        preferred_build_id=None,
        release_information_callback=(
            lambda module_name, revision_tag, build_id, site_name, release_note_entry, change_log_entry, diff: None
        ),
        progress_callback=lambda _: None,
        check_out_again_after_saving=False,
        check_out_tagged=False,
        check_dangling_links=True,
        check_link_modules=True,
        pre_save_hooks=True,
        build=True,
        mkdiff=True,
    ):
        """Rebuild a module based on the contents of YAM.config."""

        # if the option to save module releases to the module release
        # area is enabled, verify that we have a valid release directory
        if keep_release:
            if not release_directory:
                raise ReleaseDirectoryException(
                    "Release directory has not been specified even though the keep release option is enabled."
                )

            # verify that the release directory is valid if we plan to save
            # the released module to the release area
            _check_release_directory(release_directory, self.__file_system, require=False)

        # if not release_directory:
        if not release_directory:
            check_out_again_after_saving = True

        # --------------------------------------
        progress_callback("Checking validity of working copy")
        yam_log.say("\n>>> Verifying that %s work module directories exist" % module_names)
        """
        _check_working_copy(
            sandbox_root_directory=sandbox_root_directory,
            module_names=module_names,
            revision_control_system=self.__revision_control_system,
        )
        """

        # verify that each of the modules being saved is a valid part of
        # the vcs repository
        module_vcs_types = {}
        for m in module_names:
            vcs_type = self.__database_reader.vcs_type(m)
            if not vcs_type:
                vcs_type = "svn"
            module_vcs_types[m] = vcs_type
            work_module.check_working_copy(
                sandbox_root_directory=sandbox_root_directory,
                module_name=m,
                revision_control_system=self.__revision_control_system[vcs_type],
            )

        yam_log.say("<<< DONE - Verifying that %s work module directories exist\n" % module_names)

        # --------------------------------------
        configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

        # --------------------------------------
        # verify that all version controlled files are committed
        """
        raise_exception_on_uncommitted_files(
            revision_control_system=self.__revision_control_system,
            module_names=module_names,
            sandbox_root_directory=sandbox_root_directory,
        )
        """
        for m in module_names:
            vcs_type = module_vcs_types[m]
            work_module.raise_exception_on_uncommitted_files(
                revision_control_system=self.__revision_control_system[vcs_type],
                module_name=m,
                sandbox_root_directory=sandbox_root_directory,
            )

        # --------------------------------------
        if pre_save_hooks:
            progress_callback("Running pre-save hooks")
            yam_log.say("\n>>> Running pre-save hooks for %s work module" % module_names)
            raise_exception_on_pre_save_hook_failure(
                module_names=module_names,
                sandbox_root_directory=sandbox_root_directory,
                file_system=self.__file_system,
            )
            yam_log.say("<<< DONE - Running pre-save hooks for %s work module\n" % module_names)

        def _savable_module(name):
            """Return a Yam module object.

            The instance is based on name and sandbox configuration.

            """
            tag, branch_id = self.__configuration_reader.read_work_module_information(
                configuration_filename=configuration_filename, module_name=name
            )
            # print("SSSS")
            # print(sandbox_root_directory)

            if tag and not branch_id:
                return tagged_work_module.TaggedWorkModule(
                    module_name=name,
                    tag=tag,
                    revision_control_system=self.__revision_control_system,
                    parent_directory=os.path.join(sandbox_root_directory, "src"),
                    database_reader=self.__database_reader,
                    database_writer=self.__database_writer,
                    file_system=self.__file_system,
                )
            elif not tag and not branch_id:
                return main_work_module.MainWorkModule(
                    module_name=name,
                    revision_control_system=self.__revision_control_system,
                    parent_directory=os.path.join(sandbox_root_directory, "src"),
                    database_reader=self.__database_reader,
                    database_writer=self.__database_writer,
                    file_system=self.__file_system,
                )
            else:
                assert tag
                assert branch_id
                return branched_work_module.BranchedWorkModule(
                    module_name=name,
                    tag=tag,
                    branch_id=branch_id,
                    revision_control_system=self.__revision_control_system,
                    parent_directory=os.path.join(sandbox_root_directory, "src"),
                    database_reader=self.__database_reader,
                    database_writer=self.__database_writer,
                    file_system=self.__file_system,
                )

        def _module_message_tuple(name):
            """Generate a message with empty_log_filter."""
            module = _savable_module(name)
            vcs_type = module_vcs_types[name]

            # Check for None explicitly since we allow empty strings.
            if release_note_message is None:
                yam_log.say("\n>>> Generating release log message for %s work module" % name)

                message = _generate_release_note_message(
                    log_filter=empty_log_filter,
                    reference_log=module.generate_log(),
                    name=name,
                )
                yam_log.say("<<< DONE - Generating release log message for %s work module\n" % name)
            else:
                message = release_note_message

            return (module, message, vcs_type)

        def _save_modules_and_collect_status(module_message_tuple_dictionary):
            """Save modules and collect status."""
            new_revision_tag_and_build_id_dictionary = {}
            save_exceptions = {}

            for name, module_message_tuple in module_message_tuple_dictionary.items():

                desired_build_id = preferred_build_id or self.desired_build_id(
                    module_name=name, release_directory=release_directory
                )

                module, message, vcs_type = module_message_tuple
                try:

                    yam_log.say("\n>>> Saving %s work module" % name)
                    new_revision_tag_and_build_id_dictionary[name] = module.save(
                        release_note_message=message,
                        username=username,
                        release_directory=release_directory,
                        keep_release=keep_release,
                        changelogs_path=changelogs_path,
                        build_system=self.__build_system,
                        operating_system_name=operating_system_name,
                        site_name=site_name,
                        host_ip=host_ip,
                        bug_id=bug_id,
                        desired_build_id=desired_build_id,
                        release_information_callback=(release_information_callback),
                        progress_callback=progress_callback,
                        mkdiff=mkdiff,
                    )
                    yam_log.say("<<< DONE - Saving %s work module\n" % name)
                except branched_work_module.MergeConflict as merge_conflict:
                    save_exceptions[name] = merge_conflict

                    self._modify_configuration_for_merge_conflict(
                        sandbox_root_directory=sandbox_root_directory,
                        configuration_filename=configuration_filename,
                        merge_conflict=merge_conflict,
                        name=name,
                        vcs_type=vcs_type,
                    )
                except yam_exception.YamException as e:
                    save_exceptions[name] = e

            return new_revision_tag_and_build_id_dictionary, save_exceptions

        def _update_configuration(new_revision_tag_and_build_id_dictionary, save_exceptions):
            """Update the sandbox configuration."""

            module_dictionary = self.__configuration_reader.read_sandbox_configuration(
                configuration_filename=configuration_filename
            )

            # update the module information using the new module data
            module_configuration_utils.module_save_update_configuration(
                module_dictionary,
                new_revision_tag_and_build_id_dictionary,
                check_out_again_after_saving,
                check_out_tagged,
                self.__default_branch,
            )
            """

            for (
                name,
                new_revision_tag_and_build_id,
            ) in new_revision_tag_and_build_id_dictionary.items():
                if check_out_again_after_saving:
                    if check_out_tagged:
                        module_dictionary["work_modules"][name] = (
                            new_revision_tag_and_build_id[0],
                            None,
                        )
                    else:
                        # Update the revision tag if it is a branched work
                        # module
                        if module_dictionary["work_modules"][name] != (
                            None,
                            None,
                        ):
                            module_dictionary["work_modules"][name] = (
                                new_revision_tag_and_build_id[0],
                                self.__default_branch,
                            )
                else:
                    # Update the configuration. The work module should become a
                    # link module with an updated tag.
                    del module_dictionary["work_modules"][name]
                    module_dictionary["link_modules"][name] = list(
                        new_revision_tag_and_build_id
                    ) + [None, None]

            """

            if new_revision_tag_and_build_id_dictionary:
                # Write the updated the configuration.
                self.__configuration_writer.write_sandbox_configuration(
                    configuration_filename=configuration_filename,
                    work_module_dictionary=module_dictionary["work_modules"],
                    link_module_dictionary=module_dictionary["link_modules"],
                    default_branch=self.__default_branch,
                )

                if check_out_again_after_saving:
                    self.check_out_modules(
                        module_names=list(new_revision_tag_and_build_id_dictionary),
                        sandbox_root_directory=sandbox_root_directory,
                        release_directory=release_directory,
                        progress_callback=progress_callback,
                    )

                self.relink_modules(
                    module_names=list(new_revision_tag_and_build_id_dictionary),
                    sandbox_directory=sandbox_root_directory,
                    release_directory=release_directory,
                )

                if check_out_again_after_saving and build:
                    progress_callback("Building {}".format(list(new_revision_tag_and_build_id_dictionary)))

                    self.build_modules(
                        module_names=list(new_revision_tag_and_build_id_dictionary),
                        sandbox_root_directory=sandbox_root_directory,
                    )

            if save_exceptions:
                raise SaveException(save_exception_dictionary=save_exceptions)

        # --------------------------------------
        # check whether these are maintenance releases or regular
        # releases and verify that we do not have a mix
        def _check_maintenance_release(module_objs):
            """
            return True if all these work modules being released are on regular
            branches for a regular release, and False if they are on on
            maintenance branches for maintenance releases. Throw an error if we
            have a mix.
            """

            regular = []
            maintenance = []
            for m in module_objs:
                if isinstance(m, branched_work_module.BranchedWorkModule):
                    maint_name, main_num = m.maintenanceBranchTuple()
                    if maint_name:
                        maintenance.append(m)
                    else:
                        regular.append(m)
                else:
                    regular.append(m)

            # print('maint', maintenance)
            # print('regular', regular)
            if maintenance and regular:
                raise ValueError("Cannot make %s regular and %s maintenance module releases together.")

            if maintenance:
                return True
            else:
                return False

        # --------------------------------------
        # Do pre-save checks explicitly for better usability when saving
        # multiple modules.
        module_objs = [_savable_module(name) for name in module_names]

        # verify that we have either just regular saves or just
        # maintenance saves, and not a mix
        progress_callback("Verifying that we are not mixing regular and maintenance module releases")
        yam_log.say("Verifying that we are not mixing regular and maintenance module releases")
        maintenance = _check_maintenance_release(module_objs)
        if maintenance:
            progress_callback("Making maintenance releases")

        # --------------------------------------
        if check_link_modules:
            if maintenance:
                progress_callback("Skipping link modules are up to date check")
            else:
                progress_callback("Checking that link modules are up to date")
                self.raise_exception_on_out_of_date_link_modules(
                    configuration_filename=configuration_filename,
                    release_directory=release_directory,
                )

        # --------------------------------------
        if check_dangling_links:
            progress_callback("Checking for dangling links")
            yam_log.say("\n>>> Checking dangling links for %s work module" % module_names)
            raise_exception_on_dangling_links(
                module_names=module_names,
                sandbox_root_directory=sandbox_root_directory,
                file_system=self.__file_system,
            )
            yam_log.say("<<< DONE: Checking dangling links for %s work module\n" % module_names)

        # --------------------------------------
        for module in module_objs:
            yam_log.say("\n>>> Doing pre-save checks for %s work module" % module)

            module.pre_save_check(release_directory)
            yam_log.say("<<< DONE - Doing pre-save checks for %s work module\n" % module)

        # Generate all messages before doing any saving.
        # Then save and update configuration.

        _update_configuration(
            *_save_modules_and_collect_status(
                collections.OrderedDict((name, _module_message_tuple(name)) for name in module_names)
            )
        )

    def _modify_configuration_for_merge_conflict(
        self, sandbox_root_directory, configuration_filename, merge_conflict, name, vcs_type
    ):
        """Edit sandbox configuration to reflect the working copy.

        We only need to do this if the conflict occurred after we moved
        to the main branch.

        """
        module_path = os.path.join(sandbox_root_directory, "src", name)

        if work_module.on_main_branch(module_path, self.__revision_control_system[vcs_type]):
            module_dictionary = self.__configuration_reader.read_sandbox_configuration(
                configuration_filename=configuration_filename
            )

            # module_dictionary["work_modules"][name] = (None, None)
            # switch the module to the main trunk
            module_configuration_utils.work_module_to_main(module_dictionary, name)

            self.__configuration_writer.write_sandbox_configuration(
                configuration_filename=configuration_filename,
                work_module_dictionary=module_dictionary["work_modules"],
                link_module_dictionary=module_dictionary["link_modules"],
                default_branch=self.__default_branch,
            )

    def sync_module(
        self,
        module_name,
        sandbox_root_directory,
        commit,
        to_release=None,
        to_branch=None,
        allow_main=False,
        progress_callback=lambda _: None,
    ):
        """Sync a module to the specified revision.

        Return True if something gets modified.

        """
        # print('SYNC', module_name, to_release)
        _check_sandbox_directory(path=sandbox_root_directory, file_system=self.__file_system)

        configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

        tag, branch_id = self.__configuration_reader.read_work_module_information(
            configuration_filename=configuration_filename,
            module_name=module_name,
        )

        if tag and not branch_id:
            # this is tagged check out
            module = tagged_work_module.TaggedWorkModule(
                module_name=module_name,
                tag=tag,
                file_system=self.__file_system,
                revision_control_system=self.__revision_control_system,
                parent_directory=os.path.join(sandbox_root_directory, "src"),
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
            )

            if to_branch == "-":
                to_branch = ""

            new_tag_and_branch = module.sync(
                to_release=to_release,
                to_branch=to_branch,
                progress_callback=progress_callback,
            )

            if new_tag_and_branch != (tag, branch_id):
                self._update_configuration(
                    module_name=module_name,
                    new_tag_and_branch=new_tag_and_branch,
                    configuration_filename=configuration_filename,
                )

                return True
        elif not tag and not branch_id:
            # this is a main trunk checkout
            if allow_main:
                module = main_work_module.MainWorkModule(
                    module_name=module_name,
                    file_system=self.__file_system,
                    revision_control_system=self.__revision_control_system,
                    parent_directory=os.path.join(sandbox_root_directory, "src"),
                    database_reader=self.__database_reader,
                    database_writer=self.__database_writer,
                )

                if to_branch is None:
                    to_branch = self.__default_branch
                elif to_branch == "-":
                    to_branch = ""
                # print('TTT', to_release, to_branch)
                new_tag_and_branch = module.sync(
                    to_release=to_release,
                    to_branch=to_branch,
                    progress_callback=progress_callback,
                )

                self._update_configuration(
                    module_name=module_name,
                    new_tag_and_branch=new_tag_and_branch,
                    configuration_filename=configuration_filename,
                )

                return True

            else:
                raise WorkModuleTypeException(
                    "Main-branch module cannot be synced; only branched modules " "can be synced"
                )
        else:
            # this checkout is on a branch
            module = branched_work_module.BranchedWorkModule(
                module_name=module_name,
                tag=tag,
                branch_id=branch_id,
                revision_control_system=self.__revision_control_system,
                parent_directory=os.path.join(sandbox_root_directory, "src"),
                database_reader=self.__database_reader,
                database_writer=self.__database_writer,
                file_system=self.__file_system,
            )

            new_tag_and_branch = module.sync(
                commit=commit,
                to_release=to_release,
                to_branch=to_branch,
                progress_callback=progress_callback,
            )

            if new_tag_and_branch != (tag, branch_id):
                self._update_configuration(
                    module_name=module_name,
                    new_tag_and_branch=new_tag_and_branch,
                    configuration_filename=configuration_filename,
                )

                return True

    def _update_configuration(self, module_name, new_tag_and_branch, configuration_filename):
        """Update the tag/branch for a work module."""
        module_dictionary = self.__configuration_reader.read_sandbox_configuration(
            configuration_filename=configuration_filename
        )

        # module_dictionary["work_modules"][module_name] = new_tag_and_branch
        # update the work module to the new tag and branch
        module_configuration_utils.work_module_tag_branch(module_dictionary, module_name, new_tag_and_branch)

        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=configuration_filename,
            work_module_dictionary=module_dictionary["work_modules"],
            link_module_dictionary=module_dictionary["link_modules"],
            default_branch=self.__default_branch,
        )

    def module_history(self, module_names, limit, before, after, ascending):
        """Return latest module information."""
        return module_saving_utils.module_history(
            module_names=module_names,
            limit=limit,
            before=before,
            after=after,
            ascending=ascending,
            database_reader=self.__database_reader,
        )

    def latest_module_information(self, module_name, release, release_directory):
        """Return latest module information."""
        # print('TTTTT release=', module_name, release)
        return module_saving_utils.latest_module_information(
            module_name=module_name,
            release=release,
            release_directory=release_directory,
            database_reader=self.__database_reader,
            file_system=self.__file_system,
        )

    def latest_module_information_as_of(self, module_name, date=None):
        """Return module information that was latest as of the given date."""
        return self.__database_reader.latest_module_information_as_of(module_name, release=None, date=date)

    def latest_package_revision_tag(self, package_name):
        """Return latest package revision tag."""
        return self.__database_reader.latest_package_revision_tag(package_name)

    def obsolete_builds(self, release_directory):
        """Return names of modules whose builds are obsolete."""
        obsolete = self.__database_reader.obsolete_builds()
        if release_directory:
            return sorted(
                obsolete
                | set(
                    module
                    for module in self.module_names()
                    if self.latest_module_information(module, None, release_directory)["missing"]
                )
            )
        else:
            return sorted(obsolete)

    def desired_build_id(self, module_name, release_directory):
        """Return desired build ID based on what is missing in release area."""
        desired_build_id = None
        if release_directory:
            latest = self.latest_module_information(
                module_name=module_name,
                release=None,  # latest
                release_directory=release_directory,
            )
            if latest["missing"]:
                desired_build_id = self.__database_reader.latest_module_information(module_name=module_name)["build"]
        return desired_build_id

    def module_dependencies(self, module_names, recursive=False):
        """Return a module's build dependencies."""
        if not recursive:
            result = set()
            for m in module_names:
                result = result.union(self.__database_reader.module_dependencies(m))
        else:
            import itertools

            result = set(
                itertools.chain(
                    *[_recursive_dependencies(m, self.__database_reader.module_dependencies) for m in module_names]
                )
            )
        return result - set(module_names)

    def module_dependents(self, module_names, recursive=False):
        """Return a module's build dependents."""
        # return self.__database_reader.module_dependents(module_name)
        if not recursive:
            result = set()
            for m in module_names:
                result = result.union(self.__database_reader.module_dependents(m))
        else:
            import itertools

            result = set(
                itertools.chain(
                    *[_recursive_dependencies(m, self.__database_reader.module_dependents) for m in module_names]
                )
            )
        return result - set(module_names)

    def module_names(self):
        """Return a list of all module names from the database."""
        return self.__database_reader.module_names()

    def package_names(self):
        """Return a list of all package names from the database."""
        return self.__database_reader.package_names()

    def work_module_names(
        self,
        sandbox_root_directory,
        configuration_filename="",
        work_module_type=WorkModuleType.ALL,  # default get all work modules
        #         main=True,
        #         branched=True,
        #         tagged=True,
    ):
        """Return a list of work module names from the specified sandbox. With the False ones filtered out."""
        if not configuration_filename:
            configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

        # print('KKKK0',  [main, branched, tagged])
        all_work = self.__configuration_reader.read_sandbox_configuration(
            configuration_filename=configuration_filename
        )["work_modules"]
        # print('KKKK1',  all_work)

        # filter out main trunk modules if they are not wanted
        # if not main:
        if WorkModuleType.MAIN not in work_module_type:
            all_work = {name: data for (name, data) in all_work.items() if not _is_main_module(data)}
        # print('CCC1',  all_work)

        # filter out branched modules if they are not wanted
        # if not branched:
        if WorkModuleType.BRANCH not in work_module_type:
            all_work = {name: data for (name, data) in all_work.items() if not _is_branched_module(data)}
        # print('CCC2',  all_work)

        # filter out tagged release modules if they are not wanted
        # if not tagged:
        if WorkModuleType.TAGGED not in work_module_type:
            all_work = {name: data for (name, data) in all_work.items() if not _is_tagged_module(data)}

        return list(sorted(all_work))

    def link_module_names(self, sandbox_root_directory, configuration_filename=""):
        """Return a list of link module names from the specified sandbox."""
        if not configuration_filename:
            configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

        return list(
            sorted(
                self.__configuration_reader.read_sandbox_configuration(configuration_filename=configuration_filename)[
                    "link_modules"
                ]
            )
        )

    def modules_dictionary(self, configuration_filename):
        """Return the parsed module information from the YAM.config file."""
        return self.__configuration_reader.read_sandbox_configuration(configuration_filename=configuration_filename)

    def write_config_file(self, configuration_filename, module_dictionary, default_branch):
        """Write out the YAM.config file for the provided link/work module dictionary data."""
        return self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=configuration_filename,
            work_module_dictionary=module_dictionary["work_modules"],
            link_module_dictionary=module_dictionary["link_modules"],
            default_branch=default_branch,
        )

    def fix_package_relatives(self):
        """
        Populate database with any missing relatives info for package releases.
        """
        pkg_releases = self.__database_reader.all_package_releases()
        for i in pkg_releases:
            # print('i=', i)
            package_name = i["name"]
            release_tag = i["tag"]
            n = self.populate_package_relatives(package_name, release_tag)
            print("Updating %s package %s release with %d module relatives" % (package_name, release_tag, n))

    def _has_package_relatives(self, pkg_name, release_tag):
        """
        Populate database with any missing relatives info for the package release.
        """
        status = self.__database_reader.has_package_relatives(pkg_name, release_tag)
        return status

    def populate_package_relatives(self, pkg_name, release_tag):
        """
        Populate database with any missing relatives info for the package release.
        """
        status = self._has_package_relatives(pkg_name, release_tag)
        if status:
            print("Nothing to do")
            yam_log.say(
                "Nothing to do - the relatives info is already populated in the database".format(pkg_name, release_tag)
            )
            return 0

        print("Populating the relatives info for %s package %s release" % (pkg_name, release_tag))

        # get the link modules info this package release
        full_repository_url = package_sandbox.releases_url(
            package_name=pkg_name, revision_tag=release_tag, database_reader=self.__database_reader, check_dead=False
        )

        # check out the release YAM.config into a temporary file
        import tempfile

        config_file = tempfile.mktemp()
        self.__revision_control_system.export_file(
            source=full_repository_url + "/YAM.config", target=config_file  # target=tmp_file_name  # tmp_sandbox_path
        )

        try:
            module_dictionary = self.__configuration_reader.read_sandbox_configuration(
                configuration_filename=config_file
            )
        except:
            print("Batd YAM.config definition")
            return 0

        link_modules = module_dictionary["link_modules"]
        if module_dictionary["work_modules"]:
            print(
                "Something is wrong, there are %d work modules, - converting to link modules"
                % len(module_dictionary["work_modules"])
            )
            for m, data in module_dictionary["work_modules"].items():
                link_modules[m] = [data[0], None, None, None]
                module_dictionary["work_modules"] = []

        if len(link_modules) == 0:
            return 0

        # return len(link_modules)

        # delete the temporary file

        # print('LLL', link_modules)
        # write the relatives info into the database
        self.__database_writer.populate_package_relatives(pkg_name, release_tag, link_modules)
        return len(link_modules)

    def set_up_package_sandbox(
        self,
        package_name,
        sandbox_path,
        release_directory,
        tag=None,
        work_module_type=WorkModuleType.NONE,  # default is to use link module
        progress_callback=lambda _: None,
    ):
        """Set up a sandbox from an existing package.

        If tag specified, we will use a previously released package
        based on that tag.

        """
        _check_release_directory(release_directory, self.__file_system, require=False)

        if not package_name:
            raise yam_exception.YamException("Package name must be a non-empty string")

        # print("KKKK tag=", tag, " workmod=", work_branch)
        # assumes SVN repository for now
        vcs_type = "svn"
        svn_rcs = self.__revision_control_system[vcs_type]
        if tag:
            # print('OKK1')
            sandbox = tagged_package_sandbox.TaggedPackageSandbox(
                package_name=package_name,
                tag=tag,
                sandbox_path=sandbox_path,
                revision_control_system=svn_rcs,  # self.__revision_control_system,
                file_system=self.__file_system,
                database_reader=self.__database_reader,
                configuration_reader=self.__configuration_reader,
                configuration_writer=self.__configuration_writer,
                default_branch=self.__default_branch,
                release_directory=release_directory,
            )
        else:
            sandbox = main_package_sandbox.MainPackageSandbox(
                package_name=package_name,
                sandbox_path=sandbox_path,
                revision_control_system=svn_rcs,  # self.__revision_control_system['svn'],
                file_system=self.__file_system,
                database_reader=self.__database_reader,
                configuration_reader=self.__configuration_reader,
                configuration_writer=self.__configuration_writer,
                default_branch=self.__default_branch,
                release_directory=release_directory,
            )

        progress_callback("Checking out package metadata")
        sandbox.check_out(
            progress_callback=progress_callback,
            work_module_type=work_module_type,
        )

    def set_up_loose_sandbox(
        self,
        module_names,
        sandbox_path,
        release_directory,
        work_module_type=WorkModuleType.NONE,  # default is to use link module
        progress_callback=lambda _: None,
    ):
        """Set up a sandbox from a list of module names."""
        _check_release_directory(release_directory, self.__file_system, require=False)

        # assumes SVN repository for now
        vcs_type = "svn"
        svn_rcs = self.__revision_control_system[vcs_type]

        # print('orig=', module_names)
        mod_names = self.module_dependencies(module_names, recursive=True)
        # print("with deps=", mod_names)
        sandbox = loose_sandbox.LooseSandbox(
            # module_names=module_names,
            module_names=set(module_names) | mod_names,
            sandbox_path=sandbox_path,
            revision_control_system=svn_rcs,
            file_system=self.__file_system,
            database_reader=self.__database_reader,
            repository_url=self.__default_repository_url,
            configuration_writer=self.__configuration_writer,
            default_branch=self.__default_branch,
            release_directory=release_directory,
        )

        progress_callback("Checking out sandbox metadata")
        sandbox.check_out(
            parent_directory=sandbox_path,
            progress_callback=progress_callback,
            work_module_type=work_module_type,
        )

    def diff(self, module_name: str, sandbox_root_directory: str, from_revision_tag: str = None):
        """
        Return a diff showing changes made module since it was branched.

        If from_revision_tag is specified, we will return the diff with
        respect to that revision instead of the latest revision.

        """
        vcs_type = self.__database_reader.vcs_type(module_name)
        wm_path = f"{sandbox_root_directory}/src/{module_name}"
        module_branch_data = self.__revision_control_system[vcs_type].getPathModuleData(wm_path)
        # vcs_root = database_reader.module_repository_url(module_name)
        # print("LLL", module_branch_data)
        if not from_revision_tag:
            if module_branch_data._branch_id:
                # on a branch, so diff against the root of the branch
                from_data = module_branch_data.with_branch_id(None)
            elif module_branch_data._release_tag == "main":
                # on the main trunk, so need to diff against the latest release
                from_revision_tag = self.__database_reader.latest_module_information(module_name=module_name)["tag"]
                from_data = module_branch_data.with_release_tag(from_revision_tag, None)
            else:
                # have a tagged release
                from_data = module_branch_data

        """
        try:
            (from_url, to_url) = self._get_from_and_to_urls(
                sandbox_root_directory=sandbox_root_directory,
                module_name=module_name,
                from_revision_tag=from_revision_tag,
            )
        except WorkModuleTypeException:  # pragma: NO COVER
            # Ignore tagged work modules.
            return ""  # pragma: NO COVER
        """
        if module_branch_data._branch_id:
            tostr = module_branch_data._release_tag + "-" + module_branch_data._branch_id
        else:
            tostr = module_branch_data._release_tag

        msg = "For module '{}' getting diff between release '{}' and '{}'".format(
            module_name, from_data._release_tag, tostr
        )
        yam_log.say(msg)

        # get diffs for changes that have occured in this module release
        # for inclusion in notification email message
        return self.__revision_control_system[vcs_type].generate_diff(
            # from_data=from_data, to_url=to_url
            from_data=from_data,
            path=wm_path,
        )

    def get_releases_diff(self, module_name: str, from_release: str, to_release: str):
        """
        Return the difference between the specified releases of the module.
        """
        from . import work_module

        """
        from_url = work_module.releases_url(
            module_name=module_name, revision_tag=from_release, database_reader=self.__database_reader
        )
        to_url = work_module.releases_url(
            module_name=module_name, revision_tag=to_release, database_reader=self.__database_reader
        )
        """
        vcs_type = self.__database_reader.vcs_type(module_name)
        vcs_root = self.__database_reader.module_repository_url(module_name)

        from_data = rcs.ModuleBranchData(
            module_name=module_name, vcs_type=vcs_type, vcs_root=vcs_root, release_tag=from_release
        )
        to_data = rcs.ModuleBranchData(
            module_name=module_name, vcs_type=vcs_type, vcs_root=vcs_root, release_tag=to_release
        )
        # print('KKK', from_url, to_url)
        return self.__revision_control_system[vcs_type].generate_diff(from_data=from_data, to_data=to_data)

    def has_modificationsOBSOLETE(self, module_name, sandbox_root_directory):
        """Return True if there are committed changes."""
        yam_log.say("Checking {} module for modifications".format(module_name))
        try:
            (from_url, to_url) = self._get_from_and_to_urls(
                sandbox_root_directory=sandbox_root_directory,
                module_name=module_name,
            )
        except WorkModuleTypeException:  # pragma: NO COVER
            # Ignore tagged work modules.
            return False  # pragma: NO COVER

        return self.__revision_control_system.has_modifications(from_url=from_url, to_url=to_url)

    def _get_from_and_to_urlsOBSOLETE(self, sandbox_root_directory, module_name, from_revision_tag=None):
        """Return from/to URLs."""
        _check_sandbox_directory(path=sandbox_root_directory, file_system=self.__file_system)
        current_tag, current_branch = self.__configuration_reader.read_work_module_information(
            configuration_filename=os.path.join(sandbox_root_directory, "YAM.config"),
            module_name=module_name,
        )

        if current_tag and current_branch:
            to_url = work_module.feature_branches_url(
                module_name=module_name,
                revision_tag=current_tag,
                branch_id=current_branch,
                database_reader=self.__database_reader,
            )

            if not from_revision_tag:
                from_revision_tag = current_tag
        elif not current_tag and not current_branch:
            to_url = work_module.main_branch_url(module_name=module_name, database_reader=self.__database_reader)

            if not from_revision_tag:
                from_revision_tag = self.__database_reader.latest_module_information(module_name=module_name)["tag"]
        elif current_tag and not current_branch:
            raise WorkModuleTypeException("Tagged work module")
        else:
            raise yam_exception.YamException(
                "In the sandbox configuration, if a branch ID is specified, a " "revision tag must also be specified"
            )

        try:
            url_from_svn = self.__revision_control_system.url("{}/src/{}".format(sandbox_root_directory, module_name))
        except:
            url_from_svn = None
        if url_from_svn is not None and to_url != url_from_svn:
            msg = (
                "WARNING: INCONSISTENT SANDBOX for module '{}'!!!\n"
                + "YAM.config thinks the SVN url is '{}', but the local checkout thinks it is '{}'\n"
                + "I'm using the SVN URL, but you NEED to fix this if you want to trust anything\n"
                + "pyam touches"
            ).format(module_name, to_url, url_from_svn)
            yam_log.say(msg)
            red = ansi("1;31m")
            end = ansi("0m")
            print(red + msg + end)
            to_url = url_from_svn

        return (
            work_module.releases_url(
                module_name=module_name,
                revision_tag=from_revision_tag,
                database_reader=self.__database_reader,
            ),
            to_url,
        )

    def add_work_module_to_sandbox_configuration(
        self, module_name, release, branch, sandbox_root_directory, progress_callback
    ):
        """Add a work module to the sandbox configuration."""
        configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

        module_dictionary = self.__configuration_reader.read_sandbox_configuration(
            configuration_filename=configuration_filename
        )

        # add the new work module
        module_configuration_utils.add_new_work_module(
            module_dictionary,
            module_name,
            release,
            branch,
            self.__database_reader,
            partial(self.__unique_branch_id, sandbox_root_directory, progress_callback),
        )

        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=configuration_filename,
            work_module_dictionary=module_dictionary["work_modules"],
            link_module_dictionary=module_dictionary["link_modules"],
            default_branch=self.__default_branch,
        )

    def add_link_module_to_sandbox_configuration(self, module_name, release, sandbox_root_directory, release_directory):
        """Add a link module to the sandbox configuration."""
        configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

        module_dictionary = self.__configuration_reader.read_sandbox_configuration(
            configuration_filename=configuration_filename
        )

        """
        # add the new link module
        module_configuration_utils.add_new_link_module(
            module_dictionary,
            module_name,
            release
        )
        """

        work_modules = module_dictionary["work_modules"]
        if module_name in work_modules:
            raise yam_exception.YamException(
                "Module {} is a work module, but the user asked for a link module. Giving up. \n".format(module_name)
                + "======================================================================= \n \n"
                "This command is only used when the module is not listed either as a work or link module in you YAM.config file. \n"
                + "\n If you just deleted or moved this work module from your sanbox \n"
                + "try the pyam config --to-link command followed by module name.\n"
                + "Then check out the work module again.\n\n"
                + "======================================================================= \n \n"
            )

        link_modules = module_dictionary["link_modules"]

        # if we asked for a particular version, and the current sandbox has
        # something else, this is a big, bad error. Otherwise, we can catch
        # it

        if module_name in link_modules:
            if release is not None and link_modules[module_name][0] != release:
                raise yam_exception.YamException(
                    "Link module {} already exists in the sandbox. Have tag/build {}, but requested tag/build {}. Giving up.".format(
                        module_name,
                        link_modules[module_name][0],
                        link_modules[module_name][1],
                        release,
                    )
                )
            raise module_configuration_utils.AlreadyAModuleException(
                "Module '{m}' already exists in the sandbox".format(m=module_name)
            )

        from . import concrete_configuration_reader

        # if no release specified, get the latest release info from the database
        if release is None:
            latest = self.latest_module_information(module_name, release=None, release_directory=release_directory)

            release = latest["tag"]
            build = latest["build"]
            link_modules[module_name] = (release, build, None, None)
        else:
            if release == "main":
                raise yam_exception.YamException("Cannot check out link module off trunk!")
            link_modules[module_name] = revision_tag_utils.link_expression_to_tuple(
                module_name + "/" + module_name + "-" + release
            )

        # print('SSSS', module_name, link_modules[module_name])
        # generate warning if the link module path does not exists
        tagstr = revision_tag_utils.tuple_to_release_tag_suffix(
            tag=module_dictionary["link_modules"][module_name], use_build=True
        )
        releasedir_thismodule = os.path.join(release_directory, "Module-Releases", module_name)
        path = os.path.join(releasedir_thismodule, module_name + "-" + tagstr)
        if not os.path.exists(path):
            # Path doesn't exist.
            red = ansi("1;31m")
            end = ansi("0m")
            msg = (
                red
                + "WARNING: requested link module {}:{} release directory {} doesn't exist on the file system".format(
                    module_name, tagstr, path
                )
                + end
            )
            yam_log.say(msg)
            print(msg)

        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=configuration_filename,
            work_module_dictionary=module_dictionary["work_modules"],
            link_module_dictionary=module_dictionary["link_modules"],
            default_branch=self.__default_branch,
        )

    def convert_to_work_module(
        self,
        module_name,
        release,
        branch,
        module_dictionary={},
        sandbox_root_directory=None,
        work_module_type=WorkModuleType.BRANCH,  # default is to create a branch
        # tagged_branch=False,
        # main_branch=False,
        progress_callback=lambda _: None,
    ):
        """Convert a module to a work module.

        Modify the sandbox configuration file to make the specified link
        module into a work module.

        """

        # if not main_branch:
        if WorkModuleType.MAIN not in work_module_type:
            # main_branch = (release == "main")
            if release == "main":
                work_module_type = WorkModuleType.MAIN

        # load the information about the modules from the YAM.config file
        assert module_dictionary or sandbox_root_directory
        if sandbox_root_directory:
            configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")
            module_dictionary = self.__configuration_reader.read_sandbox_configuration(
                configuration_filename=configuration_filename
            )

        # print('TTT', module_dictionary )
        # update the module information using the new module data
        module_configuration_utils.convert_to_work_module(
            module_dictionary,
            module_name,
            release,
            branch,
            work_module_type,
            progress_callback,
            partial(self.__unique_branch_id, sandbox_root_directory, progress_callback),
        )

        if sandbox_root_directory:
            self.__configuration_writer.write_sandbox_configuration(
                configuration_filename=configuration_filename,
                work_module_dictionary=module_dictionary["work_modules"],
                link_module_dictionary=module_dictionary["link_modules"],
                default_branch=self.__default_branch,
            )

        return module_dictionary["work_modules"]

    def convert_work_module_to_link_module(
        self,
        module_name,
        release_directory,
        module_dictionary={},
        sandbox_root_directory=None,
        branch_id=None,
        progress_callback=lambda _: None,
    ):
        """Convert work module to link module.

        Modify the sandbox configuration file to make the specified work
        module into a link module.

        """
        if not branch_id:
            branch_id = self.__default_branch

        assert module_dictionary or sandbox_root_directory
        if sandbox_root_directory:
            configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

            module_dictionary = self.__configuration_reader.read_sandbox_configuration(
                configuration_filename=configuration_filename
            )

        # update the module information using the new module data
        revision_tag, build_id = module_configuration_utils.convert_work_module_to_link_module(
            module_dictionary,
            module_name,
            branch_id,
            release_directory,
            self.__database_reader,
            self.latest_module_information,
        )

        # Add module to link module dictionary
        link_modules = module_dictionary["link_modules"]
        link_modules[module_name] = (revision_tag, build_id, None, None)
        progress_callback("Converting '{m}' to a link module".format(m=module_name))

        if sandbox_root_directory:
            self.__configuration_writer.write_sandbox_configuration(
                configuration_filename=configuration_filename,
                work_module_dictionary=module_dictionary["work_modules"],
                link_module_dictionary=module_dictionary["link_modules"],
                default_branch=self.__default_branch,
            )

        return link_modules

    def current_modules(self):
        """
        Return list of names of all module names that are not obsolete.
        """
        # get list of all modules
        all_module_names = set(self.__database_reader.module_names())

        # get list of all module sin ObsoleteModulesPkg
        working_copy_path = self.__file_system.create_temporary_directory()

        # print('UUUU', database_reader.default_repository_url())

        # this currently requires an SVN version control system
        self.__revision_control_system["svn"]._pkg_check_out(
            source=package_sandbox.common_trunk_url(database_reader=self.__database_reader),
            target=working_copy_path,
        )

        configuration_filename = os.path.join(working_copy_path, "YAM.modules")

        obsolete_module_names = self.__configuration_reader.read_package_information(
            package_configuration_filename=configuration_filename,
            package_name="ObsoleteModulesPkg",
        )
        self.__file_system.remove_directory(working_copy_path)

        # take the difference of the two lists and get their lates link modules
        curr_module_names = all_module_names.difference(obsolete_module_names)
        # print('KJJ', curr_module_names)
        return curr_module_names

    def remove_modules_from_sandbox(
        self,
        module_list,
        sandbox_root_directory,
        release_directory,
        progress_callback=lambda _: None,
    ):
        """
        Remove work/link module from the sandbox.

        If a work module, rename the work module directory to get it out
        of the way.
        """

        configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

        self.rmlink_modules(
            module_names=module_list,
            sandbox_directory=sandbox_root_directory,
            release_directory=release_directory,
        )

        module_dictionary = self.__configuration_reader.read_sandbox_configuration(
            configuration_filename=configuration_filename
        )

        # remove the specified modules
        module_configuration_utils.remove_modules(
            module_dictionary, module_list, sandbox_root_directory, progress_callback, self.__file_system
        )

        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=configuration_filename,
            work_module_dictionary=module_dictionary["work_modules"],
            link_module_dictionary=module_dictionary["link_modules"],
            default_branch=self.__default_branch,
        )

    def update_link_modules(
        self,
        release_directory,
        module_dictionary={},
        to_release=None,
        sandbox_root_directory=None,
        module_names=None,
        backup=True,
        progress_callback=lambda _: None,
    ):
        """Update link modules in sandbox.

        Modify the sandbox configuration file to modify the specified link
        module's revision tag and build ID to be up to date.

        Return True if something gets modified.

        """

        assert module_dictionary or sandbox_root_directory
        if sandbox_root_directory:
            configuration_filename = os.path.join(sandbox_root_directory, "YAM.config")

            module_dictionary = self.__configuration_reader.read_sandbox_configuration(
                configuration_filename=configuration_filename
            )

        # update the module information using the new module data
        outdated_link_module_names = module_configuration_utils.update_link_modules(
            module_dictionary, to_release, module_names, release_directory, self.latest_module_information
        )

        if outdated_link_module_names:
            if backup:
                backup_data = self.__file_system.read_file(filename=configuration_filename)
                # Find a non-existing filename to backup the "YAM.config".
                i = 1
                while True:
                    backup_filename = "{filename}.backup{i}".format(filename=configuration_filename, i=i)
                    if not self.__file_system.path_exists(backup_filename):
                        progress_callback("Backing up to '{f}'".format(f=backup_filename))
                        self.__file_system.write_to_file(string_data=backup_data, filename=backup_filename)
                        break
                    i += 1

            if sandbox_root_directory:
                self.__build_system.remove_links(
                    module_names=outdated_link_module_names,
                    sandbox_directory=sandbox_root_directory,
                    release_directory=release_directory,
                )

                progress_callback("Updating link modules in 'YAM.config'")
                self.__configuration_writer.write_sandbox_configuration(
                    configuration_filename=configuration_filename,
                    work_module_dictionary=module_dictionary["work_modules"],
                    link_module_dictionary=module_dictionary["link_modules"],
                    default_branch=self.__default_branch,
                )

                return True
        else:
            progress_callback("Link module(s) are already up to date")
        return module_dictionary["link_modules"]

    def rmlink_modules(self, module_names, sandbox_directory, release_directory):
        """Remove the links for a specified module in a sandbox."""
        _check_release_directory(release_directory, self.__file_system, require=False)

        self.__build_system.remove_links(
            module_names=module_names,
            sandbox_directory=sandbox_directory,
            release_directory=release_directory,
        )

    def relink_modules(self, module_names, sandbox_directory, release_directory):
        """Recreate the links for a specified module in a sandbox."""
        _check_release_directory(release_directory, self.__file_system, require=False)

        self.__build_system.remove_links(
            module_names=module_names,
            sandbox_directory=sandbox_directory,
            release_directory=release_directory,
        )
        self.__build_system.make_links(
            module_names=module_names,
            sandbox_directory=sandbox_directory,
            release_directory=release_directory,
        )

    def database_date_time(self):
        """Return a datetime representing the database's local time."""
        return self.__database_reader.local_date_time()

    def test_default_repository_access(self):
        """Return True if we can access the default repository URL."""
        return self.__revision_control_system["svn"]._exists(self.__default_repository_url)

    def check_build_server(self, sandbox_directory):
        """Return True if we can access the build server."""
        return self.__build_system.check_build_server(sandbox_directory)

    def register_new_git_moduleOBSOLETE(
        self, module_name, release_directory, repository_keyword, use_git=True, progress_callback=lambda _: None
    ):
        # print("REGISTERING NEW MOD IN GIT")
        module_name = name_utils.filter_module_name(module_name)

        if module_name not in self.__database_reader.module_names():
            self.__database_writer.register_new_module(
                module_name=module_name, repository_keyword=repository_keyword, git=use_git
            )

        main_branch_url = work_module.main_branch_url(
            module_name=module_name, database_reader=self.__database_reader, use_git=True
        )
        # print("REPO PATH: ", main_branch_url)
        repo_path = Path(main_branch_url)
        repo_path.mkdir()
        create_git_repo(repo_path)
        # main_branch_url = os.path.join(release_directory , module_name)
        # from git import Repo
        repo = Repo(main_branch_url)
        self.__revision_control_system.repo = repo
        # main_branch_url should be path to gitrepo
        revision_tag = "R1-00"
        create_and_commit_basic_module_files_git(
            url=main_branch_url,
            module_name=module_name,
            file_system=self.__file_system,
            build_system=self.__build_system,
            revision_control_system=self.__revision_control_system,
        )

        self.__revision_control_system.tag_git_module(module_name, revision_tag, repo)

        date_time = self.__database_reader.local_date_time()
        self.__database_writer.write_module_source_release_information(
            module_name=module_name,
            revision_tag=revision_tag,
            username="",
            date_time=date_time,
            changed_api_filename_list=[],
            readmes=[],
            num_files_changed=0,
            num_lines_added=0,
            num_lines_removed=0,
            operating_system_name="",
            site_name="",
            host_ip="",
            release_path=release_directory,
            maintenance_name=None,
            maintenance_num=None,
        )

        module_saving_utils.move_module_for_release(
            module_path=main_branch_url,
            module_name=module_name,
            new_revision_tag=revision_tag,
            build_id=None,
            changelogs_path="",  # no useful information in initial version
            release_directory=release_directory,
            keep_release=True,
            latest_link=True,
            file_system=self.__file_system,
            build_system=self.__build_system,
            database_writer=self.__database_writer,
            progress_callback=progress_callback,
            database_reader=self.__database_reader,
            revision_control_system=self.__revision_control_system,
        )

    def register_new_module(
        self,
        module_name,
        release_directory,
        repository_keyword,
        # use_git=False,
        vcs_type,
        progress_callback=lambda _: None,
    ):
        """Register a new module.

        This affects the database and revision control system.

        """
        """
        if use_git:
            self.register_new_git_module(module_name,
                                         release_directory,
                                         repository_keyword,
                                         progress_callback)
            return
        """

        # --------------------------------------

        # vcs_type = 'svn'

        _check_release_directory(release_directory, self.__file_system, require=True)

        module_name = name_utils.filter_module_name(module_name)

        if module_name not in self.__database_reader.module_names():
            self.__database_writer.register_new_module(
                module_name=module_name, repository_keyword=repository_keyword, vcs_type=vcs_type
            )
        vcs_root = self.__database_reader.module_repository_url(module_name)

        # print('LLLL', self.__revision_control_system, vcs_type)
        revision_control_system = self.__revision_control_system[vcs_type]

        # create VCS repo/structure for the new module with R1-00 release tag

        # if bare_repo is True, then git will create bare repo. This variable has effect for SVN
        revision_control_system.create_module(vcs_root=vcs_root, module_name=module_name, bare=self._bare_repo)

        # create basic module files and get the folder with the new files
        working_copy_path = revision_control_system.create_and_commit_basic_module_files(
            vcs_root=vcs_root,
            # url=main_branch_url,
            module_name=module_name,
            file_system=self.__file_system,
            build_system=self.__build_system,
            bare=self._bare_repo,
            # revision_control_system=self.__revision_control_system,
        )

        revision_tag = "R1-00"
        if vcs_type == "svn" or (vcs_type == "git" and self._bare_repo):

            module_branch_data = rcs.ModuleBranchData(
                vcs_root=vcs_root,
                module_name=module_name,
                # release_tag='main',
                vcs_type="svn",
            )
            # main_branch_url = module_branch_data.uri(release_tag='main')
            # module_branch_data._release_tag = revision_tag
            # release_url = module_branch_data.uri(release_tag=revision_tag)
            # print('KKK', main_branch_url, release_url)
            release_data = module_branch_data.with_release_tag(release_tag=revision_tag)
            if vcs_type == "git":
                # GIT
                revision_control_system.tag(
                    destination_url=release_data,  # module_branch_data.with_release_tag(release_tag=revision_tag)
                    path=working_copy_path,
                )
            else:
                # SVN
                revision_control_system.branch(
                    source_url=module_branch_data.with_release_tag(release_tag="main"),  # main_branch_url,
                    destination_url=release_data,  # module_branch_data.with_release_tag(release_tag=revision_tag)
                )

            revision_control_system.switch_to_branch(path=working_copy_path, branch_url=release_data)  # release_url

        # Create database entry last in case the user does not have access to
        # the repository. Manually modify the repository is easier than
        # modifying the database if something goes wrong.
        date_time = self.__database_reader.local_date_time()

        # assert os.path.isdir(working_copy_path)
        self.__database_writer.write_module_source_release_information(
            module_name=module_name,
            revision_tag=revision_tag,
            username="",
            date_time=date_time,
            changed_api_filename_list=[],
            readmes=[],
            num_files_changed=0,
            num_lines_added=0,
            num_lines_removed=0,
            operating_system_name="",
            site_name="",
            host_ip="",
            release_path=release_directory,
            maintenance_name=None,
            maintenance_num=None,
        )

        # assert os.path.isdir(working_copy_path)
        # Create release directory for module before releasing
        self.__file_system.make_directory(os.path.join(release_directory, "Module-Releases", module_name))

        if vcs_type == "git" and not self._bare_repo:

            from git import Repo

            if not bare:
                temp_dir = os.path.join(vcs_root, module_name)
                # os.mkdir(temp_dir)
                # copy files tree from working_copy_dir to temp_dir
                shutil.copytree(working_copy_path, temp_dir, symlinks=True)
                working_copy_path = temp_dir
                repo = Repo(temp_dir)
                repo.git.checkout(f"{module_name}-R1-00")
            else:
                wmrepo = Repo(working_copy_path)
                wmrepo.git.checkout(f"{module_name}-R1-00")

        module_saving_utils.move_module_for_release(
            module_path=working_copy_path,
            module_name=module_name,
            new_revision_tag=revision_tag,
            build_id=None,
            changelogs_path="",  # no useful information in initial version
            release_directory=release_directory,
            keep_release=True,
            latest_link=True,
            file_system=self.__file_system,
            build_system=self.__build_system,
            database_writer=self.__database_writer,
            progress_callback=progress_callback,
            database_reader=self.__database_reader,
            revision_control_system=self.__revision_control_system[vcs_type],
        )
        # assert os.path.isdir(working_copy_path)

    def dbutil_add_release(self, module: str, release, username, release_directory):
        """
        Add a module release (eg. R2-34v) entry to into the database.
        """
        assert username

        # verify module exists
        if module not in self.__database_reader.module_names():
            raise yam_exception.YamException("The {m} module does not exist".format(m=module))

        # verify release is well-formed
        from . import revision_tag_utils

        major, minor, subminor = revision_tag_utils.split_revision_tag(release)

        # verify release entry is not already in the database
        from . import database_reader

        try:
            latest_release = self.__database_reader.latest_module_information(module_name=module, release=release)
            # print('LLLL', latest_release)
            # if we are here, this means that the release entry is already in the database
            assert 0
        except database_reader.ModuleLookupException:
            pass

        # verify that the version control system knows about this release
        from . import work_module

        """
        release_url = work_module.releases_url(
            module_name=module,
            revision_tag=release,
            database_reader=self.__database_reader,
        )
        status = self.__revision_control_system.exists(url=release_url)
        """

        vcs_type = self.__database_reader.vcs_type(module)
        vcs_root = self.__database_reader.module_repository_url(module)

        module_branch_data = rcs.ModuleBranchData(
            module_name=module, vcs_type=vcs_type, vcs_root=vcs_root, release_tag=release
        )
        status = self.__revision_control_system[vcs_type].exists_module_branch(module_branch_data)
        if not status:
            raise yam_exception.YamException(
                "The {m}-{r} module release does not exist in the version control repository".format(
                    m=module, r=release
                )
            )

        # insert a release entry into modpkgReleases table
        date_time = self.__database_reader.local_date_time()
        self.__database_writer.write_module_source_release_information(
            module_name=module,
            revision_tag=release,
            username=username,
            date_time=date_time,
            changed_api_filename_list=[],
            readmes=[],
            num_files_changed=0,
            num_lines_added=0,
            num_lines_removed=0,
            operating_system_name="",
            site_name="",
            host_ip="",
            release_path=release_directory,
            maintenance_name=None,
            maintenance_num=None,
        )

    def register_new_package(
        self,
        package_name,
        repository_keyword,
        modules,
        release_directory,
        username,
        release_information_callback=lambda package_name, revision_tag, release_note_message: None,
        progress_callback=lambda _: None,
    ):
        """Register a new package.

        This affects the database and revision control system.

        """

        package_name = name_utils.filter_package_name(package_name)

        list_of_all_module_names = self.__database_reader.module_names()
        for m in modules:
            if m not in list_of_all_module_names:
                raise yam_exception.YamException("Module '{m}' does not exist".format(m=m))

        # assumes SVN repository for now
        vcs_type = "svn"
        svn_rcs = self.__revision_control_system[vcs_type]
        append_package_to_configuration_if_needed(
            package_name=package_name,
            modules=modules,
            file_system=self.__file_system,
            revision_control_system=svn_rcs,
            database_reader=self.__database_reader,
            config_reader=self.__configuration_reader,
            progress_callback=progress_callback,
        )

        # If the SQL doesn't know about this package, create the database entry
        if package_name not in self.__database_reader.package_names():
            self.__database_writer.register_new_package(
                package_name=package_name, repository_keyword=repository_keyword
            )

        main_branch_url = package_sandbox.main_branch_url(
            package_name=package_name, database_reader=self.__database_reader
        )

        # assumes SVN repository for now
        if svn_rcs._exists(main_branch_url):
            raise yam_exception.YamException("Package '{p}' already exists".format(p=package_name))

        revision_tag = "R1-00"

        progress_callback("Registering with revision control system")

        svn_rcs.make_directory(main_branch_url)

        svn_rcs.make_directory(
            os.path.dirname(
                package_sandbox.releases_url(
                    package_name=package_name,
                    revision_tag=revision_tag,
                    database_reader=self.__database_reader,
                )
            )
        )

        create_and_commit_package_files(
            url=main_branch_url,
            package_name=package_name,
            file_system=self.__file_system,
            revision_control_system=svn_rcs,
        )

        # create dictionary of latest release link modules
        lms = {}
        for m in modules:
            info = module_saving_utils.latest_module_information(
                module_name=m,
                release=None,  # latest
                release_directory=release_directory,
                database_reader=self.__database_reader,
                file_system=self.__file_system,
            )
            lms[m] = (info["tag"], info["build"], None, None)

        self._save_package(
            package_name=package_name,
            revision_tag=revision_tag,
            # use_latest_modules=True,
            # release_configuration_filename='',
            link_modules=lms,
            release_directory=release_directory,
            changelogs_path="",  # nothing interesting in the first release
            username=username,
            message="Create package",
            release_information_callback=release_information_callback,
            progress_callback=progress_callback,
        )

    def unregister_module(self, module_name, undo=False):
        """Unregister a module from the database."""
        self.__database_writer.unregister_module(module_name, undo=undo)

    def unregister_package(self, package_name):
        """Unregister a package from the database."""
        self.__database_writer.unregister_package(package_name)

    def save_package(
        self,
        package_name,
        release_directory,
        username,
        # use_latest_modules=True,
        changelogs_path="",
        release_config_file="",
        release_note_message="",
        empty_log_filter=lambda x: x,
        revision_tag=None,
        release_configuration_filename=None,
        release_information_callback=lambda package_name, revision_tag, release_note_message: None,
        progress_callback=lambda _: None,
    ):
        """Save a package."""
        latest_tag = self.__database_reader.latest_package_revision_tag(package_name)

        if revision_tag:
            # Check validity of tag.
            if revision_tag_utils.split_revision_tag(revision_tag) < revision_tag_utils.split_revision_tag(latest_tag):
                raise yam_exception.YamException(
                    "{tag} is older than latest ({latest})".format(tag=revision_tag, latest=latest_tag)
                )
        else:
            revision_tag = revision_tag_utils.incremented(latest_tag)

        # check the validity of any specified YAM.config file for this
        # release and convert the modules into link mdules
        lms = {}
        if release_configuration_filename:
            # read the config file
            module_dictionary = self.__configuration_reader.read_sandbox_configuration(release_configuration_filename)

            #  Check that modules are OK for inclusion in a package
            #  release. No modules on the main trunk or on a branch
            lms = module_configuration_utils.package_release_check(
                module_dictionary, self.__database_reader, release_configuration_filename
            )

        # Check for None explicitly since we allow empty strings.
        if release_note_message is None:
            message = _generate_release_note_message(
                log_filter=empty_log_filter,
                reference_log=revision_tag,
                name=package_name,
            )
        else:
            message = release_note_message

        self._save_package(
            package_name=package_name,
            revision_tag=revision_tag,
            # use_latest_modules=use_latest_modules,
            release_directory=release_directory,
            changelogs_path=changelogs_path,
            username=username,
            # release_configuration_filename=release_configuration_filename,
            link_modules=lms,
            message=message,
            release_information_callback=release_information_callback,
            progress_callback=progress_callback,
        )

    def _save_package(
        self,
        package_name,
        revision_tag,
        # use_latest_modules,
        release_directory,
        changelogs_path,
        username,
        # release_configuration_filename,
        link_modules,
        message,
        release_information_callback,
        progress_callback,
    ):
        """Save a package with a specific revision tag."""
        # TODO: Break apart this abomination into functions.
        from . import sandbox

        main_branch_url = package_sandbox.main_branch_url(
            package_name=package_name, database_reader=self.__database_reader
        )

        working_copy_path = self.__file_system.create_temporary_directory()
        # this currently requires an SVN version control system
        self.__revision_control_system["svn"]._pkg_check_out(source=main_branch_url, target=working_copy_path)

        date_time = self.__database_reader.local_date_time()

        # assumes SVN repository for now
        vcs_type = "svn"
        svn_rcs = self.__revision_control_system[vcs_type]
        saving_utils.update_release_notes(
            message=message,
            new_revision_tag=revision_tag,
            date_time=date_time,
            file_system=self.__file_system,
            path=working_copy_path,
            revision_control_system=svn_rcs,
        )

        release_url = package_sandbox.releases_url(
            package_name=package_name,
            revision_tag=revision_tag,
            database_reader=self.__database_reader,
        )

        svn_rcs._branch_uri(source_url=main_branch_url, destination_url=release_url)

        svn_rcs._switch_to_branch_uri(path=working_copy_path, branch_url=release_url)

        # Copy over the common files from main branch to release.
        common_release_url = os.path.join(release_url, "common")

        svn_rcs._branch_uri(
            source_url=package_sandbox.common_url(
                package_name=package_name,
                database_reader=self.__database_reader,
            ),
            destination_url=common_release_url,
        )

        # this currently requires an SVN version control system
        svn_rcs._pkg_check_out(
            source=common_release_url,
            target=os.path.join(working_copy_path, "common"),
        )

        # set the YAM.config file name
        configuration_filename = os.path.join(working_copy_path, "YAM.config")

        # if there are no input link modules provided, use the latest
        # ones available based on the package definition
        if not link_modules:
            # create link modules with the latest module releases for the package
            # read the modules for the package from the YAM.modules file in the sandbox
            module_names = self.__configuration_reader.read_package_information(
                package_configuration_filename=os.path.join(working_copy_path, "common", "YAM.modules"),
                package_name=package_name,
            )

            for m in module_names:
                info = module_saving_utils.latest_module_information(
                    module_name=m,
                    release=None,  # latest
                    release_directory=release_directory,
                    database_reader=self.__database_reader,
                    file_system=self.__file_system,
                )
                # disable the maintenance release fields since we are
                # auto-generating this info and want the bleeding edge
                maintenance_branch = None
                maintenance_release = None
                link_modules[m] = (info["tag"], info["build"], maintenance_branch, maintenance_release)

        # write out the YAM.config file with the link module release
        # information
        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=configuration_filename,
            work_module_dictionary={},
            link_module_dictionary=link_modules,
            default_branch=self.__default_branch,
        )

        # commit the files in the sandbox
        svn_rcs.check_in(
            path=working_copy_path,
            log_message="pyam: Add latest package configuration",
        )

        # write the release info into the database
        self.__database_writer.write_package_release_information(
            package_name=package_name,
            link_modules=link_modules,
            revision_tag=revision_tag,
            username=username,
            date_time=date_time,
        )

        if release_directory:
            # Create release directory for module before releasing.
            destination_path = os.path.join(release_directory, "Pkg-Releases", package_name)
            self.__file_system.make_directory(destination_path)

            package_sandbox.move_package_for_release(
                package_path=working_copy_path,
                package_name=package_name,
                new_revision_tag=revision_tag,
                release_directory=release_directory,
                file_system=self.__file_system,
                progress_callback=progress_callback,
            )

        release_information_callback(package_name, revision_tag, message)

        # set up links for the package ReleaseNotes files for access
        # from the releases page
        if release_directory and changelogs_path:
            """
            create_changelogs_link(directory_name, changelogs_path,
                                   destination_path,
                                   progress_callback)
            """
            f = "ReleaseNotes"
            directory_name = "{m}-{tag}".format(m=package_name, tag=revision_tag)
            topath = destination_path + "/" + directory_name + "/" + f
            # print("topath=", topath,)
            if os.path.exists(topath):
                progress_callback("Creating symbolic links for {} file".format(f))
                dest_link = "package-{d}-{f}".format(d=directory_name, f=f)
                frompath = changelogs_path + "/" + dest_link
                # print("frompath=", frompath,)
                if os.path.exists(frompath):
                    os.remove(frompath)
                os.symlink(topath, frompath)

    def all_module_packages(self, type, order="name", ascending=True):
        """
        Return list of all current modules/packages. The 'type' argument can
        take 'MODULE or PACKAGE values. The 'order' argument can be
        'name', 'nrels', or 'date'. The 'ascending' argument can be used
        to change the listing order.

        """
        return self.__database_reader.all_module_packages(type, order, ascending=ascending)

    def package_release_modules(self, package, release_tag, order="name", ascending=True):
        """
        Return list of all modules releases in a package release.  The
        'order' argument can be 'name', 'nrels', or 'date'. The
        'ascending' argument can be used to change the listing order.

        """
        return self.__database_reader.package_release_modules(package, release_tag, order, ascending=ascending)

    def initialize_module_repository(self, url):
        """Initialize a repository that will contain modules.

        Raise a YamException if the repository is already initialized.

        """
        self.__revision_control_system["svn"].make_directory(os.path.join(url, "Modules"))

    def initialize_package_repository(self, url, release_directory):
        """Initialize a repository that will contain packages.

        Raise a YamException if the repository is already initialized.

        """
        rcs = self.__revision_control_system["svn"]
        rcs.make_directory(os.path.join(url, "Packages"))

        common_base_url = os.path.join(url, "common")
        del url

        rcs.make_directory(common_base_url)

        rcs.make_directory(os.path.join(common_base_url, "releases"))

        main_branch_url = os.path.join(common_base_url, "trunk")
        rcs.make_directory(main_branch_url)

        _fill_in_common_trunk(
            main_branch_url=main_branch_url,
            revision_control_system=rcs,  # self.__revision_control_system,
            file_system=self.__file_system,
            release_directory=release_directory,
        )

    def initialize_release_directory(self, release_directory):
        """Create and initialize the release directory."""
        self.__file_system.make_directory(release_directory)

        self.__file_system.make_directory(os.path.join(release_directory, "Module-Releases"))

        self.__file_system.make_directory(os.path.join(release_directory, "Pkg-Releases"))

    def initialize_database(self):
        """Create the database tables if not done so already."""
        self.__database_writer.initialize_database()

    def initialize_build_system(
        self,
        build_module_name,
        release_directory,
        username,
        operating_system_name,
        site_name,
        host_ip,
        progress_callback=lambda _: None,
    ):
        """Create the build system.

        - Register build_module_name
        - Add build files directly and commit
        - Create a temporary sandbox
            - Check out main branch
            - Save main branch

        """

        # assumes SVN repository for now
        vcs_type = "svn"
        svn_rcs = self.__revision_control_system[vcs_type]
        self.register_new_module(
            module_name=build_module_name,
            release_directory=release_directory,
            repository_keyword=None,
            vcs_type=vcs_type,
            progress_callback=progress_callback,
        )

        vcs_root = self.__database_reader.module_repository_url(build_module_name)
        module_branch_data = rcs.ModuleBranchData(
            vcs_root=vcs_root, module_name=build_module_name, release_tag="main", vcs_type="svn"
        )
        check_out_and_commit_build_files(
            url=module_branch_data,
            #             url=work_module.main_branch_url(
            #                 module_name=build_module_name,
            #                 database_reader=self.__database_reader,
            #             ),
            file_system=self.__file_system,
            revision_control=svn_rcs,  # self.__revision_control_system,
            build_system=self.__build_system,
            release_directory=release_directory,
            operating_system_name=operating_system_name,
        )

        temporary_directory = self.__file_system.create_temporary_directory()
        sandbox_path = os.path.join(temporary_directory, "sandbox")
        try:
            self.set_up_loose_sandbox(
                module_names=[build_module_name],
                sandbox_path=sandbox_path,
                release_directory=release_directory,
                progress_callback=progress_callback,
            )

            self.convert_to_work_module(
                module_name=build_module_name,
                release=None,
                branch=None,
                sandbox_root_directory=sandbox_path,
                work_module_type=WorkModuleType.MAIN,
                # main_branch=True,
                progress_callback=progress_callback,
            )

            self.check_out_modules(
                module_names=[build_module_name],
                sandbox_root_directory=sandbox_path,
                release_directory=release_directory,
                progress_callback=progress_callback,
            )

            self.save_modules(
                module_names=[build_module_name],
                sandbox_root_directory=sandbox_path,
                release_note_message="Create build system",
                username=username,
                release_directory=release_directory,
                changelogs_path="",
                keep_release=True,
                operating_system_name=operating_system_name,
                site_name=site_name,
                host_ip=host_ip,
                check_dangling_links=False,
                check_link_modules=False,
            )
        finally:
            self.__file_system.remove_directory(temporary_directory)

    def __unique_branch_id(self, sandbox_root_directory: Optional[str], progress_callback, module_name, revision_tag):
        """Return a unique branch ID.

        This is a branch ID that has not been previously used for the
        given revision.

        """
        vcs_type = self.__database_reader.vcs_type(module_name)
        if sandbox_root_directory is not None:
            parent_directory = os.path.join(sandbox_root_directory, "src")
        else:
            parent_directory = ""
        return module_saving_utils.unique_branch_id(
            module_name=module_name,
            revision_tag=revision_tag,
            revision_control_system=self.__revision_control_system[vcs_type],
            database_reader=self.__database_reader,
            default_branch=self.__default_branch,
            parent_directory=parent_directory,
            progress_callback=progress_callback,
        )

    def out_of_date_link_modules(self, configuration_filename, release_directory):
        """Return list of out-of-date link modules."""
        link_modules = self.__configuration_reader.read_sandbox_configuration(
            configuration_filename=configuration_filename
        )["link_modules"]

        out_of_date_module_names = []

        for name, info_tuple in link_modules.items():
            latest_info_dictionary = self.latest_module_information(
                module_name=name,
                release=None,
                release_directory=release_directory,
            )
            if info_tuple[0] != latest_info_dictionary["tag"] or info_tuple[1] != latest_info_dictionary["build"]:
                out_of_date_module_names.append(name)

        return out_of_date_module_names

    def out_of_date_work_modules(self, configuration_filename, release_directory):
        """Return list of out-of-date work modules."""
        work_modules = self.__configuration_reader.read_sandbox_configuration(
            configuration_filename=configuration_filename
        )["work_modules"]

        out_of_date_module_names = []

        for name, info_tuple in work_modules.items():
            latest_info_dictionary = self.latest_module_information(
                module_name=name,
                release=None,
                release_directory=release_directory,
            )
            if info_tuple[0] != latest_info_dictionary["tag"]:
                out_of_date_module_names.append(name)

        return out_of_date_module_names

    def raise_exception_on_out_of_date_link_modules(self, configuration_filename, release_directory):
        """Raise an exception if any of the link modules are out of date."""
        yam_log.say("Checking for out of date link modules")
        out_of_date_module_names = self.out_of_date_link_modules(
            configuration_filename=configuration_filename,
            release_directory=release_directory,
        )

        if out_of_date_module_names:
            raise OutOfDateLinkModuleException(module_names=out_of_date_module_names)

    def uncommitted_files(self, module_name, sandbox_root_directory):
        """Return list of uncommitted files."""
        yam_log.say("Checking {} module for uncommitted files".format(module_name))
        module_directory = os.path.join(sandbox_root_directory, "src", module_name)
        return self.__revision_control_system.uncommitted_files(module_directory)


class SandboxException(yam_exception.YamException):
    """Exception raised if the sandbox does not exist."""


class ReleaseDirectoryException(yam_exception.YamException):
    """Exception raised if the release directory does not exist."""


class WorkModuleTypeException(yam_exception.YamException):
    """Exception raised if a work module is an unexpected type."""


class SaveException(yam_exception.YamException):
    """Excepted raised if something goes wrong during saving."""

    def __init__(self, save_exception_dictionary):
        """Initialize.

        save_exception_dictionary is a dictionary with keys being the
        module names and values being the exceptions for those modules.

        """
        yam_exception.YamException.__init__(
            self,
            "Some modules {m} ".format(m=tuple(save_exception_dictionary))
            + "could not be saved due to the following errors.\n"
            + "\n".join([str(e) for e in save_exception_dictionary.values()]),
        )

        self.exception_dictionary = save_exception_dictionary


class DanglingLinkException(yam_exception.YamException):
    """Exception raised if dangling links point into module."""

    def __init__(self, dangling_links):
        yam_exception.YamException.__init__(
            self,
            "The following links are dangling: \n{links}".format(links="\n".join(dangling_links)),
        )
        self.dangling_links = dangling_links


class OutOfDateLinkModuleException(yam_exception.YamException):
    """Exception raised if a link module is out of date."""

    def __init__(self, module_names):
        yam_exception.YamException.__init__(
            self,
            "The following link modules are out of date: \n{links}".format(links="\n".join(module_names)),
        )
        self.module_names = module_names


def link_points_into(link, path, file_system):
    """Return True if link points to a subdirectory in path."""
    # Put '/' at end to make sure it matches exactly. Otherwise we will get
    # matches between  "foo" and "food".
    return (path + "/") == file_system.common_prefix([file_system.resolve_path(link) + "/", path + "/"])


def find_dangling_module_links(module_name, sandbox_root_directory, file_system):
    """Raise exception if modules have dangling links pointing to them."""

    def dangling_links(path, destination_path):
        """Return dangling links.

        Recursively find and return a list of any dangling links that
        point to files in destination_path.

        """
        path = file_system.resolve_path(path)
        destination_path = file_system.resolve_path(destination_path)

        return [
            dl
            for dl in file_system.find_dangling_links(path=path)
            if link_points_into(link=dl, path=destination_path, file_system=file_system)
        ]

    dangling_link_paths = []
    module_directory = os.path.join(sandbox_root_directory, "src", module_name)
    for directory_name in ["bin", "doc", "etc", "include", "lib"]:
        dangling_link_paths += dangling_links(
            path=os.path.join(sandbox_root_directory, directory_name),
            destination_path=module_directory,
        )
    return dangling_link_paths


def raise_exception_on_uncommitted_filesOBSOLETE(revision_control_system, module_names, sandbox_root_directory):
    """Raise an exception if there are uncommitted version-controlled files."""
    dangling_links = []

    for m in module_names:
        module_path = sandbox_root_directory + "/src/" + m
        uncommitted_module_files = revision_control_system.uncommitted_files(module_path)
        if uncommitted_module_files:
            raise work_module.UncommittedFilesException(uncommitted_files=uncommitted_module_files)


def raise_exception_on_dangling_links(module_names, sandbox_root_directory, file_system):
    """Raise an exception if there are dangling links."""
    dangling_links = []
    for m in module_names:
        dangling_links += find_dangling_module_links(
            module_name=m,
            sandbox_root_directory=sandbox_root_directory,
            file_system=file_system,
        )
    if dangling_links:
        raise DanglingLinkException(dangling_links=dangling_links)


def raise_exception_on_pre_save_hook_failure(module_names, sandbox_root_directory, file_system):
    """Raise an exception if there are dangling links."""
    for m in module_names:
        module_path = os.path.join(sandbox_root_directory, "src", m)
        hook_path = os.path.join(module_path, ".pyam", "hooks", "pre-save")

        if file_system.path_exists(hook_path):
            try:
                (exit_status, output, error) = file_system.execute(filename=hook_path, working_directory=module_path)
            except OSError:
                raise yam_exception.YamException("Pre-save hook '{f}' is not executable".format(f=hook_path))

            if exit_status != 0:
                raise yam_exception.YamException(
                    "Pre-save hook failure in {m}".format(m=m) + "\n" + output + "\n" + error
                )


def create_git_repoOBSOLETE(git_repo_path):
    repo = Repo.init(git_repo_path)
    repo.git.add(str(git_repo_path) + "/.")
    repo.index.commit("Initial Commit for Register New Module Test")
    # print("Done initializing repo")


def create_and_commit_basic_module_filesOBSOLETE(url, module_name, file_system, build_system, revision_control_system):
    """Check out trunk and add basic files.

    Return the working copy path.

    """
    working_copy_path = file_system.create_temporary_directory()
    revision_control_system.check_out(source=url, target=working_copy_path)

    build_system.create_module_files(
        module_name=module_name,
        module_path=working_copy_path,
        top_level_file_callback=revision_control_system.add_file,
    )

    revision_control_system.check_in(path=working_copy_path, log_message="pyam: Add initial files")

    return working_copy_path


def create_and_commit_basic_module_files_gitOBSOLETE(
    url, module_name, file_system, build_system, revision_control_system
):
    build_system.create_module_files(module_name=module_name, module_path=url)
    revision_control_system.add_file(url)

    # dont need to pass path for git because the repo object knows what repo to commit
    revision_control_system.check_in(path=None, log_message="pyam: Add initial files")


def create_and_commit_package_files(url, package_name, file_system, revision_control_system):
    """Check out trunk and add files needed for a package."""
    working_copy_path = file_system.create_temporary_directory()
    # this currently requires an SVN version control system
    revision_control_system._pkg_check_out(source=url, target=working_copy_path)

    def add_file(filename, contents):
        """Create and add empty filename."""
        path = os.path.join(working_copy_path, filename)
        file_system.write_to_file(string_data=contents, filename=path)
        revision_control_system.add_file(path)

    for f in ["ChangeLog", "YAM.config", "version"]:
        add_file(f, contents="\n")

    release_note_path = os.path.join(working_copy_path, "ReleaseNotes")
    wrapped_description = textwrap.fill(
        """This file documents API, usage, portability etc.
changes that have been introduced in new versions of the "{package}" package.
This information should be kept in mind when upgrading to newer versions of
the package. This file may also document major bug fixes in so far as they
may impact upgrade decisions. More complete and detailed information on
changes to the "{package}" package can be found in the ChangeLog
file.""".format(
            package=package_name
        ),
        width=79,
        break_long_words=False,
    ).strip()

    file_system.write_to_file(
        string_data="""Release notes for "{package}" package

{description}

Release R1-00:

\tCreate package
""".format(
            package=package_name, description=wrapped_description
        ),
        filename=release_note_path,
    )

    revision_control_system.add_file(release_note_path)
    del release_note_path

    revision_control_system.check_in(path=working_copy_path, log_message="pyam: Add initial files")

    file_system.remove_directory(working_copy_path)


def check_out_and_commit_build_files(
    url,
    file_system,
    revision_control,
    build_system,
    release_directory,
    operating_system_name,
):
    """Check out working copy and add build files."""
    working_copy_path = file_system.create_temporary_directory()
    try:
        # revision_control.check_out(source=url, target=working_copy_path)

        # fix this
        revision_control.module_check_out(source=url, target=working_copy_path)

        def add_callback(path):
            """Add file while ignoring exception if already added."""
            from . import revision_control_system

            try:
                revision_control.add_file(path)
            except revision_control_system.AlreadyUnderRevisionControl:
                pass

        build_system.create_build_files(
            path=working_copy_path,
            release_directory=release_directory,
            operating_system_name=operating_system_name,
            top_level_file_callback=add_callback,
        )

        revision_control.check_in(path=working_copy_path, log_message="Add build files")
    finally:
        file_system.remove_directory(working_copy_path)


def append_package_to_configuration_if_needed(
    package_name,
    modules,
    file_system,
    revision_control_system,
    database_reader,
    config_reader,
    progress_callback=lambda _: None,
):
    """Append package to configuration file."""
    working_copy_path = file_system.create_temporary_directory()

    # print('UUUU', database_reader.default_repository_url())
    # this currently requires an SVN version control system
    revision_control_system._pkg_check_out(
        source=package_sandbox.common_trunk_url(database_reader=database_reader),
        target=working_copy_path,
    )

    configuration_filename = os.path.join(working_copy_path, "YAM.modules")

    configuration = file_system.read_file(filename=configuration_filename)

    from . import configuration_reader

    try:
        # check whether package has already been defined in YAM.modules
        module_names = config_reader.read_package_information(
            package_configuration_filename=configuration_filename,
            package_name=package_name,
        )
        assert module_names

        # verify that the definitions coincide
        if modules and set(modules) != set(module_names):
            raise ValueError(
                "The command line modules list {cmdmodules} does not match the {yammodules} modules list in YAM.modules for the {pkg} package.".format(
                    cmdmodules=modules,
                    yammodules=sorted(list(map(str, module_names))),
                    pkg=package_name,
                )
            )

    except configuration_reader.ConfigurationError:
        # there is no defintion for this package in YAM.modules, so add one
        if not modules:
            raise ValueError(
                "Need to specify the modules list for the new {pkg} package either on the command line or in YAM.modules.".format(
                    pkg=package_name
                )
            )

        progress_callback('Appending to package configuration file "YAM.modules"')

        file_system.write_to_file(
            string_data=configuration
            + """

MODULES_{package} = {modules}
""".format(
                package=package_name, modules=" ".join(modules)
            ),
            filename=configuration_filename,
        )

        revision_control_system.check_in(
            working_copy_path,
            log_message="Add {package}".format(package=package_name),
        )

    file_system.remove_directory(working_copy_path)


def _check_sandbox_directory(path, file_system):
    """Raise exception if sandbox path is not valid."""
    if path:
        if not file_system.path_exists(path):
            raise SandboxException("Sandbox directory '{d}' does not exist".format(d=path))
    else:
        raise SandboxException("Sandbox directory not specified")


def _check_release_directory(path, file_system, require):
    """Raise exception if release path is not valid."""
    if require and not path:
        raise ReleaseDirectoryException("Release directory not specified")

    if path and not file_system.path_exists(path):
        raise ReleaseDirectoryException("Release directory '{d}' does not exist on the filesystem".format(d=path))


def _check_working_copyOBSOLETE(sandbox_root_directory, module_names, revision_control_system):
    """Raise exception if release path is not valid."""
    for m in module_names:
        yam_log.say("Checking whether {} work module is checked out".format(m))
        if not revision_control_system.working_copy_exists(os.path.join(sandbox_root_directory, "src", m)):
            raise yam_exception.YamException("Module '{m}' is not checked out".format(m=m))


def ansi(code):
    """Return escaped color code."""
    return "\x1b[" + code


def _generate_release_note_message(log_filter, reference_log, name):
    """Generate release note message.

    reference_log is a string that describes the changes. (For example a
    diff.) Empty reference_log means there are no changes and we will
    return an empty string.

    """

    if reference_log:

        def comment_line(line):
            """Return the line commented."""
            if line:
                return "# " + line
            else:
                return "#"

        helpful_message = """
# Enter a release note message above if desired.                       #
#                                                                      #
# Module: {m}
#
# The below log is for reference only. Do not modify the lines below as
# they will be ignored.
#
{log}

# Text should wrap at 72 columns.
# vim: set textwidth=72 fo=t comments=:# commentstring=# :
""".format(
            m=name,
            log="\n".join([comment_line(l) for l in reference_log.split("\n")]),
        )

        def is_not_a_comment(line):
            """Return True if line is not a comment."""
            return not line.strip().startswith("#")

        lines = [l.rstrip() for l in log_filter(helpful_message).split("\n")]
        entry = "\n".join(filter(is_not_a_comment, lines))

        return textwrap.dedent(entry)
    else:
        # No release note entry is necessary if no changes were made to the
        # module.
        return ""


def _fill_in_common_trunk(main_branch_url, revision_control_system, file_system, release_directory):
    """Fill in contents of "common/trunk" directory in the repository."""
    _add_files_to_repository(
        url=main_branch_url,
        revision_control_system=revision_control_system,
        file_system=file_system,
        filename_to_content_dictionary={
            "Makefile": _common_makefile_contents.format(release_directory=release_directory),
            "README": _common_readme_contents,
            "YAM.modules": _common_yam_modules_contents,
        },
    )


def _add_files_to_repository(url, revision_control_system, file_system, filename_to_content_dictionary):
    """Add files to repository.

    This involves checking out a working copy to a temporary directory,
    creating the files, and committing them.

    filename_to_content_dictionary is a dictionary with filename keys and
    file content values. The filenames are relative to main_branch_url.

    """
    temporary_directory = file_system.create_temporary_directory()
    # Fix this
    # assert 0
    try:
        revision_control_system._pkg_check_out(source=url, target=temporary_directory)

        for name, contents in filename_to_content_dictionary.items():
            full_path = os.path.join(temporary_directory, name)
            file_system.write_to_file(string_data=contents, filename=full_path)
            revision_control_system.add_file(path=full_path)

        revision_control_system.check_in(path=temporary_directory, log_message="pyam: Add initial files")
    finally:
        file_system.remove_directory(temporary_directory)


def _is_main_module(data):
    """Return True if data represents a main module."""
    return data[0] is None and data[1] is None


def _is_branched_module(data):
    """Return True if data represents a branched module."""
    return data[0] is not None and data[1] != ""


def _is_tagged_module(data):
    """Return True if data represents a tagged module."""
    return data[0] is not None and data[1] == ""


def _recursive_dependencies(node, resolve, seen=None):
    """Return all of dependencies/dependents of "node".

    "resolve" is used to determine dependencies.

    """
    if not seen:
        seen = set()

    if node in seen:
        return set()
    else:
        # take the union
        seen |= {node}

        found_dependencies = resolve(node)
        if not found_dependencies:
            found_dependencies = set()
        results = set(found_dependencies)

    for d in found_dependencies:
        results |= _recursive_dependencies(d, resolve, seen)
    # print('node=', node, 'deps=', results)
    return results


# TODO: Move this stuff to MakeBuildSystem
_common_makefile_contents = """
########################################################################
#
# !!!!!! DO NOT EDIT THIS FILE !!!!!!
#
# It is autogenerated by pyam.
#
########################################################################
#
# a top level Makefile for building the YAM software
# this includes the YAM.config file to get definitions of the
# WORK_MODULES and LINK_MODULES variables

# get the name of the local directory. Strip out any leading /export or
# /tmp_mnt from the path if running under SunOS4
export YAM_ROOT := $(shell pwd | sed -e 's@/tmp_mnt@@')
COMMON_DIR := $(YAM_ROOT)/common

# the location of the module release area for use when
# SiteDefs is a link module
YAM_VERSIONS ?= {release_directory}/Module-Releases

# set a default value for the targets to build for
#YAM_TARGETS := $(YAM_TARGET)

#=======================================================
# SiteDefs setup
#=======================================================
# check is the modules list is being specified on the command line
ifeq ($(origin WORK_MODULES),command line)
    ORIGIN_CMD_LINE := true
endif

ifeq ($(origin WORK_MODULES1),command line)
    ORIGIN_CMD_LINE := true
    WORK_MODULES := $(WORK_MODULES1)
endif

ifeq ($(origin LINK_MODULES),command line)
    ORIGIN_CMD_LINE := true
endif


# get the definitions of the WORK_MODULES and LINK_MODULES variables
# from YAM.config unless their values are being specified on the command
# line
ifneq ($(ORIGIN_CMD_LINE),true)
    ifeq ($(YAM_ROOT)/YAM.config,$(wildcard $(YAM_ROOT)/YAM.config))
        include YAM.config
    endif
endif

ifeq ($(wildcard etc/SiteDefs/Makefile.yam),etc/SiteDefs/Makefile.yam)
    HAVE_SITEDEFS :=
else
    HAVE_SITEDEFS := false
endif
# We need to look for etc/SiteDefs/Makefile.yam instead of simply etc/SiteDefs.
# This is necessary because sometimes etc/SiteDefs link exists but is pointing
# nowhere (such as right after a SiteDefs release). By looking for Makefile.yam
# we know conclusively whether the link is pointing to some place real or not

ifeq ($(HAVE_SITEDEFS),false)
    ifeq ($(filter SiteDefs,$(WORK_MODULES)),)
        ifeq ($(filter SiteDefs/SiteDefs-R%,$(LINK_MODULES)),)
            $(error "Error: The etc/SiteDefs link is missing!!!\"")
        endif
    endif
    ifneq ($(filter SiteDefs,$(WORK_MODULES)),)
        PATH_SITEDEFS := ../src/SiteDefs
        FULLPATH_SITEDEFS := $(YAM_ROOT)/src/SiteDefs
        INCPATH_SITEDEFS := ./etc/SiteDefs
    else
        LINK_SITEDEFS := $(filter SiteDefs/SiteDefs-R%,$(LINK_MODULES))
        ifneq ($(LINK_SITEDEFS),)
            PATH_SITEDEFS := $(YAM_VERSIONS)/$(LINK_SITEDEFS)
            FULLPATH_SITEDEFS := $(PATH_SITEDEFS)
            INCPATH_SITEDEFS := $(YAM_VERSIONS)/$(LINK_SITEDEFS)
        endif
    endif
endif

help:: ./etc/SiteDefs

./etc/SiteDefs: ./etc
ifneq ($(PATH_SITEDEFS),)
    ifeq ($(HAVE_SITEDEFS),false)
\t@echo "   Deleting existing, bad etc/SiteDefs link ..."
\t@rm -f etc/SiteDefs
    endif
\t@if [ ! -h ./etc/SiteDefs ]; then \
\techo "   linking $(PATH_SITEDEFS) into ./etc/SiteDefs ..."; \
\tln -f -s $(PATH_SITEDEFS) $@; \
    else \
        echo "Skipping - ./etc/SiteDefs link already exists"; \
    fi
    else
        # We should never reach this part.
    endif

./etc:
\t@mkdir -p etc

# Do nothing if the link for SiteDefs exists and is real if the link is
# non-existent or bad, check that the candidate SiteDefs path is real. Barf if
# this is not the case. Else create the etc/SiteDefs link and then build the
# actual target.
.DEFAULT:
ifneq ($(HAVE_SITEDEFS),)
\t@$(MAKE) --no-print-directory CREATE_SITEDEFS_LINK
\t@echo ""
\t@echo "  **** The etc/SiteDefs link has been created. ****"
# now reinvoke the make with the actual rule
\t@$(MAKE) --no-print-directory $(MAKECMDGOALS)
\t@echo ""
endif

CREATE_SITEDEFS_LINK:
ifneq ($(wildcard $(FULLPATH_SITEDEFS)),$(FULLPATH_SITEDEFS))
\t@echo "Error: >>>>> Cannot find the $(FULLPATH_SITEDEFS) directory <<<<"
else
\t@$(MAKE) --no-print-directory ./etc/SiteDefs
endif


#=======================================================
# The following lines should be kept after the HAVE_SITEDEFS
# variable has been set which needs the original definition of
# these values in YAM.config to find out whether SiteDefs is a work
# or a link module

# Use command line definition of work/link modules if specified via the MODULES
# variable.
ifdef MODULES
    # extract all link module entries which match either the traditional
    # Darts/Darts-R2-32f-Build01 string, or the full path specification
    # with the module name at the end (eg. /home/jain/sbox/src/Darts)
    LINK_MODULES := $(foreach l, $(MODULES), \
\t$(filter $(l)/%,$(LINK_MODULES)) $(filter %/$(l),$(LINK_MODULES)) )
    WORK_MODULES := $(foreach l, $(MODULES), \
\t$(filter $(l),$(WORK_MODULES)))
endif

# The following is added primarily for the rmlinks to work
# robustly. The idea here is that when doing a top level rmlinks,
# we need to make sure that the SiteDefs links get removed last
# to avoid breaking things for the modules that follow it because
# they cannot find the SiteDefs files anymore.
# The following makes sure that any references to SiteDefs are
# moved to the end of the work/link modules list.
# ---
# This fix will always work if you have only link or work modules.
# and sometimes when you have a mix. It might break if SiteDefs is
# a link module and there are work modules defined as well, because
# the processing of the link modules will delete the SiteDefs link
# breaking the processing of the work modules. One might need to
# add in a check at the beginning of the work modules processing to
# make sure that the SiteDefs link exists.
SITEDEFS_WORKMOD := $(findstring SiteDefs, $(WORK_MODULES))
SITEDEFS_LINKMOD := $(filter SiteDefs/SiteDefs-%, $(LINK_MODULES))
ifneq ($(SITEDEFS_LINKMOD),)
    LINK_MODULES := $(filter-out $(SITEDEFS_LINKMOD), $(LINK_MODULES)) \
        $(SITEDEFS_LINKMOD)
endif
ifneq ($(SITEDEFS_WORKMOD),)
    WORK_MODULES := $(filter-out $(SITEDEFS_WORKMOD), $(WORK_MODULES)) \
        $(SITEDEFS_WORKMOD)
endif

#=======================================================
# Handy debugging rules
#=======================================================

# rule to print out variables specified from the command line
myvars:
\t@$(foreach i, $(MYVARS), echo "$i=<$($i)>";)

# bring in the rule definitions once we have a valid link for SiteDefs
ifeq ($(HAVE_SITEDEFS),)
    include etc/SiteDefs/mkHome/shared/Makefile.top
endif
""".lstrip()

_common_readme_contents = """
README file for contents of $YAM_ROOT/common directory
------------------------------------------------------
We use the optional YAM module "SiteDefs" to provide files included by
Makefiles that specify compilers to use, compilation options, etc. If you have
this module, it may also be worth looking at SiteDefs/README.

Makefile
- Toplevel Makefile with targets "links", "depends", "libs", "bins".
- It runs "make -f Makefile.yam" for these targets in all subdirectories of
  "$YAM_ROOT/src" (which are WORK_MODULES in $YAM_ROOT/YAM.config).
- A link to this Makefile gets put in the toplevel $YAM_ROOT directory.

site.env
- Set default values for YAM environment variables.
- Don't need to edit unless adding a new supported platform.
- Included by common/Makefile, SiteDefs/Makefile.yam-common, and
  SiteDefs/site.include.

YAM.modules
- Important file! This specifies which modules make up a package.
- This is used by "pyam setup" to create a candidate YAM.config file.
""".lstrip()

_common_yam_modules_contents = """
# common/YAM.modules
#
# This file specifies the modules needed for all packages. A "module" is the
# name of a program or library, such as "Dshell". A "package" is a collection
# of modules for a specific project, such as "ROAMSDshellPkg".
#
# YAM.config has more information in it than this file, and tells which
# versions of modules to check out or link to. This file specifies how
# "pyam setup" should create a default YAM.config for the user to edit.
#
# Variables of the form MODULES_pkg should be set in this file, where "pkg" is
# the name of a package. Lines that end with backslash get continued with the
# next line.
#
# Create a new module "foo" with "pyam register-new-module foo". Create a new
# package "bar" with "pyam register-new-package bar". After doing so, edit this
# file to specify a variable of the form "MODULES_bar = foo baz"
#
# Packages may include all the modules of another package by specifying
# $(MODULES_pkg2) in its list of modules, where "pkg2" is the name of the other
# package and is defined ahead of time. In other words, variables get expanded
# here as do in Makefiles (actually like the ":=" variable assignment, as
# opposed to "=").

""".lstrip()
