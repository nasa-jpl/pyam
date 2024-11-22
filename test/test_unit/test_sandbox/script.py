import unittest

import mockito

from yam import configuration_writer
from yam import database_reader
from yam import file_system
from yam import revision_control_system
from yam import sandbox
from yam.module import WorkModuleType


class SandboxTestCase(unittest.TestCase):
    def test_write_sandbox_configuration_with_latest(self):
        mock_database_reader = mockito.mock(database_reader.DatabaseReader, strict=False)

        mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        mock_configuration_writer = mockito.mock(configuration_writer.ConfigurationWriter, strict=False)

        mockito.when(mock_database_reader).latest_module_information(module_name="ModuleA", release=None).thenReturn(
            {"tag": "my_tag1", "build": None}
        )
        mockito.when(mock_database_reader).latest_module_information(module_name="ModuleB", release=None).thenReturn(
            {"tag": "my_tag2", "build": "my_build_id2"}
        )

        sandbox.write_sandbox_configuration_with_latest(
            module_names=["ModuleA", "ModuleB"],
            configuration_filename="my_new.config",
            default_branch="my_default_branch",
            release_directory=None,
            database_reader=mock_database_reader,
            configuration_writer=mock_configuration_writer,
            file_system=None,
            revision_control_system=mock_revision_control_system,
            parent_directory=None,
            progress_callback=lambda _: None,
        )

        # Verify
        mockito.verify(mock_configuration_writer).write_sandbox_configuration(
            configuration_filename="my_new.config",
            link_module_dictionary={
                "ModuleA": ("my_tag1", None, None, None),
                "ModuleB": ("my_tag2", "my_build_id2", None, None),
            },
            work_module_dictionary={},
            default_branch="my_default_branch",
        )

    def test_write_sandbox_configuration_with_latest_with_missing_link_modules(self):
        mock_database_reader = mockito.mock(database_reader.DatabaseReader, strict=False)
        mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

        mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        mock_configuration_writer = mockito.mock(configuration_writer.ConfigurationWriter, strict=False)

        mockito.when(mock_database_reader).latest_module_information(module_name="ModuleA", release=None).thenReturn(
            {"tag": "my_tag1", "build": None}
        )
        mockito.when(mock_database_reader).latest_module_information(module_name="ModuleB", release=None).thenReturn(
            {"tag": "my_tag2", "build": "my_build_id2"}
        )

        mockito.when(mock_database_reader).module_repository_url(mockito.any()).thenReturn("")

        mockito.when(mock_file_system).list_directory(mockito.any()).thenReturn([])

        sandbox.write_sandbox_configuration_with_latest(
            module_names=["ModuleA", "ModuleB"],
            configuration_filename="my_new.config",
            default_branch="my_default_branch",
            release_directory="release_directory",
            database_reader=mock_database_reader,
            configuration_writer=mock_configuration_writer,
            file_system=mock_file_system,
            revision_control_system=mock_revision_control_system,
            parent_directory=None,
            progress_callback=lambda _: None,
        )

        # Verify
        mockito.verify(mock_configuration_writer).write_sandbox_configuration(
            configuration_filename="my_new.config",
            link_module_dictionary={},
            work_module_dictionary={
                "ModuleA": ("my_tag1", ""),
                "ModuleB": ("my_tag2", ""),
            },
            default_branch="my_default_branch",
        )


if __name__ == "__main__":
    unittest.main()
