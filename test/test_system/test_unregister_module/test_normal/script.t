Test registering of a new package.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Create a fake release area.

    $ release_directory="$CRAMTMP/fake_release"
    $ "$TESTDIR/../../../common/release_directory/make_fake_release_directory.bash" "$release_directory"

Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ "$TESTDIR/../../../common/svn/make_fake_repository.bash" "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"


Test "unregister-module".
I throw out the traceback and match the actual error.

    $ $PYAM latest Dshell++
    Dshell++ R4-06g                              -  jmc         2006-07-12 14:23:04

    $ $PYAM unregister-module Dshell++

    $ $PYAM latest Dshell++ |& awk '!/^Traceback|^  File|^    /'
    Module 'Dshell++' module is dead

    $ $PYAM register-new-module Dshell++ |& awk '!/^Traceback|^  File|^    /'
    .*[Aa]lready exists.* (re)

    $ $PYAM unregister-module --undo Dshell++

    $ $PYAM latest Dshell++
    Dshell++ R4-06g                              -  jmc         2006-07-12 14:23:04
