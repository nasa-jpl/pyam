"""Test block_until_pyam_release."""

import locale
import unittest
import subprocess


class BlockUntilPyamReleaseTests(unittest.TestCase):
    def test_command(self):
        self.assertEqual("hello\n", run(["--test", "--loop-duration=0", "echo hello"])[0])

    def test_no_command_should_imply_no_loop(self):
        run(["--test"])

    def test_loop(self):
        foos = run(["--test", "--loop-duration=.5", "echo foo"])[0].split("\n")
        self.assertIn("foo", foos)
        self.assertGreater(len(foos), 1)


def run(arguments):
    """Return output."""
    process = subprocess.Popen(
        ["../../../pyam-block-until-release"] + arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        output = process.communicate()
        return [text.decode(locale.getpreferredencoding(False)) for text in output]
    finally:
        assert 0 == process.returncode


if __name__ == "__main__":
    unittest.main()
