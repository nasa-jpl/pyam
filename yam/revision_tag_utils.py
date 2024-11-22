"""Contains functions for dealing with Yam revision tags."""

from __future__ import absolute_import

import re

from . import yam_exception


def incremented(revision_tag):
    """Return an incremented version of revision_tag.

    An example of a revision tag is "R1-04c".

    An exception will be raised if revision_tag is not a valid
    revision string.

    """

    def normalize(numbers):
        """Normalize the revision numbers."""
        if numbers[2] >= 27:
            new_numbers = (numbers[0], numbers[1] + 1, numbers[2] - 27)
        else:
            new_numbers = numbers

        if new_numbers[1] >= 100:
            return (new_numbers[0] + 1, new_numbers[1] - 100, new_numbers[2])
        else:
            return new_numbers

    numbers = split_revision_tag(revision_tag)
    numbers = (numbers[0], numbers[1], numbers[2] + 1)
    return join_revision_tag_numbers(*normalize(numbers))


def join_revision_tag_numbers(major_number, minor_number, extension_number):
    """Return the string form of a revision tag tuple.

    Take a revision tag of the form [1, 4, 3] and return the string form
    "R1-04c".

    """
    if extension_number > 0:
        extension = chr(extension_number + 96)
    else:
        extension = ""
    return "R{major}-{minor}{extension}".format(
        major=major_number,
        minor=str(minor_number).zfill(2),
        extension=extension,
    )


def check_legal_branch_id(branch_id):
    """
    Throw an exception if the specified branch name is illegal.
    """
    if branch_id.find("-") >= 0:
        raise ValueError("The '{br}' branch name has the '-' illegal character in it. ".format(br=branch_id))


def repotag_to_release_branch(repotag):
    """
    Split a <module>-Rx-xxx-<branch> repo tag into (module, release_tag,
    branch_id) tuple.

    Thus Darts-R1-23c-blah becomes (Darts, 'R1-23c', 'blah')
            Darts-R1-23c becomes (Darts, 'R1-23c', None)

    """
    # look for the first occurence of "-R" in the tag and use it to
    # extract the module name (this allows for handling module names
    # with '-' character (eg. dev-utils)
    moduleend = repotag.find("-R")
    module = repotag[:moduleend]

    # get the rest of the tag without the module name
    relpart = repotag[moduleend + 1 :]
    # fields = repotag.split("-")
    fields = relpart.split("-")
    n = len(fields)
    assert n >= 2
    # module = fields[0]
    release_tag = f"{fields[0]}-{fields[1]}"
    branch_id = None
    if n > 2:
        branch_id = "-".join(fields[2:])
    return (module, release_tag, branch_id)


def branch_to_maintenance_tuple(branch_id):
    """Return maintenance branch value as a tuple.

    For example,

    'Orion-MaintenanceM05'   to     ('Orion', '05')

    'Orion-Maintenance'   to     ('Orion', None)

    'myuser'     to     (None, None)

    """
    if branch_id.find("Maintenance") >= 0:
        fields = branch_id.replace("Maintenance", "").split("-")
        ## print('fields=', fields)
        if len(fields) == 2:
            fields[1] = fields[1].replace("M", "")
            return fields
        elif len(fields) == 1:
            return (fields[0], None)
        else:
            raise ValueError(
                "Line '{line}' is malformed as it should contain a revision tag "
                "optionally followed by a build ID or a maintenance release tag".format(line=branch_id)
            )
    else:
        return (None, None)


def split_revision_tag(revision_tag):
    """Return a split revision_tag in the form of a tuple. Get rid of this
    and instead use split_tag().

    Given a tag "R1-04c", we will return (1, 4, 3).

    """
    major_and_minor = revision_tag.strip().split("-")
    try:
        if len(major_and_minor) != 2:
            raise yam_exception.YamException(
                "'{tag}' is not a valid revision tag; " 'It does not have a "-" character'.format(tag=revision_tag)
            )

        if not major_and_minor[0].startswith("R"):
            raise yam_exception.YamException(
                "'{tag}' is not a valid revision tag; " 'it does not start with an "R"'.format(tag=revision_tag)
            )

        major = int(major_and_minor[0][1:])

        if re.match(".*[a-z]$", major_and_minor[1]):
            minor = int(major_and_minor[1][:-1])
            extension = ord(major_and_minor[1][-1]) - 96
        else:
            minor = int(major_and_minor[1])
            extension = 0
    except ValueError:
        raise yam_exception.YamException("'{tag}' is not a valid revision tag.".format(tag=revision_tag))

    return (major, minor, extension)


def split_tag(tag):
    """Return split of tag string into [release, build, mant_br, main_id]

    For example,

       'R1-01s-Build01' is split into
                             ('R1-01s', '01', None, None)

    For maintenance release link modules:

      'R1-01s-Mars2020-MaintenanceM00' is split into
                        ('R1-01s', '', Mars2020, '00')

      'R1-01s-Mars2020-Maintenance' is split into
                        ('R1-01s', '', Mars2020, '')

    Can raise an InternalMalformedLineException.

    """
    rest_noname = tag
    # print('rest_noname=', rest_noname)
    if rest_noname.find("-Build") >= 0:
        tag_and_build = rest_noname.split("-Build")
        if not 1 <= len(tag_and_build) <= 2:
            raise InternalMalformedLineException(
                "Line '{line}' is malformed as it should contain a revision tag "
                "optionally followed by a build ID".format(line=tag)
            )
        if tag_and_build[1] == "":
            tag_and_build[1] = None
        return tag_and_build + [None, None]
    elif rest_noname.find("-Maintenance") >= 0:
        fields = rest_noname.replace("Maintenance", "").split("-")
        # print('fields=', fields)
        if len(fields) > 3:
            fields[3] = fields[3].replace("M", "")
            return [
                fields[0] + "-" + fields[1],
                None,
                fields[2],
                fields[3],
            ]
        elif len(fields) > 2:
            return [
                fields[0] + "-" + fields[1],
                None,
                fields[2],
                None,
            ]
        elif len(fields) > 1:
            return [
                fields[0] + "-" + fields[1],
                None,
                None,
                None,
            ]
        else:
            raise InternalMalformedLineException(
                "Line '{line}' is malformed as it should contain a revision tag "
                "optionally followed by a build ID or a maintenance release tag".format(line=tag)
            )
    else:
        return [rest_noname, None, None, None]


def link_expression_to_name(line):
    """Return link module expression stripped to its name.

    For example,

    'Dtest/Dtest-R1-01s-Build01'

    or

    'Dtest/Dtest-R1-01s'

    to

    'Dtest'

    """
    return split_link_line(line)[0]


def split_link_line(line):
    """Return split link module.

    For example,

       'Dtest/Dtest-R1-01s-Build01' is split into
                             ('Dtest', 'R1-01s', '01', None, None)

    For maintenance release link modules:

      'Dtest++/Dtest-R1-01s-Mars2020-MaintenanceM00' is split into
                        ('Dtest', 'R1-01s', '', Mars2020, '00')

      'Dshell++/Dshell++-R1-01s-Mars2020-Maintenance' is split into
                        ('Dtest', 'R1-01s', '', Mars2020, '')

    Can raise an InternalMalformedLineException.

    """
    split_line = line.split("/")
    if len(split_line) != 2:
        raise InternalMalformedLineException(
            "Line '{line}' is malformed as it should contain exactly one slash".format(line=line)
        )
    module_name = split_line[0]
    rest = split_line[1]

    if not rest.startswith(module_name + "-"):
        raise InternalMalformedLineException("Line '{line}' is malformed".format(line=line))

    rest_noname = rest.replace(module_name + "-", "")
    return [module_name] + split_tag(rest_noname)


def link_expression_to_tuple(line):
    """Return link module expression split into a tuple. Should get rid of
    this function and instead use split_link_line.

    For example,

    'Dtest/Dtest-R1-01s-Build01'   to     ('R1-01s', '01', None, None)

    'Dtest/Dtest-R1-01s'     to     ('R1-01s', None, None, None)

    'Dtest/Dtest-R1-01s-ProjA-Maintenance'     to     ('R1-01s', '', 'ProjA', None)

    'Dtest/Dtest-R1-01s-ProjA-MaintenanceM05'     to     ('R1-01s', '', 'ProjA', '05')

    """
    result = split_link_line(line)
    # print("MMM", line, result)
    assert len(result) == 5
    user = None
    return make_linkmodule_description_tuple(result[1], user, result[2], result[3], result[4])


def tuple_to_release_tag_suffix(tag, use_build):
    """Combine the link module data to return the suffix for the directory
       name in the release area

    For example,

    ('R1-01s', '01', None, None)    to 'R1-01s'  or 'R1-10s-Build01'

    ('R1-01s', '', None, None)      to 'R1-01s'

    ('R1-01s', '', 'ProjA', None)   to  'R1-01s-ProjA-Maintenance'

    ('R1-01s', '', 'ProjA', '05')   to  'R1-01s-ProjA-MaintenanceM05'

    """
    assert not (tag[1] and tag[2])

    if use_build and tag[1]:
        return tag[0] + "-Build{}".format(tag[1])
    else:
        return tuple_to_maintenace_tag_suffix(tag)


def tuple_to_maintenace_tag_suffix(tag):
    """Combine the link module data to return the maintenance release suffix for the directory
       name in the release area

    For example,

    ('R1-01s', '01', None, None)    to ''

    ('R1-01s', '', None, None)      to ''

    ('R1-01s', '', 'ProjA', None)   to  '-ProjA-Maintenance'

    ('R1-01s', '', 'ProjA', '05')   to  '-ProjA-MaintenanceM05'

    """
    if tag[3]:
        # pointing to a maintenance release
        return "{}-{}-MaintenanceM{}".format(tag[0], tag[2], tag[3])
    elif tag[2]:
        # pointing to a maintenance branch
        return "{}-{}-Maintenance".format(tag[0], tag[2])
    else:
        return tag[0]


def make_workmodule_description_tuple(tag, branch, build):
    """Return the tuple describing the work module."""
    return (tag, branch)


def make_linkmodule_description_tuple(tag, user, build, maint_name, maint_tag):
    """Return the tuple describing the link module."""
    return (tag, build, maint_name, maint_tag)


class InternalMalformedLineException(Exception):
    """Exception when line is malformed."""
