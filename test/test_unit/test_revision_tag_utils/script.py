import unittest
from yam import revision_tag_utils


class RevisionTagUtilsTestCase(unittest.TestCase):
    def test_split_revision_tag(self):
        self.assertEqual(revision_tag_utils.split_revision_tag("R1-03c"), (1, 3, 3))

        self.assertEqual(revision_tag_utils.split_revision_tag("R1-03"), (1, 3, 0))

    def test_split_revision_tag_should_raise_exception_on_invalid_tag(self):
        from yam import yam_exception

        with self.assertRaises(yam_exception.YamException):
            revision_tag_utils.split_revision_tag("1-03c")

        with self.assertRaises(yam_exception.YamException):
            revision_tag_utils.split_revision_tag("R103c")

        with self.assertRaises(yam_exception.YamException):
            revision_tag_utils.split_revision_tag("R1-c")

    def test_join_revision_tag_numbers(self):
        self.assertEqual(revision_tag_utils.join_revision_tag_numbers(*(1, 3, 3)), "R1-03c")

    def test_join_and_split_revision_tag(self):
        for major in range(150):
            for minor in range(100):
                for extension in range(27):
                    revision_tag = revision_tag_utils.join_revision_tag_numbers(
                        major_number=major,
                        minor_number=minor,
                        extension_number=extension,
                    )
                    self.assertEqual(
                        revision_tag_utils.split_revision_tag(revision_tag),
                        (major, minor, extension),
                    )

    def test_incremented(self):
        self.assertEqual(revision_tag_utils.incremented("R1-03c"), "R1-03d")

        self.assertEqual(revision_tag_utils.incremented("R1-03"), "R1-03a")

        self.assertEqual(revision_tag_utils.incremented("R1-02z"), "R1-03")

        self.assertEqual(revision_tag_utils.incremented("R1-99a"), "R1-99b")

        self.assertEqual(revision_tag_utils.incremented("R1-99z"), "R2-00")

        self.assertEqual(revision_tag_utils.incremented("R99-99z"), "R100-00")

        self.assertEqual(revision_tag_utils.incremented("R100-00"), "R100-00a")

        self.assertEqual(revision_tag_utils.incremented("R100-00a"), "R100-00b")


if __name__ == "__main__":
    unittest.main()
