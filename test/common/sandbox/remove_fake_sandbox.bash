#!/bin/bash
#
# Remove a fake sandbox.

if [ $# -ne 1 ]
then
    echo "Usage: $0 <sandbox_directory>"
    exit 1
fi

sandbox_directory=$1
rm -rf "$sandbox_directory"
