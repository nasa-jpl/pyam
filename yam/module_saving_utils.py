"""Utility function that are used when saving a module."""

# TODO: Rename this module to "module_utils".

from __future__ import absolute_import

import os
import re
import textwrap


from git import Repo
import shutil

from . import savable_module
from . import saving_utils
from . import work_module
from . import revision_control_system as rcs


def ansi(code):
    """Return escaped color code."""
    return "\x1b[" + code


def update_yam_version_file(
    module_name,
    new_revision_tag,
    module_path,
    file_system,
    revision_control_system,
):
    """ "Update the "YamVersion.h" file with the new revision tag.

    Set revision_control_system to None to not commit changes.

    """
    filename = os.path.join(module_path, "YamVersion.h")

    if not file_system.path_exists(filename):
        return

    file_system.write_to_file(
        string_data="""/**
 * YamVersion.h
 *
 * Header file that uses Dversion.h to provide functions to access
 * version information for a module
 */

/* make sure DVERSION macros are not already defined */
#ifdef DVERSION_CPREFIX
#undef DVERSION_CPREFIX
#endif
#ifdef DVERSION_MODULE
#undef DVERSION_MODULE
#endif
#ifdef DVERSION_RELEASE
#undef DVERSION_RELEASE
#endif

/* declare module-specific RELEASE macro for use by other modules */
#define {upper_module_name}_DVERSION_RELEASE "{module_name}-{revision_tag}"

/* define DVERSION macros and include Dversion.h to declare functions */
#define DVERSION_CPREFIX {module_name}
#define DVERSION_MODULE "{module_name}"
#define DVERSION_RELEASE {upper_module_name}_DVERSION_RELEASE
#include "Dversion.h"
""".format(
            module_name=module_name,
            upper_module_name=module_name.upper(),
            revision_tag=new_revision_tag,
        ),
        filename=filename,
    )

    revision_control_system.check_in(
        path=filename, log_message=f"pyam: Update {new_revision_tag} revision tag", wmpath=module_path
    )


def update_change_log(change_log_entry, file_system, module_path, revision_control_system):
    """Prepend an entry into the ChangeLog and commit it.

    Return the change log entry text.

    Set revision_control_system to None to not commit changes.

    """
    # Update the "ReleaseNotes" file
    filename = os.path.join(module_path, "ChangeLog")

    if not file_system.path_exists(filename):
        return

    old_change_log_data = file_system.read_file(filename=filename)

    file_system.write_to_file(string_data=(change_log_entry + old_change_log_data), filename=filename)

    # print('KKKKKKKKK3.5', os.system(f'git -P -C {module_path} status'))
    revision_control_system.check_in(path=filename, log_message="pyam: Add a change log entry", wmpath=module_path)
    # print('KKKKKKKKK4', os.system(f'git -P -C {module_path} status'))


def generate_change_log_entry(bug_id, new_revision_tag, date_time, username, revision_control_log):
    """Return a ChangeLog entry."""
    # We are using ctime format to make old yam happy
    #    return f"{new_revision_tag} {date_time.ctime()} PLACEHOLDER CHANGELOG\n"

    entry = """{date}  {user}

\t* Revision tag: {tag}{bug_string}

{log}""".format(
        date=date_time.ctime(),
        user=username,
        tag=new_revision_tag,
        bug_string="\n\tTicket IDs: {bug_id}".format(bug_id=bug_id) if bug_id else "",
        log=saving_utils.indent(revision_control_log, "\t"),
    )

    return entry.strip() + "\n\n"


def move_module_for_release(
    module_path,
    module_name,
    new_revision_tag,
    build_id,
    changelogs_path,
    release_directory,
    keep_release,
    latest_link,
    file_system,
    build_system,
    database_writer,
    progress_callback,  # ,tse
    database_reader=None,
    revision_control_system=None,
):
    """Move to release directory, set permissions, and update "Latest" symlink.

    Module will be moved to
        "<release_directory>/Module-Releases/<module_name>/<module_name>-<tag>"

    suffixed with "-Build<build_id>" if build_id is not None.

    """
    import os.path

    # assert os.path.isdir(module_path)
    # Fill in API dependencies before moving the module.
    database_writer.write_build_dependencies(
        module_name=module_name,
        dependency_dictionary=build_system.build_dependencies(
            module_path=module_path, release_directory=release_directory
        ),
    )

    # assert os.path.isdir(module_path)
    if not release_directory:
        # no release directory has been specified, so simply rename the
        # saved module and keep in the local sandbox
        import time

        module_path_new = module_path + time.strftime("__%Y_%m_%d__%H_%M_%S")

        red = ansi("1;31m")
        end = ansi("0m")
        print(
            red
            + "WARNING!!! Couldn't move released directory because no release area is defined\n"
            + "Renaming '{}' to '{}' instead".format(module_path, module_path_new)
            + end
        )

        os.rename(module_path, module_path_new)
        return ""
    elif not keep_release:
        # saving the module to the release directory has been disabled, so simply rename the
        # saved module and keep in the local sandbox
        import time

        module_path_new = module_path + time.strftime("__%Y_%m_%d__%H_%M_%S")

        red = ansi("1;31m")
        end = ansi("0m")
        print(
            red
            + "WARNING!!! Move to release directory has been disabled."
            + "Renaming '{}' to '{}' instead".format(module_path, module_path_new)
            + end
        )

        os.rename(module_path, module_path_new)
        return ""

    assert os.path.isdir(module_path)
    destination_path, directory_name = module_release_path(
        release_directory=release_directory,
        module_name=module_name,
        revision_tag=new_revision_tag,
        build_id=build_id,
    )

    # assert os.path.isdir(module_path)
    # when using git, we check_out (clone) rather than move a folder
    # print('PPPP', module_path, destination_path, database_reader.vcs_type(module_name) )
    if False and database_reader and database_reader.vcs_type(module_name) == "git":

        # THIS NEEDS TO BE FIXED - will not work for releases beyond the
        # initial one. Need to check out the module for the initial
        # release externally and move here like for svn
        # assert os.path.isdir(module_path)
        ###revision_control_system._check_out(module_path, destination_path)

        vcs_root = database_reader.module_repository_url(module_name)
        module_branch_data = rcs.ModuleBranchData(
            module_name=module_name, release_tag="R1-00", branch_id=None, vcs_type="git", vcs_root=vcs_root
        )
        # revision_control_system._check_out(source=module_branch_data,
        revision_control_system.module_check_out(source=module_branch_data, target=destination_path)
        # assert os.path.isdir(module_path)

    # construct the destination of the released module
    else:

        progress_callback("Moving module to release area '{dest}'".format(dest=destination_path))

        # assert os.path.isdir(module_path)
        # print("JJJJ")
        # print(module_path)
        # print(destination_path)
        file_system.move(source_path=module_path, destination_path=destination_path)

        # if in a git repo, delete the .git because snapshots don't need histories.
        # git_folder = os.path.join(destination_path,".git")
        # if os.path.isdir(git_folder):
        #    shutil.rmtree(git_folder)
        # assert os.path.isdir(module_path)

    # assert os.path.isdir(module_path)
    file_system.make_read_only_recursively(destination_path)

    # Update the "Latest" symlink.
    if latest_link:
        latest_link_path = os.path.join(release_directory, "Module-Releases", module_name, "Latest")

        # This should be relative to the 'Latest' link.
        file_system.symbolic_link(
            source=os.path.basename(destination_path),
            link_name=latest_link_path,
            progress_callback=progress_callback,
        )

    # set up links for the ChangeLog and ReleaseNotes files for access
    # from the releases page
    if release_directory and changelogs_path:
        create_changelogs_link(directory_name, changelogs_path, destination_path, progress_callback)

    return destination_path


def module_release_path(release_directory, module_name, build_id, revision_tag):
    """Return path to module release directory."""
    if build_id:
        directory_name = "{m}-{tag}-Build{build}".format(m=module_name, tag=revision_tag, build=build_id)
    else:
        directory_name = "{m}-{tag}".format(m=module_name, tag=revision_tag)

    return os.path.join(release_directory, "Module-Releases", module_name, directory_name), directory_name


def release_module(
    module_name,
    module_path,
    new_revision_tag,
    new_release_tag,
    original_branch_data,  # original_branch_url,
    database_reader,
    database_writer,
    file_system,
    revision_control_system,
    build_system,
    diff_lines,
    modified_paths,
    changelogs_path,
    username,
    date_time,
    operating_system_name,
    site_name,
    host_ip,
    release_directory,
    keep_release,
    latest_link,
    progress_callback,
    maintenance_name,
    maintenance_num,
):
    """Release the module.

    This involves creating the new release branch, updating the
    database, and moving the module to the release area.

    """
    progress_callback("Populating database with build dependencies")

    # Fill in API dependencies before moving the module.
    database_writer.write_build_dependencies(
        module_name=module_name,
        dependency_dictionary=build_system.build_dependencies(
            module_path=module_path, release_directory=release_directory
        ),
    )

    # This is the new release URL, which has the incremented revision tag.
    new_release_data = original_branch_data.with_release_tag(new_revision_tag, None)
    """
    new_release_url = work_module.releases_url(
        module_name=module_name,
        revision_tag=new_revision_tag,
        database_reader=database_reader,
    )
    """

    ### print("BBBB making branch", original_branch_url, new_release_url)
    # Create branch in release repository.
    # if revision_control_system.vcs != "git":
    # print('NNN', original_branch_data.uri(), new_release_data.uri())
    if revision_control_system.vcs == "git":
        progress_callback("Creating release tag")
        revision_control_system.tag(new_release_data, path=module_path)
    else:
        progress_callback("Creating release branch")
        revision_control_system.branch(source_url=original_branch_data, destination_url=new_release_data)

    progress_callback("Updating database")

    # Generate statistics.
    num_files_changed = (
        len([l for l in diff_lines if l.startswith("=")])
        -
        # Ignore binary files.
        len([l for l in diff_lines if l.startswith("Cannot display:")])
    )

    num_lines_added = len([l for l in diff_lines if l.startswith("+") and not l.startswith("+++")])
    num_lines_removed = len([l for l in diff_lines if l.startswith("-") and not l.startswith("---")])

    readmes = module_readmes(module_path)

    # Write release information to the database.
    ##print('maintenance_name1=', maintenance_name, 'maintenance_num1=', maintenance_num)
    # TODO: release info will probably be different for git modules. For example, release_path
    # shouldn't be a new path, its the same git repo.
    database_writer.write_module_source_release_information(
        module_name=module_name,
        revision_tag=new_release_tag,  # new_revision_tag,
        username=username,
        date_time=date_time,
        changed_api_filename_list=[os.path.split(p)[1] for p in modified_paths if is_header_file(p)],
        readmes=readmes,
        num_files_changed=num_files_changed,
        num_lines_added=num_lines_added,
        num_lines_removed=num_lines_removed,
        operating_system_name=operating_system_name,
        site_name=site_name,
        host_ip=host_ip,
        release_path=release_directory,
        maintenance_name=maintenance_name,
        maintenance_num=maintenance_num,
    )

    if not revision_control_system.isMainTrunkCheckout(module_path):
        revision_control_system.markBranchDead(wmpath=module_path)

    # Switch working directory to release branch
    if 1 or revision_control_system.vcs != "git":
        # if 1:
        if revision_control_system.vcs == "git":
            from git import Repo

            git = Repo(module_path).git
            branches = git.branch()
            if new_release_data.repoReleaseTag() not in branches:
                # we get here if working with remote repositories all the
                # time instead of working directories. We need to create the
                # release tag branch for this case
                revision_control_system.switch_to_branch(
                    path=module_path, branch_url=new_release_data
                )  # new_release_url
            else:
                # we get here if using repos for working directories. The
                # release tag branch already exists in the local working
                # directory and We need to push the existing tagged version
                # to the remote repos g
                git.push("--set-upstream", "origin", new_release_data.repoReleaseTag())  # new_release_url
        else:
            # svn
            revision_control_system.switch_to_branch(path=module_path, branch_url=new_release_data)  # new_release_url

            # pass
    if 0 and revision_control_system.vcs == "git":
        revision_control_system.tag_git_module(module_name, new_revision_tag)
        # print("LLLL")
        # print(module_path)
        # tag the sandbox as well, so that when we move the sandbox to the releases dir,
        # the tag is in the release folder as well
        revision_control_system.tag_git_module(module_name, new_revision_tag, repo=Repo(module_path))

    # Move file system directory to release area.
    destination_path = move_module_for_release(
        module_path=module_path,
        module_name=module_name,
        new_revision_tag=new_revision_tag,
        build_id=None,
        changelogs_path=changelogs_path,
        release_directory=release_directory,
        keep_release=keep_release,
        latest_link=latest_link,
        file_system=file_system,
        build_system=build_system,
        database_writer=database_writer,
        progress_callback=progress_callback,
    )

    # create links for ChangeLog etc files
    # print("LLLL", changelogs_path)
    """
    if release_directory and changelogs_path:
        create_changelogs_link(directory_name,
                               changelogs_path,
                               destination_path)
        for f in ["ChangeLog", "ReleaseNotes"]:
            # print('TTTT', destination_path + '/' + f)
            if os.path.exists(destination_path + "/" + f):
                progress_callback(
                    "Creating symbolic links for {} file".format(f)
                )
                dest_link = "module-{m}-{r}-{f}".format(
                    m=module_name, r=new_revision_tag, f=f
                )
                os.symlink(
                    destination_path + "/" + f,
                    changelogs_path + "/" + dest_link,
                )
    """


def module_readmes(module_path):
    """
    Return the available ChangeLog etc files in the module release.
    """
    # get list of key informational files in the module
    all_readmes = [
        "ChangeLog",
        "BugFixes",
        "FeaturesLog",
        "README",
        "Readme",
        "ReleaseNotes",
    ]
    readmes = [f for f in all_readmes if os.path.exists(module_path + "/" + f)]
    return readmes


def create_changelogs_link(directory_name, changelogs_path, destination_path, progress_callback):
    """
    Create symbolic links for ChangeLog etc files for use from the
    releases page.
    """
    for f in ["ChangeLog", "ReleaseNotes"]:
        # print('TTTT', destination_path + '/' + f)
        if os.path.exists(destination_path + "/" + f):
            progress_callback("Creating symbolic links for {} file".format(f))
            # dest_link = "module-{m}-{r}-{f}".format(
            #    m=module_name, r=new_revision_tag, f=f
            # )
            dest_link = "module-{d}-{f}".format(d=directory_name, f=f)
            if os.path.exists(changelogs_path + "/" + dest_link):
                os.remove(changelogs_path + "/" + dest_link)
            os.symlink(
                destination_path + "/" + f,
                changelogs_path + "/" + dest_link,
            )


def is_header_file(filename):
    """Return True if "filename" is a header file."""
    for extension in [".h", ".hpp", ".hh"]:
        if filename.lower().endswith(extension):
            return True

    return False


def basic_module_check(module_path, expected_url: rcs.ModuleBranchData, revision_control):
    """Raise exception if module does not match the specified parameters."""
    # Do an update before doing any checks
    # print("YYYY")
    # print(expected_url)
    # print(module_path)

    revision_control.update(path=expected_url)  # module_path)

    # Make sure we have the expected repository URL.
    # actual_url = revision_control.url(path=module_path)
    # actual_url = revision_control.url(path=module_path)

    # if actual_url != expected_url.uri():
    # if actual_url != revision_control.uri(expected_url):
    # print("VVVV")
    # print(module_path)
    # print(expected_url)
    # print('KKKKK5', module_path)
    # os.system(f'ls {module_path}')
    if not revision_control.isConsistent(path=module_path, expected_data=expected_url):
        raise savable_module.RepositoryURLMismatchError(
            expected_url=expected_url.dumpStr(), actual_url=revision_control.url(path=module_path)  # actual_url
        )


def pre_save_check(file_system, release_directory):
    """Check before releasing module.

    Raise a PreSaveException if check fails.

    """
    # TODO: Add additional safety checks.
    #       1. Make sure destination in the release directory that we are
    #          moving our module to doesn't exist yet on file system.
    #       2. Make sure our module doesn't exist in the repository release
    #          directory yet.

    # Make sure release directory exists
    if release_directory and not file_system.path_exists(release_directory):
        raise savable_module.PreSaveException("Release directory '{d}' does not exist".format(d=release_directory))


def generate_build_id(module_name, database_reader, desired_build_id):
    """Return new build ID."""
    tmp_build_id = database_reader.latest_module_information(module_name=module_name, release=None)["build"]
    try:
        tmp_build_num = int(tmp_build_id)
    except (TypeError, ValueError):
        tmp_build_num = 0

    try:
        new_build_num = int(desired_build_id)
    except (TypeError, ValueError):
        new_build_num = tmp_build_num + 1

    return str(new_build_num).zfill(2)


def module_history(module_names, limit, before, after, ascending, database_reader):
    """Return latest module information.

    Return a dictionary containing information about the latest module with
    the given name.

    The dictionary contains 'branch', 'build', 'datetime', 'missing', and
    'tag'.

    """
    result = database_reader.module_history(
        module_names=module_names,
        limit=limit,
        before=before,
        after=after,
        ascending=ascending,
    )[:]
    return result


def latest_module_information(module_name, release, release_directory, database_reader, file_system):
    """
    Return latest module information for a specific release. If release
    is None, then for the latest release.

    Return a dictionary containing information about the latest module with
    the given name.

    The dictionary contains 'branch', 'build', 'datetime', 'missing', and
    'tag'.

    If the 'missing' field is False, then the module is available in the
    release area for use as a link module
    """
    # print('RRR', module_name, release)
    # get the latest release information from the database
    result = database_reader.latest_module_information(module_name=module_name, release=release).copy()
    result["missing"] = False

    # return false if there is no release area
    """
    if not release_directory:
        result["missing"] = True
        return result
    """

    # print('RESULT=', module_name, result)
    if release_directory:
        # get the latest release information from the filesystem if the
        # latest release is a build release
        if result["build"]:
            old_build_id = result["build"]

            # latest build release on the file system
            result["build"] = latest_build_id(
                module_name=module_name,
                tag=result["tag"],
                release_directory=release_directory,
                file_system=file_system,
            )
            # print('GGG', result['build'])

            if old_build_id != result["build"]:
                # raise an exception if the filesystem build id is
                # larger than the one in the database
                if result["build"] and int(old_build_id) < int(result["build"]):
                    raise ValueError(
                        "The latest build id for the {module} {tag} release in the database is {db} while that in the filesystem is {file}. Something is wrong.".format(
                            module=module_name,
                            db=old_build_id,
                            tag=result["tag"],
                            file=result["build"],
                        )
                    )
                # we have an older build release, not for the current release
                result["datetime"] = ""
                result["missing"] = True
                result["user"] = ""

        # report the link module as missing if not available in the release area
        if not file_system.path_exists(
            module_release_path(
                release_directory=release_directory,
                module_name=module_name,
                build_id=result["build"],
                revision_tag=result["tag"],
            )[0]
        ):
            result["missing"] = True

    # print('RESULT1=', module_name, result)
    return result


def link_module_availabilityOBSOLETE(module_name, release, release_directory, database_reader, file_system):
    """
    Return information for the latest build release link module for the
    specified module release include a 'missing' field indicating
    whether the build release is actually available in the release area
    for use.
    """
    # print('RRR', module_name, release)

    # print('RESULT=', module_name, result)

    # get the latest release information from the database
    result = database_reader.latest_module_information(module_name=module_name, release=release)

    # return false if there is no release area
    if not release_directory:
        result["missing"] = True
        return result

    result["missing"] = False
    # get the latest release information from the filesystem if the
    # latest release is a build release
    if result["build"]:
        old_build_id = result["build"]

        # latest build release on the file system
        result["build"] = latest_build_id(
            module_name=module_name,
            tag=result["tag"],
            release_directory=release_directory,
            file_system=file_system,
        )
        # print('GGG', result['build'])

        if old_build_id != result["build"]:
            # raise an exception if the filesystem build id is
            # larger than the one in the database
            if result["build"] and int(old_build_id) < int(result["build"]):
                raise ValueError(
                    "The latest build id for the {module} in the database is {db} while that in the filesystem is {file}. Something is wrong.".format(
                        module=module_name,
                        db=old_build_id,
                        file=result["build"],
                    )
                )
            # we have an older build release, not for the current release
            result["datetime"] = ""
            result["missing"] = True
            result["user"] = ""

    # report the link module as missing if not available in the release area
    if not file_system.path_exists(
        module_release_path(
            release_directory=release_directory,
            module_name=module_name,
            build_id=result["build"],
            revision_tag=result["tag"],
        )[0]
    ):
        result["missing"] = True

    return result


def _latest_build(module_release_names, build_prefix="Build"):
    """Return latest build based on natural sorting."""
    ids = []
    mapping = {}
    for name in module_release_names:
        split = re.split(build_prefix + "([0-9]+)$", name)
        try:
            string_value = split[-2]
            ids.append(int(string_value))
            mapping[ids[-1]] = string_value
        except (IndexError, ValueError):
            pass

    return mapping[max(ids)] if ids else None


def latest_build_id(module_name, tag, release_directory, file_system):
    """Return latest build on the file system."""
    raw_template, directory_name = module_release_path(
        release_directory=release_directory,
        module_name=module_name,
        build_id="*",
        revision_tag=tag,
    )

    assert raw_template.endswith("*")
    raw_template = raw_template[:-1]

    (root_path, raw_base) = os.path.split(raw_template)
    all_paths = file_system.list_directory(root_path)
    del raw_template

    pattern = re.escape(raw_base) + "[0-9]+"
    return _latest_build([path for path in all_paths if re.match(pattern, path)])


def unique_branch_id(
    module_name,
    revision_tag,
    revision_control_system,
    database_reader,
    default_branch,
    parent_directory,
    progress_callback,
):
    """Return a unique branch ID.

    This is a branch ID that has not been previously used for the given
    revision.
    """
    # return f"{default_branch}1"
    from . import revision_control_system as rcs

    vcs_type = database_reader.vcs_type(module_name)
    vcs_root = database_reader.module_repository_url(module_name)
    module_branch_data = rcs.ModuleBranchData(
        module_name=module_name,
        release_tag=revision_tag,
        branch_id=default_branch,
        vcs_type=vcs_type,
        vcs_root=vcs_root,
    )
    if vcs_type == "git":
        from git import Repo

        # This is going to become a work module eventually. Therefore, checkout
        # the module locally when searching for a branch, rather than checking out in temp and then doing another checkout locally later.
        module_directory = os.path.join(parent_directory, module_name)
        if revision_control_system.working_copy_exists(module_directory):
            revision_control_system.repo = Repo(module_directory)
        else:
            progress_callback(
                "Checking out source code for '{name}' module (main)".format(
                    name=module_name,
                )
            )

            revision_control_system.repo = Repo.clone_from(module_branch_data.repoPath(), module_directory)

    def already_used_branch(branch_id):
        br_mod_data = module_branch_data.with_branch_id(branch_id)
        return revision_control_system.exists_module_branch(
            br_mod_data
        ) or revision_control_system.exists_module_branch(br_mod_data.with_dead_branch())

    branch_id = default_branch
    count = 1

    while already_used_branch(branch_id):
        branch_id = "{prefix}{number}".format(prefix=default_branch, number=count)
        count += 1

    if vcs_type == "git":
        # If this is git, we've made a local copy, this better match what pyam has or else it's going to cause errors later.
        # Therefore, switch to the new branch now.
        module_directory = os.path.join(parent_directory, module_name)
        revision_control_system.switch_to_branch(module_directory, module_branch_data.with_branch_id(branch_id))

    return branch_id


def format_message(message):
    """Return formatted release note message.

    Wrap the message only if it is a single line. Trying to wrap more
    complex messages could result in breaking user-intended column
    alignment.

    """
    if not message:
        return message

    message = message.strip()
    if message and "\n" not in message:
        message = textwrap.fill(message, width=72, break_long_words=False).strip()
    return message
