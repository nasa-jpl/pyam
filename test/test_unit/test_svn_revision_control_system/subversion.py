"""Subversion command-line wrapper.

This is for testing things against the actual command-line version of
Subversion.

"""

import subprocess


def check_out(url, path):
    """Check out using  "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert not path.startswith("file://")
    subprocess.call(["svn", "checkout", "--quiet", url, path])


def make_directory(path):
    """Make directory using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert not path.startswith("file://")
    subprocess.call(["svn", "mkdir", "--quiet", path])


def make_directory_in_repository(url, message):
    """Make directory using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert url.startswith("file://")
    subprocess.call(["svn", "mkdir", "--quiet", url, "--message", message])


def commit(path, message):
    """Commit using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert not path.startswith("file://")
    subprocess.call(["svn", "commit", "--quiet", "--message", message, path])


def update(path):
    """Update using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert not path.startswith("file://")
    subprocess.call(["svn", "update", "--quiet", "--non-interactive", path])


def property_set(path, property_type, property_value):
    """Set property using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert not path.startswith("file://")
    subprocess.call(["svn", "propset", "--quiet", property_type, property_value, path])


def copy(source_url, destination_url, message):
    """Copy using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    subprocess.call(
        [
            "svn",
            "copy",
            "--quiet",
            source_url,
            destination_url,
            "--message",
            message,
        ]
    )


def add(path):
    """Add using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert not path.startswith("file://")
    subprocess.call(["svn", "add", "--quiet", path])


def get_url(path):
    """Get the URL of path using "svn" command-line application.

    (as to not depend on other SVNRevisionControlSystem methods).

    """
    assert not path.startswith("file://")
    process = subprocess.Popen(["svn", "info", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()[0].decode("utf-8")
    # Output is of the form,
    #
    # ...
    # URL: <svn_url>
    # ...
    #
    import re

    return re.search(r"URL: ([^\n]+)", output).group(1).strip()
