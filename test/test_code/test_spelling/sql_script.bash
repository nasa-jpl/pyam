#!/bin/bash -ex
#
# Check all Python files for spelling errors.

# Test SQL-related classes separately since it contains SQL queries as strings.
./check_spelling.py --word-list='sql_exceptions.txt' ../../../yam/*sql_database_reader.py ../../../yam/*sql_database_writer.py
