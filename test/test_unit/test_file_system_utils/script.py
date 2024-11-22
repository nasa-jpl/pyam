import unittest
from yam import file_system_utils


class FileSystemUtilsTestCase(unittest.TestCase):
    def test_find_sandbox_root_in_subdirectory(self):
        import os

        self.assertEqual(
            file_system_utils.find_sandbox_root("FakeSandbox/a"),
            os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox"),
        )

        self.assertEqual(
            file_system_utils.find_sandbox_root("FakeSandbox/a/b/c"),
            os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox"),
        )

        self.assertEqual(
            file_system_utils.find_sandbox_root("FakeSandbox/1"),
            os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox"),
        )

    def test_find_sandbox_root_in_root(self):
        import os

        self.assertEqual(
            file_system_utils.find_sandbox_root("FakeSandbox/"),
            os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox"),
        )

        self.assertEqual(
            file_system_utils.find_sandbox_root("FakeSandbox"),
            os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox"),
        )

    def test_find_sandbox_root_from_absolute_path(self):
        import os

        self.assertEqual(
            file_system_utils.find_sandbox_root(os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox")),
            os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox"),
        )

        self.assertEqual(
            file_system_utils.find_sandbox_root(os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox/a/b/c")),
            os.path.join(os.path.abspath(os.getcwd()), "FakeSandbox"),
        )

    def test_find_sandbox_root_exceptions(self):
        from yam import yam_exception

        with self.assertRaises(yam_exception.YamException):
            # We limit max_directory_checks otherwise we will end up finding
            # the real sandbox where pyam lives.
            file_system_utils.find_sandbox_root("NotASandbox/a/b/c", max_directory_checks=6)


if __name__ == "__main__":
    unittest.main()
