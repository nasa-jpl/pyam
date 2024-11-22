"""Contains ConcreteConfigurationWriter class."""

from __future__ import absolute_import

from . import configuration_writer
from . import revision_tag_utils
from . import yam_exception
from . import yam_log


@yam_log.function_logger("Writing sandbox config filename," + "work_module_dict," + "link_module_dict,default_branch")
def write_sandbox_configuration(
    configuration_filename,
    work_module_dictionary,
    link_module_dictionary,
    default_branch,
):
    """Write sandbox configuration file.

    configuration_filename can be '<STDOUT>' to write to standard output

    The configuration is based on work_module_dictionary and
    link_module_dictionary.

    work_module_dictionary is of both of the form

    {'module_name': ('tag', 'branch_id')
     ...
    }

    where 'tag' is something like 'R1-01s' or None. And 'branch_id' is
    something like 'my_branch_id' or None.

    link_module_dictionary is of the form

    {'module_name': ('tag', 'build_id')
     ...
    }

    where 'build_id' may be something like '23' or None.

    """
    sections = [_header]

    sections.append(("WORK_MODULES = " + " \\\n               ".join(sorted(work_module_dictionary))).rstrip())

    sections.append(
        (
            "LINK_MODULES = "
            + " \\\n               ".join(
                [generate_link_module_line(module, link_module_dictionary) for module in sorted(link_module_dictionary)]
            )
        ).rstrip()
    )

    all_module_names = list(work_module_dictionary) + list(link_module_dictionary)
    if all_module_names:
        padding_length = max(len(name) for name in all_module_names)

        # BRANCH lines
        sections.append(
            "\n".join(
                [
                    generate_work_module_line(
                        module,
                        work_module_dictionary,
                        padding_length=padding_length,
                    )
                    for module in sorted(work_module_dictionary)
                ]
            )
        )

        # Commented out BRANCH lines. Unnecessary, but helpful to the
        # user.
        commented_out_modules = {
            module: (branch_and_build[0], default_branch) for module, branch_and_build in link_module_dictionary.items()
        }

        sections.append(
            "\n".join(
                [
                    generate_work_module_line(
                        module,
                        commented_out_modules,
                        "# ",
                        padding_length=padding_length,
                    )
                    for module in sorted(commented_out_modules)
                ]
            )
        )

    sections.append(_footer)

    if configuration_filename == "<STDOUT>":
        import sys

        sys.stdout.write("\n\n".join(sections))
    else:
        try:
            with open(configuration_filename, "w") as config_file:
                config_file.write("\n\n".join(sections))
        except IOError as exception:
            raise yam_exception.YamException(str(exception))


class ConcreteConfigurationWriter(configuration_writer.ConfigurationWriter):
    """A concrete implementation of the ConfigurationWriter interface."""

    def write_sandbox_configuration(
        self,
        configuration_filename,
        work_module_dictionary,
        link_module_dictionary,
        default_branch,
    ):
        """A concrete implementation of writeConfigurationForPackage().

        configuration_filename can be '<STDOUT>' to write to standard output
        """
        write_sandbox_configuration(
            configuration_filename=configuration_filename,
            work_module_dictionary=work_module_dictionary,
            link_module_dictionary=link_module_dictionary,
            default_branch=default_branch,
        )


def generate_work_module_line(module_name, work_module_dictionary, prefix="", padding_length=0):
    """Generate work module line.

    Return string of the form,

    BRANCH_MyModule = MyModule-tag branch_id

    or

    BRANCH_MyModule = MyModule-tag

    or

    BRANCH_MyModule = main

    """
    left = "{prefix}BRANCH_{module}".format(prefix=prefix, module=module_name)

    tag = work_module_dictionary[module_name][0]
    branch_id = work_module_dictionary[module_name][1]

    if tag:
        # Align the right hand side ("R0-00" versus "R0-00a").
        if tag[-1].isdigit():
            tag += " "

        middle = "= {module}-{tag}".format(module=module_name, tag=tag)
    else:
        middle = "= main"

    if branch_id:
        right = branch_id
    else:
        right = ""

    left_padding_length = len(left) - len(module_name) + padding_length
    middle_padding_length = len(middle) - len(module_name) + padding_length

    return " ".join(
        [
            left.ljust(left_padding_length),
            middle.ljust(middle_padding_length),
            right,
        ]
    ).strip()


def generate_link_module_line(module_name, link_module_dictionary):
    """Generate link module line.

    Return string of the form,.

    <module>/<module>-<tag>-Build<build_id>

    or

    <module>/<module>-<tag>

    or

    <module>/<module>-<tag>-ProjectA-MaintenanceM15

    """
    from . import concrete_configuration_reader

    # tag = link_module_dictionary[module_name][0]
    # print('XXX', module_name, link_module_dictionary[module_name])
    tag = revision_tag_utils.tuple_to_release_tag_suffix(tag=link_module_dictionary[module_name], use_build=True)
    line = "{module}/{module}-{tag}".format(module=module_name, tag=tag)
    """
    build_id = link_module_dictionary[module_name][1]
    if build_id:
        return line + '-Build' + build_id
    else:
        return line
    """
    return line


_header = """#
# YAM.config - configuration file for yam utilities and makefiles
#
# Edit this file to suit your needs. Lines that end with backslash get spliced
# together.
#"""

_footer = """#
# Below is a list of variables that can be set:
#
# WORK_MODULES - pyam modules to checkout from repository for
#                editing/compilation.
# LINK_MODULES - pyam modules to link to.
# BRANCH_workmod - Specify tag and branch tag to use for checking out
#                  work module "workmod" and possibly branching from it.
#
# Each entry in WORK_MODULES must have a corresponding variable specifying
# repository branch options. These variables are named BRANCH_workmod, where
# "workmod" is the name of the desired work module (such as BRANCH_MyModule).
#
# The BRANCH_module variables is set to:
#
#     <revision_tag> <branch_id>
#
# <revision_tag> is the tag for the version you want to branch off of, and
# hyphen-<branch_id> is appended to the tag for the branch you want to
# create. For example,
#
#     BRANCH_MyModule = MyModule-R1-05 my_branch
#
# makes branch "MyModule-R1-05-my_branch" off of tagged version
# "MyModule-R1-05" for work module MyModule.
#
# If <branch_id> is not specified, then just checkout version <revision_tag>,
# without creating a branch from it.
#
# There is a special <revision_tag> "main" which specifies repository's current
# main branch. For example,
#
#     BRANCH_MyModule = main
#
# You cannot branch off of "main" and it is almost always best to not work
# directly on the main branch. But it sometimes necessary in extreme cases
# of merge conflict.
#
# It is an error if <revision_tag> does not exist. Use <branch_id> to create a
# new branch.
#
# If BRANCH_module is not specified at all for a given work module, the default
# action is to branch off the latest release appending hyphen-login for the
# branch name. So if the latest version of MyModule is "MyModule-R1-05", then
# branch tag might default to "MyModule-R1-05-my_branch".
"""
