from __future__ import print_function

import unittest
import contextlib

from mysql import connector

from yam import mysql_database_writer
from yam import mysql_database_utils


@contextlib.contextmanager
def server_context(load_tables_from_file=True):
    """MySQL database server context.

    If load_tables_from_file is True, table data will be loaded from
    "../../common/mysql/example_yam_for_import.sql".

    """
    # Create temporary directory where we will look for file to indicate that
    # the MySQL server is ready
    import tempfile

    temporary_file_path = tempfile.mkdtemp(dir=".")
    import os

    ready_filename = os.path.join(temporary_file_path, "ready")

    # Start MySQL server
    if load_tables_from_file:
        data_filename = "../../common/mysql/example_yam_for_import.sql"
    else:
        data_filename = "/dev/null"

    import subprocess

    mysql_process = subprocess.Popen(
        [
            "../../common/mysql/start_test_mysql_server.bash",
            "-r",
            ready_filename,
            "-s",
            data_filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    while True:
        if mysql_process.poll():
            print("MySQL server died or did not start see below for stdout and stderr from server.")
            print(mysql_process.stdout.read())
            print(mysql_process.stderr.read())
            raise IOError("MySQL server died")
        if os.path.exists(ready_filename):
            break
        import time

        time.sleep(0.1)

    with open(ready_filename) as ready_file:
        port = int(ready_file.readline())

    with mysql_database_writer.MySQLDatabaseWriter(
        hostname="127.0.0.1",
        port=port,
        username="",
        password="",
        database_name="test",
    ) as writer:

        yield (port, writer)

        # If the MySQL server died (due to error), print the server output
        if mysql_process.poll():
            print("MySQL server died or did not start see below for stdout and stderr from server.")
            print(mysql_process.stdout.read())
            print(mysql_process.stderr.read())
        else:
            mysql_process.stdout.close()
            mysql_process.stderr.close()
            mysql_process.terminate()

        import shutil

        shutil.rmtree(path=temporary_file_path, ignore_errors=True)


class Tests(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        self.maxDiff = 2000

    def tearDown(self):
        """Automatically called after each test* method."""

    def test_invalid_connection_should_raise_exception(self):
        with server_context() as (port, _):
            from yam import database

            with self.assertRaises(database.ConnectionException):
                writer = mysql_database_writer.MySQLDatabaseWriter(
                    hostname="127.0.0.1",
                    port=port,
                    username="",
                    password="",
                    database_name="non_existent",
                )

                writer.append_branch(
                    module_name="DshellEnv",
                    revision_tag="R1-49r",
                    branch_id="my_branch_id",
                )

            with self.assertRaises(database.ConnectionException):
                writer = mysql_database_writer.MySQLDatabaseWriter(
                    hostname="227.0.0.2",
                    port=port,
                    username="",
                    password="",
                    database_name="test",
                )

                writer.append_branch(
                    module_name="DshellEnv",
                    revision_tag="R1-49r",
                    branch_id="my_branch_id",
                )

    def test_append_branch(self):
        with server_context() as (port, writer):
            # Get row count for later sanity check
            old_row_count = row_count("modpkgReleases", port=port)

            # The branch we plan to append isn't already in the 'branches'
            # column
            relid = 15340
            self.assertNotIn("my_branch_id", retrieve_branch_list(relid=relid, port=port))

            writer.append_branch(
                module_name="DshellEnv",
                revision_tag="R1-49r",
                branch_id="my_branch_id",
            )

            # Our new branch should now show up in the row
            self.assertIn("my_branch_id", retrieve_branch_list(relid=relid, port=port))

            # Number of rows shouldn't change since we merely updated an
            # existing row
            self.assertEqual(old_row_count, row_count("modpkgReleases", port=port))

    def test_append_branch_non_existent_module_should_raise_exception(self):
        with server_context() as (port, writer):
            from yam import yam_exception

            with self.assertRaises(yam_exception.YamException):
                writer.append_branch(
                    module_name="NonExistentModule",
                    revision_tag="R1-49r",
                    branch_id="my_branch_id",
                )

    def test_rename_branch(self):
        with server_context() as (port, writer):
            # Get row count for later sanity check
            old_row_count = row_count("modpkgReleases", port=port)

            # Check current state of branches string
            relid = 1531
            self.assertEqual(
                ["dbreda", "shuim"],
                retrieve_branch_list(relid=relid, port=port),
            )

            # Run the rename
            writer.rename_branch(
                module_name="Dshtao++",
                revision_tag="R1-04",
                branch_id="shuim",
                new_branch_id="blah",
            )

            # Our renamed branch should now show up in the row
            self.assertEqual(retrieve_branch_list(relid=relid, port=port), ["dbreda", "blah"])

            # Partial match should do nothing
            writer.rename_branch(
                module_name="Dshtao++",
                revision_tag="R1-04",
                branch_id="dbr",
                new_branch_id="should_not_appear",
            )

            # Should stay the same
            self.assertEqual(retrieve_branch_list(relid=relid, port=port), ["dbreda", "blah"])

            # Now actually rename dbreda
            writer.rename_branch(
                module_name="Dshtao++",
                revision_tag="R1-04",
                branch_id="dbreda",
                new_branch_id="dbreda-hello",
            )

            # Should stay the same
            self.assertEqual(
                retrieve_branch_list(relid=relid, port=port),
                ["dbreda-hello", "blah"],
            )

            # Number of rows shouldn't change since we merely updated an
            # existing row
            self.assertEqual(old_row_count, row_count("modpkgReleases", port=port))

    def test_rename_branch_non_existent_module_should_raise_exception(self):
        with server_context() as (_, writer):
            from yam import yam_exception

            with self.assertRaises(yam_exception.YamException):
                writer.rename_branch(
                    module_name="NonExistentModule",
                    revision_tag="R1-49r",
                    branch_id="my_branch_id",
                    new_branch_id="blah",
                )

    def test_write_module_source_release_information(self):
        with server_context() as (port, writer):
            import datetime

            writer.write_module_source_release_information(
                module_name="Dshtao++",
                revision_tag="R7-01a",
                username="steven",
                date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
                changed_api_filename_list=[],
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

            row0 = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(
                row0,
                {
                    "tag": "R7-01a",
                    "site": 35,
                    "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                    "overallLOC": 1009,
                    "yamNative": 41,
                    "obsoletionCount": 0,
                    "relnum": 41,
                    "nrelatives": 0,
                    "addedLOC": 11,
                    "build": None,
                    "type": "SOURCE",
                    "apiChangedFiles": "",
                    "relid": 15376,
                    "changedLOC": 0,
                    "readmes": "ChangeLog",
                    "host": 50,
                    "user": "steven",
                    "path": 36,
                    "existing": "TRUE",
                    "removedLOC": 998,
                    "branches": None,
                    "modpkgId": 75,
                    "filesChanged": 2,
                    "maintBranch": None,
                    "maintNum": None,
                },
            )

            # Make sure that the data in modulePackages also got updated
            # properly.
            module_packages_row = retrieve_row(
                table_name="modulePackages",
                key="name",
                value="Dshtao++",
                port=port,
            )
            self.assertEqual(row0["relnum"], module_packages_row["Nreleases"])
            self.assertEqual(row0["relid"], module_packages_row["latestRelid"])
            self.assertEqual(row0["relid"], module_packages_row["latestSourceRelid"])

            # Try again with same values for some columns. Make sure IDs for
            # unique things stay the same.
            writer.write_module_source_release_information(
                module_name="Dshtao++",
                revision_tag="R7-01b",
                username="steven",
                date_time=datetime.datetime(2011, 11, 17, 17, 4, 12),
                changed_api_filename_list=["blah.h", "a.h"],
                readmes=["ChangeLog"],
                num_files_changed=1,
                num_lines_added=1,
                num_lines_removed=1,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                release_path="my_release_path",
                maintenance_name=None,
                maintenance_num=None,
            )

            row1 = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(
                row1,
                {
                    "tag": "R7-01b",
                    "site": 35,
                    "datetime": datetime.datetime(2011, 11, 17, 17, 4, 12),
                    "overallLOC": 2,
                    "yamNative": 41,
                    "obsoletionCount": 0,
                    "relnum": 42,
                    "nrelatives": 0,
                    "addedLOC": 1,
                    "build": None,
                    "type": "SOURCE",
                    "apiChangedFiles": "blah.h,a.h",
                    "relid": 15377,
                    "changedLOC": 0,
                    "readmes": "ChangeLog",
                    "host": 50,
                    "user": "steven",
                    "path": 36,
                    "existing": "TRUE",
                    "removedLOC": 1,
                    "branches": None,
                    "modpkgId": 75,
                    "filesChanged": 1,
                    "maintBranch": None,
                    "maintNum": None,
                },
            )

            self.assertEqual(row0["relnum"] + 1, row1["relnum"])

            self.assertEqual(row0["host"], row1["host"])

            self.assertEqual(row0["yamNative"], row1["yamNative"])

            self.assertEqual(row0["site"], row1["site"])

            self.assertEqual(row0["path"], row1["path"])

            # Make sure that the data in modulePackages also got updated
            # properly.
            module_packages_row = retrieve_row(
                table_name="modulePackages",
                key="name",
                value="Dshtao++",
                port=port,
            )
            self.assertEqual(row1["relnum"], module_packages_row["Nreleases"])
            self.assertEqual(row1["relid"], module_packages_row["latestRelid"])
            self.assertEqual(row1["relid"], module_packages_row["latestSourceRelid"])

            # Try again with new value. Make sure IDs increment for the things
            # that changed.
            writer.write_module_source_release_information(
                module_name="Dshtao++",
                revision_tag="R7-01c",
                username="steven",
                date_time=datetime.datetime(2011, 12, 17, 17, 4, 12),
                changed_api_filename_list=[],
                readmes=["ChangeLog"],
                num_files_changed=1,
                num_lines_added=1,
                num_lines_removed=1,
                operating_system_name="my_different_operating_system",
                site_name="my_different_site",
                host_ip="my_different_host_ip",
                release_path="my_different_release_path",
                maintenance_name=None,
                maintenance_num=None,
            )

            row2 = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(
                row2,
                {
                    "tag": "R7-01c",
                    "site": 36,
                    "datetime": datetime.datetime(2011, 12, 17, 17, 4, 12),
                    "overallLOC": 2,
                    "yamNative": 42,
                    "obsoletionCount": 0,
                    "relnum": 43,
                    "nrelatives": 0,
                    "addedLOC": 1,
                    "build": None,
                    "type": "SOURCE",
                    "apiChangedFiles": "",
                    "relid": 15378,
                    "changedLOC": 0,
                    "readmes": "ChangeLog",
                    "host": 51,
                    "user": "steven",
                    "path": 37,
                    "existing": "TRUE",
                    "removedLOC": 1,
                    "branches": None,
                    "modpkgId": 75,
                    "filesChanged": 1,
                    "maintBranch": None,
                    "maintNum": None,
                },
            )

            self.assertEqual(row1["relnum"] + 1, row2["relnum"])

            self.assertEqual(row1["host"] + 1, row2["host"])

            self.assertEqual(row1["yamNative"] + 1, row2["yamNative"])

            self.assertEqual(row1["site"] + 1, row2["site"])

            self.assertEqual(row1["path"] + 1, row2["path"])

            # Make sure that the data in modulePackages also got updated
            # properly.
            module_packages_row = retrieve_row(
                table_name="modulePackages",
                key="name",
                value="Dshtao++",
                port=port,
            )
            self.assertEqual(row2["relnum"], module_packages_row["Nreleases"])
            self.assertEqual(row2["relid"], module_packages_row["latestRelid"])
            self.assertEqual(row2["relid"], module_packages_row["latestSourceRelid"])

    def test_write_module_source_release_information_should_mark_dependent_builds_as_obsolete(self):
        with server_context() as (port, writer):
            # In the database, DspaceTerrain depends on Dspace's
            # dsGraphicsObject.H file
            modify_obsoletion_count(relid=15371, obsoletion_count=0, port=port)
            self.assertEqual(retrieve_obsoletion_count(relid=15371, port=port), 0)

            import datetime

            writer.write_module_source_release_information(
                module_name="Dspace",
                revision_tag="R7-01a",
                username="steven",
                date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
                changed_api_filename_list=["dsGraphicsObject.H"],
                readmes=["ChangeLog"],
                num_files_changed=1,
                num_lines_added=11,
                num_lines_removed=998,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                release_path="my_release_path",
                maintenance_name=None,
                maintenance_num=None,
            )

            # Dspace changing should result in the latest release of dependent
            # module DspaceTerrain being marked as obsolete
            self.assertEqual(retrieve_obsoletion_count(relid=15371, port=port), 2)

            # Dspace should not be marked since there is a release directory.
            row = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(0, row["obsoletionCount"])

    def test_write_module_source_release_information_should_mark_release_as_obsolete_build_if_no_release_path(self):
        with server_context() as (port, writer):
            # In the database, DspaceTerrain depends on Dspace's
            # dsGraphicsObject.H file
            modify_obsoletion_count(relid=15371, obsoletion_count=0, port=port)
            self.assertEqual(retrieve_obsoletion_count(relid=15371, port=port), 0)

            import datetime

            writer.write_module_source_release_information(
                module_name="Dspace",
                revision_tag="R7-01a",
                username="steven",
                date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
                changed_api_filename_list=["dsGraphicsObject.H"],
                readmes=["ChangeLog"],
                num_files_changed=1,
                num_lines_added=11,
                num_lines_removed=998,
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                release_path=None,
                maintenance_name=None,
                maintenance_num=None,
            )

            # Dspace changing should result in the latest release of dependent
            # module DspaceTerrain being marked as obsolete
            self.assertEqual(retrieve_obsoletion_count(relid=15371, port=port), 2)

            # Dspace should be marked too since there is no release directory.
            row = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(0, row["obsoletionCount"])

    def test_write_module_build_release_information(self):
        with server_context() as (port, writer):
            import datetime

            writer.write_module_build_release_information(
                module_name="Dshtao++",
                revision_tag="R7-01a",
                build_id="01",
                username="steven",
                date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
                readmes=[],
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                release_path="my_release_path",
            )

            row0 = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(
                row0,
                {
                    "tag": "R7-01a",
                    "site": 35,
                    "datetime": datetime.datetime(2011, 10, 17, 17, 4, 12),
                    "overallLOC": 0,
                    "yamNative": 41,
                    "obsoletionCount": 0,
                    "relnum": 41,
                    "nrelatives": 0,
                    "addedLOC": 0,
                    "build": "01",
                    "type": "BUILD",
                    "apiChangedFiles": None,
                    "relid": 15376,
                    "changedLOC": 0,
                    "readmes": "",
                    "host": 50,
                    "user": "steven",
                    "path": 36,
                    "existing": "TRUE",
                    "removedLOC": 0,
                    "branches": None,
                    "modpkgId": 75,
                    "filesChanged": 0,
                    "maintBranch": None,
                    "maintNum": None,
                },
            )

            # Make sure that the data in modulePackages also got updated
            # properly.
            module_packages_row = retrieve_row(
                table_name="modulePackages",
                key="name",
                value="Dshtao++",
                port=port,
            )
            self.assertEqual(row0["relnum"], module_packages_row["Nreleases"])
            self.assertEqual(row0["relid"], module_packages_row["latestRelid"])

            # Release ID should be higher than source release ID now, since we
            # did a build release
            self.assertGreater(
                module_packages_row["latestRelid"],
                module_packages_row["latestSourceRelid"],
            )

            # Try again with same values for some columns. Make sure IDs for
            # unique things stay the same.
            writer.write_module_build_release_information(
                module_name="Dshtao++",
                revision_tag="R7-01a",
                build_id="02",
                username="steven",
                date_time=datetime.datetime(2011, 11, 17, 17, 4, 12),
                readmes=[],
                operating_system_name="my_operating_system",
                site_name="my_site",
                host_ip="my_host_ip",
                release_path="my_release_path",
            )

            row1 = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(
                row1,
                {
                    "tag": "R7-01a",
                    "site": 35,
                    "datetime": datetime.datetime(2011, 11, 17, 17, 4, 12),
                    "overallLOC": 0,
                    "yamNative": 41,
                    "obsoletionCount": 0,
                    "relnum": 42,
                    "nrelatives": 0,
                    "addedLOC": 0,
                    "build": "02",
                    "type": "BUILD",
                    "apiChangedFiles": None,
                    "relid": 15377,
                    "changedLOC": 0,
                    "readmes": "",
                    "host": 50,
                    "user": "steven",
                    "path": 36,
                    "existing": "TRUE",
                    "removedLOC": 0,
                    "branches": None,
                    "modpkgId": 75,
                    "filesChanged": 0,
                    "maintBranch": None,
                    "maintNum": None,
                },
            )

            self.assertEqual(row0["relnum"] + 1, row1["relnum"])

            self.assertEqual(row0["host"], row1["host"])

            self.assertEqual(row0["yamNative"], row1["yamNative"])

            self.assertEqual(row0["site"], row1["site"])

            self.assertEqual(row0["path"], row1["path"])

            # Make sure that the data in modulePackages also got updated
            # properly.
            module_packages_row = retrieve_row(
                table_name="modulePackages",
                key="name",
                value="Dshtao++",
                port=port,
            )
            self.assertEqual(row1["relnum"], module_packages_row["Nreleases"])
            self.assertEqual(row1["relid"], module_packages_row["latestRelid"])

            # Release ID should be higher than source release ID now, since we
            # did a build release
            self.assertGreater(
                module_packages_row["latestRelid"],
                module_packages_row["latestSourceRelid"],
            )

            # Try again with new value. Make sure IDs increment for the things
            # that changed.
            writer.write_module_build_release_information(
                module_name="Dshtao++",
                revision_tag="R7-01a",
                build_id="03",
                username="steven",
                date_time=datetime.datetime(2011, 12, 17, 17, 4, 12),
                readmes=[],
                operating_system_name="my_different_operating_system",
                site_name="my_different_site",
                host_ip="my_different_host_ip",
                release_path="my_different_release_path",
            )

            row2 = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual(
                row2,
                {
                    "tag": "R7-01a",
                    "site": 36,
                    "datetime": datetime.datetime(2011, 12, 17, 17, 4, 12),
                    "overallLOC": 0,
                    "yamNative": 42,
                    "obsoletionCount": 0,
                    "relnum": 43,
                    "nrelatives": 0,
                    "addedLOC": 0,
                    "build": "03",
                    "type": "BUILD",
                    "apiChangedFiles": None,
                    "relid": 15378,
                    "changedLOC": 0,
                    "readmes": "",
                    "host": 51,
                    "user": "steven",
                    "path": 37,
                    "existing": "TRUE",
                    "removedLOC": 0,
                    "branches": None,
                    "modpkgId": 75,
                    "filesChanged": 0,
                    "maintBranch": None,
                    "maintNum": None,
                },
            )

            self.assertEqual(row1["relnum"] + 1, row2["relnum"])

            self.assertEqual(row1["host"] + 1, row2["host"])

            self.assertEqual(row1["yamNative"] + 1, row2["yamNative"])

            self.assertEqual(row1["site"] + 1, row2["site"])

            self.assertEqual(row1["path"] + 1, row2["path"])

            # Make sure that the data in modulePackages also got updated
            # properly.
            module_packages_row = retrieve_row(
                table_name="modulePackages",
                key="name",
                value="Dshtao++",
                port=port,
            )
            self.assertEqual(row2["relnum"], module_packages_row["Nreleases"])
            self.assertEqual(row2["relid"], module_packages_row["latestRelid"])

            # Release ID should be higher than source release ID now, since we
            # did a build release
            self.assertGreater(
                module_packages_row["latestRelid"],
                module_packages_row["latestSourceRelid"],
            )

    def test_write_package_release_information(self):
        with server_context() as (port, writer):
            import datetime

            writer.write_package_release_information(
                package_name="ROAMSDshellPkg",
                link_modules={},  # should really fill this out for relatives data
                revision_tag="R9-99a",
                username="steven",
                date_time=datetime.datetime(2011, 10, 17, 17, 4, 12),
            )

            row0 = retrieve_last_row(table_name="modpkgReleases", primary_key="relid", port=port)
            self.assertEqual("R9-99a", row0["tag"])
            self.assertEqual("steven", row0["user"])
            self.assertEqual(datetime.datetime(2011, 10, 17, 17, 4, 12), row0["datetime"])

            # Make sure that the data in modulePackages also got updated
            # properly.
            module_packages_row = retrieve_row(
                table_name="modulePackages",
                key="name",
                value="ROAMSDshellPkg",
                port=port,
            )
            self.assertEqual(row0["relnum"], module_packages_row["Nreleases"])
            self.assertEqual(row0["relid"], module_packages_row["latestRelid"])
            self.assertEqual(row0["relid"], module_packages_row["latestSourceRelid"])

    def test_register_new_module(self):
        with server_context() as (port, writer):
            self.assertNotEqual(
                retrieve_last_row(table_name="modulePackages", primary_key="id", port=port)["name"],
                "MyNewModule",
            )

            writer.register_new_module(
                module_name="MyNewModule",
                repository_keyword="my_repository_keyword",
            )

            last_row = retrieve_last_row(table_name="modulePackages", primary_key="id", port=port)

            self.assertEqual(last_row["name"], "MyNewModule")
            self.assertEqual(last_row["type"], "MODULE")
            self.assertEqual(last_row["repository"], "my_repository_keyword")

            self.assertFalse(last_row["Nreleases"])
            self.assertFalse(last_row["latestRelid"])
            self.assertFalse(last_row["latestSourceRelid"])

            from yam import database_writer

            with self.assertRaises(database_writer.ModuleAlreadyExistsException):
                writer.register_new_module(
                    module_name="MyNewModule",
                    repository_keyword="my_repository_keyword",
                )

    def test_register_new_module_with_no_keyword(self):
        with server_context() as (port, writer):
            self.assertNotEqual(
                retrieve_last_row(table_name="modulePackages", primary_key="id", port=port)["name"],
                "MyNewModule",
            )

            writer.register_new_module(module_name="MyNewModule", repository_keyword=None)

            last_row = retrieve_last_row(table_name="modulePackages", primary_key="id", port=port)

            self.assertEqual(last_row["name"], "MyNewModule")
            self.assertEqual(last_row["type"], "MODULE")
            self.assertEqual(last_row["repository"], None)

            self.assertFalse(last_row["Nreleases"])
            self.assertFalse(last_row["latestRelid"])
            self.assertFalse(last_row["latestSourceRelid"])

    def test_register_new_package(self):
        with server_context() as (port, writer):
            self.assertNotEqual(
                retrieve_last_row(table_name="modulePackages", primary_key="id", port=port)["name"],
                "MyNewPackage",
            )

            writer.register_new_package(
                package_name="MyNewPackage",
                repository_keyword="my_repository_keyword",
            )

            last_row = retrieve_last_row(table_name="modulePackages", primary_key="id", port=port)

            self.assertEqual(last_row["name"], "MyNewPackage")
            self.assertEqual(last_row["type"], "PACKAGE")
            self.assertEqual(last_row["repository"], "my_repository_keyword")

            self.assertFalse(last_row["Nreleases"])
            self.assertFalse(last_row["latestRelid"])
            self.assertFalse(last_row["latestSourceRelid"])

            from yam import database_writer

            with self.assertRaises(database_writer.PackageAlreadyExistsException):
                writer.register_new_package(
                    package_name="MyNewPackage",
                    repository_keyword="my_repository_keyword",
                )

    def test_unregister_module(self):
        with server_context() as (port, writer):
            writer.unregister_module("Dspace")

    def test_unregister_package(self):
        with server_context() as (port, writer):
            writer.unregister_package("ROAMSDshellPkg")

    def test_initialize_database(self):
        with server_context(load_tables_from_file=False) as (port, writer):
            writer.initialize_database()

            self.assertEqual(
                [
                    "hostMachine",
                    "moddeps",
                    "modpkgReleases",
                    "modulePackages",
                    "obsoleteRels",
                    "packageModuleReleases",
                    "releaseBugIds",
                    "releasesPath",
                    "yamNative",
                    "yamSite",
                ],
                [list(r.values())[0] for r in _fetch(port, lambda x: x.fetchall(), "SHOW TABLES")],
            )

    def test_initialize_database_with_existing_database_should_raise_exception(self):
        with server_context(load_tables_from_file=True) as (port, writer):
            from yam import database_writer

            with self.assertRaises(database_writer.DatabaseAlreadyInitializedException):
                writer.initialize_database()

    def test_initialize_database_twice_should_raise_exception(self):
        with server_context(load_tables_from_file=False) as (port, writer):
            writer.initialize_database()
            from yam import database_writer

            with self.assertRaises(database_writer.DatabaseAlreadyInitializedException):
                writer.initialize_database()

    def test_write_build_dependencies(self):
        with server_context(load_tables_from_file=True) as (port, writer):
            writer.write_build_dependencies(
                module_name="DspaceTerrain",
                dependency_dictionary={"Dshell++": {"Zip.h"}},
            )

            self.assertEqual(
                {"modid": 320, "uses_modid": 62, "incfile": "Zip.h"},
                retrieve_last_row(table_name="moddeps", primary_key="incfile", port=port),
            )

    def test_write_build_dependencies_mutates_correct_rows(self):
        with server_context(load_tables_from_file=True) as (port, writer):
            writer.write_build_dependencies(
                module_name="DspaceTerrain",
                dependency_dictionary={
                    "Dshell++": {"Foo.h", "Bar.h"},
                    "Dspace": {"Dspace.h"},
                },
            )

            original_row_count = row_count("moddeps", port=port)

            writer.write_build_dependencies(
                module_name="DspaceTerrain",
                dependency_dictionary={"Dshell++": {"Zip.h"}},
            )

            self.assertEqual(original_row_count - 2, row_count("moddeps", port=port))

    def test_write_build_dependencies_should_ignore_non_existent_modules(self):
        with server_context(load_tables_from_file=True) as (port, writer):
            writer.write_build_dependencies(
                module_name="DspaceTerrain",
                dependency_dictionary={
                    "NonExistentModule": {"Zoo.h"},
                    "Dshell++": {"Zip.h"},
                },
            )

            self.assertEqual(
                {"modid": 320, "uses_modid": 62, "incfile": "Zip.h"},
                retrieve_last_row(table_name="moddeps", primary_key="incfile", port=port),
            )


def retrieve_branch_list(relid, port):
    return [
        x.strip()
        for x in retrieve_row(table_name="modpkgReleases", key="relid", value=relid, port=port)["branches"].split(",")
    ]


def retrieve_last_row(table_name, primary_key, port):
    return _fetch(
        port=port,
        fetcher=lambda x: x.fetchone(),
        statement="SELECT * FROM {table} ORDER BY {key} DESC LIMIT 1".format(table=table_name, key=primary_key),
    )


def retrieve_obsoletion_count(relid, port):
    return retrieve_row(table_name="modpkgReleases", key="relid", value=relid, port=port)["obsoletionCount"]


def retrieve_row(table_name, key, value, port):
    return _fetch(
        port,
        lambda x: x.fetchone(),
        "SELECT * FROM {table} WHERE {key}=%s".format(table=table_name, key=key),
        value,
    )


def row_count(table_name, port):
    results = _fetch(
        port=port,
        fetcher=lambda x: x.fetchall(),
        statement="SELECT COUNT(*) FROM {table}".format(table=table_name),
    )

    assert results
    assert results[0]
    return list(results[0].values())[0]


def modify_obsoletion_count(relid, obsoletion_count, port):
    _fetch(
        port,
        lambda _: None,
        "UPDATE modpkgReleases SET obsoletionCount=%s WHERE relid=%s",
        obsoletion_count,
        relid,
    )


def _fetch(port, fetcher, statement, *args):
    """Execute query and fetch result."""
    with contextlib.closing(connector.connect(host="127.0.0.1", password="", database="test", port=port)) as connection:
        with contextlib.closing(connection.cursor(cursor_class=mysql_database_utils.MySQLCursorDict)) as cursor:
            cursor.execute(statement, args)
            return fetcher(cursor)


if __name__ == "__main__":
    unittest.main()
