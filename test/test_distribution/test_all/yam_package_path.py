#!/usr/bin/env python
"""Make sure that we are testing the correct yam package."""


from __future__ import print_function


if __name__ == "__main__":
    import yam
    import sys
    import os

    if len(sys.argv) != 2:
        print("Usage: {program} <path_to_compare>".format(program=sys.argv[0]))
        sys.exit(1)

    yam_package_path = os.path.realpath(yam.__file__.rstrip("c"))  # Remove c from .pyc
    correct_path = os.path.realpath(sys.argv[1])
    if yam_package_path == correct_path:
        sys.exit(0)
    else:
        print(
            'ERROR: We are testing the wrong yam Python package, "{path}". The correct one is at "{correct_path}". Make sure PYTHONPATH is correct. The yam Python package of this sandbox should have priority.'.format(
                path=yam_package_path, correct_path=correct_path
            )
        )
        sys.exit(2)
