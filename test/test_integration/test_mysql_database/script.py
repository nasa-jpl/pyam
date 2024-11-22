from __future__ import print_function

import sys
import unittest

from yam import database_writer


class Tests(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        # Create temporary directory where we will look for file to indicate
        # that the MySQL server is ready
        import tempfile

        self.__temporary_file_path = tempfile.mkdtemp(dir=".")
        import os

        ready_filename = os.path.join(self.__temporary_file_path, "ready")

        # Start MySQL server
        # Note that the server will be loaded with a known data set from
        # "../../common/mysql/example_yam_for_import.sql".
        import subprocess

        self.__mysql_process = subprocess.Popen(
            [
                "../../common/mysql/start_test_mysql_server.bash",
                "-r",
                ready_filename,
                "-s",
                "../../common/mysql/example_yam_for_import.sql",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        while True:
            if self.__mysql_process.poll():
                print(
                    "MySQL server died or did not start see below for " "stdout and stderr from server.",
                    file=sys.stderr,
                )
                print(self.__mysql_process.stdout.read(), file=sys.stderr)
                print(self.__mysql_process.stderr.read(), file=sys.stderr)
                raise IOError("MySQL server died")
            if os.path.exists(ready_filename):
                break
            import time

            time.sleep(0.1)

        with open(ready_filename) as ready_file:
            port = int(ready_file.readline())

        from yam import mysql_database_writer

        self.__sql_database_writer = mysql_database_writer.MySQLDatabaseWriter(
            hostname="127.0.0.1",
            port=port,
            username="",
            password="",
            database_name="test",
        )

        from yam import mysql_database_reader

        self.__sql_database_reader = mysql_database_reader.MySQLDatabaseReader(
            hostname="127.0.0.1",
            port=port,
            username="",
            password="",
            database_name="test",
            keyword_to_repository_dictionary={},
        )

    def tearDown(self):
        """Automatically called after each test* method."""
        # If the MySQL server died (due to error), print the server output
        if self.__mysql_process.poll():
            print(
                "MySQL server died or did not start see below for " "stdout and stderr from server.",
                file=sys.stderr,
            )
            print(self.__mysql_process.stdout.read(), file=sys.stderr)
            print(self.__mysql_process.stderr.read(), file=sys.stderr)
        else:
            # Terminate the process and wait for it to exit.
            self.__mysql_process.terminate()
            self.__mysql_process.wait(10)

        import shutil

        shutil.rmtree(path=self.__temporary_file_path, ignore_errors=True)

    def test_reading_of_appended_branch(self):
        self.assertEqual(
            self.__sql_database_reader.latest_module_information("DshellEnv")["branches"],
            "clim",
        )

        self.__sql_database_writer.append_branch(
            module_name="DshellEnv",
            revision_tag="R1-49r",
            branch_id="my_branch_id",
        )

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("DshellEnv")["branches"],
            "clim, my_branch_id",
        )

    def test_reading_of_renamed_branch(self):
        self.assertEqual(
            self.__sql_database_reader.latest_module_information("DshellEnv")["branches"],
            "clim",
        )

        self.__sql_database_writer.rename_branch(
            module_name="DshellEnv",
            revision_tag="R1-49r",
            branch_id="clim",
            new_branch_id="milk",
        )

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("DshellEnv")["branches"],
            "milk",
        )

    def test_reading_modified_module_history(self):
        import datetime

        self.assertEqual(
            self.__sql_database_reader.module_history(["AcmeModels"], 1, True, True, None)[0],
            {
                "datetime": datetime.datetime(2005, 12, 5, 9, 20, 23),
                "tag": "R3-47l",
                "build": None,
                "user": "jain",
                "name": "AcmeModels",
            },
        )

        self.__sql_database_writer.write_module_source_release_information(
            module_name="AcmeModels",
            revision_tag="R3-47m",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            changed_api_filename_list=["blah.h"],
            readmes=["ChangeLog"],
            num_files_changed=2,
            num_lines_added=11,
            num_lines_removed=998,
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_path",
            maintenance_name=None,
            maintenance_num=None,
        )

        self.assertEqual(
            self.__sql_database_reader.module_history(["AcmeModels"], 1, True, True, None)[0],
            {
                "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                "tag": "R3-47m",
                "build": None,
                "user": "steven",
                "name": "AcmeModels",
            },
        )

    def test_reading_modified_latest_module_information(self):
        import datetime

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("AcmeModels"),
            {
                "datetime": datetime.datetime(2006, 5, 31, 22, 40, 9),
                "tag": "R3-47l",
                "build": "05",
                "user": "jain",
                "branches": None,
            },
        )

        self.__sql_database_writer.write_module_source_release_information(
            module_name="AcmeModels",
            revision_tag="R3-47m",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            changed_api_filename_list=["blah.h"],
            readmes=["ChangeLog"],
            num_files_changed=2,
            num_lines_added=11,
            num_lines_removed=998,
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_path",
            maintenance_name=None,
            maintenance_num=None,
        )

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("AcmeModels"),
            {
                "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                "tag": "R3-47m",
                "build": None,
                "user": "steven",
                "branches": None,
            },
        )

    def test_reading_modified_latest_module_information_when_revision_is_greater_than9(self):
        import datetime

        self.__sql_database_writer.write_module_source_release_information(
            module_name="AcmeModels",
            revision_tag="R9-12a",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            changed_api_filename_list=["blah.h"],
            readmes=["ChangeLog"],
            num_files_changed=2,
            num_lines_added=11,
            num_lines_removed=998,
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_path",
            maintenance_name=None,
            maintenance_num=None,
        )

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("AcmeModels"),
            {
                "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                "tag": "R9-12a",
                "build": None,
                "user": "steven",
                "branches": None,
            },
        )

        self.__sql_database_writer.write_module_source_release_information(
            module_name="AcmeModels",
            revision_tag="R10-12a",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            changed_api_filename_list=["blah.h"],
            readmes=["ChangeLog"],
            num_files_changed=2,
            num_lines_added=11,
            num_lines_removed=998,
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_path",
            maintenance_name=None,
            maintenance_num=None,
        )

        # Make sure "number" in R<number> is being sorted first and numerically
        # (not alphabetically).
        self.assertEqual(
            self.__sql_database_reader.latest_module_information("AcmeModels"),
            {
                "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                "tag": "R10-12a",
                "build": None,
                "user": "steven",
                "branches": None,
            },
        )

    def test_reading_modified_latest_build_module_information(self):
        import datetime

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("AcmeModels"),
            {
                "datetime": datetime.datetime(2006, 5, 31, 22, 40, 9),
                "tag": "R3-47l",
                "build": "05",
                "user": "jain",
                "branches": None,
            },
        )

        self.__sql_database_writer.write_module_build_release_information(
            module_name="AcmeModels",
            revision_tag="R3-47l",
            build_id="99",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            readmes=[],
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_path",
        )

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("AcmeModels"),
            {
                "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                "tag": "R3-47l",
                "build": "99",
                "user": "steven",
                "branches": None,
            },
        )

        # Test '101' to make sure we are ordering the build IDs correctly (by
        # numeric order not alphabetic order)
        self.__sql_database_writer.write_module_build_release_information(
            module_name="AcmeModels",
            revision_tag="R3-47l",
            build_id="101",
            username="steven",
            date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            readmes=[],
            operating_system_name="my_operating_system",
            site_name="my_site",
            host_ip="my_host_ip",
            release_path="my_release_path",
        )

        self.assertEqual(
            self.__sql_database_reader.latest_module_information("AcmeModels"),
            {
                "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                "tag": "R3-47l",
                "build": "101",
                "user": "steven",
                "branches": None,
            },
        )

    def test_package_names(self):
        self.assertNotIn("FakePkg", self.__sql_database_reader.package_names())

        self.__sql_database_writer.register_new_package(package_name="FakePkg", repository_keyword=None)

        self.assertIn("FakePkg", self.__sql_database_reader.package_names())

        with self.assertRaises(database_writer.PackageAlreadyExistsException):
            self.__sql_database_writer.register_new_package(package_name="FakePkg", repository_keyword=None)

        self.__sql_database_writer.unregister_package(package_name="FakePkg")

        self.assertNotIn("FakePkg", self.__sql_database_reader.package_names())

        with self.assertRaises(database_writer.PackageAlreadyExistsException):
            self.__sql_database_writer.register_new_package(package_name="FakePkg", repository_keyword=None)

    def test_module_names(self):
        self.assertNotIn("FakeModule", self.__sql_database_reader.module_names())

        self.__sql_database_writer.register_new_module(
            module_name="FakeModule", repository_keyword=None, vcs_type="svn"
        )

        with self.assertRaises(database_writer.ModuleAlreadyExistsException):
            self.__sql_database_writer.register_new_module(
                module_name="FakeModule", repository_keyword=None, vcs_type="svn"
            )

        self.assertIn("FakeModule", self.__sql_database_reader.module_names())

        self.__sql_database_writer.unregister_module(module_name="FakeModule")

        self.assertNotIn("FakeModule", self.__sql_database_reader.package_names())

        with self.assertRaises(database_writer.ModuleAlreadyExistsException):
            self.__sql_database_writer.register_new_module(
                module_name="FakeModule", repository_keyword=None, vcs_type="svn"
            )

    def test_module_dependencies(self):
        self.assertEqual(
            set(
                [
                    "Dspace",
                    "SOA",
                    "CORE",
                    "DshellEnv",
                    "SimScape",
                    "DSoar",
                    "SimScapeBasic",
                    "Dshell++Scripts",
                ]
            ),
            self.__sql_database_reader.module_dependencies("DspaceTerrain"),
        )

        self.__sql_database_writer.write_build_dependencies(
            module_name="DspaceTerrain",
            dependency_dictionary={
                "Dshell++": {"Foo.h", "Bar.h"},
                "Dspace": {"Dspace.h"},
            },
        )

        self.assertEqual(
            set(["Dspace", "Dshell++"]),
            self.__sql_database_reader.module_dependencies("DspaceTerrain"),
        )

    def test_module_dependencies_is_well_behaved(self):
        original_dshell_dependencies = self.__sql_database_reader.module_dependencies("Dshell++")
        self.assertTrue(original_dshell_dependencies)

        self.assertEqual(
            set(
                [
                    "Dspace",
                    "SOA",
                    "CORE",
                    "DshellEnv",
                    "SimScape",
                    "DSoar",
                    "SimScapeBasic",
                    "Dshell++Scripts",
                ]
            ),
            self.__sql_database_reader.module_dependencies("DspaceTerrain"),
        )

        self.__sql_database_writer.write_build_dependencies(
            module_name="DspaceTerrain",
            dependency_dictionary={
                "Dshell++": {"Foo.h", "Bar.h"},
                "Dspace": {"Dspace.h"},
            },
        )

        # Make sure unrelated things are unaffected.
        self.assertEqual(
            original_dshell_dependencies,
            self.__sql_database_reader.module_dependencies("Dshell++"),
        )


if __name__ == "__main__":
    unittest.main()
