import unittest

from yam import port_utils
from yam import yam_exception


class Tests(unittest.TestCase):
    def test_unused_port(self):
        self.assertGreaterEqual(port_utils.unused_port(), 1024)

    def test_create_port_forwarding_process_with_invalid_gateway(self):
        with self.assertRaises(yam_exception.YamException):
            port_utils.create_port_forwarding_process(
                remote_port=22,
                local_port=port_utils.unused_port(),
                remote_hostname="localhost",
                gateway_hostname="fakefakefake.gov",
            )

    def test_create_port_forwarding_process_with_timeout(self):
        with self.assertRaises(yam_exception.YamException):
            port_utils.create_port_forwarding_process(
                remote_port=22,
                local_port=port_utils.unused_port(),
                remote_hostname="localhost",
                gateway_hostname="shavian.jpl.nasa.gov",
                num_tries=0,
            )


if __name__ == "__main__":
    unittest.main()
