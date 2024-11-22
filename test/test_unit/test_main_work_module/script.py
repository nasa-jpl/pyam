import datetime
import unittest

import mockito

from yam import main_work_module
from yam import savable_module


class MainWorkModuleTestCase(unittest.TestCase):
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

    def tearDown(self):
        """Automatically called after each test* method."""
        mockito.unstub()

    def test_check_out(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_revision_control_system).working_copy_exists(
            path="fake_src_directory/FakeModule"
        ).thenReturn(False)

        # Make calls
        module = main_work_module.MainWorkModule(
            module_name="FakeModule",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
            database_reader=self.__mock_database_reader,
            database_writer=self.__mock_database_writer,
            file_system=self.__mock_file_system,
        )
        module.check_out()

        # Verify
        mockito.verify(self.__mock_revision_control_system).check_out(
            source="my_repository_url/Modules/FakeModule/trunk",
            target="fake_src_directory/FakeModule",
        )

    def test_save(self):
        # Pre-save checks
        # We don't care about what order these are called with respect to each
        # other.
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/trunk"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(module_name="FakeModule").thenReturn(
            {"tag": "R1-05z"}
        )

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/YamVersion.h").thenReturn(True)

        mockito.when(self.__mock_file_system).path_exists("my_release_directory").thenReturn(True)

        # Generate date time
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_database_reader).local_date_time().thenReturn(
            datetime.datetime(2011, 10, 17, 17, 4, 12)
        )

        mockito.when(self.__mock_revision_control_system).modified_paths_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
        ).thenReturn(["blah/blah.h", "a/b/c.txt"])

        # Generate diff for release-information callback
        mockito.when(self.__mock_revision_control_system).generate_diff(
            from_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
            to_url="my_repository_url/Modules/FakeModule/trunk",
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

        # Write YamVersion.h
        mockito.when(self.__mock_file_system).write_to_file(
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

        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"})

        mockito.when(self.__mock_revision_control_system).generate_logs_since_divergence(
            path="fake_src_directory/FakeModule",
            tagged_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-05z",
            ignored_paths=("ReleaseNotes", "ChangeLog", "YamVersion.h"),
        ).thenReturn(
            """FILES: Blah.py(240137)
Improved blah."""
        )

        # Create branch in releases URL
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        # Make calls
        module = main_work_module.MainWorkModule(
            module_name="FakeModule",
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

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/YamVersion.h",
            log_message="pyam: Update revision tag",
        )

        mockito.verify(self.__mock_revision_control_system).check_in(
            path="fake_src_directory/FakeModule/ReleaseNotes",
            log_message="pyam: Add a release note entry",
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
            log_message="pyam: Add a change log entry",
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

        # Switch working copy to releases URL
        mockito.verify(self.__mock_revision_control_system).switch_to_branch(
            path="fake_src_directory/FakeModule",
            branch_url="my_repository_url/Modules/FakeModule/releases/FakeModule-R1-06",
        )

        # Move to release area
        mockito.when(self.__mock_file_system).move(
            source_path="fake_src_directory/FakeModule",
            destination_path="my_release_directory/Module-Releases/FakeModule/FakeModule-R1-06",
        )

        # Update symlink
        mockito.when(self.__mock_file_system).symbolic_link(
            source="FakeModule-R1-06",
            link_name="my_release_directory/Module-Releases/FakeModule/Latest",
            progress_callback=mockito.any(),
        )

    def test_save_build_release(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/trunk"
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
        module = main_work_module.MainWorkModule(
            module_name="FakeModule",
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
            "my_repository_url/Modules/FakeModule/trunk"
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
        module = main_work_module.MainWorkModule(
            module_name="FakeModule",
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

    def test_save_build_release_should_raise_exception_when_build_release_is_not_an_option(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("my_repository_url")

        mockito.when(self.__mock_revision_control_system).uncommitted_files(
            path="fake_src_directory/FakeModule"
        ).thenReturn([])

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "my_repository_url/Modules/FakeModule/trunk"
        )

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule", release=None
        ).thenReturn({"tag": "R1-05z"}).thenReturn({"build": "02"})

        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ReleaseNotes").thenReturn(True)
        mockito.when(self.__mock_file_system).path_exists("fake_src_directory/FakeModule/ChangeLog").thenReturn(True)

        # Make calls
        module = main_work_module.MainWorkModule(
            module_name="FakeModule",
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
            )


if __name__ == "__main__":
    unittest.main()
