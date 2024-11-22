"""Contains the Module class."""

from __future__ import absolute_import

import abc
from enum import Flag, unique, auto


class Module(object):
    """Represents an instance of a Yam module.

    The module's source code can be checked out.

    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def check_out(self, progress_callback=lambda _: None):
        """Check out the source code for this Yam module."""


@unique
class WorkModuleType(Flag):
    """
    Enum for different types of work modules
    """

    NONE = auto()  # not a work module
    TAGGED = auto()  # tagged checkout
    BRANCH = auto()  # checkout on a branch
    MAIN = auto()  # main trunk checkout
    ALL = TAGGED | BRANCH | MAIN  # any of the work module options
