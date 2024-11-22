Test "save" command.

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

Create old (pre-merge-tracking) SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ svnadmin create --pre-1.4-compatible "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

Initialize for the first time.

    $ $PYAM --repository-version=1.2.1 initialize

    $ $PYAM --repository-version=1.2.1 register-new-package MyPackage --modules SiteDefs
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

    $ sandbox_directory="$CRAMTMP/example_sandbox"
    $ $PYAM --repository-version=1.2.1 setup --directory="$sandbox_directory" MyPackage

    $ $PYAM --repository-version=1.2.1 --sandbox-root-directory="$sandbox_directory" checkout SiteDefs

Not specifying the version should fail since we default to using merge
tracking. I throw out the traceback and match the actual error.

    $ $PYAM --sandbox-root-directory="$sandbox_directory" save SiteDefs |& awk '!/^Traceback|^  File|^    /'
    .* too old.* (re)

But this should work.

    $ $PYAM --sandbox-root-directory="$sandbox_directory" --repository-version=1.2.1 save SiteDefs
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
