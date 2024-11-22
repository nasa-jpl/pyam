"""Network port functions."""


def unused_port():
    """Return a port that isn't being used."""
    lowest_port = 10000
    highest_port = 40000
    import random

    start_num = random.randint(lowest_port, highest_port)

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
