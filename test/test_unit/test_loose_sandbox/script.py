import unittest
import mockito
from yam import loose_sandbox
from yam import client


class LooseSandboxTestCase(unittest.TestCase):
    def setUp(self):
        from yam import revision_control_system

        self.__mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        from yam import file_system

        self.__mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

        from yam import database_reader

        self.__mock_database_reader = mockito.mock(database_reader.DatabaseReader, strict=False)

        from yam import configuration_writer

        self.__mock_configuration_writer = mockito.mock(configuration_writer.ConfigurationWriter, strict=False)

    def test_check_out(self):
        mockito.when(self.__mock_file_system).path_exists("FakePackage-blah").thenReturn(False)

        # Module build dependencies will be queried.
        mockito.when(self.__mock_database_reader).module_dependencies("FakeModule1").thenReturn(
            {"DependencyModuleA", "DependencyModuleB"}
        )

        mockito.when(self.__mock_database_reader).module_dependencies("FakeModule2").thenReturn(set())

        mockito.when(self.__mock_database_reader).module_dependencies("DependencyModuleA").thenReturn(set())

        # Returning None is permissible.
        mockito.when(self.__mock_database_reader).module_dependencies("DependencyModuleB").thenReturn(None)

        # Create "YAM.config" based on above "YAM.modules" and database_reader
        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule1", release=None
        ).thenReturn({"tag": "my_fake_tag1", "build": "Build02"})

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="FakeModule2", release=None
        ).thenReturn({"tag": "my_fake_tag2", "build": None})

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="DependencyModuleA", release=None
        ).thenReturn({"tag": "my_fake_tag_a", "build": None})

        mockito.when(self.__mock_database_reader).latest_module_information(
            module_name="DependencyModuleB", release=None
        ).thenReturn({"tag": "my_fake_tag_b", "build": None})

        sandbox = loose_sandbox.LooseSandbox(
            module_names=["FakeModule1", "FakeModule2"],
            sandbox_path="FakePackage-blah",
            revision_control_system=self.__mock_revision_control_system,
            file_system=self.__mock_file_system,
            database_reader=self.__mock_database_reader,
            repository_url="repository_url",
            configuration_writer=self.__mock_configuration_writer,
            default_branch="fake_default_branch",
            release_directory=None,
        )
        sandbox.check_out()

        # Verify
        mockito.verify(self.__mock_file_system).make_directory(path="FakePackage-blah")

        mockito.verify(self.__mock_revision_control_system).check_out(
            source="repository_url/common/trunk",
            target="FakePackage-blah/common",
        )

        mockito.verify(self.__mock_file_system).symbolic_link(
            source="common/Makefile", link_name="FakePackage-blah/Makefile"
        )

        mockito.verify(self.__mock_configuration_writer).write_sandbox_configuration(
            configuration_filename="FakePackage-blah/YAM.config",
            work_module_dictionary={},
            link_module_dictionary={
                "FakeModule1": ("my_fake_tag1", "Build02", None, None),
                # "DependencyModuleA": ("my_fake_tag_a", None, None, None),
                # "DependencyModuleB": ("my_fake_tag_b", None, None, None),
                "FakeModule2": ("my_fake_tag2", None, None, None),
            },
            default_branch="fake_default_branch",
        )

        mockito.verify(self.__mock_file_system).make_directory(path="FakePackage-blah/src")

    def test_check_out_existing_sandbox_should_raise_exception(self):
        mockito.when(self.__mock_file_system).path_exists("FakePackage-blah").thenReturn(True)

        mockito.when(self.__mock_database_reader).module_dependencies("FakeModule1").thenReturn(set())

        mockito.when(self.__mock_database_reader).module_dependencies("FakeModule2").thenReturn(set())

        sandbox = loose_sandbox.LooseSandbox(
            module_names=["FakeModule1", "FakeModule2"],
            sandbox_path="FakePackage-blah",
            revision_control_system=self.__mock_revision_control_system,
            file_system=self.__mock_file_system,
            database_reader=self.__mock_database_reader,
            repository_url="repository_url",
            configuration_writer=self.__mock_configuration_writer,
            default_branch="fake_default_branch",
            release_directory=None,
        )
        from yam import yam_exception

        with self.assertRaises(yam_exception.YamException):
            sandbox.check_out()

    def test_dependencies(self):
        def resolve(node):
            if node == 0:
                return {1, 2}
            elif node == 1:
                return {5}
            elif node == 2:
                return {0}
            elif node == 5:
                return {100, 101, 102}
            else:
                return set()

        self.assertEqual({100, 101, 102}, client._recursive_dependencies(5, resolve))

        self.assertEqual({5, 100, 101, 102}, client._recursive_dependencies(1, resolve))

        self.assertEqual({0, 1, 2, 5, 100, 101, 102}, client._recursive_dependencies(0, resolve))

        self.assertEqual(set(), client._recursive_dependencies(102, resolve))


if __name__ == "__main__":
    unittest.main()
