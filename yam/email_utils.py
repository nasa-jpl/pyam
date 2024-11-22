"""Contains function to send email."""

from __future__ import absolute_import

from email.message import EmailMessage


def send_email(subject, body, from_address, to_addresses, hostname, port):
    """Send an email."""
    message = EmailMessage()
    message["To"] = ", ".join(list(to_addresses))
    message["From"] = from_address
    message["Subject"] = subject
    message.set_content(body, subtype="plain", charset="utf-8", cte="8bit")

    from asyncio import run
    from aiosmtplib import send, SMTPException

    try:
        run(
            send(
                message,
                sender=from_address,
                recipients=to_addresses,
                hostname=hostname,
                port=port,
            )
        )
    except (IOError, SMTPException) as exception:
        raise EmailException(
            "Could not send email to {to_addr} on {host}:{port} from "
            "{from_addr}; ".format(
                to_addr=to_addresses,
                host=hostname,
                port=port,
                from_addr=from_address,
            )
            + "Error message: "
            + str(exception)
        )


class EmailException(Exception):
    """Exception raised when sending email fails."""

    def __init__(self, message):
        Exception.__init__(self, message)
