Test "checkout" command.

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


Set command-line parameters.

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --site=telerobotics --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

###$ echo "PYAM=", $PYAM

Set things up.

    $ $PYAM initialize
    $ $PYAM register-new-module 'MyNewModule'
    $ sandbox_directory="$CRAMTMP/example_sandbox"
    $ $PYAM setup --directory="$sandbox_directory" --modules 'SiteDefs'

Test and verify.

    $ $PYAM --sandbox-root-directory="$sandbox_directory" checkout --link 'MyNewModule'
    $ ls "$sandbox_directory/lms/MyNewModule"
    ChangeLog
    Makefile
    Makefile.yam
    ReleaseNotes
    YamVersion.h
    $ grep 'LINK_MODULES = MyNewModule' "$sandbox_directory/YAM.config"
    LINK_MODULES = MyNewModule/MyNewModule-R1-00 \
