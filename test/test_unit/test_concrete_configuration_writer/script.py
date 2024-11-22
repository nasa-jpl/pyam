import unittest

from yam import concrete_configuration_writer
from yam import yam_exception


class ConfigurationWriterTestCase(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        self.__configuration_writer = concrete_configuration_writer.ConcreteConfigurationWriter()

        import tempfile

        self.__temporary_directory = tempfile.mkdtemp(dir=".")

    def tearDown(self):
        """Automatically called after each test* method."""
        import shutil

        shutil.rmtree(path=self.__temporary_directory, ignore_errors=True)

    def test_is_important_line(self):
        self.assertTrue(is_important_line("abc"))
        self.assertTrue(is_important_line("# BRANCH_blah = blah"))
        self.assertFalse(is_important_line("# BRANCH_blah - blah"))
        self.assertFalse(is_important_line("#abc"))
        self.assertFalse(is_important_line(""))

    def test_filter_junk(self):
        self.assertEqual("", filter_junk("# comment"))

        self.assertEqual(
            "abc",
            filter_junk(
                """# comment


abc
"""
            ),
        )

    def test_write_sandbox_configuration(self):
        self.run_test(
            """
WORK_MODULES = FooBar \\
               ModuleB \\
               ModuleE \\
               ModuleF

LINK_MODULES = ModuleC/ModuleC-R1-03n-Build02 \\
               Zing/Zing-R1-01s

BRANCH_FooBar  = FooBar-R2-01   my_branch
BRANCH_ModuleB = ModuleB-R1-02b my_branch2
BRANCH_ModuleE = main
BRANCH_ModuleF = ModuleF-R1-02b

# BRANCH_ModuleC = ModuleC-R1-03n my_default_branch
# BRANCH_Zing    = Zing-R1-01s    my_default_branch

""",
            work_module_dictionary={
                "FooBar": ("R2-01", "my_branch"),
                "ModuleE": (None, None),
                "ModuleB": ("R1-02b", "my_branch2"),
                "ModuleF": ("R1-02b", None),
            },
            link_module_dictionary={
                "ModuleC": ("R1-03n", "02", None, None),
                "Zing": ("R1-01s", None, None, None),
            },
        )

    def test_write_sandbox_configuration_with_no_work_modules(self):
        self.run_test(
            """
WORK_MODULES =

LINK_MODULES = ModuleC/ModuleC-R1-03n-Build02 \\
               Zing/Zing-R1-01s

# BRANCH_ModuleC = ModuleC-R1-03n my_default_branch
# BRANCH_Zing    = Zing-R1-01s    my_default_branch

""",
            work_module_dictionary={},
            link_module_dictionary={
                "ModuleC": ("R1-03n", "02", None, None),
                "Zing": ("R1-01s", None, None, None),
            },
        )

    def test_write_sandbox_configuration_with_no_link_modules(self):
        self.run_test(
            """
WORK_MODULES = FooBar

LINK_MODULES =

BRANCH_FooBar = FooBar-R2-01a my_branch

""",
            work_module_dictionary={"FooBar": ("R2-01a", "my_branch")},
            link_module_dictionary={},
        )

    def test_write_sandbox_configuration_with_no_modules(self):
        self.run_test(
            """
WORK_MODULES =

LINK_MODULES =

""",
            work_module_dictionary={},
            link_module_dictionary={},
        )

    def run_test(self, expected, work_module_dictionary, link_module_dictionary):
        import os

        temp_config = os.path.join(self.__temporary_directory, "temp.config")
        self.__configuration_writer.write_sandbox_configuration(
            configuration_filename=temp_config,
            work_module_dictionary=work_module_dictionary,
            link_module_dictionary=link_module_dictionary,
            default_branch="my_default_branch",
        )

        with open(temp_config, "r") as outputted_config_file:
            outputted_config_data = outputted_config_file.read()
            self.assertEqual(filter_junk(outputted_config_data), filter_junk(expected))

        # Unwritable files should raise a yam exception.
        os.chmod(temp_config, 0o000)
        with self.assertRaises(yam_exception.YamException):
            self.__configuration_writer.write_sandbox_configuration(
                configuration_filename=temp_config,
                work_module_dictionary=work_module_dictionary,
                link_module_dictionary=link_module_dictionary,
                default_branch="my_default_branch",
            )
        os.chmod(temp_config, 0o777)


def is_important_line(line):
    import re

    return line.strip() and (not line.startswith("#") or re.match("# BRANCH_[a-zA-Z]+ *= *[a-zA-Z]", line))


def filter_junk(data):
    """Filter out non-branch comments and empty lines."""
    return "\n".join([line for line in data.split("\n") if is_important_line(line)])


if __name__ == "__main__":
    unittest.main()
