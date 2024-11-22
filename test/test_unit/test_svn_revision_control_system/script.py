# encoding: utf-8

"""Test SVNRevisionControlSystem.

If SVN returns a "Can't get exclusive lock on file" error, see:

http://serverfault.com/questions/61594/what-does-no-locks-available-mean

Possible causes include:

1. NFS lock daemon (lockd) may not be running.
2. The NFS drive may be full.

"""

import os
import subprocess
import unittest

try:
    from pexpect import spawnu
except ImportError:
    from pexpect import spawn as spawnu

from yam import yam_exception
from yam import svn_revision_control_system

# Use command-line Subversion wrapper rather than pysvn to simulate interaction
# with command line.
import subversion


class Tests(unittest.TestCase):
    def test_decode(self):
        self.assertEqual(
            "abc",
            svn_revision_control_system.decode(b"abc", fallback="fallback"),
        )

        self.assertEqual(
            "©",
            svn_revision_control_system.decode(b"\xa9", fallback="fallback"),
        )

    def test_decode_with_fallback(self):
        self.assertEqual(
            "fallback",
            svn_revision_control_system.decode(b"\x81b", fallback="fallback", encodings=["utf-8"]),
        )

    def test_decode_with_unicode_input(self):
        self.assertEqual(
            "okay",
            svn_revision_control_system.decode("okay", fallback="fallback"),
        )


class SVNRevisionControlSystemTests(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        self.__svn_revision_control_system = self._revision_control_system()

        # Create a temporary directory and create an repository in it
        import tempfile

        self.__temporary_file_path = os.path.abspath(tempfile.mkdtemp(dir="."))

        self.__repository_path = os.path.join(self.__temporary_file_path, "temporary_repository")
        self._create_repository(path=self.__repository_path)

        self.__repository_url = "file://" + os.path.abspath(path=self.__repository_path)

    def _revision_control_system(self):
        return svn_revision_control_system.SVNRevisionControlSystem(
            username=None,
            login_callback=lambda realm, username, may_save: (0, "", "", False),
            trust_ssl_server_callback=lambda trust_dict: (False, 0, False),
            use_merge_info=True,
            progress_callback=lambda current_bytes=-1, print_time_last=None: None,
        )

    def _create_repository(self, path):
        subprocess.call(["svnadmin", "create", path])

    def _temporary_file_path(self):
        return self.__temporary_file_path

    def _repository_url(self):
        return self.__repository_url

    def tearDown(self):
        """Automatically called after each test* method."""
        import shutil

        shutil.rmtree(path=self._temporary_file_path(), ignore_errors=True)

    def test_check_out(self):
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.assertFalse(os.path.isdir(check_out_directory))

        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)
        self.assertTrue(os.path.isdir(check_out_directory))

    def test_check_out_with_callbacks_disabled(self):
        my_revision_control_system = svn_revision_control_system.SVNRevisionControlSystem(
            username=None,
            login_callback=None,
            trust_ssl_server_callback=None,
            progress_callback=None,
        )
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.assertFalse(os.path.isdir(check_out_directory))

        my_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)
        self.assertTrue(os.path.isdir(check_out_directory))

    def test_check_out_non_existent_directory_results_in_exception(self):
        with self.assertRaises(yam_exception.YamException):
            self.__svn_revision_control_system.check_out(
                source="svn://non_existent_directory",
                target="fake_check_out_directory",
            )

    def test_check_out_with_invalid_url(self):
        with self.assertRaises(yam_exception.YamException):
            self.__svn_revision_control_system.check_out(
                source="svn//non_existent_directory",
                target="fake_check_out_directory",
            )

    def test_make_directory(self):
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)

        new_directory_path = os.path.join(check_out_directory, "new_directory")
        self.assertFalse(os.path.isdir(new_directory_path))

        self.__svn_revision_control_system.make_directory(new_directory_path)
        self.assertTrue(os.path.isdir(new_directory_path))

    def test_make_directory_that_already_exists_should_raise_exception(self):
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)

        new_directory_path = os.path.join(check_out_directory, "new_directory")

        self.__svn_revision_control_system.make_directory(new_directory_path)

        from yam import revision_control_system

        with self.assertRaises(revision_control_system.DirectoryAlreadyExists):
            self.__svn_revision_control_system.make_directory(new_directory_path)

    def test_make_directory_without_authorization_should_raise_permission_exception(self):
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)

        new_directory_path = os.path.join(check_out_directory, "new_directory")

        subprocess.call(["chmod", "-R", "ugo-w", check_out_directory])

        from yam import revision_control_system

        with self.assertRaises(revision_control_system.PermissionException):
            self.__svn_revision_control_system.make_directory(new_directory_path)

        subprocess.call(["chmod", "-R", "ug+w", check_out_directory])

    def test_make_directory_without_authorization_should_raise_permission_exception_with_url(self):
        subprocess.call(["chmod", "-R", "ugo-w", self.__repository_path])

        from yam import revision_control_system

        with self.assertRaises(revision_control_system.PermissionException):
            self.__svn_revision_control_system.make_directory(os.path.join(self.__repository_url, "foo"))

        subprocess.call(["chmod", "-R", "ug+w", self.__repository_path])

    def test_check_in(self):
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)

        new_directory_path = os.path.join(check_out_directory, "new_directory")
        self.__svn_revision_control_system.make_directory(new_directory_path)

        # A separate check out from the repository should be yet be affected.
        new_check_out_directory = os.path.join(self._temporary_file_path(), "new_checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=new_check_out_directory)
        self.assertFalse(os.path.isdir(os.path.join(new_check_out_directory, "new_directory")))

        # Check in the changes in the 'checkout_test' directory.
        self.__svn_revision_control_system.check_in(path=check_out_directory, log_message="Committed.")

        # After committing all other check outs should be affected.
        self.__svn_revision_control_system.update(path=new_check_out_directory)
        self.assertTrue(os.path.isdir(os.path.join(new_check_out_directory, "new_directory")))

    def test_check_in_with_exception(self):
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)

        conflict_filename = "blah_file"
        blah_file = os.path.join(check_out_directory, conflict_filename)
        with open(blah_file, "w") as f:
            f.write("blahblah\n")
        subversion.add(blah_file)
        del blah_file

        # A separate check out from the repository should be yet be affected.
        new_check_out_directory = os.path.join(self._temporary_file_path(), "new_checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=new_check_out_directory)

        self.__svn_revision_control_system.check_in(path=check_out_directory, log_message="Committed.")

        blah_file = os.path.join(new_check_out_directory, conflict_filename)
        with open(blah_file, "w") as f:
            f.write("hello world\n")
        del blah_file

        # A conflict should occur here.
        subversion.update(new_check_out_directory)

        # Trying to check in a conflicted file should raise an exception.
        with self.assertRaises(yam_exception.YamException):
            # Check in the changes in the 'checkout_test' directory.
            self.__svn_revision_control_system.check_in(path=new_check_out_directory, log_message="Committed.")

    def test_working_copy_exists(self):
        check_out_directory = os.path.join(self._temporary_file_path(), "checkout_test")
        self.__svn_revision_control_system.check_out(source=self._repository_url(), target=check_out_directory)
        self.assertTrue(self.__svn_revision_control_system.working_copy_exists(path=check_out_directory))

    def test_working_copy_not_exists(self):
        self.assertFalse(self.__svn_revision_control_system.working_copy_exists(path="non_existent_directory"))

    def test_branch(self):
        # Create a directory via command-line client.
        my_new_directory_url = os.path.join(self._repository_url(), "my_new_directory")
        subversion.make_directory_in_repository(my_new_directory_url, "Made my_new_directory in repository.")

        # Use svn_revision_control_system.branch() to branch the above directory
        # and put it in a given location.
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        self.__svn_revision_control_system.branch(source_url=my_new_directory_url, destination_url=my_branch_url)

        # Confirm that the branch exists by checking it out.
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)
        self.assertTrue(os.path.isdir(my_branch_path))

    def test_switch_to_branch(self):
        # Create a directory via command-line client
        my_new_directory_url = os.path.join(self._repository_url(), "my_new_directory")
        subversion.make_directory_in_repository(my_new_directory_url, "Made my_new_directory in repository.")

        # Create a branch via command-line client
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_new_directory_url,
            destination_url=my_branch_url,
            message='Branched "my_branch" off of "my_trunk".',
        )

        # Check out branch
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)

        # Check the URL
        self.assertEqual(subversion.get_url(path=my_branch_path), my_branch_url)

        # Do the switch_to_branch() call
        self.__svn_revision_control_system.switch_to_branch(path=my_branch_path, branch_url=my_new_directory_url)

        # Confirm that the URL has changed
        self.assertEqual(subversion.get_url(path=my_branch_path), my_new_directory_url)

    def test_exists(self):
        self.assertFalse(self.__svn_revision_control_system.exists(url="non_existent_url"))
        self.assertTrue(self.__svn_revision_control_system.exists(self._repository_url()))

    def test_url(self):
        # Check out repository via command-line client (as to not depend on
        # other SVNRevisionControlSystem methods).
        import subprocess

        my_checkout_directory = os.path.join(self._temporary_file_path(), "my_checkout")
        subprocess.call(
            [
                "svn",
                "checkout",
                "--quiet",
                self._repository_url(),
                my_checkout_directory,
            ]
        )

        self.assertEqual(
            self.__svn_revision_control_system.url(path=os.path.join(self._temporary_file_path(), "my_checkout")),
            os.path.join(self._repository_url()),
        )

    def test_url_when_path_is_not_a_working_copy(self):
        from yam import revision_control_system

        with self.assertRaises(revision_control_system.NotAWorkingCopyException):
            self.__svn_revision_control_system.url("non_existent_directory")

    def test_uncommitted_files(self):
        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=self._repository_url(), path=my_checkout_directory)

        self.assertEqual(
            self.__svn_revision_control_system.uncommitted_files(path=my_checkout_directory),
            [],
        )

        # Create a directory via command-line client.
        my_new_directory = path.join(my_checkout_directory, "my_new_directory")
        subversion.make_directory(my_new_directory)

        self.assertEqual(
            [
                path.realpath(f)
                for f in self.__svn_revision_control_system.uncommitted_files(path=my_checkout_directory)
            ],
            [path.realpath(my_new_directory)],
        )

        # Commit all files and test again
        subversion.commit(path=my_new_directory, message="committed!!!")

        self.assertEqual(
            self.__svn_revision_control_system.uncommitted_files(path=my_checkout_directory),
            [],
        )

    def test_uncommitted_files_with_property_modified(self):
        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=self._repository_url(), path=my_checkout_directory)

        self.assertEqual(
            self.__svn_revision_control_system.uncommitted_files(path=my_checkout_directory),
            [],
        )

        # Create a directory via command-line client and commit it.
        my_new_directory = path.join(my_checkout_directory, "my_new_directory")
        subversion.make_directory(my_new_directory)
        subversion.commit(path=my_new_directory, message="committed!!!")

        # Files with changed properties should be listed as uncomitted
        subversion.property_set(
            path=my_new_directory,
            property_type="svn:ignore",
            property_value="blah",
        )

        self.assertEqual(
            [
                path.realpath(f)
                for f in self.__svn_revision_control_system.uncommitted_files(path=my_checkout_directory)
            ],
            [path.realpath(my_new_directory)],
        )

        # Commit all files and test again
        subversion.commit(path=my_new_directory, message="committed!!!")
        self.assertEqual(
            self.__svn_revision_control_system.uncommitted_files(path=my_checkout_directory),
            [],
        )

    def test_uncommitted_files_raise_exception_when_not_a_working_copy(self):
        from yam import revision_control_system
        import tempfile

        temp_directory = tempfile.mkdtemp(dir=".")
        temporary_file = tempfile.NamedTemporaryFile(mode="w", dir=temp_directory, delete=True)

        with self.assertRaises(revision_control_system.NotAWorkingCopyException):
            self.__svn_revision_control_system.uncommitted_files(path=temporary_file.name)

        del temporary_file
        import shutil

        shutil.rmtree(temp_directory, ignore_errors=True)

    def test_generate_logs_since_last_branch(self):
        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=self._repository_url(), path=my_checkout_directory)

        # Create a directory via command-line client and commit it.
        my_new_directory = path.join(my_checkout_directory, "my_new_directory")
        subversion.make_directory(my_new_directory)
        subversion.commit(path=my_new_directory, message='Create directory "my_new_directory"')

        alpha_directory = path.join(my_checkout_directory, "alpha")
        subversion.make_directory(alpha_directory)
        subversion.commit(path=alpha_directory, message='Create directory "alpha"')

        # Files with changed properties should be listed as modified
        subversion.property_set(
            path=my_new_directory,
            property_type="svn:ignore",
            property_value="blah",
        )

        # Commit all files and test again
        subversion.commit(path=my_new_directory, message="Modify svn:ignore")

        self.assertEqual(
            self.__svn_revision_control_system.generate_logs_since_last_branch(path=my_checkout_directory),
            """* Modify svn:ignore

  SVN revision: 3
  M my_new_directory

* Create directory "alpha"

  SVN revision: 2
  A alpha

* Create directory "my_new_directory"

  SVN revision: 1
  A my_new_directory""",
        )

        self.assertEqual(
            self.__svn_revision_control_system.generate_logs_since_last_branch(
                path=my_checkout_directory, ignored_paths=("my_new_directory",)
            ),
            """* Create directory "alpha"

  SVN revision: 2
  A alpha""",
        )

        self.assertEqual(
            self.__svn_revision_control_system.generate_logs_since_last_branch(
                path=my_checkout_directory,
                ignored_paths=("my_new_directory", "alpha"),
            ),
            "",
        )

    def test_generate_logs_since_last_branch_should_ignore_branch_creation_message(self):
        my_trunk_url = os.path.join(self._repository_url(), "my_trunk")
        subversion.make_directory_in_repository(my_trunk_url, 'Created "my_trunk" directory in repository.')

        # Create a branch
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_trunk_url,
            destination_url=my_branch_url,
            message="branch creation",
        )

        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=my_branch_url, path=my_checkout_directory)

        self.assertEqual(
            self.__svn_revision_control_system.generate_logs_since_last_branch(path=my_checkout_directory),
            "",
        )

    def test_generate_logs_since_divergence(self):
        my_trunk_url = os.path.join(self._repository_url(), "my_trunk")
        subversion.make_directory_in_repository(my_trunk_url, 'Created "my_trunk" directory in repository.')

        # Check out my_trunk_url to add some files.
        #
        # my_trunk-+-blah_directory/
        #          `-blah_file (contents being 'blahblah\n')
        #
        my_trunk_path = os.path.join(self._temporary_file_path(), "my_trunk")
        subversion.check_out(url=my_trunk_url, path=my_trunk_path)
        subversion.make_directory(os.path.join(my_trunk_path, "blah_directory"))
        trunk_blah_file = os.path.join(my_trunk_path, "blah_file")
        with open(trunk_blah_file, "w") as f:
            f.write("blahblah\n")
        subversion.add(trunk_blah_file)
        subversion.commit(my_trunk_path, message='Committed "my_trunk".')

        # Branch off of my_trunk_url.
        my_tagged_url = os.path.join(self._repository_url(), "my_tag")
        subversion.copy(
            source_url=my_trunk_url,
            destination_url=my_tagged_url,
            message='Branched "my_tag" off of "my_trunk".',
        )

        # Confirm that generateLogsSinceLastDivergence() generates no logs at
        # this point.
        self.assertEqual(
            self.__svn_revision_control_system.generate_logs_since_divergence(
                path=my_trunk_path, tagged_url=my_tagged_url
            ),
            "",
        )

        with open(trunk_blah_file, "w") as f:
            f.write("modified blahblah\n")
        subversion.commit(my_trunk_path, message='Commit "my_trunk" after tag')

        # Confirm that generateLogsSinceLastDivergence() generates log text at
        # this point.
        self.assertEqual(
            self.__svn_revision_control_system.generate_logs_since_divergence(
                path=my_trunk_path, tagged_url=my_tagged_url
            ),
            '* Commit "my_trunk" after tag\n\n  SVN revision: 4\n  M blah_file',
        )

    def test_reintegrate(self):
        # Set up a "trunk" and branch off of it so that we can test
        # svn_revision_control_system.reintegrate().
        my_trunk_url = os.path.join(self._repository_url(), "my_trunk")
        subversion.make_directory_in_repository(my_trunk_url, 'Created "my_trunk" directory in repository.')

        # Check out my_trunk_url to add some files.
        #
        # my_trunk-+-blah_directory/
        #          `-blah_file (contents being 'blahblah\n')
        #
        my_trunk_path = os.path.join(self._temporary_file_path(), "my_trunk")
        subversion.check_out(url=my_trunk_url, path=my_trunk_path)
        subversion.make_directory(os.path.join(my_trunk_path, "blah_directory"))
        trunk_blah_file = os.path.join(my_trunk_path, "blah_file")
        with open(trunk_blah_file, "w") as f:
            f.write("blahblah\n")
        subversion.add(trunk_blah_file)
        subversion.commit(my_trunk_path, message='Committed "my_trunk".')

        # Branch off of my_trunk_url.
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_trunk_url,
            destination_url=my_branch_url,
            message='Branched "my_branch" off of "my_trunk".',
        )

        # Make some changes to the branch.
        #
        # my_branch-+-blah_directory/
        #           |-new_directory/
        #           `-blah_file (modified contents being 'blahblah\nappended\n')
        #
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)
        branch_blah_file = os.path.join(my_branch_path, "blah_file")
        with open(branch_blah_file, "a") as f:
            f.write("appended\n")
        subversion.make_directory(os.path.join(my_branch_path, "new_directory"))
        subversion.commit(my_branch_path, message='Committed "my_branch".')

        # Do the actual reintegrate() test.
        my_archive_url = os.path.join(self._repository_url(), "my_archive")
        self.__svn_revision_control_system.reintegrate(
            path=my_branch_path,
            original_url=my_trunk_url,
            archive_url=my_archive_url,
        )
        subversion.commit(path=my_branch_path, message="committed after reintegrate")

        # We don't want to accidentally use these during verification.
        # "my_branch" is now "dead" and archived into archive_url.
        del my_branch_path
        del my_branch_url
        del my_trunk_path

        # Do a clean check out of my_trunk_url to make sure files are merged correctly.
        #
        # clean_checkout-+-blah_directory/
        #                |-new_directory/
        #                `-blah_file (modified contents being 'blahblah\nappended\n')
        #
        def verify_current_structure(path):
            self.assertTrue(os.path.exists(os.path.join(path, "blah_directory")))
            self.assertTrue(os.path.exists(os.path.join(path, "new_directory")))
            self.assertTrue(os.path.exists(os.path.join(path, "blah_file")))
            with open(os.path.join(path, "blah_file"), "r") as f:
                self.assertEqual(f.read(), "blahblah\nappended\n")

        my_clean_trunk_path = os.path.join(self._temporary_file_path(), "my_clean_trunk")
        subversion.check_out(url=my_trunk_url, path=my_clean_trunk_path)
        verify_current_structure(path=my_clean_trunk_path)

        # Verify that branch got archived by checking out my_archive_url.
        my_archive_path = os.path.join(self._temporary_file_path(), "my_archive")
        subversion.check_out(url=my_archive_url, path=my_archive_path)
        verify_current_structure(path=my_archive_path)

    def test_reintegrate_should_roll_back_switch_and_raise_exception_on_failure(self):
        # Set up a "trunk" and branch off of it so that we can test
        # svn_revision_control_system.reintegrate().
        my_trunk_url = os.path.join(self._repository_url(), "my_trunk")
        subversion.make_directory_in_repository(my_trunk_url, 'Created "my_trunk" directory in repository.')

        # Branch off of my_trunk_url.
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_trunk_url,
            destination_url=my_branch_url,
            message='Branched "my_branch" off of "my_trunk".',
        )

        # Check out the branch and touch (but don't commit or add) a file that
        # will collide with trunk
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)
        branch_blah_file = os.path.join(my_branch_path, "blah_file")
        with open(branch_blah_file, "w") as f:
            f.write("abc\n")

        # Create the same 'blah_file' file in the trunk, but commit it here
        my_trunk_path = os.path.join(self._temporary_file_path(), "my_trunk")
        subversion.check_out(url=my_trunk_url, path=my_trunk_path)
        trunk_blah_file = os.path.join(my_trunk_path, "blah_file")
        with open(trunk_blah_file, "w") as f:
            f.write("blahblah\n")
        subversion.add(trunk_blah_file)
        subversion.commit(my_trunk_path, message='Committed "my_trunk".')

        my_archive_url = os.path.join(self._repository_url(), "my_archive")

        from yam import revision_control_system

        with self.assertRaises(revision_control_system.ReintegrationException):
            self.__svn_revision_control_system.reintegrate(
                path=my_branch_path,
                original_url=my_trunk_url,
                archive_url=my_archive_url,
            )

        # Make sure the working copy has been rolled back properly.
        self.assertEqual(my_branch_url, subversion.get_url(my_branch_path))

    def test_reintegrate_when_not_fully_up_to_sync_with_trunk(self):
        # Set up a "trunk" and branch off of it so that we can test
        # svn_revision_control_system.reintegrate().
        my_trunk_url = os.path.join(self._repository_url(), "my_trunk")
        subversion.make_directory_in_repository(my_trunk_url, 'Created "my_trunk" directory in repository.')

        # Check out my_trunk_url to add some files.
        #
        # my_trunk-+-blah_directory/
        #          `-blah_file (contents being 'blahblah\n')
        #
        my_trunk_path = os.path.join(self._temporary_file_path(), "my_trunk")
        subversion.check_out(url=my_trunk_url, path=my_trunk_path)
        subversion.make_directory(os.path.join(my_trunk_path, "blah_directory"))
        trunk_blah_file = os.path.join(my_trunk_path, "blah_file")
        with open(trunk_blah_file, "w") as f:
            f.write("blahblah\n")
        subversion.add(trunk_blah_file)
        subversion.commit(my_trunk_path, message='Committed "my_trunk".')

        # Branch off of my_trunk_url.
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_trunk_url,
            destination_url=my_branch_url,
            message='Branched "my_branch" off of "my_trunk".',
        )

        # Make some changes to the branch.
        #
        # my_branch-+-blah_directory/
        #           |-new_directory/
        #           `-blah_file (modified contents being 'blahblah\nappended\n')
        #
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)
        branch_blah_file = os.path.join(my_branch_path, "blah_file")
        with open(branch_blah_file, "a") as f:
            f.write("appended\n")
        subversion.make_directory(os.path.join(my_branch_path, "new_directory"))
        subversion.commit(my_branch_path, message='Committed "my_branch".')

        # In this case, let's change the trunk a bit before reintegration.
        # So "my_branch" will not be in sync with "my_trunk".
        subversion.make_directory(os.path.join(my_trunk_path, "another_blah_directory"))
        subversion.commit(my_trunk_path, message='Committed "my_trunk".')

        # Do the actual reintegrate() test.
        my_archive_url = os.path.join(self._repository_url(), "my_archive")
        self.__svn_revision_control_system.reintegrate(
            path=my_branch_path,
            original_url=my_trunk_url,
            archive_url=my_archive_url,
        )
        subversion.commit(path=my_branch_path, message="committed after reintegrate")

        # We don't want to accidentally use these during verification.
        # "my_branch" is now "dead" and archived into archive_url.
        del my_branch_path
        del my_branch_url
        del my_trunk_path

        # Do a clean check out of my_trunk_url to make sure files are merged correctly.
        #
        # clean_checkout-+-blah_directory/
        #                |-new_directory/
        #                `-blah_file (modified contents being 'blahblah\nappended\n')
        #
        def verify_current_structure(path):
            self.assertTrue(os.path.exists(os.path.join(path, "blah_directory")))
            self.assertTrue(os.path.exists(os.path.join(path, "new_directory")))
            self.assertTrue(os.path.exists(os.path.join(path, "blah_file")))
            with open(os.path.join(path, "blah_file"), "r") as f:
                self.assertEqual(f.read(), "blahblah\nappended\n")

        my_clean_trunk_path = os.path.join(self._temporary_file_path(), "my_clean_trunk")
        subversion.check_out(url=my_trunk_url, path=my_clean_trunk_path)
        verify_current_structure(path=my_clean_trunk_path)
        self.assertTrue(os.path.exists(os.path.join(my_clean_trunk_path, "another_blah_directory")))

        # Verify that branch got archived by checking out my_archive_url.
        my_archive_path = os.path.join(self._temporary_file_path(), "my_archive")
        subversion.check_out(url=my_archive_url, path=my_archive_path)
        verify_current_structure(path=my_archive_path)

    def test_generate_diff(self):
        my_trunk_url = os.path.join(self._repository_url(), "my_trunk")
        subversion.make_directory_in_repository(my_trunk_url, 'Created "my_trunk" directory in repository.')

        # Check out my_trunk_url to add some files.
        my_trunk_path = os.path.join(self._temporary_file_path(), "my_trunk")
        subversion.check_out(url=my_trunk_url, path=my_trunk_path)
        trunk_blah_file = os.path.join(my_trunk_path, "blah_file")
        with open(trunk_blah_file, "w") as f:
            f.write("blahblah\n1\n\n\n2")
        subversion.add(trunk_blah_file)
        subversion.commit(my_trunk_path, message='Committed "my_trunk".')

        # Branch off of my_trunk_url.
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_trunk_url,
            destination_url=my_branch_url,
            message='Branched "my_branch" off of "my_trunk".',
        )

        # Make some changes to the branch.
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)
        branch_blah_file = os.path.join(my_branch_path, "blah_file")
        with open(branch_blah_file, "w") as f:
            f.write("blahblah\n3\n\n\n2")
        subversion.make_directory(os.path.join(my_branch_path, "new_directory"))

        abc_filename = os.path.join(my_branch_path, "abc")
        with open(abc_filename, "w") as f:
            f.write("abc\nabc\nabc\n")
        subversion.add(abc_filename)

        subversion.commit(my_branch_path, message='Committed "my_branch".')

        # Test generate_diff().
        self.assertEqual(
            normalize(self.__svn_revision_control_system.generate_diff(from_url=my_trunk_url, to_url=my_branch_url)),
            normalize(
                """Index: abc
===================================================================
--- abc\t(.../my_trunk)\t(revision 0)
+++ abc\t(.../my_branch)\t(revision 4)
@@ -0,0 +1,3 @@
+abc
+abc
+abc
Index: blah_file
===================================================================
--- blah_file\t(.../my_trunk)\t(revision 4)
+++ blah_file\t(.../my_branch)\t(revision 4)
@@ -1,5 +1,5 @@
 blahblah
-1
+3


 2
\ No newline at end of file
"""
            ),
        )

        # Test generate_diff() with ignored files.
        self.assertEqual(
            self.__svn_revision_control_system.generate_diff(
                from_url=my_trunk_url,
                to_url=my_branch_url,
                ignored_paths=("blah_file", "abc"),
            ),
            "abc: Skipping diffs (uninteresting)\nblah_file: Skipping diffs (uninteresting)",
        )

        # Test generate_diff() with ignored files.
        self.assertEqual(
            normalize(
                self.__svn_revision_control_system.generate_diff(
                    from_url=my_trunk_url,
                    to_url=my_branch_url,
                    ignored_paths=("abc",),
                )
            ),
            normalize(
                """Index: blah_file
===================================================================
--- blah_file\t(.../my_trunk)\t(revision 4)
+++ blah_file\t(.../my_branch)\t(revision 4)
@@ -1,5 +1,5 @@
 blahblah
-1
+3


 2
\ No newline at end of file
"""
            ),
        )

        self.assertTrue(
            self.__svn_revision_control_system.has_modifications(from_url=my_trunk_url, to_url=my_branch_url)
        ),

        self.assertFalse(
            self.__svn_revision_control_system.has_modifications(from_url=my_branch_url, to_url=my_branch_url)
        ),

    def test_modified_paths_since_divergence(self):
        # Create a directory via command-line client.
        my_new_directory_url = os.path.join(self._repository_url(), "my_new_directory")
        subversion.make_directory_in_repository(my_new_directory_url, "Made my_new_directory in repository.")

        # Create a branch via command-line client
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_new_directory_url,
            destination_url=my_branch_url,
            message='Branched "my_branch" off of "my_trunk".',
        )

        # Check out branch
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)

        # Make some changes
        abc_filename = os.path.join(my_branch_path, "abc")
        with open(abc_filename, "w") as f:
            f.write("abc\nabc\nabc\n")
        subversion.add(abc_filename)

        # pathsChangedSinceLastBranch() should still report no changes since
        # changes haven't been committed
        self.assertEqual(
            self.__svn_revision_control_system.modified_paths_since_divergence(
                path=my_branch_path, tagged_url=my_new_directory_url
            ),
            [],
        )

        subversion.commit(path=my_branch_path, message="")

        # Now pathsChangedSinceLastBranch() should report a list of changes
        self.assertEqual(
            self.__svn_revision_control_system.modified_paths_since_divergence(
                path=my_branch_path, tagged_url=my_new_directory_url
            ),
            ["abc"],
        )

    def test_modified_paths_since_divergence_with_property_change(self):
        # Create a directory via command-line client.
        my_new_directory_url = os.path.join(self._repository_url(), "my_new_directory")
        subversion.make_directory_in_repository(my_new_directory_url, "Made my_new_directory in repository.")

        # Create a branch via command-line client
        my_branch_url = os.path.join(self._repository_url(), "my_branch")
        subversion.copy(
            source_url=my_new_directory_url,
            destination_url=my_branch_url,
            message='Branched "my_branch" off of "my_trunk".',
        )

        # Check out branch
        my_branch_path = os.path.join(self._temporary_file_path(), "my_branch")
        subversion.check_out(url=my_branch_url, path=my_branch_path)

        subversion.property_set(
            path=my_branch_path,
            property_type="svn:ignore",
            property_value="blah",
        )
        subversion.commit(path=my_branch_path, message="")

        self.assertEqual(
            self.__svn_revision_control_system.modified_paths_since_divergence(
                path=my_branch_path, tagged_url=my_new_directory_url
            ),
            ["."],
        )

    def test_add_file(self):
        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=self._repository_url(), path=my_checkout_directory)

        my_new_file = path.join(my_checkout_directory, "my_new_file")
        with open(my_new_file, "w") as f:
            f.write("abc")
        self.__svn_revision_control_system.add_file(my_new_file)

        subversion.commit(path=my_new_file, message="")

        # Confirm by checkout out
        clean_checkout_directory = path.join(self._temporary_file_path(), "clean_checkout")
        subversion.check_out(url=self._repository_url(), path=clean_checkout_directory)
        os.path.exists(os.path.join(clean_checkout_directory, "my_new_file"))

    def test_add_file_twice_should_raise_exception(self):
        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=self._repository_url(), path=my_checkout_directory)

        my_new_file = path.join(my_checkout_directory, "my_new_file")
        with open(my_new_file, "w") as f:
            f.write("abc")
        self.__svn_revision_control_system.add_file(my_new_file)

        subversion.commit(path=my_new_file, message="")

        from yam import revision_control_system

        with self.assertRaises(revision_control_system.AlreadyUnderRevisionControl):
            self.__svn_revision_control_system.add_file(my_new_file)

    def test_add_file_should_raise_exception_if_already_under_revision_control(self):
        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=self._repository_url(), path=my_checkout_directory)

        my_new_file = path.join(my_checkout_directory, "my_new_file")
        with open(my_new_file, "w") as f:
            f.write("abc")
        self.__svn_revision_control_system.add_file(my_new_file)

        from yam import revision_control_system

        with self.assertRaises(revision_control_system.AlreadyUnderRevisionControl):
            self.__svn_revision_control_system.add_file(my_new_file)

    def test_interrupt(self):
        # We might be running in coverage mode. In such a case, we should run
        # the subprocess also in coverage mode.
        with open("/proc/{pid}/cmdline".format(pid=os.getpid()), "r") as f:
            if "coverage" in f.read():
                program_name = "coverage run --parallel-mode --branch"
            else:
                program_name = "python"

        # This is timing dependent so we may have to try more than once.
        interrupt_confirmed = False
        for _ in range(100):
            # /usr/bin/env is required. Otherwise, it will break when dtest is run
            # from a parent directory.
            p = spawnu(
                "/usr/bin/env {p} interrupt_test.py".format(p=program_name),
                timeout=None,
            )

            debug = False
            if debug:
                import sys

                p.logfile = sys.stdout

            # Wait until subprocess is ready to check in files
            p.expect("waiting")
            p.sendline("\n")

            # Send interrupt after subprocess starts checking in files
            import time

            time.sleep(0.01)
            p.sendintr()

            # Subprocess will print "OK" if interrupt was properly processed
            interrupt_confirmed = "OK" in p.read()
            if interrupt_confirmed:
                break

        self.assertTrue(interrupt_confirmed)


def normalize(text):
    """Return text with trailing whitespace removed on each line."""
    result = "\n".join([t.strip() for t in text.split("\n")])
    # Needed for newer Subversion versions.
    return result.replace("(nonexistent)", "(revision 0)")


class SVNRevisionControlSystemTestsWithNoMergeInfo(SVNRevisionControlSystemTests):
    """SVNRevisionControlSystemTests, but with use_merge_info set to False."""

    def _revision_control_system(self):
        """Override to set use_merge_info to False."""
        return svn_revision_control_system.SVNRevisionControlSystem(
            username=None,
            login_callback=lambda realm, username, may_save: (0, "", "", False),
            trust_ssl_server_callback=lambda trust_dict: (False, 0, False),
            use_merge_info=False,
            progress_callback=lambda current_bytes=-1, print_time_last=None: None,
        )

    def _create_repository(self, path):
        """Override to use older version of svnadmin.

        It will create a repository with no support of merge tracking.

        """
        subprocess.call(["svnadmin", "create", "--pre-1.4-compatible", path])

    def test_merge_info_should_raise_exception(self):
        from os import path

        my_checkout_directory = path.join(self._temporary_file_path(), "my_checkout")
        subversion.check_out(url=self._repository_url(), path=my_checkout_directory)

        # Create a directory via command-line client and commit it.
        my_new_directory = path.join(my_checkout_directory, "my_new_directory")
        subversion.make_directory(my_new_directory)
        subversion.commit(path=my_new_directory, message='Create directory "my_new_directory"')

        alpha_directory = path.join(my_checkout_directory, "alpha")
        subversion.make_directory(alpha_directory)
        subversion.commit(path=alpha_directory, message='Create directory "alpha"')

        # Files with changed properties should be listed as modified
        subversion.property_set(
            path=my_new_directory,
            property_type="svn:ignore",
            property_value="blah",
        )

        # Commit all files and test again
        subversion.commit(path=my_new_directory, message="Modify svn:ignore")

        revision_control_system = svn_revision_control_system.SVNRevisionControlSystem(
            username=None,
            login_callback=lambda realm, username, may_save: (0, "", "", False),
            trust_ssl_server_callback=lambda trust_dict: (False, 0, False),
            use_merge_info=True,
            progress_callback=lambda current_bytes=-1, print_time_last=None: None,
        )

        with self.assertRaises(yam_exception.YamException):
            revision_control_system.generate_logs_since_last_branch(path=my_checkout_directory)

        # But this should succeed (without merge info).
        revision_control_system = svn_revision_control_system.SVNRevisionControlSystem(
            username=None,
            login_callback=lambda realm, username, may_save: (0, "", "", False),
            trust_ssl_server_callback=lambda trust_dict: (False, 0, False),
            use_merge_info=False,
            progress_callback=lambda current_bytes=-1, print_time_last=None: None,
        )

        revision_control_system.generate_logs_since_last_branch(path=my_checkout_directory)


if __name__ == "__main__":
    unittest.main()
