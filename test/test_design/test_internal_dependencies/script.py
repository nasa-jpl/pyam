#!/usr/bin/env python
"""
There are several concrete classes that no one other than the top-level pyam
utility should depend on. This test makes sure that remains the case.
"""


from __future__ import print_function

import subprocess
import sys


concrete_no_no = [
    "client.py",
    "concrete_configuration_reader.py",
    "concrete_configuration_writer.py",
    "email_utils.py",
    "file_system_utils.py",
    "local_file_system.py",
    "make_build_system.py",
    "mysql_database_reader.py",
    "mysql_database_writer.py",
    "port_utils.py" "svn_revision_control_system.py",
    "text_editor_utils.py",
]


output = subprocess.Popen(
    [sys.executable, "-m", "snakefood", "--internal", "../../../yam"],
    stdout=subprocess.PIPE,
).communicate()[0]

# Output is of the form
# ('/home/atbe/dev/users/myint/setup-myint01/src/pyam', 'yam/build_system.py'))

dependencies = set()
for input_line in output.decode().split("\n"):
    if len(input_line.strip()) > 0:
        left_evaled_line = eval(input_line)[0][1]
        right_evaled_line = eval(input_line)[1][1]
        if not right_evaled_line:
            continue

        dependent = left_evaled_line.strip().replace("yam/", "")
        dependency = right_evaled_line.strip().replace("yam/", "")
        assert "/" not in dependent
        assert "/" not in dependency

        if dependency in concrete_no_no:
            print(
                "ERROR: {dependent} relies on concrete class in {dependency}.".format(
                    dependent=dependent, dependency=dependency
                )
                + "Only the top level pyam utility should depend on such concrete classes."
                + "Classes should depend only on interfaces."
            )
            sys.exit(2)
        else:
            print(".", end="")

print("\nOK")
sys.exit(0)
