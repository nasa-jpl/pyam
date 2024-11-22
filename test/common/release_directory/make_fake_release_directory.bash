#!/bin/bash
#
# Make a fake release directory.

if [ $# -lt 1 ]
then
    echo "Usage: $0 release_directory"
    echo "    release_directory - Repository will be created at this path"
    exit 1
fi
release_directory="$1"

if [ -d "$release_directory" ]
then
    echo "ERROR: Path '$release_directory' already exists"
    exit 2
fi

# Get script-relative path
resolved_file_path="`readlink -f \"$0\"`"
directory_name="$(dirname $resolved_file_path)"
data="$directory_name/data/fake_release_directory/"

rsync --quiet -aP --cvs-exclude "$data" $release_directory
