import unittest
from yam import configuration_reader
from yam import concrete_configuration_reader


class ConfigurationReaderTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.__configuration_reader = concrete_configuration_reader.ConcreteConfigurationReader()

    def test_read_tagged_work_module_information(self):
        self.assertEqual(
            self.__configuration_reader.read_work_module_information("fake.config", "FakeModuleE"),
            ("R2-00a", ""),
        )

    def test_read_main_work_module_information(self):
        self.assertEqual(
            self.__configuration_reader.read_work_module_information("fake.config", "FakeModuleF"),
            (None, None),
        )

    def test_read_branched_work_module_information(self):
        self.assertEqual(
            self.__configuration_reader.read_work_module_information("fake.config", "FakeModuleD"),
            ("R1-00z", "my-tag1"),
        )

    def test_read_non_existent_work_module_information_results_in_error(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_work_module_information("fake.config", "NonExistentModule")

    def test_read_invalid_configuration_results_in_error(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_work_module_information("invalid.config", "FakeModuleA")

    def test_read_invalid_configuration1_results_in_error(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_work_module_information("invalid1.config", "FakeModuleA")

    def test_read_invalid_configuration2_results_in_error(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_work_module_information("invalid2.config", "FakeModuleA")

    def test_read_garbage_configuration_results_in_error(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_work_module_information("garbage.config", "FakeModuleA")

    def test_configuration_error(self):
        error = configuration_reader.ConfigurationError(message="My message", filename="my_filename")
        self.assertEqual(str(error), "My message in file 'my_filename'")

    def test_read_package_information(self):
        self.assertEqual(
            self.__configuration_reader.read_package_information(
                package_configuration_filename="fake.modules",
                package_name="ThirdPartyPkg",
            ),
            set(["thirdParty", "SiteDefs", "DshellEnv", "Dtest"]),
        )

        self.assertEqual(
            self.__configuration_reader.read_package_information(
                package_configuration_filename="fake.modules",
                package_name="YaMPkg",
            ),
            set(
                [
                    "SiteDefs",
                    "DshellEnv",
                    "Dtest",
                    "YaM",
                    "YaM-test",
                    "YaMUtils",
                ]
            ),
        )

    def test_read_package_information_raises_exception_when_not_finding_package(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_package_information(
                package_configuration_filename="fake.modules",
                package_name="NonExistentPkg",
            )

    def test_read_package_information_raises_exception_when_not_finding_file(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_package_information(
                package_configuration_filename="non_existent.modules",
                package_name="ThirdPartyPkg",
            )

    def test_read_sandbox_configuration(self):
        self.assertEqual(
            self.__configuration_reader.read_sandbox_configuration(configuration_filename="fake.config"),
            {
                "work_modules": {
                    "FakeModuleA": ("R1-00v", "my-tag"),
                    "FakeModuleD": ("R1-00z", "my-tag1"),
                    "FakeModuleE": ("R2-00a", ""),
                    "FakeModuleF": (None, None),
                },
                "link_modules": {
                    "FakeModuleB": ("R1-63x", None, None, None),
                    "FakeModuleC": ("R1-01f", None, None, None),
                    "FakeModuleG": ("R1-01f", None, "ProjectA", "05"),
                    "FakeModuleZ": ("R99-21", "13", None, None),
                },
            },
        )

    def test_read_sandbox_configuration_should_raise_exception_on_invalid_line(self):
        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_sandbox_configuration(configuration_filename="invalid_link.config")

        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_sandbox_configuration(configuration_filename="invalid_link1.config")

        with self.assertRaises(configuration_reader.ConfigurationError):
            self.__configuration_reader.read_sandbox_configuration(configuration_filename="invalid_link2.config")


if __name__ == "__main__":
    unittest.main()
