#!/bin/bash -ex
#
# Test make_fake_repository.bash script.

temporary_directory="$(mktemp --directory)"
fake_repository_path="$temporary_directory/fake_repository"
../../common/svn/make_fake_repository.bash "$fake_repository_path"

checkout_path="$temporary_directory/my_checkout"
svn --quiet co "file://`readlink -f \"$fake_repository_path\"`" "$checkout_path"
if [ $? -ne 0 ]
then
    echo 'ERROR: Could not check out from fake repository.'
    exit 2
fi


rm -rf "$fake_repository_path"
rm -rf "$checkout_path"
rmdir "$temporary_directory"

echo OK
