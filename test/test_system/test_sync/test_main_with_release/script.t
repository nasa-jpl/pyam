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

Note that Dshell++ is on the main trunk

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_Dshell++ = main' >> "$CRAMTMP/FakeSandbox/YAM.config"

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





--------------------------------------------------------------
Sync up to the latest release and user branch

    $ pushd "$sandbox_directory" >& /dev/null
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk

    $ $PYAM sync 'Dshell++'
    Syncing Dshell++ work module to its latest release
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06g-* (glob)
    $ svn status 'src/Dshell++'

    $ popd > /dev/null







--------------------------------------------------------------
Sync up to a specific release and branch.

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout Dshell++ --release main
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk

    $ $PYAM sync 'Dshell++' --release R4-06f --branch junk
    Syncing Dshell++ work module to R4-06f release
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06f-junk
    $ svn status 'src/Dshell++'

    $ popd > /dev/null




--------------------------------------------------------------
Sync up to a specific release and default user branch

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout Dshell++ --release main
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk

    $ $PYAM sync 'Dshell++' --release R4-06f
    Syncing Dshell++ work module to R4-06f release
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06f-* (glob)
    $ svn status 'src/Dshell++'

    $ popd > /dev/null


--------------------------------------------------------------
Sync up to a specific tagged release (no branch)

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout Dshell++ --release main
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk

    $ $PYAM sync 'Dshell++' --release R4-06f --branch -
    Syncing Dshell++ work module to R4-06f release
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06f
    $ svn status 'src/Dshell++'

    $ popd > /dev/null


--------------------------------------------------------------
Verify that we get an error when syncing if there are main trunk commits


    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout Dshell++ --release main
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk
    $ echo "JUNK" >> "$sandbox_directory/src/Dshell++/ChangeLog"
    $ svn commit -m "Dummy main trunk commit" "$sandbox_directory/src/Dshell++/ChangeLog" > /dev/null

    $ $PYAM sync 'Dshell++' |& awk '!/^Traceback|^  File|^    /'
    Syncing Dshell++ work module to its latest release
    ValueError: Cannot sync a main trunk module with main trunk commits. The following files have main trunk commits: ['ChangeLog']
