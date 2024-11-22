Test "setup" command with automatically chosen sandbox name.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

This will not exist until after "pyam initialize".

    $ release_directory="$CRAMTMP/fake_release"

Start empty MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server '/dev/null'
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ svnadmin create "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --release-directory=$release_directory --site=telerobotics --no-build-server --database-connection=127.0.0.1:$PORT/test --default-repository-url=$fake_repository_url"

Initialize for the first time.

    $ $PYAM initialize

Verify.

    $ $PYAM setup --modules SiteDefs

    $ cd 'sandbox-'*
    $ ls YAM.config
    YAM.config
