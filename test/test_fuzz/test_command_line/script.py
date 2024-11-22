#!/usr/bin/env python
"""Test random command line options with the attempt to get an uncaught
exception."""

from __future__ import print_function

import os
import sys
from functools import reduce
import subprocess
import signal


PYAM_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../../pyam"))
yam_root = os.getenv("YAM_ROOT")
common_folder = os.path.join(yam_root, "src", "pyam", "test", "common")


class TemporaryDirectory(object):
    """TemporaryDirectory will be deleted when it goes out of scope."""

    def __init__(self):
        import tempfile

        self.__temporary_file_path = tempfile.mkdtemp()

    def __del__(self):
        import shutil

        shutil.rmtree(path=self.__temporary_file_path, ignore_errors=True)

    def __str__(self):
        return self.__temporary_file_path


def main():
    # Make sure to unset these as we don't want to accidentally use the settings
    # of the global pyam installation.
    if "YAM_PROJECT_CONFIG_DIR" in os.environ:
        del os.environ["YAM_PROJECT_CONFIG_DIR"]
    if "YAM_PROJECT" in os.environ:
        del os.environ["YAM_PROJECT"]

    original_directory = os.getcwd()

    success = True

    # Run without server
    success = success and run_test(
        original_directory=original_directory,
        mandatory_options=[
            "--database-connection",
            "127.0.0.1:12345:blah:blah:blah",
        ],
    )

    # Run with server
    # mysql_temporary_directory, mysql_process, sql_info = start_mysql_server(original_directory=original_directory)

    returnval = (
        subprocess.check_output(["python3", common_folder + "/mysql/runmysql.py", common_folder])
        .decode("UTF-8")
        .split()
    )
    mysql_process, port = int(returnval[0]), int(returnval[1])

    sql_info = "127.0.0.1:{port}/test".format(port=port)
    success = success and run_test(
        original_directory=original_directory,
        mandatory_options=["--database-connection", sql_info],
    )

    os.killpg(os.getpgid(mysql_process), signal.SIGTERM)

    return 0 if success else 1


def run_command(arguments):
    command = [PYAM_PATH] + arguments
    import subprocess

    pyam_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = pyam_process.communicate()
    combined_output = (output[0] + output[1]).decode()
    del output
    if (
        "A problem occurred in a Python script" in combined_output
        or "pyam has crashed" in combined_output
        or "--database-connection needs to be specified" in combined_output
    ):
        print('Found error with command "{command}". See error below.'.format(command=" ".join(command)))
        print(combined_output)
        return False
    else:
        print(".", end="")
        import sys

        sys.stdout.flush()
        return True


def run_test(original_directory, mandatory_options):
    # Change to a temporary subdirectory of "/tmp" or else we risk screwing up
    # this sandbox.
    temporary_directory = TemporaryDirectory()
    os.chdir(str(temporary_directory))

    options, commands = parse_help([PYAM_PATH])
    filtered_options = [o for o in options if "--database-connection" not in o]
    del options

    import multiprocessing

    pool = multiprocessing.Pool()
    result = pool.map(
        run_command,
        command_permutations(
            mandatory_options=mandatory_options,
            options=filtered_options,
            commands=commands,
            max_choose=2,
        ),
    )

    pool.close()
    pool.join()
    del pool

    os.chdir(original_directory)

    print()
    if reduce(lambda x, y: x and y, result):
        print("OK")
        return True
    else:
        # Copy error directory back to original directory for debugging
        import shutil
        import tempfile

        unique_directory = os.path.join(tempfile.mkdtemp(dir=original_directory), "errors")
        shutil.copytree(src=str(temporary_directory), dst=unique_directory)
        return False


def command_permutations(mandatory_options, options, commands, max_choose):
    import itertools

    possible_last_arguments = ["abc", "a123", '"']
    last_arguments_combinations = []
    for r in range(1 + len(possible_last_arguments)):
        last_arguments_combinations += list(itertools.combinations(possible_last_arguments, r))

    arguments = []
    for r in range(max_choose):
        for option_instance in itertools.combinations(options, r):
            normalized_options = []
            for o in option_instance:
                if len(o) > 1:
                    normalized_options.extend(o.split())
                else:
                    normalized_options.append(o)

            for c in commands:
                for last_arguments in last_arguments_combinations:
                    arguments.append(mandatory_options + normalized_options + [c] + list(last_arguments))
    return arguments


def parse_help(commands):
    import subprocess

    pyam_process = subprocess.Popen(commands + ["--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    help_message = pyam_process.communicate()[0]
    del pyam_process
    assert help_message

    option_text = help_message.decode().split("[-h]")[1].split("{")[0]
    command_text = help_message.decode().split("{")[1].split("} ...")[0]

    return (
        " ".join([line.strip() for line in option_text.split("\n")]).strip().strip("[]").split("] ["),
        command_text.split(","),
    )


if __name__ == "__main__":
    sys.exit(main())
