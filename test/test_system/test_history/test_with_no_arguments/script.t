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

    $ $PYAM history
    MyNewGitModule R1-00                            -           2022-06-05 18:47:41
    CORE R1-05z                                     jain        2006-07-21 14:35:25
    PinPointLandingModels R1-00w                    clim        2006-07-21 10:05:28
    Dspace R1-16r                                   marcp       2006-07-20 18:43:24
    DspaceTerrain R1-07f                            marcp       2006-07-20 18:33:35
    RoverVehicles R1-25j                            jmc         2006-07-20 17:47:42
    Athlete R1-00                                   jmc         2006-07-20 15:13:43
    Alice R1-00d                                    jingshen    2006-07-20 14:14:08
    Dspace R1-16q                                   rmadison    2006-07-20 13:27:24
    Dshell++Scripts R1-42r                          jain        2006-07-20 12:30:25

