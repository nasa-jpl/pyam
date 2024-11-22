from __future__ import print_function

import unittest
import sys


class EmailUtilsTestCase(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""

    def tearDown(self):
        """Automatically called after each test* method."""

    def test_send_email(self):
        port, smtp_server, controller = start_server(return_status="250 OK")

        from yam import email_utils

        email_utils.send_email(
            subject="email subject",
            body="email body",
            from_address="fake.sender@127.0.0.1",
            to_addresses=[
                "fake.receiver1@127.0.0.1",
                "fake.receiver2@127.0.0.1",
            ],
            hostname="127.0.0.1",
            port=port,
        )

        # Stop the SMTP server after email is sent
        controller.stop()

        # Check the email
        self.assertEqual(smtp_server.envelope.mail_from, "fake.sender@127.0.0.1")
        self.assertEqual(
            smtp_server.envelope.rcpt_tos,
            ["fake.receiver1@127.0.0.1", "fake.receiver2@127.0.0.1"],
        )
        self.assertIn(
            b"To: fake.receiver1@127.0.0.1, fake.receiver2@127.0.0.1",
            smtp_server.envelope.content,
        )
        self.assertIn(b"Subject: email subject", smtp_server.envelope.content)

    def test_send_email_to_non_existent_host_will_raise_exception(self):
        # Create a fake server that returns an error status
        port, _, controller = start_server(return_status="441 Internal confusion")

        from yam import email_utils

        with self.assertRaises(email_utils.EmailException):
            email_utils.send_email(
                subject="email subject",
                body="email body",
                from_address="fake.sender@127.0.0.1",
                to_addresses=["fake.receiver1@nonexistentdomain132532352352532423423424.com"],
                hostname="127.0.0.1",
                port=port,
            )

        # Stop the SMTP server after email is sent
        controller.stop()


def unused_port():
    """Return a port that isn't being used."""
    lowest_port = 1024
    highest_port = 49151
    import os

    start_num = 10000 + os.getpid()

    for offset in range(lowest_port, highest_port):
        port = (offset + start_num) % (highest_port - lowest_port)
        port += lowest_port

        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()

        if result != 0:
            # Port is not open (and we assume it is available).
            return port

    return None


def start_server(return_status):
    """Return (port, smtp_server, server_thread)."""
    # Start fake server
    smtp_server = None
    # Loop in case of race condition with other processes trying to get an
    # available port
    while not smtp_server:
        port = unused_port()
        try:
            smtp_server = FakeSMTPServer(return_status)
        except IOError:
            smtp_server = None

    controller = Controller(smtp_server, hostname="127.0.0.1", port=port)
    controller.start()

    return (port, smtp_server, controller)


from aiosmtpd.controller import Controller


class FakeSMTPServer(Controller):
    def __init__(self, return_status):
        self.__return_status = return_status

    async def handle_DATA(self, server, session, envelope):
        self.server = server
        self.session = session
        self.envelope = envelope
        return self.__return_status


if __name__ == "__main__":
    unittest.main()
