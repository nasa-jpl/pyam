#!/bin/bash
#
# Make a fake GIT repository for pyam tests and dump in to file.

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

echo "MAKING FAKE GIT REPO"
pwd

# Create the "Modules" directory.
#git init "$repository_path"

# Get path to data directory
resolved_file_path="`readlink -f \"$0\"`"
directory_name="$(dirname $resolved_file_path)"
data_tar_file="$directory_name/tarred_data.tar"
cd "$repository_path"
git init
tar xf "$data_tar_file"

echo "LOCATIONS"
echo $data_tar_file
pwd
echo "MVing"
#mv ../tarred_data/* .
echo "Test stuff 1" >> file1.txt
git add file1.txt
# Add files to repo#
#temporary_directory=$(mktemp --directory)
#temporary_checkout_directory="$temporary_directory/Dshell++"
repository_url="$(readlink -f $repository_path)"
#git clone  "$repository_url" "$temporary_checkout_directory"

#pushd "$temporary_checkout_directory" >& /dev/null
#tar xf "$data_tar_file"
#mv data_tarred_to_avoid_svn_commit_hooks/* .
#rm -rf data_tarred_to_avoid_svn_commit_hooks
#popd >& /dev/null

#echo "ADDING"

#git add  "$temporary_checkout_directory"/*

echo "COMMITING"
git commit --quiet  -m "Committed file1.txt"

#echo "RMing"

# Clean up temporary files
#rm -rf "$temporary_checkout_directory"
#rm -rf "$temporary_directory"


git branch "R4-06e"


git branch "R4-06f"

git branch "R1-49q"


git branch "RR1-49r"

echo "DONE MAKING FAKE GIT REPO"
