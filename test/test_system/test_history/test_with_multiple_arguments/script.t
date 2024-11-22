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

Test the command with ascending.

    $ $PYAM history --before "2006-08-31 22:22:22" --after "2005-05-05 22:22:22" --limit 15 -asc ACSModels ANN AcmeModels AcsFswProto AejModels AgileDesign AirshipModels AirshipVehicles Alice AmesMSF_3DModels AmesMSF_IF Dshell++
    Dshell++ R4-04q                                 clim        2005-06-01 13:59:06
    Dshell++ R4-04r                                 clim        2005-06-23 08:20:29
    AejModels R1-00                                 balaram     2005-06-29 13:55:51
    Dshell++ R4-04s                                 clim        2005-06-29 15:44:08
    AejModels R1-00a                                balaram     2005-06-29 16:04:50
    Dshell++ R4-04t                                 clim        2005-06-30 14:25:39
    Dshell++ R4-04u                                 jain        2005-07-05 15:40:29
    ANN R1-02l                                      jain        2005-07-05 15:40:44
    Dshell++ R4-04v                                 jain        2005-07-13 13:51:25
    Dshell++ R4-04w                                 jain        2005-07-20 18:23:57
    Dshell++ R4-04x                                 jain        2005-07-21 18:48:25
    Dshell++ R4-04y                                 clim        2005-08-16 10:49:41
    Dshell++ R4-04z                                 clim        2005-08-22 11:43:19
    Dshell++ R4-05                                  clim        2005-08-24 13:23:54
    Dshell++ R4-05a                                 clim        2005-08-26 09:48:45

Test the command without ascending.

    $ $PYAM history --before "2006-08-31 22:22:22" --after "2005-05-05 22:22:22" --limit 15 ACSModels ANN AcmeModels AcsFswProto AejModels AgileDesign AirshipModels AirshipVehicles Alice AmesMSF_3DModels AmesMSF_IF Dshell++
    Alice R1-00d                                    jingshen    2006-07-20 14:14:08
    Alice R1-00c                                    jingshen    2006-07-14 16:50:30
    Alice R1-00b                                    jingshen    2006-07-14 16:15:02
    Alice R1-00a                                    jingshen    2006-07-13 11:46:09
    Alice R1-00                                     jain        2006-07-12 15:14:52
    Dshell++ R4-06g                                 jmc         2006-07-12 14:23:04
    Dshell++ R4-06f                                 clim        2006-07-12 08:52:57
    AirshipModels R1-00t                            jmc         2006-06-29 17:35:32
    AirshipVehicles R1-00j                          jmc         2006-06-29 17:35:13
    Dshell++ R4-06e                                 clim        2006-06-15 07:56:32
    Dshell++ R4-06d                                 jain        2006-06-08 18:45:21
    Dshell++ R4-06c                                 jain        2006-06-08 08:56:26
    Dshell++ R4-06b                                 jmc         2006-05-31 15:34:55
    Dshell++ R4-06a                                 clim        2006-05-23 15:27:19
    Dshell++ R4-06                                  jain        2006-05-20 07:52:15
