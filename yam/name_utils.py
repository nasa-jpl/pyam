"""Utilities relating to module/package names."""

from __future__ import absolute_import

from . import yam_exception


def filter_module_name(name):
    """Return a name with leading/trailing spaces and trailing slashes removed.

    Raise an exception if the module name contains invalid characters.

    """
    return _filter_name(name=name, name_type="module")


def filter_package_name(name):
    """Return a name with leading/trailing spaces and trailing slashes removed.

    Raise an exception if the package name contains invalid characters.

    """
    return _filter_name(name=name, name_type="package")


def _filter_name(name, name_type):
    """Return the name stripped of innocuous characters.

    This includes things such as leading/trailing spaces and trailing slashes.
    The latter is common when the user uses tab completion.

    This also includes commas, quotes, and spaces. These characters can
    interfere in places where we rely on comma separated values.

    Raise exception when encountering characters that will cause problems in
    the database or configuration files. Strip innocuous characters such as

    """
    # Remove trailing/leading whitespace in addition to trailing slashes
    name = name.strip().rstrip("/")

    import re

    regex = r"^[a-zA-Z\-\+_0-9]+$"
    if re.match(regex, name):
        return name
    else:
        raise InvalidNameException(
            "'{name}' is not a valid {name_type} name since it does not "
            "match the regular expression '{regex}'".format(name=name, name_type=name_type, regex=regex)
        )


class InvalidNameException(yam_exception.YamException):
    """Exception raised when finding name with invalid characters."""
