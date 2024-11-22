#!/usr/bin/env python

"""pyam installer."""

from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys

# distutils doesn't seem to set the shebang in the installed scripts properly.
from setuptools import setup
from setuptools.command import sdist


def required_packages():
    """Return list of required Python packages.

    This will print an error message if requirements are not met.

    """
    required = {
        "pysvn": "see http://pysvn.tigris.org",
        "mysql": "pip install mysql-connector",
        "dateutil": "pip install dateutil",
    }

    if not int(os.environ.get("NO_DEPENDENCY_CHECK", "0")):
        for package_name, message in required.items():
            try:
                __import__(package_name)
            except ImportError:
                print(
                    'ERROR: Python package "{name}" is required by pyam and '
                    "was not found ({message})".format(name=package_name, message=message)
                )
                sys.exit(2)

        _pysvn_version_check()
        _make_check()
        _python_check()

    return required


def _pysvn_version_check():
    """Check pysvn version."""
    import pysvn

    c = pysvn.Client()
    try:
        # Older versions of pysvn/SVN (in addition to other things) don't have
        # list() method.
        c.list
    except AttributeError:
        print("ERROR: pysvn version is either too old or built against an old " "version of the SVN library.")
        print(
            "       The below command will run without error on newer "
            "versions. Older versions are missing pysvn.client.list() among "
            "other features."
        )
        print()
        print('       python -c "import pysvn; c = pysvn.Client(); c.list"')
        print()
        sys.exit(2)


def _make_check():
    """Check if Make is installed."""
    try:
        make_process = subprocess.Popen(
            ["make", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        make_process.communicate()
    except OSError:
        print('ERROR: "make" command, which is required by pyam,  was not ' "found")
        sys.exit(2)


def _python_check():
    """Check if Python version is something we are compatible with."""
    if sys.version_info < (2, 7):
        print("ERROR: pyam requires Python 2.7")
        sys.exit(2)


def pyam_version():
    """Get version by manually reading file.

    Don't use import as it will depend on PYTHONPATH contents. (We
    definitely don't have yam in the PYTHONPATH when we distribute pyam
    to other machines.)

    """
    version = None
    with open("yam/__init__.py") as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                assert not version
                assert line.count("=") == 1
                import ast

                version = ast.literal_eval(line.split("=")[1].lstrip())
    assert version
    return version


def find_files(path):
    """Return list of all files in path (recursively).

    Ignore hidden files.

    """
    for root, directories, filenames in os.walk(path):
        for f in filenames:
            if not f.startswith("."):
                yield os.path.join(root, f)
        directories[:] = [d for d in directories if not d.startswith(".")]


class SourceDistributionCommand(sdist.sdist):
    """Override to build documentation."""

    def run(self):
        """Build documentation."""
        try:
            subprocess.call(["rst2pdf", "README.rst", "--output=README.pdf"])
        except OSError:
            pass

        # Avoid super() since we are dealing with an old-style class.
        sdist.sdist.run(self)


def main():
    """Set up pyam."""
    with open("README.rst") as readme_file:
        setup(
            name="pyam",
            version=pyam_version(),
            description="Python implementation of yam",
            long_description=readme_file.read(),
            license="",
            author="Steven Myint",
            author_email="Steven.Myint@jpl.nasa.gov",
            url="https://insidedlab.jpl.nasa.gov/internal/www/pyam/",
            cmdclass={"sdist": SourceDistributionCommand},
            packages=["yam", "yam.pysvn_verbose"],
            package_data={"yam": [os.path.relpath(f, "yam") for f in find_files("yam/make_build_system_data")]},
            scripts=[
                "pyam",
                "pyam-block-until-release",
                "pyam-build",
                "pyam-format",
                "scripts/srun",
                "scripts/yamroot",
            ],
            requires=required_packages(),
            zip_safe=False,
        )  # We need to open data files in the package.


if __name__ == "__main__":
    main()
