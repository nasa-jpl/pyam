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

    $ echo 'LINK_MODULES = Dshell++/Dshell++-R4-06g' >> "$CRAMTMP/FakeSandbox/YAM.config"

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

Check out branched module.

    $ cd "$sandbox_directory"

    $ $PYAM checkout 'Dshell++'
    $ grep Dshell YAM.config
    WORK_MODULES = Dshell++
    BRANCH_Dshell++ = Dshell++-R4-06g * (glob)

    $ ls "$sandbox_directory/src/Dshell++/YamVersion.h" > /dev/null

    $ grep 'R4-06g' "$sandbox_directory/src/Dshell++/YamVersion.h"
    #define DSHELLPP_DVERSION_RELEASE "Dshell++-R4-06g"

Make some changes and commit them to SVN repository.

    $ cd "$sandbox_directory/src/Dshell++"

    $ svn mkdir --quiet 'my_new_directory'
    $ svn commit --quiet --message 'Add directory'

Perform Config to link. Followrd by Delete of work modlule.

scraping
    $ cd "$sandbox_directory"
    $ ls src
    Dshell++

    $ $PYAM scrap 'Dshell++'
    Scrapping work-module and converting work modules to link modules
    Appending module directory name in the sandbox with timestamp
    $ ls src
    Dshell++__* (glob)
    $ grep Dshell YAM.config
    LINK_MODULES = Dshell++/Dshell++-R4-06g
    # BRANCH_Dshell++ = Dshell++-R4-06g * (glob)

remove link module
    $ $PYAM scrap --remove 'Dshell++'
    $ grep Dshell YAM.config

Check out the module again WITH --branch specification

    $ $PYAM checkout --branch 'jain' 'Dshell++'
    $ grep 'Dshell' "YAM.config"
    WORK_MODULES = Dshell++
    BRANCH_Dshell++ = Dshell++-R4-06g jain
    $ ls src/Dshell++/my_file.txt
    src/Dshell++/my_file.txt

remove work module
    $ $PYAM scrap --remove 'Dshell++'
    $ grep 'Dshell' "YAM.config"
    $ ls src/
    Dshell++__* (glob)
    Dshell++__* (glob)


Check out the module again on main trunk

    $ $PYAM checkout --release main 'Dshell++'
    $ grep 'Dshell' "YAM.config"
    WORK_MODULES = Dshell++
    BRANCH_Dshell++ = main

    $ $PYAM scrap 'Dshell++'
    Scrapping work-module and converting work modules to link modules
    Appending module directory name in the sandbox with timestamp
    $ grep 'Dshell' "YAM.config"
    LINK_MODULES = Dshell++/Dshell++-R4-06g
    # BRANCH_Dshell++ = Dshell++-R4-06g * (glob)

    $ ls src/
    Dshell++__* (glob)
    Dshell++__* (glob)
    Dshell++__* (glob)


Check out the module again on main trunk, remove directory and try scrap

    $ $PYAM checkout --release main 'Dshell++'
    $ grep 'Dshell' "YAM.config"
    WORK_MODULES = Dshell++
    BRANCH_Dshell++ = main

  Remove the module from the src/ directory

    $ rm -rf 'src/Dshell++'
    $ $PYAM scrap --remove 'Dshell++'
    Nothing to do - the Dshell++ module is not in the src/ director
    $ grep 'Dshell' "YAM.config"






scrapping multiple work modules

Check out the module again on main trunk


    $ $PYAM checkout --release main Dshell++ DshellEnv

    $ grep 'Dshell' "YAM.config"
    WORK_MODULES = Dshell++ \
                   DshellEnv
    BRANCH_Dshell++  = main
    BRANCH_DshellEnv = main


    $ $PYAM scrap Dshell++ DshellEnv
    Scrapping work-module and converting work modules to link modules
    Appending module directory name in the sandbox with timestamp
    Scrapping work-module and converting work modules to link modules
    Appending module directory name in the sandbox with timestamp

    $ grep 'Dshell' "YAM.config"
    LINK_MODULES = Dshell++/Dshell++-R4-06g \
                   DshellEnv/DshellEnv-R1-49r
    # BRANCH_Dshell++  = Dshell++-R4-06g  * (glob)
    # BRANCH_DshellEnv = DshellEnv-R1-49r * (glob)

    $ ls src/
    Dshell++__* (glob)
    Dshell++__* (glob)
    Dshell++__* (glob)
    Dshell++__* (glob)
    DshellEnv__* (glob)


Scrap multiple link modules

    $ $PYAM scrap --remove Dshell++ DshellEnv

    $ grep 'Dshell' "YAM.config"


    $ ls src/
    Dshell++__* (glob)
    Dshell++__* (glob)
    Dshell++__* (glob)
    Dshell++__* (glob)
    DshellEnv__* (glob)
