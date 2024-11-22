import unittest
import datetime

import mockito

from yam import saving_utils


class Tests(unittest.TestCase):
    def test_update_release_notes(self):
        from yam import file_system

        mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

        from yam import revision_control_system

        mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        mockito.when(mock_file_system).path_exists("my_module_path/ReleaseNotes").thenReturn(True)

        mockito.when(mock_file_system).read_file(filename=mockito.any()).thenReturn(
            "header\n\nRelease R1-00a:\n\n    blah"
        )

        saving_utils.update_release_notes(
            message="my message",
            new_revision_tag="new_revision_tag",
            date_time=datetime.datetime(2000, 1, 2, 3, 4, 5),
            file_system=mock_file_system,
            path="my_module_path",
            revision_control_system=mock_revision_control_system,
        )

        mockito.verify(mock_file_system).write_to_file(
            string_data=mockito.contains("my message"), filename=mockito.any()
        )

    def test_update_release_notes_should_work_with_empty_release_notes(self):
        from yam import file_system

        mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

        from yam import revision_control_system

        mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        mockito.when(mock_file_system).path_exists("my_module_path/ReleaseNotes").thenReturn(True)

        mockito.when(mock_file_system).read_file(filename=mockito.any()).thenReturn("")

        saving_utils.update_release_notes(
            message="my message",
            new_revision_tag="new_revision_tag",
            date_time=datetime.datetime(2000, 1, 2, 3, 4, 5),
            file_system=mock_file_system,
            path="my_module_path",
            revision_control_system=mock_revision_control_system,
        )

        mockito.verify(mock_file_system).write_to_file(
            string_data=mockito.contains("my message"), filename=mockito.any()
        )

    def test_update_release_notes_should_work_even_if_entries_are_missing(self):
        from yam import file_system

        mock_file_system = mockito.mock(file_system.FileSystem, strict=False)

        from yam import revision_control_system

        mock_revision_control_system = mockito.mock(revision_control_system.RevisionControlSystem, strict=False)

        mockito.when(mock_file_system).path_exists("my_module_path/ReleaseNotes").thenReturn(True)

        mockito.when(mock_file_system).read_file(filename=mockito.any()).thenReturn("my header\n")

        saving_utils.update_release_notes(
            message="my message",
            new_revision_tag="new_revision_tag",
            date_time=datetime.datetime(2000, 1, 2, 3, 4, 5),
            file_system=mock_file_system,
            path="my_module_path",
            revision_control_system=mock_revision_control_system,
        )

        mockito.verify(mock_file_system).write_to_file(
            string_data=mockito.contains("my message"), filename=mockito.any()
        )


if __name__ == "__main__":
    unittest.main()
