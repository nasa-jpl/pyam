"""Contains ConfigurationReader interface."""

from __future__ import absolute_import

import abc

from . import yam_exception


class ConfigurationReader(object):
    """An interface for parsing YAM.config files.

    This interface exists so that we can test classes that depend on it
    without actually reading real files. We do this via mocking.

    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def read_work_module_information(self, configuration_filename, module_name):
        r"""Read information about work module from configuration file.

        Return a (tag, branch_id) tuple after reading it from the BRANCH_* line
        in the sandbox configuration file.

        Raise a ConfigurationError if parsing goes wrong.

        A configuration file is typically named "YAM.config". Below is a
        typical example.


        WORK_MODULES = pyam

        LINK_MODULES = DshellEnv/DshellEnv-R1-64c \
                       Dtest/Dtest-R1-01o \
                       SiteDefs/SiteDefs-R1-80h

        BRANCH_pyam =  pyam-R1-03a tag

        """

    @abc.abstractmethod
    def read_package_information(self, package_configuration_filename, package_name):
        r"""Read package information from configuration file.

        Return the set of module names that are part of the package,
        according to the configuration file.

        Raise a ConfigurationError if parsing goes wrong.

        An (input) package configuration would typically be called
        "YAM.modules".  An example of the input format can be seen below. As
        you will see, variables are supported in the form "$(variable)".


        core_modules = module_a module_b \
                       module_c

        MODULES_MyPkg = module_d $(core_modules)

        """

    @abc.abstractmethod
    def read_sandbox_configuration(self, configuration_filename):
        """Read sandbox configuration file.

        Return a dictionary of two other dictionaries shown below.

        {'work_modules': {...}
         'link_modules': {...}
        }

        The 'work_modules' dictionary is defined below.

        {'module_name': ('tag', 'branch_id')
         ...
        }

        where 'tag' is something like 'R1-01s' or None. And 'branch_id' is
        something like 'my_branch_id' or None.

        The 'link_modules' dictionary is defined below. Note that the second
        tuple is a build ID (for example, '03').

        {'module_name': ('tag', 'build_id', 'maintenance branch', 'maint id')
         ...
        }

        """


class ConfigurationError(yam_exception.YamException):
    """Exception returned when reading invalid sandbox configuration files."""

    def __init__(self, message, filename):
        yam_exception.YamException.__init__(self, message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return "{message} in file '{filename}'".format(message=self.message, filename=self.filename)
