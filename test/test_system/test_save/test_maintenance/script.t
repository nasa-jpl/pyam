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



###    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test >& all_tables.sql

Dshell++ module id is 62 - filter on it

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen','DshellX.h','SOURCE',0,1,34,11,33,NULL,NULL,0,0,0,0,0); (glob)

----------------------- (1) first instance NORMAL-----------------------------------

Check out a normal development branch

    $ echo "============= MAKING MODIFICATION TO R4-06h MAIN TRUNK VERSION and SAVING ro R4-06i version"
    ============= MAKING MODIFICATION TO R4-06h MAIN TRUNK VERSION and SAVING ro R4-06i version

6 Check out the Dshell++ work module (on the main trunk)

    $ cd "$sandbox_directory"
    $ $PYAM rebuild 



7 TREE RELEASE DIR

    $ tree --noreport -d "$release_directory"
    /*/fake_release (glob)
    `-- Module-Releases
        `-- SiteDefs
            |-- SiteDefs-R1-63j
            |   `-- mkHome
            |       `-- shared
            `-- SiteDefs-R1-76l
                `-- mkHome
                    `-- shared



8 YAM CONFIG

    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    
    WORK_MODULES = Dshell++
    BRANCH_Dshell++ = main

9 Check our current revision.

    $ grep 'R4-06g' "$sandbox_directory/src/Dshell++/YamVersion.h"
    #define DSHELLPP_DVERSION_RELEASE "Dshell++-R4-06g"
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk

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


12 TREEEE

    $ echo "$release_directory"
    /*/fake_release (glob)

    $ tree --noreport -d "$release_directory"
    /*/fake_release (glob)
    `-- Module-Releases
        |-- Dshell++
        |   |-- Dshell++-R4-06h
        |   |   `-- ONE
        |   `-- Latest -> Dshell++-R4-06h
        `-- SiteDefs
            |-- SiteDefs-R1-63j
            |   `-- mkHome
            |       `-- shared
            `-- SiteDefs-R1-76l
                `-- mkHome
                    `-- shared



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
    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    #
    # YAM.config - configuration file for yam utilities and makefiles
    #
    # Edit this file to suit your needs. Lines that end with backslash get spliced
    # together.
    #
    
    WORK_MODULES =
    
    LINK_MODULES = Dshell++/Dshell++-R4-06i
    
    
    
    # BRANCH_Dshell++ = Dshell++-R4-06i * (glob)
    
    #
    # Below is a list of variables that can be set:



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
    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    #
    # YAM.config - configuration file for yam utilities and makefiles
    #
    # Edit this file to suit your needs. Lines that end with backslash get spliced
    # together.
    #
    
    WORK_MODULES =
    
    LINK_MODULES = Dshell++/Dshell++-R4-06j
    
    
    
    # BRANCH_Dshell++ = Dshell++-R4-06j * (glob)
    
    #
    # Below is a list of variables that can be set:





----------------------- (3) first instance MAINT-----------------------------------
Checkout a maint branch, add a directory to it called "three" and save it


    $ echo "============= CREATE M2020 MAINTENANCE BRANCH FROM NON-LATEST R4-06i VERSION"
    ============= CREATE M2020 MAINTENANCE BRANCH FROM NON-LATEST R4-06i VERSION

13 Check out the module again.

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen','DshellX.h','SOURCE',0,*,34,11,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06h',403,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15378,62,'R4-06i',404,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15379,62,'R4-06j',405,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','SOURCE',*,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)


    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    $ cd "$sandbox_directory"
    $ $PYAM scrap --remove 'Dshell++'
    $ $PYAM checkout 'Dshell++' --release R4-06i --maintenance 'MyprojectA'
    YOU ARE CHECKING OUT A MAINTENANCE BRANCH

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06i-MyprojectA-Maintenance

    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06i-MyprojectA-Maintenance/

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen','DshellX.h','SOURCE',0,*,34,11,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06h',403,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15378,62,'R4-06i',404,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD, MyprojectA-Maintenance','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15379,62,'R4-06j',405,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)

Copying the maint branch configuration to use later when we are done doing normal development.

    $ cp "$CRAMTMP/FakeSandbox/YAM.config" "$CRAMTMP/FakeSandbox/YAMCOPY.config"


20 TREEEE

    $ tree --noreport -d "$release_directory"
    /*/fake_release (glob)
    `-- Module-Releases
        |-- Dshell++
        |   |-- Dshell++-R4-06h
        |   |   `-- ONE
        |   |-- Dshell++-R4-06i
        |   |   |-- ONE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06j
        |   |   |-- DUMM
        |   |   |-- ONE
        |   |   `-- TWO
        |   `-- Latest -> Dshell++-R4-06j
        `-- SiteDefs
            |-- SiteDefs-R1-63j
            |   `-- mkHome
            |       `-- shared
            `-- SiteDefs-R1-76l
                `-- mkHome
                    `-- shared


    $ tree --noreport -d "$sandbox_directory/src/Dshell++"
    /*/FakeSandbox/src/Dshell++ (glob)
    |-- ONE
    `-- TWO



----------------------- (3) first MAINT relelase ------------------------------
    $ echo "============= MAKE FIRST M2020 MAINTENANCE RELEASE FOR NON-LATEST R4-06i VERSION"
    ============= MAKE FIRST M2020 MAINTENANCE RELEASE FOR NON-LATEST R4-06i VERSION

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen','DshellX.h','SOURCE',0,*,34,11,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06h',403,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15378,62,'R4-06i',404,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD, MyprojectA-Maintenance','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15379,62,'R4-06j',405,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)

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

    $ $PYAM checkout DshellEnv --release R1-49q --branch fake >& /dev/null


    $ grep DshellEnv "$CRAMTMP/FakeSandbox/YAM.config"
                   DshellEnv
    BRANCH_DshellEnv = DshellEnv-R1-49q fake


23 Test the "save" command.

    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)


23B What yam config looks like after the first maint branch has been saved

    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    #
    # YAM.config - configuration file for yam utilities and makefiles
    #
    # Edit this file to suit your needs. Lines that end with backslash get spliced
    # together.
    #
    
    WORK_MODULES = DshellEnv
    
    LINK_MODULES = Dshell++/Dshell++-R4-06i-MyprojectA-MaintenanceM00
    
    BRANCH_DshellEnv = DshellEnv-R1-49q fake
    
    # BRANCH_Dshell++  = Dshell++-R4-06i-MyprojectA-MaintenanceM00   * (glob)
    
    #
    # Below is a list of variables that can be set:
    $ svn ls "$fake_repository_url/Modules/Dshell++/releases"
    Dshell++-R4-06e/
    Dshell++-R4-06f/
    Dshell++-R4-06g/
    Dshell++-R4-06h/
    Dshell++-R4-06i/
    Dshell++-R4-06i-MyprojectA-MaintenanceM00/
    Dshell++-R4-06j/

    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06i-MyprojectA-Maintenance/

    $ tree --noreport -d "$release_directory"
    /*/fake_release (glob)
    `-- Module-Releases
        |-- Dshell++
        |   |-- Dshell++-R4-06h
        |   |   `-- ONE
        |   |-- Dshell++-R4-06i
        |   |   |-- ONE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06i-MyprojectA-MaintenanceM00
        |   |   |-- ONE
        |   |   |-- THREE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06j
        |   |   |-- DUMM
        |   |   |-- ONE
        |   |   `-- TWO
        |   `-- Latest -> Dshell++-R4-06j
        `-- SiteDefs
            |-- SiteDefs-R1-63j
            |   `-- mkHome
            |       `-- shared
            `-- SiteDefs-R1-76l
                `-- mkHome
                    `-- shared

    $ tree --noreport -d "$sandbox_directory/src"
    /*/FakeSandbox/src (glob)
    `-- DshellEnv


    $ svn info --show-item relative-url "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06i-MyprojectA-MaintenanceM00"
    ^/Modules/Dshell++/releases/Dshell++-R4-06i-MyprojectA-MaintenanceM00
    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen','DshellX.h','SOURCE',0,*,34,11,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06h',403,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15378,62,'R4-06i',404,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD, MyprojectA-Maintenance','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15379,62,'R4-06j',405,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15380,62,'R4-06i',406,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','MAINTSOURCE',0,*,36,*,41,'0','MyprojectA',0,0,0,0,0); (glob)

----------------------- (4) checkout specific maintenance release link module -----------------------------------
Checkout a previous tagged maint release as a work module

    $ echo "============= CHECKING OUT MAINT RELEASE R4-06i-MyprojectA-MaintenanceM00 LINK MODULE as WORK MODULE"
    ============= CHECKING OUT MAINT RELEASE R4-06i-MyprojectA-MaintenanceM00 LINK MODULE as WORK MODULE

24 TREE OF RELEASE DIRECTORY AFTER MAINT SAVE (no merging with latest)

25 Check out the module again.

    $ cd "$sandbox_directory"

    $ tree --noreport -d "$sandbox_directory/src"
    /*/FakeSandbox/src (glob)
    `-- DshellEnv



    $ $PYAM checkout 'Dshell++'
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06i-MyprojectA-MaintenanceM00
    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06i-MyprojectA-Maintenance/

    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    #
    # YAM.config - configuration file for yam utilities and makefiles
    #
    # Edit this file to suit your needs. Lines that end with backslash get spliced
    # together.
    #
    
    WORK_MODULES = Dshell++ \
                   DshellEnv
    
    LINK_MODULES =
    
    BRANCH_Dshell++  = Dshell++-R4-06i-MyprojectA-MaintenanceM00
    BRANCH_DshellEnv = DshellEnv-R1-49q fake
    
    
    

Changes to files in the maintenance release should fail


    $ echo "dummy line" >> $sandbox_directory/src/Dshell++/ReleaseNotes
    */ReleaseNotes: Permission denied (glob)





----------------------- (4) checkout specific maintenance release clean -----------------------------------
Checkout a previous tagged maint release as a work module

    $ echo "============= CHECKING OUT MAINT RELEASE R4-06i-MyprojectA-MaintenanceM00 as WORK MODULE"
    ============= CHECKING OUT MAINT RELEASE R4-06i-MyprojectA-MaintenanceM00 as WORK MODULE

24 TREE OF RELEASE DIRECTORY AFTER MAINT SAVE (no merging with latest)

25 Check out the module again.

    $ sleep 1
    $ $PYAM scrap --remove Dshell++
    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++' --release "R4-06i-MyprojectA-MaintenanceM00" --branch -

    $ tree --noreport -d "$sandbox_directory/src/Dshell++"
    /*/FakeSandbox/src/Dshell++ (glob)
    |-- ONE
    |-- THREE
    `-- TWO


    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06i-MyprojectA-MaintenanceM00
    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06i-MyprojectA-Maintenance/

    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    #
    # YAM.config - configuration file for yam utilities and makefiles
    #
    # Edit this file to suit your needs. Lines that end with backslash get spliced
    # together.
    #
    
    WORK_MODULES = Dshell++ \
                   DshellEnv
    
    LINK_MODULES =
    
    BRANCH_Dshell++  = Dshell++-R4-06i-MyprojectA-MaintenanceM00
    BRANCH_DshellEnv = DshellEnv-R1-49q fake
    
    
    


----------------------- (4) try to make branch off a specific maintenance release (should fail) -----------------------------------
Checkout branch of a previous tagged maint release as a work module

    $ echo "============= CHECKING OUT BRANCH of MAINT RELEASE R4-06i-MyprojectA-MaintenanceM00 as WORK MODULE"
    ============= CHECKING OUT BRANCH of MAINT RELEASE R4-06i-MyprojectA-MaintenanceM00 as WORK MODULE

24 TREE OF RELEASE DIRECTORY AFTER MAINT SAVE (no merging with latest)

25 Check out the module again.

    $ sleep 2
    $ $PYAM scrap --remove Dshell++
    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++' --release "R4-06i-MyprojectA-MaintenanceM00" --branch junk
    YaM error: Cannot create a branch off of a maintenance release such as 'R4-06i-MyprojectA-MaintenanceM00' for the 'Dshell++' module (requested branch 'junk'). Giving up.



----------------------- (4) checkout specific maintenance branch (alt) -----------------------------------
Checkout a previous tagged maint release as a work module

    $ echo "============= CHECKING OUT MAINT BRANCH R4-06i-MyprojectA-Maintenance as WORK MODULE (ALT)"
    ============= CHECKING OUT MAINT BRANCH R4-06i-MyprojectA-Maintenance as WORK MODULE (ALT)

24 TREE OF RELEASE DIRECTORY AFTER MAINT SAVE (no merging with latest)

25 Check out the module again.

    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++' --release "R4-06i" --maintenance 'MyprojectA'
    YOU ARE CHECKING OUT A MAINTENANCE BRANCH

    $ tree --noreport -d "$sandbox_directory/src/Dshell++"
    /*/FakeSandbox/src/Dshell++ (glob)
    |-- ONE
    |-- THREE
    `-- TWO


    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06i-MyprojectA-Maintenance
    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06i-MyprojectA-Maintenance/




----------------------- (4) 2nd instance MAINT-----------------------------------

    $ echo "============= MAKING SECOND MAINT RELEASE FOR R4-06i VERSION"
    ============= MAKING SECOND MAINT RELEASE FOR R4-06i VERSION


26 Make some changes and commit them to SVN repository.


28 More SVN STUFF

    $ cd "$sandbox_directory/src/Dshell++"
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06i-MyprojectA-Maintenance
    $ svn mkdir 'FOUR'
    A         FOUR
    $ svn commit --message 'Add directory'
    Adding         FOUR
    Committing transaction...
    Committed revision *. (glob)

Verify that the sync command will not work for a maitenance branch work module

    $ cd "$sandbox_directory"
    $ $PYAM sync Dshell++ DshellEnv
    YaM error: Cannot sync Dshell++ work module since it is on MyprojectA maintenance branch. Giving up.


29 Test the "save" command.

    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)


29B What yam config looks like after the first maint branch has been saved

    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    #
    # YAM.config - configuration file for yam utilities and makefiles
    #
    # Edit this file to suit your needs. Lines that end with backslash get spliced
    # together.
    #
    
    WORK_MODULES = DshellEnv
    
    LINK_MODULES = Dshell++/Dshell++-R4-06i-MyprojectA-MaintenanceM01
    
    BRANCH_DshellEnv = DshellEnv-R1-49q fake
    
    # BRANCH_Dshell++  = Dshell++-R4-06i-MyprojectA-MaintenanceM01   * (glob)
    
    #
    # Below is a list of variables that can be set:

    $ svn ls "$fake_repository_url/Modules/Dshell++/releases"
    Dshell++-R4-06e/
    Dshell++-R4-06f/
    Dshell++-R4-06g/
    Dshell++-R4-06h/
    Dshell++-R4-06i/
    Dshell++-R4-06i-MyprojectA-MaintenanceM00/
    Dshell++-R4-06i-MyprojectA-MaintenanceM01/
    Dshell++-R4-06j/

    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06i-MyprojectA-Maintenance/
    $ tree --noreport -d "$release_directory"
    /*/fake_release (glob)
    `-- Module-Releases
        |-- Dshell++
        |   |-- Dshell++-R4-06h
        |   |   `-- ONE
        |   |-- Dshell++-R4-06i
        |   |   |-- ONE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06i-MyprojectA-MaintenanceM00
        |   |   |-- ONE
        |   |   |-- THREE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06i-MyprojectA-MaintenanceM01
        |   |   |-- FOUR
        |   |   |-- ONE
        |   |   |-- THREE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06j
        |   |   |-- DUMM
        |   |   |-- ONE
        |   |   `-- TWO
        |   `-- Latest -> Dshell++-R4-06j
        `-- SiteDefs
            |-- SiteDefs-R1-63j
            |   `-- mkHome
            |       `-- shared
            `-- SiteDefs-R1-76l
                `-- mkHome
                    `-- shared


    $ head -17 "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06i-MyprojectA-MaintenanceM01/ChangeLog"
    *  * (glob)
    
    \t* Revision tag: R4-06i-MyprojectA-MaintenanceM01 (esc)
    
    \t* Add directory (esc)
    
    \t  SVN revision: * (esc) (glob)
    \t  A FOUR (esc)
    
    \t* Add THREE directory (esc)
    
    \t  SVN revision: * (esc) (glob)
    \t  A THREE (esc)
    
    * * (glob)
    
    \t* Revision tag: R4-06i-MyprojectA-MaintenanceM00 (esc)
    $ chmod -R aug+w  "src/"
    $ rm -r "src"



    $ svn info --show-item relative-url "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06i-MyprojectA-MaintenanceM01"
    ^/Modules/Dshell++/releases/Dshell++-R4-06i-MyprojectA-MaintenanceM01



----------------------- (4) MAINT Release on older Dshell++-R4-06h branch -----------------------------------

 Checkout a maint branch, add a directory to it called "FIVE" and save it


    $ echo "============= CREATE M2020 MAINTENANCE BRANCH FROM OLDER R4-06h VERSION"
    ============= CREATE M2020 MAINTENANCE BRANCH FROM OLDER R4-06h VERSION

13 Check out the module again.

    $ sleep 1
    $ $PYAM scrap --remove Dshell++
    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06i-MyprojectA-Maintenance/
    $ cd "$sandbox_directory"
    $ $PYAM checkout 'Dshell++' --maintenance 'MyprojectA' --release R4-06h
    YOU ARE CHECKING OUT A MAINTENANCE BRANCH
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/featureBranches/Dshell++-R4-06h-MyprojectA-Maintenance
    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06h-MyprojectA-Maintenance/
    Dshell++-R4-06i-MyprojectA-Maintenance/

Copying the maint branch configuration to use later when we are done doing normal development.

    $ cp "$CRAMTMP/FakeSandbox/YAM.config" "$CRAMTMP/FakeSandbox/YAMCOPY.config"


20 TREEEE

    $ tree --noreport -d "$release_directory"
    /*/fake_release (glob)
    `-- Module-Releases
        |-- Dshell++
        |   |-- Dshell++-R4-06h
        |   |   `-- ONE
        |   |-- Dshell++-R4-06i
        |   |   |-- ONE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06i-MyprojectA-MaintenanceM00
        |   |   |-- ONE
        |   |   |-- THREE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06i-MyprojectA-MaintenanceM01
        |   |   |-- FOUR
        |   |   |-- ONE
        |   |   |-- THREE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06j
        |   |   |-- DUMM
        |   |   |-- ONE
        |   |   `-- TWO
        |   `-- Latest -> Dshell++-R4-06j
        `-- SiteDefs
            |-- SiteDefs-R1-63j
            |   `-- mkHome
            |       `-- shared
            `-- SiteDefs-R1-76l
                `-- mkHome
                    `-- shared


    $ tree --noreport -d "$sandbox_directory/src/Dshell++"
    /*/FakeSandbox/src/Dshell++ (glob)
    `-- ONE


----------------------- (3) first MAINT relelase ------------------------------
    $ echo "============= MAKE FIRST M2020 MAINTENANCE RELEASE FOR OLDER R4-06h VERSION"
    ============= MAKE FIRST M2020 MAINTENANCE RELEASE FOR OLDER R4-06h VERSION


22 More SVN STUFF

    $ cd "$sandbox_directory/src/Dshell++"
    $ svn mkdir 'FIVE'
    A         FIVE
    $ svn commit --message 'Add FIVE directory'
    Adding         FIVE
    Committing transaction...
    Committed revision *. (glob)


23 Test the "save" command.

    $ $PYAM save 'Dshell++'
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)


23B What yam config looks like after the first maint branch has been saved

    $ head -17 "$CRAMTMP/FakeSandbox/YAM.config"
    #
    # YAM.config - configuration file for yam utilities and makefiles
    #
    # Edit this file to suit your needs. Lines that end with backslash get spliced
    # together.
    #
    
    WORK_MODULES = DshellEnv
    
    LINK_MODULES = Dshell++/Dshell++-R4-06h-MyprojectA-MaintenanceM00
    
    BRANCH_DshellEnv = DshellEnv-R1-49q fake
    
    # BRANCH_Dshell++  = Dshell++-R4-06h-MyprojectA-MaintenanceM00   * (glob)
    
    #
    # Below is a list of variables that can be set:

    $ svn ls "$fake_repository_url/Modules/Dshell++/releases"
    Dshell++-R4-06e/
    Dshell++-R4-06f/
    Dshell++-R4-06g/
    Dshell++-R4-06h/
    Dshell++-R4-06h-MyprojectA-MaintenanceM00/
    Dshell++-R4-06i/
    Dshell++-R4-06i-MyprojectA-MaintenanceM00/
    Dshell++-R4-06i-MyprojectA-MaintenanceM01/
    Dshell++-R4-06j/

    $ svn ls "$fake_repository_url/Modules/Dshell++/featureBranches"
    Dshell++-R4-06h-MyprojectA-Maintenance/
    Dshell++-R4-06i-MyprojectA-Maintenance/

    $ svn ls "$fake_repository_url/Modules/Dshell++/deadBranches"
    Dshell++-R4-06h-*/ (glob)
    Dshell++-R4-06i-*/ (glob)

    $ tree --noreport -d "$release_directory"
    /*/fake_release (glob)
    `-- Module-Releases
        |-- Dshell++
        |   |-- Dshell++-R4-06h
        |   |   `-- ONE
        |   |-- Dshell++-R4-06h-MyprojectA-MaintenanceM00
        |   |   |-- FIVE
        |   |   `-- ONE
        |   |-- Dshell++-R4-06i
        |   |   |-- ONE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06i-MyprojectA-MaintenanceM00
        |   |   |-- ONE
        |   |   |-- THREE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06i-MyprojectA-MaintenanceM01
        |   |   |-- FOUR
        |   |   |-- ONE
        |   |   |-- THREE
        |   |   `-- TWO
        |   |-- Dshell++-R4-06j
        |   |   |-- DUMM
        |   |   |-- ONE
        |   |   `-- TWO
        |   `-- Latest -> Dshell++-R4-06j
        `-- SiteDefs
            |-- SiteDefs-R1-63j
            |   `-- mkHome
            |       `-- shared
            `-- SiteDefs-R1-76l
                `-- mkHome
                    `-- shared




    $ svn info --show-item relative-url "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06h-MyprojectA-MaintenanceM00"
    ^/Modules/Dshell++/releases/Dshell++-R4-06h-MyprojectA-MaintenanceM00

    $ head -17 "$release_directory/Module-Releases/Dshell++/Dshell++-R4-06h-MyprojectA-MaintenanceM00/ChangeLog"
    *  * (glob)
    
    \t* Revision tag: R4-06h-MyprojectA-MaintenanceM00 (esc)
    
    \t* Add FIVE directory (esc)
    
    \t  SVN revision: * (esc) (glob)
    \t  A FIVE (esc)
    
    *  * (glob)
    
    \t* Revision tag: R4-06h (esc)
    
    \t* Add ONE directory (esc)
    
    \t  SVN revision: * (esc) (glob)
    \t  A ONE (esc)


    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',62,' | grep 'R4-06'
    INSERT INTO `modpkgReleases` VALUES (14895,62,'R4-06',395,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',2,NULL,'clim-DEAD',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14945,62,'R4-06a',396,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jmc-DEAD, jbmas',NULL,'SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (14998,62,'R4-06b',397,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',5,NULL,'clim, jbmas',NULL,'SOURCE',1,1,34,8,39,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15123,62,'R4-06c',398,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',1,NULL,NULL,NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15135,62,'R4-06d',399,'*','jain','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',1,1,34,37,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15173,62,'R4-06e',400,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',13,NULL,'clim-DEAD, jbmas',NULL,'SOURCE',2,1,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15314,62,'R4-06f',401,'*','clim','ChangeLog, Readme, ReleaseNotes','TRUE',0,NULL,'jmc-DEAD','DshellX.h','SOURCE',0,*,34,32,25,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15315,62,'R4-06g',402,'*','jmc','ChangeLog, Readme, ReleaseNotes','TRUE',4,NULL,'jbmas, jingshen','DshellX.h','SOURCE',0,*,34,11,33,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15377,62,'R4-06h',403,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD, MyprojectA-Maintenance','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15378,62,'R4-06i',404,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,'*-DEAD, MyprojectA-Maintenance','','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15379,62,'R4-06j',405,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','SOURCE',0,*,36,*,41,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15380,62,'R4-06i',406,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','MAINTSOURCE',0,*,36,*,41,'0','MyprojectA',0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15381,62,'R4-06i',407,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'YamVersion.h','MAINTSOURCE',0,*,36,*,41,'1','MyprojectA',0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (15382,62,'R4-06h',408,'*','*','ChangeLog, ReleaseNotes','TRUE',0,NULL,NULL,'','MAINTSOURCE',0,*,36,*,41,'0','MyprojectA',0,0,0,0,0); (glob)


------ Syncing of a maintenance release should fail ---------

Syncing of a maintenance branch link or work module is not permitted.

    $ cd "$sandbox_directory"
    $ $PYAM sync Dshell++ DshellEnv
    YaM error: Cannot sync Dshell++ link module since it is on MyprojectA maintenance branch. Giving up.

----- Syncing to a maint release should work  -----------

Syncing to a maintenance release is OK

    $ cd "$sandbox_directory"
    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout --release main Dshell++
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk
    $ $PYAM sync Dshell++ --release R4-06h-MyprojectA-MaintenanceM00
    Syncing Dshell++ work module to R4-06h-MyprojectA-MaintenanceM00 release

    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/releases/Dshell++-R4-06h-MyprojectA-MaintenanceM00


----- Syncing to a maint release with branch should fail  -----------

Syncing to a maintenance release is OK

    $ cd "$sandbox_directory"
    $ $PYAM scrap --remove Dshell++
    $ $PYAM checkout --release main Dshell++
    $ svn info --show-item relative-url "$sandbox_directory/src/Dshell++"
    ^/Modules/Dshell++/trunk
    $ $PYAM sync Dshell++ --release R4-06h-MyprojectA-MaintenanceM00 --branch junk
    YaM error: Cannot specify a branch when syncing to a maintenance release



