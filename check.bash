#!/bin/bash
#
# Run quick tests only.

./run_tests.bash --ignore='*/test_sql_database_writer*' \
    test/test_code \
    test/test_design \
    test/test_distribution \
    test/test_unit
