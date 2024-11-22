"""Contains ConcreteConfigurationReader class."""

from __future__ import absolute_import
from __future__ import unicode_literals

from . import revision_tag_utils

try:
    from configparser import ConfigParser as SafeConfigParser
except ImportError:
    # Python 2.
    from ConfigParser import SafeConfigParser

try:
    from configparser import Error as ConfigParserError
except ImportError:
    # Python 2.
    from ConfigParser import Error as ConfigParserError

from . import configuration_reader


def read_work_module_information(configuration_filename, module_name):
    """
    Read information about work module from configuration file.

    configuration_filename can be '<STDIN>' to read from standard input

    Return a (tag, branch_id) tuple after reading it from the BRANCH_*
    line in the sandbox configuration file. The tag and branch_id are
    None for main trunk. For a tagged release, the branch is None.

    Raise a ConfigurationError if parsing goes wrong.
    """
    work_modules = read_sandbox_configuration(configuration_filename)["work_modules"]

    if module_name not in work_modules:
        raise configuration_reader.ConfigurationError(
            "Work module '{name}' not found".format(name=module_name),
            filename=configuration_filename,
        )

    return work_modules[module_name]


def read_package_information(package_configuration_filename, package_name):
    """Read package information from configuration file.

    configuration_filename can be '<STDIN>' to read from standard input

    Return the set of module names that are part of the package,
    according to the configuration file.

    Raise a ConfigurationError if parsing goes wrong.

    """
    items = _parse_configuration(
        configuration_filename=package_configuration_filename,
        expand_variables=True,
    )

    package_key = "MODULES_{package}".format(package=package_name)
    try:
        modules = {k: v for k, v in items}[package_key]
    except KeyError:
        raise configuration_reader.ConfigurationError(
            "Could not find package '{package_key}'".format(package_key=package_key),
            filename=package_configuration_filename,
        )
    return set(modules.split())


def read_sandbox_configuration(configuration_filename):
    """Read sandbox configuration file.

    Return a dictionary of two other dictionaries shown below.

    configuration_filename can be '<STDIN>' to read from standard input

    The 'work_modules' dictionary is defined below.

    {'module_name': ('tag', 'branch_id')
     ...
    }

    where 'tag' is something  like 'R1-01s' or None. And 'branch_id' is
    something like 'my_branch_id' or None.

    For regular branch -  ('R1-01s', my_branch_id)
    For tagged release -  ('R1-01s', '')
    For main trunk     -  (None, None)

    The 'link_modules' dictionary is defined below. Note that the second
    tuple is a build ID (for example, '03').

    {'module_name': ('tag', 'build_id', 'maint branch', 'maint num')
     ...
    }

    """

    def raise_branch_exception(name, configuration_filename):
        """Raise an exception regarding the branch information."""
        raise configuration_reader.ConfigurationError(
            message="Branch '{name}' is malformed".format(name=name),
            filename=configuration_filename,
        )

    work_modules = {}
    link_modules = {}

    wms = []
    for key, value in _parse_configuration(configuration_filename=configuration_filename, expand_variables=False):
        # print('YYY', key, value)
        if key == "LINK_MODULES":
            # Get link modules
            try:
                link_modules = {}
                for x in value.split():
                    nm = revision_tag_utils.link_expression_to_name(x)
                    if nm in link_modules:
                        raise DuplicateLinkModule("The '%s' link module has been specified more than once" % nm)
                    link_modules[nm] = revision_tag_utils.link_expression_to_tuple(x)

            except revision_tag_utils.InternalMalformedLineException as e:
                raise configuration_reader.ConfigurationError(message=str(e), filename=configuration_filename)
        elif key == "WORK_MODULES":
            # Get work modules
            wms = value.split()
            for w in wms:
                n = wms.count(w)
                if n > 1:
                    raise configuration_reader.ConfigurationError(
                        message='Found %d "%s" entries in WORK_MODULES' % (n, w),
                        filename=configuration_filename,
                    )
        elif key.find("BRANCH_") >= 0:
            import re

            name = re.findall(r"BRANCH_(.*)", key)
            if name:
                split_value = value.split()
                if len(split_value) == 1:
                    # no branch has been specified
                    if split_value[0] == "main":
                        # the value is 'main'
                        work_modules[name[0]] = revision_tag_utils.make_workmodule_description_tuple(None, None, None)
                    elif split_value[0].startswith(name[0] + "-"):
                        # tagged module release of form Ndarts-R3-23b
                        work_modules[name[0]] = revision_tag_utils.make_workmodule_description_tuple(
                            split_value[0].replace(name[0] + "-", "", 1),
                            "",
                            None,
                        )
                    else:
                        raise_branch_exception(
                            name=name[0],
                            configuration_filename=configuration_filename,
                        )
                elif len(split_value) == 2:
                    # we have a branch specified
                    if split_value[0].startswith(name[0] + "-"):
                        # extract the release tag R3-23b and the branch id
                        work_modules[name[0]] = revision_tag_utils.make_workmodule_description_tuple(
                            split_value[0].replace(name[0] + "-", "", 1),
                            split_value[1],
                            None,
                        )
                    else:
                        raise_branch_exception(
                            name=name[0],
                            configuration_filename=configuration_filename,
                        )
                else:
                    raise_branch_exception(
                        name=name[0],
                        configuration_filename=configuration_filename,
                    )
        else:
            raise configuration_reader.ConfigurationError(
                message='Found unrecognized "%s" key with "%s" value' % (key, value),
                filename=configuration_filename,
            )

    # print("WMS=", wms)
    # print("WORK=", work_modules)
    diff1 = set(wms).difference(set(work_modules))
    if diff1:
        raise configuration_reader.ConfigurationError(
            message='BRANCH-* entries are missing for the "%s" work modules' % (list(diff1)),
            filename=configuration_filename,
        )

    diff1 = set(work_modules).difference(set(wms))
    if diff1:
        raise configuration_reader.ConfigurationError(
            message='There are BRANCH-* entries for the "%s" modules that are not listed in WORK_MODULES'
            % (list(diff1)),
            filename=configuration_filename,
        )

    diff1 = set(work_modules).intersection(set(link_modules))
    if diff1:
        raise configuration_reader.ConfigurationError(
            message='The "%s" modules are listed in both WORK_MODULES and LINK_MODULES' % (list(diff1)),
            filename=configuration_filename,
        )

    # print('BBBB')
    # from pprint import pprint
    # pprint({'work_modules': work_modules,
    #        'link_modules': link_modules})
    return {"work_modules": work_modules, "link_modules": link_modules}


class ConcreteConfigurationReader(configuration_reader.ConfigurationReader):
    """A concrete implementation of the ConfigurationReader interface."""

    def read_work_module_information(self, configuration_filename, module_name):
        """A concrete implementation of read_work_module_information()."""
        return read_work_module_information(configuration_filename, module_name)

    def read_package_information(self, package_configuration_filename, package_name):
        """A concrete implementation of writeConfigurationForPackage()."""
        return read_package_information(package_configuration_filename, package_name)

    def read_sandbox_configuration(self, configuration_filename):
        """Concrete implementation of read_sandbox_configuration()."""
        return read_sandbox_configuration(configuration_filename)


def _parse_configuration(configuration_filename, expand_variables):
    """Return the configuration in the form of a list of (key, value) tuples.

    configuration_filename can be '<STDIN>' to read from standard input
    If expand_variables is True, variables of the form
    "$(variable_name)" will be expanded.

    """
    if configuration_filename == "<STDIN>":
        import sys

        data = sys.stdin.read().replace("\\\n", "")
    else:
        try:
            with open(configuration_filename, "r") as config_file:
                # Read and remove escaped newlines
                data = config_file.read().replace("\\\n", "")
        except IOError:
            raise configuration_reader.ConfigurationError(
                "Could not read configuration file",
                filename=configuration_filename,
            )

    # Remove leading whitespace which causes problems with the parser.
    import re

    data = re.sub(r"\n\s+", "\n", data)

    # Replace "$(variable)" with "%(variable)s" so that ConfigParser
    # can do the expansion of variables.
    if expand_variables:

        def replace_variable(match_object):
            """Take "$(variable)" and input and return "%(variable)s"."""
            # group(1) is the first parenthesized group (while group(0) is the
            # entire match).
            return "%(" + match_object.group(1) + ")s"

        data = re.sub(r"\$\(([^)]*)\)", replace_variable, data)

    config_parser = SafeConfigParser()

    # Make it case-sensitive.
    config_parser.optionxform = str

    import io

    try:
        # Read in the configuration file and specify that all the text is
        # part of the "Defaults" section.
        fake_file = io.StringIO("[Defaults]\n" + data)
        config_parser.read_file(fake_file)
        return config_parser.items("Defaults", raw=not expand_variables)
    except ConfigParserError as error:
        raise configuration_reader.ConfigurationError(
            message=error.message.rstrip("."), filename=configuration_filename
        )


class DuplicateLinkModule(Exception):
    """Exception when there are multiple link modules defined."""
