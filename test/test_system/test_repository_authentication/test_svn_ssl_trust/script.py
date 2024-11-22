from __future__ import print_function

import contextlib
from distutils.version import StrictVersion
import getpass
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


@contextlib.contextmanager
def server_context():
    """Yield Apache server."""
    # Unset configuration file environment variables as they may interfere.
    if "YAM_PROJECT_CONFIG_DIR" in os.environ:
        del os.environ["YAM_PROJECT_CONFIG_DIR"]
    if "YAM_PROJECT" in os.environ:
        del os.environ["YAM_PROJECT"]

    temporary_file_path = os.path.realpath(tempfile.mkdtemp(dir="."))

    os.chmod(temporary_file_path, 0o755)

    repository_path = os.path.join(temporary_file_path, "temporary_repository")
    subprocess.call(["svnadmin", "create", repository_path])

    # Start Apache server
    server_is_up = False
    num_tries_left = 10
    while not server_is_up:
        sys.stderr.write(".")

        host_and_port = "127.0.0.1:{port}".format(port=network_port.unused_port())

        # Create directory for Apache
        apache_path = os.path.join(
            temporary_file_path,
            tempfile.mkdtemp(dir=temporary_file_path, prefix="apache"),
        )

        os.chmod(apache_path, 0o755)

        _create_apache_configuration(
            apache_path=apache_path,
            host_and_port=host_and_port,
            repository_path=repository_path,
        )

        # Note that we don't run in single-process mode (-X) because it
        # leaks semaphores (see ipcs -s).
        apache_arguments = ["/usr/sbin/httpd", "-d", apache_path]

        # Check configuration syntax
        debug = True
        with open(os.devnull, "w") as dev_null:
            assert (
                subprocess.call(
                    apache_arguments + ["-t"],
                    stderr=None if debug else dev_null,
                )
                == 0
            )

        assert subprocess.call(apache_arguments) == 0

        for i in range(10):
            with open(os.devnull, "w") as dev_null:
                server_is_up = 0 == subprocess.call(
                    [
                        "wget",
                        "{host_and_port}".format(host_and_port=host_and_port),
                        "-O",
                        "/dev/null",
                    ],
                    stderr=dev_null,
                )
            if server_is_up:
                break
            time.sleep(0.1)

        if num_tries_left <= 0:
            print(
                "httpd failed; see {}".format(os.path.join(apache_path, "logs", "error_log")),
                file=sys.stderr,
            )
            assert False
        else:
            num_tries_left -= 1

    assert host_and_port
    yield "https://{host_and_port}".format(host_and_port=host_and_port)

    subprocess.call(apache_arguments + ["-k", "graceful-stop"])

    # Clean up semaphores left lying around by httpd (see ipcs -s).
    shutil.rmtree(path=temporary_file_path, ignore_errors=True)


def _apache_version():
    process = subprocess.Popen(["httpd", "-v"], stdout=subprocess.PIPE)
    first_line = process.communicate()[0].decode("utf-8").splitlines()[0]
    version_word = first_line.split("version: ")[1]

    return StrictVersion(version_word.split("/")[1].split()[0])


class SVNLogin(unittest.TestCase):
    @unittest.skipIf(
        _apache_version() > StrictVersion("2.4"),
        "This test does not work on newer Apache httpd",
    )
    def test_accept_ssl_certificate(self):
        with server_context() as repository_url:
            p = spawnu(
                " ".join(
                    [
                        PYAM_PATH,
                        "--database-connection=fake:0/fake",
                        "--default-repository-url={url}".format(url=repository_url),
                        "test",
                    ]
                ),
                # Run it outside the sandbox to avoid the ssh
                # test.
                cwd="/",
                timeout=None,
            )

            # Set debug to True to output what pexpect sees
            debug = True
            if debug:
                p.logfile = sys.stdout

            # Special characters are escaped as to not trigger regular
            # expression
            p.expect("\(R\)eject.* +\(t\)emporarily.* +accept +\(p\)ermanently\?")

            # Only temporarily accept the certificate as we do not want to touch
            # ~/.subversion
            p.sendline("t")

            p.expect("succeeded")


def _create_apache_configuration(apache_path, host_and_port, repository_path):
    apache_conf_path = os.path.join(apache_path, "conf")

    os.mkdir(apache_conf_path)
    os.symlink("/etc/httpd/conf/magic", os.path.join(apache_conf_path, "magic"))

    os.mkdir(os.path.join(apache_path, "conf.d"))
    os.mkdir(os.path.join(apache_path, "logs"))
    os.mkdir(os.path.join(apache_path, "run"))
    os.symlink("/etc/httpd/modules", os.path.join(apache_path, "modules"))

    ssl_path = os.path.join(apache_path, "ssl")
    os.mkdir(ssl_path)

    with open(os.path.join(ssl_path, "httpd.pem"), "w") as f:
        f.write(
            """-----BEGIN CERTIFICATE-----
MIID2zCCAsOgAwIBAgIJAJWnWA6c+KEMMA0GCSqGSIb3DQEBBQUAMIGDMQswCQYD
VQQGEwJVUzELMAkGA1UECAwCQ0ExFDASBgNVBAcMC0xvcyBBbmdlbGVzMRMwEQYD
VQQKDApNeSBDb21wYW55MRAwDgYDVQQLDAdNeSBVbml0MRIwEAYDVQQDDAkxMjcu
MC4wLjExFjAUBgkqhkiG9w0BCQEWB25vZW1haWwwHhcNMTExMTIxMDcyMDMwWhcN
MTIxMTIwMDcyMDMwWjCBgzELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkNBMRQwEgYD
VQQHDAtMb3MgQW5nZWxlczETMBEGA1UECgwKTXkgQ29tcGFueTEQMA4GA1UECwwH
TXkgVW5pdDESMBAGA1UEAwwJMTI3LjAuMC4xMRYwFAYJKoZIhvcNAQkBFgdub2Vt
YWlsMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzh23VLzh+P1I1CGZ
KNR8ndQrPjk7K3TQGy5i7mxP4PsO04+uZBKO1Xib6162G6gKowox7xxkVbusr2pf
N4aK6md9/bEivkaPJKl+gwHj7rmrFZ279j13rd+iMQPEQIeZh97nhzsRtV5HPV2m
Rdbk5NSQgaUobKHsc6r4Gb4IPEzb6WRsaGgsnl4SBxWoTNc0UTZI5PjQTaGWZj3o
a0iTAcKYrxLx/neflIYy1ERRJfIDbX+X8DjwGgIEmL8WqBHaKJTJ5niW8SUGsWCo
JJizBJyj8CuV+3HG2RQ9K0ATNMf1qMgT+RQaQgRuzh9jPgVD58H/PEaxCl6xocqQ
MIe36wIDAQABo1AwTjAdBgNVHQ4EFgQUuVDRCuUI/hegs42Sa6w5ju5GEJUwHwYD
VR0jBBgwFoAUuVDRCuUI/hegs42Sa6w5ju5GEJUwDAYDVR0TBAUwAwEB/zANBgkq
hkiG9w0BAQUFAAOCAQEAy0x8+XN3rGqrRlKMGJH+imLi808Mr2AgoOLEfGi0zm2+
4OPBAzVPW6bfe67UV7a9ZgFT4/sAcmE2LeJXldqG0lX+u27XtS1u9y1JIBs+wNgV
/rPT/WteTZiI58H4mS9zs9c1K4cbPxhhl2pR8buSf5cnDXCQDGLCBLaHyQObS+NF
q7PJ75cmLkozSji2KnmXILnByfHdPTQn/7Jo44fxhNjvlZmkjwLPgKIZTxo41mFX
761q7AXWn2ZKkZb6NPj2qS3xSkcoc0ZNLLUFBggYGpXQbxQK+Q2xy8DaTxxAd3uc
x7uQ3lJAtjE5L50R/GRE9QP77H7O9JxilAvOuIXxtg==
-----END CERTIFICATE-----
"""
        )

    with open(os.path.join(ssl_path, "httpd.key"), "w") as f:
        f.write(
            """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDOHbdUvOH4/UjU
IZko1Hyd1Cs+OTsrdNAbLmLubE/g+w7Tj65kEo7VeJvrXrYbqAqjCjHvHGRVu6yv
al83horqZ339sSK+Ro8kqX6DAePuuasVnbv2PXet36IxA8RAh5mH3ueHOxG1Xkc9
XaZF1uTk1JCBpShsoexzqvgZvgg8TNvpZGxoaCyeXhIHFahM1zRRNkjk+NBNoZZm
PehrSJMBwpivEvH+d5+UhjLURFEl8gNtf5fwOPAaAgSYvxaoEdoolMnmeJbxJQax
YKgkmLMEnKPwK5X7ccbZFD0rQBM0x/WoyBP5FBpCBG7OH2M+BUPnwf88RrEKXrGh
ypAwh7frAgMBAAECggEAMAmI8rzaxZbyZE44TeXH7VjHg0b/XU9qOQuEjyC7NSoN
+IyiDjytAV+Mpzx5oNR3NixoGtw5HioRQwi9jElVEvBv0rJ38HStY9QE4i+MmdS3
5N/QMMF+pQ1b1aSVFp0D0UDIISJJLEX+wHSVDe3ZhuNrkmuVkkviucp87DL35GVy
P3qelNHyKg9l9lVh1RwUHX62Drq0lRP7TWFQOmm8sOxorRqMauhZJuigGx7O+oVU
6e6kRuzCJn9Iw5IYMlXr5UmPft8wOXVTpHuARuLNzRLNxRtLQNsDrL60HvvUMQZY
yAEU7BzlfzYI38mWIhV2KQMMKsq0foOF+y+UGCEOAQKBgQDn8edoREW1A8ObcjaT
niCvX4CSfhkg0SackIXcCXSJ1OIRsDNAGvl8ui+3X4ChtRebnKcWtDGm9dEqM/C1
xe5yZoakZi6HBL0gxTcEbvbE8vJKgKAgff6M//2sRg+mE9CxGL6wtLepplQBTB/m
YxA0/aBRtIz5xH71qTfsmQZ9awKBgQDjfg+JGEr6RMwBw+mR8Thb9IMAsZzjv8f3
ohYU1YKHGkm5FYwI0VhSzOZNzgP6Gnbbiu2nMAK1ddLwiW4kvUv2PFDF7OthZvdZ
gZSGeQIoQ3evWgGl5FJVPRvH3/6G/iDneAm1Gvc2g7IrX7LCarxWLB07uqEXBaW8
D0YfY8vPgQKBgD20ekaf2xeT/8br9J8C81kUhCT0zQSQ/7+pJyNplIpSiy3/fTLx
uiu3cJhNHPBoN/abD0yX9ZmgTdv3Y3NIS+49XlaAJKKg3RvJu6A/UQEGTPULEQ5z
1nN2ausY3HLnVJ64oYprGW1VpYWO1fG5qwcd7jeuW87aupfqQ8l60GIvAoGBAJqk
aN8i2mUCO0O/75i7xzoLHrpsAmB3T/GwBx6mfRJl9lOQqB6eYFH4411kfCOZtc5L
xH1wD4dWzsugQHVNEMQUADxrbx5JJj977ID05ViFdGiI4LHqYWV8ItReGeGeArQW
T1MDP6WZJJaDeTrb36ccWcrudO73cdBC+cIAzt0BAoGAT3I6XAAnrdG4ldBbg6Tu
LbUGgCxSI0u+Nc1Rumt1b+fvb3ruCNHndJiHUtRuWsjlVMOHuHyXGO1Bfhq1u425
h6HFJ8lFm1uBcAApVn6b3sAiljoAJ/vUb6o9Bb/h5KD0QRCt+/gt4oHMMl6340VA
B9yhK51KQqGCvPVWZNODh8U=
-----END PRIVATE KEY-----
"""
        )

    if _apache_version() > StrictVersion("2.4"):
        extra_configuration = """
LoadModule mpm_worker_module    modules/mod_mpm_worker.so
LoadModule access_compat_module modules/mod_access_compat.so
LoadModule authn_core_module    modules/mod_authn_core.so
LoadModule authz_core_module    modules/mod_authz_core.so
LoadModule unixd_module         modules/mod_unixd.so

DefaultRuntimeDir "{apache_path}"
""".format(
            apache_path=os.path.abspath(apache_path)
        )
    else:
        extra_configuration = ""

    with open(os.path.join(apache_conf_path, "httpd.conf"), "w") as f:
        f.write(
            """
ServerTokens OS

ServerRoot "{apache_path}"

PidFile run/httpd.pid

Timeout 60

KeepAlive Off

MaxKeepAliveRequests 100

KeepAliveTimeout 5

##
## Server-Pool Size Regulation (MPM specific)
##

# prefork MPM
# StartServers: number of server processes to start
# MinSpareServers: minimum number of server processes which are kept spare
# MaxSpareServers: maximum number of server processes which are kept spare
# ServerLimit: maximum value for MaxClients for the lifetime of the server
# MaxClients: maximum number of server processes allowed to start
# MaxRequestsPerChild: maximum number of requests a server process serves
<IfModule prefork.c>
StartServers       1
MinSpareServers    1
MaxSpareServers   20
ServerLimit      256
MaxClients       256
MaxRequestsPerChild  4000
</IfModule>

# worker MPM
# StartServers: initial number of server processes to start
# MaxClients: maximum number of simultaneous client connections
# MinSpareThreads: minimum number of worker threads which are kept spare
# MaxSpareThreads: maximum number of worker threads which are kept spare
# ThreadsPerChild: constant number of worker threads in each server process
# MaxRequestsPerChild: maximum number of requests a server process serves
<IfModule worker.c>
StartServers         1
MaxClients         300
MinSpareThreads     25
MaxSpareThreads     75
ThreadsPerChild     25
MaxRequestsPerChild  0
</IfModule>

#
# Listen: Allows you to bind Apache to specific IP addresses and/or
# ports, instead of the default. See also the <VirtualHost>
# directive.
#
# Change this to Listen on specific IP addresses as shown below to
# prevent Apache from glomming onto all bound IP addresses.
#
Listen {host_and_port}

#
# Dynamic Shared Object (DSO) Support
#
# To be able to use the functionality of a module which was built as a DSO you
# have to place corresponding `LoadModule' lines at this location so the
# directives contained in it are actually available _before_ they are used.
# Statically compiled modules (those listed by `httpd -l') do not need
# to be loaded here.
#
# Example:
# LoadModule foo_module modules/mod_foo.so
#
LoadModule auth_basic_module  modules/mod_auth_basic.so
LoadModule auth_digest_module modules/mod_auth_digest.so
LoadModule authn_file_module  modules/mod_authn_file.so
LoadModule authz_user_module  modules/mod_authz_user.so
LoadModule authz_host_module  modules/mod_authz_host.so
LoadModule authz_owner_module modules/mod_authz_owner.so

LoadModule log_config_module  modules/mod_log_config.so
LoadModule mime_magic_module  modules/mod_mime_magic.so
LoadModule mime_module        modules/mod_mime.so
LoadModule deflate_module     modules/mod_deflate.so
LoadModule ssl_module         modules/mod_ssl.so
LoadModule dir_module         modules/mod_dir.so

LoadModule dav_module         modules/mod_dav.so
LoadModule dav_svn_module     modules/mod_dav_svn.so
LoadModule authz_svn_module   modules/mod_authz_svn.so

{extra_configuration}

#
# If you wish httpd to run as a different user or group, you must run
# httpd as root initially and it will switch.
#
# User/Group: The name (or #number) of the user/group to run httpd as.
#  . On SCO (ODT 3) use "User nouser" and "Group nogroup".
#  . On HPUX you may not be able to use shared memory as nobody, and the
#    suggested workaround is to create a user www and use that user.
#  NOTE that some kernels refuse to setgid(Group) or semctl(IPC_SET)
#  when the value of (unsigned)Group is above 60000;
#  don't use Group #-1 on these systems!
#
User {real_user}
#Group apache

### Section 2: 'Main' server configuration
#
# The directives in this section set up the values used by the 'main'
# server, which responds to any requests that aren't handled by a
# <VirtualHost> definition.  These values also provide defaults for
# any <VirtualHost> containers you may define later in the file.
#
# All of these directives may appear inside <VirtualHost> containers,
# in which case these default settings will be overridden for the
# virtual host being defined.
#

#
# ServerAdmin: Your address, where problems with the server should be
# e-mailed.  This address appears on some server-generated pages, such
# as error documents.  e.g. admin@your-domain.com
#
ServerAdmin root@localhost

#
# ServerName gives the name and port that the server uses to identify itself.
# This can often be determined automatically, but we recommend you specify
# it explicitly to prevent problems during startup.
#
# If this is not set to valid DNS name for your host, server-generated
# redirections will not work.  See also the UseCanonicalName directive.
#
# If your host doesn't have a registered DNS name, enter its IP address here.
# You will have to access it by its address anyway, and this will make
# redirections work in a sensible way.
#
ServerName fakename

#
# UseCanonicalName: Determines how Apache constructs self-referencing
# URLs and the SERVER_NAME and SERVER_PORT variables.
# When set "Off", Apache will use the Hostname and Port supplied
# by the client.  When set "On", Apache will use the value of the
# ServerName directive.
#
UseCanonicalName Off

#
# DocumentRoot: The directory out of which you will serve your
# documents. By default, all requests are taken from this directory, but
# symbolic links and aliases may be used to point to other locations.
#
DocumentRoot "/var/www/html"

#
# TypesConfig describes where the mime.types file (or equivalent) is
# to be found.
#
TypesConfig /etc/mime.types

#
# The mod_mime_magic module allows the server to use various hints from the
# contents of the file itself to determine its type.  The MIMEMagicFile
# directive tells the module where the hint definitions are located.
#
<IfModule mod_mime_magic.c>
#   MIMEMagicFile /usr/share/magic.mime
    MIMEMagicFile conf/magic
</IfModule>

#
# ErrorLog: The location of the error log file.
# If you do not specify an ErrorLog directive within a <VirtualHost>
# container, error messages relating to that virtual host will be
# logged here.  If you *do* define an error logfile for a <VirtualHost>
# container, that host's errors will be logged there and not here.
#
ErrorLog logs/error_log

#
# LogLevel: Control the number of messages logged to the error_log.
# Possible values include: debug, info, notice, warn, error, crit,
# alert, emerg.
#
LogLevel debug

<Location />
  DAV svn
  SVNPath {repository_path}
</Location>

### Section 3: Virtual Hosts

# SSL files created via:
# openssl req -new -x509 -days 365 -nodes -out httpd.pem -keyout httpd.key
<VirtualHost {host_and_port}>
     SSLEngine On
     SSLCertificateFile ssl/httpd.pem
     SSLCertificateKeyFile ssl/httpd.key
</VirtualHost>
""".format(
                real_user=getpass.getuser(),
                apache_path=os.path.abspath(apache_path),
                repository_path=os.path.abspath(repository_path),
                host_and_port=host_and_port,
                extra_configuration=extra_configuration,
            )
        )


if __name__ == "__main__":
    unittest.main()
