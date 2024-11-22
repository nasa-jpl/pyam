#!/bin/bash
#
# Make a fake sandbox.

if [ $# -ne 1 ]
then
    echo "Usage: $0 <sandbox_directory>"
    exit 1
fi

sandbox_directory=$1

resolved_file_path="`readlink -f \"$0\"`"
dir_name="`dirname $resolved_file_path`"

rsync --archive --cvs-exclude "${dir_name}/data/fake_sandbox_for_rsync_only/"* "$sandbox_directory/"
# need this when running from a tagged pyam module checkout
chmod -R ug+w $sandbox_directory/
