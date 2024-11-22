import unittest
import mockito
from yam import package_sandbox
from yam.module import WorkModuleType


class FakePackageSandbox(package_sandbox.PackageSandbox):
    """A PackageSandbox with its abstract methods set to return predetermined
    values."""

    def __init__(self, package_name, sandbox_path, revision_control_system, file_system):
        package_sandbox.PackageSandbox.__init__(
            self,
            package_name=package_name,
            sandbox_path=sandbox_path,
            revision_control_system=revision_control_system,
            file_system=file_system,
        )

    def _check_out_package_data_files(
        self,
        package_name,
        sandbox_path,
        revision_control_system,
        file_system,
        parent_directory,
        progress_callback,
        work_module_type=WorkModuleType.NONE,
        #         work_branch=False,
        #         tagged_branch=False,
        #         main_branch=False,
    ):
        """Fake implementation of
        package_sandbox._check_out_package_data_files()."""


class PackageSandboxTestCase(unittest.TestCase):
    def setUp(self):
        from yam import revision_control_system

        self.__mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        from yam import file_system

        self.__mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

    def test_check_out(self):
        mockito.when(self.__mock_file_system).path_exists("FakePackage-blah").thenReturn(False)

        # Make calls
        sandbox = FakePackageSandbox(
            package_name="FakePackage",
            sandbox_path="FakePackage-blah",
            revision_control_system=self.__mock_revision_control_system,
            file_system=self.__mock_file_system,
        )
        sandbox.check_out(progress_callback=lambda _: None)

        # Verify
        mockito.verify(self.__mock_file_system).symbolic_link(
            source="common/Makefile", link_name="FakePackage-blah/Makefile"
        )

        mockito.verify(self.__mock_file_system).make_directory(path="FakePackage-blah/src")

    def test_check_out_raises_exception_when_sandbox_already_exists(self):
        mockito.when(self.__mock_file_system).path_exists("FakePackage-blah").thenReturn(True)

        sandbox = FakePackageSandbox(
            package_name="FakePackage",
            sandbox_path="FakePackage-blah",
            revision_control_system=self.__mock_revision_control_system,
            file_system=self.__mock_file_system,
        )
        from yam import yam_exception

        with self.assertRaises(yam_exception.YamException):
            sandbox.check_out(progress_callback=lambda _: None)


if __name__ == "__main__":
    unittest.main()
