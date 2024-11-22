#!/usr/bin/env python
"""Make sure that all interfaces have no implementation.

If code reuse is necessary, then it should be done via functions not
methods.

"""


from __future__ import print_function


from yam import build_system
from yam import configuration_reader
from yam import configuration_writer
from yam import database_reader
from yam import database_writer
from yam import file_system
from yam import module
from yam import revision_control_system
from yam import sandbox

interface_list = [
    build_system.BuildSystem,
    configuration_reader.ConfigurationReader,
    configuration_writer.ConfigurationWriter,
    database_reader.DatabaseReader,
    database_writer.DatabaseWriter,
    file_system.FileSystem,
    module.Module,
    revision_control_system.RevisionControlSystem,
    sandbox.Sandbox,
]

for interface in interface_list:
    for method_name in dir(interface):
        if not method_name.startswith("_"):
            try:
                is_abstract = getattr(interface, method_name).__isabstractmethod__
            except AttributeError:
                is_abstract = False
            if is_abstract:
                print(".", end="")
            else:
                print(
                    "ERROR: {name}.{method}() should be abstract with no implementation.".format(
                        name=interface.__name__, method=method_name
                    )
                    + " {name} is an interface and should not have implementation code.".format(name=interface.__name__)
                    + " If code reuse is wanted, then it should be done via functions not methods."
                )
                import sys

                sys.exit(2)

print("\nOK")
