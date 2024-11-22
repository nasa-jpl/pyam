Test "latest" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Set up environment.

    $ sandbox_directory="$CRAMTMP/FakeSandbox"
    $ "$TESTDIR/../../../common/sandbox/make_fake_sandbox.bash" "$sandbox_directory"

    $ release_directory="$CRAMTMP/fake_release"
    $ "$TESTDIR/../../../common/release_directory/make_fake_release_directory.bash" "$release_directory"

    $ # Fill in the YAM.config
    $ config_filename="$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'WORK_MODULES = Dshell++' >> "$config_filename"
    $ echo 'BRANCH_Dshell++ = Dshell++-R4-06g my_branch' >> "$config_filename"
    $ echo 'LINK_MODULES = DshellEnv/DshellEnv-R1-64e FakeModule/FakeModule-R1-01f' >> "$config_filename"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --release-directory="$release_directory" --no-build-server --database-connection '127.0.0.1:0/none'"

Our fake sandbox makes a file called "mklinks" if "make mklinks" is called. It
should be there yet.

    $ ls "$sandbox_directory/mklinks" >& /dev/null

    $ cd "$sandbox_directory"
    $ $PYAM relink

$ Our fake sandbox makes a file called "mklinks" if "make mklinks" is called.

    $ ls "$sandbox_directory/mklinks" > /dev/null
