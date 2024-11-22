import unittest
import mockito
from yam import work_module


class FakeWorkModule(work_module.WorkModule):
    """A WorkModule with its abstract methods set to return predetermined
    values."""

    def __init__(self, module_name, revision_control_system, parent_directory):
        work_module.WorkModule.__init__(
            self,
            module_name=module_name,
            revision_control_system=revision_control_system,
            parent_directory=parent_directory,
        )
        self.__module_directory_name = module_name

    def _repository_url(self):
        """Fake implementation of work_module._repository_url()."""
        return "fake_repository_url"


class WorkModuleTestCase(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        from yam import database_reader

        self.__mock_database_reader = mockito.mock(database_reader.DatabaseReader, strict=False)

        from yam import revision_control_system

        self.__mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

    def tearDown(self):
        """Automatically called after each test* method."""
        mockito.unstub()

    def test_check_out(self):
        # Set up the mock objects
        mockito.when(self.__mock_revision_control_system).working_copy_exists(
            path="fake_src_directory/FakeModule"
        ).thenReturn(False)

        # Make calls
        module = FakeWorkModule(
            module_name="FakeModule",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
        )
        module.check_out()

        # Verify
        mockito.verify(self.__mock_revision_control_system).check_out(
            source="fake_repository_url", target="fake_src_directory/FakeModule"
        )

    def test_check_out_multiple_times_should_only_check_out_once(self):
        # Set up the mock objects
        mockito.when(self.__mock_revision_control_system).working_copy_exists(
            path="fake_src_directory/FakeModule"
        ).thenReturn(False).thenReturn(True)

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "fake_repository_url"
        )

        # Make calls
        module = FakeWorkModule(
            module_name="FakeModule",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
        )
        module.check_out()
        module.check_out()
        module.check_out()

        # Verify
        mockito.verify(self.__mock_revision_control_system, times=1).check_out(
            source="fake_repository_url", target="fake_src_directory/FakeModule"
        )

    def test_check_out_with_mismatching_url_should_raise_exception(self):
        mockito.when(self.__mock_revision_control_system).working_copy_exists(
            path="fake_src_directory/FakeModule"
        ).thenReturn(True)

        mockito.when(self.__mock_revision_control_system).url(path="fake_src_directory/FakeModule").thenReturn(
            "unmatching_repository_url"
        )

        module = FakeWorkModule(
            module_name="FakeModule",
            revision_control_system=self.__mock_revision_control_system,
            parent_directory="fake_src_directory",
        )

        from yam import yam_exception

        with self.assertRaises(yam_exception.YamException):
            module.check_out()

    def test_feature_branches_url(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("repo_url")

        self.assertEqual(
            work_module.feature_branches_url(
                module_name="FakeModule",
                revision_tag="my_revision",
                branch_id="my_branch",
                database_reader=self.__mock_database_reader,
            ),
            "repo_url/Modules/FakeModule/featureBranches/FakeModule-my_revision-my_branch",
        )

    def test_main_branch_url(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("repo_url")

        self.assertEqual(
            work_module.main_branch_url(
                module_name="FakeModule",
                database_reader=self.__mock_database_reader,
            ),
            "repo_url/Modules/FakeModule/trunk",
        )

    def test_releases_url(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("repo_url")

        self.assertEqual(
            work_module.releases_url(
                module_name="FakeModule",
                revision_tag="my_revision",
                database_reader=self.__mock_database_reader,
            ),
            "repo_url/Modules/FakeModule/releases/FakeModule-my_revision",
        )

    def test_dead_branches_url(self):
        mockito.when(self.__mock_database_reader).module_repository_url("FakeModule").thenReturn("repo_url")

        self.assertEqual(
            work_module.dead_branches_url(
                module_name="FakeModule",
                revision_tag="my_revision",
                branch_id="my_branch",
                database_reader=self.__mock_database_reader,
            ),
            "repo_url/Modules/FakeModule/deadBranches/FakeModule-my_revision-my_branch",
        )


if __name__ == "__main__":
    unittest.main()
