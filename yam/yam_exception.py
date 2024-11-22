"""Contains base Yam exception class."""

from __future__ import absolute_import


class YamException(Exception):
    """Base exception for Yam exception classes."""

    def __init__(self, message):
        Exception.__init__(self, message)
