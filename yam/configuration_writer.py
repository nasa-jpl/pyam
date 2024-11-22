"""Contains ConfigurationWriter interface."""

from __future__ import absolute_import

import abc


class ConfigurationWriter(object):
    """An interface for generating YAM.config files.

    This interface exists so that we can test classes that depend on it
    without actually writing real files. We do this via mocking.

    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write_sandbox_configuration(
        self,
        configuration_filename,
        work_module_dictionary,
        link_module_dictionary,
        default_branch,
    ):
        r"""Write sandbox configuration file.

        The configuration is based on work_module_dictionary and
        link_module_dictionary.

        work_module_dictionary is of both of the form

        {'module_name': ('tag', 'branch_id', 'maint branch', 'maint num')
         ...
        }

        where 'tag' is something like 'R1-01s' or None. And 'branch_id' is
        something like 'my_branch_id' or None.

        link_module_dictionary is of the form

        {'module_name': ('tag', 'build_id')
         ...
        }

        where 'build_id' may be something like '23' or None.

        The output configuration file is typically named "YAM.config". Below is
        a typical example.


        WORK_MODULES = pyam

        LINK_MODULES = DshellEnv/DshellEnv-R1-64c \
                       Dtest/Dtest-R1-01o \
                       SiteDefs/SiteDefs-R1-80h-Build01

        BRANCH_pyam =  pyam-R1-03a tag

        # BRANCH_Dtest = Dtest-R1-01o default_branch
        # BRANCH_DshellEnv = DshellEnv-R1-64c default_branch
        # BRANCH_SiteDefs = SiteDefs-R1-80h default_branch

        """
