import unittest


class LocalFileSystemTestCase(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        from yam import local_file_system

        self.__file_system = local_file_system.LocalFileSystem()

        # Create a temporary directory
        import tempfile

        self.__temporary_file_path = tempfile.mkdtemp(dir=".")

    def tearDown(self):
        """Automatically called after each test* method."""
        import shutil

        shutil.rmtree(path=self.__temporary_file_path)

    def test_make_read_only_recursively(self):
        import os

        my_file_path = os.path.join(self.__temporary_file_path, "my_file")
        my_file = open(my_file_path, "w")
        my_file.close()
        import stat

        # Should be writable by default
        self.assertEqual(
            stat.S_IMODE(os.lstat(my_file_path).st_mode) & stat.S_IWUSR,
            stat.S_IWUSR,
        )

        self.__file_system.make_read_only_recursively(self.__temporary_file_path)

        # Should no longer be writable
        self.assertNotEqual(
            stat.S_IMODE(os.lstat(my_file_path).st_mode) & stat.S_IWUSR,
            stat.S_IWUSR,
        )

    def test_make_read_only_recursively_should_preserve_executable_bit(self):
        import os

        my_file_path = os.path.join(self.__temporary_file_path, "my_file")
        my_file = open(my_file_path, "w")
        my_file.close()
        import stat

        os.chmod(my_file_path, 0o700)

        self.__file_system.make_read_only_recursively(self.__temporary_file_path)

        self.assertEqual(
            stat.S_IMODE(os.lstat(my_file_path).st_mode),
            0o555,
            msg="Read/executable bits should be uniform across owner, " "group, and  other.",
        )

    def test_make_read_only_recursively_should_ignore_failure(self):
        self.__file_system.make_read_only_recursively("/var/log")

    def test_path_exists(self):
        self.assertTrue(self.__file_system.path_exists("."))
        self.assertFalse(self.__file_system.path_exists("non_existent_path"))

    def test_list_directory(self):
        self.assertTrue(self.__file_system.list_directory("."))

    def test_list_directory_with_non_existent_path(self):
        self.assertFalse(self.__file_system.list_directory("non_existent_path"))

    def test_make_directory(self):
        import os

        my_directory = os.path.join(self.__temporary_file_path, "my_directory")

        self.assertFalse(os.path.exists(my_directory))

        self.__file_system.make_directory(path=my_directory)

        self.assertTrue(os.path.exists(my_directory))

    def test_make_directory_ignores_recreate_error(self):
        import os

        my_directory = os.path.join(self.__temporary_file_path, "my_directory")

        self.assertFalse(os.path.exists(my_directory))

        self.__file_system.make_directory(path=my_directory)

        self.assertTrue(os.path.exists(my_directory))

        self.__file_system.make_directory(path=my_directory)

    def test_remove_directory(self):
        import os

        my_directory = os.path.join(self.__temporary_file_path, "my_directory")
        os.mkdir(my_directory)
        self.assertTrue(os.path.exists(my_directory))

        self.__file_system.remove_directory(my_directory)
        self.assertFalse(os.path.exists(my_directory))

    def test_move(self):
        import os

        my_directory = os.path.join(self.__temporary_file_path, "my_directory")
        os.mkdir(my_directory)

        moved_directory = os.path.join(self.__temporary_file_path, "moved_directory")
        self.assertFalse(os.path.exists(moved_directory))

        self.__file_system.move(source_path=my_directory, destination_path=moved_directory)

        self.assertTrue(os.path.exists(moved_directory))

    def test_move_with_error(self):
        import os

        my_directory = os.path.join(self.__temporary_file_path, "my_directory")
        os.mkdir(my_directory)

        my_file = os.path.join(self.__temporary_file_path, "my_file")
        with open(my_file, "w") as f:
            f.write("")

        self.assertTrue(os.path.exists(my_file))

        message_list = []

        def callback(message):
            message_list.append(message)

        self.__file_system.move(
            source_path=my_directory,
            destination_path=my_file,
            progress_callback=callback,
        )

        self.assertEqual(1, len(message_list))

    def test_symbolic_link(self):
        import os

        self.assertFalse(os.path.exists("my_symbolic_link"))

        self.__file_system.symbolic_link(source=".", link_name="my_symbolic_link")

        # Check
        self.assertTrue(os.path.exists("my_symbolic_link"))
        self.assertEqual(os.path.realpath("my_symbolic_link"), os.path.realpath("."))

        # Should be able to call it multiple times, in which case it removes
        # the old one and makes a new link
        self.__file_system.symbolic_link(source="..", link_name="my_symbolic_link")

        # Check
        self.assertTrue(os.path.exists("my_symbolic_link"))
        self.assertEqual(os.path.realpath("my_symbolic_link"), os.path.realpath(".."))

        os.remove("my_symbolic_link")

    def test_symbolic_link_with_error(self):
        import os

        my_file = os.path.join(self.__temporary_file_path, "my_file")
        with open(my_file, "w") as f:
            f.write("")

        self.assertTrue(os.path.exists(my_file))

        message_list = []

        def callback(message):
            message_list.append(message)

        self.__file_system.symbolic_link(source="..", link_name=my_file, progress_callback=callback)

        self.assertEqual(1, len(message_list))

    def test_write_to_file(self):
        from os import path

        filename = path.join(self.__temporary_file_path, "my_new_file")
        self.__file_system.write_to_file(string_data="blah\nabc", filename=filename)
        with open(filename) as f:
            self.assertEqual(f.read(), "blah\nabc")

    def test_write_to_file_should_overwrite_existing(self):
        from os import path

        filename = path.join(self.__temporary_file_path, "my_new_file")
        with open(filename, "w") as f:
            f.write("something")

        with open(filename) as f:
            self.assertNotEqual(f.read(), "blah\nabc")

        # This call should overwrite existing file
        self.__file_system.write_to_file(string_data="blah\nabc", filename=filename)
        with open(filename) as f:
            self.assertEqual(f.read(), "blah\nabc")

    def test_read_file(self):
        from os import path

        filename = path.join(self.__temporary_file_path, "my_new_file")
        with open(filename, "w") as f:
            f.write("something\n123")

        self.assertEqual(self.__file_system.read_file(filename=filename), "something\n123")

    def test_find_dangling_links(self):
        import os

        link_path1 = os.path.join(self.__temporary_file_path, "bad_link1")
        link_path2 = os.path.join(self.__temporary_file_path, "bad_link2")
        os.symlink("non_existent_path1", link_path1)
        os.symlink("non_existent_path2", link_path2)

        os.symlink(
            os.path.abspath(self.__temporary_file_path),
            os.path.join(self.__temporary_file_path, "existent_link1"),
        )

        os.symlink(".", os.path.join(self.__temporary_file_path, "existent_link2"))

        self.assertEqual(
            sorted(self.__file_system.find_dangling_links(path=self.__temporary_file_path)),
            sorted([link_path1, link_path2]),
        )

    def test_find_dangling_links_with_no_links(self):
        self.assertEqual(
            self.__file_system.find_dangling_links(path=self.__temporary_file_path),
            [],
        )

    def test_find_dangling_links_with_one_good_link(self):
        import os

        os.symlink(".", os.path.join(self.__temporary_file_path, "existent_link"))

        self.assertEqual(
            self.__file_system.find_dangling_links(path=self.__temporary_file_path),
            [],
        )

    def test_common_prefix(self):
        self.assertEqual(self.__file_system.common_prefix(["/a/b/c", "/a/b/d"]), "/a/b/")

    def test_resolve_link(self):
        import os

        link_location = os.path.join(self.__temporary_file_path, "tmp_link")
        os.symlink("/tmp", link_location)

        self.assertEqual(self.__file_system.resolve_path(link_location), "/tmp")

    def test_create_temporary_directory(self):
        path = self.__file_system.create_temporary_directory()
        import os

        self.assertTrue(os.path.exists(path))
        os.removedirs(path)

    def test_execute(self):
        self.assertEqual(
            0,
            self.__file_system.execute("./succeed.bash", working_directory=".")[0],
        )

    def test_execute_in_different_working_directory(self):
        import os

        result = self.__file_system.execute(os.path.realpath("./succeed.bash"), working_directory="example_path")
        self.assertEqual((0, "example_file\n", ""), result)

    def test_execute_with_different_exit_status(self):
        self.assertEqual(
            1,
            self.__file_system.execute("./fail.bash", working_directory=".")[0],
        )

    def test_execute_with_exception(self):
        with self.assertRaises(OSError):
            self.__file_system.execute("./non_existent_file", working_directory=".")


if __name__ == "__main__":
    unittest.main()
