Test "latest" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_read_only_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ PORT=$READ_ONLY_MYSQL_SERVER_PORT

    $ PYAM="$TESTDIR/../../../../pyam --no-build-server --database-connection=127.0.0.1:$PORT/test"

Test the command.

    $ $PYAM history Dshell++
    Dshell++ R4-06g                                 jmc         2006-07-12 14:23:04
    Dshell++ R4-06f                                 clim        2006-07-12 08:52:57
    Dshell++ R4-06e                                 clim        2006-06-15 07:56:32
    Dshell++ R4-06d                                 jain        2006-06-08 18:45:21
    Dshell++ R4-06c                                 jain        2006-06-08 08:56:26
    Dshell++ R4-06b                                 jmc         2006-05-31 15:34:55
    Dshell++ R4-06a                                 clim        2006-05-23 15:27:19
    Dshell++ R4-06                                  jain        2006-05-20 07:52:15
    Dshell++ R4-05z                                 jmc         2006-05-12 13:41:31
    Dshell++ R4-05y                                 jain        2006-05-05 16:45:49
