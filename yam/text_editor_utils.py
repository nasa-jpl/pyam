"""Contains functions for getting input from a text editor."""

from __future__ import absolute_import

import tempfile
import os
import shlex
import subprocess


def retrieve_text(initial_text, editor):
    """Open editor with initial_text as the initial text.

    Return the data that the user saves in the text editor.

    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yamtemp", delete=False) as output_file:
        filename = output_file.name
        output_file.write(initial_text)

    subprocess.call(shlex.split(editor) + [filename], shell=False)

    with open(filename, "r") as input_file:
        final_text = input_file.read()

    os.remove(filename)

    return final_text
