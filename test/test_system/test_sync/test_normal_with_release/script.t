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

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_Dshell++ = Dshell++-R4-06e my_branch' >> "$CRAMTMP/FakeSandbox/YAM.config"

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

    $ PYAM="$TESTDIR/../../../../pyam --quiet --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

Check out branched module.

    $ pushd "$sandbox_directory" > /dev/null

    $ $PYAM rebuild 'Dshell++'
    $ popd > /dev/null

Check our current SVN URL.

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++/YamVersion.h"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06e-my_branch/YamVersion.h


Make some changes and commit them to SVN repository.

    $ pushd "$sandbox_directory/src/Dshell++" > /dev/null
    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'
    $ popd > /dev/null

--------------------------------------------------------------
Sync up to the latest branch.

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM sync 'Dshell++' --release R4-06f --branch junk
    Syncing Dshell++ work module to R4-06f release
    $ svn status 'src/Dshell++'
    A  +    src/Dshell++/my_new_directory

    $ popd > /dev/null

Make sure our SVN URL is updated to be off the latest revision.

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++/YamVersion.h"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06f-junk/YamVersion.h
