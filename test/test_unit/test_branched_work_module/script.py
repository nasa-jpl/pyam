import mockito
import unittest
import datetime

from yam import branched_work_module
from yam import savable_module
from yam import yam_exception


class BranchedWorkModuleTestCase(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        from yam import database_reader

        self.__mock_database_reader = mockito.mock(database_reader.DatabaseReader, strict=False)

        from yam import database_writer

        self.__mock_database_writer = mockito.mock(database_writer.DatabaseWriter, strict=False)

        from yam import revision_control_system

        self.__mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        from yam import file_system

        self.__mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

        from yam import build_system

        self.__mock_build_system = mockito.mock(build_system.BuildSystem, strict=False)

        # This unittest.TestCase attribute controls the maximum length of diffs
        # output by assert methods that report diffs on failure
        self.maxDiff = None

    def tearDown(self):
        """Automatically called after each test* method."""
        mockito.unstub()

    def test_check_out(self):
        # Set up expectations

        # Branch creation and related checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/releases/FakeModule-fake-tag"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-fake-tag-fake-branch"
        ).thenReturn(False)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-fake-tag-fake-branch"
        ).thenReturn(False)

        # Check if working copy already exists
        mockito.when(self.__mock_revision_control_system).working_copy_exists(
            path="fake_src_directory/FakeModule"
        ).thenReturn(False)

        # Check out code
        self.__mock_revision_control_system.check_out(
            source="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-fake-tag-fake-branch",
            target="fake_src_directory/FakeModule",
        )

        self.__mock_database_writer.append_branch(
            module_name="FakeModule",
            revision_tag="fake-tag",
            branch_id="fake-branch",
        )

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="fake-tag",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )
        module.check_out()

        # Verify
        mockito.verify(self.__mock_revision_control_system).branch(
            source_url="my_repository_url/Modules/FakeModule/releases/FakeModule-fake-tag",
            destination_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-fake-tag-fake-branch",
        )

    def test_check_out_should_raise_error_when_it_does_not_find_tag(self):
        # Pre-branch creation checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/releases/FakeModule-fake-tag"
        ).thenReturn(False)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="fake-tag",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        with self.assertRaises(yam_exception.YamException):
            module.check_out()

    def test_check_out_when_branch_already_exists_should_reuse_the_existing_branch(self):
        # Pre-branch creation checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/releases/FakeModule-fake-tag"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-fake-tag-fake-branch"
        ).thenReturn(False)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-fake-tag-fake-branch"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).working_copy_exists(
            path="fake_src_directory/FakeModule"
        ).thenReturn(False)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="fake-tag",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )
        module.check_out()

        # Verify
        mockito.verify(self.__mock_revision_control_system).check_out(
            source="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-fake-tag-fake-branch",
            target="fake_src_directory/FakeModule",
        )

    def test_check_out_should_raise_error_when_the_branch_is_dead(self):
        # Pre-branch creation checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/releases/FakeModule-fake-tag"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-fake-tag-fake-branch"
        ).thenReturn(True)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="fake-tag",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        with self.assertRaises(yam_exception.YamException):
            module.check_out()

    def test_save_module_instance(self):
        # Pre-save checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/YamVersion.h").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn(["blah/blah.h", "a/b/c.txt", "Me.h"])

        # Generate diff for release-information callback
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_revision_control_system).generate_diff(
            from_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
            to_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch",
            ignored_paths=(
                "ReleaseNotes",
                "ChangeLog",
                "YamVersion.h",
                "swig/docstrings.i",
            ),
        ).thenReturn(
            """Index: my_changed_file.txt
=======
--- previous release
+++ current release
@@ @@
- this line was removed as you can see by the - sign
+ this line was appended as you can see by the + sign
+ this blah line was appended
    blah"""
        )

        # Generate logs before reintegration
        mockito.when(self.__mock_revision_control_system).generate_logs_since_last_branch(
            path="fake_src_directory/FakeModule",
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        ).thenReturn(
            """FILES: Blah.py(240137)
Improved blah."""
        )

        # Reintegration into trunk
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        # ReleaseNotes
        mockito.when(self.__mock_file_system).read_file(
            filename="fake_src_directory/FakeModule/ReleaseNotes"
        ).thenReturn(
            """This
is the header.

Release R1-05z (2011-10-12 13:10:23):

\tThis is some existing entry.
"""
        )

        # ChangeLog
        mockito.when(self.__mock_file_system).read_file(filename="fake_src_directory/FakeModule/ChangeLog").thenReturn(
            """2011-10-12 13:10:23  steven

\t* Revision tag: R1-05z

\tFILES: Blah.py(240130)
\tImplemented blah.
"""
        )

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),
            ("R1-06", None),
        )

        # Verify
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

        mockito.verify(self.__mock_revision_control_system).reintegrate(
            path="fake_src_directory/FakeModule",
            original_url="my_repository_url/Modules/FakeModule/trunk",
            archive_url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule", log_message=mockito.any(str)
        )

        # Write YamVersion.h
        mockito.verify(self.__mock_file_system).write_to_file(
            string_data="""/**
 * YamVersion.h
 *
 * Header file that uses Dversion.h to provide functions to access
 * version information for a module
 */

/* make sure DVERSION macros are not already defined */
#ifdef DVERSION_CPREFIX
#undef DVERSION_CPREFIX
#endif
#ifdef DVERSION_MODULE
#undef DVERSION_MODULE
#endif
#ifdef DVERSION_RELEASE
#undef DVERSION_RELEASE
#endif

/* declare module-specific RELEASE macro for use by other modules */
#define FAKEMODULE_DVERSION_RELEASE "FakeModule-R1-06"

/* define DVERSION macros and include Dversion.h to declare functions */
#define DVERSION_CPREFIX FakeModule
#define DVERSION_MODULE "FakeModule"
#define DVERSION_RELEASE FAKEMODULE_DVERSION_RELEASE
#include "Dversion.h"
""",
            filename="fake_src_directory/FakeModule/YamVersion.h",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/YamVersion.h",
            log_message=mockito.any(str),
        )

        mockito.verify(self.__mock_file_system).write_to_file(
            string_data="""This
is the header.

Release R1-06 (2011-10-17 17:04:12):

\tMy release.

Release R1-05z (2011-10-12 13:10:23):

\tThis is some existing entry.
""",
            filename="fake_src_directory/FakeModule/ReleaseNotes",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/ReleaseNotes",
            log_message=mockito.any(str),
        )

        mockito.verify(self.__mock_file_system).write_to_file(
            string_data="""Mon Oct 17 17:04:12 2011  steven

\t* Revision tag: R1-06
\tTicket IDs: 54321

\tFILES: Blah.py(240137)
\tImproved blah.

2011-10-12 13:10:23  steven

\t* Revision tag: R1-05z

\tFILES: Blah.py(240130)
\tImplemented blah.
""",
            filename="fake_src_directory/FakeModule/ChangeLog",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/ChangeLog",
            log_message=mockito.any(str),
        )

        # Create branch in releases URL
        mockito.verify(self.__mock_revision_control_system).branch(
            source_url="my_repository_url/Modules/FakeModule/trunk",
            destination_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06",
        )

        # Update database with release information
        mockito.verify(self.__mock_database_writer).write_module_source_release_information(
            module_name="FakeModule",
            revision_tag="R1-06",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            changed_api_filename_list=["blah.h", "Me.h"],
            readmes=[],  # ['ChangeLog'],
            num_files_changed=1,
            num_lines_added=2,
            num_lines_removed=1,
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_directory",
            maintenance_name=None,
            maintenance_num=None,
        )

        # Switch working copy to releases URL
        mockito.verify(self.__mock_revision_control_system).switch_to_branch(
            path="fake_src_directory/FakeModule",
            branch_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06",
        )

        # Move to release area
        mockito.verify(self.__mock_file_system).move(
            source_path="fake_src_directory/FakeModule",
            destination_path="my_release_directory/Module-Releases/FakeModule/FakeModule-R1-06",
        )

        # Update symlink
        mockito.verify(self.__mock_file_system).symbolic_link(
            source="FakeModule-R1-06",
            link_name="my_release_directory/Module-Releases/FakeModule/Latest",
            progress_callback=mockito.any(),
        )

        # Add suffix "-DEAD" to dead branch in database
        mockito.verify(self.__mock_database_writer).rename_branch(
            module_name="FakeModule",
            revision_tag="R1-05z",
            branch_id="fake-branch",
            new_branch_id="fake-branch-DEAD",
        )

    def test_save_module_instance_with_merge_conflict(self):
        # Pre-save checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn(["blah/blah.h", "a/b/c.txt", "Me.h"])

        # Generate diff for release-information callback
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_revision_control_system).generate_diff(
            from_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
            to_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch",
            ignored_paths=(
                "ReleaseNotes",
                "ChangeLog",
                "YamVersion.h",
                "swig/docstrings.i",
            ),
        ).thenReturn(
            """Index: my_changed_file.txt
=======
--- previous release
+++ current release
@@ @@
- this line was removed as you can see by the - sign
+ this line was appended as you can see by the + sign
+ this blah line was appended
    blah"""
        )

        # Generate logs before reintegration
        mockito.when(self.__mock_revision_control_system).generate_logs_since_last_branch(
            path="fake_src_directory/FakeModule",
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        ).thenReturn(
            """FILES: Blah.py(240137)
Improved blah."""
        )

        # Reintegration into trunk
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        # ReleaseNotes
        mockito.when(self.__mock_file_system).read_file(
            filename="fake_src_directory/FakeModule/ReleaseNotes"
        ).thenReturn(
            """This
is the header.

Release R1-05z (2011-10-12 13:10:23):

\tThis is some existing entry.
"""
        )

        # ChangeLog
        mockito.when(self.__mock_file_system).read_file(filename="fake_src_directory/FakeModule/ChangeLog").thenReturn(
            """2011-10-12 13:10:23  steven

\t* Revision tag: R1-05z

\tFILES: Blah.py(240130)
\tImplemented blah.
"""
        )

        mockito.when(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule", log_message=mockito.any(str)
        ).thenRaise(yam_exception.YamException("blah"))

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        merge_conflict = None
        try:
            self.assertEqual(
                module.save(
                    release_note_message="My release.",
                    username="steven",
                    release_directory="my_release_directory",
                    keep_release=True,
                    changelogs_path="",
                    build_system=self.__mock_build_system,
                    operating_system_name="my_operating_system",
                    site_name="my_site",
                    host_ip="my_host_ip",
                    bug_id="54321",
                ),
                ("R1-06", None),
            )
        except branched_work_module.MergeConflict as exception:
            merge_conflict = exception

        self.assertTrue(merge_conflict)

    def test_save_module_instance_with_empty_release_note_message_and_no_bug_id(self):
        # Pre-save checks.
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/YamVersion.h").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn(["blah/blah.h"])

        # Generate diff for release-information callback
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_revision_control_system).generate_diff(
            from_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
            to_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch",
            ignored_paths=(
                "ReleaseNotes",
                "ChangeLog",
                "YamVersion.h",
                "swig/docstrings.i",
            ),
        ).thenReturn(
            """Index: my_changed_file.txt
=======
--- previous release
+++ current release
@@ @@
- this line was removed as you can see by the - sign
+ this line was appended as you can see by the + sign
+ this blah line was appended
    blah"""
        )

        mockito.when(self.__mock_revision_control_system).generate_logs_since_last_branch(
            path="fake_src_directory/FakeModule",
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        ).thenReturn(
            """FILES: Blah.py(240137)
Improved blah.

"""
        )

        # Reintegration into trunk
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_file_system).read_file(
            filename="fake_src_directory/FakeModule/ReleaseNotes"
        ).thenReturn(
            """This
is the header.

Release R1-05z (2011-10-17 17:04:12):

\tThis is some existing entry.

Release R1-05y (2011-10-12 13:10:23):

\tThis is an older entry.
"""
        )

        # ChangeLog
        mockito.when(self.__mock_file_system).read_file(filename="fake_src_directory/FakeModule/ChangeLog").thenReturn(
            """2011-10-12 13:10:23  steven

\t* Revision tag: R1-05z

\tFILES: Blah.py(240130)
\tImplemented blah.
"""
        )

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(
            module.save(
                release_note_message=None,
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
            ),
            ("R1-06", None),
        )

        # Verify
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

        # Reintegration into trunk
        mockito.verify(self.__mock_revision_control_system).reintegrate(
            path="fake_src_directory/FakeModule",
            original_url="my_repository_url/Modules/FakeModule/trunk",
            archive_url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule", log_message=mockito.any(str)
        )

        mockito.verify(self.__mock_file_system).write_to_file(
            string_data="""This
is the header.

Release R1-05z (2011-10-17 17:04:12):

\tThis is some existing entry.

Release R1-05y (2011-10-12 13:10:23):

\tThis is an older entry.
""",
            filename="fake_src_directory/FakeModule/ReleaseNotes",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/ReleaseNotes",
            log_message=mockito.any(str),
        )

        # Write YamVersion.h
        mockito.verify(self.__mock_file_system).write_to_file(
            string_data="""/**
 * YamVersion.h
 *
 * Header file that uses Dversion.h to provide functions to access
 * version information for a module
 */

/* make sure DVERSION macros are not already defined */
#ifdef DVERSION_CPREFIX
#undef DVERSION_CPREFIX
#endif
#ifdef DVERSION_MODULE
#undef DVERSION_MODULE
#endif
#ifdef DVERSION_RELEASE
#undef DVERSION_RELEASE
#endif

/* declare module-specific RELEASE macro for use by other modules */
#define FAKEMODULE_DVERSION_RELEASE "FakeModule-R1-06"

/* define DVERSION macros and include Dversion.h to declare functions */
#define DVERSION_CPREFIX FakeModule
#define DVERSION_MODULE "FakeModule"
#define DVERSION_RELEASE FAKEMODULE_DVERSION_RELEASE
#include "Dversion.h"
""",
            filename="fake_src_directory/FakeModule/YamVersion.h",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/YamVersion.h",
            log_message=mockito.any(str),
        )

        mockito.verify(self.__mock_file_system).write_to_file(
            string_data="""Mon Oct 17 17:04:12 2011  steven

\t* Revision tag: R1-06

\tFILES: Blah.py(240137)
\tImproved blah.

2011-10-12 13:10:23  steven

\t* Revision tag: R1-05z

\tFILES: Blah.py(240130)
\tImplemented blah.
""",
            filename="fake_src_directory/FakeModule/ChangeLog",
        )

        # Create branch in releases URL
        mockito.verify(self.__mock_revision_control_system).branch(
            source_url="my_repository_url/Modules/FakeModule/trunk",
            destination_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/ChangeLog",
            log_message=mockito.any(str),
        )

        # Update database with release information
        mockito.verify(self.__mock_database_writer).write_module_source_release_information(
            module_name="FakeModule",
            revision_tag="R1-06",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            changed_api_filename_list=["blah.h"],
            readmes=[],
            num_files_changed=1,
            num_lines_added=2,
            num_lines_removed=1,
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_directory",
            maintenance_name=None,
            maintenance_num=None,
        )

        # Switch working copy to (new) releases URL
        mockito.verify(self.__mock_revision_control_system).switch_to_branch(
            path="fake_src_directory/FakeModule",
            branch_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06",
        )

        # Move to release area
        mockito.verify(self.__mock_file_system).move(
            source_path="fake_src_directory/FakeModule",
            destination_path="my_release_directory/Module-Releases/FakeModule/FakeModule-R1-06",
        )

        # Update symlink
        mockito.verify(self.__mock_file_system).symbolic_link(
            source="FakeModule-R1-06",
            link_name="my_release_directory/Module-Releases/FakeModule/Latest",
            progress_callback=mockito.any(),
        )

        # Add suffix "-DEAD" to dead branch in database
        mockito.verify(self.__mock_database_writer).rename_branch(
            module_name="FakeModule",
            revision_tag="R1-05z",
            branch_id="fake-branch",
            new_branch_id="fake-branch-DEAD",
        )

    def test_save_module_instance_should_raise_error_when_not_files_are_uncommitted(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        # Return uncommitted changes so that save() raises an exception
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn(["my_uncommitted_file"])

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="fake-tag",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        from yam import revision_control_system

        with self.assertRaises(Exception):
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
            )

        # Verify
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

    def test_save_module_instance_should_raise_error_when_not_on_expected_repository_url(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        # Cause an error by returning a mismatched URL
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "totally_unrelated_repository_url"
        )

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="fake-tag",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        with self.assertRaises(savable_module.RepositoryURLMismatchError):
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
            )
        # Verify
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

    def test_save_module_instance_should_raise_error_when_not_on_latest_revision(self):
        # Set up the mock objects
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-fake-tag-fake-branch"
        )
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-fake-tag-fake-branch"
        ).thenReturn(False)

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "latest_revision"})

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="fake-tag",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        with self.assertRaises(branched_work_module.NotLatestRevisionError):
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
            )

        # Verify
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

    def test_save_module_instance_should_skip_non_existent_files(self):
        # Pre-save checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(
            False
        )
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(False)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/YamVersion.h").thenReturn(
            False
        )

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn(["blah/blah.h", "a/b/c.txt", "Me.h"])

        # Generate diff for release-information callback
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_revision_control_system).generate_diff(
            from_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
            to_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch",
            ignored_paths=(
                "ReleaseNotes",
                "ChangeLog",
                "YamVersion.h",
                "swig/docstrings.i",
            ),
        ).thenReturn(
            """Index: my_changed_file.txt
=======
--- previous release
+++ current release
@@ @@
- this line was removed as you can see by the - sign
+ this line was appended as you can see by the + sign
+ this blah line was appended
    blah"""
        )

        # Generate logs before reintegration
        mockito.when(self.__mock_revision_control_system).generate_logs_since_last_branch(
            path="fake_src_directory/FakeModule",
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        ).thenReturn(
            """FILES: Blah.py(240137)
Improved blah."""
        )

        # Reintegration into trunk
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        module.save(
            release_note_message="My release.",
            username="steven",
            release_directory="my_release_directory",
            keep_release=True,
            changelogs_path="",
            build_system=self.__mock_build_system,
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            bug_id="54321",
        ),

    def test_save_module_instance_should_raise_exception_when_there_is_no_release_directory(self):
        # Pre-save checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(False)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        with self.assertRaises(savable_module.PreSaveException):
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),

    def test_save_module_instance_should_raise_exception_when_no_changes_and_build_release_is_not_an_option(self):
        # Pre-save checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        with self.assertRaises(savable_module.PreSaveException):
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory=None,
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),

    def test_save_module_instance_should_raise_exception_when_dead_branch_already_exists(self):
        # Pre-save checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(True)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        with self.assertRaises(savable_module.PreSaveException):
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),

    def test_save_build_release(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"}).thenReturn({"build": "02"})

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn([])

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),
            ("R1-05z", "03"),
        )

        # Verify
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

        # Move to release area
        mockito.verify(self.__mock_file_system).move(
            source_path="fake_src_directory/FakeModule",
            destination_path="my_release_directory/Module-Releases/FakeModule/FakeModule-R1-05z-Build03",
        )

        # Update symlink
        mockito.verify(self.__mock_file_system).symbolic_link(
            source="FakeModule-R1-05z-Build03",
            link_name="my_release_directory/Module-Releases/FakeModule/Latest",
            progress_callback=mockito.any(),
        )

        # Update database with release information
        mockito.verify(self.__mock_database_writer).write_module_build_release_information(
            module_name="FakeModule",
            revision_tag="R1-05z",
            build_id="03",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            readmes=[],
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_directory",
        )

    def test_save_build_release_with_build_id_none(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"}).thenReturn({"build": None})

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn([])

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),
            ("R1-05z", "01"),
        )

        # Verify
        # Pre-save checks
        mockito.verify(self.__mock_database_reader, atleast=1).module_repository_url("FakeModule")
        mockito.verify(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule")
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

        # Move to release area
        mockito.verify(self.__mock_file_system).move(
            source_path="fake_src_directory/FakeModule",
            destination_path="my_release_directory/Module-Releases/FakeModule/FakeModule-R1-05z-Build01",
        )

        # Update symlink
        mockito.verify(self.__mock_file_system).symbolic_link(
            source="FakeModule-R1-05z-Build01",
            link_name="my_release_directory/Module-Releases/FakeModule/Latest",
            progress_callback=mockito.any(),
        )

        # Update database with release information
        mockito.verify(self.__mock_database_writer).write_module_build_release_information(
            module_name="FakeModule",
            revision_tag="R1-05z",
            build_id="01",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            readmes=[],
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_directory",
        )

    def test_save_build_release_with_build_greater_than100(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"}).thenReturn({"build": 100})

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn([])

        # Get current build ID
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),
            ("R1-05z", "101"),
        )

        # Verify
        mockito.verify(self.__mock_database_reader, atleast=1).module_repository_url("FakeModule")
        mockito.verify(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule")
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

        # Move to release area
        mockito.verify(self.__mock_file_system).move(
            source_path="fake_src_directory/FakeModule",
            destination_path="my_release_directory/Module-Releases/FakeModule/FakeModule-R1-05z-Build101",
        )

        # Update symlink
        mockito.verify(self.__mock_file_system).symbolic_link(
            source="FakeModule-R1-05z-Build101",
            link_name="my_release_directory/Module-Releases/FakeModule/Latest",
            progress_callback=mockito.any(),
        )

        # Update database with release information
        mockito.verify(self.__mock_database_writer).write_module_build_release_information(
            module_name="FakeModule",
            revision_tag="R1-05z",
            build_id="101",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            readmes=[],
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_directory",
        )

    def test_save_build_release_with_build_id_empty(self):
        # Pre-save checks
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )

        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"}).thenReturn({"build": ""})

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Get date
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        # Check if we can just do a build release
        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn([])

        # Get current build ID
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(
            module.save(
                release_note_message="My release.",
                username="steven",
                release_directory="my_release_directory",
                keep_release=True,
                changelogs_path="",
                build_system=self.__mock_build_system,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                bug_id="54321",
            ),
            ("R1-05z", "01"),
        )

        # Verify
        mockito.verify(self.__mock_revision_control_system).update(path="fake_src_directory/FakeModule")

        # Move to release area
        mockito.verify(self.__mock_file_system).move(
            source_path="fake_src_directory/FakeModule",
            destination_path="my_release_directory/Module-Releases/FakeModule/FakeModule-R1-05z-Build01",
        )

        # Update symlink
        mockito.verify(self.__mock_file_system).symbolic_link(
            source="FakeModule-R1-05z-Build01",
            link_name="my_release_directory/Module-Releases/FakeModule/Latest",
            progress_callback=mockito.any(),
        )

        # Update database with release information
        mockito.verify(self.__mock_database_writer).write_module_build_release_information(
            module_name="FakeModule",
            revision_tag="R1-05z",
            build_id="01",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            readmes=[],
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_directory",
        )

    def test_not_latest_revision_error(self):
        self.assertEqual(
            str(
                branched_work_module.NotLatestRevisionError(
                    module_name="MyModule",
                    current_revision_tag="old_revision",
                    latest_revision_tag="new_revision",
                )
            ),
            "Module 'MyModule' is on revision 'old_revision' instead of latest revision 'new_revision'; It needs to be synced up to the latest revision",
        )

    def test_repository_url_mismatch_error(self):
        self.assertEqual(
            str(savable_module.RepositoryURLMismatchError(expected_url="my_url_a", actual_url="my_url_b")),
            "Repository is expected to be 'my_url_a', but we instead see 'my_url_b' in the checked out directory",
        )

    def test_sync(self):
        # Pre-sync checks
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-06b"})
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Create a unique branch with the latest revision tag
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch"
        ).thenReturn(False)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06b"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-06b-fake-branch"
        ).thenReturn(False)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch"
        ).thenReturn(False)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(module.sync(commit=False), ("R1-06b", "fake-branch"))

        # Verify
        mockito.verify(self.__mock_revision_control_system, atleast=1).update(path="fake_src_directory/FakeModule")

        mockito.verify(self.__mock_revision_control_system).branch(
            destination_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch",
            source_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06b",
        )

        mockito.verify(self.__mock_database_writer).append_branch(
            module_name="FakeModule",
            revision_tag="R1-06b",
            branch_id="fake-branch",
        )

        # Reintegrate our changes into this new branch
        mockito.verify(self.__mock_revision_control_system).reintegrate(
            path="fake_src_directory/FakeModule",
            original_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch",
            archive_url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch",
        )

        # Remove old branch from database
        mockito.verify(self.__mock_database_writer).rename_branch(
            module_name="FakeModule",
            revision_tag="R1-05z",
            branch_id="fake-branch",
            new_branch_id="fake-branch-DEAD",
        )

    def test_sync_should_avoid_branch_collision(self):
        # Pre-sync checks
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-06b"})
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Create a unique branch with the latest revision tag
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1"
        ).thenReturn(False)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06b"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-06b-fake-branch1"
        ).thenReturn(False)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1"
        ).thenReturn(False)

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(module.sync(commit=True), ("R1-06b", "fake-branch1"))

        # Verify
        mockito.verify(self.__mock_revision_control_system, atleast=1).update(path="fake_src_directory/FakeModule")

        # Reintegrate our changes into this new branch
        mockito.verify(self.__mock_revision_control_system).reintegrate(
            path="fake_src_directory/FakeModule",
            original_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1",
            archive_url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch",
        )

        # Remove old branch from database
        mockito.verify(self.__mock_database_writer).rename_branch(
            module_name="FakeModule",
            revision_tag="R1-05z",
            branch_id="fake-branch",
            new_branch_id="fake-branch-DEAD",
        )

        mockito.verify(self.__mock_revision_control_system).branch(
            destination_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1",
            source_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06b",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule", log_message=mockito.any(str)
        )

        mockito.verify(self.__mock_database_writer).append_branch(
            module_name="FakeModule",
            revision_tag="R1-06b",
            branch_id="fake-branch1",
        )

    def test_sync_with_merge_conflict(self):
        # Pre-sync checks
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-06b"})
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])
        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-05z-fake-branch"
        )
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch"
        ).thenReturn(False)

        # Create a unique branch with the latest revision tag
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1"
        ).thenReturn(False)

        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06b"
        ).thenReturn(True)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-06b-fake-branch1"
        ).thenReturn(False)
        mockito.when(self.__mock_revision_control_system).exists(
            url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1"
        ).thenReturn(False)

        mockito.when(self.__mock_revision_control_system).check_in(
            path=mockito.any(str), log_message=mockito.any(str)
        ).thenRaise(yam_exception.YamException("blah"))

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(module.sync(commit=True), ("R1-06b", "fake-branch1"))

        # Verify
        mockito.verify(self.__mock_revision_control_system, atleast=1).update(path="fake_src_directory/FakeModule")

        # Reintegrate our changes into this new branch
        mockito.verify(self.__mock_revision_control_system).reintegrate(
            path="fake_src_directory/FakeModule",
            original_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1",
            archive_url="my_repository_url/Modules/FakeModule/deadBranches/FakeModule-R1-05z-fake-branch",
        )

        # Remove old branch from database
        mockito.verify(self.__mock_database_writer).rename_branch(
            module_name="FakeModule",
            revision_tag="R1-05z",
            branch_id="fake-branch",
            new_branch_id="fake-branch-DEAD",
        )

        mockito.verify(self.__mock_revision_control_system).branch(
            destination_url="my_repository_url/Modules/FakeModule/featureBranches/FakeModule-R1-06b-fake-branch1",
            source_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06b",
        )

        mockito.verify(self.__mock_database_writer).append_branch(
            module_name="FakeModule",
            revision_tag="R1-06b",
            branch_id="fake-branch1",
        )

    def test_sync_should_do_nothing_if_already_in_sync(self):
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})

        # Make calls
        module = branched_work_module.BranchedWorkModule(
            module_name="FakeModule",
            tag="R1-05z",
            branch_id="fake-branch",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )

        self.assertEqual(module.sync(commit=False), ("R1-05z", "fake-branch"))
        # Verify
        mockito.verify(self.__mock_database_reader).latest_module_information(module_name="FakeModule", release=None)
        mockito.verifyNoMoreInteractions(self.__mock_revision_control_system)
        mockito.verifyNoMoreInteractions(self.__mock_database_reader)
        mockito.verifyNoMoreInteractions(self.__mock_database_writer)
        mockito.verifyNoMoreInteractions(self.__mock_file_system)

    def test_filter_legal_branch_id(self):
        self.assertEqual(branched_work_module.filter_legal_branch_id("abc-123"), "abc-123")

        self.assertEqual(branched_work_module.filter_legal_branch_id("abc_123"), "abc_123")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("abc 123")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("abc/123")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("abc/123")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("abc,123")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("abc\n123")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("abc\t123")

        with self.assertRaises(yam_exception.YamException):
            branched_work_module.filter_legal_branch_id("abc-DEAD")


if __name__ == "__main__":
    unittest.main()
