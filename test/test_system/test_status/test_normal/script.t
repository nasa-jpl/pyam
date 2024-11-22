Test "sync" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Create a fake sandbox.

    $ sandbox_directory="$CRAMTMP/FakeSandbox"
    $ "$TESTDIR/../../../common/sandbox/make_fake_sandbox.bash" "$sandbox_directory"

Note that "R4-06f" is one revision behind the latest.

    $ echo 'WORK_MODULES =' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'LINK_MODULES = Dshell++/Dshell++-R4-06f' >> "$CRAMTMP/FakeSandbox/YAM.config"

Create a fake release area.

    $ release_directory="$CRAMTMP/fake_release"
    $ "$TESTDIR/../../../common/release_directory/make_fake_release_directory.bash" "$release_directory"

Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_read_only_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ PORT=$READ_ONLY_MYSQL_SERVER_PORT

    $ PYAM="$TESTDIR/../../../../pyam --quiet --no-build-server --database-connection=127.0.0.1:$PORT/test"

Check the "status" command.

    $ cd "$sandbox_directory"
    $ $PYAM status
    Out-of-date link modules:
        Dshell++
