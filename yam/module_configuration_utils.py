"""
Utility function that are used for transforming the lin/work module
module information from YAM.config files.
"""

from __future__ import absolute_import

import os

# import re
# import textwrap

# from . import savable_module
# from . import saving_utils
# from . import work_module
from . import yam_log
from . import yam_exception
from . import branched_work_module
from . import module_saving_utils
from . import revision_tag_utils
from .module import WorkModuleType


def module_save_update_configuration(
    module_dictionary,  # existing module data
    new_revision_tag_and_build_id_dictionary,  # new module data
    check_out_again_after_saving,
    check_out_tagged,
    default_branch,
):
    """
    Update the modules configuration via the speccified dictionary when
    saving a module.
    """

    # loop through and process all the new module data
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
                        default_branch,
                    )
        else:
            # Update the configuration. The work module should become a
            # link module with an updated tag.
            del module_dictionary["work_modules"][name]
            module_dictionary["link_modules"][name] = list(new_revision_tag_and_build_id) + [None, None]


def work_module_tag_branch(
    module_dictionary, module_name, new_tag_and_branch  # existing module data  # module name  # new tag and branch pair
):
    """
    Switch the existing work module info to the new tag and branch.
    """
    assert module_name in module_dictionary["work_modules"]
    module_dictionary["work_modules"][module_name] = new_tag_and_branch


def work_module_to_main(module_dictionary, module_name):  # existing module data  # module name
    """
    Switch the existing work module info to the main trunk.
    """
    new_tag_and_branch = [None, None]
    work_module_tag_branch(module_dictionary, module_name, new_tag_and_branch)


def add_new_work_module(
    module_dictionary, module_name, release, branch, database_reader, unique_branch_id_cb  # existing module data
):
    """
    Add the new work module to the configuration
    """
    link_modules = module_dictionary["link_modules"]
    if module_name in link_modules:
        raise yam_exception.YamException(
            "Module {} is a link module, but the user asked for a work module. Giving up.".format(module_name)
        )

    # Add module to work module dictionary
    work_modules = module_dictionary["work_modules"]

    # if we asked for a particular version, and the current sandbox has
    # something else, this is a big, bad error. Otherwise, we can catch
    # it

    def branch_eq(have, want):
        if have is None and want == "":
            return True
        return have == want

    if branch == "-":
        branch = ""  # check out a release tag
    if module_name in work_modules:
        if release is not None and (
            work_modules[module_name][0] != release
            or (branch is not None and not branch_eq(work_modules[module_name][1], branch))
        ):
            raise yam_exception.YamException(
                "Work module {} already exists in the sandbox'd YAM.config file. Have tag/branch {}/{}, but requested tag/branch {}/{}. Giving up.".format(
                    module_name,
                    work_modules[module_name][0],
                    work_modules[module_name][1],
                    release,
                    branch,
                )
            )
        raise AlreadyAModuleException(
            "Module '{m}' already exists in the sandbox's YAM.config file".format(m=module_name)
        )

    getbranch = False
    # if no release is specified, get the latest from the database
    if release is None:
        release = database_reader.latest_module_information(module_name=module_name)["tag"]
        getbranch = True
    else:
        if release == "main":
            release = None
        else:
            getbranch = True

    if getbranch and branch is None:
        # get unique branch id from the database
        branch = unique_branch_id_cb(module_name=module_name, revision_tag=release)

    work_modules[module_name] = (release, branch)


def convert_to_work_module(
    module_dictionary,  # existing module data
    module_name,
    release,  # if 'main', then trunk version
    branch,  # branch to use. If null, look up a unique branch id. If '-' no branch
    work_module_type,
    progress_callback,
    unique_branch_id_cb,
):
    """
    Convert the existing link/work module into a work module
    """

    # get the list of link modules defined in YAM.confg that are
    # different from the specified module

    link_modules = {k: v for k, v in module_dictionary["link_modules"].items() if k != module_name}
    # print(link_modules)

    # if revision tag is a maintenance release, set tagged_branch to true

    if release == "main":
        release = None
        branch = None

    # get the list of work modules defined in YAM.confg
    work_modules = dict(module_dictionary["work_modules"])
    # print('modules=', module_dictionary)
    # print('link_modules=', link_modules)
    # print('work_modules=', work_modules)
    # print('MMM0', module_name, [release, branch, tagged_branch, main_branch])
    if module_name in module_dictionary["link_modules"]:
        # print('LLL')
        # release, build id, maint branch, maint id
        tag = module_dictionary["link_modules"][module_name]
        # print('tag=',tag)
        # Extract the revision and maintenance branch info from the link module data
        # if main_branch:
        if WorkModuleType.MAIN == work_module_type:
            # a main trunk checkout is specified
            revision_tag = None
            branch_id = None
        else:
            from . import concrete_configuration_reader

            # get a revison tag for this link module
            revision_tag = revision_tag_utils.tuple_to_release_tag_suffix(tag=tag, use_build=False)
            # print('revtag=',revision_tag)

        # tag[2] is the maintenance branch name
        # if main_branch or tag[2]:
        if (WorkModuleType.MAIN == work_module_type) or tag[2]:
            # we have the main trunk or a maintenance bramch rev
            branch_id = None

        else:
            # get the desired branch
            ###if tagged_branch:
            if WorkModuleType.TAGGED == work_module_type:  # default is to use link module
                branch_id = None

            elif branch is None:
                branch_id = unique_branch_id_cb(module_name=module_name, revision_tag=revision_tag)

                # print('SSSSS getting unique branch id', branch_id)
            else:
                branch_id = branch
                if branch_id == "-":
                    branch_id = ""  # check out a release tag

        def branch_eq(have, want):
            if want is None:
                return True
            if have is None and want == "":
                return True
            return have == want

        if branch == "-":
            branch = ""  # check out a release tag

        # compare the link module release info with the user specified ones
        if release is not None and (
            revision_tag != release or (branch is not None and not branch_eq(branch_id, branch))
        ):
            raise yam_exception.YamException(
                "Link module {} already exists in the sandbox with tag/branch {}/{}, but requested tag/branch {}/{}. Giving up.".format(
                    module_name, revision_tag, branch_id, release, branch
                )
            )

        # convert to a work module
        work_modules[module_name] = (revision_tag, branch_id)
        # print('revision_tag=', revision_tag, 'branch_id=', branch_id)
        progress_callback("Converting '{m}' to a work module".format(m=module_name))
    else:
        # module is a work module
        # print('FFFF')
        if module_name in work_modules:
            # print('FFFF1')
            # we already have a work module. If we asked for specific
            # versions, we barf unless the exact versions exist already
            def branch_eq(have, want):
                if want is None:
                    return True
                if have is None and want == "":
                    return True
                return have == want

            if branch == "-":
                branch = ""  # check out a release tag

            tagbr = work_modules[module_name]
            # print('FFFF2', tagbr)
            if release is not None and (
                tagbr[0] != release or (branch is not None and not branch_eq(tagbr[1], branch))
            ):
                raise yam_exception.YamException(
                    "Work module {} YAM.config entry already exists in the sandbox's YAM.config with tag/branch {}/{}, but requesting inconsistent tag/branch {}/{}. Giving up.".format(
                        module_name, tagbr[0], tagbr[1], release, branch
                    )
                )

            if tagbr[0] and tagbr[1] is None:
                revision_tag = tagbr[0]

                work_modules[module_name] = (
                    revision_tag,
                    unique_branch_id_cb(module_name=module_name, revision_tag=revision_tag),
                )
            else:
                raise AlreadyAModuleException(
                    "Module '{m}' is already a work module in the YAM.config file".format(m=module_name)
                )
        else:
            raise MissingModuleException(
                "Module '{m}' does not exist in this sandbox's YAM.config file".format(m=module_name)
            )

    module_dictionary["link_modules"] = link_modules
    module_dictionary["work_modules"] = work_modules


def convert_work_module_to_link_module(
    module_dictionary,  # existing module data
    module_name,
    branch_id,
    release_directory,
    database_reader,
    latest_module_information_cb,
):
    """
    Convert a work module into a link module. If a revision tag is
    specified, then find the latest build release from the for that
    reevision in the database. If no revision tag is specified then use
    the lastest releasse as the revision tag.
    """
    link_modules = module_dictionary["link_modules"]
    old_work_modules = module_dictionary["work_modules"]

    try:
        module_information = old_work_modules[module_name]
    except KeyError:
        if module_name in link_modules:
            raise AlreadyAModuleException("Module '{m}' is already a link module".format(m=module_name))
        else:
            raise MissingModuleException("Module '{m}' does not exist in this sandbox".format(m=module_name))

    # get the input reviesion tag (None for the latest)
    revision_tag = module_information[0]

    if revision_tag:
        # Get latest build ID if there is one. Note that we don't the the
        # latest revision information. We need the build ID for a specific
        # and possibly older revision.
        build_id = database_reader.module_information(module_name=module_name, revision_tag=revision_tag)["build"]
    else:
        # no revision tag spsecified, so look up the latest one
        # info = self.latest_module_information(
        info = latest_module_information_cb(
            module_name=module_name,
            release=None,
            release_directory=release_directory,
        )
        revision_tag = info["tag"]
        build_id = info["build"]

    # Copy of work module dictionary (with module_name removed)
    module_dictionary["work_modules"] = {k: v for k, v in module_dictionary["work_modules"].items() if k != module_name}

    # return the revision tab/build id for the work module
    return revision_tag, build_id


def add_latest_available_module(
    module_dictionary,
    module_name,
    work_module_type,
    revision_control_system,
    release_directory,
    database_reader,
    default_branch,
    file_system,
    parent_directory,
    progress_callback,
):
    """
    Add the latest available module info for this module. If the link
    module exists on the file system, a link module is added, else a
    work module is added. If to_work is true, then a work module is
    added.
    """
    link_modules = module_dictionary["link_modules"]
    work_modules = module_dictionary["work_modules"]

    # if forcing work module, then only one type
    #     assert not (main_branch and tagged_branch)
    #     assert not (main_branch and work_branch)
    #     assert not (tagged_branch and work_branch)

    # verify that the module is not alread in the list of link and work
    # modules
    assert module_name not in link_modules and module_name not in work_modules

    # Get dictionary containing 'branch', 'build', 'datetime',
    # 'missing', and 'tag' for the latest module release. missing if
    # False if the release is available as a link module on the file
    # system
    # print('reldir=', release_directory)
    info = module_saving_utils.latest_module_information(
        module_name=module_name,
        release=None,  # latest
        release_directory=release_directory,
        database_reader=database_reader,
        file_system=file_system,
    )

    # print('GGG', work_branch, tagged_branch, main_branch)
    # to_work = work_branch or tagged_branch or main_branch
    to_work = WorkModuleType.NONE != work_module_type
    # print('MMM', module_name, info, work_module_type, to_work)
    # print('QQQQ', to_work, ' miissing=', info['missing'])
    if to_work or info["missing"]:
        revision_tag = None
        branch_id = None
        # print('HHH', module_name, info)
        # if not main_branch:
        if WorkModuleType.MAIN != work_module_type:
            revision_tag = info["tag"]

            # if info["missing"] or
            # if not tagged_branch:
            if WorkModuleType.BRANCH == work_module_type:
                # crate a branch checkout

                # print('MOD=', module_name)
                # print('GGGG', module_name, revision_tag, default_branch,
                #      database_reader.module_repository_url(
                #          module_name))
                branch_id = module_saving_utils.unique_branch_id(
                    module_name=module_name,
                    revision_tag=revision_tag,
                    revision_control_system=revision_control_system,
                    database_reader=database_reader,
                    default_branch=default_branch,
                    parent_directory=parent_directory,
                    progress_callback=progress_callback,
                )
            elif WorkModuleType.TAGGED == work_module_type:
                # create a tagged release
                branch_id = ""
            elif info["missing"]:
                # we really want a link module, but it is not in the
                # release area, so create a tagged release
                branch_id = ""

        # print('LLL', module_name, rev, branch_id)
        work_modules[module_name] = (revision_tag, branch_id)
    else:
        # print('SSSS')
        link_modules[module_name] = (
            info["tag"],
            info["build"],
            None,
            None,
        )


def get_latest_available_modules(
    module_names,
    work_module_type,
    revision_control_system,
    release_directory,
    database_reader,
    default_branch,
    file_system,
    parent_directory,
    progress_callback,
):
    """
    Get the latest link/work module available for this list of module
    names. Link modules are used if available, unless work modules are
    requested.
    """

    # initialize and empty modules dictionary
    module_dictionary = {"work_modules": {}, "link_modules": {}}

    for module_name in module_names:
        add_latest_available_module(
            module_dictionary,
            module_name,
            work_module_type,
            revision_control_system,
            release_directory,
            database_reader,
            default_branch,
            file_system,
            parent_directory,
            progress_callback,
        )

    # print('Mods=', module_dictionary)
    return module_dictionary


def update_with_available_modules(
    module_dictionary,
    to_work,
    # $work_branch=work_branch,    # specified branch work module
    # tagged_branch=tagged_branch,  # tagged release work module
    # main_branch=False,     # main trunk work module
    branch,
    release_directory,
    database_reader,
    file_system,
):
    """
    If a link module is unavailable in the release area replace it with
    a corresponding work module. Always replace if to_work is True.
    """

    converted_lms = []
    for module_name, module_data in module_dictionary["link_modules"].items():
        revision, build, maint_br, maint_id = module_data

        # if to_work is true, or not available in the release are,
        # replace with a work module:
        convert_to_wm = to_work
        if not convert_to_wm:
            info = module_saving_utils.latest_module_information(
                module_name, revision, release_directory, database_reader, file_system
            )
            convert_to_wm = info["missing"]
            yam_log.say(
                "The %(m)s module with %(r)s revision is not available in the release area. Converting to a work module".format(
                    m=module_name, r=revision
                )
            )

        if convert_to_wm:
            converted_lms.append(module_name)
            # build the revision tag for the work module (including
            # handling of maintenance bracnches)
            from . import concrete_configuration_reader

            # get a revison tag for this link module
            revision_tag = revision_tag_utils.tuple_to_release_tag_suffix(tag=module_data, use_build=False)
            module_dictionary["work_modules"][module_name] = [revision_tag, branch]

    # get the list of link modules that have not been converted
    link_modules = {k: v for k, v in module_dictionary["link_modules"].items() if k not in converted_lms}
    module_dictionary["link_modules"] = link_modules


def remove_modules(
    module_dictionary, module_list, sandbox_root_directory, progress_callback, file_system  # existing module data
):
    """
    Remove the speified modules from the configuration.
    """
    link_modules = module_dictionary["link_modules"]
    work_modules = module_dictionary["work_modules"]
    for module_name in module_list:
        if module_name in link_modules:
            progress_callback("Removing '{m}' link module from the sandbox".format(m=module_name))
            del link_modules[module_name]
        elif module_name in work_modules:
            progress_callback("Removing '{m}' work module from the sandbox".format(m=module_name))
            del work_modules[module_name]
            if 1:  # try:
                ## print("Appending module directory name in the sandbox with timestamp")
                import time

                module_path_new = time.strftime("__%Y_%m_%d__%H_%M_%S")
                orig_dir = sandbox_root_directory + "/src/" + module_name
                if file_system.path_exists(orig_dir):
                    new_dir = sandbox_root_directory + "/src/" + module_name + module_path_new
                    if file_system.path_exists(new_dir):
                        new_dir += "dummy"
                    # os.rename(orig_dir, new_dir)
                    file_system.move(orig_dir, new_dir)
                    del orig_dir
                else:
                    print("Nothing to do - the {} module is not in the src/ director".format(module_name))

            # except:
            #    raise ValueError("Unable to rename %s directory to %s" % (orig_dir, new_dir))
        else:
            raise MissingModuleException(
                "Module '{m}' does not exist in this sandbox's YAM.config as a link or a work module".format(
                    m=module_name
                )
            )


def update_link_modules(
    module_dictionary,  # existing module data
    to_release,  # = None,
    module_names,  # =None,
    release_directory,
    latest_module_information_cb,
):
    """
    Update the specified link module to the specified release
    """

    # Create link module dictionary with updated revision tags and build
    # IDs.
    def latest_tag_and_build(module_name, release=None):
        """Return (tag, build) tuple for the specified release. Use the latest
        release if unspecified."""
        # info = self.latest_module_information(
        info = latest_module_information_cb(
            module_name=module_name,
            release=to_release,
            release_directory=release_directory,
        )

        if info["build"]:
            return (info["tag"], info["build"], None, None)
        else:
            return (info["tag"], None, None, None)

    if module_names:
        # raw release info for all the link modules in the YAM.config file
        link_modules = {m: module_dictionary["link_modules"][m] for m in module_dictionary["link_modules"]}

        # latest release info for all the link modules in the YAM.config file
        lms = {m: latest_tag_and_build(m, to_release) for m in module_names}

        # latest release info for only the outdated link modules that
        # are in the command line as well as the YAM.config file
        outdated_link_module_names = lms.keys()

        # update to the latest info for the modules we want to update
        for m, data in lms.items():
            link_modules[m] = data

    else:
        # latest release info for all the link modules in the YAM.config file
        link_modules = {m: latest_tag_and_build(m, to_release) for m in module_dictionary["link_modules"]}

        # latest release info for the link modules that are NOT the latest release
        outdated_link_module_names = [
            m for m in link_modules if link_modules[m] != module_dictionary["link_modules"][m]
        ]

        # revert to the link module versions in the YAM.config file for all but the outdated modules
        for name in list(link_modules):
            if name not in outdated_link_module_names:
                link_modules[name] = module_dictionary["link_modules"][name]

    module_dictionary["link_modules"] = link_modules
    return outdated_link_module_names


def package_release_check(module_dictionary, database_reader, release_configuration_filename):  # existing module data
    """
    Check that modules are OK for inclusion in a package release. No
    modules on the main trunk or on a branch
    """

    # verify that work modules are tagged modules and convert them into link modules
    lms = module_dictionary["link_modules"]
    wms = module_dictionary["work_modules"]
    for m, data in wms.items():
        tag = data[0]
        # print('LLL', m, data)
        branch = data[1]
        # maintenance_branch = None
        # maintenance_release = None
        # if branch is not null, then verify that it is a maintenance release
        # print('XXX', m, tag, branch)
        if not tag:
            # on the main trunk
            raise ValueError(
                "Main trunk {} module in {} config file cannot be used in a package release.".format(
                    m, release_configuration_filename
                )
            )
        if branch:
            maintenance_branch, maintenance_release = revision_tag_utils.branch_to_maintenance_tuple(branch)
            raise ValueError(
                "{} module with {}-{} branch in {} config file cannot be used in a package release.".format(
                    m, tag, branch, release_configuration_filename
                )
            )

        just_tag = tag.replace(m + "-", "")
        from . import concrete_configuration_reader

        revision, build, maintenance_branch, maintenance_release = revision_tag_utils.split_tag(just_tag)
        # print('GGG', elt[0], ',', elt[1], ',', elt[2], ',', elt[3])
        # maintenance_branch = elt[2]
        # maintenance_release = elt[3]
        # maintenance_branch, maintenance_release = revision_tag_utils.branch_to_maintenance_tuple(
        # just_tag # branch
        # )
        # print('  YYY', maintenance_branch, maintenance_release)

        if maintenance_branch:
            if not maintenance_release:
                raise ValueError(
                    "Branch {} for {} module in {} config file does not correspond to a maintenance release.".format(
                        branch,
                        m["name"],
                        release_configuration_filename,
                    )
                )
            # convert this into a link module
            lms[m] = (
                revision,
                None,
                maintenance_branch,
                maintenance_release,
            )
        else:
            lms[m] = (tag, None, None, None)

    # verify that the module releases are valid
    for m, data in lms.items():
        """
        self.__database_reader.module_information(m, data[0])
        """
        try:
            # print('FFF', m, data[0], data[2], data[3])
            database_reader.module_information(m, data[0], data[2], data[3])
            # print('FFF1', m, data[0], data[2], data[3])
        except:
            maintstr = ""
            if data[2]:
                maintstr = "(maintenance release={}/{}) ".format(data[2], data[3])
            raise ValueError(
                "There is no existing {} release {}for the {} module specified in the {} config file.".format(
                    data[0], maintstr, m, release_configuration_filename
                )
            )
    return lms


class AlreadyAModuleException(yam_exception.YamException):
    """Excepted raised if a specified module is already a work module."""


class MissingModuleException(yam_exception.YamException):
    """Exception raised if a specified module does not exist in the sandbox."""
