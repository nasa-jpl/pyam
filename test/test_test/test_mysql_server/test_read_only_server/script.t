Test read-only server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_read_only_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ PORT=$READ_ONLY_MYSQL_SERVER_PORT

    $ PYAM="$TESTDIR/../../../../pyam --no-build-server --database-connection=127.0.0.1:$PORT/test"

Make sure it is read only.

    $ mysql -h 127.0.0.1 --user="" --password="" --port=$READ_ONLY_MYSQL_SERVER_PORT test << EOF
    > DROP DATABASE test;
    > EOF
    ERROR .* server is running with the .*read.only option .* (re)


Test that running it again reuses the existing server.

    $ start_read_only_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ [ $PORT -eq $READ_ONLY_MYSQL_SERVER_PORT ]
