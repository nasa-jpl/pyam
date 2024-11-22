#!/bin/bash
#
# Test start_test_mysql_server.bash script.

rm -f ready
../../../common/mysql/start_test_mysql_server.bash -r ready -e

# Check that the mysqld process is automatically killed after the start_test_mysql_server.bash script exits.
port=$(cat ready)
if mysqladmin --port="$port" --host=127.0.0.1 ping >& /dev/null
then
    echo 'ERROR: mysqld was not killed automatically by start_test_mysql_server.bash when it exited'
    exit 2
fi
rm -f ready
