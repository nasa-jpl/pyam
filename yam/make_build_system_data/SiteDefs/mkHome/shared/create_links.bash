#!/bin/bash -u

# This script is used for the yam-mklinks Makefile.yam target to export
# module links to the top level.
#
# USAGE:
#     crlinks.bash \
#         yam_root yam_root_relative_destination module_directory copy_link \
#         file1 file2 ...

yam_root=$1
shift

yam_root_relative_destination=$1
shift

module_directory=$1
shift

copy_link=$1
shift

destination=${yam_root}/${yam_root_relative_destination}

# Only create the link if there are some files to be linked.
if [ "$#" != "0" ]; then
    mkdir -p "$destination"
fi

while [ "$#" != "0" ]; do
    file=$1
    shift
    comp=$(basename "$file")
    if [ "$copy_link" -eq 0 ]
    then
        if [ ! -h "$destination/$comp" ]; then
            ln -s "$module_directory/$file" "$destination/$comp"
        fi
    else
        rm -f "$destination/$comp"
        cp --archive "$module_directory/$file" "$destination/$comp"
    fi
done
