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

We expect an error when the limit given is negative.

    $ $PYAM history --limit -1 NonExistentModule
    usage: pyam history [-h] [--limit [LIMIT]] [--before [BEFORE]]
                        [--after [AFTER]] [--ascending]
                        [module_name ...]
    pyam history: error: argument --limit/-l: -1 is an invalid positive int value


We expect an error when the limit is not given.

    $ $PYAM history --limit NonExistentModule
    usage: pyam history [-h] [--limit [LIMIT]] [--before [BEFORE]]
                        [--after [AFTER]] [--ascending]
                        [module_name ...]
    pyam history: error: argument --limit/-l: invalid check_positive value: 'NonExistentModule'


We expect an error when the before given is in an incorrect format.

    $ $PYAM history --before 1 NonExistentModule
    usage: pyam history [-h] [--limit [LIMIT]] [--before [BEFORE]]
                        [--after [AFTER]] [--ascending]
                        [module_name ...]
    pyam history: error: argument --before/-b: 1 is an invalid datetime value. Must be of the format "XXXX-XX-XX XX:XX:XX"


We expect an error when the after given is in an incorrect format.

    $ $PYAM history --after 1 NonExistentModule
    usage: pyam history [-h] [--limit [LIMIT]] [--before [BEFORE]]
                        [--after [AFTER]] [--ascending]
                        [module_name ...]
    pyam history: error: argument --after/-a: 1 is an invalid datetime value. Must be of the format "XXXX-XX-XX XX:XX:XX"


We expect an error when the before given is in an incorrect format.

    $ $PYAM history --before "1111-11-11 24:23:23" NonExistentModule
    The datetime value for --before is invalid.


We expect an error when the after given is in an incorrect format.

    $ $PYAM history --after "1111-11-11 24:23:23" NonExistentModule
    The datetime value for --after is invalid.

We expect an error when the before is not given.

    $ $PYAM history --before NonExistentModule
    usage: pyam history [-h] [--limit [LIMIT]] [--before [BEFORE]]
                        [--after [AFTER]] [--ascending]
                        [module_name ...]
    pyam history: error: argument --before/-b: NonExistentModule is an invalid datetime value. Must be of the format "XXXX-XX-XX XX:XX:XX"


We expect an error when the after is not given.

    $ $PYAM history --after NonExistentModule
    usage: pyam history [-h] [--limit [LIMIT]] [--before [BEFORE]]
                        [--after [AFTER]] [--ascending]
                        [module_name ...]
    pyam history: error: argument --after/-a: NonExistentModule is an invalid datetime value. Must be of the format "XXXX-XX-XX XX:XX:XX"
