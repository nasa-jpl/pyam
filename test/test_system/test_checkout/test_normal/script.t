Test "checkout" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Set up.

    $ fakedatatar=$TESTDIR/../../../common/pyamfakedata.tar.gz
    $ tar zxf $fakedatatar  -C $CRAMTMP
    $ mv  $CRAMTMP/pyamfakedata/*  $CRAMTMP

    $ sandbox_directory="$CRAMTMP/FakeSandbox"


    $ release_directory="$CRAMTMP/fake_release"


Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ port=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_svn_repository_path="$CRAMTMP/fake_svn_repository"


    $ fake_svn_repository_url="file://`readlink -f \"$fake_svn_repository_path\"`"

Set command-line parameters.

    $ PYAM="$TESTDIR/../../../../pyam --quiet --release-directory=$release_directory --no-build-server --database-connection=127.0.0.1:$port/test --default-repository-url=$fake_svn_repository_url"


#--------------------------------------------------------------


Fill in the YAM.config.

    $ echo 'LINK_MODULES = Dshell++/Dshell++-R4-06g' >> "$CRAMTMP/FakeSandbox/YAM.config"

Check out branched module.

    $ cd "$sandbox_directory"

    $ $PYAM checkout 'Dshell++'

    $ ls "$sandbox_directory/src/Dshell++/YamVersion.h" > /dev/null

    $ grep 'R4-06g' "$sandbox_directory/src/Dshell++/YamVersion.h" > /dev/null

Make some changes and commit them to SVN repository.

    $ cd "$sandbox_directory/src/Dshell++"

    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'

Do a clean check out of the same branched module to make sure changes are still
there.

    $ rm -rf "$sandbox_directory/src/Dshell++"
    $ cd "$sandbox_directory"

    $ $PYAM rebuild 'Dshell++'

    $ ls "$sandbox_directory/src/Dshell++/my_new_directory"
