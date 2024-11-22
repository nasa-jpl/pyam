import unittest
from yam import text_editor_utils


class TextEditorUtilsTestCase(unittest.TestCase):
    def test_filter_module_text_editor(self):
        self.assertEqual(
            text_editor_utils.retrieve_text(
                initial_text="my initial text\n123\n",
                editor="./fake_editor.bash",
            ),
            "my initial text\n123\nfake data from fake_editor.bash\nabc\n",
        )


if __name__ == "__main__":
    unittest.main()
