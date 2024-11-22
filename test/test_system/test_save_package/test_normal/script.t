Test registering of a new package.

Unset YAM_ROOT or it will interfere.
Makefile.yam will pick up the real sandbox that contains the pyam module.

    $ unset YAM_ROOT

Unset configuration file environment variables as they may interfere.

    $ unset YAM_PROJECT_CONFIG_DIR
    $ unset YAM_PROJECT

Start empty MySQL server.

    $ . "$TESTDIR/../../../common/mysql/mysql_server.bash"
    $ start_mysql_server '/dev/null'
    $ PORT=$START_MYSQL_SERVER_RETURN_PORT

Initialize pyam.

    $ release_directory="$CRAMTMP/fake_release"
    $ fake_repository_path="$CRAMTMP/fake_repository"
    $ svnadmin create "$fake_repository_path"
    $ fake_repository_url="file://`readlink -f \"$fake_repository_path\"`"

    $ PYAM="$TESTDIR/../../../../pyam --quiet --non-interactive --no-build-server --database-connection=127.0.0.1:$PORT/test --release-directory=$release_directory --default-repository-url=$fake_repository_url"

    $ $PYAM --site telerobotics initialize
    $ $PYAM register-new-module Dshell++
    $ $PYAM register-new-module SimScape

-----------------------------------------------------------------------------
Create a new package.

    $ $PYAM register-new-package MyNewPkg --modules Dshell++ SimScape
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

-----------------------------------------------------------------------------
Test "save-package"

    $ $PYAM save-package --release-note-message='Fake message' MyNewPkg
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

Verifying by checking out a tagged package.

    $ sandbox_directory="$CRAMTMP/sandbox"
    $ $PYAM setup --directory="$sandbox_directory" --revision-tag='R1-00a' MyNewPkg

    $ ls -d "$sandbox_directory"
    */sandbox (glob)

    $ grep 'SimScape' "$sandbox_directory/YAM.config"
                   SimScape/SimScape-R1-00 \
    # BRANCH_SimScape = SimScape-R1-00  * (glob)

    $ grep 'SiteDefs' "$sandbox_directory/YAM.config"
                   SiteDefs/SiteDefs-R1-00a
    # BRANCH_SiteDefs = SiteDefs-R1-00a * (glob)


    $ ls "$sandbox_directory/Makefile"
    */sandbox/Makefile (glob)
    $ ls -d "$sandbox_directory/common"
    */sandbox/common (glob)


    $ ls -d "$sandbox_directory/Makefile"
    */sandbox/Makefile (glob)


    $ ls -d "$sandbox_directory/common"
    */sandbox/common (glob)

Check that the sandbox directory is checked out from "Packages/.../releases"

    $ svn info --show-item relative-url $sandbox_directory
    ^/Packages/MyNewPkg/releases/MyNewPkg-R1-00a

Check that the sandbox directory is checked out from "Packages/.../releases/.../common"

    $ svn info --show-item relative-url "$sandbox_directory/common"
    ^/Packages/MyNewPkg/releases/MyNewPkg-R1-00a/common

Make sure our release note is in there.

    $ grep 'Fake message' "$sandbox_directory/ReleaseNotes"
    \tFake message (esc)

-----------------------------------------------------------------------------
Saving the package with "--config-file" should result in a custom YAM.config
in the package release.

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/yamconfig-1"
    $ echo 'BRANCH_Dshell++ = Dshell++-R1-00' >> "$CRAMTMP/yamconfig-1"
    $ echo 'LINK_MODULES = SimScape/SimScape-R1-00' >> "$CRAMTMP/yamconfig-1"

Check the latest package release

    $ $PYAM latest-package MyNewPkg
    MyNewPkg R1-00a


    $ ls "$release_directory/Pkg-Releases/MyNewPkg"
    Latest
    MyNewPkg-R1-00
    MyNewPkg-R1-00a


Check for the package entry and its '427' id

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep 'MyNewPkg'
    INSERT INTO `modulePackages` VALUES (427,'MyNewPkg',2,'PACKAGE',18453,18453,NULL,NULL,'FALSE','FALSE','svn');

Check for the SimScape module entry and its '426' id

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modulePackages | grep 'SimScape'
    INSERT INTO `modulePackages` VALUES (426,'SimScape',1,'MODULE',18451,18451,NULL,NULL,'FALSE','FALSE','svn');

Check the 2 relatives for the SimScape (id=426) latest release (relid=18451)

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',426,'
    INSERT INTO `modpkgReleases` VALUES (18451,426,'R1-00',1,*,'','','TRUE',2,NULL,NULL,'','SOURCE',0,50,51,70,58,NULL,NULL,0,0,0,0,0); (glob)


Actually make the package release

    $ $PYAM save-package --config-file "$CRAMTMP/yamconfig-1" --release-note-message='Fake message' MyNewPkg
    WARNING: Skipping sending email because both 'email_from_address' and 'email_to_address' need to be defined (eithier in the pyamrc file or on the command line)

    $ $PYAM latest-package MyNewPkg
    MyNewPkg R1-00b

    $ ls "$release_directory/Pkg-Releases/MyNewPkg"
    Latest
    MyNewPkg-R1-00
    MyNewPkg-R1-00a
    MyNewPkg-R1-00b


Check for package release entries


    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',427,'
    INSERT INTO `modpkgReleases` VALUES (18452,427,'R1-00',1,*,'*',NULL,'TRUE',3,NULL,NULL,NULL,'PACKAGE',0,1,1,1,1,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (18453,427,'R1-00a',2,*,'*',NULL,'TRUE',3,NULL,NULL,NULL,'PACKAGE',0,1,1,1,1,NULL,NULL,0,0,0,0,0); (glob)
    INSERT INTO `modpkgReleases` VALUES (18454,427,'R1-00b',3,*,'*',NULL,'TRUE',2,NULL,NULL,NULL,'PACKAGE',0,1,1,1,1,NULL,NULL,0,0,0,0,0); (glob)

Check for the module release relatives entry for this package release (relid=18454)

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test packageModuleReleases | grep '18454,'
    INSERT INTO `packageModuleReleases` VALUES (18454,18451);
    INSERT INTO `packageModuleReleases` VALUES (18454,18450);


Check the now 3 relatives for the SimScape (id=426) latest release (relid=18451)

    $ mysqldump --host=127.0.0.1 --port=$PORT --skip-opt --compact test modpkgReleases | grep ',426,'
    INSERT INTO `modpkgReleases` VALUES (18451,426,'R1-00',1,*,'','','TRUE',3,NULL,NULL,'','SOURCE',0,50,51,70,58,NULL,NULL,0,0,0,0,0); (glob)


    $ grep 'SimScape' "$release_directory/Pkg-Releases/MyNewPkg/MyNewPkg-R1-00b/YAM.config"
                   SimScape/SimScape-R1-00
    # BRANCH_SimScape = SimScape-R1-00  * (glob)

    $ grep 'SiteDefs' "$release_directory/Pkg-Releases/MyNewPkg/MyNewPkg-R1-00b/YAM.config"


-----------------------------------------------------------------------------
Should not allow package release with a module on the main trunk.

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/yamconfig-2"
    $ echo 'BRANCH_Dshell++ = main' >> "$CRAMTMP/yamconfig-2"
    $ echo 'LINK_MODULES = SimScape/SimScape-R1-00' >> "$CRAMTMP/yamconfig-2"


    $ $PYAM save-package --config-file "$CRAMTMP/yamconfig-2" --release-note-message='Fake message' MyNewPkg  |& awk '!/^Traceback|^  File|^    /'
    ValueError: Main trunk Dshell++ module in */yamconfig-2 config file cannot be used in a package release. (glob)



-----------------------------------------------------------------------------
Should not allow package release with a branched module.

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/yamconfig-3"
    $ echo 'BRANCH_Dshell++ = Dshell++-R1-00  mybranch' >> "$CRAMTMP/yamconfig-3"
    $ echo 'LINK_MODULES = SimScape/SimScape-R1-00' >> "$CRAMTMP/yamconfig-3"


    $ $PYAM save-package --config-file "$CRAMTMP/yamconfig-3" --release-note-message='Fake message' MyNewPkg |& awk '!/^Traceback|^  File|^    /'
    ValueError: Dshell++ module with R1-00-mybranch branch in */yamconfig-3 config file cannot be used in a package release. (glob)



-----------------------------------------------------------------------------
Should not allow package release with a module release that does not exist.

    $ echo 'WORK_MODULES = Dshell++' >> "$CRAMTMP/yamconfig-4"
    $ echo 'BRANCH_Dshell++ = Dshell++-R1-02' >> "$CRAMTMP/yamconfig-4"
    $ echo 'LINK_MODULES = SimScape/SimScape-R1-00' >> "$CRAMTMP/yamconfig-4"


 ###$ $PYAM save-package --config-file "$CRAMTMP/yamconfig-4" --release-note-message='Fake message' MyNewPkg  |& awk '!/^Traceback|^  File|^    /'

    $ $PYAM save-package --config-file "$CRAMTMP/yamconfig-4" --release-note-message='Fake message' MyNewPkg  |& awk '/^ValueError: There is no /'
    ValueError: There is no existing R1-02 release for the Dshell++ module specified in the */yamconfig-4 config file. (glob)




-----------------------------------------------------------------------------
Clean up

    $ chmod u+w "$release_directory/Pkg-Releases/MyNewPkg/MyNewPkg-R1-00a"
    $ chmod u+w "$release_directory/Pkg-Releases/MyNewPkg/MyNewPkg-R1-00b"
    $ chmod u+w "$release_directory/Pkg-Releases/MyNewPkg/MyNewPkg-R1-00"
