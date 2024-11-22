#!/bin/bash -ex
#
# Check all Python files for spelling errors.

./check_spelling.py --word-list='exceptions.txt' \
    `find ../../../yam -name '*.py' -a -not -name '*sql_database_reader.py' -a -not -name '*sql_database_writer.py' -a -not -name 'make_build_system.py'` \
    ../../../pyam ../../../setup.py ../../../pyam-block-until-release ../../../pyam-build
