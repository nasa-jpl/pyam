Test "pyam config --recall-from" command.

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

    $ echo 'WORK_MODULES = Darts Dshell++'                     >> "$sandbox_directory/YAM.config"
    $ echo 'BRANCH_Dshell++ = Dshell++-R4-06g my_branch' >> "$sandbox_directory/YAM.config"
    $ echo 'BRANCH_Darts = Darts-R3-15a my_branch'       >> "$sandbox_directory/YAM.config"
    $ echo 'LINK_MODULES = DshellEnv/DshellEnv-R1-64e'   >> "$sandbox_directory/YAM.config"

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

    $ PYAM_INTERACTIVE="$TESTDIR/../../../../pyam --quiet --require-bug-id --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"
    $ PYAM="$PYAM_INTERACTIVE --non-interactive"


    $ pushd "$sandbox_directory" > /dev/null

Config file with link module

    $ $TESTDIR/../../../../pyam --database-connection=127.0.0.1:$PORT/test config --recall-from 2006-01-01 --input-file "$sandbox_directory/YAM.config" --output-file "$sandbox_directory/YAM.config.out"

    $ cat $sandbox_directory/YAM.config.out | grep -E  '^[^#].+'
    WORK_MODULES = Darts \
                   Dshell++
    LINK_MODULES = DshellEnv/DshellEnv-R1-48a
    BRANCH_Darts     = Darts-R3-14z
    BRANCH_Dshell++  = Dshell++-R4-05i



Config file with link modules converted to work modules on branches

    $ $TESTDIR/../../../../pyam --database-connection=127.0.0.1:$PORT/test config --recall-from 2006-01-01 --input-file "$sandbox_directory/YAM.config" --output-file "$sandbox_directory/YAM.config.out" --all-to-work 
    --->  Converting 'DshellEnv' to a work module

    $ cat $sandbox_directory/YAM.config.out | grep -E  '^[^#].+'
    WORK_MODULES = Darts \
                   Dshell++ \
                   DshellEnv
    LINK_MODULES =
    BRANCH_Darts     = Darts-R3-14z
    BRANCH_Dshell++  = Dshell++-R4-05i
    BRANCH_DshellEnv = DshellEnv-R1-48a * (glob)


Config file with link modules converted to tagged work modules

    $ $TESTDIR/../../../../pyam --database-connection=127.0.0.1:$PORT/test config --recall-from 2006-01-01 --input-file "$sandbox_directory/YAM.config" --output-file "$sandbox_directory/YAM.config.out" --all-to-work --branch -
    --->  Converting 'DshellEnv' to a work module

    $ cat $sandbox_directory/YAM.config.out | grep -E  '^[^#].+'
    WORK_MODULES = Darts \
                   Dshell++ \
                   DshellEnv
    LINK_MODULES =
    BRANCH_Darts     = Darts-R3-14z
    BRANCH_Dshell++  = Dshell++-R4-05i
    BRANCH_DshellEnv = DshellEnv-R1-48a


Config file with link modules converted to user specified branch

    $ $TESTDIR/../../../../pyam --database-connection=127.0.0.1:$PORT/test config --recall-from 2006-01-01 --input-file "$sandbox_directory/YAM.config" --output-file "$sandbox_directory/YAM.config.out" --all-to-work --branch junk
    --->  Converting 'DshellEnv' to a work module

    $ cat $sandbox_directory/YAM.config.out | grep -E  '^[^#].+'
    WORK_MODULES = Darts \
                   Dshell++ \
                   DshellEnv
    LINK_MODULES =
    BRANCH_Darts     = Darts-R3-14z
    BRANCH_Dshell++  = Dshell++-R4-05i
    BRANCH_DshellEnv = DshellEnv-R1-48a junk


Verify that we cannot convert to link modules with the recall from option

    $ $TESTDIR/../../../../pyam --database-connection=127.0.0.1:$PORT/test config --recall-from 2006-01-01 --input-file "$sandbox_directory/YAM.config" --output-file "$sandbox_directory/YAM.config.out" --all-to-link
    usage: pyam config [-h] [--input-file INPUT_FILE] [--output-file OUTPUT_FILE]
                       [--branch BRANCH] [--all-to-work] [--baseline]
                       [--release RELEASE] [--to-link TO_LINK [TO_LINK ...] |
                       --all-to-link | --update-links | --current-modules |
                       --recall-from RECALL_FROM]
    pyam config: error: argument --all-to-link: not allowed with argument --recall-from


