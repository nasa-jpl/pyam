#!/bin/bash
#
# Tar up the software for distribution.

if [ $# -lt 1 ]
then
    echo "Usage: $0 <output_directory>"
    exit 1
fi

# Get absolute path
output_directory=$(readlink -f "$1")

# Change directory so that we are in the root of pyam
resolved_file_path=$(readlink -f "$0")
pyam_directory_path=$(dirname "$resolved_file_path")
cd "$pyam_directory_path"

# "sdist" cannot be run by multiple processes in the same directory since it
# puts things in the current directory.
lock_directory="$pyam_directory_path/distribute_lock"
count=0
while true
do
    if mkdir "$lock_directory" >& /dev/null
    then
        break
    fi

    if [ $count -gt 18 ]
    then
        echo 'Timed out due to another process using the script' >&2
        exit 1
    fi

    echo "Waiting for other process to finish ('$lock_directory')"  >&2
    sleep 10

    let count=$count+1
done

cleanup()
{
    rm -rf "$lock_directory"
}
trap cleanup SIGINT SIGTERM

./setup.py sdist --dist-dir="$output_directory"

cleanup
