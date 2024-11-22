#!/bin/bash
#
# Make a fake SVN repository for pyam tests and dump in to file.

if [ $# -lt 1 ]
then
    echo "Usage: $0 repository_path"
    echo "    repository_path - Repository will be created at this path"
    exit 1
fi
repository_path="$1"

if [ -d "$repository_path" ]
then
    echo "ERROR: Path '$repository_path' already exists"
    exit 2
fi

# Create the "Modules" directory.
svnadmin create "$repository_path"

# Get path to data directory
resolved_file_path="`readlink -f \"$0\"`"
directory_name="$(dirname $resolved_file_path)"
data_tar_file="$directory_name/data_tarred_to_avoid_svn_commit_hooks.tar"

# Add files to repo
temporary_directory=$(mktemp --directory)
temporary_checkout_directory="$temporary_directory/Dshell++"
repository_url="file://$(readlink -f $repository_path)"
svn checkout --quiet "$repository_url" "$temporary_checkout_directory"

pushd "$temporary_checkout_directory" >& /dev/null
tar xf "$data_tar_file"
mv data_tarred_to_avoid_svn_commit_hooks/* .
rm -rf data_tarred_to_avoid_svn_commit_hooks
popd >& /dev/null

svn add --quiet "$temporary_checkout_directory"/*
svn commit --quiet --message 'Committed.' "$temporary_checkout_directory"/*

# Clean up temporary files
rm -rf "$temporary_checkout_directory"
rm -rf "$temporary_directory"

# Make a feature branch "R4-06e" for Dshell++
svn copy --quiet "$repository_url/Modules/Dshell++/trunk" "$repository_url/Modules/Dshell++/releases/Dshell++-R4-06e" --message='Created feature branch "R4-06e"'

# Make a feature branch "R4-06f" for Dshell++
svn copy --quiet "$repository_url/Modules/Dshell++/trunk" "$repository_url/Modules/Dshell++/releases/Dshell++-R4-06f" --message='Created feature branch "R4-06f"'

# Make a feature branch "R4-06g for Dshell++
svn copy --quiet "$repository_url/Modules/Dshell++/trunk" "$repository_url/Modules/Dshell++/releases/Dshell++-R4-06g" --message='Created feature branch "R4-06g"'

# Make a feature branch "R1-49q" for DshellEnv
svn copy --quiet "$repository_url/Modules/DshellEnv/trunk" "$repository_url/Modules/DshellEnv/releases/DshellEnv-R1-49q" --message='Created feature branch "R1-49q"'

# Make a feature branch "R1-49r for DshellEnv
svn copy --quiet "$repository_url/Modules/DshellEnv/trunk" "$repository_url/Modules/DshellEnv/releases/DshellEnv-R1-49r" --message='Created feature branch "RR1-49r"'
