"""Contains functions for port forwarding."""

from __future__ import absolute_import

import socket
import subprocess
import time

from yam import yam_exception


def port_is_open(port):
    """Return True if port is open."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(("127.0.0.1", port))
    s.close()
    return result == 0


def unused_port():
    """Return a port that isn't being used."""
    lowest_port = 10000
    highest_port = 40000
    import random

    start_num = random.randint(lowest_port, highest_port)

    for offset in range(lowest_port, highest_port):
        port = (offset + start_num) % (highest_port - lowest_port)
        port += lowest_port

        if not port_is_open(port):
            # Port is not open (and we assume it is available).
            return port

    return None  # pragma: NO COVER


def create_port_forwarding_process(remote_port, local_port, remote_hostname, gateway_hostname, num_tries=10):
    """Return process that runs ssh port forwarding.

    It will block until the port forwarding is running.

    """
    process = None
    while num_tries > 0 and not port_is_open(local_port):
        last_try = num_tries <= 1

        if not process or process.poll() is not None:
            process = subprocess.Popen(
                ["ssh"]
                + ([] if last_try else ["-q"])
                + [
                    "-o",
                    "ExitOnForwardFailure=yes",
                    "-L",
                    "{}:{}:{}".format(local_port, remote_hostname, remote_port),
                    "-N",
                    gateway_hostname,
                ]
            )

            num_tries -= 1
        else:
            time.sleep(0.01)  # pragma: NO COVER

    if not port_is_open(local_port):
        raise yam_exception.YamException(
            "Failed to establish ssh tunnel to "
            "{remote_hostname}:{remote_port} from "
            "local port {local_port}".format(
                remote_hostname=remote_hostname,
                remote_port=remote_port,
                local_port=local_port,
            )
        )

    return process  # pragma: NO COVER
