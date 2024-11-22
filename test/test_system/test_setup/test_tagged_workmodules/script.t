asacacascest "save" command.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

1 Create a fake sandbox.

    $ sandbox_directory="$CRAMTMP/FakeSandbox"
    $ "$TESTDIR/../../../common/sandbox/make_fake_sandbox.bash" "$sandbox_directory"

2 Note that "R4-06g" is the latest Dshell++, but DshellEnv link module is not the latest

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/FakeSandbox/YAM.config"
    $ echo 'BRANCH_Dshell++ = main' >> "$CRAMTMP/FakeSandbox/YAM.config"

3 Create a fake release area.

    $ release_directory="$CRAMTMP/fake_release"
    $ "$TESTDIR/../../../common/release_directory/make_fake_release_directory.bash" "$release_directory"

4 Start MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server "$TESTDIR/../../../common/mysql/example_yam_for_import.sql"
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

5 Create fake SVN repository.

    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ "$TESTDIR/../../../common/svn/make_fake_repository.bash" "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

## $ echo "PYAM=" $PYAM

PYAM= /home/atbe/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC29-2/src/pyam/test/test_system/test_save/test_maintenance/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:36820/test --release-directory=/*/fake_release --default-repository-url=file:///*/fake_repository (glob)

Check the latest version of DshellEnv

    $ $PYAM latest 'DshellEnv'
    DshellEnv R1-49r                             -  jain        2006-07-14 12:24:09


----------------------- (1) first instance NORMAL-----------------------------------

Check out a normal development branch

 "============= MAKING MODIFICATION TO R4-06h MAIN TRUNK VERSION and SAVING to R4-06i version"


6 Check out the Dshell++ work module (on the main trunk)

    $ cd "$sandbox_directory"
    $ $PYAM rebuild


10 Make some changes and commit them to SVN repository.

    $ cd "$sandbox_directory/src/Dshell++"
    $ svn mkdir 'ONE'
    A         ONE
    $ svn commit --message 'Add ONE directory'
    Adding         ONE
    Committing transaction...
    Committed revision *. (glob)

11 Test the "save" command.

    $ cd "$sandbox_directory"
    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

----------------------- (2) Second instance NORMAL-----------------------------------

Checkout a normal development branch, add a directory to it called "two"
and save it to get Dshell++-R4-06i release


    $ echo "============= MAKING SECOND MODIFICATION TO R4-06i VERSION"
    ============= MAKING SECOND MODIFICATION TO R4-06i VERSION


13 Check out the module again.

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++'

22 Make a change to the module

    $ cd "$sandbox_directory/src/Dshell++"
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06h-* (glob)
    $ svn mkdir 'TWO'
    A         TWO
    $ svn commit --message 'Add TWO directory'
    Adding         TWO
    Committing transaction...
    Committed revision *. (glob)

23 Run the "save" command to make the Dshell++-R4-06i release

    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)


13 Check out the Dshell++ module again.

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++'

22 Make another change to the module

    $ cd "$sandbox_directory/src/Dshell++"
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06i-* (glob)

    $ svn mkdir 'DUMM'
    A         DUMM
    $ svn commit --message 'Add TWO directory'
    Adding         DUMM
    Committing transaction...
    Committed revision *. (glob)

23 Run the "save" command to make the Dshell++-R4-06j release (want to
do this so the remaining tests would be for a maintenance branch on an
older release)

    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)


----------------------- (3) first instance MAINT-----------------------------------
Checkout a maint branch, add a directory to it called "three" and save it


    $ echo "============= CREATE M2020 MAINTENANCE BRANCH FROM NON-LATEST R4-06i VERSION"
    ============= CREATE M2020 MAINTENANCE BRANCH FROM NON-LATEST R4-06i VERSION

13 Check out the module again.

    $ cd "$sandbox_directory"
    $ $PYAM scrap --remove 'Dshell++'
    $ $PYAM checkout 'Dshell++' --release R4-06i --maintenance 'MyprojectA'
    YOU ARE CHECKING OUT A MAINTENANCE BRANCH


----------------------- (3) first MAINT relelase ------------------------------
    $ echo "============= MAKE FIRST M2020 MAINTENANCE RELEASE FOR NON-LATEST R4-06i VERSION"
    ============= MAKE FIRST M2020 MAINTENANCE RELEASE FOR NON-LATEST R4-06i VERSION


22 More SVN STUFF

    $ cd "$sandbox_directory/src/Dshell++"
    $ svn mkdir 'THREE'
    A         THREE
    $ svn commit --message 'Add THREE directory'
    Adding         THREE
    Committing transaction...
    Committed revision *. (glob)

Add a work module for non-latest branch of DshellEnv. This is to
verify that the maintenance release process does not insist on the
sandbox having the latest module versions in the sandbox.

    $ $PYAM checkout DshellEnv --release R1-49q --branch - >& /dev/null


    $ grep Dshell "$CRAMTMP/FakeSandbox/YAM.config"
    WORK_MODULES = Dshell++ \
                   DshellEnv
    BRANCH_Dshell++  = Dshell++-R4-06i  MyprojectA-Maintenance
    BRANCH_DshellEnv = DshellEnv-R1-49q


23 Test the "save" command.

    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)


23B What yam config looks like after the first maint branch has been saved

    $ grep Dshell "$CRAMTMP/FakeSandbox/YAM.config"
    WORK_MODULES = DshellEnv
    LINK_MODULES = Dshell++/Dshell++-R4-06i-MyprojectA-MaintenanceM00
    BRANCH_DshellEnv = DshellEnv-R1-49q
    # BRANCH_Dshell++  = Dshell++-R4-06i-MyprojectA-MaintenanceM00   * (glob)

---------------------------------------------------------

Create a package in strict mode (so SiteDefs does not get added in)

    $ $PYAM register-new-package MyNewPkg --modules Dshell++ DshellEnv --strict
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

Make a regular package release

    $ $PYAM latest-package MyNewPkg
    MyNewPkg R1-00


    $ $PYAM save-package MyNewPkg
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

    $ $PYAM latest-package  MyNewPkg
    MyNewPkg R1-00a


Make a package release with the current sandbox with maintenance releases

    $ $PYAM save-package MyNewPkg --config-file "$CRAMTMP/FakeSandbox/YAM.config"
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

    $ $PYAM latest-package  MyNewPkg
    MyNewPkg R1-00b


---------------------------------------------------------

Make a regular package checkout - all work modules on branches


    $ $PYAM setup MyNewPkg -d "$CRAMTMP/FakeSandbox-regular-wm" --work-modules

###    $ cat "$CRAMTMP/FakeSandbox-regular-wm/common/YAM.modules"

###    $ cat "$CRAMTMP/FakeSandbox-regular-wm/YAM.config"

    $ grep Dshell "$CRAMTMP/FakeSandbox-regular-wm/YAM.config"
    WORK_MODULES = Dshell++ \
                   DshellEnv
    BRANCH_Dshell++  = Dshell++-R4-06j  * (glob)
    BRANCH_DshellEnv = DshellEnv-R1-49r * (glob)

---------------------------------------------------------

Make a regular package checkout - missing link modules will be tagged work modules


    $ $PYAM setup MyNewPkg -d "$CRAMTMP/FakeSandbox-regular"


    $ grep Dshell "$CRAMTMP/FakeSandbox-regular/YAM.config"
    WORK_MODULES = DshellEnv
    LINK_MODULES = Dshell++/Dshell++-R4-06j
    BRANCH_DshellEnv = DshellEnv-R1-49r
    # BRANCH_Dshell++  = Dshell++-R4-06j  * (glob)


---------------------------------------------------------

Make a  package checkout with maintenance release modules


    $ $PYAM setup MyNewPkg -d "$CRAMTMP/FakeSandbox-maint" -r R1-00b


    $ grep Dshell "$CRAMTMP/FakeSandbox-maint/YAM.config"
    LINK_MODULES = Dshell++/Dshell++-R4-06i-MyprojectA-MaintenanceM00 \
                   DshellEnv/DshellEnv-R1-49q
    # BRANCH_Dshell++  = Dshell++-R4-06i  * (glob)
    # BRANCH_DshellEnv = DshellEnv-R1-49q * (glob)


---------------------------------------------------------

Make a  package checkout with maintenance release modules - all work modules


    $ $PYAM setup MyNewPkg -d "$CRAMTMP/FakeSandbox-maint-wm"  -r R1-00b --work-modules


    $ grep Dshell "$CRAMTMP/FakeSandbox-maint-wm/YAM.config"
    WORK_MODULES = Dshell++ \
                   DshellEnv
    BRANCH_Dshell++  = Dshell++-R4-06i-MyprojectA-MaintenanceM00
    BRANCH_DshellEnv = DshellEnv-R1-49q
