#!/usr/bin/env python
"""Fake SMTP server."""


from __future__ import print_function

import base64
import os
from aiosmtpd.controller import Controller
import sys


def write_atomically(filename, contents):
    """Write contents atomically to file.

    This is necessary if we want the file to be complete upon reading.

    """
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", dir=os.path.dirname(filename), delete=False) as temp_file:
        temp_file.write(contents)

        # Flush is necessary before rename. See
        # stackoverflow.com/questions/7433057/is-rename-without-fsync-safe
        temp_file.flush()
        os.fsync(temp_file.fileno())

    os.rename(temp_file.name, filename)


def start_server(port_filename, mail_dump_filename):
    """Start the smtp server. aiosmtpd does this in a separate thread. Therefore, register a function at exit to stop this other thread."""
    from atexit import register

    # Start fake server
    handler = FilePrintingSMTPServer(mail_dump_filename)
    controller = Controller(handler, hostname="127.0.0.1")

    controller.start()
    register(controller.stop)

    write_atomically(
        filename=port_filename,
        contents=str(controller.port),
    )


class FilePrintingSMTPServer:
    def __init__(self, mail_dump_filename):
        self.__mail_dump_filename = mail_dump_filename

    async def handle_DATA(self, server, session, envelope):
        data = envelope.content.replace(b"\r\n", b"\n")
        with open(self.__mail_dump_filename, "a") as f:
            if sys.version_info.major >= 3:
                (header, body) = data.rsplit(b"\n\n", 1)
                f.write(header.decode("utf-8"))
            else:
                (header, body) = data.rsplit(b"\n\n", 1)
                f.write(header)
            f.write("\n\n")
            try:
                if sys.version_info[0] == 2:
                    f.write(base64.decodestring(body))
                else:
                    text = base64.decodebytes(body)
                    f.write(text.decode("utf-8"))
            except Exception:
                f.write(body)
        return "250 OK"


def main():
    from time import sleep
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "port_filename",
        help="write a file with the server port number when it is ready",
    )
    parser.add_argument("mail_dump_filename", help="write emails to this location")
    args = parser.parse_args()

    start_server(
        port_filename=args.port_filename,
        mail_dump_filename=args.mail_dump_filename,
    )
    while True:
        # Keep the email server open
        sleep(1)


if __name__ == "__main__":
    main()
