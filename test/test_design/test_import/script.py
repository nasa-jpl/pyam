#!/usr/bin/env python
"""Make sure importing is done correctly.

In the top-level pyam utility, we should import Yam modules in a way that can
be caught by our exception handling.

"""

from __future__ import print_function

import sys


def main():
    filename = "../../../pyam"
    with open(filename) as pyam:
        for line_number, line in enumerate(pyam):
            if line.startswith("import") or line.startswith("from"):
                if "yam" in line.lower():
                    sys.stderr.write(
                        "{filename}:{line_number}: ".format(filename=filename, line_number=line_number)
                        + "yam should be imported more locally so that we can "
                        "catch an ImportError via exception handling\n"
                    )
                    return 1

    print("OK")


if __name__ == "__main__":
    sys.exit(main())
