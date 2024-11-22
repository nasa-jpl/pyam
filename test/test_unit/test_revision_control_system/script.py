import unittest
from yam import revision_control_system


class RevisionControlSystemTestCase(unittest.TestCase):
    def test_url_check(self):
        import mockito

        mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem)
        mockito.when(mock_revision_control_system).exists(url="non_existent_url").thenReturn(False)

        with self.assertRaises(revision_control_system.NonExistentURLException):
            revision_control_system.url_check(mock_revision_control_system, url="non_existent_url")

    def test_exceptions(self):
        message = "foo bar"
        self.assertEqual(message, str(revision_control_system.PermissionException(message)))


if __name__ == "__main__":
    unittest.main()
