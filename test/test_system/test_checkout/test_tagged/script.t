Test "checkout" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Set up.

    $ sandbox_directory="$CRAMTMP/FakeSandbox"
    $ "$TESTDIR/../../../common/sandbox/make_fake_sandbox.bash" "$sandbox_directory"

    $ release_directory="$CRAMTMP/fake_release"
    $ "$TESTDIR/../../../common/release_directory/make_fake_release_directory.bash" "$release_directory"

Fill in the YAM.config.

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_Dshell++ = Dshell++-R4-06g' >> "$CRAMTMP/FakeSandbox/YAM.config"

Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ port=$START_MYSQL_SERVER_RETURN_PORT

Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ "$TESTDIR/../../../common/svn/make_fake_repository.bash" "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

Set command-line parameters.

    $ PYAM="$TESTDIR/../../../../pyam --quiet --release-directory=$release_directory --no-build-server --database-connection=127.0.0.1:$port/test --default-repository-url=$fake_repository_url"

Set up tagged module.

    $ pushd "$sandbox_directory" > /dev/null

    $ $PYAM rebuild 'Dshell++'
    $ popd > /dev/null

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06g
    $ cat "$sandbox_directory/YAM.config" | grep 'Dshell'
    WORK_MODULES = Dshell++
    BRANCH_Dshell++ = Dshell++-R4-06g

Check out branched module.

    $ ls "$sandbox_directory/src/Dshell++/YamVersion.h"
    */FakeSandbox/src/Dshell++/YamVersion.h (glob)


Remove the checked out module, and check it this time directly from the command line

    $ cd $sandbox_directory
    $ $PYAM scrap --remove Dshell++
    $ ls "$sandbox_directory/src"
    Dshell++__* (glob)


    $ $PYAM checkout 'Dshell++' --release R4-06g --branch -
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06g
    $ cat "$sandbox_directory/YAM.config" | grep 'Dshell'
    WORK_MODULES = Dshell++
    BRANCH_Dshell++ = Dshell++-R4-06g
