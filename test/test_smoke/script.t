Test "initialize" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

This will not exist until after "pyam initialize".

    $ release_directory="$CRAMTMP/fake_release"

Start empty MySQL server.

    $ . "$TESTDIR/../common/mysql/mysql_server.bash"
    $ start_mysql_server '/dev/null'
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ svnadmin create "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ CONFIGURATION="--site=telerobotics --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"
    $ PYAM_NORMAL="$TESTDIR/../../pyam $CONFIGURATION"
    $ PYAM="$TESTDIR/../../pyam --quiet --non-interactive $CONFIGURATION"

Initialize for the first time.

    $ $PYAM initialize

Run smoke tests. I filter out the 'make' commands because this output depends on
the runtime

    $ sandbox_directory="$CRAMTMP/example_sandbox"
    $ $PYAM_NORMAL setup --work-modules --modules SiteDefs | grep -E -v "Running.*subprocess"
    --->  Creating sandbox directory 'sandbox-*' (glob)
    --->  Checking out sandbox metadata
    --->  Checking out source code for 'SiteDefs' module (SiteDefs-R1-00a-*) (glob)
    --->  Building ['SiteDefs']
    --->  Created sandbox in 'sandbox-*' (glob)
  $ $PYAM setup --work-modules --modules SiteDefs
    $ $PYAM setup --main-work-modules --modules SiteDefs
    $ $PYAM setup --tagged-work-modules --modules SiteDefs
    $ $PYAM --text-editor='true' setup --edit --modules SiteDefs
