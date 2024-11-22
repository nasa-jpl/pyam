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

    $ $PYAM latest ACSModels ANN AcmeModels AcsFswProto AejModels AgileDesign AirshipModels AirshipVehicles Alice AmesMSF_3DModels AmesMSF_IF Dshell++
    ACSModels R1-01t                       Build03  jain        2006-05-31 22:40:57
    ANN R1-02p                             Build02  jain        2006-05-31 22:41:45
    AcmeModels R3-47l                      Build05  jain        2006-05-31 22:40:09
    AcsFswProto R1-02p                           -  dmyers      2005-04-22 13:26:22
    AejModels R1-00a                             -  balaram     2005-06-29 16:04:50
    AgileDesign R1-00d                           -  balaram     2003-10-24 20:12:56
    AirshipModels R1-00t                         -  jmc         2006-06-29 17:35:32
    AirshipVehicles R1-00j                       -  jmc         2006-06-29 17:35:13
    Alice R1-00d                                 -  jingshen    2006-07-20 14:14:08
    AmesMSF_3DModels R1-00l                      -  wagnermd    2003-11-11 06:37:42
    AmesMSF_IF R1-00r                            -  23173       2003-01-17 06:51:09
    Dshell++ R4-06g                              -  jmc         2006-07-12 14:23:04
