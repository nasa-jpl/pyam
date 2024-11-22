"""Methods for logging."""

from __future__ import print_function

import traceback
import time
import os
import sys
import errno
import re
import glob
import datetime

from yam import __version__

_inited = False
_dolog = False
_logfile = None


def cull_old_logs(directory):
    """Delete too-old logs.

    Looks at yam logs in a given directory, and deletes all logs older than a
    certain age. The goal is to prevent accumulation of cruft.

    """

    now = datetime.datetime.now()
    for l in glob.glob(directory + "/yamlog.*"):
        m = re.match(r"(?:.*/)?yamlog.\w+-(\d+)_(\d+)_(\d+)__(\d+)_(\d+)_(\d+)", l)
        if m:
            Y, M, D, h, m, s = (
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(5)),
                int(m.group(6)),
            )

            d = datetime.datetime(Y, M, D, h, m, s)
            dt = now - d

            # I delete if older than X days, but not older than some crazy
            # amount. The second check is for sanity only.
            if dt.total_seconds() > 30 * 24 * 3600 and dt.total_seconds() < 10 * 12 * 30 * 24 * 3600:

                sys.stderr.write("Removing too-old logfile '{}'. It was older than 30 days\n".format(l))

                # use try/except to get around race conditions when
                # multiple pyam sessions are invoked
                try:
                    os.unlink(l)
                except Exception:
                    pass


# We apparently use python3 now, so I'm expected to jump through hoops.
try:
    file_base = file
except:
    import io

    file_base = io.FileIO


class LoggedFile(file_base):
    """A 'file' subclass to produce a loglevel on each write().

    Used just like a file, but write() is overridden such that the output
    produced by this class has a loglevel preceding each line.

    """

    def __init__(self, *args, **kwargs):
        super(LoggedFile, self).__init__(*args, **kwargs)
        self.write("Hello! I am pyam {}\n".format(__version__))

    def write(self, s, *args, **kwargs):
        r"""Enhance file.write() to precede each line with a loglevel."""

        if "level" in kwargs and kwargs["level"] is not None:
            level = kwargs["level"]
        else:
            level = 1
        if "level" in kwargs:
            del kwargs["level"]
        level = "level{}: ".format(level)

        for l in s.splitlines(True):

            # This is required to be compatible with python2 AND python3 AND
            # various users' locale environment settings. The test is to try to
            # log some unicode stuff in all of these ways. I did this;
            #
            # 1. Write some unicode anything to /tmp/unicodefile
            # 2. Apply this patch to make 'pyam latest' log unicode:
            #
            # Index: pyam
            # ===================================================================
            # --- pyam	(revision 94426)
            # +++ pyam	(working copy)
            # @@ -660,6 +665,11 @@
            #          red = ansi('31m')
            #          end = ansi('0m')
            #
            # +        with open('/tmp/unicodefile', 'r') as f:
            # +            line = f.read()
            # +        yam_log.say(line)
            # +        sys.exit()
            # +
            #
            # 3. Run the 4 scenarios:
            #
            #    LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 python3 ../pyam/pyam latest NEO
            #    LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 python2 ../pyam/pyam latest NEO
            #    LC_ALL=C           LANG=C           python3 ../pyam/pyam latest NEO
            #    LC_ALL=C           LANG=C           python2 ../pyam/pyam latest NEO
            #
            # 4. Make sure none of the 4 barfed, and look at the resulting logs:
            #
            #    tail -n3 ~/yamlogs/*(om[1,4])
            s = level + l
            try:
                s = s.decode("utf8")
            except:
                pass
            s = s.encode("utf8")
            super(LoggedFile, self).write(s, *args, **kwargs)
        if s[-1] != "\n":
            super(LoggedFile, self).write(b"\n")


def init(dolog, subcmd):
    """Initialize the logging system.

    Call this exactly once before you start to log. All attempted log entries
    prior to this are silently thrown away.

    """

    global _inited
    global _dolog
    global _logfile

    if _inited:
        raise Exception("logging was already initialized!")

    _inited = True
    _dolog = dolog
    if not _dolog:
        return

    if "_logfile" not in locals():
        directory = os.getenv("HOME") + "/yamlogs"
        name_timestamped = time.strftime("yamlog.{}-%Y_%m_%d__%H_%M_%S".format(subcmd))
        filename = directory + "/" + name_timestamped

        # make log directory
        try:
            os.mkdir(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        _logfile = LoggedFile(filename, "w")

        cull_old_logs(directory)


def enter(s, level=None):
    """Log traceback."""

    if not _inited:
        # Happens when pieces of yam are called outside of the main pyam
        # executable. Either something is weird or we're running the pyam test
        # suite
        return

    if not _dolog:
        return

    _logfile.write("{ ===================================================\n", level=level)

    # I print the backtrace without the elements that are are inside the
    # yam_log.py machinery
    f = traceback.extract_stack()
    for i in range(len(f)):
        if f[i][0].endswith("/yam_log.py"):
            f = f[:i]
            break
    for filename, lineno, name, line in f:
        _logfile.write(
            '  File "%s", line %d, in %s\n' % (filename, lineno, name),
            level=level,
        )
        if line:
            _logfile.write("    %s\n" % line.strip(), level=level)
    _logfile.write(s + " ...\n", level=level)
    _logfile.write("------------\n", level=level)


def lexit(s, level=None):
    """Log exit string."""

    if not _inited:
        # Happens when pieces of yam are called outside of the main pyam
        # executable. Either something is weird or we're running the pyam test
        # suite
        return

    if not _dolog:
        return

    _logfile.write("... " + s + "\n", level=level)
    _logfile.write("} ===================================================\n", level=level)


def say(s, console_also=False, level=None):
    """Log a string to the log file.

    if(console_also) then also log to the console.

    """

    if not _inited:
        # Happens when pieces of yam are called outside of the main pyam
        # executable. Either something is weird or we're running the pyam test
        # suite
        return

    if not _dolog:
        return

    _logfile.write(s + "\n", level=level)

    if console_also:
        sys.stdout.write(s + "\n")


def logfile_path():
    """Return the logfile path."""
    return _logfile.name


def function_logger(s, level=None):
    """decorator to log function calls."""

    def wrap(f):
        """Wrapper callback"""

        def wrapped_f(*args, **kwargs):
            """Actual wrapper fn"""
            enter("{}: {} {}".format(s, args, kwargs), level=level)
            result = f(*args, **kwargs)
            lexit("result: '{}'".format(result), level=level)
            return result

        return wrapped_f

    return wrap
