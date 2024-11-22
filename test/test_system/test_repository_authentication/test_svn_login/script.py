from __future__ import unicode_literals

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

try:
    from pexpect import spawnu
except ImportError:
    from pexpect import spawn as spawnu

sys.path.append("../../../common")
import network_port


PYAM_PATH = os.path.realpath("../../../../pyam")


class SVNLogin(unittest.TestCase):
    def setUp(self):
        # Unset configuration file environment variables as they may interfere.
        if "YAM_PROJECT_CONFIG_DIR" in os.environ:
            del os.environ["YAM_PROJECT_CONFIG_DIR"]
        if "YAM_PROJECT" in os.environ:
            del os.environ["YAM_PROJECT"]

        self.__temporary_file_path = os.path.realpath(tempfile.mkdtemp(dir="."))

        os.chmod(self.__temporary_file_path, 0o755)

        # Create a password protected repository
        repository_path = os.path.join(self.__temporary_file_path, "temporary_repository")
        subprocess.call(["svnadmin", "create", repository_path])

        with open(os.path.join(repository_path, "conf", "svnserve.conf"), "w") as f:
            f.write(
                """[general]
anon-access = none
auth-access = write
password-db = passwd
"""
            )

        self.__username = "my_user"
        self.__password = "my_password"

        with open(os.path.join(repository_path, "conf", "passwd"), "w") as f:
            f.write(
                """[users]
{user} = {password}
""".format(
                    user=self.__username, password=self.__password
                )
            )

        # Start svnserve
        debug = False
        self.__dev_null = None if debug else open(os.devnull, "w")
        server_is_up = False
        while not server_is_up:
            sys.stderr.write(".")

            port = network_port.unused_port()

            self.__svnserve = subprocess.Popen(
                [
                    "svnserve",
                    "--foreground",
                    "--daemon",
                    "--listen-port={port}".format(port=port),
                    "--root={path}".format(path=repository_path),
                ],
                stdout=self.__dev_null,
                stderr=self.__dev_null,
            )

            self.__repository_url = "svn://127.0.0.1:{port}".format(port=port)

            for i in range(10):
                if self.__svnserve.poll() is not None:
                    # If svnserve dies, we need to try recreating it by going
                    # back to the top of the (outer) while loop.
                    break

                with open(os.devnull, "w") as dev_null:
                    server_is_up = 0 == subprocess.call(
                        [
                            "svn",
                            "ls",
                            self.__repository_url,
                            "--username={user}".format(user=self.__username),
                            "--password={pw}".format(pw=self.__password),
                            "--no-auth-cache",
                        ],
                        stdout=dev_null,
                        stderr=dev_null,
                    )
                if server_is_up:
                    break
                time.sleep(0.1)

        assert self.__repository_url

    def tearDown(self):
        self.__svnserve.terminate()

        if self.__dev_null:
            self.__dev_null.close()

        shutil.rmtree(path=self.__temporary_file_path, ignore_errors=True)

    def test_login(self):
        p = spawnu(
            " ".join(
                [
                    PYAM_PATH,
                    "--repository-username={username}".format(username=self.__username),
                    "--database-connection=fake:0/fake",
                    "--default-repository-url={url}".format(url=self.__repository_url),
                    "test",
                ]
            ),
            # Run it outside the sandbox to avoid the ssh test.
            cwd="/",
            timeout=None,
        )

        # Set debug to True to output what pexpect sees
        debug = False
        if debug:
            p.logfile = sys.stdout

        p.expect("Password.*:")
        p.sendline(self.__password)
        p.expect("Store password.*:")
        p.sendline("n")

        p.expect("succeeded")

    def test_login_with_initially_incorrect_username(self):
        p = spawnu(
            " ".join(
                [
                    PYAM_PATH,
                    "--repository-username=fakeuser123",
                    "--database-connection=fake:0/fake",
                    "--default-repository-url={url}".format(url=self.__repository_url),
                    "test",
                ]
            ),
            # Run it outside the sandbox to avoid the ssh test.
            cwd="/",
            timeout=None,
        )

        # Set debug to True to output what pexpect sees
        debug = False
        if debug:
            p.logfile = sys.stdout

        p.expect("Password.*:")
        p.sendline("junk")
        p.expect("Store password.*:")
        p.sendline("n")

        p.expect("Username:")
        p.sendline(self.__username)
        p.expect("Password.*:")
        p.sendline(self.__password)
        p.expect("Store password.*:")
        p.sendline("n")

        p.expect("succeeded")

    def test_login_failure(self):
        p = spawnu(
            " ".join(
                [
                    PYAM_PATH,
                    "--repository-username=fakeuser123",
                    "--database-connection=fake:0/fake",
                    "--default-repository-url={url}".format(url=self.__repository_url),
                    "test",
                ]
            ),
            # Run it outside the sandbox to avoid the ssh test.
            cwd="/",
            timeout=None,
        )

        # Set debug to True to output what pexpect sees
        debug = False
        if debug:
            p.logfile = sys.stdout

        p.expect("Password.*:")
        p.sendline("junk")
        p.expect("Store password.*:")
        p.sendline("n")

        p.expect("Username:")
        p.sendline("fakeuser123")
        p.expect("Password.*:")
        p.sendline("junk")
        p.expect("Store password.*:")
        p.sendline("n")

        # User gives up by sending EOF
        p.expect("Username:")
        p.sendeof()

        p.expect("failed")


if __name__ == "__main__":
    unittest.main()
