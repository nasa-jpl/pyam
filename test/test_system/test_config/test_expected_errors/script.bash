#!/bin/bash
#
# Test that "pyam config --to-work" prints a friendly error message
# when issued outside of a sandbox.

# Unset configuration file environment variables as they may interfere.
unset YAM_PROJECT_CONFIG_DIR
unset YAM_PROJECT

# Use absolute path to avoid getting some possibly aliased version
PYAM=$(readlink -f ../../../../pyam)

temporary_directory=$(mktemp --directory)

pushd "$temporary_directory" >& /dev/null

expected='This command needs to be issued from within a sandbox'

# verify that the --to-work option is not available
actual=$("$PYAM" --quiet --no-build-server --database-connection '127.0.0.1:0/none' config --to-work FakeModule 2>&1)
if echo "$actual" | grep unrecognized
then
    echo 'OK'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
fi

# verify that the --branch option cannot be used with the --all-to-link option
actual=$("$PYAM" --quiet --no-build-server --database-connection '127.0.0.1:0/none' config --all-to-link --branch blah 2>&1)
if echo "$actual" | grep "can only be used"
then
    echo 'OK'
else
    echo "ERROR: Unexpected error occurred. See below (+ expected, - unexpected)"
    echo "+ $expected"
    echo "- $actual"
    exit 2
fi

popd > /dev/null


../../../common/sandbox/remove_fake_sandbox.bash "$sandbox_directory"
rm -rf "$temporary_directory"
