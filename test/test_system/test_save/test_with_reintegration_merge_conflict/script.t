Test "save" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Create a fake sandbox.

    $ sandbox_directory="$CRAMTMP/FakeSandbox"
    $ "$TESTDIR/../../../common/sandbox/make_fake_sandbox.bash" "$sandbox_directory"

Note that "R4-06g" is the latest.

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_Dshell++ = Dshell++-R4-06g my_branch' >> "$CRAMTMP/FakeSandbox/YAM.config"

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

Check out branched module.

    $ pushd "$sandbox_directory" > /dev/null

    $ $PYAM rebuild 'Dshell++'
    $ popd > /dev/null

Check our current SVN URL.

    $ svn info "$sandbox_directory/src/Dshell++/YamVersion.h" | grep 'URL' | grep 'R4-06g' > /dev/null

Make some changes and commit them to SVN repository.

    $ pushd "$sandbox_directory/src/Dshell++" > /dev/null
    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'
    $ popd > /dev/null

Someone sneakily modifies the main branch.

    $ pushd "$CRAMTMP" >& /dev/null
    $ svn checkout --quiet "$fake_repository_url/Modules/Dshell++/trunk" 'direct_checkout'
    $ cd 'direct_checkout'
    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'
    $ popd >& /dev/null

Test the "save" command.
I throw out the traceback and match the actual error.

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM save 'Dshell++' |& awk '!/^Traceback|^  File|^    /'
    .* could not be saved .* (re)
    .*conflict occurred.* (re)
    $ popd > /dev/null

We should be on the main branch since the conflict occurred after reintegration.

    $ pushd "$sandbox_directory/src/Dshell++" >& /dev/null
    $ svn info | grep 'URL' | grep '/trunk' > /dev/null
    $ svn status | grep 'my_new_directory'
     *C my_new_directory * (re)
    $ popd >& /dev/null

Resolve conflict and save.

    $ pushd "$sandbox_directory/src/Dshell++" >& /dev/null
    $ svn resolved --quiet 'my_new_directory'
    $ svn commit --quiet --message=''
    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)
    $ popd >& /dev/null

Confirm that the change is released.

    $ $PYAM latest 'Dshell++' | grep 'R4-06h' > /dev/null
