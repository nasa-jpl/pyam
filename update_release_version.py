#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
#
# Update pyam/__init__.py with a major/minor/patch version number
# derived from the YaM release tag (convert the trailing character into
# a patch level integer).

from yam.revision_tag_utils import split_revision_tag, incremented

if __name__ == "__main__":
    import os

    import subprocess

    latest = subprocess.Popen(["pyam", "--no-log", "latest", "pyam"], stdout=subprocess.PIPE).communicate()[0]

    # latest = os.system('pyam latest pyam')
    print("latest=", latest)
    old_revision_tag = latest.decode().split()[1]
    # get the release tag
    # revision_tag = os.getenv('YAM_RELEASE_TAG')
    assert old_revision_tag
    # print('RTAG=', revision_tag)

    revision_tag = incremented(old_revision_tag)
    # print('IIIII', old_revision_tag, revision_tag)
    # extract the major/minor/patch version numbers
    (major, minor, extension) = split_revision_tag(revision_tag)
    # print('LLL', major, minor, extension)
    relnum = "%d.%d" % (major, minor)
    if extension:
        relnum += ".%d" % (extension)

    # print('relnum=', relnum)
    print('Updating version number for "%s" releaase to "%s"' % (revision_tag, relnum))

    # write out the contents into yam/__init__.py file
    mess = (
        """\"""yam package.\"""

__author__ = "Steven Myint"

__version__ = "%s"

__maintainer__ = "Abhi Jain"
__email__ = "jain@jpl.nasa.gov"
"""
        % relnum
    )

    fd = open("yam/__init__.py", "w")
    fd.write(mess)
    fd.close()
    os.system("svn commit -m Updated yam/__init__.py")
