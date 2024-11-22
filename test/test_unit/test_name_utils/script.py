import unittest
from yam import name_utils


class NameUtilsTestCase(unittest.TestCase):
    def test_filter_module_name(self):
        self.assertEqual(name_utils.filter_module_name("abc"), "abc")
        self.assertEqual(name_utils.filter_module_name(" abc/ "), "abc")
        self.assertEqual(name_utils.filter_module_name("abc/"), "abc")

    def test_filter_module_name_with_exception(self):
        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_module_name('"abc"')

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_module_name("'abc'")

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_module_name("/abc")

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_module_name("a bc")

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_module_name("a'bc")

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_module_name("a,bc")

    def test_filter_package_name(self):
        self.assertEqual(name_utils.filter_package_name("abc"), "abc")
        self.assertEqual(name_utils.filter_package_name(" abc/ "), "abc")
        self.assertEqual(name_utils.filter_package_name("abc/"), "abc")

    def test_filter_package_name_with_exception(self):
        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_package_name('"abc"')

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_package_name("'abc'")

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_package_name("/abc")

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_package_name("a bc")

        with self.assertRaises(name_utils.InvalidNameException):
            name_utils.filter_package_name("a,bc")


if __name__ == "__main__":
    unittest.main()
