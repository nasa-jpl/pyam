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

    $ cat > "$CRAMTMP/FakeSandbox/YAM.config" << EOF
    > WORK_MODULES = Dshell++ FakeModule
    > BRANCH_Dshell++ = Dshell++-R4-06f my_branch
    > BRANCH_FakeModule = FakeModule-R4-06f my_branch
    > EOF

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

#     echo "PYAM-=" $PYAM

Check out branched module.

    $ cd "$sandbox_directory"
    $ $PYAM rebuild 'Dshell++'

Saving when in need of a sync should fail.
I throw out the traceback and match the actual error.

    $ cd "$sandbox_directory"
    $ $PYAM latest 'Dshell++'
    Dshell++ R4-06g                              -  jmc         2006-07-12 14:23:04
    $ svn info --show-item relative-url 'src/Dshell++'
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06f-my_branch
    $ echo "Dummy line" >>  'src/Dshell++/ReleaseNotes'
    $ svn commit -m "Added text" 'src/Dshell++' > /dev/null

# $PYAM save 'Dshell++' |& awk '!/^Traceback|^  File|^    /'
    $ $PYAM save 'Dshell++'
    .* needs to be synced up to the latest revision (re)


Saving when module is not checked out should fail.
I throw out the traceback and match the actual error.

    $ cd "$sandbox_directory"
    $ $PYAM save 'FakeModule' |& awk '!/^Traceback|^  File|^    /'
    .* Module 'FakeModule' is not checked out (re)

Saving when module is not in sandbox should fail.
I throw out the traceback and match the actual error.

    $ cd "$sandbox_directory"
    $ $PYAM save 'AlephOne' |& awk '!/^Traceback|^  File|^    /'
    .* Module 'AlephOne' is not checked out (re)

Saving outside of a sandbox should fail.
I throw out the traceback and match the actual error.

    $ cd "$CRAMTMP"
    $ $PYAM save 'Dshell++' |& awk '!/^Traceback|^  File|^    /'
    .*needs to be issued from within a sandbox (re)

Try requiring "--bug-id".
I throw out the traceback and match the actual error.

    $ cd "$CRAMTMP"
    $ $PYAM --require-bug-id save 'Dshell++' |& awk '!/^Traceback|^  File|^    /'
    .* --bug-id must be specified.* (re)
