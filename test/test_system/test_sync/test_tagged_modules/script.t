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

    $ echo 'WORK_MODULES = Dshell++ DshellEnv' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_Dshell++ = Dshell++-R4-06f' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_DshellEnv = DshellEnv-R1-49q' >> "$CRAMTMP/FakeSandbox/YAM.config"

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

    $ $PYAM rebuild
    $ popd > /dev/null

Check our current SVN URL.

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06f
    $ svn info --show-item relative-url "$sandbox_directory/src/DshellEnv"
    ^/Modules/DshellEnv/releases/DshellEnv-R1-49q
    $ cat "$sandbox_directory/YAM.config" | grep 'Dshell'
    WORK_MODULES = Dshell++ DshellEnv
    BRANCH_Dshell++ = Dshell++-R4-06f
    BRANCH_DshellEnv = DshellEnv-R1-49q


--------------------------------------------------------------
Now we will check that we can individually sync modules

    $ $PYAM latest DshellEnv
    DshellEnv R1-49r* (glob)
    $ $PYAM latest Dshell++
    Dshell++ R4-06g* (glob)

    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM sync Dshell++
    Syncing Dshell++ work module to its latest release
    $ svn status 'src/Dshell++'

    $ popd > /dev/null

Make sure our SVN URL is updated to be off the latest revision.

    $ svn info  --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06g
    $ svn info  --show-item relative-url "$sandbox_directory/src/DshellEnv"
    ^/Modules/DshellEnv/releases/DshellEnv-R1-49q
    $ cat "$sandbox_directory/YAM.config" | grep 'Dshell'
    WORK_MODULES = Dshell++ \
                   DshellEnv
    BRANCH_Dshell++  = Dshell++-R4-06g
    BRANCH_DshellEnv = DshellEnv-R1-49q


--------------------------------------------------------------
Sync up to the latest branch.


    $ pushd "$sandbox_directory" >& /dev/null
    $ $PYAM sync --tagged-work-modules
    Syncing Dshell++ work module to its latest release
    Syncing DshellEnv work module to its latest release
    $ svn status 'src/Dshell++'

    $ popd > /dev/null

Make sure our SVN URL is updated to be off the latest revision.

    $ svn info  --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06g
    $ svn info  --show-item relative-url "$sandbox_directory/src/DshellEnv"
    ^/Modules/DshellEnv/releases/DshellEnv-R1-49r
    $ cat "$sandbox_directory/YAM.config" | grep 'Dshell'
    WORK_MODULES = Dshell++ \
                   DshellEnv
    BRANCH_Dshell++  = Dshell++-R4-06g
    BRANCH_DshellEnv = DshellEnv-R1-49r
