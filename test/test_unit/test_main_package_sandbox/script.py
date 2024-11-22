import unittest
from yam import main_package_sandbox


class MainPackageSandboxTestCase(unittest.TestCase):
    def test_check_out(self):
        import mockito

        from yam import revision_control_system

        mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        from yam import file_system

        mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

        from yam import database_reader

        mock_database_reader = mockito.mock(database_reader.DatabaseReader, strict=False)

        from yam import configuration_reader

        mock_configuration_reader = mockito.mock(configuration_reader.ConfigurationReader, strict=False)

        from yam import configuration_writer

        mock_configuration_writer = mockito.mock(configuration_writer.ConfigurationWriter, strict=False)

        mockito.when(mock_database_reader).package_repository_url("FakePackage").thenReturn("my_repository_url")

        mockito.when(mock_file_system).path_exists("FakePackage-blah").thenReturn(False)

        # Read "YAM.modules"
        mockito.when(mock_configuration_reader).read_package_information(
            package_configuration_filename="FakePackage-blah/common/YAM.modules",
            package_name="FakePackage",
        ).thenReturn(set(["FakeModule"]))

        # Create "YAM.config" based on above "YAM.modules" and database_reader
        mockito.when(mock_database_reader).latest_module_information(module_name="FakeModule", release=None).thenReturn(
            {"tag": "my_fake_tag", "build": "Build02"}
        )

        # Make calls
        sandbox = main_package_sandbox.MainPackageSandbox(
            package_name="FakePackage",
            sandbox_path="FakePackage-blah",
            revision_control_system=mock_revision_control_system,
            file_system=mock_file_system,
            database_reader=mock_database_reader,
            configuration_reader=mock_configuration_reader,
            configuration_writer=mock_configuration_writer,
            default_branch="fake_default_branch",
            release_directory=None,
        )
        sandbox.check_out()

        # Verify
        mockito.verify(mock_revision_control_system).check_out(
            source="my_repository_url/Packages/FakePackage/trunk",
            target="FakePackage-blah",
        )

        mockito.verify(mock_revision_control_system).check_out(
            source="my_repository_url/common/trunk",
            target="FakePackage-blah/common",
        )

        mockito.verify(mock_file_system).symbolic_link(source="common/Makefile", link_name="FakePackage-blah/Makefile")

        mockito.verify(mock_configuration_writer).write_sandbox_configuration(
            configuration_filename="FakePackage-blah/YAM.config",
            work_module_dictionary={},
            link_module_dictionary={"FakeModule": ("my_fake_tag", "Build02", None, None)},
            default_branch="fake_default_branch",
        )

        mockito.verify(mock_file_system).make_directory(path="FakePackage-blah/src")


if __name__ == "__main__":
    unittest.main()
