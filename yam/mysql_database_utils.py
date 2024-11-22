"""Used for connecting to MySQL."""

from __future__ import absolute_import

from mysql import connector


try:

    class MySQLCursorDict(connector.cursor.MySQLCursorDict):
        """Cursor that returns dictionaries instead of tuples."""

        def _row_to_python(self, rowdata, desc=None):  # pragma: NO COVER
            """Override MySQLCursor._row_to_python() to return dictionary."""
            # pylint: disable=W0212,super-on-old-class
            row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)  # pragma: NO COVER
            if row:  # pragma: NO COVER
                return {k: decode(v) for (k, v) in row.items()}  # pragma: NO COVER
            return None  # pragma: NO COVER

except AttributeError:
    # For backward compatibility with mysql-connector-python 1.x.
    class MySQLCursorDict(connector.cursor.MySQLCursor):
        """Cursor that returns dictionaries instead of tuples."""

        def _row_to_python(self, rowdata, desc=None):
            """Override MySQLCursor._row_to_python() to return dictionary."""
            # pylint: disable=W0212,bad-super-call
            row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
            if row:
                return {k: decode(v) for (k, v) in zip(self.column_names, row)}
            return None  # pragma: NO COVER


def decode(byte_string):
    """Return decoded string if necessary."""
    try:
        return byte_string.decode("utf-8")
    except AttributeError:
        return byte_string
