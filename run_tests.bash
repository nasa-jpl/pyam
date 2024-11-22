#!/bin/bash -e

# Start shared read-only MySQL server to speed things up.
. './test/common/mysql/mysql_server.bash'
start_read_only_mysql_server './test/common/mysql/example_yam_for_import.sql'

../../bin/Drun dtest --jobs=-1 --fail-fast --max-load-saturation=1. "$@"

# Test port forwarding database connection. Run this here since this is
# potentially require user interaction.
echo 'Testing --database-gateway'
./pyam --database-gateway fake.fake.jpl.nasa.gov latest 2>&1 \
    | grep 'Failed' > /dev/null
./pyam --database-gateway shavian.jpl.nasa.gov latest \
    | grep '^pyam R' > /dev/null
echo -e '\x1b[32mOkay\x1b[0m'
