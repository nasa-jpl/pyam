import unittest
from yam import concrete_configuration_reader
from yam import concrete_configuration_writer


class ConcreteConfigurationIntegratinTestCase(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        self.__configuration_reader = concrete_configuration_reader.ConcreteConfigurationReader()
        self.__configuration_writer = concrete_configuration_writer.ConcreteConfigurationWriter()

    def test_read_and_write_and_read(self):
        # Read existing data
        module_dictionaries = self.__configuration_reader.read_sandbox_configuration("fake.config")

        # Write it back to file
        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename="temporary.config",
            work_module_dictionary=module_dictionaries["work_modules"],
            link_module_dictionary=module_dictionaries["link_modules"],
            default_branch="blah",
        )

        # Make sure reading back the written file results in the same data
        self.assertEqual(
            module_dictionaries,
            self.__configuration_reader.read_sandbox_configuration("temporary.config"),
        )

        import os

        os.remove("temporary.config")

    def test_bad_entry_read(self):
        # Raise error for bad key
        try:
            module_dictionaries = self.__configuration_reader.read_sandbox_configuration("bad_entry.config")
            # should never get here
            assert 0
        except Exception as e:
            import sys

            # print('TTT', dir(e), str(e.message))
            assert e.message.find("Found unrecognized") >= 0

    def test_duplicate_wm_read(self):
        # Raise error for duplicate work module entry
        try:
            module_dictionaries = self.__configuration_reader.read_sandbox_configuration("duplicate_work_module.config")
            # should never get here
            assert 0
        except Exception as e:
            import sys

            # print('TTT', dir(e), str(e.message))
            assert e.message.find("Found 2") >= 0

    def test_repeated_branch_read(self):
        # Raise error when there is more than one BRANCH entry for a work module
        try:
            module_dictionaries = self.__configuration_reader.read_sandbox_configuration("repeated_branch.config")
            # should never get here
            assert 0
        except Exception as e:
            import sys

            # print('TTT', dir(e), str(e.message))
            assert e.message.find("already exists") >= 0

    def test_missing_wm_read(self):
        # Raise error for case where there is no listed wm but there is a branch entry
        try:
            module_dictionaries = self.__configuration_reader.read_sandbox_configuration("missing_wm.config")
            # should never get here
            assert 0
        except Exception as e:
            import sys

            # print('TTT', dir(e), str(e.message))
            assert e.message.find("There are BRANCH-* entries") >= 0

    def test_missing_branch_read(self):
        # Raise error for case where there is no BRANCH-* entry for a work module
        try:
            module_dictionaries = self.__configuration_reader.read_sandbox_configuration("missing_branch.config")
            # should never get here
            assert 0
        except Exception as e:
            import sys

            # print('TTT', dir(e), str(e.message))
            assert e.message.find("BRANCH-* entries are missing") >= 0

    def test_branch_for_link_read(self):
        # Raise error when a BRANCH_ entry is specified for a link module
        try:
            module_dictionaries = self.__configuration_reader.read_sandbox_configuration("branch_for_link.config")
            # should never get here
            assert 0
        except Exception as e:
            import sys

            # print('TTT', dir(e), str(e.message))
            assert e.message.find("There are BRANCH-* entries for the") >= 0

    def test_work_and_link_read(self):
        # Raise error when a module is listed as both a work and a link module
        try:
            module_dictionaries = self.__configuration_reader.read_sandbox_configuration("work_and_link.config")
            # should never get here
            assert 0
        except Exception as e:
            import sys

            # print('TTT', dir(e), str(e.message))
            assert e.message.find("listed in both WORK_MODULES and LINK_MODULES") >= 0


if __name__ == "__main__":
    unittest.main()
