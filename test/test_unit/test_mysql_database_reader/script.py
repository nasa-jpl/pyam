from __future__ import print_function

import contextlib
import os
import unittest

from yam import mysql_database_reader


class SQLDatabaseReaderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start MySQL server only once.

        This is okay since all tests in here are read-only. This dramatically
        improves test speed.

        """
        # Create temporary directory where we will look for file to indicate
        # that the MySQL server is ready
        import tempfile

        cls._temporary_mysql_server_path = tempfile.mkdtemp(dir=".")
        cls._ready_filename = os.path.join(cls._temporary_mysql_server_path, "ready")

        # Start MySQL server
        # Note that the server will be loaded with a known data set from
        # "../../common/mysql/example_yam_for_import.sql".
        import subprocess

        cls._mysql_process = subprocess.Popen(
            [
                "../../common/mysql/start_test_mysql_server.bash",
                "-r",
                cls._ready_filename,
                "-s",
                "../../common/mysql/example_yam_for_import.sql",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        while True:
            if cls._mysql_process.poll():
                print("MySQL server died or did not start see below for " "stdout and stderr from server.")
                print(cls._mysql_process.stdout.read())
                print(cls._mysql_process.stderr.read())
                raise IOError("MySQL server died")
            if os.path.exists(cls._ready_filename):
                break
            import time

            time.sleep(0.1)

        with open(cls._ready_filename) as ready_file:
            cls._port = int(ready_file.readline())

        # Set read-only flag. This makes sure that none of the
        # SQLDatabaseReader methods accidentally modify the database. If a
        # modification occurs, an exception on the client side will occur.
        mysql_client = subprocess.Popen(
            [
                "mysql",
                "-h",
                "127.0.0.1",
                "--user=root",
                "--password=",
                "--port={port}".format(port=cls._port),
                "test",
            ],
            stdin=subprocess.PIPE,
        )
        mysql_client.communicate("SET GLOBAL read_only = ON;".encode("utf-8"))
        assert mysql_client.returncode == 0

    @classmethod
    def tearDownClass(cls):
        # If the MySQL server died (due to error), print the server output
        if cls._mysql_process.poll():
            print("MySQL server died or did not start see below for stdout " "and stderr from server.")
            print(cls._mysql_process.stdout.read())
            print(cls._mysql_process.stderr.read())
        else:
            # Wait for the process to terminate
            cls._mysql_process.terminate()
            cls._mysql_process.wait(10)

        import shutil

        shutil.rmtree(path=cls._temporary_mysql_server_path, ignore_errors=True)

    def test_invalid_connection_should_raise_exception(self):
        from yam import database

        with self.assertRaises(database.ConnectionException):
            reader = mysql_database_reader.MySQLDatabaseReader(
                hostname="127.0.0.1",
                port=self._port,
                username="",
                password="",
                database_name="non_existent",
                keyword_to_repository_dictionary={
                    None: "fake_default_url",
                    "DEFAULT": "fake_default_url",
                },
            )

            reader.latest_module_information("AcmeModels")

        with self.assertRaises(database.ConnectionException):
            reader = mysql_database_reader.MySQLDatabaseReader(
                hostname="227.0.0.2",
                port=self._port,
                username="",
                password="",
                database_name="test",
                keyword_to_repository_dictionary={
                    None: "fake_default_url",
                    "DEFAULT": "fake_default_url",
                },
            )

            reader.latest_module_information("AcmeModels")

    def test_module_history(self):
        with reader_context(self._port) as reader:
            import datetime

            print(reader.module_history(["AcmeModels"], 1, True, True, None)[0])

            self.assertEqual(
                reader.module_history(["AcmeModels"], 1, True, True, None)[0],
                {
                    "datetime": datetime.datetime(2005, 12, 5, 9, 20, 23),
                    "tag": "R3-47l",
                    "build": None,
                    "user": "jain",
                    "name": "AcmeModels",
                },
            )

    def test_latest_module_information(self):
        with reader_context(self._port) as reader:
            import datetime

            self.assertEqual(
                reader.latest_module_information("AcmeModels"),
                {
                    "datetime": datetime.datetime(2006, 5, 31, 22, 40, 9),
                    "tag": "R3-47l",
                    "build": "05",
                    "user": "jain",
                    "branches": None,
                },
            )

    def test_latest_module_information_with_no_build(self):
        with reader_context(self._port) as reader:
            import datetime

            self.assertEqual(
                reader.latest_module_information("Dshell++"),
                {
                    "datetime": datetime.datetime(2006, 7, 12, 14, 23, 4),
                    "tag": "R4-06g",
                    "build": None,
                    "user": "jmc",
                    "branches": "jbmas, jingshen",
                },
            )

    def test_latest_module_information_should_throw_exception_on_non_existent_module(self):
        with reader_context(self._port) as reader:
            from yam import database_reader

            with self.assertRaises(database_reader.ModuleLookupException):
                reader.latest_module_information("NonExistentModule123")

    def test_latest_module_information_should_raise_exception_on_dead_module(self):
        with reader_context(self._port) as reader:
            from yam import yam_exception

            with self.assertRaises(yam_exception.YamException):
                reader.latest_module_information("FlowDemo")

    def test_module_information(self):
        with reader_context(self._port) as reader:
            import datetime

            self.assertEqual(
                reader.module_information(module_name="AcmeModels", revision_tag="R3-46a"),
                {
                    "datetime": datetime.datetime(1998, 10, 30, 17, 4, 2),
                    "build": "04",
                    "user": "jain",
                    "branches": None,
                },
            )

    def test_module_information_should_raise_exception_when_not_finding_name_and_tag(self):
        with reader_context(self._port) as reader:
            from yam import database_reader

            with self.assertRaises(database_reader.ModuleLookupException):
                reader.module_information(module_name="AcmeModels", revision_tag="R8-11b")

    def test_latest_package_revision_tag(self):
        with reader_context(self._port) as reader:
            self.assertEqual("R1-15s", reader.latest_package_revision_tag("ROAMSDshellPkg"))

    def test_latest_package_revision_tag_should_raise_exception_on_non_existent_package(self):
        with reader_context(self._port) as reader:
            from yam import database_reader

            with self.assertRaises(database_reader.PackageLookupException):
                reader.latest_package_revision_tag("NonExistentPackage")

    def test_latest_package_revision_tag_should_raise_exception_on_dead_package(self):
        with reader_context(self._port) as reader:
            from yam import yam_exception

            with self.assertRaises(yam_exception.YamException):
                reader.latest_package_revision_tag("MsfRoamsPkg")

    def test_module_names(self):
        with reader_context(self._port) as reader:
            self.assertIn("Dshell++", reader.module_names())
            self.assertNotIn("NonExistentModule", reader.module_names())

    def test_package_names(self):
        with reader_context(self._port) as reader:
            self.assertIn("ROAMSDshellPkg", reader.package_names())
            self.assertNotIn("NonExistentPkg", reader.package_names())

    def test_module_repository_url(self):
        with reader_context(self._port) as reader:
            self.assertEqual(reader.module_repository_url("Alice"), "fake_default_url")
            self.assertEqual(reader.module_repository_url("VisMap"), "fake_default_url")

    def test_module_repository_url_exception(self):
        reader = mysql_database_reader.MySQLDatabaseReader(
            hostname="127.0.0.1",
            port=self._port,
            username="",
            password="",
            database_name="test",
            keyword_to_repository_dictionary={},
        )

        from yam import database_reader

        with self.assertRaises(database_reader.RepositoryLookupException):
            reader.module_repository_url("Alice")

    def test_module_repository_url_should_throw_exception_on_lookup_error(self):
        with reader_context(self._port) as reader:
            from yam import database_reader

            with self.assertRaises(database_reader.ModuleLookupException):
                reader.module_repository_url("NonExistentModule")

    def test_package_repository_url(self):
        with reader_context(self._port) as reader:
            self.assertEqual(
                reader.package_repository_url("ROAMSDshellPkg"),
                "fake_default_url",
            )

    def test_package_repository_url_should_throw_exception_on_lookup_error(self):
        with reader_context(self._port) as reader:
            from yam import database_reader

            with self.assertRaises(database_reader.PackageLookupException):
                reader.package_repository_url("NonExistentPackage")

    def test_local_date_time(self):
        with reader_context(self._port) as reader:
            t1 = reader.local_date_time()
            t2 = reader.local_date_time()
            self.assertLessEqual(t1, t2)

            t3 = reader.local_date_time()
            self.assertLessEqual(t2, t3)

    def test_local_date_time_is_accurate(self):
        with reader_context(self._port) as reader:
            # In this test, the fake server is run locally, so its date should
            # match datetime
            import datetime

            actual = datetime.datetime.now()

            database_time = reader.local_date_time()

            import time

            delta_in_seconds = 2.0
            self.assertAlmostEqual(
                time.mktime(database_time.timetuple()),
                time.mktime(actual.timetuple()),
                delta=delta_in_seconds,
            )

    def test_obsolete_modules(self):
        with reader_context(self._port) as reader:
            self.assertEqual(
                set(
                    [
                        "LaRCModels",
                        "RoverTests",
                        "AnnModels",
                        "RoverNavModels",
                        "DartsExtIK",
                        "Ksolv",
                        "ContactModels",
                        "OPSPModels",
                        "EnvClient",
                        "TerrainObject",
                        "Dnoise",
                        "DSolverModels",
                        "SimModels",
                        "EnvClientTest",
                        "SiteEnvClient",
                        "DshellDspace",
                        "RsrModels",
                        "AtbeTclMesg",
                        "MachineVisionCore",
                        "Gestalt",
                        "SwigTclDot",
                        "aejModels",
                        "FSTModels",
                        "MpfModels",
                        "DshellScope",
                        "NrovModels",
                        "SiteEnvClientTest",
                        "SimScape-VisSite",
                        "Dmex",
                        "FidoValidation",
                        "MathTclUtils",
                        "SimScape",
                        "DefunctModels",
                        "Craft",
                        "ACSModels",
                        "DshellEnvCache",
                        "CVode",
                        "Darts",
                        "spk2darts",
                        "AcmeModels",
                        "MarsGRAM2005Models",
                        "SurfaceContact",
                        "RoamsDev",
                        "SOA",
                        "DmexStubModels",
                        "CameraImageModels",
                        "GravityModels",
                        "TerrainSurface",
                        "StarlightModels",
                        "libMSIM",
                        "CameraResponse",
                        "SimScapeVista",
                        "SpicePositionModels",
                        "TerrainInstrumentServer",
                        "RoverModels",
                        "SimScapeMigration",
                        "MslModels",
                        "DshellExpr",
                        "Dshtcl++",
                        "EphemPropagatorModels",
                        "SpiceModels",
                        "MatlabServer",
                        "EDLAeroModels",
                        "RoverDynModels",
                        "MDSModels",
                        "SimScape-Import",
                        "DspaceTerrain",
                        "ANN",
                        "GeneralModels",
                        "gusto",
                        "DhssModels",
                        "IntegratorModels",
                        "GllModels",
                        "DshellEnvClient",
                        "RsrAcsModels",
                        "Spice",
                        "IntegratorTest",
                        "DshellSwift",
                        "IKGraph",
                        "AmesMSF_IF",
                        "Dhss",
                        "Vista",
                    ]
                ),
                reader.obsolete_builds(),
            )

    def test_module_dependencies(self):
        with reader_context(self._port) as reader:
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
                reader.module_dependencies("DspaceTerrain"),
            )

    def test_module_dependents(self):
        with reader_context(self._port) as reader:
            self.assertEqual({"DspaceTerrain"}, reader.module_dependents("DSoar"))


@contextlib.contextmanager
def reader_context(port):
    """Create instance of SQLDatabaseReader with some fixed arguments."""
    with mysql_database_reader.MySQLDatabaseReader(
        hostname="127.0.0.1",
        port=port,
        username="",
        password="",
        database_name="test",
        keyword_to_repository_dictionary={
            None: "fake_default_url",
            "DEFAULT": "fake_default_url",
        },
    ) as reader:
        yield reader


if __name__ == "__main__":
    unittest.main()
