"""Utility functions for dealing with Yam and the file system."""

from __future__ import absolute_import

from . import yam_exception


def find_sandbox_root(directory, max_directory_checks=None):
    """Return absolute path to the root of the sandbox that contains directory.

    Specify max_directory_checks to limit the number of parent
    directories we check.

    """

    def find_paths_in_ancestor_directory(paths, start_directory, max_directory_checks):
        """Return the parent directory that contains all specified paths."""
        import os

        split_path = os.path.abspath(start_directory).split("/")
        check_count = 0
        for i in reversed(range(len(split_path))):
            if max_directory_checks and check_count > max_directory_checks:
                break
            cur_path = os.path.join("/", *split_path[0 : i + 1])
            found_all = True
            for p in paths:
                if not os.path.exists(os.path.join(cur_path, p)):
                    found_all = False
            if found_all:
                return cur_path
            check_count += 1
        raise yam_exception.YamException(
            "Could not find root of sandbox of directory {directory}".format(directory=start_directory)
        )

    return find_paths_in_ancestor_directory(
        paths=("YAM.config", "common/YAM.modules"),
        start_directory=directory,
        max_directory_checks=max_directory_checks,
    )
