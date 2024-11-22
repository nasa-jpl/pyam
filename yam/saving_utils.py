"""Functions used in saving a module or package."""

import os
import re


def update_release_notes(
    message,
    new_revision_tag,
    date_time,
    file_system,
    path,
    revision_control_system,
):
    """Update and commit the release notes.

    Return the release note entry.

    Set revision_control_system to None to not commit changes.

    """
    filename = os.path.join(path, "ReleaseNotes")

    if not file_system.path_exists(filename):
        return ""

    header_separator_and_rest = re.split(
        pattern=r"(Release R[0-9]+\-[0-9]+)",
        string=file_system.read_file(filename=filename),
        maxsplit=1,
    )
    assert len(header_separator_and_rest) == 1 or len(header_separator_and_rest) == 3
    if len(header_separator_and_rest) != 3:
        header_separator_and_rest += ["", ""]

    release_note_entry = generate_release_note_entry(
        new_revision_tag=new_revision_tag, message=message, date_time=date_time
    )

    file_system.write_to_file(
        string_data="{header}{entry}{separator}{rest}".format(
            header=header_separator_and_rest[0],
            entry=release_note_entry,
            separator=header_separator_and_rest[1],
            rest=header_separator_and_rest[2],
        ),
        filename=filename,
    )

    revision_control_system.check_in(
        path=filename, log_message=f"pyam: Add a {new_revision_tag} release note entry", wmpath=path
    )

    return release_note_entry


def generate_release_note_entry(new_revision_tag, message, date_time):
    """Return full release note entry."""
    if message and message.strip():
        header = "Release {tag} ({date}):".format(tag=new_revision_tag, date=date_time)

        entry = "{header}\n\n{message}".format(header=header, message=indent(message.strip(), "\t"))

        # Normalize whitespace for non-empty entries.
        if entry.strip():
            return entry.strip() + "\n\n"
    else:
        return ""


def indent(text, indentation):
    """Indent each line."""

    def indent_non_empty(line):
        """Indent non-empty line."""
        if line:
            return indentation + line
        else:
            return line

    return "\n".join([indent_non_empty(l) for l in text.split("\n")])
